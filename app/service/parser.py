import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aiohttp

from core import logger
from core.exceptions import NetworkError, ParserError

logger = logger.get_logger(__name__)


class Parser:
    """
    Парсер для API Роспатента

    Особенности:
    - Асинхронные HTTP-запросы
    - Экспоненциальная backoff-стратегия при повторах
    - Валидация ответов API
    - Подробное логирование
    """

    def __init__(self, config):
        self.config = config
        self._session: aiohttp.ClientSession | None = None
        self._session_owner: bool = False
        self._auto_close: bool = True

    @asynccontextmanager
    async def _ensure_session(self) -> AsyncGenerator[aiohttp.ClientSession, None]:
        """
        Контекстный менеджер для сессии.

        Args:
            auto_close: Если True, сессия закроется после выхода.
                        Если False, останется открытой.
                        По умолчанию использует self._auto_close
        """

        auto_close = self._auto_close

        try:
            if self._session is None or self._session.closed:
                self._session = aiohttp.ClientSession()
                self._session_owner = True
                logger.debug("Created new session")

            yield self._session
        finally:
            if auto_close and self._session_owner and not self._session.closed:
                await self._session.close()
                self._session = None
                self._session_owner = False
                logger.debug("Closed owned session (auto_close=True)")

    async def __aenter__(self):
        """Контекстный менеджер для внешнего использования"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._session_owner = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из контекста"""
        await self.close()

    async def close(self):
        """Явное закрытие сессии"""
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None
            self._session_owner = False

    async def request_with_retries(
        self,
        method: str,
        url: str,
        session: aiohttp.ClientSession,
        headers: dict | None = None,
        params: dict | None = None,
        payload: dict | None = None,
        **kwargs,
    ) -> dict | None:
        """
        Универсальный метод для HTTP запросов с повторными попытками

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            url: URL для запроса
            session: Сессия aiohttp
            headers: HTTP заголовки
            params: Параметры запроса (для GET)
            payload: Тело запроса (для POST/PUT)

        Returns:
            Ответ в формате JSON или None при ошибке
        """
        headers = headers or {}
        retries = kwargs.get("retries") or getattr(self.config, "request_retries", 3)
        timeout = kwargs.get("timeout") or getattr(self.config, "request_timeout", 30)
        base_delay = kwargs.get("base_delay") or getattr(self.config, "request_base_delay", 1)

        for attempt in range(1, retries + 1):
            try:
                logger.debug(f"{method} attempt {attempt}/{retries}: {url}")

                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as response:
                    # Успешный ответ
                    if response.status == 200:
                        try:
                            return await response.json()
                        except aiohttp.ContentTypeError as e:
                            text = await response.text()
                            logger.error(f"Invalid JSON response: {e}, text: {text[:200]}")
                            raise ParserError("Invalid JSON format") from e

                    # 401 - авторизация не пройдена
                    if response.status == 401:
                        text = await response.text()
                        logger.error(f"Authorization failed (401): {text}")
                        raise NetworkError("Authorization failed")

                    # Клиентские ошибки (не повторяем)
                    if response.status in {400, 403, 404}:
                        text = await response.text()
                        logger.error(f"Client error {response.status}: {text[:200]}")
                        raise NetworkError(f"Client error {response.status}")

                    # Серверные ошибки (повторяем)
                    if response.status in {429, 500, 502, 503, 504} and attempt < retries:
                        delay = base_delay * (2 ** (attempt - 1))
                        logger.warning(f"Server error {response.status}, retrying in {delay}s")
                        await asyncio.sleep(delay)
                        continue

                    # Другие статусы
                    text = await response.text()
                    raise NetworkError(f"HTTP {response.status}: {text[:200]}")

            except TimeoutError as e:
                logger.warning(f"Timeout attempt {attempt}")
                if attempt < retries:
                    delay = base_delay * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)
                    continue
                raise NetworkError(f"Timeout after {retries} attempts") from e

            except aiohttp.ClientError as e:
                logger.warning(f"Client error attempt {attempt}: {e}")
                if attempt < retries:
                    delay = base_delay * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)
                    continue
                raise NetworkError(f"Client error: {e}") from e

        raise NetworkError(f"{method} failed after {retries} attempts")

    async def disable_auto_close(self):
        """Disables automatic session closure."""
        self._auto_close = False
        logger.debug("Auto-close disabled")

    async def enable_auto_close(self):
        """Enables automatic session closure."""
        self._auto_close = True
        logger.debug("Auto-close enabled")
