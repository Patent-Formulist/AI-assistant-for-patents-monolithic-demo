from core import logger
from core.domain.analog import Analog
from core.domain.attribute import Attribute
from core.dto.identify_attribute import IdentifyPrototypeDto, IdentifyRowDto

from .attribute_matcher import AttributeMatcher
from .response_parser import IdentityResponseParser

logger = logger.get_logger(__name__)


class IdentityDtoBuilder:
    def __init__(self, parser: IdentityResponseParser, matcher: AttributeMatcher):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def build(
        self,
        raw_response: str,
        analog: Analog,
        patent_attributes: list[Attribute],
        general_attributes: list[Attribute],
    ) -> IdentifyPrototypeDto:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
