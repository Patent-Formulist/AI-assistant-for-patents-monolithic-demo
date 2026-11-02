from app.service.table.component_generator import BaseComponentGenerator
from core import logger
from core.dto.attribute_sign import AnalogSignsMap

logger = logger.get_logger(__name__)


class AnalogAttributeCheckingComponentGenerator(BaseComponentGenerator):
    """Генератор для таблицы совпадений атрибутов"""

    async def generate(self, analog_signs_map: AnalogSignsMap):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
