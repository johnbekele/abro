"""Run every abro-specific gate and summarise.

    python scripts/gates/run_all.py

Exits non-zero if any gate found a violation, after running all of them — one failure
should not hide the next.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import amharic_search
import geo_safety
import i18n_parity
import money_float
import pii_logging
import time_safety
from _common import REPO_ROOT, report

GATES = (money_float, time_safety, i18n_parity, amharic_search, geo_safety, pii_logging)


def main() -> int:
    failed: list[str] = []

    for gate in GATES:
        status = report(gate.GATE, gate.run(REPO_ROOT), root=REPO_ROOT, hint=gate.HINT)
        if status != 0:
            failed.append(gate.GATE)

    if failed:
        print(f"\nfailed: {', '.join(failed)}")
        return 1

    print(f"\nall {len(GATES)} abro gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
