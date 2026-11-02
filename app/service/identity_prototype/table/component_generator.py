from typing import Any

from app.service.table.component_generator import BaseComponentGenerator
from core import logger
from core.dto.identify_attribute import IdentifyPrototypeDto

logger = logger.get_logger(__name__)


class IdentifyAnalogComponentGenerator(BaseComponentGenerator):
    """Генератор для таблицы идентификации аналога"""

    async def generate(
        self, identify: IdentifyPrototypeDto
    ) -> tuple[list[str] | None, list[list[Any]] | None]:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
