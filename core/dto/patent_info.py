from dataclasses import dataclass


@dataclass
class PatentSearchResult:
    patent_number: str
    url: str
    title: str | None = None
    publication_date: str | None = None
    office: str | None = None
    doc_number: str | None = None
    kind: str | None = None


@dataclass
class PatentDocument:
    abstract: str | None = None
    description: str | None = None
    claims: str | None = None
