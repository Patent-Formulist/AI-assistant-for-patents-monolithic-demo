from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies.dependencies import get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_legal_service(db: SessionDep):
    from app.service.legal.legal import LegalService
    from core.settings import BASE_DIR, get_settings

    settings = get_settings()
    return LegalService(
        session=db,
        settings=settings.legal,
        root=BASE_DIR / settings.storage.storage_dir / "legal",
    )


def get_consent_check():
    from app.service.legal.legal import ConsentCheck
    from core.settings import BASE_DIR, get_settings

    settings = get_settings()
    return ConsentCheck(settings.legal, BASE_DIR / settings.storage.storage_dir / "legal")
