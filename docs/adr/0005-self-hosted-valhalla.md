# ADR 0005 — Self-hosted Valhalla and OSM, not a commercial maps API

**Status:** accepted · **Date:** 2026-07-31

## Decision

Self-host the geo stack on an OpenStreetMap Ethiopia extract: **Valhalla** for routing, matrix and
snapping, **Photon** for place search, **PMTiles** from object storage for basemap tiles,
**MapLibre** on both clients.

## Why

**Google is disqualified on licensing, not price.** Its terms forbid persisting the underlying
data, and ADR 0004 requires storing route linestrings in our own tables and running spatial
predicates against them. That is the product.

**The extract is small.** Ethiopia is ~139 MB from Geofabrik, about 0.22% of the planet file. The
whole stack runs comfortably on a 2 vCPU / 4 GB VPS at roughly $12–24 a month — headroom, not a
compromise. The equivalent Google bill at 100k requests per product per month is over $1,100.

**Foreign currency is a real obstacle.** Ethiopian businesses struggle to pay USD-denominated SaaS
invoices, and those payments cannot be used for local tax documentation. Self-hosting removes the
problem for our highest-volume calls entirely.

**Valhalla over OSRM** because Valhalla computes at request time. OSRM precomputes a contracted
graph, faster per query but fixing the cost model at build time — so per-driver detour tolerances
and alternates would need a rebuild. Valhalla also gives isochrones and Meili map matching, both
of which we want later.

**Photon over Nominatim** because Nominatim is built around structured street addresses and
Ethiopia does not have them. Photon's fuzzy prefix search over a POI-heavy index is the right
shape — though it stays secondary to the curated gazetteer. See ADR 0009.

## Consequences

- We own an operational service. A nightly job pulls the Geofabrik extract, rebuilds tiles and
  swaps the directory atomically. At this size that is minutes, and it is a shell script plus a
  timer.
- **Do not trust OSM `surface` tags for travel-time estimates.** 51% of Ethiopian arterial road
  kilometres have no surface tag, and satellite-derived classification beats the tags 89% to 65%.
  Calibrate ETAs from observed trip durations instead.
- Ethiopian OSM coverage of the trunk network is good — every launch corridor is mapped — but road
  names are frequently missing, another reason the gazetteer carries the naming.
- Improving OSM on our corridors is a direct product investment. Contribute fixes upstream.
- Gebeta Maps, which bills in ETB with tax-valid receipts, stays available as an optional POI
  autocomplete supplement, not a dependency.
