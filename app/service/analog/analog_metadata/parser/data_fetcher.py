import re

from core import logger
from core.exceptions import ParserError

logger = logger.get_logger(__name__)


class ParserAnalogMetadataDataFetcher:
    def fetch(
        self,
        number: str,
        data: dict,
        required_fields: list[str],
        lang: str = "ru",
        priority_langs: list[str] = None,
    ) -> dict[str, str]:
        """
        Extracts patent document data from API response.

        Args:
            number: Patent number for logging.
            data: Raw API response dictionary.
            lang: Language code (e.g., "ru", "en") or "all" to take any available language.

        Returns:
            PatentDocument or None if extraction fails.
        """
        required_fields = required_fields or ["abstract", "claims", "description"]
        try:
            logger.debug(f"Extracting metadata for patent {number} (lang={lang})")
            patent_data = {}
            for field in required_fields:
                patent_data[field] = self._get_nested_text(data, field, lang, priority_langs)
            logger.debug(f"Extracted {len(patent_data)} fields for patent {number}")
            return patent_data
        except Exception as e:
            logger.error(
                f"Unexpected error extracting data for patent {number}: {e}",
                exc_info=True,
            )
            raise ParserError(f"Failed to extract patent {number}: {e}") from e

    def _get_nested_text(
        self, data: dict, field: str, lang: str, priority_langs: list[str] = None
    ) -> str:
        """
        Extract text from nested dictionary with language selection.

        Args:
            data: API response dict.
            field: Top-level field name (e.g., "abstract").
            lang: Language code (e.g., "ru", "en") or "all".
            priority_langs: Ordered list of preferred languages (used only if lang=="all").

        Returns:
            Extracted text or empty string.
        """
        nested = data.get(field)
        if not isinstance(nested, dict):
            return ""

        if lang != "all":
            # Specific language
            text = nested.get(lang, "")
            return self._clean_xml(text) if text else ""

        # lang == "all" – use priority list if provided
        if priority_langs:
            # First, try priority languages in order
            for prio in priority_langs:
                if prio in nested and nested[prio] and isinstance(nested[prio], str):
                    return self._clean_xml(nested[prio])
            # Then, any other language (excluding already checked)
            for key, value in nested.items():
                if key not in priority_langs and isinstance(value, str) and value.strip():
                    return self._clean_xml(value)
            return ""
        else:
            # No priority list – first non-empty value in any order
            for value in nested.values():
                if isinstance(value, str) and value.strip():
                    return self._clean_xml(value)
            return ""

    @staticmethod
    def _clean_xml(xml_string: str) -> str:
        """Remove XML tags and normalize whitespace."""
        if not xml_string or not isinstance(xml_string, str):
            return ""
        try:
            # Remove XML tags
            text = re.sub(r"<[^>]+>", "", xml_string)
            # Remove ASCII control characters
            text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
            # Ensure valid UTF-8
            text = text.encode("utf-8", "ignore").decode("utf-8")
            # Normalize whitespace (any whitespace sequence -> single space) and trim
            text = " ".join(text.split())
            # Optional: clean spaces around punctuation (keep if you need)
            text = re.sub(r"\s+([.,;:!?])", r"\1", text)
            text = re.sub(r"([.,;:!?])\s+", r"\1 ", text)
            return text.strip()
        except Exception as e:
            logger.warning(f"Error cleaning text: {e}")
            raise
