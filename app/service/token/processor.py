from jose import JWTError

from app.service.token.data import TokenDataService
from app.service.token.token import TokenService
from app.service.user.user import UserService
from core import logger
from core.domain.token import Token
from core.domain.user import User
from core.dto.token_pair import TokenPair
from core.enum.token_type import TokenType
from core.enum.user_status import UserStatus
from core.exceptions import AccessTokenError, RefreshTokenError, ValidationTokenError

logger = logger.get_logger(__name__)


class ProcessorTokenService:
    def __init__(self, ds: TokenDataService, ts: TokenService):
        self._data_service: TokenDataService = ds
        self._token_service: TokenService = ts

    async def process_create_token_pair(
        self, user_id: int, user_service: UserService, data: dict = None
    ) -> TokenPair:
        """
        Создаёт пару токенов для пользователя.
        """
        try:
            user = await user_service.get_user_by_id(user_id)
            if not user:
                raise ValidationTokenError("User not found")

            # Создаём refresh токен
            refresh_data = {
                "user_agent": None,  # В будующем передаем из контекста
                "ip_address": None,
            }
            refresh: Token = await self._token_service.create_token(
                user_id=user_id, token_type=TokenType.REFRESH, data=refresh_data
            )

            # Создаём access токен с привязкой к refresh
            access_data = {
                "refresh_jti": refresh.jti,
                "user_agent": None,
                "ip_address": None,
            }
            access: Token = await self._token_service.create_token(
                user_id=user_id, token_type=TokenType.ACCESS, data=access_data
            )

            logger.info(f"Created token pair for user {user_id}")
            return TokenPair(access_token=access.token, refresh_token=refresh.token)

        except Exception as e:
            logger.error(f"Failed to create token pair for user {user_id}: {e}")
            raise

    async def process_check_token(
        self, token: str, expected_type: TokenType, user_service: UserService
    ) -> Token:
        try:
            # Декодирование токена
            payload = self._data_service.decode_token(token)
            token_type = payload.get("type")

            # Проверка типа токена
            if token_type != expected_type.value:
                if expected_type == TokenType.ACCESS:
                    raise AccessTokenError(f"Only {TokenType.ACCESS.value} tokens are accepted")
                else:
                    raise RefreshTokenError(f"Only {TokenType.REFRESH.value} tokens are accepted")

            # Проверка отзыва токена
            token_domain: Token = await self._token_service.get_token(payload["jti"])
            if token_domain.revoked:
                raise ValidationTokenError("Token has been revoked")

            # Проверка пользователя
            user: User = await user_service.get_user_by_id(int(payload["sub"]))
            if not user:
                raise ValidationTokenError("User not found")

            if user.status == UserStatus.SUSPENDED:
                raise ValidationTokenError("User account is suspended")
            elif user.status == UserStatus.BANNED:
                raise ValidationTokenError("User account is banned")

            # Обновляем время последнего использования токена
            token_domain.update_last_used()
            await self._token_service.touch_token(token_domain.jti, token_domain.last_used_at)

            return token_domain
        except JWTError as e:
            raise ValidationTokenError("Invalid token") from e
        except Exception as e:
            logger.error(f"Unexpected error in process_check_token: {e}")
            raise
