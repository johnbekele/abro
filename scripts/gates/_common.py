"""Shared plumbing for the six abro-specific CI gates.

Each gate is a module exposing ``GATE``, ``run(root) -> list[Finding]`` and ``main()``.
``run`` taking an explicit root is what lets the gates be tested against fixture trees
instead of against the repository they live in.

Every gate must exit 0 when the tree it inspects is absent. These run on each pull
request from the first one, and the repository is pre-code.

A line may be exempted with ``abro-gate: allow <gate-name> <reason>`` in a comment. The
reason is mandatory: an exemption nobody has to justify is a deleted gate with extra
steps.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SKIP_DIRS = frozenset(
    {
        ".git",
        ".next",
        ".expo",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "coverage",
        "dist",
        "node_modules",
        "venv",
    }
)

PY = (".py",)
TS = (".ts", ".tsx")
SQL = (".sql",)

_ALLOW_RE = re.compile(r"abro-gate:\s*allow\s+(?P<gate>[a-z0-9-]+)(?P<reason>.*)$")


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    message: str


def iter_files(root: Path, subtrees: Sequence[str], suffixes: Sequence[str]) -> Iterator[Path]:
    """Yield files under the given subtrees. Absent subtrees yield nothing."""
    for subtree in subtrees:
        base = root / subtree
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.suffix not in suffixes or not path.is_file():
                continue
            if SKIP_DIRS.intersection(path.parts):
                continue
            yield path


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def suppressions(path: Path, text: str, gate: str) -> tuple[frozenset[int], list[Finding]]:
    """Line numbers exempted from ``gate``, plus findings for exemptions with no reason."""
    allowed: set[int] = set()
    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = _ALLOW_RE.search(line)
        if match is None or match.group("gate") != gate:
            continue
        if match.group("reason").strip(" -–—:#/*"):
            allowed.add(lineno)
        else:
            findings.append(
                Finding(path, lineno, f"{gate} exemption needs a reason on the same line")
            )
    return frozenset(allowed), findings


def report(
    gate: str, findings: Sequence[Finding], *, root: Path = REPO_ROOT, hint: str = ""
) -> int:
    if not findings:
        print(f"{gate}: ok")
        return 0

    for finding in sorted(findings, key=lambda f: (str(f.path), f.line)):
        try:
            location = finding.path.relative_to(root)
        except ValueError:
            location = finding.path
        print(f"{location}:{finding.line}: {finding.message}")

    print(f"\n{gate}: {len(findings)} violation(s)")
    if hint:
        print(hint)
    return 1
