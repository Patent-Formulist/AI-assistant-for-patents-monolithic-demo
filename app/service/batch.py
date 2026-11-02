import asyncio
from collections.abc import Awaitable, Callable, Hashable

from core import logger

logger = logger.get_logger(__name__)


class BatchItemsFailedError(Exception):
    """Some items of a batch failed even after retries; the whole batch fails.

    A partial result would look complete: statistics without some analogs,
    paid for and never noticed. The message names the items and is shown to
    the user through the job error.
    """

    def __init__(self, what: str, failed: dict[Hashable, BaseException]):
        self.failed = failed
        names = ", ".join(str(key) for key in failed)
        first = next(iter(failed.values()))
        super().__init__(f"Не удалось обработать {what}: {names} ({first})")


async def gather_all[K: Hashable, T](
    items: dict[K, Callable[[], Awaitable[T]]],
    what: str,
    retries: int = 2,
) -> dict[K, T]:
    """Run every item concurrently; retry the failed ones; fail if any still fails.

    ``items`` maps a key (e.g. analog number) to a call that produces its
    result. Failed items are retried up to ``retries`` more rounds: an LLM
    answer that did not parse usually parses on the next ask.
    """
    results: dict[K, T] = {}
    pending = dict(items)
    failed: dict[K, BaseException] = {}
    for round_ in range(retries + 1):
        keys = list(pending)
        outcomes = await asyncio.gather(*(pending[k]() for k in keys), return_exceptions=True)
        failed = {}
        for key, outcome in zip(keys, outcomes, strict=True):
            if isinstance(outcome, asyncio.CancelledError):
                raise outcome
            if isinstance(outcome, BaseException):
                failed[key] = outcome
            else:
                results[key] = outcome
        if not failed:
            return results
        logger.warning(
            f"{len(failed)} of {len(items)} {what} failed in round {round_ + 1}: "
            + "; ".join(f"{k}: {e}" for k, e in failed.items())
        )
        pending = {k: items[k] for k in failed}
    raise BatchItemsFailedError(what, failed)
