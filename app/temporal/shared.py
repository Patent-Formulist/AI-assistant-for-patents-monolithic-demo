"""Contracts shared by workflows, activities and starters.

Pure Python only: workflow code imports this module inside the Temporal
sandbox, so it must not pull in SQLAlchemy, aiohttp or app services.
"""

from dataclasses import dataclass, field

# Task queues: workflows and database activities / calls to external services
PIPELINES_TASK_QUEUE = "pipelines"
EXTERNAL_TASK_QUEUE = "external"

# --- Job/task status activities (pipelines queue) ---
MARK_JOB_RUNNING = "mark_job_running"
MARK_JOB_COMPLETED = "mark_job_completed"
MARK_JOB_FAILED = "mark_job_failed"
MARK_TASK_RUNNING = "mark_task_running"
MARK_TASK_COMPLETED = "mark_task_completed"
MARK_TASK_FAILED = "mark_task_failed"

# --- Analog search activities (external queue) ---
FIND_PATENT_ANALOG_LINKS = "find_patent_analog_links"
ENRICH_PATENT_ANALOGS_METADATA = "enrich_patent_analogs_metadata"
FIND_ANALOG_LINK = "find_analog_link"
ENRICH_ANALOG_METADATA = "enrich_analog_metadata"

# --- Statistics activities (external queue) ---
GENERATE_ANALOG_ATTRIBUTES = "generate_analog_attributes"
MATCH_ANALOG_ATTRIBUTES = "match_analog_attributes"
GENERATE_PATENT_ATTRIBUTES = "generate_patent_attributes"
GENERATE_GENERAL_ATTRIBUTES = "generate_general_attributes"
GENERATE_ANALOG_COINCIDENCES = "generate_analog_coincidences"
GENERATE_PATENT_COINCIDENCES = "generate_patent_coincidences"

# --- Identity prototype activities (external queue) ---
GENERATE_IDENTITY = "generate_identity"

# --- Patent application activities (external queue) ---
GENERATE_APPLICATION = "generate_application"


@dataclass
class RetryOptions:
    """Activity retry policy in plain numbers (becomes temporalio RetryPolicy)."""

    initial_interval_seconds: float = 1.0
    backoff_coefficient: float = 2.0
    maximum_interval_seconds: float | None = None
    # 0 means unlimited attempts
    maximum_attempts: int = 0


@dataclass
class ActivityOptions:
    start_to_close_seconds: float
    retry: RetryOptions = field(default_factory=RetryOptions)


def _default_status_options() -> ActivityOptions:
    # Status writes are short and must reach the database even during outages
    return ActivityOptions(
        start_to_close_seconds=30,
        retry=RetryOptions(maximum_interval_seconds=30, maximum_attempts=10),
    )


def _default_external_options() -> ActivityOptions:
    # Steps calling external services (Rospatent, LLM)
    return ActivityOptions(
        start_to_close_seconds=900,
        retry=RetryOptions(
            initial_interval_seconds=5,
            backoff_coefficient=2.0,
            maximum_interval_seconds=60,
            maximum_attempts=3,
        ),
    )


@dataclass
class StepOptions:
    """Timeouts and retries of a workflow's activities.

    The starter fills it from config.yaml (``temporal.steps``) and passes it in
    the workflow input: the workflow must not read config itself, and a value
    recorded in the input keeps replays deterministic. A config change applies to
    workflows started after it; running ones keep their options.
    """

    status: ActivityOptions = field(default_factory=_default_status_options)
    external: ActivityOptions = field(default_factory=_default_external_options)


@dataclass
class AnalogSearchInput:
    """Search analogs for a patent; with ``analog_number`` — add that one analog."""

    job_id: int
    patent_id: int
    analog_number: str | None = None
    step_options: StepOptions = field(default_factory=StepOptions)


@dataclass
class PatentPipelineInput:
    """A pipeline over one patent: statistics, identity prototype, patent application."""

    job_id: int
    patent_id: int
    step_options: StepOptions = field(default_factory=StepOptions)


@dataclass
class StatisticsInput(PatentPipelineInput):
    """Statistics; only what changed since the stored results is recomputed.

    ``skip_steps`` are tasks whose results in the database come from the same
    inputs. ``analog_ids`` limits analog attribute generation to changed and new
    analogs; None means all of them.
    """

    skip_steps: list[str] = field(default_factory=list)
    analog_ids: list[int] | None = None


def step_activity_id(job_id: int, task_name: str) -> str:
    """Activity ID of a pipeline step: tells the activity side whose step it runs.

    Unique within a workflow run: a job runs each of its tasks once.
    """
    return f"job-{job_id}:{task_name}"


def parse_step_activity_id(activity_id: str) -> tuple[int, str] | None:
    """(job_id, task_name) from ``step_activity_id``; None for other activities."""
    prefix, sep, task_name = activity_id.partition(":")
    if not sep or not prefix.startswith("job-") or not prefix[4:].isdigit():
        return None
    return int(prefix[4:]), task_name


def patent_workflow_id(patent_id: int) -> str:
    """One workflow ID for every pipeline of a patent.

    The pipelines of a patent run strictly one after another; Temporal refuses
    to start a workflow while another one with the same ID is running, so the
    ID makes that rule atomic. A finished workflow frees the ID.
    """
    return f"patent-{patent_id}"
