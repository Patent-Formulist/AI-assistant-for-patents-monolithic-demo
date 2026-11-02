from app.service.table.component_generator import BaseComponentGenerator
from core import logger
from core.domain.attribute import Attribute

logger = logger.get_logger(__name__)


class PatentAttributesComponentGenerator(BaseComponentGenerator):
    """Генератор для таблицы атрибутов основного патента"""

    async def generate(self, attributes: list[Attribute]):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
