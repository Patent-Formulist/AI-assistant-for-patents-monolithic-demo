from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.http.base_controller import handle_file_request
from app.service.analog.table.component_generator.link import (
    AnalogLinksComponentGenerator,
)
from app.service.analog.table.component_generator.metadata import (
    AnalogMetadataComponentGenerator,
)
from app.service.analog.table.component_generator.search import (
    AnalogSearchComponentGenerator,
)
from app.service.analog.table.table_generator import AnalogTableGenerator
from app.service.identity_prototype.table.component_generator import (
    IdentifyAnalogComponentGenerator,
)
from app.service.statistics.table.component_generator.analog.attribute import (
    AnalogAttributesComponentGenerator,
)
from app.service.statistics.table.component_generator.analog.attribute_checking import (
    AnalogAttributeCheckingComponentGenerator,
)
from app.service.statistics.table.component_generator.analog.attributes_mather import (
    AnalogAttributesMatherComponentGenerator,
)
from app.service.statistics.table.component_generator.statistic import (
    StatisticsComponentGenerator,
)
from app.service.statistics.table.table_generator.analog_attribute import (
    AnalogAttributeTableGenerator,
)
from app.service.statistics.table.table_generator.patent_attribute import (
    PatentAttributeTableGenerator,
)
from app.service.statistics.table.table_generator.statistics import (
    AttributeTableGenerator,
)
from core import logger
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.analog.analog import get_analog_table_generator
from core.dependencies.analog.analog_link import get_component_analog_links
from core.dependencies.analog.analog_metadata import get_component_analog_metadata
from core.dependencies.analog.search import get_component_analog_search
from core.dependencies.component_generator import (
    get_component_analog_attributes,
    get_component_analog_attributes_checking,
    get_component_analog_attributes_mather,
    get_component_identify,
    get_component_statistics,
)
from core.dependencies.dto import get_user_patent_id_pair_header
from core.dependencies.table_generator import (
    get_analog_attribute_table_generator,
    get_attribute_table_generator,
    get_patent_attribute_table_generator,
)
from core.domain.user_patent import UserPatentIDPair
from core.enum.table_type import TableType

router = APIRouter(prefix="/api/v2/patents/{patent_uuid}", tags=["Export"])
logger = logger.get_logger(__name__)
UserPatentIDPairDep = Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_header)]
AnalogTableGeneratorDep = Annotated[AnalogTableGenerator, Depends(get_analog_table_generator)]
AnalogAttributeTableGeneratorDep = Annotated[
    AnalogAttributeTableGenerator, Depends(get_analog_attribute_table_generator)
]
AttributeTableGeneratorDep = Annotated[
    AttributeTableGenerator, Depends(get_attribute_table_generator)
]
PatentAttributeTableGeneratorDep = Annotated[
    PatentAttributeTableGenerator, Depends(get_patent_attribute_table_generator)
]


#################################################################################
# Analogs: links
#################################################################################
@auth_doc
@router.get("/table/analogs/link/", summary="Download analogs link table")
@handle_exceptions
async def download_analogs_link(
    user_patent: UserPatentIDPairDep,
    generator: AnalogTableGeneratorDep,
    component: Annotated[AnalogLinksComponentGenerator, Depends(get_component_analog_links)],
    fmt: TableType = Query(TableType.XLSX, description="Table format: csv or xlsx"),
):
    return await handle_file_request(
        file_type=fmt.value,
        default_filename="analogs_link",
        patent_id=str(user_patent.patent_id),
        func=generator.generate_analogs_link,
        func_args=(user_patent.patent_id, component, fmt),
    )


#################################################################################
# Analogs: metadata
#################################################################################
@auth_doc
@router.get("/table/analogs/metadata/", summary="Download analogs metadata table")
@handle_exceptions
async def download_analogs_metadata(
    user_patent: UserPatentIDPairDep,
    generator: AnalogTableGeneratorDep,
    component: Annotated[AnalogMetadataComponentGenerator, Depends(get_component_analog_metadata)],
    fmt: TableType = Query(TableType.XLSX, description="Table format: csv or xlsx"),
):
    return await handle_file_request(
        file_type=fmt.value,
        default_filename="analogs_metadata",
        patent_id=str(user_patent.patent_id),
        func=generator.generate_analogs_metadata,
        func_args=(user_patent.patent_id, component, fmt),
    )


