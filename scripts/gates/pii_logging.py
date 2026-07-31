"""pii-logging — no phone numbers, Fayda identifiers, OTP codes or payment references in logs.

Logs are retained longer, shipped to more third parties and read by more people than the
database is. The logging configuration redacts known keys and ``+251`` patterns as a
backstop; this gate exists so nobody has to rely on it.

Message text is deliberately not searched — ``logger.info("phone verified")`` is fine.
What is flagged is a PII-named value reaching the logger: an identifier, a structured
log key, or a literal Ethiopian number.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from _common import PY, TS, Finding, iter_files, read, report, suppressions

GATE = "pii-logging"
SUBTREES = ("abro-api", "abro-web", "abro-mobile", "packages")
HINT = "Log an opaque id instead. If you need the value for support, it belongs in the database."

LOG_LEVELS = frozenset(
    {"critical", "debug", "error", "exception", "fatal", "info", "log", "trace", "warn", "warning"}
)
LOG_RECEIVERS = frozenset({"logger", "log", "logging", "structlog", "console"})
SAFE_KEYWORDS = frozenset({"exc_info", "extra", "stack_info", "stacklevel"})

PII_RE = re.compile(
    r"phone|msisdn|otp|fayda|national_?id|id_?number|passport"
    r"|tx_?ref|payment_?ref(?:erence)?|card_?number|account_?number|cvv|iban",
    re.IGNORECASE,
)
ETHIOPIAN_NUMBER_RE = re.compile(r"\+251\d")
_STRING_RE = re.compile(r"'[^']*'|\"[^\"]*\"|`[^`]*`")
_TS_LOG_RE = re.compile(
    r"\b(?:console|logger|log)\s*\.\s*(?:" + "|".join(sorted(LOG_LEVELS)) + r")\s*\((?P<args>.*)$"
)


def _receiver(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_log_call(node: ast.Call) -> bool:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id == "print"
    if isinstance(func, ast.Attribute) and func.attr.lower() in LOG_LEVELS:
        receiver = _receiver(func.value)
        return receiver is not None and receiver.lower().lstrip("_") in LOG_RECEIVERS
    return False


def _inspect_argument(path: Path, node: ast.AST) -> list[Finding]:
    findings: list[Finding] = []

    for child in ast.walk(node):
        name: str | None = None
        if isinstance(child, ast.Name):
            name = child.id
        elif isinstance(child, ast.Attribute):
            name = child.attr
        elif isinstance(child, ast.Constant) and isinstance(child.value, str):
            if ETHIOPIAN_NUMBER_RE.search(child.value):
                findings.append(Finding(path, child.lineno, "Ethiopian phone number in a log call"))
            continue

        if name and PII_RE.search(name):
            lineno = getattr(child, "lineno", 1)
            findings.append(Finding(path, lineno, f"'{name}' passed to logger"))

    for child in ast.walk(node):
        if not isinstance(child, ast.Dict):
            continue
        for key in child.keys:
            is_literal_key = isinstance(key, ast.Constant) and isinstance(key.value, str)
            if is_literal_key and PII_RE.search(key.value):
                findings.append(Finding(path, key.lineno, f"log key '{key.value}' carries PII"))

    return findings


def _check_python(path: Path, text: str) -> list[Finding]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [Finding(path, exc.lineno or 1, f"could not parse: {exc.msg}")]

    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not _is_log_call(node):
            continue

        for argument in node.args:
            findings.extend(_inspect_argument(path, argument))

        for keyword in node.keywords:
            if keyword.arg and keyword.arg not in SAFE_KEYWORDS and PII_RE.search(keyword.arg):
                findings.append(Finding(path, node.lineno, f"log key '{keyword.arg}' carries PII"))
            findings.extend(_inspect_argument(path, keyword.value))

    return findings


def _check_typescript(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        match = _TS_LOG_RE.search(line)
        if match is None:
            continue

        arguments = match.group("args")
        if ETHIOPIAN_NUMBER_RE.search(arguments):
            findings.append(Finding(path, lineno, "Ethiopian phone number in a log call"))

        identifiers = _STRING_RE.sub("", arguments)
        hit = PII_RE.search(identifiers)
        if hit is not None:
            findings.append(Finding(path, lineno, f"'{hit.group(0)}' passed to logger"))

    return findings


def run(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    for path in iter_files(root, SUBTREES, PY + TS):
        text = read(path)
        allowed, exemption_findings = suppressions(path, text, GATE)
        findings.extend(exemption_findings)

        raw = _check_python(path, text) if path.suffix == ".py" else _check_typescript(path, text)
        seen: set[tuple[int, str]] = set()
        for finding in raw:
            key = (finding.line, finding.message)
            if finding.line in allowed or key in seen:
                continue
            seen.add(key)
            findings.append(finding)

    return findings


def main() -> int:
    from _common import REPO_ROOT

    return report(GATE, run(REPO_ROOT), root=REPO_ROOT, hint=HINT)


if __name__ == "__main__":
    raise SystemExit(main())
