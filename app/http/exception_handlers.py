"""Обработчики исключений на уровне приложения.

Нужны для ошибок, которые возникают в зависимостях FastAPI: `handle_exceptions`
обёрнут только вокруг тела эндпоинта, а зависимости разрешаются до его вызова,
поэтому брошенное там исключение до декоратора не доходит и без обработчика
превратилось бы в 500 вместо 401.

Обработчики живут в `ExceptionMiddleware`, который обёрнут вокруг всего роутинга,
и ловят исключения как из зависимостей, так и из тел эндпоинтов. Поиск идёт по
классу исключения и вверх по его базовым классам — выигрывает самый специфичный
из зарегистрированных, порядок регистрации значения не имеет.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from jose.exceptions import JWTError

from core.exceptions import (
    AccessTokenError,
    InvalidSchemeError,
    MissingHeaderError,
    RefreshTokenError,
    ValidationTokenError,
)

# Текст сообщений совпадает с тем, что раньше отдавал handle_exceptions,
# чтобы ответы API не изменились.
UNAUTHORIZED: dict[type[Exception], str] = {
    MissingHeaderError: "Authorization header required",
    InvalidSchemeError: "Invalid authentication scheme",
    AccessTokenError: "Access token required",
    RefreshTokenError: "Refresh token required",
    ValidationTokenError: "Invalid token",
    JWTError: "Token validation failed",
}


def register_exception_handlers(app: FastAPI) -> None:
    for error, message in UNAUTHORIZED.items():

        async def handler(request: Request, exc: Exception, message: str = message) -> JSONResponse:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": f"{message}: {str(exc)}"},
            )

        app.add_exception_handler(error, handler)
