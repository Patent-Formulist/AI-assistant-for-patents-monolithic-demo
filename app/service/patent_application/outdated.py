from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models.patent_application import PatentApplicationModel


async def flag_application_outdated(db: AsyncSession, patent_id: int) -> None:
    """Mark a generated patent application as outdated.

    Called whenever the source data the application was generated from
    (patent fields, drawings or the identified prototype) changes, so the
    preparation page can surface the "data changed — regenerate" hint and
    re-enable the generate button.

    No-op when no application has been generated for the patent yet (the
    UPDATE simply matches zero rows). Does not commit — the caller owns the
    surrounding transaction so the flag lands together with the change that
    triggered it.
    """
    await db.execute(
        update(PatentApplicationModel)
        .where(PatentApplicationModel.patent_id == patent_id)
        .values(is_outdated=True)
    )
