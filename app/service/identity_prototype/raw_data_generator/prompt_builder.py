import json

from core import logger
from core.domain.analog import Analog
from core.domain.attribute import Attribute
from core.domain.patent import Patent
from core.enum.ai_purpose import AIPurpose
from core.manager_prompt.prompt_manager import PromptManager

logger = logger.get_logger(__name__)


class IdentityPrototypePromptBuilder:
    def __init__(self, prompt_manager: PromptManager):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def build(
        self,
        analog: Analog,
        patent_attributes: list[Attribute],
        general_attributes: list[Attribute],
        patent: Patent,
    ) -> str:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
