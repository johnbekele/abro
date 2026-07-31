# Session handoff

**Read this first if you are picking up this repository in a new session.** It records what has
been done, what is left, and every decision already made so none of it gets relitigated or
re-researched.

Delete this file once the backlog is fully created and the repo is handed to developers.

---

## What this repo is

`abro` (አብሮ, "together") — a BlaBlaCar-style **intercity carpooling platform for Ethiopia**.
Public repo: <https://github.com/johnbekele/abro>. Owner `johnbekele`, commit email
`yohansdemisie@gmail.com` (set repo-locally already).

The current task is **not to build the product**. It is to leave the repository in a state where
a developer or an AI agent can pick up a single issue and ship it. That means: governance,
CI gates, and a backlog of very detailed issues. No application code.

---

## Status

### Done

- Repo created, public, cloned to `~/personal/abro`. Git identity set repo-locally.
- `README.md`, `LICENSE`, `.gitignore`, `.editorconfig`, `.nvmrc`, root `package.json`.
- `docs/PRODUCT_CONTEXT.md` — the product, business rules, legal position, out-of-scope list.
- `docs/ARCHITECTURE.md` — intended system shape, layering, data model outline.
- `docs/DOMAIN_GLOSSARY.md` — vocabulary. Use these words in code.
- `docs/adr/0001-monorepo-and-stack.md`.

### Remaining, in order

1. **ADRs 0002–0010** (see list below). Short, ~40 lines each.
2. **`AGENTS.md`** — invariants and escalation rules for AI agents. High value; write it well.
3. **`CONTRIBUTING.md`**, **`docs/CI_GATES.md`**, **`docs/RUNBOOK.md`**.
4. **`AUTOPILOT.md`** — adapted from the Pokojowo playbook (see "Prior art" below).
5. **`.github/`** — workflows, issue templates, PR template, CODEOWNERS, renovate config.
6. **`scripts/gates/`** — the six custom gate scripts.
7. **Labels and milestones** via `gh`.
8. **The backlog: ~120 issues.** This is the main deliverable.
9. **GitHub Project board** — needs `gh auth refresh -s project` first; the token lacks the scope.

### ADRs still to write

| File | Subject |
|---|---|
| `0002-deposit-not-escrow.md` | Deposit online, balance in cash. NBE licensing makes escrow illegal for us. |
| `0003-cancellation-and-refund-tiers.md` | The four-tier matrix, 30-min grace, 15-min no-show clock. |
| `0004-postgis-two-stage-matching.md` | Gross match in PostGIS then Valhalla; the `_ST_Expand` index pairing; direction via `ST_LineLocatePoint`; no materialized view. |
| `0005-self-hosted-valhalla.md` | OSM + Valhalla + Photon + PMTiles. Google forbidden by licence. |
| `0006-price-cap-as-legal-spine.md` | 80–120% band as the Code 2 legal defence. |
| `0007-ethiopian-time-in-typescript.md` | All calendar/clock logic in `@abro/time`; backend pure UTC. |
| `0008-telegram-first-otp.md` | Telegram Gateway primary, local SMS fallback, mock in dev. |
| `0009-curated-gazetteer.md` | Curated meeting points instead of geocoding. |
| `0010-offline-first-clients.md` | Shutdowns and dark highways make offline a requirement. |

---

## Locked decisions — do not reopen these

Settled with the repo owner. Changing any of them means redoing large parts of the backlog.

| Decision | Value |
|---|---|
| Name | `abro` |
| Visibility | **Public** — chosen for unlimited free Actions minutes and free CodeQL/Dependabot/Scorecard |
| Structure | Monorepo |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2 + Alembic, **PostgreSQL + PostGIS**, Redis, ARQ |
| Web | Next.js 15 App Router |
| Mobile | Expo SDK 54, expo-router, React Query, Zustand, NativeWind |
| Infra | Pulumi (Python), AWS |
| Money flow | **Deposit online + balance in cash**, not escrow |
| Payments | Chapa first, M-Pesa second, Telebirr collection-only. **Stripe is unavailable in Ethiopia** |
| Geo | Self-hosted Valhalla + Photon + PMTiles over OSM Ethiopia. **Never Google** |
| OTP | Telegram Gateway primary, local SMS fallback |
| Providers | Everything behind an interface with a `mock` default, so no account is needed to develop |
| Cost posture | Free/self-hosted for development; paid providers only at beta |
| TS baseline | **Zero** `tsc` errors, unlike Pokojowo's grandfathered allowance of three |

