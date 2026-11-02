from app.service.attribute.attribute import AttributeService
from app.service.processor import Processor, UnitOfWork
from app.service.statistics.attribute_generator.raw_data_generator.matching_analog_attributes import (
    MatchingAnalogAttributeGenerator,
)
from core import logger
from core.db.models.attribute import AttributeModel
from core.domain.attribute import Attribute
from core.domain.patent_attribute import PatentAttributeIDPair
from core.enum.attribute_type import AttributeType
from core.exceptions import MatchingAnalogAttributeCreationError

logger = logger.get_logger(__name__)


class ProcessorMatchingAnalogAttributeService(Processor):
    def __init__(
        self,
        uow: UnitOfWork,
        generator: MatchingAnalogAttributeGenerator,
        attribute_service: AttributeService,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def process_generate_matcher_analog_attribute(self, patent_id: int) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")





