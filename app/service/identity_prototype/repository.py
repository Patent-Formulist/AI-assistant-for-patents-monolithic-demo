from collections.abc import Sequence

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import delete, select
from sqlalchemy.orm import aliased

from core.db.models.analog import AnalogModel
from core.db.models.attribute import AttributeModel
from core.db.models.identify_attribute import IdentifyAttributeModel


class IdentifyAttributeRepository(SQLAlchemyAsyncRepository[IdentifyAttributeModel]):
    model_type = IdentifyAttributeModel

    async def list_rows_by_patent(
        self, patent_id: int
    ) -> Sequence[tuple[int, str, int | None, str | None, int | None, str | None, int, str]]:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def delete_by_patent(self, patent_id: int) -> int:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
