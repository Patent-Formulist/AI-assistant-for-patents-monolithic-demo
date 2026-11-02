"""Parse a patent claims list into a dependency graph.

Each claim string looks like ``"2. Опреснитель по п.1, отличающийся тем, что ..."``.
The parser extracts, for every claim:

- its number;
- which claims it depends on (``depends_on``);
- whether it is independent (no references);
- the family it belongs to (the root independent claim reachable through its
  references) and a stable colour for that family.

Supported reference forms: ``по п.1``, ``по пп.1-3``, ``по п.1 или 2``,
``по пп.1 и 2``, ``по любому из пп.1-3``, ``по одному из пп.1, 3 и 5`` as well as
several such references inside one claim (e.g. a claim depending on п.2 and п.3).
"""

import re

from app.http.response_models.patent_application import (
    ClaimNode,
    ClaimsFamily,
    ClaimsGraphResponse,
)

# Colours assigned to families in order of their root independent claim.
# Red / green / blue first to match the canonical Rospatent examples.
_PALETTE = [
    "#E53935",  # red
    "#43A047",  # green
    "#1E88E5",  # blue
    "#FB8C00",  # orange
    "#8E24AA",  # purple
    "#00ACC1",  # cyan
    "#FDD835",  # yellow
    "#6D4C41",  # brown
]

# Leading "12. <text>".
_NUMBER_RE = re.compile(r"^\s*(\d+)\s*\.\s*(.*)$", re.DOTALL)

# A reference clause: "по [любому/одному из] п.<...>" up to the next comma.
_REF_RE = re.compile(
    r"по\s+(?:любому\s+из\s+|одному\s+из\s+)?пп?\.?\s*([^,]*)",
    re.IGNORECASE,
)

# A range like "1-3" / "1 – 3".
_RANGE_RE = re.compile(r"(\d+)\s*[-–—]\s*(\d+)")


def _parse_reference_numbers(fragment: str) -> set[int]:
    """Extract claim numbers from a reference fragment ("1-3", "1 или 2", ...)."""
    numbers: set[int] = set()
    for match in _RANGE_RE.finditer(fragment):
        start, end = int(match.group(1)), int(match.group(2))
        numbers.update(range(min(start, end), max(start, end) + 1))
    # Remaining standalone numbers, after stripping the ranges we already used.
    without_ranges = _RANGE_RE.sub(" ", fragment)
    for match in re.finditer(r"\d+", without_ranges):
        numbers.add(int(match.group()))
    return numbers


def _parse_claim(raw: str, fallback_number: int) -> tuple[int, str, list[int]]:
    matched = _NUMBER_RE.match(raw)
    if matched:
        number = int(matched.group(1))
        body = matched.group(2).strip()
    else:
        number = fallback_number
        body = raw.strip()

    parents: set[int] = set()
    for ref in _REF_RE.finditer(body):
        parents.update(_parse_reference_numbers(ref.group(1)))
    parents.discard(number)  # a claim never depends on itself
    return number, body, sorted(parents)


def _resolve_root(
    number: int,
    parents_by_number: dict[int, list[int]],
    independents: set[int],
    cache: dict[int, int],
    visiting: set[int],
) -> int:
    """Find the root independent claim a claim ultimately depends on."""
    if number in independents:
        return number
    if number in cache:
        return cache[number]

    parents = parents_by_number.get(number, [])
    roots: list[int] = []
    for parent in parents:
        if parent in visiting or parent not in parents_by_number:
            continue
        visiting.add(parent)
        roots.append(_resolve_root(parent, parents_by_number, independents, cache, visiting))
        visiting.discard(parent)

    # No resolvable independent ancestor (dangling/cyclic reference): treat the
    # claim as its own root so it still gets a family and a colour.
    root = min(roots) if roots else number
    cache[number] = root
    return root


def build_claims_graph(claims: list[str]) -> ClaimsGraphResponse:
    parsed = [_parse_claim(raw, fallback_number=index + 1) for index, raw in enumerate(claims)]

    parents_by_number = {number: parents for number, _, parents in parsed}
    independents = {number for number, _, parents in parsed if not parents}

    cache: dict[int, int] = {}
    root_by_number = {
        number: _resolve_root(number, parents_by_number, independents, cache, {number})
        for number, _, _ in parsed
    }

    # Assign a colour to each family in ascending order of its root claim.
    family_roots = sorted(set(root_by_number.values()))
    color_by_root = {
        root: _PALETTE[index % len(_PALETTE)] for index, root in enumerate(family_roots)
    }

    nodes = [
        ClaimNode(
            number=number,
            text=body,
            is_independent=not parents,
            depends_on=parents,
            family=root_by_number[number],
            color=color_by_root[root_by_number[number]],
        )
        for number, body, parents in parsed
    ]

    families = [
        ClaimsFamily(
            root=root,
            color=color_by_root[root],
            members=sorted(number for number, value in root_by_number.items() if value == root),
        )
        for root in family_roots
    ]

    return ClaimsGraphResponse(claims=nodes, families=families)
