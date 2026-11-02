import asyncio
import json
from functools import partial

from app.service.base_attribute_generator import BaseAttributeGenerator
from app.service.batch import gather_all
from app.service.llm_client.llm_client import LLMClient
from core import logger
from core.domain.analog import Analog
from core.domain.attribute import Attribute
from core.enum.ai_purpose import AIPurpose
from core.enum.attribute_type import AttributeType
from core.manager_prompt.prompt_manager import PromptManager

logger = logger.get_logger(__name__)


class AnalogAttributeGenerator(BaseAttributeGenerator):
    """Generator of attributes for patent analogs using LLM."""

    def __init__(
        self,
        llm_client: LLMClient,
        prompt_manager: PromptManager,
        max_concurrent: int = 10,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    @property
    def attribute_type(self) -> AttributeType:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def generate_batch(self, analogs: list[Analog]) -> dict[int, list[Attribute]]:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")



