from typing import Annotated

import sentry_sdk
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.service.token.processor import ProcessorTokenService
from app.service.token.token import TokenService
from app.service.user.user import UserService
from core.dependencies.token import get_token_processor, get_token_service
from core.dependencies.user import get_user_service
from core.domain.token import Token
from core.enum.token_type import TokenType
from core.exceptions import InvalidSchemeError, MissingHeaderError

# auto_error=False: пустой или отсутствующий заголовок разбираем сами,
# чтобы ответ был таким же, как у остальных auth-ошибок (см. app/http/exception_handlers.py).
security = HTTPBearer(auto_error=False)

SecurityDep = Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
ProcessorTokenServiceDep = Annotated[ProcessorTokenService, Depends(get_token_processor)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user_id(
    credentials: SecurityDep,
    processor: ProcessorTokenServiceDep,
    token_service: TokenServiceDep,
    user_service: UserServiceDep,
) -> int:
    """Проверяет access-токен и возвращает id пользователя.

    Раньше эту проверку выполнял nginx (`auth_request` к `/api/v2/users/validate`),
    а роуты доверяли заголовку `X-User-Id`. Теперь токен проверяет сам бэкенд,
    поэтому заголовку из запроса больше ничего не доверяется.

    Исключения из зависимости не попадают в `handle_exceptions` (декоратор обёрнут
    только вокруг тела эндпоинта, а зависимости разрешаются до его вызова) —
    их переводит в 401 обработчик, зарегистрированный в `register_exception_handlers`.
    """
    if not credentials:
        raise MissingHeaderError("Bearer token is required")
    if credentials.scheme.lower() != "bearer":
        raise InvalidSchemeError("Only the Bearer scheme is accepted")

    token: Token = await processor.process_check_token(
        token=credentials.credentials.strip(),
        user_service=user_service,
        expected_type=TokenType.ACCESS,
    )
    # process_check_token уже загрузил пользователя по payload["sub"]; этот запрос
    # берёт user_id из таблицы токенов — так же, как делал /users/validate до переноса.
    user_id = await token_service.get_user_id_by_token_jti(token.jti)
    # Errors of this request show whose they were (only the id: no personal data)
    sentry_sdk.set_user({"id": str(user_id)})
    return user_id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
