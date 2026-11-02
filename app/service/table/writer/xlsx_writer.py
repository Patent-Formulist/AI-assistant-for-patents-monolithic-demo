from io import BytesIO

from openpyxl import Workbook

from .base import BaseTableWriter


class XLSXTableWriter(BaseTableWriter):
    """Запись таблицы в XLSX формат"""

    def write(self, headers: list, rows: list, title: str = "table") -> bytes:
        wb = Workbook()
        ws = wb.active
        ws.title = title[:31]  # Excel ограничение на длину имени листа
        ws.append(headers)
        for row in rows:
            ws.append(row)
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
