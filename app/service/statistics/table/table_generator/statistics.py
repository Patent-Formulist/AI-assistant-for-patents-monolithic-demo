from app.service.attribute.attribute import AttributeService
from app.service.patent.patent import PatentService
from app.service.statistics.statistics import StatisticsService
from app.service.statistics.table.component_generator.patent.attribute_mather import (
    AttributesMatherComponentGenerator,
)
from app.service.statistics.table.component_generator.statistic import (
    StatisticsComponentGenerator,
)
from app.service.table.table_generator import BaseTableGenerator
from app.service.table.writer.csv_writer import CSVTableWriter
from app.service.table.writer.xlsx_writer import XLSXTableWriter
from core import logger
from core.domain.attribute import Attribute
from core.dto.attribute_sign import AnalogSignsMap, PatentAttributesSignDto
from core.enum.table_type import TableType

logger = logger.get_logger(__name__)


class AttributeTableGenerator(BaseTableGenerator):
    def __init__(
        self,
        patent_service: PatentService,
        attribute_service: AttributeService,
        statistics_service: StatisticsService,
        csv_writer: CSVTableWriter,
        xlsx_writer: XLSXTableWriter,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def generate_attributes_mather(
        self,
        patent_id: int,
        generator_component: AttributesMatherComponentGenerator,
        table_type: TableType,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def generate_statistics(
        self,
        patent_id: int,
        generator_component: StatisticsComponentGenerator,
        table_type: TableType,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
