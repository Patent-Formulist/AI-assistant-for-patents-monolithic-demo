from datetime import datetime

from pydantic import BaseModel

from core.domain.legal import ConsentState, LegalDocument


class LegalDocumentResponse(BaseModel):
    document: str
    version: str
    title: str
    requires_consent: bool
    content: str  # Markdown

    @classmethod
    def of(cls, document: LegalDocument) -> "LegalDocumentResponse":
        return cls(
            document=document.document,
            version=document.version,
            title=document.title,
            requires_consent=document.requires_consent,
            content=document.content,
        )


class LegalDocumentSummaryResponse(BaseModel):
    document: str
    version: str
    title: str
    requires_consent: bool


class ConsentResponse(BaseModel):
    document: str
    current_version: str
    requires_consent: bool
    accepted_version: str | None
    accepted_at: datetime | None
    choices: dict | None
    up_to_date: bool

    @classmethod
    def of(cls, state: ConsentState) -> "ConsentResponse":
        return cls(
            document=state.document,
            current_version=state.current_version,
            requires_consent=state.requires_consent,
            accepted_version=state.accepted_version,
            accepted_at=state.accepted_at,
            choices=state.choices,
            up_to_date=state.up_to_date,
        )


class ConsentStatusResponse(BaseModel):
    all_accepted: bool
    # Required documents whose current edition is not accepted
    missing: list[ConsentResponse]
