from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from core.dependencies.attribute import get_attribute_service
from core.dependencies.dependencies import get_db
from core.dependencies.table_generator import get_csv_writer, get_xlsx_writer

logger = logger.get_logger(__name__)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_analog_service(db: SessionDep):
    from app.service.analog.analog import AnalogService

    return AnalogService(session=db)


def get_analog_table_generator(db: SessionDep):
    from app.service.table.table_generator.analog import AnalogTableGenerator

    return AnalogTableGenerator(
        analog_service=get_analog_service(db),
        attribute_service=get_attribute_service(db),
        csv_writer=get_csv_writer(),
        xlsx_writer=get_xlsx_writer(),
    )
