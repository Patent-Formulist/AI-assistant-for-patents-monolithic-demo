import csv
from io import StringIO

from .base import BaseTableWriter


class CSVTableWriter(BaseTableWriter):
    """Запись таблицы в CSV формат"""

    def write(self, headers: list, rows: list, title: str = "table") -> bytes:
        buffer = StringIO()
        buffer.write("\ufeff")  # BOM for Excel
        writer = csv.writer(buffer)
        writer.writerow(headers)
        writer.writerows(rows)
        return buffer.getvalue().encode("utf-8")
