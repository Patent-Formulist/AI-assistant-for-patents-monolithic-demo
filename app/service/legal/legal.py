import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models.legal_consent import LegalConsentModel
from core.domain.legal import ConsentState, LegalDocument
from core.exceptions import (
    ConsentRequiredError,
    ConsentVersionError,
    LegalDocumentNotFoundError,
)
from core.settings import LegalSettings

# Versions name files: nothing that could leave the document's directory
_VERSION = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._-]{0,49}$")


class LegalService:
    """Published legal documents and users' consents to them.

    A document's text is ``<root>/<document>/<version>.md``; the current version
    comes from settings (``legal.documents``). A new edition is a new file, so a
    consent always points to the exact text the user saw. Consents are
    append-only rows with IP and User-Agent, the evidence of acceptance.
    Runs in the request session: the caller commits.
    """

    def __init__(self, session: AsyncSession, settings: LegalSettings, root: Path):
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    def current(self) -> list[LegalDocument]:
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    def document(self, name: str, version: str | None = None) -> LegalDocument:
        """The document's current version, or the given one if it was published."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def accept(
        self,
        user_id: int,
        name: str,
        version: str,
        choices: dict | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> ConsentState:
        """Record that the user accepted ``version``, which must be the current one."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    def check_current(self, accepted: list[tuple[str, str]]) -> None:
        """Every (document, version) names a published document's current edition."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def accept_many(
        self,
        user_id: int,
        accepted: list[tuple[str, str]],
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        """Record several (document, version) consents at once, e.g. at registration."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def missing(self, user_id: int) -> list[ConsentState]:
        """Documents that require consent and whose current edition the user has not accepted."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def require_all(self, user_id: int) -> None:
        """Raise ConsentRequiredError (403) unless every required document is accepted."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def consents(self, user_id: int, names: list[str] | None = None) -> list[ConsentState]:
        """The user's latest consent to each document (all published ones by default)."""
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")


class ConsentCheck:
    """``LegalService.require_all`` for services with their own sessions (billing, payments)."""

    def __init__(self, settings: LegalSettings, root: Path):
        raise NotImplementedError("Демонстрационная заглушка: реализация не публикуется")

    async def require(self, session: AsyncSession, user_id: int) -> None:
        await LegalService(session, self._settings, self._root).require_all(user_id)
