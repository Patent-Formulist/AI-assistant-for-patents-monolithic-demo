"""Side channel for LLM token usage: LLMClient adds, the caller around it collects.

``LLMClient.ask`` returns only the answer text. The usage of every response goes
to the collector opened by the code that runs the work (the Temporal activity
interceptor), which knows whose work it is and stores it. Without an open
collector the usage is dropped.

The collector lives in a context variable: tasks started inside (``asyncio.gather``)
copy the context and add to the same collector.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field


@dataclass(frozen=True)
class LLMUsage:
    """Tokens one LLM response was billed for."""

    model: str
    prompt_tokens: int
    completion_tokens: int
    # Prompt tokens served from the provider's cache (billed cheaper)
    cached_tokens: int = 0
    key_id: str | None = None


@dataclass
class UsageCollector:
    records: list[LLMUsage] = field(default_factory=list)


_collector: ContextVar[UsageCollector | None] = ContextVar("llm_usage_collector", default=None)


@contextmanager
def collect_usage() -> Iterator[UsageCollector]:
    """Collect the usage of the LLM calls made inside the block."""
    collector = UsageCollector()
    token = _collector.set(collector)
    try:
        yield collector
    finally:
        _collector.reset(token)


def record_usage(usage: LLMUsage) -> None:
    """Add usage to the open collector; without one it is dropped."""
    collector = _collector.get()
    if collector is not None:
        collector.records.append(usage)
