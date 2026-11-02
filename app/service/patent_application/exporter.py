import io
from typing import BinaryIO

from docx import Document
from docx.shared import Pt

from app.http.response_models.patent_application import PatentApplicationResponse
from core import logger

logger = logger.get_logger(__name__)


class PatentApplicationExporter:
    @staticmethod
    def export_to_docx(patent_name: str, application: PatentApplicationResponse) -> BinaryIO:
        logger.debug(f"Exporting patent application for {patent_name}")

        doc = Document()
        doc.add_heading(patent_name, level=1)

        if application.abstract:
            doc.add_heading("Реферат", level=2)
            doc.add_paragraph(application.abstract)

        if application.claims:
            doc.add_heading("Формула изобретения", level=2)
            for claim in application.claims:
                p = doc.add_paragraph(claim)
                p.paragraph_format.space_after = Pt(4)

        if application.description:
            doc.add_heading("Описание изобретения", level=2)
            for line in application.description.split("\n"):
                stripped = line.strip()
                if not stripped:
                    continue
                # Section headings are ALL CAPS lines
                if stripped.isupper() and len(stripped) < 80:
                    doc.add_heading(stripped.title(), level=3)
                else:
                    doc.add_paragraph(stripped)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
