from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Response,
)

from app.http.request_models import PatentFieldsRequest
from app.http.request_models.patent import LastUIButtonRequest
from app.http.response_models import (
    PatentFieldsResponse,
    PatentResponse,
    PatentUUIDResponse,
)
from app.http.response_models.patent import PatentProgressResponse
from app.http.swagger.patent.delete import PatentDeleteResponses
from app.http.swagger.patent.get import PatentGetResponses, PatentsGetResponses
from app.http.swagger.patent.post import PatentCreationResponses
from app.http.swagger.patent.put import PatentEditResponses
from app.service.patent.patent import PatentService
from app.service.user_patent_UI_progress.progress import PatentProgressQuery
from app.service.user_patent_UI_progress.user_patent_UI_progress import (
    UserPatentUIProgressService,
)
from core import logger
from core.data_mapper.patent.patent import PatentMapper
from core.data_mapper.patent.patents import PatentsMapper
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.auth import CurrentUserId
from core.dependencies.dto import get_user_patent_id_pair_header
from core.dependencies.patent import get_patent_service
from core.dependencies.user_patent_UI_progress import (
    get_patent_progress_query,
    get_user_patent_UI_progress_service,
)
from core.domain.patent import Patent
from core.domain.user_patent import UserPatentIDPair

router = APIRouter(prefix="/api/v2/patents", tags=["Patent"])
logger = logger.get_logger(__name__)


UserPatentIDPairDep = Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_header)]
PatentServiceDep = Annotated[PatentService, Depends(get_patent_service)]
UserPatentUIProgressServiceDep = Annotated[
    UserPatentUIProgressService, Depends(get_user_patent_UI_progress_service)
]
PatentProgressQueryDep = Annotated[PatentProgressQuery, Depends(get_patent_progress_query)]


#################################################################################
# DELETE
#################################################################################
@auth_doc
@router.delete(
    "/{patent_uuid}/",
    summary="Delete a patent",
    description="Delete a patent for the authenticated user and returns 200",
    responses=PatentDeleteResponses.get_responses(),
    response_model=PatentUUIDResponse,
)
@handle_exceptions
async def delete_patent(
    upip: UserPatentIDPairDep,
    patent_service: PatentServiceDep,
):
    logger.debug(f"Request to delete a patent from user {str(upip.user_id)[:10]}")
    await patent_service.delete_patent(upip)
    return PatentUUIDResponse(patent_uuid=str(upip.patent_id))


#################################################################################
# GET
#################################################################################
@auth_doc
@router.get(
    "/",
    summary="Get patents",
    responses=PatentsGetResponses.get_responses(),
    response_model=PatentResponse,
)
@handle_exceptions
async def get_patents(
    user_id: CurrentUserId,
    patent_service: PatentServiceDep,
):
    logger.debug(f"Request to get patents from user {user_id}")
    patents: list[Patent] = await patent_service.get_patents(user_id)
    patent_responses = PatentsMapper.to_pydantic(patents)
    return patent_responses or PatentResponse(patents={})


@auth_doc
@router.get(
    "/{patent_uuid}/",
    summary="Get patent",
    responses=PatentGetResponses.get_responses(),
    response_model=PatentFieldsResponse,
)
@handle_exceptions
async def get_patent(
    user_patent: UserPatentIDPairDep,
    patent_service: PatentServiceDep,
):
    logger.debug(f"Request to get patent from user {str(user_patent.user_id)[:8]}")
    patent: Patent = await patent_service.get_patent(user_patent.patent_id)
    return PatentMapper.to_pydantic(patent) if patent else PatentFieldsResponse()


@auth_doc
@router.get(
    "/{patent_uuid}/progress/",
    summary="Get patent progress for frontend reload",
    response_model=PatentProgressResponse,
)
@handle_exceptions
async def get_patent_progress(
    user_patent: UserPatentIDPairDep,
    progress_query: PatentProgressQueryDep,
):
    data = await progress_query.get(
        user_id=user_patent.user_id,
        patent_id=user_patent.patent_id,
    )
    if not data:
        return PatentProgressResponse()
    return PatentProgressResponse(**data)


#################################################################################
# POST
#################################################################################
@auth_doc
@router.post(
    "/",
    summary="Create a new patent",
    responses=PatentCreationResponses.get_responses(),
    response_model=PatentUUIDResponse,
)
@handle_exceptions
async def create_patent(
    patent_request: PatentFieldsRequest,
    user_id: CurrentUserId,
    patent_service: PatentServiceDep,
):
    logger.debug(f"Request to create a patent from user {user_id}")
    patent = PatentMapper.from_pydantic_to_domain(pydantic_model=patent_request, patent_id=None)
    patent_id = await patent_service.create_patent(patent, user_id)
    return PatentUUIDResponse(patent_uuid=str(patent_id))


#################################################################################
# PUT
#################################################################################
@router.put(
    "/{patent_uuid}/",
    summary="Edit a patent",
    description="""
    Edit an existing patent for the authenticated user.

    ## Parameters
    - **patent_uuid**: UUID of the patent to edit (path parameter)

    ## Features
    - Updates only the fields provided in the request
    - Partial updates are supported (send only fields that need changing)
    - Returns the UUID of the edited patent
    - User can only edit patents that belong to them
    """,
    responses=PatentEditResponses.get_responses(),
    response_model=PatentUUIDResponse,
)
@auth_doc
@handle_exceptions
async def edit_patent(
    patent_request: PatentFieldsRequest,
    upip: UserPatentIDPairDep,
    patent_service: PatentServiceDep,
):
    logger.debug(f"Request to edit a patent from user {str(upip.user_id)[:8]}")
    patent = PatentMapper.from_pydantic_to_domain(
        pydantic_model=patent_request, patent_id=upip.patent_id
    )
    await patent_service.edit_patent(patent=patent)
    return PatentUUIDResponse(patent_uuid=str(upip.patent_id))


@auth_doc
@router.put(
    "/{patent_uuid}/progress/last-ui-button",
    summary="Save the last opened section of the patent page",
    description="Remembers which section (ANALOGS_SEARCH | STATISTICS | IDENTITY) "
    "to open after reload or on another device. Returns 204.",
    status_code=204,
)
@handle_exceptions
async def set_last_ui_button(
    request: LastUIButtonRequest,
    user_patent: UserPatentIDPairDep,
    ui_progress_service: UserPatentUIProgressServiceDep,
):
    await ui_progress_service.set_last_ui_button(
        user_id=user_patent.user_id,
        patent_id=user_patent.patent_id,
        button=request.last_ui_button,
    )
    return Response(status_code=204)
