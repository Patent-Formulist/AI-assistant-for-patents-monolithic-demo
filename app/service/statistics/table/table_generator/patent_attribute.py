from app.service.statistics.statistics import StatisticsService
from app.service.statistics.table.component_generator.patent.attribute_checking import (
    PatentAttributeCheckingComponentGenerator,
)
from app.service.table.table_generator import BaseTableGenerator
from app.service.table.writer.csv_writer import CSVTableWriter
from app.service.table.writer.xlsx_writer import XLSXTableWriter
from core import logger
from core.dto.attribute_sign import PatentAttributesSignDto
from core.enum.table_type import TableType

logger = logger.get_logger(__name__)


class PatentAttributeTableGenerator(BaseTableGenerator):
    def __init__(
        self,
        statistics_service: StatisticsService,
        csv_writer: CSVTableWriter,
        xlsx_writer: XLSXTableWriter,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def generate_patent_attributes_checking(
        self,
        patent_id: int,
        generator_component: PatentAttributeCheckingComponentGenerator,
        table_type: TableType,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
