"""Sends failed activity attempts to Sentry (worker side).

Temporal catches activity exceptions to retry them, so nothing reaches Sentry
on its own. Each failed attempt is reported with the step, the job and the
attempt number; Sentry groups repeated failures into one issue.
"""

from typing import Any

import sentry_sdk
from temporalio import activity
from temporalio.worker import ActivityInboundInterceptor, ExecuteActivityInput, Interceptor

from app.temporal import shared


class SentryInterceptor(Interceptor):
    def intercept_activity(self, next: ActivityInboundInterceptor) -> ActivityInboundInterceptor:
        return _ReportFailures(next)


class _ReportFailures(ActivityInboundInterceptor):
    async def execute_activity(self, input: ExecuteActivityInput) -> Any:
        try:
            return await super().execute_activity(input)
        except Exception as e:
            info = activity.info()
            with sentry_sdk.new_scope() as scope:
                scope.set_tag("activity", info.activity_type)
                scope.set_tag("workflow_id", info.workflow_id)
                scope.set_tag("attempt", str(info.attempt))
                if step := shared.parse_step_activity_id(info.activity_id):
                    scope.set_tag("job_id", str(step[0]))
                    scope.set_tag("task", step[1])
                scope.capture_exception(e)
            raise
