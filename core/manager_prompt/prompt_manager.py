import asyncio
from pathlib import Path
from typing import Any

from core import logger
from core.enum.ai_purpose import AIPurpose
from core.settings import StorageSettings

logger = logger.get_logger(__name__)


class PromptError(RuntimeError):
    """Raised when a prompt cannot be located or rendered.

    Returning an empty prompt instead would silently feed the LLM nothing and
    let the pipeline "succeed" with no output, so failures are surfaced loudly.
    """


class PromptManager:
    _instance = None

    def __init__(self, config: StorageSettings):
        self._config = config

    @classmethod
    def init(cls, config: StorageSettings) -> "PromptManager":
        if not cls._instance:
            cls._instance = cls(config)
        return cls._instance

    async def get_prompt(self, purpose: AIPurpose, variables: dict[str, Any]):
        prompt_path = await self._resolve_prompt_path(purpose)
        try:
            # Read off the event loop: prompts are loaded on every LLM call
            raw_prompt = await asyncio.to_thread(Path(prompt_path).read_text, encoding="utf-8")
        except (FileNotFoundError, IsADirectoryError) as e:
            logger.error(f"Prompt path not found: {prompt_path}")
            raise PromptError(f"Prompt path not found: {prompt_path}") from e

        try:
            logger.info(f"Raw prompt loaded, length: {len(raw_prompt)}")

            prompt = raw_prompt.format(**variables)
            logger.info(f"Final prompt, length: {len(prompt)}")
            return prompt
        except KeyError as e:
            # Missing template variable: the builder did not supply a {placeholder}
            # the template requires. Fail loudly instead of sending an empty prompt.
            logger.error(
                f"Prompt {prompt_path} is missing template variable {e}; "
                f"supplied variables: {sorted(variables)}"
            )
            raise PromptError(f"Missing template variable {e} for prompt {purpose}") from e
        except PromptError:
            raise
        except Exception as e:
            logger.error(f"Failed to read or format prompt {prompt_path}: {e}")
            raise PromptError(f"Failed to read or format prompt {purpose}: {e}") from e

    async def _resolve_prompt_path(self, purpose: AIPurpose) -> Path:
        path = ""
        if AIPurpose.IDENTIFY == purpose:
            path = self._config.analog_identify_prompt_path
        elif AIPurpose.ANALOG_ATTRIBUTE_GENERATION == purpose:
            path = self._config.analog_attribute_prompt_path
        elif AIPurpose.PATENT_ATTRIBUTE_GENERATION == purpose:
            path = self._config.patent_attribute_matcher_prompt_path
        elif AIPurpose.ANALOG_ATTRIBUTE_MATCHER == purpose:
            path = self._config.analog_attribute_matcher_prompt_path
        elif AIPurpose.PATENT_ATTRIBUTE_MATCHER == purpose:
            path = self._config.patent_attribute_matcher_prompt_path
        elif AIPurpose.GENERAL_ATTRIBUTE == purpose:
            path = self._config.analog_attribute_matcher_prompt_path
        elif AIPurpose.ANALOG_CHECKING_ATTRIBUTE == purpose:
            path = self._config.analog_checking_attribute_prompt_path
        elif AIPurpose.PATENT_CHECKING_ATTRIBUTE == purpose:
            path = self._config.patent_checking_attribute_prompt_path
        storage_dir = self._config.storage_dir
        prompt_dir = self._config.prompt_dir
        return Path(storage_dir) / prompt_dir / path
