from app.http.response_models.drawing import (
    DrawingElementResponse,
    DrawingFigureResponse,
)
from app.service.drawing.drawing_service import DrawingService
from app.service.patent.patent import PatentService
from app.service.patent_application.generator import PatentApplicationGenerator
from core import logger

logger = logger.get_logger(__name__)


class DrawingGenerationService:
    """Drives AI generation of the parts list and the figures distribution.

    Wraps the patent source data, the LLM-backed generator and the drawing
    CRUD service so the HTTP layer can expose one button per generation step.
    """

    def __init__(
        self,
        drawing_service: DrawingService,
        patent_service: PatentService,
        generator: PatentApplicationGenerator,
    ):
        self._drawing = drawing_service
        self._patent = patent_service
        self._generator = generator

    async def generate_elements(self, patent_id: int) -> list[DrawingElementResponse]:
        """Generate the numbered list of parts and store it for the patent."""
        logger.debug(f"Generating elements list for patent {patent_id}")
        patent = await self._patent.get_patent(patent_id)
        descriptions = await self._generator.generate_elements_list(patent)
        if not descriptions:
            raise ValueError("Модель не вернула ни одного элемента")
        return await self._drawing.replace_elements(patent_id, descriptions)

    async def generate_figures(self, patent_id: int) -> list[DrawingFigureResponse]:
        """Distribute the patent's existing elements across figures."""
        logger.debug(f"Generating figures for patent {patent_id}")
        patent = await self._patent.get_patent(patent_id)
        elements = await self._drawing.get_elements(patent_id)
        if not elements:
            raise ValueError("Сначала сформируйте список элементов, затем фигуры")
        parsed_figures = await self._generator.generate_figures(patent, elements)
        if not parsed_figures:
            raise ValueError("Модель не вернула ни одной фигуры")
        return await self._drawing.replace_figures(patent_id, parsed_figures, elements)
