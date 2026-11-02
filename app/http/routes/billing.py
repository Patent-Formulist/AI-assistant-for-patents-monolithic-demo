from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.http.request_models.billing import (
    AdjustmentRequest,
    PayerRequest,
    PaymentRequest,
    RefundRequest,
    YooKassaNotification,
)
from app.http.response_models.billing import (
    BalanceResponse,
    LedgerEntryResponse,
    MemberLimitResponse,
    PayerResponse,
    PaymentResponse,
    PricesResponse,
    RefundResponse,
)
from app.service.billing.billing import BillingService
from app.service.payment.payment import PaymentService
from core.decorators.api_router import auth_doc, handle_exceptions
from core.dependencies.auth import CurrentUserId
from core.dependencies.billing import get_billing_service
from core.dependencies.payment import get_payment_service
from core.domain.billing import AccountOwner

router = APIRouter(prefix="/api/v2/billing", tags=["Billing"])
BillingServiceDep = Annotated[BillingService, Depends(get_billing_service)]
PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
OrganizationIdQuery = Annotated[
    int | None, Query(description="The organization's balance instead of your own")
]


@auth_doc
@router.get(
    "/balance",
    summary="Balance of the user or, for its members, of an organization",
    response_model=BalanceResponse,
)
@handle_exceptions
async def get_balance(
    user_id: CurrentUserId, billing: BillingServiceDep, organization_id: OrganizationIdQuery = None
) -> BalanceResponse:
    return BalanceResponse.of(await billing.balance(user_id, organization_id))


@auth_doc
@router.get(
    "/transactions",
    summary=(
        "Balance history, newest first: the user's or, for owners and admins, an organization's"
    ),
    response_model=list[LedgerEntryResponse],
)
@handle_exceptions
async def get_transactions(
    user_id: CurrentUserId,
    billing: BillingServiceDep,
    organization_id: OrganizationIdQuery = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[LedgerEntryResponse]:
    return [
        LedgerEntryResponse.of(e)
        for e in await billing.history(user_id, organization_id, limit, offset)
    ]


@auth_doc
@router.get(
    "/limit",
    summary="The user's monthly spending limit in an organization and its use",
    response_model=MemberLimitResponse,
)
@handle_exceptions
async def get_member_limit(
    user_id: CurrentUserId,
    billing: BillingServiceDep,
    organization_id: Annotated[int, Query()],
) -> MemberLimitResponse:
    return MemberLimitResponse.of(await billing.member_limit(user_id, organization_id))


@auth_doc
@router.get(
    "/payer", summary="Whose balance pays for the user's pipelines", response_model=PayerResponse
)
@handle_exceptions
async def get_payer(user_id: CurrentUserId, billing: BillingServiceDep) -> PayerResponse:
    payer = await billing.payer(user_id)
    return PayerResponse(organization_id=payer.organization_id)


@auth_doc
@router.put(
    "/payer",
    summary="Pay for pipelines from an organization's balance (as its member) or your own",
    response_model=PayerResponse,
)
@handle_exceptions
async def set_payer(
    user_id: CurrentUserId, request: PayerRequest, billing: BillingServiceDep
) -> PayerResponse:
    payer = await billing.set_payer(user_id, request.organization_id)
    return PayerResponse(organization_id=payer.organization_id)


@router.get("/prices", summary="Full price of each pipeline", response_model=PricesResponse)
@handle_exceptions
async def get_prices(billing: BillingServiceDep) -> PricesResponse:
    return PricesResponse(
        prices={job_type.value: price for job_type, price in billing.pipeline_prices().items()}
    )


@auth_doc
@router.post(
    "/adjustments",
    summary="Correct a user's or an organization's balance (administrators only)",
    response_model=BalanceResponse,
)
@handle_exceptions
async def adjust_balance(
    user_id: CurrentUserId, request: AdjustmentRequest, billing: BillingServiceDep
) -> BalanceResponse:
    return BalanceResponse.of(
        await billing.adjust(
            admin_id=user_id,
            owner=AccountOwner(user_id=request.user_id, organization_id=request.organization_id),
            amount=request.amount,
            comment=request.comment,
        )
    )


@auth_doc
@router.post(
    "/payments",
    summary="Start a top-up: returns the payment page URL",
    status_code=201,
    response_model=PaymentResponse,
)
@handle_exceptions
async def create_payment(
    user_id: CurrentUserId, request: PaymentRequest, payments: PaymentServiceDep
) -> PaymentResponse:
    return PaymentResponse.of(
        await payments.create(user_id, request.amount, request.organization_id)
    )


@auth_doc
@router.get(
    "/payments",
    summary="Top-ups of the user, newest first",
    response_model=list[PaymentResponse],
)
@handle_exceptions
async def list_payments(
    user_id: CurrentUserId,
    payments: PaymentServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[PaymentResponse]:
    return [PaymentResponse.of(p) for p in await payments.recent(user_id, limit)]


@auth_doc
@router.get(
    "/payments/{payment_id}",
    summary="Top-up status (checked with the provider while pending)",
    response_model=PaymentResponse,
)
@handle_exceptions
async def get_payment(
    user_id: CurrentUserId,
    payments: PaymentServiceDep,
    payment_id: Annotated[int, Path()],
) -> PaymentResponse:
    return PaymentResponse.of(await payments.get(user_id, payment_id))


@auth_doc
@router.post(
    "/payments/{payment_id}/refunds",
    summary="Refund a payment through YooKassa (administrators; only money left on the balance)",
    status_code=201,
    response_model=RefundResponse,
)
@handle_exceptions
async def refund_payment(
    user_id: CurrentUserId,
    request: RefundRequest,
    payments: PaymentServiceDep,
    payment_id: Annotated[int, Path()],
) -> RefundResponse:
    return RefundResponse.of(await payments.refund(user_id, payment_id, request.amount))


@auth_doc
@router.post(
    "/refunds/{refund_id}/sync",
    summary="Check a refund with YooKassa, or ask again if it never reached it (administrators)",
    response_model=RefundResponse,
)
@handle_exceptions
async def sync_refund(
    user_id: CurrentUserId, payments: PaymentServiceDep, refund_id: Annotated[int, Path()]
) -> RefundResponse:
    return RefundResponse.of(await payments.sync_refund(user_id, refund_id))


@router.post(
    "/payments/yookassa/notifications",
    summary="YooKassa HTTP notification (no auth: the payment is re-read from YooKassa)",
    include_in_schema=False,
)
@handle_exceptions
async def yookassa_notification(
    notification: YooKassaNotification, payments: PaymentServiceDep
) -> dict:
    payment_id = notification.object.get("id")
    if isinstance(payment_id, str) and notification.event.startswith("payment."):
        await payments.sync(payment_id)
    return {}
