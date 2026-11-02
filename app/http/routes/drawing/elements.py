from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.http.request_models.drawing import (
    DrawingElementReorderRequest,
    DrawingElementRequest,
    DrawingElementUpdateRequest,
    DrawingImportRequest,
)
from app.http.response_models.drawing import (
    DrawingElementListResponse,
    DrawingElementResponse,
    DrawingImportResponse,
)
from app.service.drawing import (
    DrawingGenerationService,
    DrawingService,
)
from core import logger
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.drawing import get_drawing_generation_service, get_drawing_service
from core.dependencies.dto import get_user_patent_id_pair_header
from core.domain.user_patent import UserPatentIDPair
from core.exceptions import ResourceNotFoundError

router = APIRouter(prefix="/api/v2/patents/{patent_uuid}/drawings", tags=["Drawing"])
logger = logger.get_logger(__name__)


UserPatentIDPairDep = Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_header)]
DrawingServiceDep = Annotated[DrawingService, Depends(get_drawing_service)]
DrawingGenerationServiceDep = Annotated[
    DrawingGenerationService, Depends(get_drawing_generation_service)
]


#################################################################################
# GET
#################################################################################
@auth_doc
@router.get(
    "/elements",
    summary="Get all drawing elements",
    response_model=DrawingElementListResponse,
)
@handle_exceptions
async def get_elements(
    user_patent: UserPatentIDPairDep,
    drawing_service: DrawingServiceDep,
):
    """Get all drawing elements for a patent"""
    logger.debug(f"Getting elements for patent {user_patent.patent_id}")
    elements = await drawing_service.get_elements(user_patent.patent_id)
    return DrawingElementListResponse(elements=elements)


#################################################################################
# POST
#################################################################################
@auth_doc
@router.post(
    "/elements/generate",
    summary="Generate the drawing elements list via AI",
    response_model=DrawingElementListResponse,
)
@handle_exceptions
async def generate_elements(
    user_patent: UserPatentIDPairDep,
    generation_service: DrawingGenerationServiceDep,
):
    """Generate the numbered list of parts from the patent source data.

    Replaces any existing elements with the freshly generated list.
    """
    logger.debug(f"Generating elements for patent {user_patent.patent_id}")
    elements = await generation_service.generate_elements(user_patent.patent_id)
    return DrawingElementListResponse(elements=elements)


@auth_doc
@router.post(
    "/elements",
    summary="Create a new drawing element",
    response_model=DrawingElementResponse,
)
@handle_exceptions
async def create_element(
    user_patent: UserPatentIDPairDep,
    request: DrawingElementRequest,
    drawing_service: DrawingServiceDep,
):
    """Create a new drawing element"""
    logger.debug(f"Creating element for patent {user_patent.patent_id}")
    return await drawing_service.create_element(user_patent.patent_id, request)


@auth_doc
@router.post(
    "/elements/reorder",
    summary="Reorder drawing elements",
    response_model=DrawingElementListResponse,
)
@handle_exceptions
async def reorder_elements(
    user_patent: UserPatentIDPairDep,
    request: DrawingElementReorderRequest,
    drawing_service: DrawingServiceDep,
):
    """Reorder drawing elements"""
    logger.debug(f"Reordering elements for patent {user_patent.patent_id}")
    elements = await drawing_service.reorder_elements(user_patent.patent_id, request.element_ids)
    return DrawingElementListResponse(elements=elements)


@auth_doc
@router.post(
    "/import",
    summary="Import elements from a list of descriptions",
    response_model=DrawingImportResponse,
)
@handle_exceptions
async def import_elements(
    user_patent: UserPatentIDPairDep,
    request: DrawingImportRequest,
    drawing_service: DrawingServiceDep,
):
    """Import drawing elements from a provided list of descriptions"""
    logger.debug(f"Importing elements for patent {user_patent.patent_id}")

    if not request.elements:
        raise ValueError("Element list is empty")

    elements = await drawing_service.import_elements(user_patent.patent_id, request.elements)

    return DrawingImportResponse(imported_count=len(elements), elements=elements)


#################################################################################
# PUT
#################################################################################
@auth_doc
@router.put(
    "/elements/{element_id}",
    summary="Update drawing element",
    response_model=DrawingElementResponse,
)
@handle_exceptions
async def update_element(
    user_patent: UserPatentIDPairDep,
    element_id: Annotated[int, Path(description="Element ID")],
    request: DrawingElementUpdateRequest,
    drawing_service: DrawingServiceDep,
):
    """Update drawing element description"""
    logger.debug(f"Updating element {element_id}")
    element = await drawing_service.update_element(
        user_patent.patent_id, element_id, request.description
    )
    if not element:
        raise ResourceNotFoundError(f"Element {element_id} not found")
    return element


#################################################################################
# DELETE
#################################################################################
@auth_doc
@router.delete(
    "/elements/{element_id}",
    summary="Delete drawing element",
)
@handle_exceptions
async def delete_element(
    user_patent: UserPatentIDPairDep,
    element_id: Annotated[int, Path(description="Element ID")],
    drawing_service: DrawingServiceDep,
):
    """Delete drawing element"""
    logger.debug(f"Deleting element {element_id}")
    result = await drawing_service.delete_element(user_patent.patent_id, element_id)
    if not result:
        raise ResourceNotFoundError(f"Element {element_id} not found")
    return {"success": True}
