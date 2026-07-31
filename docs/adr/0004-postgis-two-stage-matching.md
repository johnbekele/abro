# ADR 0004 — Two-stage matching: PostGIS, then Valhalla

**Status:** accepted · **Date:** 2026-07-31

## Context

Match a passenger's origin and destination against thousands of published route linestrings, fast
enough for interactive search. BlaBlaCar published their approach in 2024 and it transfers
directly.

## Decision

**Stage 1 — gross match, in PostGIS.** Straight-line proximity of pickup and dropoff to each
trip's route, filtered by that driver's own detour tolerance. Cheap and indexed.

**Stage 2 — exact match, in Valhalla.** Real detour distance and duration for the survivors only,
batched into one `sources_to_targets` matrix call rather than one route call per candidate.

**Never call the router on an unfiltered candidate set.**

### The index detail that makes stage 1 work

`ST_DWithin` can use a GiST index only when the distance argument is constant. Each driver has
their own tolerance, so the distance varies per row and the index is skipped — the difference
between a fast query and a sequential scan over every trip.

The fix is a functional index on the expanded route, and a query using **both** the overlap
operator (to hit the index) and `ST_DWithin` (to do the real check):

```sql
CREATE INDEX ix_trip_route_expanded
  ON trip USING GIST (_ST_Expand(route_geog, detour_tolerance_m));
```

```sql
WHERE _ST_Expand(t.route_geog, t.detour_tolerance_m) && :pickup
  AND ST_DWithin(:pickup, t.route_geog, t.detour_tolerance_m)
```

Using only one of the two looks equivalent and is not. BlaBlaCar measured the pairing at 34×.

### Direction

Proximity alone is not a match: a passenger going Adama→Addis is close to a driver going
Addis→Adama. Enforce ordering with linear referencing.

```sql
ST_LineLocatePoint(route, :pickup)  AS f_pickup,
ST_LineLocatePoint(route, :dropoff) AS f_dropoff
-- match only when f_dropoff > f_pickup
```

That predicate is the cheapest, highest-value line in the matcher, and a CI gate fails any
corridor query that omits it.

### Storage

Routes are `geography(LineString, 4326)` so `ST_DWithin` takes metres directly, removing a class
of unit bugs over ~1,000 km distances. Cast explicitly when using linear-referencing functions —
their geography and geometry implementations measure differently.

### No materialized view

BlaBlaCar's load test found a concurrent refresh took two to three minutes and consumed the whole
database, and they named it as their scaling weak point. Use a trigger-maintained denormalised
`trip_search` table instead: same benefit, no refresh cliff, and it costs nothing to choose now.

## Consequences

- H3 and geohash bucketing are not needed. Those index points; our primary object is a long
  linestring, which is GiST's job. Revisit only if live point-to-point dispatch is ever added.
- Boost trips multiply the candidate set, so stage 1 must stay strictly indexed.
- Log every accept and refuse decision from day one so an acceptance-prediction model becomes
  trainable later.
