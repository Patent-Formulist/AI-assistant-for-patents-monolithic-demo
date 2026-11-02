from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.http.request_models.drawing import (
    DrawingElementRequest,
    DrawingFigureRequest,
)
from app.http.response_models.drawing import (
    DrawingElementResponse,
    DrawingFigureElementResponse,
    DrawingFigureResponse,
)
from app.service.base import BaseService
from app.service.drawing.repository import (
    DrawingElementRepository,
    DrawingFigureRepository,
    FigureElementRepository,
)
from core import logger
from core.db.models.drawing_element import DrawingElementModel
from core.db.models.drawing_figure import DrawingFigureModel

if TYPE_CHECKING:
    from app.service.patent_application.generator import ParsedFigure

logger = logger.get_logger(__name__)


class DrawingService(BaseService[DrawingElementModel, DrawingElementRepository]):
    """Patent drawings: numbered elements (parts) and figures showing them.

    Every change flags the generated patent application outdated in the same
    transaction. Never commits: the request session owns the transaction.

    Elements and figures are addressed within a patent: an id of another
    patent's element or figure is treated as not found, and element ids given
    for a figure or a reordering are limited to the patent's own elements.
    """

    repository_type = DrawingElementRepository

    def __init__(self, session: AsyncSession, **kwargs):
        super().__init__(session=session, **kwargs)
        self._elements = self.repository
        self._figures = DrawingFigureRepository(session=session)
        self._figure_elements = FigureElementRepository(session=session)

    # --- Elements ---

    async def create_element(
        self, patent_id: int, request: DrawingElementRequest
    ) -> DrawingElementResponse:
        logger.debug(f"Creating element for patent {patent_id}")
        element = await self._add_element(patent_id, request.number, request.description)
        await self._flag_outdated(patent_id)
        return DrawingElementResponse.model_validate(element)

    async def get_elements(self, patent_id: int) -> list[DrawingElementResponse]:
        elements = await self._elements.list_active_by_patent(patent_id)
        return [DrawingElementResponse.model_validate(el) for el in elements]

    async def update_element(
        self, patent_id: int, element_id: int, description: str
    ) -> DrawingElementResponse | None:
        logger.debug(f"Updating element {element_id}")
        element = await self._element(patent_id, element_id)
        if element is None:
            return None
        element.description = description
        element = await self._elements.update(element)
        await self._flag_outdated(element.patent_id)
        return DrawingElementResponse.model_validate(element)

    async def delete_element(self, patent_id: int, element_id: int) -> bool:
        logger.debug(f"Deleting element {element_id}")
        element = await self._element(patent_id, element_id)
        if element is None:
            return False
        element.is_active = False
        await self._elements.update(element)
        await self._flag_outdated(element.patent_id)
        return True

    async def reorder_elements(
        self, patent_id: int, element_ids: list[int]
    ) -> list[DrawingElementResponse]:
        """Number the given elements 1..N in the given order; unknown ids are skipped."""
        logger.debug(f"Reordering elements for patent {patent_id}")
        elements = []
        for number, element_id in enumerate(element_ids, start=1):
            element = await self._element(patent_id, element_id)
            if element is None:
                continue
            element.number = number
            elements.append(await self._elements.update(element))
        await self._flag_outdated(patent_id)
        return [DrawingElementResponse.model_validate(el) for el in elements]

    async def replace_elements(
        self, patent_id: int, descriptions: list[str]
    ) -> list[DrawingElementResponse]:
        """Replace all elements of a patent with a freshly generated list.

        Existing elements are soft-deleted, then the new descriptions are
        stored numbered 1..N in the order they were produced.
        """
        logger.debug(
            f"Replacing elements for patent {patent_id} with {len(descriptions)} generated items"
        )
        await self._elements.deactivate_by_patent(patent_id)
        return await self.import_elements(patent_id, descriptions)

    async def import_elements(
        self, patent_id: int, descriptions: list[str]
    ) -> list[DrawingElementResponse]:
        """Add elements numbered 1..N from a list of descriptions."""
        logger.debug(f"Importing {len(descriptions)} elements for patent {patent_id}")
        elements = [
            await self._add_element(patent_id, number, description.strip())
            for number, description in enumerate(descriptions, start=1)
        ]
        await self._flag_outdated(patent_id)
        return [DrawingElementResponse.model_validate(el) for el in elements]

    async def _element(self, patent_id: int, element_id: int) -> DrawingElementModel | None:
        element = await self._elements.get_active(element_id)
        return element if element is not None and element.patent_id == patent_id else None

    async def _own_element_ids(self, patent_id: int, element_ids: list[int]) -> list[int]:
        """The given ids that are active elements of the patent, in the given order."""
        own = {el.id for el in await self._elements.list_active_by_patent(patent_id)}
        return [eid for eid in element_ids if eid in own]

    # --- Figures ---

    async def _figure(self, patent_id: int, figure_id: int) -> DrawingFigureModel | None:
        figure = await self._figures.get_active(figure_id)
        return figure if figure is not None and figure.patent_id == patent_id else None

    async def create_figure(
        self, patent_id: int, request: DrawingFigureRequest
    ) -> DrawingFigureResponse:
        logger.debug(f"Creating figure for patent {patent_id}")
        figure = await self._figures.add(
            DrawingFigureModel(
                patent_id=patent_id, number=request.number, title=request.title, is_active=True
            )
        )
        valid_element_ids = await self._own_element_ids(patent_id, request.element_ids)
        if valid_element_ids:
            await self._figure_elements.replace_for_figure(figure.id, valid_element_ids)
        await self._flag_outdated(patent_id)
        return await self._figure_to_response(figure)

    async def get_figures(self, patent_id: int) -> list[DrawingFigureResponse]:
        figures = await self._figures.list_active_by_patent(patent_id)
        return [await self._figure_to_response(fig) for fig in figures]

    async def update_figure(
        self, patent_id: int, figure_id: int, title: str, element_ids: list[int]
    ) -> DrawingFigureResponse | None:
        logger.debug(f"Updating figure {figure_id}")
        figure = await self._figure(patent_id, figure_id)
        if figure is None:
            return None
        figure.title = title
        figure = await self._figures.update(figure)
        await self._figure_elements.replace_for_figure(
            figure_id, await self._own_element_ids(patent_id, element_ids)
        )
        await self._flag_outdated(figure.patent_id)
        return await self._figure_to_response(figure)

    async def delete_figure(self, patent_id: int, figure_id: int) -> bool:
        logger.debug(f"Deleting figure {figure_id}")
        figure = await self._figure(patent_id, figure_id)
        if figure is None:
            return False
        figure.is_active = False
        await self._figures.update(figure)
        await self._flag_outdated(figure.patent_id)
        return True

    async def replace_figures(
        self,
        patent_id: int,
        parsed_figures: list["ParsedFigure"],
        elements: list[DrawingElementResponse],
    ) -> list[DrawingFigureResponse]:
        """Replace all figures of a patent with a freshly generated set.

        Element numbers referenced by each figure are resolved against the
        current elements; numbers without a matching element are ignored.
        """
        logger.debug(
            f"Replacing figures for patent {patent_id} with {len(parsed_figures)} generated figures"
        )
        number_to_id = {el.number: el.id for el in elements}
        await self._figures.deactivate_by_patent(patent_id)

        figures = []
        for parsed in parsed_figures:
            figure = await self._figures.add(
                DrawingFigureModel(
                    patent_id=patent_id, number=parsed.number, title=parsed.title, is_active=True
                )
            )
            element_ids = [number_to_id[n] for n in parsed.element_numbers if n in number_to_id]
            if element_ids:
                await self._figure_elements.replace_for_figure(figure.id, element_ids)
            figures.append(figure)

        await self._flag_outdated(patent_id)
        return [await self._figure_to_response(figure) for figure in figures]

    # --- Helpers ---

    async def _add_element(self, patent_id: int, number: int, description: str):
        return await self._elements.add(
            DrawingElementModel(
                patent_id=patent_id, number=number, description=description, is_active=True
            )
        )

    async def _flag_outdated(self, patent_id: int) -> None:
        # Lazy: app.service.patent_application imports this service.
        from app.service.patent_application.outdated import flag_application_outdated

        await flag_application_outdated(self.repository.session, patent_id)

    async def _figure_to_response(self, figure: DrawingFigureModel) -> DrawingFigureResponse:
        elements = await self._elements.list_active_by_figure(figure.id)
        return DrawingFigureResponse(
            id=figure.id,
            patent_id=figure.patent_id,
            number=figure.number,
            title=figure.title,
            elements=[
                DrawingFigureElementResponse(number=el.number, description=el.description)
                for el in elements
            ],
        )
