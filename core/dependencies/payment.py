from core.dependencies.dependencies import get_session_factory


def get_payment_service():
    from app.service.payment.payment import PaymentService
    from app.service.payment.yookassa import YooKassaClient
    from core.dependencies.billing import get_billing_service
    from core.dependencies.legal import get_consent_check
    from core.settings import get_settings

    settings = get_settings().payments
    return PaymentService(
        session_factory=get_session_factory(),
        billing=get_billing_service(),
        client=YooKassaClient(settings.yookassa),
        settings=settings,
        consents=get_consent_check(),
    )
