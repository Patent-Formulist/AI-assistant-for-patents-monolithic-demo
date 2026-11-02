from app.service.attribute.attribute import AttributeService
from app.service.statistics.statistics import StatisticsService
from app.service.statistics.table.component_generator.analog.attribute import (
    AnalogAttributesComponentGenerator,
)
from app.service.statistics.table.component_generator.analog.attribute_checking import (
    AnalogAttributeCheckingComponentGenerator,
)
from app.service.statistics.table.component_generator.analog.attributes_mather import (
    AnalogAttributesMatherComponentGenerator,
)
from app.service.table.table_generator import BaseTableGenerator
from app.service.table.writer.csv_writer import CSVTableWriter
from app.service.table.writer.xlsx_writer import XLSXTableWriter
from core import logger
from core.domain.attribute import Attribute
from core.dto.analog_attribute import AnalogAttributesGroupDto
from core.dto.attribute_sign import (
    AnalogSignsMap,
)
from core.enum.table_type import TableType

logger = logger.get_logger(__name__)


class AnalogAttributeTableGenerator(BaseTableGenerator):
    def __init__(
        self,
        attribute_service: AttributeService,
        statistics_service: StatisticsService,
        csv_writer: CSVTableWriter,
        xlsx_writer: XLSXTableWriter,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def generate_analogs_attributes(
        self,
        patent_id: int,
        generator_component: AnalogAttributesComponentGenerator,
        table_type: TableType,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def generate_analogs_attributes_mather(
        self,
        patent_id: int,
        generator_component: AnalogAttributesMatherComponentGenerator,
        table_type: TableType,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def generate_analogs_attributes_checking(
        self,
        patent_id: int,
        generator_component: AnalogAttributeCheckingComponentGenerator,
        table_type: TableType,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
