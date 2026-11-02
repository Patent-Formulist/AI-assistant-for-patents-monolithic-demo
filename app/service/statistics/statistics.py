from sqlalchemy.ext.asyncio import AsyncSession

from app.service.base import BaseService
from app.service.statistics.repository import (
    AnalogAttributeSignRepository,
    PatentAttributeSignRepository,
)
from core import logger
from core.db.models.analog_attribute_sign import AnalogAttributeSignModel
from core.db.models.patent_attribute_sign import PatentAttributeSignModel
from core.domain.analog_sign import AnalogAttributeSign
from core.domain.coincidence import Coincidence
from core.domain.patent_sign import PatentAttributeSign
from core.dto.attribute_sign import (
    AnalogSignsDto,
    AnalogSignsMap,
    AttributeSignDetailDto,
    PatentAttributesSignDto,
)
from core.exceptions import (
    AnalogAttributeSignCreationError,
    AnalogAttributeSignDeleteError,
    AnalogSignGetError,
    CoincidenceGetError,
    PatentAttributeSignCreationError,
    PatentAttributeSignDeleteError,
    PatentSignGetError,
)

logger = logger.get_logger(__name__)


class StatisticsService(BaseService[AnalogAttributeSignModel, AnalogAttributeSignRepository]):

    repository_type = AnalogAttributeSignRepository

    def __init__(self, session: AsyncSession, **kwargs):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")


    async def get_coincidences(self, patent_id: int) -> list[Coincidence]:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")


    async def create_patent_signs(self, signs: list[PatentAttributeSign]) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def get_patent_signs(self, patent_id: int) -> PatentAttributesSignDto:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def delete_patent_signs(self, patent_id: int) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")


    async def create_analog_signs(self, signs: list[AnalogAttributeSign]) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def get_analog_signs_map(self, patent_id: int) -> AnalogSignsMap:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def delete_analog_signs(self, analog_ids: list[int]) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
