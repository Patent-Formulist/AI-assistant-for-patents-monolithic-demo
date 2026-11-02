from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LegalDocument:
    document: str
    version: str
    title: str
    requires_consent: bool
    content: str


@dataclass(frozen=True)
class ConsentState:
    """Where the user stands with the current version of a document."""

    document: str
    current_version: str
    requires_consent: bool
    accepted_version: str | None = None
    accepted_at: datetime | None = None
    choices: dict | None = None

    @property
    def up_to_date(self) -> bool:
        return self.accepted_version == self.current_version
