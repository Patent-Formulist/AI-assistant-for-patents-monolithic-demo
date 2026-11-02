from app.service.access import PatentAccess
from app.service.analog.analog import AnalogService
from app.service.processor import Processor, UnitOfWork
from core import logger
from core.domain.analog import Analog
from core.exceptions import PatentAnalogsEditSearchError

logger = logger.get_logger(__name__)


class SearchEditOrchestratorService(Processor):
    def __init__(self, uow: UnitOfWork, analog_service: AnalogService, access: PatentAccess):
        super().__init__(uow=uow, error_class=PatentAnalogsEditSearchError)
        self._analog_service = analog_service
        self._access = access

    async def edit(self, patent_id: int, user_id: int, request_analogs: dict[int:Analog]) -> None:
        # Outside _run: a foreign patent is a 404, not a failed edit
        await self._access.patent(user_id, patent_id)
        return await self._run(
            operation=self._edit,
            operation_name="search edit",
            patent_id=patent_id,
            user_id=user_id,
            request_analogs=request_analogs,
        )

    async def _edit(self, patent_id: int, user_id: int, request_analogs: dict[int:Analog]) -> None:
        async with self._uow:
            # download the current status
            current_map: dict[int, Analog] = await self._load_current_state(patent_id)
            # identify changes (to_update, to_delete)
            to_update, to_delete = self._detect_changes(current_map, request_analogs)
            # performs updates and deletes
            await self._apply_changes(patent_id, user_id, to_update, to_delete)

    async def _load_current_state(self, patent_id: int) -> dict[int, Analog]:
        """Loads the active analogues and returns the dictionary id: model."""
        analogs: list[Analog] = await self._analog_service.get_analogs(patent_id)
        return {analog.id: analog for analog in analogs}

    def _detect_changes(
        self, current_map: dict[int, Analog], request_analogs: dict[int:Analog]
    ) -> tuple[dict, list]:
        """Compares the current state with incoming data, returns lists for updating and deleting."""
        to_update = {}

        for aid, req in request_analogs.items():
            domain = current_map.pop(aid, None)
            if domain is None:
                logger.warning(f"Analog with id {aid} not found or already deleted")
                continue
            if self._is_modified(domain, req):
                to_update[aid] = req

        to_delete: list[Analog] = list(current_map.values())
        return to_update, to_delete

    async def _apply_changes(
        self, patent_id: int, user_id: int, to_update: dict, to_delete: list[Analog]
    ) -> None:
        """Performs updates and deletes."""
        await self._analog_service.edit_analogs(patent_id=patent_id, analogs=to_update)
        await self._analog_service.delete_analogs(
            analog_ids=[analog.id for analog in to_delete], user_id=user_id
        )

    def _is_modified(self, domain: Analog, req: Analog) -> bool:
        """Checks if the data has changed compared to the request."""
        return (
            domain.analog_num != req.analog_num
            or domain.title != req.title
            or domain.analog_link != req.analog_link
            or domain.abstract != req.abstract
            or domain.claims != req.claims
        )
