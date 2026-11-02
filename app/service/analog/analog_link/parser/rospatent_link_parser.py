from typing import Any

from app.service.analog.analog_link.parser.data_fetcher import (
    ParserAnalogLinkDataFetcher,
)
from app.service.parser import Parser
from core import logger
from core.dto.patent_info import PatentSearchResult
from core.exceptions import ParserError
from core.settings import RospatentSettings

logger = logger.get_logger(__name__)


class RospatentLinkParser(Parser):
    def __init__(
        self, config: RospatentSettings, data_fetcher: ParserAnalogLinkDataFetcher
    ) -> None:
        self._data_fetcher = data_fetcher
        super().__init__(config)

    def get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.key.get_secret_value()}",
            "Content-Type": "application/json",
            "User-Agent": self.config.user_agent,
        }

    async def parse_by_search_query(self, search_query: str) -> list[PatentSearchResult]:
        # Build payload depending on the type
        payload = self._build_payload(search_query)
        # Send request and get response
        response = await self._send_api_request_by_search_query(payload)
        # Process response
        return self._process_response(response, search_query)

    async def parse_by_number(self, number: str) -> list[PatentSearchResult]:
        search_url = self._data_fetcher.build_patent_url(
            docs_url=self.config.docs_url, patent_number=number
        )
        # Send request and get response
        response = await self._send_api_request_by_number(search_url)
        logger.debug(f"Response from RosPatent for number {number}: {response}")
        # Process response
        return self._process_response(response, number)

    @staticmethod
    def _validate_response(response: Any) -> None:
        if not isinstance(response, dict):
            logger.error("Response is not a dictionary")
            raise ParserError("Invalid API response: not a dictionary")

        # If this is the direct response of the patent document
        if "common" in response or "id" in response:
            logger.info("Response is a single patent document (no 'hits')")
            return

        if "hits" not in response:
            logger.error("Missing 'hits' key in response")
            raise ParserError("Invalid API response: missing 'hits'")
        if not isinstance(response["hits"], list):
            logger.error("'hits' is not a list")
            raise ParserError("Invalid API response: 'hits' is not a list")
        logger.info("Response validation passed")

    def _build_payload(self, query: str) -> dict:
        """Search request body for the Rospatent search API."""
        return {
            self.config.request_language: query,
            "limit": self.config.request_limit,
            "sort": self.config.request_sort,
            "group_by": self.config.request_group_by,
            "filter": {"country": self.config.request_countries},
        }

    async def _send_api_request_by_search_query(self, payload: dict) -> dict:
        """Common method for sending POST requests."""
        async with self._ensure_session() as session:
            response = await self.request_with_retries(
                method="POST",
                url=self.config.api_url,
                session=session,
                headers=self.get_headers(),
                payload=payload,
                retries=getattr(self.config, "request_retries", 3),
                timeout=getattr(self.config, "request_timeout", 60),
            )
        return response

    async def _send_api_request_by_number(self, api_url: str) -> dict:
        """Common method for sending POST requests."""
        async with self._ensure_session() as session:
            response = await self.request_with_retries(
                method="GET",
                url=api_url,
                session=session,
                headers=self.get_headers(),
                retries=getattr(self.config, "request_retries", 3),
                timeout=getattr(self.config, "request_timeout", 60),
            )
        return response

    def _process_response(self, response: dict, param_value: str) -> list[PatentSearchResult]:
        """Validates response, extracts data and maps to domain objects."""
        self._validate_response(response)

        if "hits" in response:
            hits = response.get("hits", [])
        else:
            # The direct answer of the document is to wrap it as a single hit.
            hits = [response]

        patent_data = self._data_fetcher.fetch(self.config.docs_url, hits)
        logger.info(f"Successfully parsed {len(patent_data)} patents: '{param_value}'")

        return self._convert_to_patent_results(patent_data)

    @staticmethod
    def _convert_to_patent_results(
        patent_data: dict[str, dict[str, str]],
    ) -> list[PatentSearchResult]:
        """
        Args:
            patent_data: Mapping from patent number to extracted fields.

        Returns:
            List of domain objects (invalid entries are skipped).
        """
        patents = []
        for patent_number, data in patent_data.items():
            try:
                patent = PatentSearchResult(
                    patent_number=patent_number,
                    url=data.get("url", ""),
                    title=data.get("title"),
                    publication_date=data.get("publication_date"),
                    office=data.get("office"),
                    doc_number=data.get("doc_number"),
                    kind=data.get("kind"),
                )
                patents.append(patent)
            except Exception as e:
                logger.error(
                    f"Failed to create PatentSearchResult for {patent_number}: {e}",
                    exc_info=True,
                )
                continue
        logger.info(f"Mapped {len(patents)} PatentSearchResult objects")
        return patents
