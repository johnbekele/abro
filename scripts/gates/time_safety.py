"""time-safety — the backend stores UTC and knows nothing about the Ethiopian calendar.

Two rules.

``datetime.now()`` is machine-local and ``datetime.utcnow()`` returns a naive value that
lies about being UTC. Both produce timestamps that compare wrongly against stored data,
and the failure is silent until someone deploys to a host in another zone.

Ethiopian calendar and 6-hour-clock conversion lives only in ``packages/@abro/time``.
Ethiopians count hours from dawn, so 09:00 EAT is spoken as "3:00 in the morning".
Duplicating that conversion across a server and two clients guarantees they eventually
disagree, and the symptom is a passenger left at a terminal. See ADR 0007.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from _common import PY, TS, Finding, iter_files, read, report, suppressions

GATE = "time-safety"
SUBTREES = ("abro-api", "abro-web", "abro-mobile", "packages")
TIME_PACKAGE = "packages/@abro/time"
HINT = (
    "Use datetime.now(timezone.utc) in the backend. "
    f"Ethiopian calendar and clock conversion belongs in {TIME_PACKAGE}."
)

_DATETIME_RECEIVERS = frozenset({"datetime", "dt", "date", "_datetime"})

ETHIOPIAN_RE = re.compile(
    r"pagum[e\u0113]"
    r"|ethiopic"
    r"|ethiopian[_\s-]?(?:calendar|date|time|clock|hour|year|month)"
    r"|ge[\u2019']?ez[_\s-]?numeral"
    r"|\bkenat\b"
    r"|(?:to|from)[_]?ethiopian"
    r"|dawn[_\s-]?offset"
    r"|six[_\s-]?hour[_\s-]?clock",
    re.IGNORECASE,
)


def _receiver(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _check_call(path: Path, node: ast.Call) -> list[Finding]:
    func = node.func
    if not isinstance(func, ast.Attribute):
        return []

    receiver = _receiver(func.value)
    keywords = {kw.arg for kw in node.keywords}

    if func.attr == "utcnow":
        return [Finding(path, node.lineno, "datetime.utcnow() returns a naive value")]

    if (
        func.attr == "now"
        and receiver in _DATETIME_RECEIVERS
        and not node.args
        and "tz" not in keywords
    ):
        return [Finding(path, node.lineno, "datetime.now() is machine-local; pass a timezone")]

    if func.attr == "today" and receiver in _DATETIME_RECEIVERS:
        return [Finding(path, node.lineno, f"{receiver}.today() is machine-local")]

    if func.attr == "fromtimestamp" and len(node.args) < 2 and "tz" not in keywords:
        return [Finding(path, node.lineno, "fromtimestamp() without tz returns a naive value")]

    if func.attr == "replace":
        strips_tz = any(
            kw.arg == "tzinfo" and isinstance(kw.value, ast.Constant) and kw.value.value is None
            for kw in node.keywords
        )
        if strips_tz:
            return [Finding(path, node.lineno, "replace(tzinfo=None) discards timezone awareness")]

    return []


def _check_python(path: Path, text: str) -> list[Finding]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [Finding(path, exc.lineno or 1, f"could not parse: {exc.msg}")]

    findings: list[Finding] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            findings.extend(_check_call(path, node))
    return findings


def _check_ethiopian(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = ETHIOPIAN_RE.search(line)
        if match is not None:
            findings.append(
                Finding(
                    path,
                    lineno,
                    f"Ethiopian calendar/clock logic ('{match.group(0)}') outside {TIME_PACKAGE}",
                )
            )
    return findings


def run(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    time_package = (root / TIME_PACKAGE).resolve()

    for path in iter_files(root, SUBTREES, PY + TS):
        text = read(path)
        allowed, exemption_findings = suppressions(path, text, GATE)
        findings.extend(exemption_findings)

        raw: list[Finding] = []
        if path.suffix == ".py":
            raw.extend(_check_python(path, text))
        if not path.resolve().is_relative_to(time_package):
            raw.extend(_check_ethiopian(path, text))

        findings.extend(f for f in raw if f.line not in allowed)

    return findings


def main() -> int:
    from _common import REPO_ROOT

    return report(GATE, run(REPO_ROOT), root=REPO_ROOT, hint=HINT)


if __name__ == "__main__":
    raise SystemExit(main())
