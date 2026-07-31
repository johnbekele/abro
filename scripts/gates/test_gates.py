"""Fixture tests for the six abro-specific gates.

A gate that never fires is worse than no gate: it reports success and nobody looks again.
These cannot be validated against real source because the repository has no application
code yet, so each gate is exercised against an inline fixture tree that proves it both
catches its violation and stays quiet on the correct form.

    python -m pytest scripts/gates/test_gates.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import amharic_search
import geo_safety
import i18n_parity
import money_float
import pii_logging
import time_safety

ALL_GATES = (money_float, time_safety, i18n_parity, amharic_search, geo_safety, pii_logging)


def write(root: Path, relative: str, content: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip("\n"), encoding="utf-8")
    return path


def messages(findings: list) -> str:
    return " | ".join(f"{f.line}: {f.message}" for f in findings)


@pytest.mark.parametrize("gate", ALL_GATES, ids=lambda g: g.GATE)
def test_passes_on_an_empty_tree(gate, tmp_path: Path) -> None:
    """The repository is pre-code. Every gate has to be green before its target exists."""
    assert gate.run(tmp_path) == []


# --- money-float -----------------------------------------------------------------


def test_money_float_catches_float_annotation(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/schemas/booking.py",
        """
        class Booking:
            service_fee: float = 0.0
        """,
    )
    assert "typed float" in messages(money_float.run(tmp_path))


def test_money_float_catches_inline_division(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/services/pricing.py",
        """
        def to_birr(contribution_santim):
            return contribution_santim / 100
        """,
    )
    assert "divided inline" in messages(money_float.run(tmp_path))


def test_money_float_accepts_integer_santim(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/services/pricing.py",
        """
        from app.core.money import allocate

        def split(total_santim: int, shares: list[int]) -> list[int]:
            return allocate(total_santim, shares)
        """,
    )
    assert money_float.run(tmp_path) == []


def test_money_float_catches_typescript_fraction(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-web/src/lib/checkout.ts",
        """
        const withFee = contributionSantim * 1.15;
        const display = totalSantim.toFixed(2);
        """,
    )
    findings = money_float.run(tmp_path)
    assert len(findings) == 2, messages(findings)


def test_money_float_accepts_typescript_helpers(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-web/src/lib/checkout.ts",
        """
        import { formatSantim, applyRate } from '@abro/money';

        const withFee = applyRate(contributionSantim, SERVICE_FEE_RATE);
        const display = formatSantim(withFee);
        """,
    )
    assert money_float.run(tmp_path) == []


def test_exemption_requires_a_reason(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/legacy.py",
        """
        legacy_fee: float = 0.0  # abro-gate: allow money-float
        """,
    )
    assert "needs a reason" in messages(money_float.run(tmp_path))


def test_exemption_with_a_reason_is_honoured(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/legacy.py",
        """
        legacy_fee: float = 0.0  # abro-gate: allow money-float - mirrors the provider payload
        """,
    )
    assert money_float.run(tmp_path) == []


# --- time-safety -----------------------------------------------------------------


@pytest.mark.parametrize(
    "call",
    ["datetime.now()", "datetime.utcnow()", "date.today()", "datetime.fromtimestamp(raw)"],
)
def test_time_safety_catches_naive_clock_reads(tmp_path: Path, call: str) -> None:
    write(tmp_path, "abro-api/app/services/trip.py", f"stamp = {call}\n")
    assert time_safety.run(tmp_path) != []


def test_time_safety_accepts_aware_utc(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/services/trip.py",
        """
        from datetime import datetime, timezone

        departs_at = datetime.now(timezone.utc)
        """,
    )
    assert time_safety.run(tmp_path) == []


def test_time_safety_confines_ethiopian_conversion(tmp_path: Path) -> None:
    write(tmp_path, "abro-web/src/lib/format.ts", "export const toEthiopian = (d: Date) => d;\n")
    assert "outside packages/@abro/time" in messages(time_safety.run(tmp_path))


def test_time_safety_allows_ethiopian_conversion_in_its_package(tmp_path: Path) -> None:
    write(
        tmp_path,
        "packages/@abro/time/src/calendar.ts",
        "export const toEthiopian = (d: Date) => d;\n",
    )
    assert time_safety.run(tmp_path) == []


# --- i18n-parity -----------------------------------------------------------------


def test_i18n_parity_catches_a_missing_amharic_key(tmp_path: Path) -> None:
    write(tmp_path, "packages/@abro/i18n/src/en.json", '{"trip": {"publish": "Publish"}}')
    write(tmp_path, "packages/@abro/i18n/src/am.json", "{}")
    assert "missing key 'trip.publish'" in messages(i18n_parity.run(tmp_path))


def test_i18n_parity_catches_a_catalog_with_no_counterpart(tmp_path: Path) -> None:
    write(tmp_path, "abro-mobile/locales/en.json", '{"trip": "Trip"}')
    assert "no matching 'am' catalog" in messages(i18n_parity.run(tmp_path))


def test_i18n_parity_accepts_matching_catalogs(tmp_path: Path) -> None:
    write(tmp_path, "abro-web/messages/en/common.json", '{"trip": {"publish": "Publish"}}')
    write(tmp_path, "abro-web/messages/am/common.json", '{"trip": {"publish": "አጋራ"}}')
    assert i18n_parity.run(tmp_path) == []


# --- amharic-search --------------------------------------------------------------


def test_amharic_search_catches_a_raw_comparison(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/repositories/place.py",
        """
        stmt = select(Place).where(Place.name_am.ilike(f"%{query}%"))
        """,
    )
    assert "without am_normalize" in messages(amharic_search.run(tmp_path))


def test_amharic_search_accepts_a_normalised_comparison(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/repositories/place.py",
        """
        from app.core.amharic import am_normalize

        stmt = select(Place).where(Place.name_am_normalized.ilike(am_normalize(query)))
        """,
    )
    assert amharic_search.run(tmp_path) == []


def test_amharic_search_runs_the_homophone_fixtures(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/core/amharic.py",
        """
        def am_normalize(value: str) -> str:
            return value.strip().lower()
        """,
    )
    assert "does not unify" in messages(amharic_search.run(tmp_path))


def test_amharic_search_accepts_a_correct_normalizer(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/core/amharic.py",
        """
        FOLDINGS = {
            "\\u1210": "\\u1200", "\\u1280": "\\u1200",
            "\\u1220": "\\u1230",
            "\\u12d0": "\\u12a0",
            "\\u1340": "\\u1338",
        }


        def am_normalize(value: str) -> str:
            return "".join(FOLDINGS.get(c, c) for c in value.strip())
        """,
    )
    assert amharic_search.run(tmp_path) == []


# --- geo-safety ------------------------------------------------------------------


def test_geo_safety_catches_unpaired_st_dwithin(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/repositories/matching.sql",
        """
        SELECT id FROM trip_search
        WHERE ST_DWithin(route, :origin, :radius);
        """,
    )
    assert "_ST_Expand" in messages(geo_safety.run(tmp_path))


def test_geo_safety_accepts_the_paired_predicate(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/repositories/matching.sql",
        """
        SELECT id FROM trip_search
        WHERE _ST_Expand(:origin, :radius) && route
          AND ST_DWithin(route, :origin, :radius);
        """,
    )
    assert geo_safety.run(tmp_path) == []


def test_geo_safety_catches_a_missing_direction_check(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/repositories/corridor.sql",
        """
        SELECT id,
               ST_LineLocatePoint(route, :origin) AS f_pickup,
               ST_LineLocatePoint(route, :destination) AS f_dropoff
        FROM trip_search;
        """,
    )
    assert "f_dropoff > f_pickup" in messages(geo_safety.run(tmp_path))


def test_geo_safety_accepts_a_directional_corridor_query(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/repositories/corridor.sql",
        """
        SELECT id FROM (
            SELECT ST_LineLocatePoint(route, :origin) AS f_pickup,
                   ST_LineLocatePoint(route, :destination) AS f_dropoff
            FROM trip_search
        ) candidates
        WHERE f_dropoff > f_pickup;
        """,
    )
    assert geo_safety.run(tmp_path) == []


# --- pii-logging -----------------------------------------------------------------


def test_pii_logging_catches_a_structured_phone_key(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/services/otp.py",
        """
        logger.info("otp dispatched", extra={"phone": user.phone_number})
        """,
    )
    assert pii_logging.run(tmp_path) != []


def test_pii_logging_catches_a_literal_ethiopian_number(tmp_path: Path) -> None:
    write(tmp_path, "abro-api/app/services/otp.py", 'logger.info("sent to +251911234567")\n')
    assert "Ethiopian phone number" in messages(pii_logging.run(tmp_path))


def test_pii_logging_allows_message_text_mentioning_pii(tmp_path: Path) -> None:
    write(
        tmp_path,
        "abro-api/app/services/otp.py",
        """
        logger.info("phone verified", extra={"user_id": user.id})
        """,
    )
    assert pii_logging.run(tmp_path) == []


def test_pii_logging_catches_a_typescript_console_call(tmp_path: Path) -> None:
    write(tmp_path, "abro-mobile/src/api/auth.ts", "console.log('sending', user.phoneNumber);\n")
    assert "passed to logger" in messages(pii_logging.run(tmp_path))


def test_pii_logging_allows_an_opaque_identifier(tmp_path: Path) -> None:
    write(tmp_path, "abro-mobile/src/api/auth.ts", "console.log('sending otp', user.id);\n")
    assert pii_logging.run(tmp_path) == []
