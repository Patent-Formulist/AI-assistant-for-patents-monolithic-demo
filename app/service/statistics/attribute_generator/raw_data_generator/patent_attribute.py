from app.service.base_attribute_generator import BaseAttributeGenerator
from core import logger
from core.domain.attribute import Attribute
from core.domain.patent import Patent
from core.enum.ai_purpose import AIPurpose
from core.enum.attribute_type import AttributeType

logger = logger.get_logger(__name__)


class PatentAttributeGenerator(BaseAttributeGenerator):
    @property
    def attribute_type(self) -> AttributeType:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

