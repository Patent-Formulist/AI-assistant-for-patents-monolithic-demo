from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from app.temporal import shared
    from app.temporal.workflows.base import PipelineWorkflow

TASK_IDENTITY_GENERATION = "identity_generation"


@workflow.defn(name="IdentityWorkflow")
class IdentityWorkflow(PipelineWorkflow):
    """Identity prototype of the patent from its analogs and attributes via LLM."""

    @workflow.run
    async def run(self, pipeline: shared.PatentPipelineInput) -> None:
        await self._run_job(
            pipeline.job_id,
            pipeline.step_options,
            lambda: self._step(
                pipeline.job_id,
                TASK_IDENTITY_GENERATION,
                shared.GENERATE_IDENTITY,
                pipeline.patent_id,
            ),
        )
