from dataclasses import dataclass, field

from app.service.billing.billing import BillingService
from app.service.job.job import JobService
from app.service.pipeline_preconditions import (
    PipelinePreconditions,
    StatisticsInputs,
    fingerprint,
)
from app.service.processor import PipelineStarter
from app.service.task.task import TaskService
from app.temporal import shared
from app.temporal.client import WorkflowStarter
from app.temporal.workflows.statistics import (
    ATTRIBUTE_STEPS,
    COINCIDENCE_STEPS,
    StatisticsWorkflow,
)
from core import logger
from core.enum.job_type import JobType
from core.enum.task_status import TaskStatus

logger = logger.get_logger(__name__)

# Attribute steps run one after another; the coincidence steps share one order: parallel
TASK_ORDERS = {name: i for i, (name, _) in enumerate(ATTRIBUTE_STEPS)} | {
    name: len(ATTRIBUTE_STEPS) for name, _ in COINCIDENCE_STEPS
}
ANALOG_ATTRIBUTES = "analog_attributes_generation"
# Steps computed from the analogs only; the rest also read the patent
ANALOG_ONLY_STEPS = {ANALOG_ATTRIBUTES, "analog_attributes_matching"}


def step_inputs(inputs: StatisticsInputs) -> dict[str, str]:
    raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")


@dataclass
class StoredResults:

    steps: dict[str, str | None] = field(default_factory=dict)
    analogs: dict[int, str] | None = None


@dataclass
class Plan:
    skip: set[str]
    # None: generate attributes for every analog
    analog_ids: list[int] | None


class ProcessorStatisticsService(PipelineStarter):

    def __init__(
        self,
        job_service: JobService,
        task_service: TaskService,
        workflow_starter: WorkflowStarter,
        billing: BillingService,
        preconditions: PipelinePreconditions,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def run_statistics_pipeline(self, user_id: int, patent_id: int) -> int:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")






