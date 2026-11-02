from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.http.base_controller import handle_file_request
from app.service.statistics.table.component_generator.patent.attribute_checking import (
    PatentAttributeCheckingComponentGenerator,
)
from app.service.statistics.table.component_generator.patent.attribute_mather import (
    AttributesMatherComponentGenerator,
)
from app.service.statistics.table.table_generator.patent_attribute import (
    PatentAttributeTableGenerator,
)
from app.service.statistics.table.table_generator.statistics import (
    AttributeTableGenerator,
)
from core import logger
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.component_generator import (
    get_component_attributes_mather,
    get_component_patent_attributes_checking,
)
from core.dependencies.dto import get_user_patent_id_pair_header
from core.dependencies.table_generator import (
    get_attribute_table_generator,
    get_patent_attribute_table_generator,
)
from core.domain.user_patent import UserPatentIDPair
from core.enum.table_type import TableType

router = APIRouter(prefix="/api/v2/patents/{patent_uuid}", tags=["Export"])
logger = logger.get_logger(__name__)

UserPatentIDPairDep = Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_header)]
AttributeTableGeneratorDep = Annotated[
    AttributeTableGenerator, Depends(get_attribute_table_generator)
]
PatentAttributeTableGeneratorDep = Annotated[
    PatentAttributeTableGenerator, Depends(get_patent_attribute_table_generator)
]


#################################################################################
# Patent attributes: matching
#################################################################################
@auth_doc
@router.get(
    "/table/attributes/matching/",
    summary="Download patent attributes matching table",
)
@handle_exceptions
async def download_patent_attributes_matching(
    user_patent: UserPatentIDPairDep,
    generator: AttributeTableGeneratorDep,
    component: Annotated[
        AttributesMatherComponentGenerator, Depends(get_component_attributes_mather)
    ],
    fmt: TableType = Query(TableType.XLSX),
):
    return await handle_file_request(
        file_type=fmt.value,
        default_filename="patent_attributes_matching",
        patent_id=str(user_patent.patent_id),
        func=generator.generate_attributes_mather,
        func_args=(user_patent.patent_id, component, fmt),
    )


#################################################################################
# Patent attributes checking
#################################################################################
@auth_doc
@router.get(
    "/table/attributes/checking/",
    summary="Download patent attributes checking table",
)
@handle_exceptions
async def download_patent_attributes_checking(
    user_patent: UserPatentIDPairDep,
    generator: PatentAttributeTableGeneratorDep,
    component: Annotated[
        PatentAttributeCheckingComponentGenerator,
        Depends(get_component_patent_attributes_checking),
    ],
    fmt: TableType = Query(TableType.XLSX),
):
    return await handle_file_request(
        file_type=fmt.value,
        default_filename="patent_attributes_checking",
        patent_id=str(user_patent.patent_id),
        func=generator.generate_patent_attributes_checking,
        func_args=(user_patent.patent_id, component, fmt),
    )
