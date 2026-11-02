from fastapi import APIRouter

from app.http.routes.export.drawing_export import router as export_router

from .elements import router as elements_router
from .figures import router as figures_router

router = APIRouter()

# Include subrouters
router.include_router(elements_router)
router.include_router(figures_router)
router.include_router(export_router)

__all__ = ["router"]
