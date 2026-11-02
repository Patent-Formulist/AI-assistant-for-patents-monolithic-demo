from advanced_alchemy.exceptions import NotFoundError
from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.analog.repository import AnalogRepository, PatentAnalogRepository
from app.service.base import BaseService
from core import logger
from core.data_mapper.analog.analog import AnalogMapper
from core.data_mapper.analog.analogs import AnalogsMapper
from core.db.models.analog import AnalogModel
from core.db.models.patent_analog import PatentAnalogModel
from core.domain.analog import Analog
from core.domain.user_analog import UserAnalogIDPair
from core.exceptions import (
    AnalogCreationError,
    AnalogDeleteError,
    AnalogEditError,
    AnalogGetError,
    AnalogNotFoundError,
)

logger = logger.get_logger(__name__)


class AnalogService(BaseService[AnalogModel, AnalogRepository]):
    """Analog use cases: analogs and their links to patents."""

    repository_type = AnalogRepository

    def __init__(self, session: AsyncSession, **kwargs):
        super().__init__(session=session, **kwargs)
        self._patent_analogs = PatentAnalogRepository(session=session)

    async def create_analog(self, analog: Analog) -> Analog:
        # Domain field names differ from the model (analog_num -> number), so map explicitly.
        with self.raise_as(AnalogCreationError, f"Failed to create analog {analog.analog_num}"):
            model = await self.create(await AnalogMapper.to_model(analog))
        return await AnalogMapper.to_domain(model)

    async def create_analogs(self, analogs: list[Analog]) -> list[Analog]:
        if not analogs:
            return []
        with self.raise_as(AnalogCreationError, "Failed to create analogs"):
            models = await self.create_many(await AnalogsMapper.to_model(analogs))
        return await AnalogsMapper.to_domain(list(models))

    async def link_to_patent(self, patent_id: int, analog_ids: list[int]) -> None:
        """Link analogs to the patent; already linked analogs are skipped."""
        if not analog_ids:
            return
        with self.raise_as(
            AnalogCreationError, f"Failed to link analogs {analog_ids} to patent {patent_id}"
        ):
            linked = await self._patent_analogs.list_linked_analog_ids(patent_id, analog_ids)
            to_link = [aid for aid in dict.fromkeys(analog_ids) if aid not in linked]
            if to_link:
                await self._patent_analogs.add_many(
                    [PatentAnalogModel(patent_id=patent_id, analog_id=aid) for aid in to_link]
                )

    async def get_analog(self, analog_id: int) -> Analog:
        with self.raise_as(AnalogGetError, f"Failed to get analog {analog_id}"):
            model = await self._get_active_analog(analog_id)
        return await AnalogMapper.to_domain(model)

    async def get_analogs(self, patent_id: int) -> list[Analog]:
        with self.raise_as(AnalogGetError, f"Failed to get analogs for patent {patent_id}"):
            models = await self.repository.list_by_patent(patent_id)
        return [await AnalogMapper.to_domain(model) for model in models]

    async def get_analogs_by_numbers(self, patent_id: int, numbers: list[str]) -> dict[str, Analog]:
        """Active analogs of the patent keyed by number.

        Only the patent's own: analogs are never shared between patents, so
        editing or deleting one cannot touch another user's data.
        """
        if not numbers:
            return {}
        with self.raise_as(AnalogGetError, "Failed to get analogs by numbers"):
            models = await self.repository.list_by_numbers(patent_id, numbers)
        return {model.number: await AnalogMapper.to_domain(model) for model in models}

    async def edit_analog(self, analog: Analog) -> None:
        """Update the fields that are set; None means "leave as is".

        analog_num/analog_link have no same-named model columns, so update()
        drops them and number/link stay as is.
        """
        with self.raise_as(AnalogEditError, f"Failed to edit analog {analog.id}"):
            await self._get_active_analog(analog.id)
            await self.update(analog, item_id=analog.id)

    async def edit_analogs(self, patent_id: int, analogs: dict[int, Analog]) -> None:
        """Update analogs of a patent; empty fields keep the stored value."""
        with self.raise_as(AnalogEditError, f"Failed to edit analogs for patent {patent_id}"):
            models = {m.id: m for m in await self.repository.list_by_patent(patent_id)}
            for analog_id, analog in analogs.items():
                model = models.get(analog_id)
                if model is None:
                    logger.warning(f"Analog {analog_id} not found, skipping update")
                    continue
                model.number = analog.analog_num or model.number
                model.title = analog.title or model.title
                model.link = analog.analog_link or model.link
                model.abstract = analog.abstract or model.abstract
                model.claims = analog.claims or model.claims
                model.description = analog.description or model.description
                await self.update(model)

    async def update_metadata(self, analogs: list[Analog]) -> None:
        """Store abstract, claims and description of the given analogs."""
        if not analogs:
            return
        with self.raise_as(AnalogEditError, "Failed to update analog metadata"):
            models = {m.id: m for m in await self.repository.list_by_ids([a.id for a in analogs])}
            for analog in analogs:
                model = models.get(analog.id)
                if model is None:
                    logger.warning(f"Analog {analog.id} not found, skipping metadata update")
                    continue
                model.abstract = analog.abstract
                model.claims = analog.claims
                model.description = analog.description
            await self.update_many(list(models.values()))

    async def delete_analog(self, user_analog: UserAnalogIDPair) -> None:
        analog_id, user_id = user_analog.analog_id, user_analog.user_id
        with self.raise_as(AnalogDeleteError, f"Failed to delete analog {analog_id}"):
            model = await self._get_active_analog(analog_id)
            model.is_active = False
            model.deleted_at = func.now()
            model.deleted_by = user_id
            await self.update(model)
        logger.debug(f"Analog {analog_id} soft deleted by {user_id}")

    async def delete_analogs(self, analog_ids: list[int], user_id: int) -> None:
        if not analog_ids:
            return
        with self.raise_as(AnalogDeleteError, f"Failed to delete analogs {analog_ids}"):
            await self.repository.session.execute(
                update(AnalogModel)
                .where(AnalogModel.id.in_(analog_ids), AnalogModel.is_active)
                .values(is_active=False, deleted_at=func.now(), deleted_by=user_id)
            )

    async def _get_active_analog(self, analog_id: int) -> AnalogModel:
        try:
            return await self.get_active(analog_id)
        except NotFoundError as e:
            raise AnalogNotFoundError(f"Analog {analog_id} not found") from e
