# Runbook

How to run abro locally.

**Nothing described here exists yet.** The repository is pre-code, and the `M0 Foundations`
milestone delivers the `Makefile`, the compose file and the services below. This document is the
contract those issues implement against: if an M0 issue produces a different target name, the issue
is wrong, because [`README.md`](../README.md), [`CONTRIBUTING.md`](../CONTRIBUTING.md) and
[`AUTOPILOT.md`](../AUTOPILOT.md) already reference these by name.

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Node | as pinned in [`.nvmrc`](../.nvmrc) | `nvm use` in the repo root |
| Python | 3.12 | `uv` preferred for environment management |
| Docker | with Compose v2 | 8 GB allocated; the Valhalla tile build is the hungry part |
| `make` | any | |

No provider credentials. Every external integration defaults to its `mock` implementation, because
production credentials for Chapa, Telebirr and SMS all require a registered Ethiopian business.

## First run

```bash
nvm use
make setup     # install Python and Node dependencies, create .env from .env.example, install hooks
make up        # start the compose stack, wait for health, run migrations, seed the gazetteer
```

`make setup` is idempotent. Run it again after pulling changes that touch dependencies.

The Valhalla tiles are **not** built by `make up` — see [Routing tiles](#routing-tiles). Until they
exist the routing service returns an error, and the two-stage matcher's second stage is unavailable
while its PostGIS first stage still works.

## Make targets

| Target | What it does |
|---|---|
| `make setup` | Install dependencies, create `.env`, install git hooks |
| `make up` | Start the stack, migrate, seed |
| `make down` | Stop the stack, keeping volumes |
| `make verify` | **Run the gates CI runs.** Do this before opening a pull request |
| `make test` | Tests only, no linting |
| `make migrate` | Apply Alembic migrations to the local database |
| `make db-reset` | Drop, recreate, migrate, reseed |
| `make tiles` | Build the Valhalla routing tiles from the OSM Ethiopia extract |

`make verify` is the one that matters. It runs the same set as CI — see
[`docs/CI_GATES.md`](CI_GATES.md), including the six abro-specific gates in
[`scripts/gates/`](../scripts/gates/) — and it is far faster than waiting for a red build.

## Services

Started by `docker compose`, per [`docs/ARCHITECTURE.md`](ARCHITECTURE.md).

| Service | Port | Notes |
|---|---|---|
| PostgreSQL 16 + PostGIS | 5432 | `pg_trgm` and `unaccent` enabled by the first migration |
| Redis | 6379 | Cache, distributed locks, and the ARQ queue |
| Valhalla | 8002 | Routing, matrix and snapping. Needs built tiles |
| Photon | 2322 | Fuzzy place search, secondary to the curated gazetteer |
| `abro-api` | 8000 | FastAPI with reload. OpenAPI at `/docs` |
| ARQ worker | — | Scheduled and queued jobs |
| `abro-web` | 3000 | Next.js dev server |

The mobile client runs outside compose, via `npx expo start` in `abro-mobile/`.

## Routing tiles

The Ethiopia extract is roughly 139 MB from Geofabrik and the whole geo stack fits comfortably in
4 GB of RAM — see [ADR 0005](adr/0005-self-hosted-valhalla.md).

```bash
make tiles     # download the extract, build, then swap the tile directory atomically
```

Expect tens of minutes on the first build. It downloads to a staging directory and swaps only on
success, so an interrupted build leaves the previous tiles serving. Rebuild when you want fresher
OSM data; nothing in the application requires it routinely.

Do not derive travel-time estimates from OSM `surface` tags. 51% of Ethiopian arterial road
kilometres have no surface tag at all. Calibrate against observed trip durations instead.

## Resetting the database

```bash
make db-reset
```

Drops the local database, recreates it, runs every migration from scratch and reseeds the
gazetteer. Use it when a migration conflict leaves the schema in an unclear state — that is a
faster fix than hand-patching, and it also proves the migration chain still applies cleanly from
empty, which is what CI's drift gate checks.

Local only. It refuses to run against any host that is not localhost.

## Configuration

`.env` is created from `.env.example` by `make setup` and is never committed. Provider selection is
per integration:

```ini
PAYMENTS_PROVIDER=mock      # chapa | telebirr | mpesa | mock
OTP_PROVIDER=mock           # telegram | sms | mock
EKYC_PROVIDER=mock          # fayda | mock
PUSH_PROVIDER=mock          # expo | mock
```

`mock` is the default everywhere except staging and production. Production boots refuse to start
if any provider is still `mock`.

## When something is wrong

- **`make up` hangs on database health.** Usually a stale volume from an older schema. `make down`
  then `make db-reset`.
- **Routing returns errors, search still works.** Tiles are not built. Run `make tiles`.
- **Amharic search returns nothing for a spelling you expect to match.** Check the query goes
  through `am_normalize()`. The `amharic-search` gate exists for exactly this and catches it in CI.
- **A test passes locally and fails in CI.** CI uses ephemeral testcontainers with a clean
  database; a local pass often depends on seeded rows. Reproduce with `make db-reset && make test`.
