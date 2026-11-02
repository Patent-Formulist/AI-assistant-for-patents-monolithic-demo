"""Temporal worker process: ``python -m app.temporal.worker`` (ADR 0005)."""

import asyncio
import signal

from temporalio.worker import Worker

from app.service.alerts import AlertService
from app.service.health import HealthChecker
from app.service.job.job import JobService
from app.service.task.task import TaskService
from app.temporal import shared
from app.temporal.activities.analog_search import AnalogSearchActivities
from app.temporal.activities.job_status import JobStatusActivities
from app.temporal.activities.patent_pipelines import PatentPipelineActivities
from app.temporal.activities.statistics import StatisticsActivities
from app.temporal.client import get_temporal_client
from app.temporal.heartbeat import heartbeat_loop
from app.temporal.llm_usage import LLMUsageInterceptor, database_usage_store
from app.temporal.sentry import SentryInterceptor
from app.temporal.watchdog import Watchdog
from app.temporal.workflows.analog_search import AnalogSearchWorkflow
from app.temporal.workflows.identity import IdentityWorkflow
from app.temporal.workflows.patent_application import PatentApplicationWorkflow
from app.temporal.workflows.statistics import StatisticsWorkflow
from core import logger
from core.db.db import DB, set_db_instance
from core.dependencies.billing import get_billing_service
from core.logger import Logger
from core.sentry import init_sentry
from core.settings import get_settings

logger = logger.get_logger(__name__)


async def run_worker(stop: asyncio.Event) -> None:
    settings = get_settings()
    db = DB(settings.database)
    await db.init_db_client()
    # Same initialization as main.py does for the API. Processors are assembled
    # through core.dependencies.*, and some of those factories (for example
    # get_job_service) take the session factory from the global DB instance.
    # Without registering it here, activities would fail with
    # "Database not initialized".
    set_db_instance(db)
    client = await get_temporal_client()

    alerts = AlertService(db.session_factory, settings.monitoring)
    job_status = JobStatusActivities(
        JobService(session_factory=db.session_factory),
        TaskService(session_factory=db.session_factory),
        get_billing_service(),
        alerts,
    )
    external_activities = [
        *AnalogSearchActivities(db.session_factory).all(),
        *StatisticsActivities(db.session_factory).all(),
        *PatentPipelineActivities(db.session_factory).all(),
    ]

    pipelines = Worker(
        client,
        task_queue=shared.PIPELINES_TASK_QUEUE,
        workflows=[
            AnalogSearchWorkflow,
            StatisticsWorkflow,
            IdentityWorkflow,
            PatentApplicationWorkflow,
        ],
        activities=job_status.all(),
        interceptors=[SentryInterceptor()],
    )
    external = Worker(
        client,
        task_queue=shared.EXTERNAL_TASK_QUEUE,
        activities=external_activities,
        interceptors=[
            LLMUsageInterceptor(database_usage_store(db.session_factory)),
            SentryInterceptor(),
        ],
        max_concurrent_activities=settings.temporal.external_max_concurrent_activities,
    )
    watchdog = asyncio.create_task(
        Watchdog(db.session_factory, alerts, settings.monitoring).run(stop)
    )
    heartbeat = None
    if settings.monitoring.worker_heartbeat_url:
        checker = HealthChecker(
            db.session_factory,
            get_temporal_client,
            settings.monitoring.health_timeout_seconds,
        )
        heartbeat = asyncio.create_task(
            heartbeat_loop(
                checker,
                settings.monitoring.worker_heartbeat_url,
                settings.monitoring.worker_heartbeat_seconds,
                stop,
            )
        )
    try:
        async with pipelines, external:
            logger.info(
                f"[WORKER] Polling '{shared.PIPELINES_TASK_QUEUE}' and "
                f"'{shared.EXTERNAL_TASK_QUEUE}' at {settings.temporal.address}"
            )
            await stop.wait()
            logger.info("[WORKER] Shutting down, waiting for running activities")
    finally:
        watchdog.cancel()
        if heartbeat is not None:
            heartbeat.cancel()
        await db.close_db_client()


def main() -> None:
    Logger.init_logger(get_settings().log)
    init_sentry(get_settings().monitoring, "worker")

    async def _main() -> None:
        stop = asyncio.Event()
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop.set)
        await run_worker(stop)

    asyncio.run(_main())


if __name__ == "__main__":
    main()
