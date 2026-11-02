import io
from typing import BinaryIO

from docx import Document
from openpyxl import Workbook
from openpyxl.styles import Font

from app.http.response_models.drawing import DrawingFigureResponse
from core import logger

logger = logger.get_logger(__name__)


class DrawingExporter:
    """Service for exporting drawings to DOCX/XLSX"""

    @staticmethod
    def export_to_docx(figures: list[DrawingFigureResponse]) -> BinaryIO:
        """Export figures to DOCX format"""
        logger.debug(f"Exporting {len(figures)} figures to DOCX")

        doc = Document()
        doc.add_heading("Чертежи патента", level=1)

        for fig_idx, figure in enumerate(figures, start=1):
            # Add figure title
            doc.add_heading(f"Фиг. {fig_idx}", level=2)
            doc.add_paragraph(figure.title)

            # Add table with elements
            if figure.elements:
                table = doc.add_table(rows=1, cols=2)
                table.style = "Light Grid Accent 1"

                # Header row
                header_cells = table.rows[0].cells
                header_cells[0].text = "№"
                header_cells[1].text = "Описание"

                # Make header bold
                for cell in header_cells:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.bold = True

                # Add element rows
                for el_idx, element in enumerate(figure.elements, start=1):
                    row_cells = table.add_row().cells
                    row_cells[0].text = str(el_idx)
                    row_cells[1].text = element.description

            doc.add_paragraph()  # Add spacing

        # Save to BytesIO
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    @staticmethod
    def export_to_xlsx(figures: list[DrawingFigureResponse]) -> BinaryIO:
        """Export figures to XLSX format"""
        logger.debug(f"Exporting {len(figures)} figures to XLSX")

        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet

        for fig_idx, figure in enumerate(figures, start=1):
            # Create sheet for each figure
            sheet_name = f"Фиг. {fig_idx}"
            ws = wb.create_sheet(title=sheet_name)

            # Add figure title
            ws["A1"] = f"Фиг. {fig_idx}: {figure.title}"
            ws["A1"].font = Font(bold=True, size=14)
            ws.merge_cells("A1:B1")

            # Add table headers
            ws["A3"] = "№"
            ws["B3"] = "Описание"
            ws["A3"].font = Font(bold=True)
            ws["B3"].font = Font(bold=True)

            # Add elements
            for row_idx, element in enumerate(figure.elements, start=4):
                ws[f"A{row_idx}"] = row_idx - 3  # sequential 1, 2, 3...
                ws[f"B{row_idx}"] = element.description

            # Adjust column widths
            ws.column_dimensions["A"].width = 10
            ws.column_dimensions["B"].width = 80

        # Save to BytesIO
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
