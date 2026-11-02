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
def get_rospatent_link_parser_data_fetcher():
    from app.service.analog.analog_link.parser.data_fetcher import (
        ParserAnalogLinkDataFetcher,
    )

    return ParserAnalogLinkDataFetcher()


@lru_cache
def get_rospatent_link_parser():
    from app.service.analog.analog_link.parser.rospatent_link_parser import (
        RospatentLinkParser,
    )

    return RospatentLinkParser(
        get_settings().parser.rospatent, get_rospatent_link_parser_data_fetcher()
    )


@lru_cache
def get_component_analog_links():
    from app.service.analog.table.component_generator.link import (
        AnalogLinksComponentGenerator,
    )

    return AnalogLinksComponentGenerator()


def get_analog_link_for_patent_processor(db: SessionDep):
    from app.service.analog.analog_link.processor.for_patent import (
        ProcessorPatentAnalogsLinksService,
    )
    from core.dependencies.analog.analog import get_analog_service
    from core.dependencies.dependencies import get_unit_of_work
    from core.dependencies.patent import get_patent_service

    return ProcessorPatentAnalogsLinksService(
        uow=get_unit_of_work(db=db),
        patent_service=get_patent_service(db),
        analog_service=get_analog_service(db),
        parser=get_rospatent_link_parser(),
    )


def get_analog_link_for_analog_processor(db: SessionDep):
    from app.service.analog.analog_link.processor.for_analog import (
        ProcessorPatentAnalogLinksService,
    )
    from core.dependencies.analog.analog import get_analog_service
    from core.dependencies.dependencies import get_unit_of_work

    return ProcessorPatentAnalogLinksService(
        uow=get_unit_of_work(db=db),
        analog_service=get_analog_service(db),
        parser=get_rospatent_link_parser(),
    )
