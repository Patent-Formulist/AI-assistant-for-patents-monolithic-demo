import asyncio

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from app.temporal import shared
    from app.temporal.workflows.base import PipelineWorkflow

# Task name -> activity. Attributes form a chain: each step reads what the
# previous one saved (patent attributes use the matched analog attributes).
ATTRIBUTE_STEPS = (
    ("analog_attributes_generation", shared.GENERATE_ANALOG_ATTRIBUTES),
    ("analog_attributes_matching", shared.MATCH_ANALOG_ATTRIBUTES),
    ("patent_attributes_generation", shared.GENERATE_PATENT_ATTRIBUTES),
    ("general_attributes_generation", shared.GENERATE_GENERAL_ATTRIBUTES),
)
# Both read only the general attributes and write their own signs: run in parallel
COINCIDENCE_STEPS = (
    ("analog_coincidence", shared.GENERATE_ANALOG_COINCIDENCES),
    ("patent_coincidence", shared.GENERATE_PATENT_COINCIDENCES),
)
STEPS = ATTRIBUTE_STEPS + COINCIDENCE_STEPS


@workflow.defn(name="StatisticsWorkflow")
class StatisticsWorkflow(PipelineWorkflow):
    """Attributes of the analogs and the patent via LLM, then their coincidences."""

    @workflow.run
    async def run(self, pipeline: shared.StatisticsInput) -> None:
        await self._run_job(pipeline.job_id, pipeline.step_options, lambda: self._steps(pipeline))

    async def _steps(self, pipeline: shared.StatisticsInput) -> None:
        # Skipped steps have results from the same inputs already; their tasks
        # are created SKIPPED by the starter
        skip = set(pipeline.skip_steps)
        for task_name, activity_name in ATTRIBUTE_STEPS:
            if task_name in skip:
                continue
            args = [pipeline.patent_id]
            if activity_name == shared.GENERATE_ANALOG_ATTRIBUTES:
                args.append(pipeline.analog_ids)
            await self._step(pipeline.job_id, task_name, activity_name, *args)

        # Wait for both even if one fails, so each task gets its final status
        results = await asyncio.gather(
            *(
                self._step(pipeline.job_id, task_name, activity_name, pipeline.patent_id)
                for task_name, activity_name in COINCIDENCE_STEPS
                if task_name not in skip
            ),
            return_exceptions=True,
        )
        errors = [r for r in results if isinstance(r, BaseException)]
        if errors:
            raise errors[0]
