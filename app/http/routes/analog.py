from typing import Annotated

from fastapi import APIRouter, Depends

from app.http.request_models.analog import AnalogFieldsRequest
from app.http.response_models import AnalogFieldsResponse, AnalogUUIDResponse
from app.http.swagger.analog.delete import AnalogDeleteResponses
from app.http.swagger.analog.get import AnalogsGetResponses
from app.http.swagger.analog.put import AnalogEditResponses
from app.service.analog.analog import AnalogService
from core import logger
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.analog.analog import get_analog_service
from core.dependencies.dto import get_user_analog_id_pair
from core.domain.analog import Analog
from core.domain.user_analog import UserAnalogIDPair

router = APIRouter(prefix="/api/v2/analogs", tags=["Analog"])
logger = logger.get_logger(__name__)
AnalogServiceDep = Annotated[AnalogService, Depends(get_analog_service)]
UserAnalogIDPairDep = Annotated[UserAnalogIDPair, Depends(get_user_analog_id_pair)]


#################################################################################
# DELETE
#################################################################################
@auth_doc
@router.delete(
    "/{analog_uuid}",
    summary="Delete a analog",
    description="Delete a analog for the authenticated user and returns 200",
    responses=AnalogDeleteResponses.get_responses(),
    response_model=AnalogUUIDResponse,
)
@handle_exceptions
async def delete_analog(uaip: UserAnalogIDPairDep, analog_service: AnalogServiceDep):
    logger.debug(f"Request to delete a analog from user {str(uaip.user_id)[:10]}")
    await analog_service.delete_analog(uaip)
    return AnalogUUIDResponse(analog_uuid=str(uaip.analog_id))


#################################################################################
# GET
#################################################################################
@auth_doc
@router.get(
    "/{analog_uuid}/",
    summary="Get analog",
    description="Get analog by id",
    responses=AnalogsGetResponses.get_responses(),
    response_model=AnalogFieldsResponse,
)
@handle_exceptions
async def get_analog(user_analog: UserAnalogIDPairDep, analog_service: AnalogServiceDep):
    logger.debug(
        f"Request to get analog {user_analog.analog_id} by user {str(user_analog.user_id)[:8]}"
    )
    analog = await analog_service.get_analog(user_analog.analog_id)
    return AnalogFieldsResponse(
        id=str(analog.id) if analog.id is not None else None,
        title=analog.title,
        analog_num=analog.analog_num,
        analog_link=analog.analog_link,
        abstract=analog.abstract,
        claims=analog.claims,
        description=analog.description,
        created_at=analog.created_at,
        updated_at=analog.updated_at,
    )


#################################################################################
# PUT
#################################################################################
@router.put(
    "/{analog_uuid}",
    summary="Edit an analog",
    description="Update editable analog fields for the authenticated user.",
    responses=AnalogEditResponses.get_responses(),
    response_model=AnalogUUIDResponse,
)
@auth_doc
@handle_exceptions
async def edit_analog(
    analog_request: AnalogFieldsRequest,
    uad: UserAnalogIDPairDep,
    analog_service: AnalogServiceDep,
):
    logger.debug(f"Request to edit an analog from user {str(uad.user_id)[:8]}")
    analog = Analog(
        id=uad.analog_id,
        title=analog_request.title,
        analog_num=analog_request.analog_num,
        analog_link=analog_request.analog_link,
        abstract=analog_request.abstract,
        claims=analog_request.claims,
        description=analog_request.description,
    )
    await analog_service.edit_analog(analog)
    return AnalogUUIDResponse(analog_uuid=str(uad.analog_id))
