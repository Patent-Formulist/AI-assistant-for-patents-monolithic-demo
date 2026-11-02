from app.service.analog.analog import AnalogService
from app.service.analog.table.component_generator.link import (
    AnalogLinksComponentGenerator,
)
from app.service.analog.table.component_generator.metadata import (
    AnalogMetadataComponentGenerator,
)
from app.service.analog.table.component_generator.search import (
    AnalogSearchComponentGenerator,
)
from app.service.attribute.attribute import AttributeService
from app.service.table.table_generator import BaseTableGenerator
from app.service.table.writer.csv_writer import CSVTableWriter
from app.service.table.writer.xlsx_writer import XLSXTableWriter
from core import logger
from core.domain.analog import Analog
from core.dto.analog_attribute import AnalogAttributesGroupDto
from core.enum.table_type import TableType

logger = logger.get_logger(__name__)


class AnalogTableGenerator(BaseTableGenerator):
    def __init__(
        self,
        analog_service: AnalogService,
        attribute_service: AttributeService,
        csv_writer: CSVTableWriter,
        xlsx_writer: XLSXTableWriter,
    ):
        super().__init__(csv_writer, xlsx_writer)
        self._analog_service = analog_service
        self._attribute_service = attribute_service

    async def generate_analogs_link(
        self,
        patent_id: int,
        generator_component: AnalogLinksComponentGenerator,
        table_type: TableType,
    ):
        logger.info("Start generate_analogs_link")
        analogs: list[Analog] = await self._analog_service.get_analogs(patent_id)
        headers, rows = await generator_component.generate(analogs)
        if not headers or not rows:
            raise ValueError
        return await self.write(headers, rows, table_type)

    async def generate_analogs_metadata(
        self,
        patent_id: int,
        generator_component: AnalogMetadataComponentGenerator,
        table_type: TableType,
    ):
        logger.info("Start generate_analogs_metadata")
        analogs: list[Analog] = await self._analog_service.get_analogs(patent_id)
        headers, rows = await generator_component.generate(analogs)
        if not headers or not rows:
            raise ValueError
        return await self.write(headers, rows, table_type)

    async def generate_analogs_search(
        self,
        patent_id: int,
        generator_component: AnalogSearchComponentGenerator,
        table_type: TableType,
    ):
        logger.info("Start generate_analogs_search")
        analogs: list[Analog] = await self._analog_service.get_analogs(patent_id)
        attribute: list[
            AnalogAttributesGroupDto
        ] = await self._attribute_service.get_analog_attributes_grouped(patent_id)
        headers, rows = await generator_component.generate(analogs, attribute)
        if not headers or not rows:
            raise ValueError
        return await self.write(headers, rows, table_type)
