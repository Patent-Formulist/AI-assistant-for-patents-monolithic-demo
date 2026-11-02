from app.service.table.component_generator import BaseComponentGenerator
from core import logger
from core.dto.attribute_sign import PatentAttributesSignDto

logger = logger.get_logger(__name__)


class PatentAttributeCheckingComponentGenerator(BaseComponentGenerator):
    async def generate(self, patent_attributes: PatentAttributesSignDto):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
