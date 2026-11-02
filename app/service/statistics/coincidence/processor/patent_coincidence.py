from app.service.attribute.attribute import AttributeService
from app.service.patent.patent import PatentService
from app.service.processor import Processor, UnitOfWork
from app.service.statistics.coincidence.raw_data_generator.checking_patent import (
    CheckingPatentGenerator,
)
from app.service.statistics.statistics import StatisticsService
from core import logger
from core.domain.attribute import Attribute
from core.domain.patent_sign import PatentAttributeSign
from core.dto.attribute_sign import PatentAttributesSignDto
from core.exceptions import PatentAttributeSignCreationError

logger = logger.get_logger(__name__)


class ProcessorPatentCoincidencesService(Processor):
    def __init__(
        self,
        uow: UnitOfWork,
        statistics_service: StatisticsService,
        attribute_service: AttributeService,
        patent_service: PatentService,
        generator: CheckingPatentGenerator,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def process_generate_patent_coincidences(self, patent_id: int) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

