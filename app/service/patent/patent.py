from advanced_alchemy.exceptions import NotFoundError
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.base import BaseService
from app.service.patent.repository import PatentRepository, UserPatentRepository
from core import logger
from core.data_mapper.patent.patent import PatentMapper
from core.db.models.patent import PatentModel
from core.db.models.user_patents import UserPatentModel
from core.domain.patent import Patent
from core.domain.user_patent import UserPatentIDPair
from core.exceptions import (
    PatentCreationError,
    PatentDeleteError,
    PatentEditError,
    PatentGetError,
    PatentNotFoundError,
)

logger = logger.get_logger(__name__)


class PatentService(BaseService[PatentModel, PatentRepository]):
    """Patent use cases."""

    repository_type = PatentRepository

    def __init__(self, session: AsyncSession, **kwargs):
        super().__init__(session=session, **kwargs)
        self._user_patents = UserPatentRepository(session=session)

    async def create_patent(self, patent: Patent, user_id: int) -> int:
        with self.raise_as(PatentCreationError, f"Failed to create patent for user {user_id}"):
            model = await self.create(patent)
            await self._user_patents.add(UserPatentModel(user_id=user_id, patent_id=model.id))
        logger.debug(f"Patent {model.id} created for user {user_id}")
        return model.id

    async def get_patent(self, patent_id: int) -> Patent:
        with self.raise_as(PatentGetError, f"Failed to get patent {patent_id}"):
            model = await self._get_active_patent(patent_id)
        return await PatentMapper.to_domain(model)

    async def get_patents(self, user_id: int) -> list[Patent]:
        with self.raise_as(PatentGetError, f"Failed to get patents for user {user_id}"):
            models = await self.repository.list_by_user(user_id)
        return [await PatentMapper.to_domain(model) for model in models]

    async def edit_patent(self, patent: Patent) -> None:
        """Update the fields that are set; None means "leave as is"."""
        # Lazy: app.service.patent_application imports PatentService.
        from app.service.patent_application.outdated import flag_application_outdated

        with self.raise_as(PatentEditError, f"Failed to edit patent {patent.id}"):
            await self._get_active_patent(patent.id)
            await self.update(patent, item_id=patent.id)
            await flag_application_outdated(self.repository.session, patent.id)

    async def delete_patent(self, patent_user: UserPatentIDPair) -> None:
        patent_id, user_id = patent_user.patent_id, patent_user.user_id
        with self.raise_as(PatentDeleteError, f"Failed to delete patent {patent_id}"):
            patent = await self._get_active_patent(patent_id)
            link = await self._user_patents.get_one_or_none(
                UserPatentModel.user_id == user_id,
                UserPatentModel.patent_id == patent_id,
                UserPatentModel.is_active.is_(True),
            )
            if link is None:
                raise PatentNotFoundError(f"Patent {patent_id} is not linked to user {user_id}")
            for row in (patent, link):
                row.is_active = False
                row.deleted_at = func.now()
                row.deleted_by = user_id
            await self.update(patent)
            await self._user_patents.update(link)
        logger.debug(f"Patent {patent_id} soft deleted by {user_id}")

    async def _get_active_patent(self, patent_id: int) -> PatentModel:
        try:
            return await self.get_active(patent_id)
        except NotFoundError as e:
            raise PatentNotFoundError(f"Patent {patent_id} not found") from e
