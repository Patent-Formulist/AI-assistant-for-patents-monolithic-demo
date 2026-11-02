from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.service.statistics.frontend import StatisticsFrontendQuery
from app.service.statistics.processor.statistics import ProcessorStatisticsService
from core import logger
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.dto import (
    get_user_patent_id_pair_body,
    get_user_patent_id_pair_header,
)
from core.dependencies.statistics import get_statistics_frontend_query, get_statistics_processor
from core.domain.user_patent import UserPatentIDPair

router = APIRouter(prefix="/api/v2/processor", tags=["Processor_Statistics"])
logger = logger.get_logger(__name__)

UserPatentIDPairBodyDep = Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_body)]
UserPatentIDPairHeaderDep = Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_header)]
ProcessorStatisticsServiceDep = Annotated[
    ProcessorStatisticsService, Depends(get_statistics_processor)
]
StatisticsFrontendQueryDep = Annotated[
    StatisticsFrontendQuery, Depends(get_statistics_frontend_query)
]


#################################################################################
# POST
#################################################################################
@auth_doc
@router.post("/statistics/", summary="Create statistics")
@handle_exceptions
async def create_statistics(
    user_patent: UserPatentIDPairBodyDep,
    processor: ProcessorStatisticsServiceDep,
) -> JSONResponse:
    """
    Start statistics generation pipeline for a patent.

    Pipeline steps:
    1. Generate analog attributes via LLM
    2. Match analog attributes
    3. Generate patent attributes
    4. Generate general (combined) attributes
    5. Calculate analog coincidences
    6. Calculate patent coincidences

    Coincidence totals are computed on read from the signs.

    Returns job_id for tracking progress.
    """
    job_id = await processor.run_statistics_pipeline(
        patent_id=user_patent.patent_id,
        user_id=user_patent.user_id,
    )
    return JSONResponse(
        status_code=202,
        content={
            "message": "Statistics generation pipeline accepted",
            "job_id": job_id,
        },
    )


#################################################################################
# GET
#################################################################################
@auth_doc
@router.get("/patent/{patent_uuid}/statistics/", summary="Get statistics")
@handle_exceptions
async def get_analogs_statistics(
    user_patent: UserPatentIDPairHeaderDep, statistics_query: StatisticsFrontendQueryDep
):
    logger.info(f"Request to get statistics for patent {user_patent.patent_id}")
    return await statistics_query.get(patent_id=user_patent.patent_id)
