# ADR 0001 — A monorepo, and a two-language stack

**Status:** accepted · **Date:** 2026-07-31

## Context

abro ships four deployable things — a FastAPI backend, a Next.js web app, an Expo mobile app and a
Pulumi infrastructure definition — plus a self-hosted geo stack. The first structural decision is
whether those live together, and how many languages they are allowed to be written in.

Every other ADR in this directory assumes an answer to that question. This one records it.

## Decision

**One public monorepo, and exactly two languages: Python 3.12 and TypeScript.**

| Component | Choice |
|---|---|
| `abro-api/` | FastAPI, Python 3.12, SQLAlchemy 2, Alembic, PostgreSQL 16 + PostGIS, Redis, ARQ |
| `abro-web/` | Next.js 15, App Router |
| `abro-mobile/` | Expo SDK 54, expo-router, React Query, Zustand, NativeWind |
| `abro-infra/` | Pulumi, in Python |
| `abro-routing/` | Valhalla, Photon and PMTiles over an OSM Ethiopia extract |
| `packages/` | Shared TypeScript: `@abro/api-client`, `@abro/time`, `@abro/i18n`, `@abro/config` |

The repository is **public**. Provider adapters are the only place a third-party SDK may appear,
and each sits behind an interface with a `mock` implementation as the default.

## Why

**A monorepo is what makes the shared packages enforceable.** Three of abro's six custom CI gates
compare one part of the tree against another: `@abro/api-client` must not drift from the OpenAPI
spec the backend generates, the `en` and `am` catalogs must have identical key sets, and Ethiopian
time conversion must not appear outside `packages/@abro/time`. Split across repositories those
checks become a cross-repo release dance, and a gate that is awkward to run is a gate that gets
skipped. Here they are a path filter and a script.

**Two languages, because the time logic can only live in one place.** Ethiopian calendar and
6-hour-clock conversion is the single highest-risk piece of logic in the product — a six-hour error
is a passenger left at a terminal. Both clients are TypeScript, so putting the conversion in a
TypeScript package means one implementation rather than one per client. The backend then holds only
timezone-aware UTC and needs no calendar code at all. Pulumi is written in Python rather than
TypeScript for the same reason inverted: it keeps the infrastructure definition in the same language
as the service it deploys, so there is no third toolchain. See ADR 0007.

**PostgreSQL with PostGIS is not interchangeable here.** Bookings and money need real transactions —
a seat hold, a ledger entry and a payment intent commit or fail together — and matching is
fundamentally geometric, storing route linestrings and running indexed spatial predicates against
them. See ADR 0004.

**Public, deliberately.** Unlimited free Actions minutes, plus CodeQL, Dependabot and OpenSSF
Scorecard at no cost. abro's differentiator is the Ethiopian domain knowledge encoded in
`docs/`, not the CRUD around it, and the gate pipeline this buys is worth more than the secrecy.
It does mean no secret may ever reach the tree, which is why every provider defaults to `mock`.

## Consequences

- **Workflows must be path-filtered.** A monorepo where a docs typo runs the mobile suite trains
  people to ignore CI. Filters are set at workflow level, which also means nothing fires for a
  directory that does not exist yet.
- **A single npm workspace root** covers `abro-web`, `abro-mobile` and `packages/*`. The backend
  keeps its own Python tooling; there is no attempt to unify the two package managers.
- **Zero `tsc` errors from the first commit.** The predecessor project carried a grandfathered
  allowance of three, and an allowance above zero is an allowance that grows.
- Provider SDKs are confined to `app/integrations/`, reachable only through a service interface.
  That containment is what lets a developer run the whole system with no credentials — which
  matters because production credentials require a registered Ethiopian business.
- One version, one CI run, one review surface. The cost is that CI configuration is more complex
  than four small repositories would need, and it is paid up front in `.github/workflows/`.