---

## Research findings the issues depend on

Gathered from five research passes. These are the non-obvious facts that make abro different from
a generic marketplace. Cite them in issue bodies so implementers understand *why*.

**Legal and money**

- NBE directive ONPS/01/2020: holding e-money float needs ETB 100M capital (May 2025), 10+
  shareholders, none >20%, float in bank trust. Escrow is therefore out of reach.
- Only 21% of Ethiopian adults made a digital payment last year; 16% rurally.
- BlaBlaCar's Poland launch (fee online, contribution in cash) cut no-shows by ~90%.
- Chapa: only Ethiopian PSP with public self-serve charge + partial refund + split + payout, free
  sandbox, no merchant account needed. Fee disputed — official page says 2.5%, independent
  sources 1.5%. **Confirm in writing before modelling unit economics.**
- Telebirr: 60.6M customers, but **no programmatic refunds**, T+1 settlement, USSD push only.
- M-Pesa Ethiopia: only real B2C disbursement API, but small (5.2M 90-day-active).
- Commission anchors: Ride 12%, Feres 8%.
- Proclamation 608/2010 + Code 2 plates: the existential legal risk. ZayRide has had 15+ vehicles
  impounded lobbying on it.

**Matching and geo**

- BlaBlaCar's two-stage algorithm, the `_ST_Expand(...) && ` + `ST_DWithin` index pairing worth
  34×, and their materialized-view refresh taking 2–3 minutes and consuming the database.
- "Boost" partial-route rides: **45% of displayed results, 30% of all bookings.** Core, not v2.
- Google's licence forbids persisting route geometry — disqualifying, regardless of price.
- Ethiopia OSM extract is ~139 MB; whole geo stack fits a 4 GB VPS at $12–24/month.
- 51% of Ethiopian arterial road-km lack OSM `surface` tags — do not trust them for ETAs.
- No street addressing. eDAS is a Bishoftu-only pilot. People navigate by landmark.
- Addis–Adama Expressway is access-controlled: **mid-route pickups are physically impossible**,
  and tolls are a fare line item.

**Localization**

- The 6-hour dawn-offset clock: 09:00 EAT is spoken as "3:00 in the morning". A six-hour error is
  a missed trip. `kenat` is the recommended library; keep it all in TypeScript.
- Ethiopian calendar: 13 months, Pagumē of 5–6 days, ~7–8 years behind Gregorian.
- Amharic homophones `ሀ/ሐ/ኀ`, `ሰ/ሠ`, `አ/ዐ`, `ጸ/ፀ` are spelled interchangeably — search needs
  `am_normalize()` + `pg_trgm`, and both Amharic and Latin transliteration indexed.
- Bundle Noto Sans Ethiopic; do not rely on system font fallback on low-end devices.

**Channels and connectivity**

- Telegram beat WhatsApp in Ethiopia in a 27-country study (only other exception: Algeria); 97.8%
  usage among surveyed students. Telegram Gateway OTP $0.01 with a **free `checkSendAbility`
  pre-check**, vs Twilio at $0.3425 per SMS to +251.
- **Ethio Telecom blocks unregistered SMS sender IDs from 8 October 2026.** Registration takes
  1–2 weeks and needs a VAT number. Launch-blocking, not development-blocking.
- Production SMS credentials require a registered Ethiopian business with a current trade licence.
- 4G: 82% population coverage but only **36% geographic** — the highway between towns is dark.
- Ethiopia has shut down the internet 26+ times since 2016; Amhara saw ~345 days. Bahir Dar,
  Gondar and Mekelle are all launch corridors.
- Transsion (Tecno, Infinix, itel) dominates; aggressive battery killers, so push is best-effort.
  They ship Google Play Services, so FCM works and HMS is unnecessary.
- Ethiopia is ~96% Android. Smartphone penetration 45%.
- Email is weak — phone is the identity, email optional.

---

## The issue template

Every issue uses this. The rigidity is the point: it is what makes an agent's output predictable.

