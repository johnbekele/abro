# ADR 0002 — A deposit, not escrow

**Status:** accepted · **Date:** 2026-07-31

## Context

BlaBlaCar takes the full contribution online at booking, holds it, and pays the driver 48 hours
after the trip. Reproducing that in Ethiopia means holding customer funds.

## Decision

**The passenger pays a deposit online, sized to cover our service fee. The balance is paid in
cash to the driver at pickup.** We never hold money belonging to either party.

Where a ledger balance is unavoidable it is a double-entry record in our database, reconciled
against a balance held by a licensed PSP — never a bank account in abro's name.

## Why

**It is not legal otherwise.** NBE directive ONPS/01/2020 makes holding an e-money float a
licensed activity: ETB 100 million paid-up capital as of May 2025, at least ten shareholders with
none above 20%, and the float held in trust at a bank. That is not a startup-stage obstacle, it is
a different company.

**Cash is the market.** Only 21% of Ethiopian adults made a digital payment in the last year, 16%
rurally. Full prepay would exclude most of the addressable market.

**The deposit still solves what prepay was for.** BlaBlaCar's Poland launch kept the contribution
in cash and moved only the fee online, and passenger no-shows fell by nearly 90%. Requiring *some*
payment is what changes behaviour.

**It removes the payout leg.** For a cash trip there is nothing to pay the driver, which matters
because Ethiopian PSPs bill each payout as its own transaction on top of the ~2.5% inbound cost.

## Consequences

- No payout scheduling, reconciliation, or unclaimed-funds escheatment in v1.
- Refunds only ever return the deposit, so the money matrix is simpler than BlaBlaCar's — but
  driver-side compensation cannot be paid in money, only in reputation. See ADR 0003.
- Drivers carry cash-handling risk. The product must not pretend otherwise.
- Telebirr has no programmatic refund API, so refundable deposits must route through Chapa.
- If a PSP float partnership later becomes available, full escrow is a provider-level change
  rather than a redesign, because the ledger already exists.
