# Product context

The single source of truth for what abro is and the business rules that govern it. Every issue
assumes you have read this.

---

## 1. The product

Intercity carpooling for Ethiopia, modelled closely on BlaBlaCar. A driver already making a long
journey publishes their empty seats and a per-seat cost contribution. Passengers travelling the
same corridor search, book a seat, and meet the driver at an agreed landmark.

**We are a marketplace and an introduction service.** We do not employ drivers, own vehicles,
dispatch anyone, or set prices. This is not a legal nicety — see §7.

### Why this and not ride-hailing

Every incumbent in Ethiopia — Ride, Feres, ZayRide, Yango — is urban, on-demand and
point-to-point. More than fifty companies have entered that market in eight years and fewer than
ten sizeable ones survive. Intercity is unserved.

What exists on the corridors today is the bus: Selam Bus and Sky Bus at the luxury end, informal
operators at the low end. The informal ones **wait until the vehicle is full before departing**,
so a stated departure time means little. A committed departure time and a guaranteed seat is a
real product improvement, and it is what to lean on in positioning.

### Launch corridors

Roughly 90% of Ethiopia's long-distance buses are based in Addis Ababa, so the network is a star,
not a mesh. Launch on the spokes.

| Corridor | Distance | Bus time | Notes |
|---|---|---|---|
| Addis Ababa – Adama | ~90 km | ~1.5 h | Expressway. Highest frequency, genuinely commuter-like. |
| Addis Ababa – Hawassa | ~275 km | ~4 h | Expressway upgrade in place. |
| Addis Ababa – Jimma | ~350 km | ~6 h | |
| Addis Ababa – Dire Dawa | ~445 km | ~6 h | Continues to Harar. |
| Addis Ababa – Bahir Dar | ~565 km | ~7 h | Shutdown-prone region. |
| Addis Ababa – Gondar | ~730 km | ~10 h+ | Most intermediate towns of any corridor. |
| Addis Ababa – Mekelle | ~780 km | ~12 h+ | Assess security before enabling. |

Two structural facts to design around. **Departures cluster before 08:00 and dry up by midday**,
because night intercity travel is widely avoided on safety grounds — the publish flow should
default to morning, and sparse afternoon results are correct behaviour rather than a bug. And
**Addis–Adama is a commuter route**, so recurring rides deserve more prominence than BlaBlaCar
gives them.

---

## 2. Users

- **Driver.** Owns a Code 2 private vehicle, already making the trip, wants to offset fuel. Needs
  the publish flow to take under two minutes and the money to be unambiguous.
- **Passenger.** Currently takes the bus. Wants a departure time that is real, a guaranteed seat,
  and enough information about the driver to feel safe on a seven-hour journey.
- **Operations.** Reviews identity documents, adjudicates no-shows and disputes, moderates
  content, monitors for drivers operating commercially. The admin CRM is their entire workday.

---

## 3. The money flow

**The passenger pays a deposit online at booking. The balance is paid in cash to the driver at
pickup.** The deposit is sized to cover the platform's service fee.

This is the correct design for this market, for three reasons.

1. **We cannot legally hold passenger funds.** National Bank of Ethiopia directive ONPS/01/2020
   makes holding an e-money float a licensed activity, requiring ETB 100 million in paid-up
   capital (raised May 2025), at least ten shareholders with none above 20%, and the float held
   in trust at a bank. Full escrow is off the table until a licensed PSP partnership exists.
2. **Cash dominates.** Only 21% of Ethiopian adults made a digital payment last year, and 16%
   rurally. A full-prepay product would exclude most of the market.
3. **It still fixes no-shows.** When BlaBlaCar introduced paid booking in Poland, passenger
   no-shows fell by nearly 90%. Requiring *any* payment produces the effect; requiring the full
   fare is not necessary to get it.

It also removes the payout leg entirely for cash trips, which matters because payout fees are
billed per transaction on top of the roughly 2.5% inbound cost.

**Service fee.** Ride and Feres have anchored the market at 12% and 8% commission. Target 10–15%
of the contribution with an absolute floor around ETB 10–15 — the floor must clear Chapa's ETB 5
minimum fee.

**Providers.** Chapa first: the only Ethiopian provider with public self-serve APIs covering
charge, partial refund, split and payout, and its sandbox works without a merchant account.
M-Pesa Ethiopia second, for its B2C disbursement API. Telebirr is collection-only — it has no
programmatic refunds. **Stripe is unavailable to Ethiopian entities and will not become
available**; it exists here only as a test double, never a launch path.

Everything sits behind a provider interface with a `mock` implementation. See
[ADR 0002](adr/0002-deposit-not-escrow.md).

---

## 4. Pricing and the cap

The platform recommends a per-seat contribution computed from distance, a fuel-consumption
assumption, the current administered fuel price, and a seat divisor. Fuel prices in Ethiopia are
set administratively and change, so the per-kilometre basis is **configuration, never a
constant**.

The recommendation should land **between the ordinary and the luxury bus fare** for the corridor
— cheap enough to beat a coach, high enough to genuinely offset the driver's fuel. Reference
point: Addis→Bahir Dar is roughly ETB 185 ordinary and ETB 340 luxury.

