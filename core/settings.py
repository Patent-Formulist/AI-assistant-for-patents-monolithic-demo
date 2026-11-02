"""Application settings: config.yaml + environment, validated at startup.

Priority from high to low:
  1. arguments of Settings(...)  (tests)
  2. environment variables (compose passes them from .env.dev / .env.prod)
  3. env file, only when given to load_settings (DAO tests: .env.test)
  4. config.yaml (CONFIG_YAML_PATH, default config.yaml)
  5. defaults below

Environment variables keep their flat names (see ENV_PATHS): compose files and
the Temporal containers use the same names.
"""

import logging
import os
import urllib.parse
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from sqlalchemy.pool import NullPool

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variable -> place in the settings
ENV_PATHS: dict[str, tuple[str, ...]] = {
    "DATABASE_HOST": ("database", "host"),
    "DATABASE_PORT": ("database", "port"),
    "DATABASE_NAME": ("database", "db_name"),
    "DATABASE_USERNAME": ("database", "username"),
    "DATABASE_PASSWORD": ("database", "password"),
    "ROSPATENT_API_URL": ("parser", "rospatent", "api_url"),
    "ROSPATENT_API_KEY": ("parser", "rospatent", "key"),
    "ROSPATENT_DOC_PATH": ("parser", "rospatent", "docs_url"),
    "DEEPSEEK_API_URL": ("llm", "deepseek", "api_uri"),
    "JWT_SECRET_KEY": ("auth", "jwt_secret_key"),
    "WORKER_HEARTBEAT_URL": ("monitoring", "worker_heartbeat_url"),
    "SENTRY_DSN": ("monitoring", "sentry_dsn"),
    "TELEGRAM_BOT_TOKEN": ("monitoring", "telegram_bot_token"),
    "SENTRY_ENVIRONMENT": ("monitoring", "environment"),
    "SMTP_HOST": ("mail", "host"),
    "SMTP_PORT": ("mail", "port"),
    "SMTP_USERNAME": ("mail", "username"),
    "SMTP_PASSWORD": ("mail", "password"),
    "SMTP_FROM": ("mail", "from_address"),
    "EMAIL_VERIFICATION_URL": ("auth", "email_verification_url"),
    "YOOKASSA_SHOP_ID": ("payments", "yookassa", "shop_id"),
    "YOOKASSA_SECRET_KEY": ("payments", "yookassa", "secret_key"),
    "PAYMENT_RETURN_URL": ("payments", "return_url"),
    "TEMPORAL_ADDRESS": ("temporal", "address"),
    "TEMPORAL_NAMESPACE": ("temporal", "namespace"),
    "LOG_DIR": ("log", "logs_dir"),
    "LOG_FILE_SYSTEM": ("log", "file_system"),
    "LOG_FILE_USER": ("log", "file_user"),
    "DEBUG": ("log", "debug"),
}


class _Section(BaseModel):
    """Settings are fixed for the life of the process: no assignment after startup."""

    model_config = ConfigDict(frozen=True)


class StorageSettings(_Section):
    storage_dir: str = "./storage"
    prompt_dir: str = "./prompts"
    analog_attribute_prompt_path: str = ""
    analog_attribute_matcher_prompt_path: str = ""
    analog_checking_attribute_prompt_path: str = ""
    analog_identify_prompt_path: str = ""
    search_query_instruction: str = ""
    patent_checking_attribute_prompt_path: str = ""
    patent_attribute_matcher_prompt_path: str = ""


class DatabaseSettings(_Section):
    host: str = "localhost"
    port: int = 5432
    db_name: str = "formulist"
    username: str = "admin"
    password: SecretStr = SecretStr("admin1admin")

    protocol: str = "postgresql+asyncpg"
    echo: bool = False
    pool_class: Literal["NullPool", "QueuePool"] = "QueuePool"
    pool_size: int = 10
    max_overflow: int = 30
    pre_ping: bool = True
    pool_recycle: int = 3600
    expire_on_commit: bool = True
    autocommit: bool = False
    autoflush: bool = True
    future: bool = True

    @property
    def database_url(self) -> str:
        """URL for SQLAlchemy; contains the password, do not log it."""
        protocol = self.protocol.replace("://", "")
        user = urllib.parse.quote_plus(self.username)
        password = self.password.get_secret_value()
        if password:
            user = f"{user}:{urllib.parse.quote_plus(password)}"
        return f"{protocol}://{user}@{self.host}:{self.port}/{self.db_name}"

    @property
    def engine_kwargs(self) -> dict[str, Any]:
        """Parameters for the SQLAlchemy engine."""
        kwargs: dict[str, Any] = {
            "echo": self.echo,
            "pool_pre_ping": self.pre_ping,
            "pool_recycle": self.pool_recycle,
            "future": self.future,
        }
        if self.pool_class == "NullPool":
            kwargs["poolclass"] = NullPool
        else:
            kwargs.update(pool_size=self.pool_size, max_overflow=self.max_overflow)
        return kwargs

    @property
    def session_kwargs(self) -> dict[str, Any]:
        """Parameters for the SQLAlchemy session."""
        return {
            "expire_on_commit": self.expire_on_commit,
            "autocommit": self.autocommit,
            "autoflush": self.autoflush,
            "future": self.future,
        }


