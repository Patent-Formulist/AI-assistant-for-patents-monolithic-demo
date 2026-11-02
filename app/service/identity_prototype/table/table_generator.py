from app.service.attribute.attribute import AttributeService
from app.service.identity.table.component_generator import (
    IdentifyAnalogComponentGenerator,
)
from app.service.patent.patent import PatentService
from app.service.table.table_generator import BaseTableGenerator
from app.service.table.writer.csv_writer import CSVTableWriter
from app.service.table.writer.xlsx_writer import XLSXTableWriter
from core import logger
from core.dto.identify_attribute import IdentifyDto
from core.enum.table_type import TableType

logger = logger.get_logger(__name__)


class AttributeTableGenerator(BaseTableGenerator):
    def __init__(
        self,
        patent_service: PatentService,
        attribute_service: AttributeService,
        csv_writer: CSVTableWriter,
        xlsx_writer: XLSXTableWriter,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def generate_identify(
        self,
        patent_id: int,
        generator_component: IdentifyAnalogComponentGenerator,
        table_type: TableType,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
