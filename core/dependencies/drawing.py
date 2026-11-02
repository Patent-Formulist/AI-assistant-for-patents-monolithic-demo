from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies.dependencies import get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_drawing_generation_service(db: SessionDep):
    from app.service.drawing.generation_service import DrawingGenerationService
    from core.dependencies.patent import get_patent_service
    from core.dependencies.patent_application import get_application_generator

    return DrawingGenerationService(
        drawing_service=get_drawing_service(db=db),
        patent_service=get_patent_service(db=db),
        generator=get_application_generator(),
    )


def get_drawing_service(db: SessionDep):
    from app.service.drawing import DrawingService

    return DrawingService(session=db)
