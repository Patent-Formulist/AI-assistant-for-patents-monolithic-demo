from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from app.temporal import shared
    from app.temporal.workflows.base import PipelineWorkflow

TASK_GENERATE_APPLICATION = "generate_application"


@workflow.defn(name="PatentApplicationWorkflow")
class PatentApplicationWorkflow(PipelineWorkflow):
    """Abstract, claims and description of the patent application via LLM."""

    @workflow.run
    async def run(self, pipeline: shared.PatentPipelineInput) -> None:
        await self._run_job(
            pipeline.job_id,
            pipeline.step_options,
            lambda: self._step(
                pipeline.job_id,
                TASK_GENERATE_APPLICATION,
                shared.GENERATE_APPLICATION,
                pipeline.patent_id,
            ),
        )
