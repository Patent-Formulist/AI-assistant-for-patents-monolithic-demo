import json
from collections import defaultdict

from app.service.base_attribute_generator import BaseAttributeGenerator
from core import logger
from core.db.models.attribute import AttributeModel
from core.enum.ai_purpose import AIPurpose
from core.enum.attribute_type import AttributeType

logger = logger.get_logger(__name__)


class MatchingAnalogAttributeGenerator(BaseAttributeGenerator):
    """Generator for matching analog attributes."""

    @property
    def attribute_type(self) -> AttributeType:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

