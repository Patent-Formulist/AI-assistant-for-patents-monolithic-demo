from app.service.analog.analog import AnalogService
from app.service.drawing.drawing_service import DrawingService
from app.service.identity_prototype.identity_prototype import IdentifyPrototypeService
from app.service.patent.patent import PatentService
from app.service.patent_application.generator import PatentApplicationGenerator
from app.service.patent_application.service import PatentApplicationService
from app.service.processor import UnitOfWork
from core.exceptions import IdentifyPrototypeGetError


class ProcessorPatentApplicationService:
    """Patent application documents for a patent via LLM (ADR 0002)."""

    def __init__(
        self,
        uow: UnitOfWork,
        application_service: PatentApplicationService,
        patent_service: PatentService,
        drawing_service: DrawingService,
        identify_prototype_service: IdentifyPrototypeService,
        analog_service: AnalogService,
        generator: PatentApplicationGenerator,
    ):
        self._uow = uow
        self._application_service = application_service
        self._patent_service = patent_service
        self._drawing_service = drawing_service
        self._identify_prototype_service = identify_prototype_service
        self._analog_service = analog_service
        self._generator = generator

    async def generate_application(self, patent_id: int) -> None:
        """Generate abstract, claims and description and save them, replacing the old ones."""
        # Read in its own transaction so the connection is released before the LLM calls
        async with self._uow:
            patent = await self._patent_service.get_patent(patent_id)
            elements = await self._drawing_service.get_elements(patent_id)
            figures = await self._drawing_service.get_figures(patent_id)
            analog_data, analog_num = await self._collect_prototype(patent_id)

        abstract = await self._generator.generate_abstract(patent)
        claims = await self._generator.generate_claims(patent, elements)
        description = await self._generator.generate_description(
            patent, elements, figures, analog_data, analog_num
        )

        async with self._uow:
            await self._application_service.save_generated(
                patent_id=patent_id,
                abstract=abstract,
                claims=claims,
                description=description,
            )

    async def _collect_prototype(self, patent_id: int) -> tuple[str, str]:
        """Build prototype description and Rospatent number for the description prompt.

        Returns empty strings when no prototype is identified for the patent.
        """
        try:
            identify = await self._identify_prototype_service.get_by_patent(patent_id)
        except IdentifyPrototypeGetError:
            return "", ""

        analog = await self._analog_service.get_analog(analog_id=identify.analog_id)

        features = []
        for row in identify.row:
            title = row.analog_attr_title
            if title and title.strip() and title != "None" and title not in features:
                features.append(title)

        parts = [f"Название: {analog.title}"]
        if analog.abstract:
            parts.append(f"Реферат: {analog.abstract}")
        if analog.claims:
            parts.append(f"Формула: {analog.claims}")
        if features:
            joined = "; ".join(features)
            parts.append(f"Совпадающие с заявляемым изобретением признаки: {joined}")

        return "\n".join(parts), analog.analog_num or ""
