from core.dependencies.dependencies import get_session_factory


def get_billing_service():
    from datetime import timedelta

    from app.service.billing.billing import BillingService
    from app.service.billing.pricing import PriceList
    from core.dependencies.legal import get_consent_check
    from core.settings import get_settings

    settings = get_settings()
    return BillingService(
        session_factory=get_session_factory(),
        prices=PriceList(settings.billing.task_prices),
        hold_lifetime=timedelta(
            seconds=settings.temporal.workflow_execution_timeout_seconds
            + settings.billing.hold_margin_seconds
        ),
        consents=get_consent_check(),
    )
