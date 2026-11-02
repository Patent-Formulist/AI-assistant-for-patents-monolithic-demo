from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from core.dependencies.dependencies import get_db
from core.settings import get_settings

logger = logger.get_logger(__name__)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


@lru_cache
def get_component_analog_metadata():
    from app.service.analog.table.component_generator.metadata import (
        AnalogMetadataComponentGenerator,
    )

    return AnalogMetadataComponentGenerator()


@lru_cache
def get_rospatent_metadata_parser_data_fetcher():
    from app.service.analog.analog_metadata.parser.data_fetcher import (
        ParserAnalogMetadataDataFetcher,
    )

    return ParserAnalogMetadataDataFetcher()


@lru_cache
def get_rospatent_metadata_parser():
    from app.service.analog.analog_metadata.parser.metadata_patent_analog_rospatent import (
        RospatentMetadataParser,
    )

    return RospatentMetadataParser(
        config=get_settings().parser.rospatent,
        data_fetcher=get_rospatent_metadata_parser_data_fetcher(),
    )


@lru_cache
def get_generator_metadata():
    from app.service.analog.analog_metadata.raw_data_generator.analog_metadata import (
        MetaGenerator,
    )

    return MetaGenerator(parser_service=get_rospatent_metadata_parser())


def get_analog_metadata_for_patent_processor(db: SessionDep):
    from app.service.analog.analog_metadata.processor.for_patent import (
        ProcessorPatentAnalogsMetadataService,
    )
    from core.dependencies.analog.analog import get_analog_service
    from core.dependencies.dependencies import get_unit_of_work

    return ProcessorPatentAnalogsMetadataService(
        uow=get_unit_of_work(db=db),
        analog_service=get_analog_service(db),
        generator=get_generator_metadata(),
    )


def get_analog_metadata_for_analog_processor(db: SessionDep):
    from app.service.analog.analog_metadata.processor.for_analog import (
        ProcessorPatentAnalogMetadataService,
    )
    from core.dependencies.analog.analog import get_analog_service
    from core.dependencies.dependencies import get_unit_of_work

    return ProcessorPatentAnalogMetadataService(
        uow=get_unit_of_work(db=db),
        analog_service=get_analog_service(db),
        generator=get_generator_metadata(),
    )
