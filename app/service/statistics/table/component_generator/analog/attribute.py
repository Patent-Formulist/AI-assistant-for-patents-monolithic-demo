from app.service.table.component_generator import BaseComponentGenerator
from core import logger
from core.dto.analog_attribute import AnalogAttributesGroupDto

logger = logger.get_logger(__name__)


class AnalogAttributesComponentGenerator(BaseComponentGenerator):
    """Генератор для таблицы с атрибутами аналогов"""

    async def generate(self, analog_groups: list[AnalogAttributesGroupDto]):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
