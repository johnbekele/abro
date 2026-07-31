"""amharic-search — gazetteer name queries go through ``am_normalize()``.

``ሀ/ሐ/ኀ``, ``ሰ/ሠ``, ``አ/ዐ`` and ``ጸ/ፀ`` are pronounced identically and Ethiopians spell
them interchangeably. A query that compares raw Amharic text silently returns nothing for
a large share of real users — and looks perfectly correct when a developer tests it with
their own spelling, which is why a static check has to carry it.

Two parts. A comparison against a gazetteer name column must mention ``am_normalize``
nearby, and where an ``am_normalize`` implementation exists it is run against a fixture
suite of homophone pairs that must all collapse to the same string.
"""

from __future__ import annotations

import importlib
import re
import sys
from collections.abc import Callable
from pathlib import Path

from _common import PY, SQL, Finding, iter_files, read, report, suppressions

GATE = "amharic-search"
SUBTREES = ("abro-api",)
BACKEND = "abro-api"
NEARBY_LINES = 5
HINT = "Compare am_normalize(query) against the normalised column, and index both spellings."

HOMOPHONES: tuple[tuple[str, str], ...] = (
    ("ሰላም", "ሠላም"),
    ("ሀዋሳ", "ሐዋሳ"),
    ("ሐዋሳ", "ኀዋሳ"),
    ("አዳማ", "ዐዳማ"),
    ("ጸሐይ", "ፀሐይ"),
    ("አዲስ አበባ", "ዐዲስ ዐበባ"),
)

_NAME_COLUMN_RE = re.compile(r"\b(?:name_am|name_latin|place_name|aliases?)\b", re.IGNORECASE)
_COMPARISON_RE = re.compile(r"ilike|\blike\b|==|similarity\s*\(|<->|@@|\bsimilar\s+to\b", re.I)
_DEFINITION_RE = re.compile(
    r"mapped_column|Column\(|create\s+table|add\s+column|create\s+index", re.IGNORECASE
)
_NORMALIZE_RE = re.compile(r"am_normalize", re.IGNORECASE)
_DEF_NORMALIZE_RE = re.compile(r"^def\s+am_normalize\b", re.MULTILINE)


def _check_queries(path: Path, text: str) -> list[Finding]:
    lines = text.splitlines()
    findings: list[Finding] = []

    for index, line in enumerate(lines):
        if not _NAME_COLUMN_RE.search(line) or not _COMPARISON_RE.search(line):
            continue
        if _DEFINITION_RE.search(line):
            continue

        window = lines[max(0, index - NEARBY_LINES) : index + NEARBY_LINES + 1]
        if any(_NORMALIZE_RE.search(nearby) for nearby in window):
            continue

        findings.append(Finding(path, index + 1, "gazetteer name compared without am_normalize()"))

    return findings


def _forget(dotted: str) -> None:
    """Drop a previous import of the backend package so a second call reloads from disk."""
    root_package = dotted.split(".")[0]
    for name in [n for n in sys.modules if n == root_package or n.startswith(f"{root_package}.")]:
        del sys.modules[name]


def _load_normalizer(root: Path, module_path: Path) -> tuple[Callable[[str], str] | None, str]:
    backend = str((root / BACKEND).resolve())
    dotted = ".".join(module_path.relative_to(root / BACKEND).with_suffix("").parts)

    inserted = backend not in sys.path
    if inserted:
        sys.path.insert(0, backend)
    try:
        _forget(dotted)
        importlib.invalidate_caches()
        module = importlib.import_module(dotted)
        return module.am_normalize, ""
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"
    finally:
        if inserted:
            sys.path.remove(backend)


def _check_fixtures(root: Path) -> list[Finding]:
    candidates = [
        path for path in iter_files(root, SUBTREES, PY) if _DEF_NORMALIZE_RE.search(read(path))
    ]
    if not candidates:
        return []

    module_path = candidates[0]
    normalize, error = _load_normalizer(root, module_path)
    if normalize is None:
        return [Finding(module_path, 1, f"could not load am_normalize ({error})")]

    return [
        Finding(module_path, 1, f"am_normalize does not unify {first!r} and {second!r}")
        for first, second in HOMOPHONES
        if normalize(first) != normalize(second)
    ]


def run(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    for path in iter_files(root, SUBTREES, PY + SQL):
        text = read(path)
        allowed, exemption_findings = suppressions(path, text, GATE)
        findings.extend(exemption_findings)
        findings.extend(f for f in _check_queries(path, text) if f.line not in allowed)

    findings.extend(_check_fixtures(root))
    return findings


def main() -> int:
    from _common import REPO_ROOT

    return report(GATE, run(REPO_ROOT), root=REPO_ROOT, hint=HINT)


if __name__ == "__main__":
    raise SystemExit(main())
