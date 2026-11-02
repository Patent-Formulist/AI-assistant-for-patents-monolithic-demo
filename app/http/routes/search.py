from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.http.request_models.analog import AnalogRequest
from app.http.response_models import (
    AnalogResponse,
)
from app.http.swagger.analog.get import AnalogGetResponses
from app.service.analog.analog import AnalogService
from app.service.analog.search.analog_search import ProcessorAnalogSearchService
from app.service.analog.search.edit_orchestrator import SearchEditOrchestratorService
from core import logger
from core.data_mapper.analog.analog import AnalogMapper
from core.data_mapper.analog.analogs import AnalogsMapper
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.analog.analog import get_analog_service
from core.dependencies.analog.search import (
    get_analog_search_processor,
    get_search_edit_orchestrator,
)
from core.dependencies.auth import CurrentUserId
from core.dependencies.dto import (
    get_patent_analog_id,
    get_user_patent_id_pair_body,
    get_user_patent_id_pair_header,
)
from core.domain.analog import Analog
from core.domain.user_patent import UserPatentIDPair

router = APIRouter(prefix="/api/v2/processor", tags=["Processor_Search"])
logger = logger.get_logger(__name__)
# Dependencies
UserPatentIDPairDep = Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_header)]
UserPatentIDPairBodyDep = Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_body)]
AnalogServiceDep = Annotated[AnalogService, Depends(get_analog_service)]
# Dependencies
ProcessorAnalogSearchServiceDep = Annotated[
    ProcessorAnalogSearchService, Depends(get_analog_search_processor)
]
SearchEditOrchestratorServiceDep = Annotated[
    SearchEditOrchestratorService, Depends(get_search_edit_orchestrator)
]


#################################################################################
# GET
#################################################################################
@auth_doc
@router.get(
    "/patent/{patent_uuid}/search/",
    summary="Get analogs search",
    responses=AnalogGetResponses.get_responses(),
)
@handle_exceptions
async def get_analogs_search(user_patent: UserPatentIDPairDep, analog_service: AnalogServiceDep):
    logger.debug(f"Request to get analogs from user {str(user_patent.user_id)[:8]}")
    result: list[Analog] = await analog_service.get_analogs(user_patent.patent_id)
    response = AnalogsMapper.to_pydantic_response(result)
    return response or AnalogResponse(analogs={})


@auth_doc
@router.get(
    "/patent/{patent_uuid}/search/{analog_uuid}/}",
    summary="Get analog by uuid",
    responses=AnalogGetResponses.get_responses(),
)
@handle_exceptions
async def get_analog_by_uuid(
    analog_uuid: Annotated[int, Depends(get_patent_analog_id)], analog_service: AnalogServiceDep
):
    logger.debug(f"Request to get analog {analog_uuid}")
    result: Analog = await analog_service.get_analog(analog_uuid)
    response = AnalogMapper.to_pydantic(result)
    return response or AnalogResponse(analogs={})


#################################################################################
# POST
#################################################################################
@auth_doc
@router.post("/search/batch", summary="Create patent analogs search")
@handle_exceptions
async def create_patent_analogs_search(
    user_patent: UserPatentIDPairBodyDep, processor: ProcessorAnalogSearchServiceDep
) -> JSONResponse:
    """
    Start a bulk analog search pipeline for a given patent.

    Returns job_id for tracking progress.
    """
    logger.debug(
        f"Request to create patent analogs search for user {str(user_patent.user_id)[:10]}"
    )
    job_id = await processor.start_patent_search(
        patent_id=user_patent.patent_id,
        user_id=user_patent.user_id,
    )
    return JSONResponse(
        status_code=202,
        content={
            "message": "Patent analogs search pipeline started successfully",
            "task_id": job_id,
        },
    )


@auth_doc
@router.post("/search/{analog_num}", summary="Create analog search")
@handle_exceptions
async def create_analog_search(
    user_patent: UserPatentIDPairBodyDep,
    processor: ProcessorAnalogSearchServiceDep,
    analog_num: str,
) -> JSONResponse:
    """
    Start a single analog search pipeline by analog number.

    Returns job_id for tracking progress.
    """
    logger.debug(
        f"Request to create analog search for user {str(user_patent.user_id)[:10]}, analog {analog_num}"
    )
    job_id = await processor.start_analog_search(
        patent_id=user_patent.patent_id,
        user_id=user_patent.user_id,
        analog_number=analog_num,
    )
    return JSONResponse(
        status_code=202,
        content={
            "message": f"Analog search pipeline started successfully for {analog_num}",
            "task_id": job_id,
        },
    )


#################################################################################
# PUT
#################################################################################
@auth_doc
@router.put("/search/", summary="Edit patent analogs search")
@handle_exceptions
async def edit_patent_analogs_search(
    processor: SearchEditOrchestratorServiceDep,
    request: AnalogRequest,
    user_id: CurrentUserId,
) -> JSONResponse:
    logger.debug("Edit analogs, user %s", user_id)

    patent_id = int(request.patent_id)

    analogs_map: dict[int, Analog] = AnalogsMapper.from_pydantic_to_domain(request)
    await processor.edit(patent_id=patent_id, user_id=user_id, request_analogs=analogs_map)
    return JSONResponse(status_code=200, content={"message": "ok"})
