from core import logger
from core.domain.identify_prototype import IdentityPrototype
from core.dto.identify_attribute import IdentifyPrototypeDto

logger = logger.get_logger(__name__)


class IdentifyDomainBuilder:
    async def build(
        self, identify_dto: IdentifyPrototypeDto, patent_id: int, analog_id: int
    ) -> tuple[list[IdentityPrototype], list[tuple[IdentityPrototype, str]]]:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
