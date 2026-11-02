import time

from app.service.llm_client.llm_client import LLMClient
from core import logger
from core.domain.analog import Analog
from core.domain.attribute import Attribute
from core.domain.patent import Patent
from core.dto.identify_attribute import IdentifyPrototypeDto

from .dto_builder import IdentityDtoBuilder
from .prompt_builder import IdentityPrototypePromptBuilder

logger = logger.get_logger(__name__)


class IdentityGenerator:
    def __init__(
        self,
        llm_client: LLMClient,
        dto_builder: IdentityDtoBuilder,
        prompt_builder: IdentityPrototypePromptBuilder,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def generate_data(
        self,
        analog: Analog,
        patent_attributes: list[Attribute],
        general_attributes: list[Attribute],
        patent: Patent,
    ) -> IdentifyPrototypeDto:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
