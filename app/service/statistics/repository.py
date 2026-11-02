from collections.abc import Sequence

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import and_, delete, func, select

from core.db.models.analog import AnalogModel
from core.db.models.analog_attribute_sign import AnalogAttributeSignModel
from core.db.models.attribute import AttributeModel
from core.db.models.patent_analog import PatentAnalogModel
from core.db.models.patent_attribute_sign import PatentAttributeSignModel


class PatentAttributeSignRepository(SQLAlchemyAsyncRepository[PatentAttributeSignModel]):
    model_type = PatentAttributeSignModel

    async def list_sign_rows(self, patent_id: int) -> Sequence[tuple[int, str, bool]]:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def delete_by_patent(self, patent_id: int) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")


class AnalogAttributeSignRepository(SQLAlchemyAsyncRepository[AnalogAttributeSignModel]):
    model_type = AnalogAttributeSignModel

    async def list_sign_rows(self, patent_id: int) -> Sequence[tuple[int, str, int, str, bool]]:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def delete_by_analogs(self, analog_ids: list[int]) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def list_coincidence_rows(self, patent_id: int) -> Sequence[tuple[int, int]]:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
