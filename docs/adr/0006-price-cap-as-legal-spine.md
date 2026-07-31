# ADR 0006 — The price cap is the legal spine

**Status:** accepted · **Date:** 2026-07-31

## Context

Ethiopian Proclamation 608/2010 requires Code 1 plates to operate public transport. Ride-hailing
runs on Code 1 and Code 3. **Carpooling depends on Code 2 — ordinary private vehicles — and that
is the legally contested category.** ZayRide has lobbied to have Code 2 admitted and has had 15+
affiliated vehicles impounded. There is no dedicated framework for app-based transport, oversight
is fragmented with no lead agency, and litigation is pending in federal court.

This is the single largest existential risk to the product.

## Decision

Adopt BlaBlaCar's defence: **abro is not a transport service, it is a cost-sharing intermediary,
and the price cap is the evidence.** Encode that in the system, not only in the terms of service.

Treated as launch-blocking:

1. **A hard price band of 80–120% of the computed recommendation**, enforced server-side at
   publish time. Publishing above the cap is rejected, not warned about. BlaBlaCar allows 50–150%;
   we are tighter because we have no legacy to protect and a weaker position to defend.
2. **The recommendation is a cost proxy** — distance, fuel consumption, current administered fuel
   price, seat divisor. It does not respond to demand.
3. **No surge pricing, ever.** There is no code path that raises a price because demand rose.
4. **Per-driver monitoring** of trip frequency, passenger counts and cumulative contributions,
   with automatic suspension on patterns suggesting commercial operation.
5. **No dispatch and no assignment.** Drivers publish, passengers choose. abro never picks.
6. **No company-owned vehicles**, ever, including for testing.
7. **Vehicle document requests** on demand, to establish non-commercial entitlement.

## Consequences

- The pricing service is compliance infrastructure. Changes to it warrant more scrutiny than a
  normal feature, and the cap constants belong in one auditable place.
- Drivers will ask to charge more. The answer is no, and the UI should explain why rather than
  simply refusing.
- Anti-commercialisation monitoring produces false positives — a genuine daily Addis–Adama
  commuter looks like a commercial operator. Suspension must be reviewable by a human.
- Assume the **data-residency expectation** from the 2019 Addis Ababa Transport Bureau directive
  applies to us.
- Intercity routes cross regional boundaries, so this is a federal conversation as well as a city
  one.
