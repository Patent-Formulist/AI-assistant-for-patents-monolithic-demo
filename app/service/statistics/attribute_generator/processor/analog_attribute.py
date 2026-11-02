from app.service.analog.analog import AnalogService
from app.service.attribute.attribute import AttributeService
from app.service.processor import Processor, UnitOfWork
from app.service.statistics.attribute_generator.raw_data_generator.analog_attribute import (
    AnalogAttributeGenerator,
)
from core import logger
from core.domain.analog import Analog
from core.domain.attribute import Attribute
from core.exceptions import AnalogAttributeCreationError

logger = logger.get_logger(__name__)


class ProcessorAnalogAttributeService(Processor):
    def __init__(
        self,
        uow: UnitOfWork,
        analog_service: AnalogService,
        attribute_service: AttributeService,
        generator: AnalogAttributeGenerator,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def process_generate_analog_attribute(
        self, patent_id: int, analog_ids: list[int] | None = None
    ) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")