class RospatentSettings(_Section):
    """Rospatent search platform (https://searchplatform.rospatent.gov.ru/for_developers)."""

    api_url: str = "https://searchplatform.rospatent.gov.ru/patsearch/v0.2/search"
    # Required: the single key is given at startup, there is no key storage for Rospatent
    key: SecretStr = Field(min_length=1)
    docs_url: str = "https://searchplatform.rospatent.gov.ru/patsearch/v0.2/docs"

    request_language: Literal["q", "qn"] = "q"
    request_limit: int = Field(6, ge=0, le=10000)
    request_sort: str = "relevance"
    request_group_by: str = "family:docdb"
    request_countries: str = "RU"
    request_base_delay: int = 3
    request_timeout: int = 100
    request_retries: int = 3
    max_concurrent_requests: int = 10
    user_agent: str = "Formulist/1.2"
    required_fields: tuple[str, ...] = ("abstract", "claims", "description")
    priority_langs: tuple[str, ...] = ("ru", "eu")


class ParserSettings(_Section):
    rospatent: RospatentSettings


class LLMSettings(_Section):
    api_uri: str = ""
    temperature: float = 0
    referer: str = ""
    site_name: str = ""
    model: str = ""
    max_retries: int = 3
    base_delay: int = 2


class DeepSeekSettings(LLMSettings):
    api_uri: str = "https://api.deepseek.com/v1/chat/completions"
    max_retries_get_key: int = 3
    timeout: int = 120


class LLMProviders(_Section):
    deepseek: DeepSeekSettings = DeepSeekSettings()


class TemporalSettings(_Section):
    """Temporal client and worker settings (ADR 0005)."""

    address: str = "localhost:7233"
    namespace: str = "default"
    # Parallel Rospatent/LLM activities per worker process
    external_max_concurrent_activities: int = 5
    # Last-resort limit for a whole workflow execution (see WorkflowStarter.start)
    workflow_execution_timeout_seconds: int = 7200
    # Raw temporal.steps: activity timeouts and retries (see step_options_from_config)
    steps: dict[str, Any] = {}


class BillingSettings(_Section):
    """Prices of pipeline tasks.

    A pipeline costs the sum of its tasks that will run; a task not listed is free.
    """

    # Task name -> price in kopecks
    task_prices: dict[str, int] = {}
    # A hold outlives the longest workflow by this much, then stops reserving money
    hold_margin_seconds: int = 600


class YooKassaSettings(_Section):
    api_url: str = "https://api.yookassa.ru/v3"
    # Both empty: payments are off (the API answers 503)
    shop_id: str = ""
    secret_key: SecretStr = SecretStr("")
    timeout_seconds: int = 30
    # VAT code of the receipt item (54-FZ); None: no receipt is sent with the payment
    # (when the shop sends receipts itself or they are not needed)
    receipt_vat_code: int | None = None
    receipt_item_description: str = "Пополнение баланса Formulist"

    @property
    def enabled(self) -> bool:
        return bool(self.shop_id and self.secret_key.get_secret_value())


class PaymentSettings(_Section):
    yookassa: YooKassaSettings = YooKassaSettings()
    # Where the payment page returns the user
    return_url: str = "http://localhost/profile"
    # Top-up limits, kopecks
    min_amount: int = 100_00
    max_amount: int = 100_000_00


class LegalDocumentSettings(_Section):
    title: str
    # Current version: storage/legal/<document>/<version>.md; older files stay for history
    version: str
    # True: the user must accept the current version (POST /legal/consents)
    requires_consent: bool = False


class LegalSettings(_Section):
    """Published legal documents."""

    documents: dict[str, LegalDocumentSettings] = {}


class MonitoringSettings(_Section):
    """Health checks and outside monitors."""

    # A check slower than this counts as failed
    health_timeout_seconds: float = 3
    # healthchecks.io-style ping URL: the worker GETs it while healthy and
    # <url>/fail when not; empty: no heartbeat
    worker_heartbeat_url: str = ""
    worker_heartbeat_seconds: int = 60
    # Sentry project DSN; empty: errors are not sent anywhere
    sentry_dsn: SecretStr = SecretStr("")
    # Sentry environment tag: dev / prod
    environment: str = "dev"
    # Bot that sends alerts to administrators with a tg_id; empty: alerts only go to the log
    telegram_bot_token: SecretStr = SecretStr("")
    # The same alert (by key) at most this often
    alert_repeat_seconds: int = 3600
    # At most this many alerts per window; the rest are counted and summarised
    alert_burst: int = 10
    alert_burst_window_seconds: int = 600
    # Worker watchdog: how often it looks for stuck money and keys
    watchdog_seconds: int = 600
    # A refund not finished after this long is stuck
    refund_stuck_minutes: int = 30
    # Alert when the last usable LLM key expires sooner than this
    llm_key_warning_days: int = 3


