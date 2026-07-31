"""i18n-parity — the ``en`` and ``am`` catalogs must carry identical key sets.

A missing Amharic key renders as a raw key name to the majority of users, and nothing in
a normal test suite notices. A catalog with no Amharic counterpart at all is the same
failure one step earlier.

Two catalog shapes are recognised: sibling files (``…/en.json`` beside ``…/am.json``) and
sibling directories (``…/en/common.json`` beside ``…/am/common.json``).

The other half of the rule — no hardcoded user-facing strings in components — is enforced
by ``eslint-plugin-i18next`` in the client lint configuration rather than here, because
distinguishing a user-facing literal from a test id needs the parser's scope information.
"""

from __future__ import annotations

import json
from pathlib import Path

from _common import Finding, iter_files, read, report

GATE = "i18n-parity"
SUBTREES = ("packages", "abro-web", "abro-mobile")
LOCALES = ("en", "am")
HINT = "Every user-facing string exists in both en and am. Ge'ez numerals are for dates, not money."

CatalogKey = tuple[Path, str]


def _flatten(value: object, prefix: str = "") -> set[str]:
    if not isinstance(value, dict):
        return {prefix}

    keys: set[str] = set()
    for key, child in value.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        keys |= _flatten(child, path)
    return keys


def _classify(path: Path) -> tuple[CatalogKey, str] | None:
    if path.stem in LOCALES:
        return (path.parent, ""), path.stem
    if path.parent.name in LOCALES:
        return (path.parent.parent, path.name), path.parent.name
    return None


def _collect(root: Path) -> dict[CatalogKey, dict[str, Path]]:
    catalogs: dict[CatalogKey, dict[str, Path]] = {}
    for path in iter_files(root, SUBTREES, (".json",)):
        classified = _classify(path)
        if classified is None:
            continue
        key, locale = classified
        catalogs.setdefault(key, {})[locale] = path
    return catalogs


def _keys(path: Path) -> tuple[set[str], Finding | None]:
    try:
        return _flatten(json.loads(read(path))), None
    except json.JSONDecodeError as exc:
        return set(), Finding(path, exc.lineno, f"invalid JSON: {exc.msg}")


def run(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    for _key, by_locale in sorted(_collect(root).items(), key=lambda item: str(item[0])):
        present = set(by_locale)
        if len(present) == 1:
            (locale,) = present
            missing = next(other for other in LOCALES if other != locale)
            findings.append(
                Finding(by_locale[locale], 1, f"no matching '{missing}' catalog beside this one")
            )
            continue

        en_keys, en_error = _keys(by_locale["en"])
        am_keys, am_error = _keys(by_locale["am"])
        findings.extend(error for error in (en_error, am_error) if error is not None)
        if en_error is not None or am_error is not None:
            continue

        for path, missing in (
            (by_locale["am"], en_keys - am_keys),
            (by_locale["en"], am_keys - en_keys),
        ):
            for name in sorted(missing):
                findings.append(Finding(path, 1, f"missing key '{name}'"))

    return findings


def main() -> int:
    from _common import REPO_ROOT

    return report(GATE, run(REPO_ROOT), root=REPO_ROOT, hint=HINT)


if __name__ == "__main__":
    raise SystemExit(main())
