from core.dependencies.dependencies import get_session_factory


def get_health_checker():
    from app.service.health import HealthChecker
    from app.temporal.client import get_temporal_client
    from core.settings import get_settings

    return HealthChecker(
        session_factory=get_session_factory(),
        temporal_client=get_temporal_client,
        timeout_seconds=get_settings().monitoring.health_timeout_seconds,
    )
