from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from core.dependencies.attribute import get_attribute_service
from core.dependencies.dependencies import get_db

logger = logger.get_logger(__name__)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_csv_writer():
    from app.service.table.writer.csv_writer import CSVWriter

    return CSVWriter()


def get_xlsx_writer():
    from app.service.table.writer.xlsx_writer import XLSXWriter

    return XLSXWriter()


def get_analog_attribute_table_generator(db: SessionDep):
    from app.service.statistics.table.table_generator.analog_attribute import (
        AnalogAttributeTableGenerator,
    )
    from core.dependencies.statistics import get_statistics_service

    return AnalogAttributeTableGenerator(
        attribute_service=get_attribute_service(db),
        statistics_service=get_statistics_service(db),
        csv_writer=get_csv_writer(),
        xlsx_writer=get_xlsx_writer(),
    )


def get_attribute_table_generator(db: SessionDep):
    from app.service.statistics.table.table_generator.statistics import (
        AttributeTableGenerator,
    )
    from core.dependencies.patent import get_patent_service
    from core.dependencies.statistics import get_statistics_service

    return AttributeTableGenerator(
        patent_service=get_patent_service(db),
        attribute_service=get_attribute_service(db),
        statistics_service=get_statistics_service(db),
        csv_writer=get_csv_writer(),
        xlsx_writer=get_xlsx_writer(),
    )


def get_patent_attribute_table_generator(db: SessionDep):
    from app.service.statistics.table.table_generator.patent_attribute import (
        PatentAttributeTableGenerator,
    )
    from core.dependencies.statistics import get_statistics_service

    return PatentAttributeTableGenerator(
        statistics_service=get_statistics_service(db),
        csv_writer=get_csv_writer(),
        xlsx_writer=get_xlsx_writer(),
    )
