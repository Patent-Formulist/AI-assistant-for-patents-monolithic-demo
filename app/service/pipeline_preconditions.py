import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.service.analog.analog import AnalogService
from app.service.patent.patent import PatentService
from app.service.statistics.statistics import StatisticsService
from core.exceptions import PipelinePreconditionError


class PipelinePreconditions:
    """Data a pipeline needs before it can run, and the inputs it depends on.

    Checked by the starter before the job is created (API answers 400) and
    again by the first activity: the data may change between the two.
    """

    def __init__(
        self,
        analog_service: AnalogService,
        statistics_service: StatisticsService,
        patent_service: PatentService,
    ):
        self._analog_service = analog_service
        self._statistics_service = statistics_service
        self._patent_service = patent_service

    async def check_statistics(self, patent_id: int) -> None:
        """Statistics needs analogs with text: without them the LLM gets an empty prompt."""
        analogs = await self._analog_service.get_analogs(patent_id)
        if not any(a.abstract or a.claims or a.description for a in analogs):
            raise PipelinePreconditionError(
                "Сначала найдите аналоги: для статистики нужен хотя бы один аналог "
                "с рефератом, формулой или описанием"
            )

    async def check_identity(self, patent_id: int) -> None:
        """Identity needs coincidences, i.e. finished statistics."""
        if not await self._statistics_service.get_coincidences(patent_id):
            raise PipelinePreconditionError(
                "Сначала рассчитайте статистику: для выявления прототипа нужны "
                "совпадения признаков с аналогами"
            )

    async def statistics_inputs(self, patent_id: int) -> "StatisticsInputs":
        """Fingerprints of what statistics is computed from: the patent and each analog."""
        patent = await self._patent_service.get_patent(patent_id)
        analogs = await self._analog_service.get_analogs(patent_id)
        return StatisticsInputs(
            patent=fingerprint(
                [
                    patent.name,
                    patent.search_query,
                    patent.appointment,
                    patent.construction,
                    patent.operation_principle,
                    patent.technical_area,
                    patent.technical_result,
                ]
            ),
            analogs={
                a.id: fingerprint([a.analog_num, a.title, a.abstract, a.claims, a.description])
                for a in analogs
            },
        )


@dataclass(frozen=True)
class StatisticsInputs:
    """Fingerprint of the patent texts and of every analog (analog id -> fingerprint)."""

    patent: str
    analogs: dict[int, str]


def fingerprint(data: Any) -> str:
    """Stable hash of JSON-serializable data: equal data, equal fingerprint."""
    return hashlib.sha256(json.dumps(data, ensure_ascii=False).encode()).hexdigest()
