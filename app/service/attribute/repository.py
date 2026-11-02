from collections.abc import Sequence

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import delete, select

from core.db.models.analog import AnalogModel
from core.db.models.analog_attributes import AnalogAttributeModel
from core.db.models.attribute import AttributeModel
from core.db.models.patent_analog import PatentAnalogModel
from core.db.models.patent_attributes import PatentAttributeModel
from core.enum.attribute_type import AttributeType


class AttributeRepository(SQLAlchemyAsyncRepository[AttributeModel]):
    model_type = AttributeModel

    async def list_patent_attributes(self, patent_id: int) -> Sequence[AttributeModel]:
        """Attributes linked to the patent, except MATCHING_ANALOG."""
        return await self.list(
            statement=select(AttributeModel)
            .join(PatentAttributeModel, PatentAttributeModel.attribute_id == AttributeModel.id)
            .where(
                PatentAttributeModel.patent_id == patent_id,
                AttributeModel.attribute_type != AttributeType.MATCHING_ANALOG,
            )
            .distinct()
        )

    async def list_by_patent_and_type(
        self, patent_id: int, attribute_type: AttributeType
    ) -> Sequence[AttributeModel]:
        return await self.list(
            statement=select(AttributeModel)
            .join(PatentAttributeModel, PatentAttributeModel.attribute_id == AttributeModel.id)
            .where(
                PatentAttributeModel.patent_id == patent_id,
                AttributeModel.attribute_type == attribute_type,
            )
            .distinct()
        )

    async def list_analog_attribute_rows(
        self, patent_id: int
    ) -> Sequence[tuple[int, str, AttributeModel]]:
        """(analog_id, analog_title, attribute) for every active analog of the patent."""
        result = await self.session.execute(
            select(
                AnalogModel.id.label("analog_id"),
                AnalogModel.title.label("analog_title"),
                AttributeModel,
            )
            .select_from(AnalogModel)
            .join(AnalogAttributeModel, AnalogAttributeModel.analog_id == AnalogModel.id)
            .join(AttributeModel, AttributeModel.id == AnalogAttributeModel.attribute_id)
            .join(PatentAnalogModel, PatentAnalogModel.analog_id == AnalogModel.id)
            .where(PatentAnalogModel.patent_id == patent_id, AnalogModel.is_active)
            .distinct()
        )
        return result.tuples().all()

    async def delete_analog_attributes_by_patent(
        self, patent_id: int, analog_ids: Sequence[int] | None = None
    ) -> int:
        """Delete the ANALOG attributes of the patent's analogs with their analog links.

        ``analog_ids`` limits it to those analogs. ANALOG attributes are linked to
        analogs (analog_attributes), not to the patent, so delete_by_patent_and_type
        never finds them.
        """
        query = (
            select(AttributeModel.id)
            .join(AnalogAttributeModel, AnalogAttributeModel.attribute_id == AttributeModel.id)
            .join(PatentAnalogModel, PatentAnalogModel.analog_id == AnalogAttributeModel.analog_id)
            .where(
                PatentAnalogModel.patent_id == patent_id,
                AttributeModel.attribute_type == AttributeType.ANALOG,
            )
            .distinct()
        )
        if analog_ids is not None:
            query = query.where(AnalogAttributeModel.analog_id.in_(analog_ids))
        attribute_ids = (await self.session.scalars(query)).all()
        if not attribute_ids:
            return 0

        await self.session.execute(
            delete(AnalogAttributeModel).where(AnalogAttributeModel.attribute_id.in_(attribute_ids))
        )
        await self.session.execute(
            delete(AttributeModel).where(AttributeModel.id.in_(attribute_ids))
        )
        return len(attribute_ids)

    async def delete_by_patent_and_type(self, patent_id: int, attribute_type: AttributeType) -> int:
        """Delete patent links of the given type together with the attributes themselves."""
        attribute_ids = (
            await self.session.scalars(
                select(AttributeModel.id)
                .join(
                    PatentAttributeModel,
                    PatentAttributeModel.attribute_id == AttributeModel.id,
                )
                .where(
                    PatentAttributeModel.patent_id == patent_id,
                    AttributeModel.attribute_type == attribute_type,
                )
            )
        ).all()
        if not attribute_ids:
            return 0

        await self.session.execute(
            delete(PatentAttributeModel).where(
                PatentAttributeModel.patent_id == patent_id,
                PatentAttributeModel.attribute_id.in_(attribute_ids),
            )
        )
        await self.session.execute(
            delete(AttributeModel).where(AttributeModel.id.in_(attribute_ids))
        )
        return len(attribute_ids)


class PatentAttributeRepository(SQLAlchemyAsyncRepository[PatentAttributeModel]):
    model_type = PatentAttributeModel


class AnalogAttributeRepository(SQLAlchemyAsyncRepository[AnalogAttributeModel]):
    model_type = AnalogAttributeModel
