"""geo-safety — corridor queries must be indexed and directional.

``ST_DWithin`` against a route needs its ``_ST_Expand(...) &&`` companion predicate or the
GiST index goes unused and the query degrades to a sequential scan over every trip.
BlaBlaCar measured the pairing at 34x.

Corridor matching needs the ``f_dropoff > f_pickup`` direction check. Without it a
passenger travelling Adama to Addis matches a driver heading the other way, and the bug
looks like a ranking problem rather than a correctness one. See ADR 0004.

Both checks read a window of lines around each hit rather than parsing SQL, because the
predicates are routinely split across lines by a query builder or a formatter.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from pathlib import Path

from _common import PY, SQL, Finding, iter_files, read, report, suppressions

GATE = "geo-safety"
SUBTREES = ("abro-api",)
WINDOW = 12
HINT = "Pair ST_DWithin with _ST_Expand(...) && , and keep the f_dropoff > f_pickup check."

_DWITHIN_RE = re.compile(r"st_dwithin", re.IGNORECASE)
_EXPAND_RE = re.compile(r"_st_expand", re.IGNORECASE)
_OVERLAP_RE = re.compile(r"&&")
_FRACTION_RE = re.compile(r"\b(?:f_pickup|f_dropoff|pickup_fraction|dropoff_fraction)\b", re.I)
_PICKUP_RE = re.compile(r"\b(?:f_pickup|pickup_fraction)\b", re.IGNORECASE)
_DROPOFF_RE = re.compile(r"\b(?:f_dropoff|dropoff_fraction)\b", re.IGNORECASE)
_DIRECTION_RE = re.compile(
    r"(?:f_dropoff|dropoff_fraction)\s*>\s*(?:[\w.]*\.)?(?:f_pickup|pickup_fraction)"
    r"|(?:f_pickup|pickup_fraction)\s*<\s*(?:[\w.]*\.)?(?:f_dropoff|dropoff_fraction)",
    re.IGNORECASE,
)


def _blocks(lines: Sequence[str], pattern: re.Pattern[str]) -> Iterator[tuple[int, str]]:
    """Yield (first hit index, surrounding text) for each cluster of matching lines."""
    hits = [index for index, line in enumerate(lines) if pattern.search(line)]
    if not hits:
        return

    start = previous = hits[0]
    for index in hits[1:]:
        if index - previous > WINDOW:
            yield start, "\n".join(lines[max(0, start - WINDOW) : previous + WINDOW + 1])
            start = index
        previous = index

    yield start, "\n".join(lines[max(0, start - WINDOW) : previous + WINDOW + 1])


def _check(path: Path, text: str) -> list[Finding]:
    lines = text.splitlines()
    findings: list[Finding] = []

    for index, window in _blocks(lines, _DWITHIN_RE):
        if not (_EXPAND_RE.search(window) and _OVERLAP_RE.search(window)):
            findings.append(
                Finding(path, index + 1, "ST_DWithin without its _ST_Expand(...) && companion")
            )

    for index, window in _blocks(lines, _FRACTION_RE):
        both_present = _PICKUP_RE.search(window) and _DROPOFF_RE.search(window)
        if both_present and not _DIRECTION_RE.search(window):
            findings.append(
                Finding(path, index + 1, "corridor match without the f_dropoff > f_pickup check")
            )

    return findings


def run(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    for path in iter_files(root, SUBTREES, PY + SQL):
        text = read(path)
        allowed, exemption_findings = suppressions(path, text, GATE)
        findings.extend(exemption_findings)
        findings.extend(f for f in _check(path, text) if f.line not in allowed)

    return findings


def main() -> int:
    from _common import REPO_ROOT

    return report(GATE, run(REPO_ROOT), root=REPO_ROOT, hint=HINT)


if __name__ == "__main__":
    raise SystemExit(main())
