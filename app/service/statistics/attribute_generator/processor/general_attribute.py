from app.service.attribute.attribute import AttributeService
from app.service.processor import Processor, UnitOfWork
from app.service.statistics.attribute_generator.raw_data_generator.general_attribute import (
    GeneralAttributeGenerator,
)
from core import logger
from core.domain.attribute import Attribute
from core.domain.patent_attribute import PatentAttributeIDPair
from core.enum.attribute_type import AttributeType
from core.exceptions import GeneralAttributeCreationError

logger = logger.get_logger(__name__)


class ProcessorGeneralAttributeService(Processor):
    def __init__(
        self,
        uow: UnitOfWork,
        attribute_service: AttributeService,
        generator: GeneralAttributeGenerator,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def process_generate_general_attribute(self, patent_id: int) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")