class MailSettings(_Section):
    """SMTP for service mail (email confirmation). Without a host mail goes to the log."""

    host: str = ""
    port: int = 587
    username: str = ""
    password: SecretStr = SecretStr("")
    from_address: str = ""
    # STARTTLS on a plain connection (587) or TLS from the start (465)
    starttls: bool = True
    use_ssl: bool = False
    timeout_seconds: int = 30

    @property
    def enabled(self) -> bool:
        return bool(self.host and self.from_address)


class AuthSettings(_Section):
    # Required: without it tokens would be signed with a key known to everyone
    jwt_secret_key: SecretStr = Field(min_length=32)
    access_token_expire_minutes: int = 4000
    refresh_token_expire_minutes: int = 400
    jwt_algorithm: str = "HS256"
    # Frontend page that confirms the email: the link is <url>?token=<token>
    email_verification_url: str = "http://localhost/verify-email"
    email_verification_ttl_minutes: int = 24 * 60
    # A new verification email at most this often
    email_verification_resend_seconds: int = 60


class LogSettings(_Section):
    logs_dir: str = "./logs"
    debug: bool = False
    file_system: str = "system.log"
    file_user: str = "user.log"
    max_bytes: int = 10 * 1024 * 1024
    backup_count: int = 5
    encoding: str = "utf-8"
    system_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    user_format: str = "%(asctime)s - %(message)s"
    file_level: str = "INFO"
    console_level: str = "INFO"

    def get_log_file_path(self, log_type: str = "system") -> Path:
        """Full path of a log file."""
        filename = self.file_system if log_type == "system" else self.file_user
        return Path(self.logs_dir) / filename

    @property
    def log_level(self) -> int:
        return logging.DEBUG if self.debug else logging.INFO


class _FlatEnvSource(PydanticBaseSettingsSource):
    """Places the flat environment variables of ENV_PATHS into the sections."""

    def __init__(self, settings_cls: type[BaseSettings], *sources: EnvSettingsSource):
        super().__init__(settings_cls)
        # From high to low priority
        self._sources = sources

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        # Abstract in PydanticBaseSettingsSource, so it must exist. Never called:
        # __call__ is overridden and builds the whole dict from ENV_PATHS.
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for name, path in ENV_PATHS.items():
            # The sources keep the names in lower case
            values = (source.env_vars.get(name.lower()) for source in self._sources)
            value = next((v for v in values if v is not None), None)
            if value is None:
                continue
            node = data
            for key in path[:-1]:
                node = node.setdefault(key, {})
            node[path[-1]] = value
        return data


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        # VAR= (empty) counts as not set: the next source (.env, config.yaml, default) is used.
        # compose passes unset variables as empty strings (${ROSPATENT_API_KEY:-}).
        env_ignore_empty=True,
        hide_input_in_errors=True,  # the error must not print secrets
        frozen=True,
    )

    storage: StorageSettings = StorageSettings()
    database: DatabaseSettings = DatabaseSettings()
    parser: ParserSettings
    llm: LLMProviders = LLMProviders()
    temporal: TemporalSettings = TemporalSettings()
    billing: BillingSettings = BillingSettings()
    payments: PaymentSettings = PaymentSettings()
    legal: LegalSettings = LegalSettings()
    mail: MailSettings = MailSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    auth: AuthSettings
    log: LogSettings = LogSettings()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        yaml_file = BASE_DIR / os.getenv("CONFIG_YAML_PATH", "config.yaml")
        return (
            init_settings,
            _FlatEnvSource(settings_cls, env_settings, dotenv_settings),
            YamlConfigSettingsSource(settings_cls, yaml_file=yaml_file),
        )


def load_settings(env_file: str | Path | None = None) -> Settings:
    """Build settings from config.yaml and the environment.

    No env file is read by default: compose passes the variables directly.
    A given env_file (relative to the repository root) must exist.
    """
    if env_file is None:
        return Settings(_env_file=None)
    env_path = BASE_DIR / env_file
    if not env_path.is_file():
        raise FileNotFoundError(f"Env file not found: {env_path}")
    return Settings(_env_file=env_path)


@lru_cache
def get_settings() -> Settings:
    """Process-wide settings, built on the first call.

    They are read once and frozen until the process stops: after changing
    .env.dev / .env.prod recreate the containers (see README).
    """
    return load_settings()
