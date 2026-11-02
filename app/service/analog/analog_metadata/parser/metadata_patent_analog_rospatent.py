import asyncio

import aiohttp

from app.service.analog.analog_metadata.parser.data_fetcher import (
    ParserAnalogMetadataDataFetcher,
)
from app.service.parser import Parser
from core import logger
from core.domain.analog import Analog
from core.dto.patent_info import PatentDocument
from core.exceptions import NetworkError, ParserError
from core.settings import RospatentSettings

logger = logger.get_logger(__name__)


class RospatentMetadataParser(Parser):
    def __init__(
        self,
        config: RospatentSettings,
        data_fetcher: ParserAnalogMetadataDataFetcher,
    ):
        self._data_fetcher = data_fetcher
        super().__init__(config)

    async def parse_for_analog(self, analog: Analog) -> PatentDocument:
        patent_doc = await self._fetch_and_parse(analog.analog_num, analog.analog_link)
        return patent_doc

    async def parse_for_analogs(self, patent_links: dict[str, str]) -> dict[str, PatentDocument]:
        logger.info(f"Starting metadata parsing for {len(patent_links)} patents")

        await self.disable_auto_close()

        try:
            async with self._ensure_session() as session:
                semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)

                async def fetch_one(number: str, link: str) -> PatentDocument | None:
                    """Fetch and parse a single patent using shared session."""
                    async with semaphore:
                        return await self._fetch_with_session(number, link, session)

                tasks = [fetch_one(num, link) for num, link in patent_links.items()]
                results = await asyncio.gather(*tasks, return_exceptions=True)

            patents: dict[str, PatentDocument] = {}
            for (number, _), result in zip(patent_links.items(), results, strict=True):
                if isinstance(result, PatentDocument):
                    patents[number] = result
                elif isinstance(result, Exception):
                    logger.error(f"Task error for patent {number}: {result}")
                else:
                    logger.error(f"No data for patent {number}: {result}")

            success_count = len(patents)
            logger.info(
                f"Metadata parsing completed: {success_count}/{len(patent_links)} successful"
            )
            return patents

        finally:
            await self.enable_auto_close()

    def get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.key.get_secret_value()}",
            "Content-Type": "application/json",
            "User-Agent": f"{self.config.user_agent}",
        }

    async def _fetch_and_parse(self, number: str, link: str) -> PatentDocument | None:
        """
        Fetch and parse for a single patent (auto_close enabled by default).
        Used by parse_for_analog.
        """
        async with self._ensure_session() as session:
            return await self._fetch_with_session(number, link, session)

    async def _fetch_with_session(
        self, number: str, link: str, session: aiohttp.ClientSession
    ) -> PatentDocument | None:
        """
        Fetch metadata using an existing session.
        Used by both single and batch parsing methods.
        """
        try:
            logger.debug(f"Fetching metadata for patent {number}")
            logger.info(f"Fetching metadata {link}")

            response = await self.request_with_retries(
                method="GET",
                url=link,
                session=session,
                headers=self.get_headers(),
                retries=getattr(self.config, "metadata_retries", 3),
                timeout=getattr(self.config, "metadata_timeout", 30),
                base_delay=getattr(self.config, "metadata_base_delay", 2),
            )
            if not response:
                return None
            return self._parse_patent_data(number, response)

        except (NetworkError, ParserError) as e:
            logger.warning(f"Parser error for patent {number}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error for patent {number}: {e}")
            return None

    def _parse_patent_data(self, number: str, response: dict) -> PatentDocument | None:
        """Parse raw API response into PatentDocument and validate content."""
        patent_data = self._data_fetcher.fetch(
            number=number, data=response, required_fields=self.config.required_fields
        )
        patent_doc = PatentDocument(
            abstract=patent_data.get("abstract", ""),
            claims=patent_data.get("claims", ""),
            description=patent_data.get("description", ""),
        )
        if patent_doc and any([patent_doc.abstract, patent_doc.claims, patent_doc.description]):
            logger.debug(f"Successfully parsed patent {number}")
            return patent_doc
        else:
            logger.warning(f"No content extracted for patent {number}")
            return None
