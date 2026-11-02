"""Sentry for the API and the worker: errors with their context, nothing else.

Without SENTRY_DSN nothing is sent. Performance tracing is off: the free plan
is spent on errors. No personal data beyond the user id: patent texts and
tokens stay on the server.
"""

import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from core.settings import MonitoringSettings


def init_sentry(settings: MonitoringSettings, component: str) -> bool:
    """Start the SDK for ``component`` ("api" or "worker"); False if there is no DSN."""
    dsn = settings.sentry_dsn.get_secret_value()
    if not dsn:
        return False
    sentry_sdk.init(
        dsn=dsn,
        environment=settings.environment,
        server_name=component,
        send_default_pii=False,
        traces_sample_rate=0,
        integrations=[
            # Log records are breadcrumbs for the error they lead to; the code
            # logs errors before re-raising them, so making each one an event
            # would report every failure twice
            LoggingIntegration(level=logging.INFO, event_level=None),
        ],
    )
    sentry_sdk.set_tag("component", component)
    return True
