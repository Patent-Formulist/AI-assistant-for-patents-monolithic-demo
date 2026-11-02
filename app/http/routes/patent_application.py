from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.http.request_models.patent_application import PatentApplicationUpdateRequest
from app.http.response_models.patent_application import (
    ClaimsGraphResponse,
    PatentApplicationResponse,
)
from app.service.patent.patent import PatentService
from app.service.patent_application.exporter import PatentApplicationExporter
from app.service.patent_application.pipeline import ProcessorApplicationPipelineService
from app.service.patent_application.service import PatentApplicationService
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.dependencies import get_db
from core.dependencies.dto import get_user_patent_id_pair_header
from core.dependencies.patent import get_patent_service
from core.dependencies.patent_application import get_application_pipeline, get_application_service
from core.domain.user_patent import UserPatentIDPair

router = APIRouter(
    prefix="/api/v2/patents/{patent_uuid}/application",
    tags=["Patent Application"],
)

UserPatentIDPairDep = Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_header)]
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
ApplicationPipelineDep = Annotated[
    ProcessorApplicationPipelineService, Depends(get_application_pipeline)
]
ApplicationServiceDep = Annotated[PatentApplicationService, Depends(get_application_service)]
PatentServiceDep = Annotated[PatentService, Depends(get_patent_service)]


#################################################################################
# GET
#################################################################################
@auth_doc
@router.get(
    "/",
    summary="Get patent application documents",
    response_model=PatentApplicationResponse,
)
@handle_exceptions
async def get_application(
    user_patent: UserPatentIDPairDep,
    service: ApplicationServiceDep,
):
    application = await service.get(user_patent.patent_id)
    if not application:
        # No application generated yet: return an empty payload (200) so the
        # preparation page can show the "generate" state without a client error.
        return PatentApplicationResponse(patent_id=user_patent.patent_id)
    return application


@auth_doc
@router.get(
    "/claims-graph",
    summary="Get claims dependency graph (families and colours)",
    response_model=ClaimsGraphResponse,
)
@handle_exceptions
async def get_claims_graph(
    user_patent: UserPatentIDPairDep,
    service: ApplicationServiceDep,
):
    graph = await service.get_claims_graph(user_patent.patent_id)
    if graph is None:
        raise ValueError("Patent application not found. Run /generate first.")
    return graph


#################################################################################
# POST
#################################################################################
@auth_doc
@router.post(
    "/generate",
    summary="Generate patent application documents via AI",
    status_code=202,
)
@handle_exceptions
async def generate_application(
    user_patent: UserPatentIDPairDep,
    processor: ApplicationPipelineDep,
) -> JSONResponse:
    job_id = await processor.run_application_pipeline(
        user_id=user_patent.user_id,
        patent_id=user_patent.patent_id,
    )
    return JSONResponse(
        status_code=202,
        content={"message": "Генерация заявки запущена", "job_id": job_id},
    )


@auth_doc
@router.put(
    "/",
    summary="Update patent application documents",
    response_model=PatentApplicationResponse,
)
@handle_exceptions
async def update_application(
    user_patent: UserPatentIDPairDep,
    request: PatentApplicationUpdateRequest,
    service: ApplicationServiceDep,
):
    application = await service.update(user_patent.patent_id, request)
    if not application:
        raise ValueError("Patent application not found. Run /generate first.")
    return application


@auth_doc
@router.post(
    "/export",
    summary="Export patent application to DOCX",
)
@handle_exceptions
async def export_application(
    user_patent: UserPatentIDPairDep,
    service: ApplicationServiceDep,
    patent_service: PatentServiceDep,
):
    application = await service.get(user_patent.patent_id)
    if not application:
        raise ValueError("Patent application not found. Run /generate first.")

    patent = await patent_service.get_patent(user_patent.patent_id)
    buffer = PatentApplicationExporter.export_to_docx(patent.name, application)

    filename = f"patent_application_{user_patent.patent_id}.docx"
    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
