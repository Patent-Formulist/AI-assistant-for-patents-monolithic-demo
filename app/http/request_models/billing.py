from pydantic import BaseModel, Field, model_validator


class AdjustmentRequest(BaseModel):
    """Exactly one of ``user_id`` and ``organization_id``: whose balance."""

    user_id: int | None = None
    organization_id: int | None = None
    amount: int = Field(description="Kopecks: positive adds, negative takes")
    comment: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def one_owner(self) -> "AdjustmentRequest":
        if (self.user_id is None) == (self.organization_id is None):
            raise ValueError("Set exactly one of user_id and organization_id")
        return self


class PaymentRequest(BaseModel):
    amount: int = Field(gt=0, description="Kopecks")
    organization_id: int | None = Field(
        default=None, description="Top up this organization's balance instead of your own"
    )


class PayerRequest(BaseModel):
    organization_id: int | None = Field(
        description="Pay for pipelines from this organization's balance; null: your own"
    )


class YooKassaNotification(BaseModel):
    """Only the payment id is used: its state is read from YooKassa itself."""

    event: str
    object: dict


class RefundRequest(BaseModel):
    amount: int | None = Field(
        default=None, gt=0, description="Kopecks; null: what is left of the payment"
    )
