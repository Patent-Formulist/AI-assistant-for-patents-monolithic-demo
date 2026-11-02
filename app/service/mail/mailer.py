import asyncio
import smtplib
from email.message import EmailMessage

from core import logger
from core.settings import MailSettings

logger = logger.get_logger(__name__)


class Mailer:
    """Plain-text email over SMTP.

    Without SMTP settings (dev) the message is written to the log instead,
    so links in it can still be followed by hand.
    """

    def __init__(self, settings: MailSettings):
        self._settings = settings

    async def send(self, to: str, subject: str, text: str) -> None:
        if not self._settings.enabled:
            logger.warning(f"SMTP is not configured; mail to {to}: {subject}\n{text}")
            return
        message = EmailMessage()
        message["From"] = self._settings.from_address
        message["To"] = to
        message["Subject"] = subject
        message.set_content(text)
        # smtplib blocks: keep the event loop free
        await asyncio.to_thread(self._send, message)
        logger.info(f"Mail sent to {to}: {subject}")

    def _send(self, message: EmailMessage) -> None:
        settings = self._settings
        smtp_class = smtplib.SMTP_SSL if settings.use_ssl else smtplib.SMTP
        with smtp_class(settings.host, settings.port, timeout=settings.timeout_seconds) as smtp:
            if settings.starttls and not settings.use_ssl:
                smtp.starttls()
            if settings.username:
                smtp.login(settings.username, settings.password.get_secret_value())
            smtp.send_message(message)
