from app.service.base import BaseService
from app.service.user_patent_UI_progress.repository import UserPatentRepository
from core.db.models.user_patents import UserPatentModel
from core.enum.ui_button import UIButton
from core.exceptions import PatentEditError, PatentGetError, PatentNotFoundError


class UserPatentUIProgressService(BaseService[UserPatentModel, UserPatentRepository]):
    """UI state of a patent page kept per user across devices: the last opened section.

    Pipeline progress is not stored here; it comes from jobs (ADR 0004).
    """

    repository_type = UserPatentRepository

    async def get_last_ui_button(self, user_id: int, patent_id: int) -> UIButton | None:
        """None when the user has no active link to the patent."""
        with self.raise_as(PatentGetError, f"Failed to get UI progress for patent {patent_id}"):
            user_patent = await self._get_user_patent(user_id, patent_id)
        return UIButton(user_patent.last_ui_button) if user_patent else None

    async def set_last_ui_button(self, user_id: int, patent_id: int, button: UIButton) -> None:
        with self.raise_as(PatentEditError, f"Failed to save UI progress for patent {patent_id}"):
            user_patent = await self._get_user_patent(user_id, patent_id)
            if user_patent is None:
                raise PatentNotFoundError(f"Patent {patent_id} not found for user {user_id}")
            user_patent.last_ui_button = button.value
            await self.update(user_patent)

    async def _get_user_patent(self, user_id: int, patent_id: int) -> UserPatentModel | None:
        return await self.get_one_or_none(
            UserPatentModel.user_id == user_id,
            UserPatentModel.patent_id == patent_id,
            UserPatentModel.is_active.is_(True),
        )
