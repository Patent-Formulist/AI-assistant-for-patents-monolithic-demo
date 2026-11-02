from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.service.analog.analog import AnalogService
from app.service.identity_prototype.identity_prototype import IdentifyPrototypeService
from app.service.identity_prototype.processor.pipeline import ProcessorIdentityPipelineService
from core import logger
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.analog.analog import get_analog_service
from core.dependencies.dto import (
    get_user_patent_id_pair_body,
    get_user_patent_id_pair_header,
)
from core.dependencies.identity_prototype.processor import get_identity_pipeline
from core.dependencies.identity_prototype.service import get_identify_prototype_service
from core.domain.analog import Analog
from core.domain.user_patent import UserPatentIDPair
from core.dto.identify_attribute import IdentifyPrototypeDto
from core.exceptions import IdentifyPrototypeGetError

router = APIRouter(prefix="/api/v2/processor", tags=["Processor_Identity_Prototype"])
logger = logger.get_logger(__name__)
UserPatentIDPairDep = Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_header)]
UserPatentIDPairBodyDep = Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_body)]
IdentifyPrototypeServiceDep = Annotated[
    IdentifyPrototypeService, Depends(get_identify_prototype_service)
]
AnalogServiceDep = Annotated[AnalogService, Depends(get_analog_service)]
IdentityPipelineDep = Annotated[ProcessorIdentityPipelineService, Depends(get_identity_pipeline)]


#################################################################################
# GET
#################################################################################
@auth_doc
@router.get("/patent/{patent_uuid}/identity/", summary="Get identity")
@handle_exceptions
async def get_analogs_identity(
    user_patent: UserPatentIDPairDep,
    service_i: IdentifyPrototypeServiceDep,
    service_a: AnalogServiceDep,
):
    logger.info(f"Request to get identity for patent {user_patent.patent_id}")
    try:
        try:
            identify_dto: IdentifyPrototypeDto = await service_i.get_by_patent(
                user_patent.patent_id
            )
        except IdentifyPrototypeGetError:
            return {
                str(user_patent.patent_id): {
                    "prototype": {},
                    "prototype_features": [],
                    "patent_features": [],
                    "rows": [],
                    "analog_id": None,
                    "analog_num": None,
                }
            }

        analog: Analog = await service_a.get_analog(analog_id=identify_dto.analog_id)

        prototype_data = {
            "number": analog.analog_num,
            "title": analog.title,
            "link": analog.analog_link,
            "abstract": analog.abstract or "",
            "claims": analog.claims or "",
        }

        rows = identify_dto.row if isinstance(identify_dto.row, list) else [identify_dto.row]

        prototype_features = []
        patent_features = []
        formatted_rows = []
        limiting_counter = 1
        distinguishing_counter = 1

        for r in rows:
            general = r.general_attr_title
            patent_text = r.patent_attr_title
            analog_text = r.analog_attr_title

            if analog_text == "None":
                analog_text = None
            if patent_text == "None":
                patent_text = None
            if general == "None":
                general = None

            has_patent = bool(patent_text and patent_text.strip())
            has_analog = bool(analog_text and analog_text.strip())

            if has_patent and has_analog:
                section = "limiting"
                row_number = limiting_counter
                limiting_counter += 1
                feature = general or patent_text
                patent_feature = patent_text
                prototype_feature = analog_text
            elif has_patent and not has_analog:
                section = "distinguishing"
                row_number = distinguishing_counter
                distinguishing_counter += 1
                feature = general or patent_text
                patent_feature = patent_text
                prototype_feature = "—"
            elif has_analog and not has_patent:
                continue
            else:
                continue

            if has_analog and analog_text not in prototype_features:
                prototype_features.append(analog_text)
            if has_patent and patent_text not in patent_features:
                patent_features.append(patent_text)

            formatted_rows.append(
                {
                    "row_number": row_number,
                    "feature": feature,
                    "patent_feature": patent_feature,
                    "prototype_feature": prototype_feature,
                    "section": section,
                }
            )

        return {
            str(user_patent.patent_id): {
                "prototype": prototype_data,
                "prototype_features": prototype_features,
                "patent_features": patent_features,
                "rows": formatted_rows,
                "analog_id": identify_dto.analog_id,
                "analog_num": identify_dto.analog_num,
            }
        }
    except Exception as e:
        logger.error(f"Error getting identity for patent {user_patent.patent_id}: {e}")
        raise


#################################################################################
# POST
#################################################################################
@auth_doc
@router.post("/identity/", summary="Create patent identity")
@handle_exceptions
async def create_patent_identity(
    user_patent: UserPatentIDPairBodyDep,
    processor: IdentityPipelineDep,
) -> JSONResponse:
    """
    Start identity prototype generation pipeline for a patent.

    Pipeline steps:
    1. Fetch analog and attributes data
    2. Generate identity prototype DTO via LLM
    3. Build domain objects from DTO
    4. Delete old identity data
    5. Save new attributes
    6. Link identity prototypes to attributes and save

    Returns job_id for tracking progress.
    """
    logger.debug(
        f"Request to create identity for patent {user_patent.patent_id} "
        f"from user {str(user_patent.user_id)[:10]}"
    )
    job_id = await processor.run_identity_pipeline(
        user_id=user_patent.user_id,
        patent_id=user_patent.patent_id,
    )
    return JSONResponse(
        status_code=202,
        content={
            "message": "Identity prototype generation pipeline accepted",
            "job_id": job_id,
        },
    )
