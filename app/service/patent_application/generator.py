import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from app.service.llm_client.llm_client import LLMClient
from core import logger
from core.settings import get_settings

if TYPE_CHECKING:
    from app.http.response_models.drawing import (
        DrawingElementResponse,
        DrawingFigureResponse,
    )
    from core.domain.patent import Patent

logger = logger.get_logger(__name__)


@dataclass
class ParsedFigure:
    """A single figure parsed from the figures-distribution prompt output."""

    number: int
    title: str
    element_numbers: list[int] = field(default_factory=list)


@lru_cache
def _load_prompt(filename: str) -> str:
    path = Path(get_settings().storage.storage_dir) / "prompts" / "patent_application" / filename
    return path.read_text(encoding="utf-8")


class PatentApplicationGenerator:
    def __init__(self, llm_client: LLMClient):
        self._llm = llm_client

    async def generate_elements_list(self, patent: "Patent") -> list[str]:
        """Ask the model to build a numbered list of invention parts.

        Returns the parts as plain descriptions (without the leading numbers),
        ready to be stored as drawing elements numbered 1..N.
        """
        prompt = _load_prompt("elements_list.txt").format(**self._patent_vars(patent))
        raw = await self._llm.ask(prompt)
        return self._parse_elements_list(raw)

    async def generate_figures(
        self,
        patent: "Patent",
        elements: list["DrawingElementResponse"],
    ) -> list[ParsedFigure]:
        """Ask the model to distribute the given elements across figures."""
        variables = self._patent_vars(patent)
        variables["parts"] = self._format_parts(elements)
        prompt = _load_prompt("figures_distribution.txt").format(**variables)
        raw = await self._llm.ask(prompt)
        return self._parse_figures(raw)

    async def generate_abstract(self, patent: "Patent") -> str:
        prompt = _load_prompt("abstract.txt").format(**self._patent_vars(patent))
        result = await self._llm.ask(prompt)
        return result.strip()

    async def generate_claims(
        self,
        patent: "Patent",
        elements: list["DrawingElementResponse"],
    ) -> list[str]:
        variables = self._patent_vars(patent)
        variables["parts"] = self._format_parts(elements)
        prompt = _load_prompt("claims.txt").format(**variables)
        raw = await self._llm.ask(prompt)
        return self._parse_claims(raw)

    async def generate_description(
        self,
        patent: "Patent",
        elements: list["DrawingElementResponse"],
        figures: list["DrawingFigureResponse"],
        analog_data: str,
        analog_id_rospatent: str,
    ) -> str:
        variables = self._patent_vars(patent)
        variables["parts"] = self._format_parts(elements)
        variables["figures"] = self._format_figures(figures)
        variables["analog_data"] = analog_data or "Сведения о прототипе отсутствуют."
        variables["analog_id_rospatent"] = analog_id_rospatent or "не указан"
        prompt = _load_prompt("description.txt").format(**variables)
        result = await self._llm.ask(prompt)
        return result.strip()

    @staticmethod
    def _patent_vars(patent: "Patent") -> dict[str, str]:
        return {
            "appointment": patent.appointment,
            "technical_area": patent.technical_area,
            "technical_result": patent.technical_result,
            "construction": patent.construction,
            "operation_principle": patent.operation_principle,
        }

    @staticmethod
    def _format_parts(elements: list["DrawingElementResponse"]) -> str:
        if not elements:
            return "Список составных частей не задан."
        ordered = sorted(elements, key=lambda el: el.number)
        return "\n".join(f"{el.number}. {el.description}" for el in ordered)

    @staticmethod
    def _format_figures(figures: list["DrawingFigureResponse"]) -> str:
        if not figures:
            return "Чертежи отсутствуют."
        lines: list[str] = [f"Число фигур: {len(figures)}", ""]
        for fig in sorted(figures, key=lambda f: f.number):
            element_nums = ", ".join(str(num) for num in sorted(el.number for el in fig.elements))
            lines.append(f"Фигура {fig.number}:")
            lines.append("*Описание*")
            lines.append(fig.title)
            lines.append("*Элементы на фиг*")
            lines.append(element_nums)
            lines.append("")
        return "\n".join(lines).strip()

    @staticmethod
    def _parse_elements_list(raw: str) -> list[str]:
        """Extract descriptions from a numbered list emitted by the model."""
        items: list[str] = []
        for line in raw.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            match = re.match(r"^\d+\s*[.)]\s*(.+)$", line)
            if match:
                items.append(match.group(1).strip())
        return items

    @staticmethod
    def _parse_figures(raw: str) -> list[ParsedFigure]:
        """Parse the rigid figures-distribution format into structured figures."""
        figures: list[ParsedFigure] = []
        current: ParsedFigure | None = None
        mode: str | None = None  # "desc" while reading title, "elems" for numbers

        for line in raw.strip().split("\n"):
            text = line.strip()
            if not text:
                continue

            header = re.match(r"^Фигура\s+(\d+)\s*:?\s*$", text)
            if header:
                if current is not None:
                    figures.append(current)
                current = ParsedFigure(number=int(header.group(1)), title="")
                mode = None
                continue

            if current is None:
                continue

            if text.startswith("*Описание*"):
                mode = "desc"
                continue
            if text.startswith("*Элементы"):
                mode = "elems"
                continue

            if mode == "desc":
                current.title = f"{current.title} {text}".strip() if current.title else text
            elif mode == "elems":
                current.element_numbers.extend(int(num) for num in re.findall(r"\d+", text))

        if current is not None:
            figures.append(current)
        return figures

    @staticmethod
    def _parse_claims(raw: str) -> list[str]:
        lines = raw.strip().split("\n")
        claims: list[str] = []
        current = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if re.match(r"^\d+\.", line):
                if current:
                    claims.append(current)
                current = line
            elif current:
                current += " " + line
        if current:
            claims.append(current)
        return claims if claims else [raw.strip()]