#################################################################################
# Analogs: search
#################################################################################
@auth_doc
@router.get("/table/analogs/search/", summary="Download analogs search table")
@handle_exceptions
async def download_analogs_search(
    user_patent: UserPatentIDPairDep,
    generator: AnalogTableGeneratorDep,
    component: Annotated[AnalogSearchComponentGenerator, Depends(get_component_analog_search)],
    fmt: TableType = Query(TableType.XLSX, description="Table format: csv or xlsx"),
):
    return await handle_file_request(
        file_type=fmt.value,
        default_filename="analogs_search",
        patent_id=str(user_patent.patent_id),
        func=generator.generate_analogs_search,
        func_args=(user_patent.patent_id, component, fmt),
    )


#################################################################################
# Analog attributes
#################################################################################
@auth_doc
@router.get("/table/analogs/attributes/", summary="Download analog attributes table")
@handle_exceptions
async def download_analog_attributes(
    user_patent: UserPatentIDPairDep,
    generator: AnalogAttributeTableGeneratorDep,
    component: Annotated[
        AnalogAttributesComponentGenerator, Depends(get_component_analog_attributes)
    ],
    fmt: TableType = Query(TableType.XLSX),
):
    return await handle_file_request(
        file_type=fmt.value,
        default_filename="analog_attributes",
        patent_id=str(user_patent.patent_id),
        func=generator.generate_analogs_attributes,
        func_args=(user_patent.patent_id, component, fmt),
    )


#################################################################################
# Analog attributes matching
#################################################################################
@auth_doc
@router.get(
    "/table/analogs/attributes/matching/",
    summary="Download analog attributes matching table",
)
@handle_exceptions
async def download_analog_attributes_matching(
    user_patent: UserPatentIDPairDep,
    generator: AnalogAttributeTableGeneratorDep,
    component: Annotated[
        AnalogAttributesMatherComponentGenerator,
        Depends(get_component_analog_attributes_mather),
    ],
    fmt: TableType = Query(TableType.XLSX),
):
    return await handle_file_request(
        file_type=fmt.value,
        default_filename="analog_attributes_matching",
        patent_id=str(user_patent.patent_id),
        func=generator.generate_analogs_attributes_mather,
        func_args=(user_patent.patent_id, component, fmt),
    )


#################################################################################
# Analog attributes checking
#################################################################################
@auth_doc
@router.get(
    "/table/analogs/attributes/checking/",
    summary="Download analog attributes checking table",
)
@handle_exceptions
async def download_analog_attributes_checking(
    user_patent: UserPatentIDPairDep,
    generator: AnalogAttributeTableGeneratorDep,
    component: Annotated[
        AnalogAttributeCheckingComponentGenerator,
        Depends(get_component_analog_attributes_checking),
    ],
    fmt: TableType = Query(TableType.XLSX),
):
    return await handle_file_request(
        file_type=fmt.value,
        default_filename="analog_attributes_checking",
        patent_id=str(user_patent.patent_id),
        func=generator.generate_analogs_attributes_checking,
        func_args=(user_patent.patent_id, component, fmt),
    )


#################################################################################
# Statistics
#################################################################################
@auth_doc
@router.get("/table/analogs/statistics/", summary="Download statistics table")
@handle_exceptions
async def download_statistics(
    user_patent: UserPatentIDPairDep,
    generator: AttributeTableGeneratorDep,
    component: Annotated[StatisticsComponentGenerator, Depends(get_component_statistics)],
    fmt: TableType = Query(TableType.XLSX),
):
    return await handle_file_request(
        file_type=fmt.value,
        default_filename="statistics",
        patent_id=str(user_patent.patent_id),
        func=generator.generate_statistics,
        func_args=(user_patent.patent_id, component, fmt),
    )


#################################################################################
# Identification
#################################################################################
@auth_doc
@router.get("/table/analogs/identity/", summary="Download identity table")
@handle_exceptions
async def download_identity(
    user_patent: UserPatentIDPairDep,
    generator: AttributeTableGeneratorDep,
    component: Annotated[IdentifyAnalogComponentGenerator, Depends(get_component_identify)],
    fmt: TableType = Query(TableType.XLSX),
):
    return await handle_file_request(
        file_type=fmt.value,
        default_filename="identity",
        patent_id=str(user_patent.patent_id),
        func=generator.generate_identify,
        func_args=(user_patent.patent_id, component, fmt),
    )
