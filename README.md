# abro (አብሮ)

**Intercity carpooling for Ethiopia.** Share the ride, share the cost.

`abro` means "together" in Amharic. Drivers already making a long trip — Addis Ababa to
Bahir Dar, Adama, Hawassa, Dire Dawa — publish their empty seats. Passengers travelling the
same corridor book one. The passenger pays a small deposit online and the balance in cash at
pickup. The platform takes a service fee and nothing else.

This is a cost-sharing marketplace, not a transport company. We never dispatch a driver, never
set a fare above the cost-sharing cap, and never own a vehicle. That distinction is load-bearing
— see [ADR 0006](docs/adr/0006-price-cap-as-legal-spine.md).

---

## Status: pre-code

The repository is set up and the backlog is fully specified. **No application code exists yet.**
Every directory below is created by its own issue.

If you are picking this up, start here:

1. [`docs/PRODUCT_CONTEXT.md`](docs/PRODUCT_CONTEXT.md) — what we are building and the business
   rules behind it.
2. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — the intended shape of the system.
3. [`docs/adr/`](docs/adr/) — the decisions that are already made, and why. Do not relitigate
   these in a pull request; open an issue instead.
4. [The open issues](https://github.com/johnbekele/abro/issues?q=is%3Aissue+is%3Aopen+label%3Aready)
   labelled `ready` — pick one, and read it fully before starting.

Work through the `M0 Foundations` milestone first. It builds the scaffolding everything else
depends on.

## Planned layout

| Directory | What it will be | Created by |
|---|---|---|
| `abro-api/` | FastAPI backend. Python 3.12, SQLAlchemy 2, Alembic, PostgreSQL + PostGIS, Redis, ARQ. | `M0` |
| `abro-web/` | Next.js 15 App Router. Passenger web, admin CRM, SEO route-pair pages. | `M0` |
| `abro-mobile/` | Expo SDK 54. The primary client — Ethiopia is ~96% Android. | `M0` |
| `abro-routing/` | Self-hosted Valhalla, Photon, and the PMTiles pipeline over an OSM Ethiopia extract. | `M1` |
| `abro-infra/` | Pulumi (Python) on AWS. Staging and production stacks. | `M0` |
| `packages/` | Shared TypeScript: generated API client, `@abro/time`, i18n catalogs. | `M0` |
| `docs/` | Product context, architecture, glossary, runbook, ADRs. | done |

## Contributing

Every change lands through a pull request that closes exactly one issue and passes the gate
pipeline in [`docs/CI_GATES.md`](docs/CI_GATES.md). Read [`CONTRIBUTING.md`](CONTRIBUTING.md)
first.

**If you are an AI coding agent, read [`AGENTS.md`](AGENTS.md) before anything else.** It lists
the invariants that are not negotiable and the conditions under which you must stop and escalate
to a human rather than guess.

## Ten things about this project that will surprise you

These are the constraints Ethiopia imposes that most codebases do not have. Each one has an
automated gate behind it, because each is the kind of mistake that passes code review and fails
in production.

1. **Ethiopians tell the time differently.** The clock starts at dawn, so 09:00 EAT is spoken as
   "3:00 in the morning". A six-hour error is a missed trip and a refund. All calendar and clock
   conversion lives in `@abro/time`; the backend stores UTC and contains no calendar code at all.
2. **The calendar has thirteen months** and runs seven to eight years behind the Gregorian one.
3. **There are no street addresses.** People navigate by landmark. We ship a curated gazetteer
   of verified pickup points instead of relying on a geocoder.
4. **Several Amharic letters are pronounced identically** and spelled interchangeably, so `ሰላም`
   and `ሠላም` are the same word to a user but not to Postgres. Search goes through
   `am_normalize()` or it silently returns nothing.
5. **Money is never a float.** Every amount is an integer count of santim.
6. **We cannot legally hold your money.** Escrow is a ledger entry plus a balance at a licensed
   payment provider, never a bank account in our name.
7. **The internet goes away.** Ethiopia has shut it down 26+ times since 2016, sometimes for
   months, in exactly the regions we serve. The app has to work offline.
8. **The highway is dark.** 4G reaches 82% of the population but only 36% of the land area, so
   location tracking buffers and forwards rather than streaming.
9. **Push notifications are best-effort.** Transsion phones dominate here and kill background
   apps aggressively. Anything that matters also goes out over Telegram or SMS.
10. **Telegram beats email and WhatsApp**, by a wide margin, for very nearly everything.

## License

[MIT](LICENSE)
