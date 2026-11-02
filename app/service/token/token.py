from datetime import datetime
from typing import Any

from jose import JWTError
from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.base import BaseService
from app.service.token.data import TokenDataService
from app.service.token.repository import TokenRepository, UserTokenRepository
from core import logger
from core.data_mapper.token import TokenMapper
from core.db.models.token import TokenModel
from core.db.models.user_token import UserTokenModel
from core.domain.token import Token
from core.enum.token_type import TokenType
from core.exceptions import TokenError, ValidationTokenError

logger = logger.get_logger(__name__)


class TokenService(BaseService[TokenModel, TokenRepository]):
    """Issued JWT tokens and their owners."""

    repository_type = TokenRepository

    def __init__(self, session: AsyncSession, data_service: TokenDataService, **kwargs):
        super().__init__(session=session, **kwargs)
        self._user_tokens = UserTokenRepository(session=session)
        self._data_service = data_service

    async def create_token(
        self, user_id: int, token_type: TokenType, data: dict[str, Any] = None
    ) -> Token:
        if token_type == TokenType.ACCESS:
            token_domain = self._data_service.create_access_token(data, str(user_id))
        elif token_type == TokenType.REFRESH:
            token_domain = self._data_service.create_refresh_token(data, str(user_id))
        else:
            raise NotImplementedError

        token_model = await self.create(await TokenMapper.to_model(token_domain))
        await self._user_tokens.add(UserTokenModel(user_id=user_id, token_id=token_model.jti))
        return token_domain

    async def get_token(self, jti: str) -> Token:
        logger.debug(f"Start get token: {jti}")
        token_model = await self.get_one_or_none(jti=jti)
        if token_model is None:
            raise ValidationTokenError("Token not found in database")
        return await TokenMapper.to_domain(token_model)

    async def get_user_id_by_token_jti(self, jti: str) -> int:
        logger.debug(f"Start get user id: {jti}")
        user_token = await self._user_tokens.get_one_or_none(token_id=jti)
        if user_token is None:
            raise ValidationTokenError("User not found in database")
        return user_token.user_id

    async def touch_token(self, jti: str, last_used_at: datetime) -> None:
        """Store when the token was last used."""
        token_model = await self.get_one_or_none(jti=jti)
        if token_model is None:
            raise ValidationTokenError("Token not found in database")
        token_model.last_used_at = last_used_at
        await self.update(token_model)

    async def revoke_token(self, jti: str, reason: str) -> None:
        """Revoke the token once.

        A conditional UPDATE, so of two concurrent requests with the same token
        only one succeeds; the other gets ValidationTokenError.
        """
        result = await self.repository.session.execute(
            update(TokenModel)
            .where(TokenModel.jti == jti, TokenModel.revoked.is_not(True))
            .values(revoked=True, revoked_at=func.now(), revocation_reason=reason)
        )
        if result.rowcount == 0:
            if await self.get_one_or_none(jti=jti) is None:
                raise ValidationTokenError("Token not found in database")
            raise ValidationTokenError("Token has been revoked")

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        """Revoke a refresh token given as the encoded JWT (logout)."""
        try:
            payload = self._data_service.decode_token(refresh_token)
        except JWTError as e:
            raise ValidationTokenError("Invalid token") from e
        if payload.get("type") != TokenType.REFRESH.value:
            raise TokenError(f"Only {TokenType.REFRESH.value} tokens can be revoked")
        await self.revoke_token(payload["jti"], reason="logout")
