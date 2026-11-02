from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.http.request_models.drawing import (
    DrawingFigureRequest,
    DrawingFigureUpdateRequest,
)
from app.http.response_models.drawing import (
    DrawingFigureListResponse,
    DrawingFigureResponse,
)
from app.service.drawing import (
    DrawingGenerationService,
    DrawingService,
)
from core import logger
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.drawing import (
    get_drawing_generation_service,
    get_drawing_service,
)
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
    "/figures",
    summary="Get all drawing figures",
    response_model=DrawingFigureListResponse,
)
@handle_exceptions
async def get_figures(
    user_patent: UserPatentIDPairDep,
    drawing_service: DrawingServiceDep,
):
    """Get all drawing figures for a patent"""
    logger.debug(f"Getting figures for patent {user_patent.patent_id}")
    figures = await drawing_service.get_figures(user_patent.patent_id)
    return DrawingFigureListResponse(figures=figures)


#################################################################################
# POST
#################################################################################
@auth_doc
@router.post(
    "/figures/generate",
    summary="Generate the figures distribution via AI",
    response_model=DrawingFigureListResponse,
)
@handle_exceptions
async def generate_figures(
    user_patent: UserPatentIDPairDep,
    generation_service: DrawingGenerationServiceDep,
):
    """Distribute the patent's existing elements across figures via AI.

    Replaces any existing figures with the freshly generated set.
    """
    logger.debug(f"Generating figures for patent {user_patent.patent_id}")
    figures = await generation_service.generate_figures(user_patent.patent_id)
    return DrawingFigureListResponse(figures=figures)


@auth_doc
@router.post(
    "/figures",
    summary="Create a new drawing figure",
    response_model=DrawingFigureResponse,
)
@handle_exceptions
async def create_figure(
    user_patent: UserPatentIDPairDep,
    request: DrawingFigureRequest,
    drawing_service: DrawingServiceDep,
):
    """Create a new drawing figure"""
    logger.debug(f"Creating figure for patent {user_patent.patent_id}")
    return await drawing_service.create_figure(user_patent.patent_id, request)


#################################################################################
# PUT
#################################################################################
@auth_doc
@router.put(
    "/figures/{figure_id}",
    summary="Update drawing figure",
    response_model=DrawingFigureResponse,
)
@handle_exceptions
async def update_figure(
    user_patent: UserPatentIDPairDep,
    figure_id: Annotated[int, Path(description="Figure ID")],
    request: DrawingFigureUpdateRequest,
    drawing_service: DrawingServiceDep,
):
    """Update drawing figure"""
    logger.debug(f"Updating figure {figure_id}")
    figure = await drawing_service.update_figure(
        user_patent.patent_id, figure_id, request.title, request.element_ids
    )
    if not figure:
        raise ResourceNotFoundError(f"Figure {figure_id} not found")
    return figure


#################################################################################
# DELETE
#################################################################################
@auth_doc
@router.delete(
    "/figures/{figure_id}",
    summary="Delete drawing figure",
)
@handle_exceptions
async def delete_figure(
    user_patent: UserPatentIDPairDep,
    figure_id: Annotated[int, Path(description="Figure ID")],
    drawing_service: DrawingServiceDep,
):
    """Delete drawing figure"""
    logger.debug(f"Deleting figure {figure_id}")
    result = await drawing_service.delete_figure(user_patent.patent_id, figure_id)
    if not result:
        raise ResourceNotFoundError(f"Figure {figure_id} not found")
    return {"success": True}
