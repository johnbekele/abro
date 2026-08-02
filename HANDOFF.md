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

> Read `HANDOFF.md`. **The backlog is complete — 115 issues, #6–#120, across all five
> milestones**, every one labelled `ready` + `autopilot` and created in dependency order, and all
> of them on the project board. One thing remains before an unattended run: set `CODECOV_TOKEN`,
> or the first backend pull request goes red on #11. Everything else is now an issue, so the next
> session is the first one that writes application code — pick up #6 and work the pipeline.

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

### Done since the last session

- **Branch protection** on `main`. Requires `abro gates`, `workflow and shell lint`, `markdown`,
  `gitleaks` and `semgrep` — the five that run on every pull request regardless of path — plus
  linear history, up-to-date branches, conversation resolution, and a pull request for every
  change. See "Branch protection" below for the two judgement calls in that configuration.
- **The full label taxonomy and all five milestones**, created by a scripted `gh` run. The six
  unused stock labels are deleted.
- **`M0 Foundations` is fully specified: 25 issues, #6–#30**, all labelled `ready` + `autopilot`,
  created in dependency order so each `Blocked by #N` cites an issue that already exists.

### Done in the session after that

**The whole `M1`–`M4` backlog. 115 issues in total, #6–#120, no gaps**, every one carrying a
milestone and both the `ready` and `autopilot` labels, every `Blocked by #N` pointing backwards at
an issue that already existed when it was written.

| Milestone | Issues | Range |
|---|---|---|
| `M0 Foundations` | 25 | #6–#30 |
| `M1 Rides & Search` | 33 | #31–#62, plus #83 |
| `M2 Money` | 20 | #63–#82 |
| `M3 Trust & Comms` | 20 | #84–#103 |
| `M4 Admin CRM & Launch` | 17 | #104–#120 |

By discipline: backend 80, web 24, mobile 20, security 17, data 14, devops 10, infra 6, QA 5,
docs 3, design 1. Labels overlap, so those do not sum to 115.

**Two ordering decisions worth knowing about**, because both look like mistakes otherwise:

