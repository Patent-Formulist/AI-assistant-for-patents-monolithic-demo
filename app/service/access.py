from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models.analog import AnalogModel
from core.db.models.job import JobModel
from core.db.models.patent import PatentModel
from core.db.models.patent_analog import PatentAnalogModel
from core.db.models.user_patents import UserPatentModel
from core.exceptions import AnalogNotFoundError, PatentNotFoundError, ResourceNotFoundError


class PatentAccess:
    """Who may touch what: patents are personal, everything else hangs off a patent.

    A patent is the user's when an active user_patent link joins them. An
    analog, a job, drawings belong to a patent; the user may touch them when
    the patent is theirs. Missing and foreign objects look the same (404), so
    ids of other users' data cannot be probed.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def patent(self, user_id: int, patent_id: int) -> None:
        owned = await self._session.scalar(
            select(UserPatentModel.id)
            .join(PatentModel, PatentModel.id == UserPatentModel.patent_id)
            .where(
                UserPatentModel.user_id == user_id,
                UserPatentModel.patent_id == patent_id,
                UserPatentModel.is_active,
                PatentModel.is_active,
            )
        )
        if owned is None:
            raise PatentNotFoundError(f"Patent {patent_id} not found for user {user_id}")

    async def analog(self, user_id: int, analog_id: int) -> int:
        """Check the analog is in one of the user's patents; return that patent's id."""
        patent_id = await self._session.scalar(
            select(PatentAnalogModel.patent_id)
            .join(AnalogModel, AnalogModel.id == PatentAnalogModel.analog_id)
            .join(UserPatentModel, UserPatentModel.patent_id == PatentAnalogModel.patent_id)
            .where(
                PatentAnalogModel.analog_id == analog_id,
                UserPatentModel.user_id == user_id,
                UserPatentModel.is_active,
                AnalogModel.is_active,
            )
        )
        if patent_id is None:
            raise AnalogNotFoundError(f"Analog {analog_id} not found for user {user_id}")
        return patent_id

    async def analog_of_patent(self, patent_id: int, analog_id: int) -> None:
        linked = await self._session.scalar(
            select(PatentAnalogModel.id)
            .join(AnalogModel, AnalogModel.id == PatentAnalogModel.analog_id)
            .where(
                PatentAnalogModel.patent_id == patent_id,
                PatentAnalogModel.analog_id == analog_id,
                AnalogModel.is_active,
            )
        )
        if linked is None:
            raise AnalogNotFoundError(f"Analog {analog_id} not found in patent {patent_id}")

    async def job(self, user_id: int, job_id: int) -> None:
        patent_id = await self._session.scalar(
            select(JobModel.patent_id).where(JobModel.id == job_id)
        )
        if patent_id is None:
            raise ResourceNotFoundError(f"Job {job_id} not found")
        try:
            await self.patent(user_id, patent_id)
        except PatentNotFoundError as e:
            raise ResourceNotFoundError(f"Job {job_id} not found") from e
