import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.http.exception_handlers import register_exception_handlers
from app.http.routes import (
    analog,
    analog_table,
    billing,
    drawing,
    drawing_table,
    elements,
    identity_prototype,
    job,
    legal,
    organization,
    patent,
    patent_application,
    patent_table,
    search,
    statistics,
    user,
)
from app.service.health import HealthChecker
from core import logger
from core.db.db import DB, set_db_instance
from core.dependencies.health import get_health_checker
from core.logger import Logger
from core.sentry import init_sentry
from core.settings import get_settings

logger = logger.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = DB(get_settings().database)

    try:
        await db.init_db_client()
        set_db_instance(db)
        logger.info("[INIT] Database successfully initialized")
    except ConnectionRefusedError:
        logger.error("[INIT] Could not connect to database")
        os._exit(1)
    except Exception as e:
        logger.error(f"[INIT] Critical database error: {type(e).__name__}: {e}")
        os._exit(1)

    yield

    # Graceful shutdown
    try:
        await db.close_db_client()
        logger.info("[SHUTDOWN] Database connection closed")
    except Exception as e:
        logger.error(f"[SHUTDOWN] Error closing database: {e}")


def create_app() -> FastAPI:
    # Invalid settings stop the app here, before it serves anything
    Logger.init_logger(get_settings().log)
    init_sentry(get_settings().monitoring, "api")

    app = FastAPI(
        title="Patent Service API",
        version="1.0.0",
        lifespan=lifespan,
        redirect_slashes=False,
        swagger_ui_parameters={"persistAuthorization": True},
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Auth-ошибки из зависимостей → 401 (см. app/http/exception_handlers.py)
    register_exception_handlers(app)

    # Healthcheck
    @app.get("/health", tags=["System"])
    async def health_check(checker: Annotated[HealthChecker, Depends(get_health_checker)]):
        """200 when the database and Temporal answer, 503 naming what does not."""
        report = await checker.check()
        return JSONResponse(
            status_code=200 if report.ok else 503,
            content={"status": "ok" if report.ok else "fail", "checks": report.checks},
        )

    # Register all routers
    routers = [
        patent,
        job,
        user,
        billing,
        legal,
        organization,
        # Analog
        analog,
        # Workflows
        search,
        statistics,
        identity_prototype,
        drawing,
        elements,
        patent_application,
        # Export
        analog_table,
        patent_table,
        drawing_table,
    ]

    for router in routers:
        app.include_router(router)

    return app


app = create_app()

__all__ = ["app"]
