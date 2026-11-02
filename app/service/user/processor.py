from passlib.context import CryptContext

from app.service.token.token import TokenService
from app.service.user.user import UserService
from core import logger
from core.domain.user import User
from core.dto.user import UserAuth, UserUpdate
from core.enum.user_status import UserStatus
from core.exceptions import LoginError, LogoutError, RegistrationError

logger = logger.get_logger(__name__)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class ProcessorUserService:
    def __init__(self, us: UserService):
        self._user_service: UserService = us

    async def registration(self, dto: UserAuth) -> User:
        try:
            hashed_password = pwd_context.hash(dto.password)
            return await self._user_service.create_user_by_email(
                email=dto.email, hashed_password=hashed_password
            )
        except Exception as e:
            logger.error(e)
            raise RegistrationError(e) from e

    async def login(self, dto: UserAuth) -> User:
        try:
            user: User = await self._user_service.get_user_by_email(dto.email)
            if not pwd_context.verify(dto.password, user.hashed_password):
                raise LoginError("Invalid password")
            if user.status == UserStatus.BANNED.value or user.status == UserStatus.SUSPENDED.value:
                raise LoginError("The user is blocked")
            return user
        except Exception as e:
            logger.error(e)
            raise LoginError(e) from e

    async def logout(self, refresh_token: str, ts: TokenService):
        try:
            await ts.revoke_refresh_token(refresh_token)
        except Exception as e:
            logger.error(e)
            raise LogoutError(e) from e

    async def update_profile(self, user_id: int, dto: UserUpdate) -> User:
        try:
            return await self._user_service.update_user_profile(user_id, dto)
        except Exception as e:
            logger.error(f"Profile update error: {e}")
            # Здесь можно использовать кастомную ошибку, например UpdateProfileError
            raise ValueError(str(e)) from e
