import asyncio
from abc import ABC, abstractmethod
from functools import partial
from typing import Any

from app.service.batch import gather_all
from app.service.llm_client.llm_client import LLMClient
from core import logger
from core.domain.attribute import Attribute
from core.manager_prompt.prompt_manager import PromptManager

logger = logger.get_logger(__name__)


class BaseCheckingGenerator[T](ABC):
    """Base class for LLM-based sign checking generators."""

    # What the entities are, in the error shown to the user
    batch_name = "аналоги"

    def __init__(
        self,
        llm_client: LLMClient,
        prompt_manager: PromptManager,
        max_concurrent: int = 10,
    ):
        self._llm_client = llm_client
        self._prompt_manager = prompt_manager
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def generate_single(self, entity: Any, attributes: list[Attribute]) -> T:
        """Generate signs for a single entity (patent or analog)."""
        if not self._has_required_data(entity):
            logger.warning("Entity has insufficient data, skipping")
            return self._empty_result(entity)
        prompt = await self._build_prompt(entity, attributes)
        response = await self._llm_client.ask(prompt)
        return await self._parse_response(entity, attributes, response)

    async def generate_batch(
        self, entities: list[Any], attributes: list[Attribute]
    ) -> dict[int, T]:
        """Generate signs for the entities concurrently: entity id -> result.

        Entities without data are skipped. If one still fails after retries,
        BatchItemsFailedError names it: the step fails rather than storing
        coincidences without it.
        """
        return await gather_all(
            {
                self._get_entity_id(entity): partial(
                    self._process_with_semaphore, entity, attributes
                )
                for entity in entities
                if self._has_required_data(entity)
            },
            what=self.batch_name,
        )

    async def _process_with_semaphore(self, entity: Any, attributes: list[Attribute]) -> T:
        """Apply semaphore limit before calling generate_single."""
        async with self._semaphore:
            return await self.generate_single(entity, attributes)

    @abstractmethod
    async def _build_prompt(self, entity: Any, attributes: list[Attribute]) -> str:
        """Build LLM prompt for the given entity and attributes."""
        pass

    @abstractmethod
    async def _parse_response(
        self, entity: Any, attributes: list[Attribute], raw_response: str
    ) -> T:
        """Parse LLM response into a result DTO for the entity."""
        pass

    @abstractmethod
    def _has_required_data(self, entity: Any) -> bool:
        """Check if the entity has enough data to generate signs."""
        pass

    @abstractmethod
    def _get_entity_id(self, entity: Any) -> int:
        """Extract unique identifier from the entity."""
        pass

    @abstractmethod
    def _empty_result(self, entity: Any) -> T:
        """Return an empty/default result when entity lacks data."""
        pass
