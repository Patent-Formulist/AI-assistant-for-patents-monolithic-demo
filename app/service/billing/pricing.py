from collections.abc import Iterable, Mapping

from app.temporal.workflows.analog_search import TASK_LINK_GENERATION, TASK_METADATA_ENRICHMENT
from app.temporal.workflows.identity import TASK_IDENTITY_GENERATION
from app.temporal.workflows.patent_application import TASK_GENERATE_APPLICATION
from app.temporal.workflows.statistics import STEPS
from core.enum.job_type import JobType

# Tasks of each pipeline the user can start
PIPELINE_TASKS: dict[JobType, tuple[str, ...]] = {
    JobType.ANALOG_SEARCH: (TASK_LINK_GENERATION, TASK_METADATA_ENRICHMENT),
    JobType.STATISTICS: tuple(name for name, _ in STEPS),
    JobType.IDENTITY: (TASK_IDENTITY_GENERATION,),
    JobType.APPLICATION_GENERATION: (TASK_GENERATE_APPLICATION,),
}


class PriceList:
    """Prices in kopecks: a pipeline costs the sum of its tasks that will run."""

    def __init__(self, task_prices: Mapping[str, int]):
        self._task_prices = dict(task_prices)

    def tasks(self, task_names: Iterable[str]) -> int:
        return sum(self._task_prices.get(name, 0) for name in task_names)

    def pipelines(self) -> dict[JobType, int]:
        """Full price of each pipeline, every task run."""
        return {job_type: self.tasks(tasks) for job_type, tasks in PIPELINE_TASKS.items()}
