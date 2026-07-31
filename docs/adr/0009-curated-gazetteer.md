# ADR 0009 — A curated gazetteer instead of geocoding

**Status:** accepted · **Date:** 2026-07-31

## Context

Both parties need to agree on where to meet. In Europe that is an address or a dropped pin.
Ethiopia has neither convention working reliably.

Formal street addressing effectively does not exist. The national digital addressing system, eDAS,
is a pilot covering one town. People locate each other by **landmark and relative position** —
"around Bole Medhanealem", "in front of the Total station" — using the Amharic construction
*akababi* (አካባቢ, "around"). Administrative hierarchy (region, zone, woreda, kebele) exists but
boundaries shift, so it is a label rather than dependable geometry. OSM's own status note for
Addis Ababa reads "main roads, many names missing", and roads are commonly known by a colloquial
name rather than the official one: Africa Avenue is universally "Bole Road".

## Decision

Ship a **curated gazetteer** of roughly 200 hand-verified places as seed data, and let users pick
from it rather than typing an address.

Each entry carries:

- a canonical **Amharic name** and a **Latin transliteration** — many users type "Bahir Dar"
  rather than switching keyboards, so both are indexed;
- an **alias array** of colloquial names and the misspellings people actually type;
- a **kind** — city, bus terminal (*menaharia*), fuel station, junction, landmark, university,
  LRT station, town gate;
- a coordinate **snapped to the road network**;
- a flag for **access-controlled roads**. The Addis–Adama Expressway is grade-separated, so a car
  physically cannot stop on it to collect someone. Those places are valid destinations and must
  never be offered as a mid-route meeting point.

Photon remains available for exploratory search but is secondary. The gazetteer is the source of
truth for anywhere a passenger can actually be picked up.

## Why this is the easier problem

BlaBlaCar's open version of this — synthesising an arbitrary meeting point anywhere along a route —
is genuinely hard, and their Smart Stop work is funded accordingly. Selecting from a finite,
human-verified, named set is tractable, and a name both parties recognise does more work at the
roadside than a coordinate does.

Intercity carpooling also needs only coarse endpoints — a city, then a named landmark on the trunk
road — not doorstep precision. Building address entry would be solving a harder problem than we
have.

## Consequences

- Seeding and maintaining the gazetteer is real product work, not a data chore. Coverage gaps show
  up directly as corridors where nobody can arrange a pickup.
- Meeting-point suggestion becomes: take the route window around the passenger's origin with
  `ST_LineSubstring`, intersect it with the gazetteer, rank by walking distance and added detour.
  Raw OSM POI density outside Addis is too thin and too inconsistently named to use instead.
- The gazetteer ships to the mobile client as local SQLite so search works with no connection.
- Amharic search over it must go through `am_normalize()` — see ADR 0004's sibling gate — because
  `ሀ/ሐ/ኀ`, `ሰ/ሠ`, `አ/ዐ` and `ጸ/ፀ` are pronounced identically and spelled interchangeably.
- Show a photo of the meeting point where we have one. Recognition beats precision here.
