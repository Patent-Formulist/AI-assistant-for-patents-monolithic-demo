from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from core.dependencies.dependencies import get_db

logger = logger.get_logger(__name__)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


@lru_cache
def get_component_analog_attributes():
    from app.service.statistics.table.component_generator.analog.attribute import (
        AnalogAttributesComponentGenerator,
    )

    return AnalogAttributesComponentGenerator()


@lru_cache
def get_component_analog_attributes_mather():
    from app.service.statistics.table.component_generator.analog.attributes_mather import (
        AnalogAttributesMatherComponentGenerator,
    )

    return AnalogAttributesMatherComponentGenerator()


@lru_cache
def get_component_analog_attributes_checking():
    from app.service.statistics.table.component_generator.analog import (
        AnalogAttributeCheckingComponentGenerator,
    )

    return AnalogAttributeCheckingComponentGenerator()


@lru_cache
def get_component_statistics():
    from app.service.statistics.table.component_generator.statistic import (
        StatisticsComponentGenerator,
    )

    return StatisticsComponentGenerator()


@lru_cache
def get_component_identify():
    from app.service.identity.table.component_generator import (
        IdentifyAnalogComponentGenerator,
    )

    return IdentifyAnalogComponentGenerator()


@lru_cache
def get_component_attributes_mather():
    from app.service.statistics.table.component_generator.patent.attribute_mather import (
        AttributesMatherComponentGenerator,
    )

    return AttributesMatherComponentGenerator()


@lru_cache
def get_component_patent_attributes_checking():
    from app.service.statistics.table.component_generator.patent.attribute_checking import (
        PatentAttributeCheckingComponentGenerator,
    )

    return PatentAttributeCheckingComponentGenerator()
