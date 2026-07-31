# ADR 0007 — Ethiopian calendar and clock live only in TypeScript

**Status:** accepted · **Date:** 2026-07-31

## Context

Ethiopia uses two conventions that differ from the Gregorian/24-hour defaults, and both apply to
the single most important field in the product: a trip's departure time.

**The calendar** has thirteen months — twelve of thirty days plus Pagumē of five or six — and runs
roughly seven to eight years behind Gregorian.

**The clock starts at dawn.** The day begins at 06:00 EAT, which is spoken as "12:00". So 09:00
EAT is "3:00 in the morning" and 15:00 EAT is "9:00". In practice it is a flat six-hour offset,
not tied to actual sunrise. People switch to EAT when speaking to foreigners, which makes the
ambiguity worse rather than better.

A documented real-world failure: a meeting set for "6 o'clock" where one party arrived at 6 PM and
the other expected noon. For abro, that failure is a passenger stranded at a bus terminal and a
refund.

## Decision

**All Ethiopian calendar and clock conversion lives in exactly one place: `packages/@abro/time`.**

- The backend stores and reasons in **UTC only** and contains no calendar code whatsoever.
- Web and mobile both import `@abro/time`. Neither implements its own conversion.
- The library wraps [`kenat`](https://github.com/MelakuDemeke/kenat), which covers conversion,
  thirteen-month arithmetic, the Ethiopian time system, Ge'ez numerals, and Bahire Hasab for
  movable feasts.
- Calendar system and clock convention are a **persisted per-user setting**, chosen during
  onboarding rather than inferred, defaulting to Ethiopian.
- **Both conventions are always displayed together anywhere a mistake is costly.** For a departure
  time that means: `ጠዋት 3:00 (9:00 AM) · Meskerem 5, 2019 / Sept 15, 2026`. The redundancy costs a
  few characters; the alternative costs a trip.
- Every SMS, Telegram message and push notification mentioning a departure time is disambiguated
  the same way.

A CI gate fails any Ethiopian-time conversion found outside the package, and any naive datetime in
the backend.

## Why one place

If the conversion existed on the server and in two clients, they would eventually disagree — a
different rounding rule, a different leap-year check, one of them updated and the others not. The
symptom would be a six-hour discrepancy appearing intermittently on some devices, which is close
to the hardest possible bug to reproduce.

Ethiopia is UTC+03:00 with no daylight saving, so there is at least no ambiguous-hour handling.

## Consequences

- The backend cannot format a user-facing date. It returns ISO 8601 UTC and the client renders it.
- Any timestamp crossing an API boundary is Gregorian UTC. Note that `kenat`'s default Ethiopian
  ISO output appends a non-standard `+12h` suffix for night times — never let that reach the wire.
- Holidays drive intercity demand: Enkutatash, Meskel, Genna, Timkat, Fasika and the Eids are peak
  travel. The movable feasts need Bahire Hasab, which is why the library choice matters.
- Ge'ez numerals are acceptable for dates and wrong for money and seat counts.
