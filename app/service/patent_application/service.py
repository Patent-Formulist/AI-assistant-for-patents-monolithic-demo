from datetime import datetime

from app.http.request_models.patent_application import PatentApplicationUpdateRequest
from app.http.response_models.patent_application import (
    ClaimsGraphResponse,
    PatentApplicationResponse,
)
from app.service.base import BaseService
from app.service.patent_application.claims_graph import build_claims_graph
from app.service.patent_application.repository import PatentApplicationRepository
from core import logger
from core.db.models.patent_application import PatentApplicationModel

logger = logger.get_logger(__name__)


class PatentApplicationService(BaseService[PatentApplicationModel, PatentApplicationRepository]):
    """Generated patent application documents: abstract, claims, description."""

    repository_type = PatentApplicationRepository

    async def get(self, patent_id: int) -> PatentApplicationResponse | None:
        application = await self.repository.get_by_patent(patent_id)
        if application is None:
            return None
        return PatentApplicationResponse.model_validate(application)

    async def get_claims_graph(self, patent_id: int) -> ClaimsGraphResponse | None:
        application = await self.repository.get_by_patent(patent_id)
        if application is None or not application.claims:
            return None
        return build_claims_graph(application.claims)

    async def update(
        self, patent_id: int, request: PatentApplicationUpdateRequest
    ) -> PatentApplicationResponse | None:
        """Edit the documents by hand; fields not sent are kept."""
        application = await self.repository.get_by_patent(patent_id)
        if application is None:
            return None
        if request.abstract is not None:
            application.abstract = request.abstract
        if request.claims is not None:
            application.claims = request.claims
        if request.description is not None:
            application.description = request.description
        application = await self.repository.update(application)
        return PatentApplicationResponse.model_validate(application)

    async def save_generated(
        self, patent_id: int, abstract: str, claims: list[str], description: str
    ) -> None:
        """Store freshly generated documents; the application is no longer outdated."""
        application = await self.repository.get_by_patent(patent_id)
        fields = dict(
            abstract=abstract,
            claims=claims,
            description=description,
            generated_at=datetime.utcnow(),
            is_outdated=False,
        )
        if application is None:
            await self.repository.add(PatentApplicationModel(patent_id=patent_id, **fields))
            return
        for name, value in fields.items():
            setattr(application, name, value)
        await self.repository.update(application)
