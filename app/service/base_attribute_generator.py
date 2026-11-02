from abc import ABC, abstractmethod
from typing import Any

from app.service.attribute_tool import AttributeToolService
from app.service.llm_client.llm_client import LLMClient
from core.domain.attribute import Attribute
from core.enum.attribute_type import AttributeType
from core.manager_prompt.prompt_manager import PromptManager


class BaseAttributeGenerator(ABC):
    """Base class for all attribute generators using LLM."""

    def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager):
        self._llm_client = llm_client
        self._prompt_manager = prompt_manager

    @property
    def attribute_type(self) -> AttributeType:
        """Override this property in child classes."""
        raise NotImplementedError

    async def generate(self, *args: Any, **kwargs: Any) -> list[Attribute]:
        """
        Template method:
        1. Build prompt from input arguments.
        2. Call LLM.
        3. Parse response into Attribute objects.
        """
        prompt = await self._build_prompt(*args, **kwargs)
        response = await self._llm_client.ask(prompt)
        names = await self._parse_response(response)
        return [
            Attribute.create(name=name.strip(), attr_type=self.attribute_type)
            for name in names
            if name and name.strip()
        ]

    @abstractmethod
    async def _build_prompt(self, *args: Any, **kwargs: Any) -> str:
        """Construct prompt for LLM based on input data."""
        pass

    async def _parse_response(self, raw_response: str) -> list[str]:
        """Convert LLM response into list of attribute names."""
        if not raw_response:
            return []
        return await AttributeToolService.attribute_list_generator(raw_response)
