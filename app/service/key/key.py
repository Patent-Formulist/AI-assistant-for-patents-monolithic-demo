import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.service.base import BaseService
from app.service.key.repository import KeyRepository, KeyUsageRepository
from core import logger
from core.data_mapper.key.key import KeyMapper
from core.db.models.key import KeyModel
from core.domain.key import Key
from core.enum.token_key import KeyType

logger = logger.get_logger(__name__)


class KeyService(BaseService[KeyModel, KeyRepository]):
    """API keys of external services (LLM) and their usage limits.

    Errors are raised as ValueError, which the LLM client expects.
    """

    repository_type = KeyRepository

    # Immediate re-attempts when a concurrent request took the chosen key first
    _CONTENDED_ATTEMPTS = 5

    def __init__(self, session: AsyncSession, **kwargs):
        super().__init__(session=session, **kwargs)
        self._usages = KeyUsageRepository(session=session)

    async def acquire_key(
        self, key_type: KeyType, max_retries: int = 3, retry_delay: int = 30
    ) -> Key:
        """
        Take one use of an available key, waiting when all keys are exhausted.

        The use is counted in the caller's transaction, so commit right after
        acquiring: the key's usage row stays locked until then.

        Args:
            key_type: Type of key to retrieve
            max_retries: Maximum number of waits for a free key (default: 3)
            retry_delay: Delay in seconds between waits (default: 30)

        Raises:
            ValueError: If no key is available after all retries
        """
        logger.debug(f"Start acquire key {key_type.value}")
        try:
            for attempt in range(1, max_retries + 1):
                key_id = await self._take_usage(key_type)
                if key_id is not None:
                    key = await KeyMapper.to_domain(await self.get(key_id))
                    logger.debug(f"Acquired key {key.id}")
                    return key

                if attempt == max_retries:
                    break
                logger.info(
                    f"No keys available for {key_type.value}, retrying in {retry_delay} seconds "
                    f"(attempt {attempt}/{max_retries})"
                )
                await asyncio.sleep(retry_delay)
        except Exception as e:
            logger.error(f"Failed to get key: {e}")
            raise ValueError(f"Error during get key: {e}") from e

        logger.error(f"Failed to get key after {max_retries} attempts")
        raise ValueError(f"Error during get key: No keys available after {max_retries} attempts")

    async def _take_usage(self, key_type: KeyType):
        for _ in range(self._CONTENDED_ATTEMPTS):
            key_id = await self._usages.take_usage(key_type)
            if key_id is not None:
                return key_id
        return None
