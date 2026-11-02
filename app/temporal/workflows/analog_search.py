from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from app.temporal import shared
    from app.temporal.workflows.base import PipelineWorkflow

TASK_LINK_GENERATION = "analog_link_generation"
TASK_METADATA_ENRICHMENT = "analog_metadata_enrichment"


@workflow.defn(name="AnalogSearchWorkflow")
class AnalogSearchWorkflow(PipelineWorkflow):
    """Find analog links on Rospatent, then enrich the analogs with metadata.

    Without an analog number every analog found by the patent's search query is
    processed; with one — only that analog is added to the patent.
    """

    @workflow.run
    async def run(self, search: shared.AnalogSearchInput) -> None:
        await self._run_job(search.job_id, search.step_options, lambda: self._search(search))

    async def _search(self, search: shared.AnalogSearchInput) -> None:
        job_id = search.job_id
        if search.analog_number is None:
            await self._step(
                job_id, TASK_LINK_GENERATION, shared.FIND_PATENT_ANALOG_LINKS, search.patent_id
            )
            await self._step(
                job_id,
                TASK_METADATA_ENRICHMENT,
                shared.ENRICH_PATENT_ANALOGS_METADATA,
                search.patent_id,
            )
            return

        analog_id = await self._step(
            job_id,
            TASK_LINK_GENERATION,
            shared.FIND_ANALOG_LINK,
            search.patent_id,
            search.analog_number,
            result_type=int,
        )
        await self._step(job_id, TASK_METADATA_ENRICHMENT, shared.ENRICH_ANALOG_METADATA, analog_id)
