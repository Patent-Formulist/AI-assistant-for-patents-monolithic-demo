from typing import Annotated

from fastapi import APIRouter, Depends

from app.http.base_controller import handle_file_request
from app.http.request_models.drawing import DrawingExportRequest
from app.service.drawing import DrawingService
from app.service.drawing.exporter import DrawingExporter
from core import logger
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.drawing import get_drawing_service
from core.dependencies.dto import get_user_patent_id_pair_header
from core.domain.user_patent import UserPatentIDPair

router = APIRouter(prefix="/api/v2/patents/{patent_uuid}/drawings", tags=["Export"])
logger = logger.get_logger(__name__)

UserPatentIDPairDep = Annotated[UserPatentIDPair, Depends(get_user_patent_id_pair_header)]
DrawingServiceDep = Annotated[DrawingService, Depends(get_drawing_service)]


@auth_doc
@router.post(
    "/export",
    summary="Export drawings to DOCX or XLSX",
)
@handle_exceptions
async def export_drawings(
    user_patent: UserPatentIDPairDep,
    request: DrawingExportRequest,
    drawing_service: DrawingServiceDep,
):
    """Export drawings to DOCX or XLSX format"""

    # Get all figures
    figures = await drawing_service.get_figures(user_patent.patent_id)

    async def export_drawings_data(figures: list, format: str) -> bytes:
        if format.lower() == "docx":
            buffer = DrawingExporter.export_to_docx(figures)
            return buffer.getvalue() if hasattr(buffer, "getvalue") else buffer
        elif format.lower() == "xlsx":
            buffer = DrawingExporter.export_to_xlsx(figures)
            return buffer.getvalue() if hasattr(buffer, "getvalue") else buffer
        else:
            raise ValueError(f"Unsupported format: {format}")

    return await handle_file_request(
        file_type=request.format.lower(),  # "docx" или "xlsx"
        default_filename=f"patent_{user_patent.patent_id}_drawings",
        patent_id=str(user_patent.patent_id),
        func=export_drawings_data,
        func_args=(figures, request.format),
    )
