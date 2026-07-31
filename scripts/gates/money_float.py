"""money-float — every monetary amount is an integer count of santim.

Binary floating point cannot represent 0.1. A marketplace that mis-rounds a fee a hundred
thousand times has lost real money and can no longer reconcile its ledger.

Python is checked with the ``ast`` module: ``float`` annotations and ``float()`` calls on
money, and inline arithmetic that produces fractional santim.

TypeScript has no integer type, so every ``number`` is already a double and the type
annotation carries no information. The gate therefore targets the *operations* that
introduce a fraction — division, multiplication by a non-integer, ``parseFloat`` and
``toFixed`` — rather than the declaration. Splitting or scaling an amount goes through
the money helpers, which guarantee the parts sum back to the whole.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from _common import PY, TS, Finding, iter_files, read, report, suppressions

GATE = "money-float"
SUBTREES = ("abro-api", "abro-web", "abro-mobile", "packages")
HINT = "Amounts are integer santim. Use the money helpers for any proportion or split."

MONEY_WORDS = frozenset(
    {
        "amount",
        "amounts",
        "balance",
        "cap",
        "commission",
        "contribution",
        "cost",
        "deposit",
        "fare",
        "fee",
        "fees",
        "payout",
        "price",
        "refund",
        "santim",
        "subtotal",
        "total",
    }
)

_SEGMENT_RE = re.compile(r"[^A-Za-z0-9]+|(?<=[a-z0-9])(?=[A-Z])")
_COMMENT_RE = re.compile(r"^\s*(?://|/\*|\*)")
_SCALE_RE = re.compile(r"([A-Za-z_$][\w$]*)\s*\*\s*\d+\.\d+|(\d+\.\d+)\s*\*\s*([A-Za-z_$][\w$]*)")
_DIVIDE_RE = re.compile(r"([A-Za-z_$][\w$]*)\s*/\s*\d")
_TOFIXED_RE = re.compile(r"([A-Za-z_$][\w$]*)(?:\.[\w$]+)*\s*\.toFixed\s*\(")
_PARSEFLOAT_RE = re.compile(r"parseFloat\s*\(\s*([A-Za-z_$][\w$]*)")


def is_money(name: str | None) -> bool:
    if not name:
        return False
    return any(part.lower() in MONEY_WORDS for part in _SEGMENT_RE.split(name) if part)


def _target_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _mentions_float(annotation: ast.expr) -> bool:
    return any(isinstance(n, ast.Name) and n.id == "float" for n in ast.walk(annotation))


def _check_python(path: Path, text: str) -> list[Finding]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [Finding(path, exc.lineno or 1, f"could not parse: {exc.msg}")]

    findings: list[Finding] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and node.annotation is not None:
            name = _target_name(node.target)
            if is_money(name) and _mentions_float(node.annotation):
                findings.append(Finding(path, node.lineno, f"money field '{name}' typed float"))

        elif isinstance(node, ast.arg) and node.annotation is not None:
            if is_money(node.arg) and _mentions_float(node.annotation):
                findings.append(
                    Finding(path, node.lineno, f"money parameter '{node.arg}' typed float")
                )

        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "float" and node.args:
                name = _target_name(node.args[0])
                if is_money(name):
                    findings.append(Finding(path, node.lineno, f"float() applied to '{name}'"))

        elif isinstance(node, ast.BinOp):
            findings.extend(_check_python_binop(path, node))

    return findings


def _check_python_binop(path: Path, node: ast.BinOp) -> list[Finding]:
    operands = (node.left, node.right)
    money = next((_target_name(o) for o in operands if is_money(_target_name(o))), None)
    if money is None:
        return []

    if isinstance(node.op, ast.Div):
        return [Finding(path, node.lineno, f"'{money}' divided inline; use the money helpers")]

    if isinstance(node.op, ast.Mult):
        scaled_by_float = any(
            isinstance(o, ast.Constant) and isinstance(o.value, float) for o in operands
        )
        if scaled_by_float:
            return [
                Finding(path, node.lineno, f"'{money}' scaled by a float; use the money helpers")
            ]

    return []


def _check_typescript(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        if _COMMENT_RE.match(line):
            continue

        for match in _SCALE_RE.finditer(line):
            name = match.group(1) or match.group(3)
            if is_money(name):
                findings.append(
                    Finding(path, lineno, f"'{name}' scaled by a float; use the money helpers")
                )

        for match in _DIVIDE_RE.finditer(line):
            if is_money(match.group(1)):
                findings.append(
                    Finding(
                        path, lineno, f"'{match.group(1)}' divided inline; use the money helpers"
                    )
                )

        coercions = ((_TOFIXED_RE, "toFixed() on"), (_PARSEFLOAT_RE, "parseFloat() on"))
        for pattern, message in coercions:
            for match in pattern.finditer(line):
                if is_money(match.group(1)):
                    findings.append(Finding(path, lineno, f"{message} '{match.group(1)}'"))

    return findings


def run(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    for path in iter_files(root, SUBTREES, PY + TS):
        text = read(path)
        allowed, exemption_findings = suppressions(path, text, GATE)
        findings.extend(exemption_findings)

        raw = _check_python(path, text) if path.suffix == ".py" else _check_typescript(path, text)
        findings.extend(f for f in raw if f.line not in allowed)

    return findings


def main() -> int:
    from _common import REPO_ROOT

    return report(GATE, run(REPO_ROOT), root=REPO_ROOT, hint=HINT)


if __name__ == "__main__":
    raise SystemExit(main())
