from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

from jose import JWTError, jwt
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.mail.mailer import Mailer
from core import logger
from core.db.models.user import UserModel
from core.exceptions import EmailVerificationError, TooManyRequestsError
from core.settings import AuthSettings

logger = logger.get_logger(__name__)

PURPOSE = "email_verification"


class EmailVerificationService:
    """Confirms that a user owns their email.

    The link carries a signed token (JWT with the app's key) naming the user and
    the email it was sent to: changing the email makes older links useless, and
    nothing has to be stored to check one. Runs in the request session.
    """

    def __init__(self, session: AsyncSession, mailer: Mailer, settings: AuthSettings):
        self._session = session
        self._mailer = mailer
        self._settings = settings

    async def send(self, user_id: int) -> bool:
        """Mail a confirmation link; False if the email is already confirmed.

        Raises TooManyRequestsError (429) when asked again too soon.
        """
        # Read fresh, in one query: the row may have just been updated in this session
        row = (
            await self._session.execute(
                select(
                    UserModel.email,
                    UserModel.is_email_verified,
                    func.now() - UserModel.email_verification_sent_at,
                ).where(UserModel.id == user_id)
            )
        ).one_or_none()
        if row is None or not row[0]:
            raise EmailVerificationError("Нет email для подтверждения")
        email, verified, since_sent = row
        if verified:
            return False
        resend = timedelta(seconds=self._settings.email_verification_resend_seconds)
        if since_sent is not None and since_sent < resend:
            raise TooManyRequestsError("Письмо уже отправлено, попробуйте через минуту")
        link = (
            f"{self._settings.email_verification_url}?"
            f"{urlencode({'token': self._token(user_id, email)})}"
        )
        await self._mailer.send(
            email,
            "Подтвердите email в Formulist",
            "Чтобы подтвердить email, откройте ссылку:\n\n"
            f"{link}\n\n"
            f"Ссылка действует {self._settings.email_verification_ttl_minutes // 60} ч. "
            "Если вы не регистрировались в Formulist, просто удалите это письмо.",
        )
        await self._session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(email_verification_sent_at=func.now())
        )
        return True

    async def send_quietly(self, user_id: int) -> None:
        """``send`` for registration: a mail failure must not fail the registration."""
        try:
            await self.send(user_id)
        except Exception as e:
            logger.error(f"Could not send the confirmation email to user {user_id}: {e}")

    async def send_if_changed(self, user_id: int, new_email: str | None) -> None:
        """After a profile update: a changed email is unconfirmed, mail a new link."""
        if new_email is not None:
            await self.send_quietly(user_id)

    async def verify(self, token: str) -> int:
        """Confirm the email the token was sent to; return the user id."""
        try:
            claims = jwt.decode(
                token,
                self._settings.jwt_secret_key.get_secret_value(),
                algorithms=[self._settings.jwt_algorithm],
            )
        except JWTError as e:
            raise EmailVerificationError("Ссылка недействительна или устарела") from e
        if claims.get("purpose") != PURPOSE:
            raise EmailVerificationError("Ссылка недействительна или устарела")
        user = await self._session.get(UserModel, int(claims["sub"]))
        if user is None or (user.email or "").lower() != claims.get("email"):
            raise EmailVerificationError("Ссылка выдана для другого email")
        if not user.is_email_verified:
            user.is_email_verified = True
            user.email_verified_at = func.now()
            await self._session.flush()
            logger.info(f"User {user.id} confirmed the email")
        return user.id

    def _token(self, user_id: int, email: str) -> str:
        expires = datetime.now(UTC) + timedelta(
            minutes=self._settings.email_verification_ttl_minutes
        )
        return jwt.encode(
            {
                "sub": str(user_id),
                "email": email.lower(),
                "purpose": PURPOSE,
                "exp": expires,
            },
            self._settings.jwt_secret_key.get_secret_value(),
            algorithm=self._settings.jwt_algorithm,
        )
