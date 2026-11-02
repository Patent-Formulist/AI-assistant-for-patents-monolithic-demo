from collections.abc import Sequence

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select

from core.db.models.analog import AnalogModel
from core.db.models.patent_analog import PatentAnalogModel


class AnalogRepository(SQLAlchemyAsyncRepository[AnalogModel]):
    model_type = AnalogModel

    async def list_by_patent(self, patent_id: int) -> Sequence[AnalogModel]:
        return await self.list(
            statement=select(AnalogModel)
            .join(PatentAnalogModel, AnalogModel.id == PatentAnalogModel.analog_id)
            .where(PatentAnalogModel.patent_id == patent_id, AnalogModel.is_active)
        )

    async def list_by_numbers(self, patent_id: int, numbers: list[str]) -> Sequence[AnalogModel]:
        """Active analogs of the patent with these numbers."""
        return await self.list(
            statement=select(AnalogModel)
            .join(PatentAnalogModel, PatentAnalogModel.analog_id == AnalogModel.id)
            .where(
                PatentAnalogModel.patent_id == patent_id,
                AnalogModel.number.in_(numbers),
                AnalogModel.is_active.is_(True),
            )
        )

    async def list_by_ids(self, analog_ids: list[int]) -> Sequence[AnalogModel]:
        return await self.list(AnalogModel.id.in_(analog_ids), AnalogModel.is_active.is_(True))


class PatentAnalogRepository(SQLAlchemyAsyncRepository[PatentAnalogModel]):
    model_type = PatentAnalogModel

    async def list_linked_analog_ids(self, patent_id: int, analog_ids: list[int]) -> set[int]:
        result = await self.session.execute(
            select(PatentAnalogModel.analog_id).where(
                PatentAnalogModel.patent_id == patent_id,
                PatentAnalogModel.analog_id.in_(analog_ids),
            )
        )
        return set(result.scalars().all())