- **The user model (#83) sits in `M1`, not `M3`.** `trip.driver_id` is a foreign key to it, so the
  table has to exist before anything in `M1 Rides & Search` can be built. The rest of identity —
  OTP, sessions, Fayda — stayed in `M3` where it belongs.
- **Pricing and the price cap (#38) moved from `M2` into `M1`.** Publishing a trip validates the
  contribution against the cap, and shipping publish before the cap opens a window in which trips
  can be created that ADR 0006 forbids. The legal spine cannot be retrofitted.

Consolidated during the run: `m3b-passenger-profile` folded into #97, which covers both sides.
Split out during the run: an Android release pipeline (#119), which nothing else covered and
without which there is no way to get the app onto a phone.

### The project board

<https://github.com/users/johnbekele/projects/12> — public, linked to the repo, with all 115
issues on it. Three single-select fields, `Discipline`, `Priority` and `Size`, are populated from
the labels. Six views: **By milestone**, **By discipline**, **Autopilot queue**, **In flight**,
**Needs a human** and **M0 Foundations**.

Two things about it worth knowing.

**Group-by is not settable through the API.** Neither `createProjectV2View` nor
`updateProjectV2View` accepts it, so "By milestone" and "By discipline" have the right fields and
filters but need their grouping set once in the UI. One click each.

**`Discipline` is single-valued and `area:` labels are not.** An issue labelled both
`area:security` and `area:backend` lands under Backend; the precedence is mobile, web, backend,
infra, QA, security, data, design. That is deliberate — security is a dimension of backend work
here rather than a separate person's queue — but it leaves the `Security` and `Design & Docs`
options empty even though 17 and 3 issues carry those labels. Filter on the label, not the field,
for those two.

`.backlog/board.py` and `.backlog/views.py` rebuild the whole thing. Both are idempotent, so
re-running after adding issues is safe.

### Remaining

**1. Set `CODECOV_TOKEN`** before an agent starts. See the known gaps below: without it the first
backend pull request goes red, and it is the most likely place for an unattended run to stall.

**2. Delete `HANDOFF.md`** and remove its reference from `README.md`. This is step 5 of the `M0`
exit check, issue #30, rather than a loose task — leave it to that issue.

### How the backlog was built, if any of it needs redoing

- Bodies live in `.backlog/<slug>.md` (`.backlog/` is in `.gitignore`, so none of this is
  committed).
- `.backlog/create.py <batch>.json` creates them, substituting a `{{slug}}` token with the number
  GitHub assigned to that issue and recording the mapping in `.backlog/numbers.json`, so a partial
  run resumes without opening duplicates. Only tokens matching `b<digit>-…` or `m<digit><letter>-…`
  are substituted, which is what stops an i18n `{{count}}` example being mangled — an unknown token
  of that shape is a typo and fails loudly.
- Work milestone by milestone, batch by epic, five to nine per batch. Do **not** try to hold a
  whole milestone in context at once.
- Creation order **is** the dependency mechanism: stage 2 of the autopilot pipeline picks the
  oldest `ready` issue.
- `gh` fails a creation with an unknown label rather than warning. `mod:booking` is singular and
  there is no `mod:safety` — it is `mod:trust`. Both cost a failed batch during the run.

### Branch protection, and two decisions inside it

**Required reviews are set to zero, and CODEOWNERS review is off.** The original plan called for
code-owner review, but `@johnbekele` is the only code owner and GitHub forbids approving your own
pull request. An agent running as that account could open a pull request and never be able to
merge it, which deadlocks the whole pipeline. A pull request is still required and the five checks
must still pass, so nothing red can land — what is not enforced is a second pair of eyes, and
with a single maintainer there was never going to be one.

**`enforce_admins` is off**, so the repository owner can still push directly to `main`. Turn it on
once the pipeline is running unattended.

**The per-project checks are not required yet.** `CI backend`, `CI web` and `CI mobile` are
path-filtered, and a workflow that never runs never reports — a required check that never reports
blocks every merge forever. Issue #30 adds them once all three directories exist.

### Known gaps, deliberate

The first two used to be open questions and are now issues, which is the right place for them.

- **Dependabot covers `github-actions` and root `npm` only.** A configured directory that does not
  exist is a Dependabot error, so the `uv` and Docker ecosystems wait until those directories are
  created. Issue #29.
- **Prettier is not yet in CI.** `npm ci` needs a lockfile and there is none. Issue #6 generates it
  and wires `format:check` into the `markdown` job of `ci.yml` — inside that job rather than as a
  new one, because a new job produces a check name that branch protection does not require.
- **`CODECOV_TOKEN` is unset, and `ci-backend.yml` sets `fail_ci_if_error: true`.** The `tests` job
  therefore goes red the first time it runs, on issue #11. That issue treats it as a missing-secret
  escalation rather than something to disable, which is correct — but it is the most likely
  point at which the M0 run stalls, so consider setting the secret before an agent starts.
- **Deploy workflows have no credentials.** Both skip with a `::notice::` rather than failing.
  They need `AWS_ROLE_ARN` and `PULUMI_ACCESS_TOKEN` set on the `staging` and `production`
  environments. Obtaining them is a human task — see the escalation rules in `AGENTS.md`.
- **No autopilot runner exists in this repository.** `AUTOPILOT.md` describes the three-stage
  pipeline and its last line puts the runner outside the repo; nothing in `.github/workflows/`
  reads the `autopilot` label. The labels are the interface, and they stay inert until something
  is pointed at them.
- **Dependabot opens pull requests already.** The dependency graph, vulnerability alerts and
  Dependabot security updates are all enabled, so `dependency review` works. Bot pull requests
  skip `commitlint` and `danger` deliberately — machine-written commit messages cannot satisfy
  the commit conventions, and there is no issue for a bot to link.

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

## Governance taxonomy

Created. Recorded here because the `M1`–`M4` issues have to label themselves from the same set,
and `gh` fails a creation with an unknown label rather than warning.

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

**Backlog shape**

Planned at roughly 120; landed at 115. The estimate was close enough that the difference is
consolidation rather than omission — see the per-milestone table above for what was actually
created.

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

- **The `project` scope is an interactive device flow.** It has been granted, but a fresh machine
  or a re-authentication will drop it, and `gh auth refresh -s project` cannot be run unattended.
- **Cursor approval prompts:** open `~/personal/abro` as the workspace folder, otherwise every
  file write is treated as outside the workspace and needs manual approval.
- **`main` now requires a pull request.** Admins are exempt, so a direct push still works for the
  repo owner, but do not assume it for an agent.
- **Issue numbers 1–5 are Dependabot pull requests**, not issues. The backlog starts at #6.
