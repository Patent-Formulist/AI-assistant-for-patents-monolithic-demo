import asyncio
from typing import Any, TypeVar

import aiohttp

from app.service.key.key import KeyService
from app.service.llm_usage.collector import LLMUsage, record_usage
from core import logger
from core.dependencies.handler import with_db
from core.dependencies.key import get_key_service
from core.domain.key import Key
from core.enum.token_key import KeyType
from core.exceptions import NetworkError, RateLimitError
from core.settings import LLMSettings

logger = logger.get_logger(__name__)
T = TypeVar("T", bound=LLMSettings)


class LLMClient:
    """Base LLM client; subclasses adapt headers and payload to a provider."""

    def __init__(self, config: T):
        self.config: T = config

    async def ask(self, prompt: str) -> str:
        """Основной метод с повторными попытками и обработкой ошибок."""
        last_error = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                result = await self._make_request(prompt)
                return result
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries and await self._is_retryable(e):
                    delay = self.config.base_delay ** (attempt - 1)
                    logger.warning(f"Attempt {attempt} failed, retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.config.max_retries} attempts failed: {e}")
                    break
        raise last_error or RuntimeError(
            f"LLM request failed after {self.config.max_retries} attempts"
        )

    async def _make_request(self, prompt: str) -> str:
        """Формирует и отправляет HTTP-запрос, возвращает текст ответа."""
        key = await self._acquire_key()
        headers = await self._build_headers(key.key)
        data = await self._build_request_data(prompt)
        timeout = aiohttp.ClientTimeout(total=getattr(self.config, "timeout", 30))

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=self.config.api_uri, headers=headers, json=data, timeout=timeout
                ) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        # Billed even if the content turns out unusable
                        self._record_usage(response_json, key)
                        return await self._extract_content(response_json)
                    else:
                        error_text = await response.text()
                        await self._handle_http_error(response.status, error_text)
        except TimeoutError as e:
            raise NetworkError("Request timeout") from e
        except aiohttp.ClientError as e:
            raise NetworkError(f"HTTP error: {e}") from e

    # Методы, которые могут быть переопределены в наследниках
    async def _acquire_key(self) -> Key:
        """Take one use of an API key from the pool."""
        try:
            key = await with_db(self._get_token)
        except Exception as e:
            logger.error(f"Failed to get API token from database: {e}")
            raise
        if not key:
            logger.error("No key domain returned from with_db")
            raise ValueError("Failed to get API key")
        logger.info(f"Successfully obtained token for {KeyType.DeepSeek}")
        return key

    async def _build_headers(self, token: str) -> dict[str, str]:
        """Формирует заголовки запроса. По умолчанию только Authorization."""
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _record_usage(self, response_data: dict[str, Any], key: Key) -> None:
        """Pass the billed tokens of the response to the usage collector, if any.

        OpenAI format; DeepSeek reports cached prompt tokens as
        ``prompt_cache_hit_tokens``, OpenAI as ``prompt_tokens_details.cached_tokens``.
        """
        usage = response_data.get("usage")
        if not usage:
            logger.warning("LLM response has no usage")
            return
        cached = usage.get("prompt_cache_hit_tokens")
        if cached is None:
            cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0)
        record_usage(
            LLMUsage(
                model=response_data.get("model") or self.config.model,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                cached_tokens=cached or 0,
                key_id=str(key.id) if key.id is not None else None,
            )
        )

    async def _get_token(self, session) -> Key:
        """Take one use of a DeepSeek API key; with_db commits it right away."""
        key_service: KeyService = get_key_service(session)
        key = await key_service.acquire_key(KeyType.DeepSeek)
        logger.debug(f"Retrieved key {key.id} from DB")
        return key

    async def _build_request_data(self, prompt: str) -> dict[str, Any]:
        """Формирует тело запроса. По умолчанию стандартное для OpenAI-совместимых API."""
        request_data = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
        }
        log_data = request_data.copy()
        if len(prompt) > 300:
            log_data["messages"] = [{"role": "user", "content": prompt[:300] + "..."}]

        logger.info(f"Request data: {log_data}")
        return request_data

    async def _extract_content(self, response_data: dict[str, Any]) -> str:
        """Извлекает текст ответа из JSON. По умолчанию для OpenAI-формата."""
        try:
            return response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise ValueError(f"Invalid response format: {e}") from e

    async def _is_retryable(self, error: Exception) -> bool:
        """Определяет, стоит ли повторять запрос при этой ошибке."""
        return isinstance(error, (NetworkError, aiohttp.ClientError, asyncio.TimeoutError))

    async def _handle_http_error(self, status_code: int, error_text: str):
        """Обрабатывает HTTP-ошибки."""
        if status_code == 401:
            raise PermissionError("Invalid API key")
        elif status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif status_code >= 500:
            raise NetworkError(f"Server error {status_code}")
        else:
            raise RuntimeError(f"API error {status_code}: {error_text[:200]}")
