from app.service.table.component_generator import BaseComponentGenerator
from core import logger
from core.domain.attribute import Attribute

logger = logger.get_logger(__name__)


class AttributesMatherComponentGenerator(BaseComponentGenerator):
    """Генератор для таблицы с маппингом атрибутов патента"""

    async def generate(self, attributes_mather: list[Attribute]):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
