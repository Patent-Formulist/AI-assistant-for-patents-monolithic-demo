"""The worker tells an outside monitor it is alive (healthchecks.io-style ping URL).

A monitor that hears nothing for a while alerts: the worker process died or
hangs, and no pipeline runs. A failed health check pings ``<url>/fail`` at
once instead of waiting for the silence.
"""

import asyncio

import aiohttp

from app.service.health import HealthChecker
from core import logger

logger = logger.get_logger(__name__)


async def ping(url: str, healthy: bool, timeout_seconds: float = 10) -> None:
    target = url if healthy else url.rstrip("/") + "/fail"
    try:
        async with (
            aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_seconds)) as session,
            session.get(target) as response,
        ):
            if response.status >= 400:
                logger.warning(f"Heartbeat ping answered {response.status}")
    except (aiohttp.ClientError, TimeoutError) as e:
        # The monitor alerts on the silence anyway
        logger.warning(f"Heartbeat ping failed: {e}")


async def heartbeat_loop(
    checker: HealthChecker, url: str, interval_seconds: float, stop: asyncio.Event
) -> None:
    while not stop.is_set():
        report = await checker.check()
        await ping(url, report.ok)
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval_seconds)
        except TimeoutError:
            pass
