from collections.abc import Sequence

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload

from core.db.models.drawing_element import DrawingElementModel
from core.db.models.drawing_figure import DrawingFigureModel
from core.db.models.figure_element import FigureElementModel


class DrawingElementRepository(SQLAlchemyAsyncRepository[DrawingElementModel]):
    model_type = DrawingElementModel

    async def get_active(self, element_id: int) -> DrawingElementModel | None:
        return await self.get_one_or_none(
            DrawingElementModel.id == element_id, DrawingElementModel.is_active.is_(True)
        )

    async def list_active_by_patent(self, patent_id: int) -> Sequence[DrawingElementModel]:
        return await self.list(
            statement=select(DrawingElementModel)
            .where(
                DrawingElementModel.patent_id == patent_id,
                DrawingElementModel.is_active.is_(True),
            )
            .order_by(DrawingElementModel.number)
        )

    async def list_active_by_figure(self, figure_id: int) -> Sequence[DrawingElementModel]:
        return await self.list(
            statement=select(DrawingElementModel)
            .join(FigureElementModel, FigureElementModel.element_id == DrawingElementModel.id)
            .where(
                FigureElementModel.figure_id == figure_id,
                FigureElementModel.is_active.is_(True),
                DrawingElementModel.is_active.is_(True),
            )
            .order_by(DrawingElementModel.number)
        )

    async def deactivate_by_patent(self, patent_id: int) -> None:
        await self.session.execute(
            update(DrawingElementModel)
            .where(
                DrawingElementModel.patent_id == patent_id,
                DrawingElementModel.is_active.is_(True),
            )
            .values(is_active=False)
            .execution_options(synchronize_session=False)
        )


class DrawingFigureRepository(SQLAlchemyAsyncRepository[DrawingFigureModel]):
    model_type = DrawingFigureModel

    async def get_active(self, figure_id: int) -> DrawingFigureModel | None:
        return await self.get_one_or_none(
            DrawingFigureModel.id == figure_id, DrawingFigureModel.is_active.is_(True)
        )

    async def list_active_by_patent(self, patent_id: int) -> Sequence[DrawingFigureModel]:
        return await self.list(
            statement=select(DrawingFigureModel)
            .options(selectinload(DrawingFigureModel.figure_elements))
            .where(
                DrawingFigureModel.patent_id == patent_id,
                DrawingFigureModel.is_active.is_(True),
            )
            .order_by(DrawingFigureModel.number)
        )

    async def deactivate_by_patent(self, patent_id: int) -> None:
        await self.session.execute(
            update(DrawingFigureModel)
            .where(
                DrawingFigureModel.patent_id == patent_id,
                DrawingFigureModel.is_active.is_(True),
            )
            .values(is_active=False)
            .execution_options(synchronize_session=False)
        )


class FigureElementRepository(SQLAlchemyAsyncRepository[FigureElementModel]):
    model_type = FigureElementModel

    async def replace_for_figure(self, figure_id: int, element_ids: list[int]) -> None:
        """Set the figure's elements to exactly ``element_ids``."""
        await self.session.execute(
            delete(FigureElementModel).where(FigureElementModel.figure_id == figure_id)
        )
        if element_ids:
            await self.add_many(
                [
                    FigureElementModel(figure_id=figure_id, element_id=eid, is_active=True)
                    for eid in element_ids
                ]
            )
