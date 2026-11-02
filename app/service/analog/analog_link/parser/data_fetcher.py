from typing import Any

from core import logger

logger = logger.get_logger(__name__)


class ParserAnalogLinkDataFetcher:
    """
    Fetches and structures patent analog link data from API response hits.

    This class is responsible for extracting patent information from raw API
    responses and converting it into a structured format suitable for further
    processing or storage.
    """

    @staticmethod
    def fetch(docs_url: str, hits: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
        """
        Extracts patent data from the API response.

        Args:
            docs_url: Base URL of the Rospatent documents endpoint.
            hits: List of raw patent dictionaries from the API.

        Returns:
            Dictionary mapping patent numbers to their extracted details.
        """
        logger.debug(f"Extracting data from {len(hits)} patent hits")

        patent_entries = {}
        for index, item in enumerate(hits):
            try:
                patent_data = ParserAnalogLinkDataFetcher._parse_single_patent(
                    index, item, docs_url
                )
                if patent_data:
                    patent_number = patent_data["patent_number"]
                    patent_entries[patent_number] = patent_data["details"]
            except Exception as e:
                logger.error(
                    f"Unexpected error processing patent at index {index}: {e}",
                    exc_info=True,
                )

        logger.debug(f"Successfully extracted {len(patent_entries)} patents")
        return patent_entries

    @staticmethod
    def _parse_single_patent(
        index: int, item: dict[str, Any], docs_url: str
    ) -> dict[str, Any] | None:
        try:
            common = item.get("common", {})
            doc_number = common.get("document_number")
            kind = common.get("kind", "")
            office = common.get("publishing_office", "")
            pub_date = common.get("publication_date", "").replace(".", "")

            title = "No title"

            biblio = item.get("biblio", {})
            if biblio:
                ru = biblio.get("ru", {})
                if ru.get("title"):
                    title = ru["title"].strip()
                else:
                    en = biblio.get("en", {})
                    if en.get("title"):
                        title = en["title"].strip()

            if title == "No title":
                snippet = item.get("snippet", {})
                title = snippet.get("title", "No title")

            title = title.strip()

            if not ParserAnalogLinkDataFetcher._validate_patent_fields(
                index, doc_number, office, pub_date
            ):
                return None

            patent_number = f"{office}{doc_number}{kind}_{pub_date}"
            url = ParserAnalogLinkDataFetcher.build_patent_url(docs_url, patent_number)

            details = {
                "url": url,
                "title": title,
                "publication_date": pub_date,
                "office": office,
                "doc_number": doc_number,
                "kind": kind,
            }

            logger.debug(
                f"Parsed patent {patent_number} at index {index} with title '{title[:50]}...'"
            )
            return {"patent_number": patent_number, "details": details}

        except KeyError as e:
            logger.error(f"Missing expected key in patent at index {index}: {e}")
        except AttributeError as e:
            logger.error(f"Attribute error while parsing patent at index {index}: {e}")
        except Exception as e:
            logger.error(f"Failed to parse patent at index {index}: {e}", exc_info=True)
        return None

    @staticmethod
    def _validate_patent_fields(
        index: int, doc_number: str | None, office: str | None, pub_date: str
    ) -> bool:
        """
        Validates that all required fields are present and non-empty.

        Args:
            index: Position in the list for logging context.
            doc_number: Document number extracted from the response.
            office: Publishing office code.
            pub_date: Publication date (after cleanup).

        Returns:
            True if all fields are valid, False otherwise.
        """
        if not all([doc_number, office, pub_date]):
            missing = []
            if not doc_number:
                missing.append("document_number")
            if not office:
                missing.append("publishing_office")
            if not pub_date:
                missing.append("publication_date")
            logger.warning(
                f"Skipping patent at index {index} due to missing fields: {', '.join(missing)}"
            )
            return False
        return True

    @staticmethod
    def build_patent_url(docs_url: str, patent_number: str) -> str:
        """
        Constructs the full URL for the patent document.

        Args:
            docs_url: Base URL of the Rospatent documents endpoint.
            patent_number: Full patent identifier (office+number+kind).

        Returns:
            Constructed URL string, or empty string if docs_url is empty.
        """
        if not docs_url:
            logger.debug("docs_url is empty, returning empty URL")
            return ""
        # Remove trailing slash if present and append patent info
        base = docs_url.rstrip("/")
        url = f"{base}/{patent_number}"
        logger.debug(f"Built URL: {url}")
        return url
