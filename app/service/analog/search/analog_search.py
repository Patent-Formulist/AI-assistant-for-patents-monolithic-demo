from app.service.processor import PipelineStarter
from app.temporal import shared
from app.temporal.workflows.analog_search import (
    TASK_LINK_GENERATION,
    TASK_METADATA_ENRICHMENT,
    AnalogSearchWorkflow,
)
from core.enum.job_type import JobType

SEARCH_TASKS = [
    {"name": TASK_LINK_GENERATION, "order": 0},
    {"name": TASK_METADATA_ENRICHMENT, "order": 1},
]


class ProcessorAnalogSearchService(PipelineStarter):
    """Starts analog search as a Temporal workflow (ADR 0005).

    Both methods create the job with its tasks, start AnalogSearchWorkflow and
    return the job id right away; the search itself runs on the worker.
    """

    async def start_patent_search(self, patent_id: int, user_id: int) -> int:
        """Search analogs by the patent's search query and enrich them with metadata."""
        return await self._start(patent_id, user_id, analog_number=None)

    async def start_analog_search(self, patent_id: int, user_id: int, analog_number: str) -> int:
        """Add one analog, found by its number, to the patent and enrich it with metadata."""
        return await self._start(patent_id, user_id, analog_number=analog_number)

    async def _start(self, patent_id: int, user_id: int, analog_number: str | None) -> int:
        return await self._start_pipeline(
            job_type=JobType.ANALOG_SEARCH,
            task_definitions=SEARCH_TASKS,
            user_id=user_id,
            patent_id=patent_id,
            workflow_run=AnalogSearchWorkflow.run,
            # Adding one analog and searching all of them are different requests
            key=f"analog_search:{analog_number}" if analog_number else "analog_search",
            build_input=lambda job_id, step_options: shared.AnalogSearchInput(
                job_id=job_id,
                patent_id=patent_id,
                analog_number=analog_number,
                step_options=step_options,
            ),
        )
