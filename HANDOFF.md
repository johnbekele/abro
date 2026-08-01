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

### Start here in a new session

Open `~/personal/abro` as the Cursor workspace folder first, or every write needs manual approval.
Then give the agent this:

> Read `HANDOFF.md`. Continue from the "Remaining" list, starting at the first item that is not
> assigned to M0. Do not write application code — this repo intentionally contains none. What is
> left is the label taxonomy, the issue backlog, the project board and branch protection.

### Done

- Repo created, **public**, cloned to `~/personal/abro`, default branch `main`, git identity set
  repo-locally. First commit pushed.
- Root files: `README.md`, `LICENSE`, `.gitignore`, `.editorconfig`, `.nvmrc`, `package.json`,
  `commitlint.config.mjs`, `.markdownlint.json`, `.yamllint.yml`.
- `AGENTS.md` — the invariants and escalation rules. **The most important file in the repo.**
- `CONTRIBUTING.md`, `AUTOPILOT.md`.
- `docs/PRODUCT_CONTEXT.md`, `docs/ARCHITECTURE.md`, `docs/DOMAIN_GLOSSARY.md`,
  `docs/CI_GATES.md`, `docs/RUNBOOK.md`.
- `docs/adr/0001` through `docs/adr/0010` — all ten written.
- **`scripts/gates/`** — the six custom gates, plus `run_all.py` and `test_gates.py`. Each exits 0
  when the tree it inspects is absent, and the fixture tests prove each one still fires. Run them
  with `python scripts/gates/run_all.py`.
- **`.github/`** — `ci.yml` (always-on: the six gates, actionlint, yamllint, shellcheck,
  markdownlint) plus `ci-backend.yml`, `ci-web.yml` and `ci-mobile.yml`, each filtered at workflow
  level to its own directory. Also `security.yml`, `codeql.yml`, `scorecard.yml`, `pr-hygiene.yml`,
  `nightly.yml`, `infra.yml`, `deploy-staging.yml`, `deploy-prod.yml`, the three issue templates
  plus `config.yml`, `PULL_REQUEST_TEMPLATE.md`, `CODEOWNERS`, `dependabot.yml`, `dangerfile.ts`.
  Every action is pinned by commit SHA. `actionlint`, `yamllint` and `markdownlint` were run
  locally and are clean.

### Remaining, in order

**1. Root `Makefile` and `docker-compose.yml`.** These were written once and deliberately removed
because they referenced directories that do not exist. Recreate them **as part of the M0
scaffolding issues**, not now — but `README.md`, `CONTRIBUTING.md` and `docs/RUNBOOK.md` already
reference `make setup`, `make up`, `make verify` and the rest, so the M0 issues must deliver those
exact targets. `make verify` must run `python scripts/gates/run_all.py`.

**2. Labels and milestones** via `gh`. Taxonomy below. Do it in one scripted run. The issue
templates already apply `type:feature`, `type:bug` and `type:spike`, and `dependabot.yml` applies
`area:devops` and `type:chore`, so those five must exist or they are silently dropped.

**3. The backlog: ~120 issues.** The main deliverable. Approach that works:

- Write bodies to `.backlog/NNN-slug.md` (`.backlog/` is already in `.gitignore`).
- Create with `gh issue create --title ... --body-file ... --label ... --milestone ...`.
- Work milestone by milestone so a partial run still leaves a coherent backlog.
- Do **not** try to hold all 120 in context at once. Batch by epic, roughly 8–10 per batch.
- Every issue uses the template below, no exceptions.

**4. GitHub Project board.** Run `gh auth refresh -s project` first — the current token lacks the
scope. Then create the board and add every issue, with views grouped by discipline and milestone.

**5. Branch protection** on `main` once the workflows have run at least once (required checks
cannot be named until GitHub has seen them). Require the `abro gates`, `workflow and shell lint`
and `markdown` checks from `ci.yml`, plus `gitleaks`, linear history, and CODEOWNERS review. The
per-project CI checks cannot be required while their directories are absent — a path-filtered
workflow never reports, so a required check that never runs blocks every merge. Add each one as
its project lands.

**6. Delete `HANDOFF.md`** and remove its reference from `README.md`.

### Known gaps, deliberate

- **Dependabot covers `github-actions` and root `npm` only.** A configured directory that does not
  exist is a Dependabot error, so the `uv` and Docker ecosystems get added by the M0 issues that
  create `abro-api/` and the Dockerfiles.
- **Prettier is not yet in CI.** `npm ci` needs a lockfile and there is none until M0 installs
  dependencies. `package.json` already declares the `format:check` script; wire it into `ci.yml`
  with the M0 tooling issue.
- **Deploy workflows have no credentials.** Both skip with a `::notice::` rather than failing.
  They need `AWS_ROLE_ARN` and `PULUMI_ACCESS_TOKEN` set on the `staging` and `production`
  environments. Obtaining them is a human task — see the escalation rules in `AGENTS.md`.
- **Dependency review needs the dependency graph enabled.** The `dependency review` job in
  `security.yml` fails with "not supported on this repository" until it is switched on under
  Settings → Code security. It only runs on pull requests, so `main` is unaffected meanwhile.
  Enable it together with Dependabot security updates, which is also currently off.

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

- BlaBlaCar's two-stage algorithm, the `_ST_Expand(...) &&` + `ST_DWithin` index pairing worth
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

## CI gates

Built. `docs/CI_GATES.md` is the reference and `scripts/gates/` is the implementation of the six
custom ones. Two things to carry into the backlog:

**Each per-project workflow is a promise the M0 issues must keep.** `ci-backend.yml` invokes
`uv sync`, `alembic upgrade head`, `lint-imports`, `app.cli export-openapi` and
`npm run generate:api-client`; `ci-web.yml` and `ci-mobile.yml` invoke workspace `lint`,
`typecheck`, `test` and `build` scripts. An M0 issue that scaffolds a project must deliver the
commands its workflow already calls, or the first pull request in that directory goes red.

**The custom gates are static checks, not a substitute for design.** They catch the mistake after
it is written. The issue bodies still have to say what correct looks like.

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