```markdown
## Context
Why this exists. Cite the business rule or research finding behind it.

## Scope
**In scope:** ...
**Out of scope:** ... (say what a reasonable person might assume is included but is not)

## Technical design
Exact file paths to create or modify. Function signatures, SQLAlchemy models, Pydantic
schemas, endpoint contracts with status codes and error bodies.

## Data model and migration
Table DDL, indexes (GiST for geometry, GIN for trigram), the Alembic revision expected.

## Acceptance criteria
1. Numbered, individually testable statements.

## Test plan
Named test files and the specific cases each must cover, including edge cases.

## CI gates
Which gates must be green. Any new gate this issue adds.

## Dependencies
Blocked by #N. Blocks #M.

## Escalation
Stop and apply `needs-human` if: ...
```

---

## Governance taxonomy to create

**Labels**

- `area:` backend, web, mobile, infra, devops, qa, security, data, design, docs
- `mod:` identity, rides, search, booking, payments, geo, chat, trust, notifications, i18n,
  admin, growth
- `type:` feature, bug, chore, spike, epic
- Priority `P0`–`P3`; size `size:S`, `size:M`, `size:L`, `size:XL`
- Autopilot workflow: `autopilot`, `ready`, `changes-requested`, `needs-human`, `autopilot-done`,
  `blocked`

**Milestones**

`M0 Foundations` → `M1 Rides & Search` → `M2 Money` → `M3 Trust & Comms` →
`M4 Admin CRM & Launch`

**Backlog shape (~120 issues)**

Backend ≈48, web ≈20, mobile ≈22, infra/devops ≈13, QA ≈8, security ≈8, data ≈5, design/docs ≈6.

---

## CI gates to build

Path-filtered `ci.yml` plus `security.yml`, `codeql.yml`, `scorecard.yml`, `pr-hygiene.yml`,
`nightly.yml`, `infra.yml`, `deploy-staging.yml`, `deploy-prod.yml`.

Standard gates: ruff, mypy --strict, pytest at 85% coverage with Codecov patch gate, Alembic
drift, squawk, import-linter, xenon, bandit, pip-audit; OpenAPI spectral + oasdiff + client-drift;
ESLint with boundaries, Prettier, tsc at zero, Vitest 80%, knip, size-limit, Lighthouse,
Playwright + axe; expo-doctor, Maestro nightly; pulumi preview, checkov, hadolint, actionlint,
yamllint, shellcheck, Trivy, syft SBOM; CodeQL, Semgrep, gitleaks, OSV, Dependency Review,
Scorecard, harden-runner; commitlint, semantic PR titles, markdownlint, lychee, Danger.js.

**Six custom gates unique to abro** — these are the differentiator, so build them properly:

1. **money-float** — bans float arithmetic on money; forces integer santim.
2. **time-safety** — bans naive `datetime` and bare `datetime.now()`; bans any Ethiopian calendar
   or 6-hour-clock conversion outside `packages/@abro/time`.
3. **i18n-parity** — `en` and `am` catalogs must have identical key sets; no hardcoded strings.
4. **amharic-search** — gazetteer name queries must go through `am_normalize()`; fixture suite of
   homophone spelling pairs.
5. **geo-safety** — bans `ST_DWithin` on route geometry without its `_ST_Expand(...) &&`
   companion; bans corridor matching without the `f_dropoff > f_pickup` direction check.
6. **pii-logging** — bans logging phone numbers, Fayda IDs, payment references.

---

## Prior art worth reading

The sibling repo `~/personal/pokojowo-web-project` (also `johnbekele`) is the predecessor.

- **`AUTOPILOT.md`** — the three-stage headless agent pipeline (plan → implement → review) driven
  by the `autopilot`/`ready`/`changes-requested`/`needs-human` labels, where the implementer opens
  PRs and only the reviewer merges. `abro`'s `AUTOPILOT.md` adapts this.
- **`CLAUDE.md`** — the Archyra frontend guardrails (component ≤150 lines, hook ≤100, service
  ≤200, no fetch in components, no `any`, React Query for server state). Carry these forward; the
  ESLint boundaries config should encode them.
- **`.github/workflows/ci.yml`** — the three-job baseline abro expands on.

What *not* to copy from it: MongoDB, the absence of migrations, `BackgroundTasks` instead of a
real worker, no structured logging, no staging environment, and the `tsc` error baseline of 3.

---

## Practical gotchas

- **`gh` token lacks the `project` scope.** Run `gh auth refresh -s project` before attempting the
  Project board. Everything else works with the current token.
- **Cursor approval prompts:** open `~/personal/abro` as the workspace folder, otherwise every
  file write is treated as outside the workspace and needs manual approval.
- Nothing has been committed or pushed yet beyond the initial repo creation — check `git status`.
