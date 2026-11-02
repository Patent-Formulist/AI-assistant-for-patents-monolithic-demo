from typing import Any

from app.service.attribute.attribute import AttributeService
from app.service.statistics.statistics import StatisticsService
from core.domain.attribute import Attribute
from core.domain.coincidence import Coincidence
from core.dto.attribute_sign import AnalogSignsMap, PatentAttributesSignDto




class StatisticsFrontendQuery:
    """Read model for the statistics page: attributes, signs and coincidences."""

    def __init__(self, statistics_service: StatisticsService, attribute_service: AttributeService):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def get(self, patent_id: int) -> dict[str, Any]:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

