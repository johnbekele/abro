# ADR 0003 — Cancellation and refund tiers

**Status:** accepted · **Date:** 2026-07-31

## Context

Cancellation policy is the main lever on marketplace reliability. Too lenient and seats get held
then abandoned; too harsh and nobody books. BlaBlaCar has iterated on this across fifteen years
and twenty countries, so copy the structure and adapt the amounts to the deposit model.

## Decision

### Passenger cancels

| When | Deposit | Reputation |
|---|---|---|
| More than 24 h before departure | Refunded in full | None |
| Within 24 h, under 30 min since booking | Refunded in full | None |
| Within 24 h, more than 30 min since booking | Forfeited | Automatic 1/5 |
| After departure, or no-show past 15 min | Forfeited | Automatic 1/5 |

The **30-minute grace window** survives inside the 24-hour penalty zone deliberately: it protects
a mis-tap without weakening the deadline.

### Driver cancels

Any driver cancellation, including failing to appear within 15 minutes of the agreed meeting
time, refunds the passenger's deposit **in full** and applies an automatic 1/5 to the driver.
Seats return to inventory immediately.

### Other rules

- **Manual-approval expiry.** If a driver does not respond before the deadline, the request
  expires and the deposit refunds automatically.
- **Post-trip complaint window.** One hour after scheduled arrival. Absent a complaint the trip
  is tacitly confirmed and ratings open.
- **No-show clock.** 15 minutes, matching BlaBlaCar's European default.

## Why

Under the deposit model we hold only the service fee, so we cannot move the contribution between
parties as compensation. The financial penalty is therefore smaller than BlaBlaCar's and the
**reputational penalty carries proportionally more weight** — which is why automatic 1/5 ratings
are part of the policy rather than an optional extra. Without them, a late cancellation costs
almost nothing.

## Consequences

- Every tier boundary is a timestamp comparison against departure, so the booking state machine
  needs precise timezone-aware transition timestamps. This is one of the places a naive datetime
  quietly costs real money.
- Refunds need a provider that supports them programmatically. A Telebirr deposit must be
  refunded as ledger credit rather than reversed.
- Operations need a manual override with an audit trail — BlaBlaCar reserves sole discretion over
  refund legitimacy and so do we.
