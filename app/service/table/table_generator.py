from app.service.table.writer.csv_writer import CSVTableWriter
from app.service.table.writer.xlsx_writer import XLSXTableWriter
from core import logger
from core.enum.table_type import TableType

logger = logger.get_logger(__name__)


class BaseTableGenerator:
    def __init__(self, csv_writer: CSVTableWriter, xlsx_writer: XLSXTableWriter):
        self._csv_writer = csv_writer
        self._xlsx_writer = xlsx_writer

    async def write(self, headers: list[str], rows: list[list[str]], table_type: TableType):
        table = None

        if table_type == TableType.CSV:
            table = self._csv_writer.write(headers, rows)
        elif table_type == TableType.XLSX:
            table = self._xlsx_writer.write(headers, rows)
        return table