**Drivers may adjust within 80–120% of the recommendation.** BlaBlaCar allows 50–150%; we are
tighter because we have no legacy to protect and a weaker regulatory position to defend. Above
the cap, publishing is rejected outright. There is no surge pricing, ever.

---

## 5. Matching

Two stages, following BlaBlaCar's published approach.

1. **Gross match in PostGIS.** Cheap, indexed, as-the-crow-flies. Filters thousands of candidate
   trips down to tens.
2. **Exact match via Valhalla.** Computes real detour distance and duration for the survivors
   only, batched into a single matrix call.

Never call the router on an unfiltered candidate set. Details and the index trick are in
[ADR 0004](adr/0004-postgis-two-stage-matching.md).

**Partial-route matching is core, not a refinement.** BlaBlaCar's "Boost" rides — synthetic
offers generated by adding a short detour to an existing trip — are 45% of their displayed
results and produce 30% of all their bookings. A passenger in a town off the main corridor has no
other way to find a ride.

Ranking is rule-based at launch. Log every accept and refuse decision from day one so an
acceptance-prediction model becomes trainable later; do not attempt the model before there is
data.

---

## 6. Trust and safety

Copy BlaBlaCar's mechanics closely. They are well tested and the reasoning behind each is sound.

- **Two-way ratings with blind reveal.** Ratings become visible when both parties have rated, or
  14 days after the first rating, whichever comes first. This is what kills revenge ratings.
- **Automatic ratings.** 5/5 to both parties if a completed trip goes unrated for 14 days; 1/5
  for a late cancellation or a confirmed no-show.
- **Cancellation tiers.** Four of them, keyed on timing, with a 30-minute grace window after
  booking that survives even inside the penalty zone. Full matrix in
  [ADR 0003](adr/0003-cancellation-and-refund-tiers.md).
- **No-show clock.** 15 minutes past the agreed meeting time.
- **Post-trip complaint window.** One hour, after which the trip is tacitly confirmed.
- **Contact details are released at booking confirmation**, not before. Pre-booking messages are
  templated and moderated, and the blocklist covers phone numbers, email addresses, price
  negotiation, cash-payment proposals and external links.
- **Identity.** Phone verification is the floor for everyone. Fayda national eKYC is required for
  drivers and optional for passengers — over 30 million Fayda IDs have been issued, and the
  unique national identifier is the only real defence against ban evasion via duplicate accounts.
- **Ladies Only.** A female driver may restrict a ride to female passengers.
- **Long-journey safety.** These are seven-hour trips through remote areas, so BlaBlaCar's
  European assumptions do not transfer. Itinerary sharing with a trusted contact, an in-app SOS,
  and an explicit night-travel policy are launch requirements, not enhancements.

Verification badges must carry BlaBlaCar's disclaimer: verified means only that the procedure was
completed, not that the information is true. That wording is a real liability shield.

---

## 7. The legal position

**This is the biggest existential risk to the product, and it shapes the code.**

Proclamation 608/2010 requires Code 1 plates to operate public transport. Ride-hailing runs on
Code 1 and Code 3. **Carpooling depends on Code 2 — private vehicles — which is precisely the
contested category.** ZayRide has lobbied to have Code 2 admitted and has had 15+ affiliated
vehicles impounded. There is no dedicated national framework for app-based transport, oversight
is split across several agencies with no lead, and litigation is pending in federal court.

Our defence is the same one BlaBlaCar uses across Europe: **we are not a transport service, we
are a cost-sharing intermediary, and the price cap is the proof.** That makes the following
launch-blocking compliance infrastructure, not product features:

- a hard price cap at 120% of the recommendation, enforced server-side;
- per-driver revenue and trip-frequency monitoring, with automatic suspension on patterns
  suggesting commercial operation;
- no surge pricing, no dispatch, no fare metering, no company-owned vehicles;
- the ability to demand vehicle documents proving non-commercial entitlement.

There is also a **data-residency expectation** from the 2019 Addis Ababa Transport Bureau
directive, which required ride-hailing companies to store their database locally. Assume it
applies. Intercity routes cross regional boundaries, so the federal transport ministry matters as
much as the city bureau.

---

## 8. Explicitly out of scope for v1

| Not building | Why |
|---|---|
| Full online payment of the contribution | Requires a licensed PSP float partnership. |
| Programmatic driver payouts | Follows from the above; the deposit model avoids needing it. |
| ML ranking of matches | No training data exists yet. Rule-based first, log the labels. |
| Insurance products | Needs a partner. |
| A bus vertical | BlaBlaCar bought Ouibus eventually. Not now. |
| Corporate and commuter accounts | Addis–Adama makes this attractive later. |
| Urban point-to-point rides | Head-on competition with well-funded incumbents. |
| Afaan Oromo and Tigrinya | After launch. `am` and `en` only for v1. |

---

## 9. What success looks like for v1

A passenger in Addis Ababa can find a ride to Bahir Dar leaving tomorrow morning, see who the
driver is and what other passengers thought of them, book a seat by paying a deposit with
Telebirr, receive a confirmation over Telegram that survives having no data connection, meet the
driver at a landmark they both recognise, pay the balance in cash, and rate each other
afterwards — with the whole interface in Amharic and the departure time shown the way they
actually think about time.
