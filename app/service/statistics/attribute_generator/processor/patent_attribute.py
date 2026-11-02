from app.service.attribute.attribute import AttributeService
from app.service.patent.patent import PatentService
from app.service.processor import Processor, UnitOfWork
from app.service.statistics.attribute_generator.raw_data_generator.patent_attribute import (
    PatentAttributeGenerator,
)
from core import logger
from core.domain.attribute import Attribute
from core.domain.patent_attribute import PatentAttributeIDPair
from core.enum.attribute_type import AttributeType
from core.exceptions import MatchingAnalogAttributeCreationError

logger = logger.get_logger(__name__)


class ProcessorPatentAttributeService(Processor):
    def __init__(
        self,
        uow: UnitOfWork,
        generator: PatentAttributeGenerator,
        attribute_service: AttributeService,
        patent_service: PatentService,  # Added missing dependency
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def process_generate_patent_attribute(self, patent_id: int) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")





