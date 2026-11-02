"""Alerts to administrators in Telegram: problems that are not exceptions.

Sentry reports errors; this reports states that need a person: a pipeline
failed for good, a refund is stuck, money is held by a dead workflow, LLM
keys run out. Recipients are users with ``is_admin`` and a ``tg_id``.

Alerts never fail the caller: a Telegram outage is logged and forgotten.
The same alert (by key) is sent at most once per ``alert_repeat_seconds``,
and at most ``alert_burst`` alerts go out per window, so a mass failure
(the LLM is down: every job fails) does not flood the chat.
"""

import time
from collections import deque

import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core import logger
from core.db.models.user import UserModel
from core.settings import MonitoringSettings

logger = logger.get_logger(__name__)

TELEGRAM_API = "https://api.telegram.org"


class AlertService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        settings: MonitoringSettings,
        api_url: str = TELEGRAM_API,
        clock=time.monotonic,
    ):
        self._session_factory = session_factory
        self._settings = settings
        self._api_url = api_url
        self._clock = clock
        self._last_sent: dict[str, float] = {}
        self._window: deque[float] = deque()
        self._suppressed = 0

    async def alert(self, key: str, text: str) -> None:
        """Send ``text`` unless the same ``key`` was sent recently or the burst is spent."""
        now = self._clock()
        last = self._last_sent.get(key)
        if last is not None and now - last < self._settings.alert_repeat_seconds:
            return
        while self._window and now - self._window[0] > self._settings.alert_burst_window_seconds:
            self._window.popleft()
        if len(self._window) >= self._settings.alert_burst:
            self._suppressed += 1
            logger.warning(f"Alert suppressed (burst): {text}")
            return
        self._last_sent[key] = now
        self._window.append(now)
        if self._suppressed:
            text += (
                f"\n\n(и ещё {self._suppressed} алертов пропущено: слишком много за короткое время)"
            )
            self._suppressed = 0
        logger.warning(f"ALERT {key}: {text}")
        await self._send(text)

    async def _send(self, text: str) -> None:
        token = self._settings.telegram_bot_token.get_secret_value()
        if not token:
            return
        try:
            async with self._session_factory() as session:
                chats = (
                    await session.scalars(
                        select(UserModel.tg_id).where(
                            UserModel.is_admin, UserModel.tg_id.is_not(None)
                        )
                    )
                ).all()
            if not chats:
                logger.warning("No administrator has a tg_id: the alert stays in the log")
                return
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as http:
                for chat_id in chats:
                    async with http.post(
                        f"{self._api_url}/bot{token}/sendMessage",
                        json={"chat_id": chat_id, "text": text[:4000]},
                    ) as response:
                        if response.status != 200:
                            logger.error(f"Telegram answered {response.status} for chat {chat_id}")
        except Exception as e:
            logger.error(f"Could not send an alert to Telegram: {e}")
