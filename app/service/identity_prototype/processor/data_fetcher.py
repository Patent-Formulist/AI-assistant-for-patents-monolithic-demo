import time

from app.service.analog.analog import AnalogService
from app.service.attribute.attribute import AttributeService
from app.service.patent.patent import PatentService
from app.service.statistics.statistics import StatisticsService
from core import logger
from core.domain.analog import Analog
from core.domain.attribute import Attribute
from core.domain.coincidence import Coincidence
from core.domain.patent import Patent
from core.exceptions import ValidationError

logger = logger.get_logger(__name__)


class IdentityDataFetcher:

    def __init__(
        self,
        statistics_service: StatisticsService,
        attribute_service: AttributeService,
        analog_service: AnalogService,
        patent_service: PatentService,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def fetch(
        self, patent_id: int
    ) -> tuple[Analog, list[Attribute], list[Attribute], Patent]:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

