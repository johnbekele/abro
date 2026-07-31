# ADR 0010 — Offline-first clients

**Status:** accepted · **Date:** 2026-07-31

## Context

Two facts about Ethiopian connectivity make offline behaviour a requirement rather than a polish
item.

**Internet shutdowns.** Ethiopia is the leading perpetrator of network blackouts in Africa, having
shut down the internet at least 26 times since 2016. Tigray was dark from November 2020 to
November 2022. Amhara mobile internet was restricted from August 2023 across 19 cities and not
fully restored until July 2024 — roughly 345 days. Bahir Dar, Gondar and Mekelle are all on the
launch corridor list. A regional shutdown removes an entire route from service for weeks.

**The highway is dark.** 4G reaches 82.23% of the population but only **36.29% of the land area**.
Population coverage is measured where people live — in towns. abro operates on the 900 km between
towns.

## Decision

The mobile client works without a connection, and degrades to SMS when it has none at all.

- **Bundle the basemap.** PMTiles for the trunk corridors and the eight launch cities, read from
  device storage. MapLibre Native supports `pmtiles://file://` directly. Note that PMTiles sources
  do not participate in MapLibre's offline pack caching, so the download and file path are ours to
  manage, and `pmtiles://asset://` does not work because the asset manager cannot do byte-range
  reads.
- **Ship the gazetteer as local SQLite** so place search works offline.
- **Cache upcoming trips in full** — route polyline, meeting point, and above all the driver's
  phone number. A passenger mid-journey during a blackout needs the phone number more than
  anything else the app can offer.
- **Queue writes with idempotency keys.** Booking, cancelling and messaging are recorded locally
  and reconciled on reconnect. A failed POST is never data loss.
- **Store-and-forward location tracking**, not streaming. Buffer fixes locally, flush in batches,
  delta-encode them. One fix per 30–60 seconds on the highway is plenty; tighten to 5–10 seconds
  only in the last 2 km before pickup. Use distance intervals so a stationary vehicle costs
  nothing. Batched HTTPS beats a persistent socket, which burns battery on reconnection storms
  over flaky 2G.
- **Interpolate on the consumer side.** Animate the vehicle along the known route polyline between
  sparse fixes; sparse data feels smooth when rendered against the route.
- **SMS is the degraded channel.** Every state transition that matters must be recoverable from an
  SMS, in a compact format that carries the booking code, meeting point and driver contact.

## Consequences

- Background location on Android needs a development build, `FOREGROUND_SERVICE_LOCATION` on
  Android 14+, and Play Store review for `ACCESS_BACKGROUND_LOCATION`. Budget calendar time.
- Continuity cannot be guaranteed. Android will kill the app, and Transsion, Xiaomi and Samsung
  skins are aggressive about it. Onboard drivers through disabling battery optimisation, with
  device-specific instructions, and treat the persistent foreground-service notification as a
  feature rather than something to hide.
- Keep the APK small and offer direct APK distribution alongside Play Store — normal in Ethiopia.
- Payloads stay small, with ETags and aggressive `Cache-Control`.
- Multi-region deployment later, so a regional shutdown does not take down the platform itself.
