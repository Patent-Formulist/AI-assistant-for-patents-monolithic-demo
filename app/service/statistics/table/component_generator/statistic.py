from app.service.table.component_generator import BaseComponentGenerator
from core import logger
from core.dto.attribute_sign import AnalogSignsMap, PatentAttributesSignDto

logger = logger.get_logger(__name__)


class StatisticsComponentGenerator(BaseComponentGenerator):
    """Генератор для статистической таблицы аналогов"""

    async def generate(self, patent_attrs_dto: PatentAttributesSignDto, analog_map: AnalogSignsMap):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
