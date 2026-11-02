from datetime import UTC, datetime, timedelta

import uuid6
from jose import jwt

from core import logger
from core.domain.token import Token
from core.enum.token_frame import TokenFrame
from core.enum.token_type import TokenType
from core.settings import AuthSettings

logger = logger.get_logger(__name__)


class TokenDataService:
    def __init__(self, config: AuthSettings):
        self._config = config

    def create_access_token(
        self,
        data: dict[str, any],
        subject: str,
        ttl: TokenFrame | None = TokenFrame.DEFAULT,
    ) -> Token:
        """Создаёт access токен и возвращает доменный объект Token"""
        if ttl == TokenFrame.DEFAULT:
            ttl_delta = timedelta(minutes=self._config.access_token_expire_minutes)
        else:
            ttl_delta = None

        return self._create_token(
            token_type=TokenType.ACCESS, subject=subject, payload=data, ttl=ttl_delta
        )

    def create_refresh_token(
        self,
        data: dict[str, any],
        subject: str,
        ttl: TokenFrame | None = TokenFrame.DEFAULT,
    ) -> Token:
        """Создаёт refresh токен и возвращает доменный объект Token"""
        if ttl == TokenFrame.DEFAULT:
            ttl_delta = timedelta(minutes=self._config.refresh_token_expire_minutes)
        else:
            ttl_delta = None

        return self._create_token(
            token_type=TokenType.REFRESH, subject=subject, payload=data, ttl=ttl_delta
        )

    def _create_token(
        self,
        token_type: TokenType,
        subject: str,
        payload: dict[str, any],
        ttl: timedelta | None = None,
    ) -> Token:
        """
        Создаёт токен и возвращает доменный объект.

        Args:
            token_type: тип токена (ACCESS/REFRESH)
            subject: идентификатор пользователя
            payload: дополнительные данные для токена
            ttl: время жизни токена
        """
        current_timestamp = datetime.now(UTC)
        jti = str(uuid6.uuid7())

        expires_at = None
        if ttl:
            expires_at = current_timestamp + ttl

        # Формируем payload для JWT
        jwt_payload = {
            "iss": "formula@auth_service",
            "sub": subject,
            "type": token_type.value,
            "jti": jti,
            "iat": current_timestamp,
            "nbf": payload.get("nbf", current_timestamp),
        }

        # Добавляем expiration если есть ttl
        if expires_at:
            jwt_payload["exp"] = expires_at

        # Добавляем пользовательские данные
        jwt_payload.update(payload)

        # Кодируем JWT
        encoded_token = jwt.encode(
            jwt_payload,
            key=self._config.jwt_secret_key.get_secret_value(),
            algorithm=self._config.jwt_algorithm,
        )

        # Создаём доменный объект Token
        domain_token = Token(
            jti=jti,
            token=encoded_token,
            token_type=token_type,
            issued_at=current_timestamp,
            expires_at=expires_at,
            revoked=False,
            revoked_at=None,
            revocation_reason=None,
            last_used_at=None,
            user_agent=payload.get("user_agent"),
            ip_address=payload.get("ip_address"),
            device_info=payload.get("device_info"),
        )

        return domain_token

    def decode_token(self, token: str):
        return jwt.decode(
            token,
            self._config.jwt_secret_key.get_secret_value(),
            algorithms=[self._config.jwt_algorithm],
        )
