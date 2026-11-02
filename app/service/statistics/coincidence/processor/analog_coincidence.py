from app.service.analog.analog import AnalogService
from app.service.attribute.attribute import AttributeService
from app.service.processor import Processor, UnitOfWork
from app.service.statistics.coincidence.raw_data_generator.checking_analog import (
    CheckingAnalogGenerator,
)
from app.service.statistics.statistics import StatisticsService
from core import logger
from core.domain.analog import Analog
from core.domain.analog_sign import AnalogAttributeSign
from core.domain.attribute import Attribute
from core.dto.attribute_sign import AnalogSignsMap
from core.exceptions.domain.coincidence import AnalogAttributeSignCreationError

logger = logger.get_logger(__name__)


class ProcessorAnalogCoincidencesService(Processor):
    def __init__(
        self,
        uow: UnitOfWork,
        statistics_service: StatisticsService,
        attribute_service: AttributeService,
        analog_service: AnalogService,
        generator: CheckingAnalogGenerator,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def process_generate_analog_coincidences(self, patent_id: int) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")


