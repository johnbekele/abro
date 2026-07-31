# CI gates

Every gate here runs on each pull request unless noted. `make verify` runs the same set locally,
which is much faster than waiting for a red build. Jobs are **path-filtered** — changing only
`abro-api/` does not run the mobile suite.

---

## The six abro-specific gates

These matter most. Each catches a class of bug that passes human code review and fails in
production, and each exists because of something specific about this product or this market. If
you are tempted to delete one, read the "why" first.

### 1. `money-float`

Bans floating-point arithmetic on monetary values, and any money field typed as `float` — or
`number` where an integer is required. All amounts are integer santim.

*Why:* binary floating point cannot represent 0.1 exactly. A marketplace that mis-rounds a fee a
hundred thousand times has lost real money and can no longer reconcile its ledger.

### 2. `time-safety`

Bans naive `datetime`, `datetime.now()` and `datetime.utcnow()` in the backend. Bans Ethiopian
calendar and 6-hour-clock conversion anywhere outside `packages/@abro/time`.

*Why:* the Ethiopian day starts at dawn, so 09:00 EAT is spoken as "3:00 in the morning".
Duplicating that conversion across a server and two clients guarantees they eventually disagree,
and the symptom is an intermittent six-hour error on departure times — a stranded passenger and a
refund. See ADR 0007.

### 3. `i18n-parity`

The `en` and `am` catalogs must have identical key sets. No hardcoded user-facing strings in
components.

*Why:* a missing Amharic key renders as a raw key name to the majority of users, and nothing in a
normal test suite notices.

### 4. `amharic-search`

Gazetteer name queries must go through `am_normalize()`. Backed by a fixture suite of homophone
spelling pairs that must all match.

*Why:* `ሀ/ሐ/ኀ`, `ሰ/ሠ`, `አ/ዐ` and `ጸ/ፀ` are pronounced identically and spelled interchangeably. A
raw comparison silently returns nothing for a large share of real queries — and looks perfectly
fine when a developer tests it with their own spelling.

### 5. `geo-safety`

Bans `ST_DWithin` against a route without its `_ST_Expand(...) &&` companion predicate. Bans
corridor matching without the `f_dropoff > f_pickup` direction check.

*Why:* without the paired predicate the GiST index goes unused and the query degrades to a scan
over every trip — BlaBlaCar measured the pairing at 34×. Without the direction check, a passenger
travelling Adama→Addis matches a driver heading the opposite way. See ADR 0004.

### 6. `pii-logging`

Bans passing phone numbers, Fayda identifiers, OTP codes and payment references to the logger.

*Why:* logs are retained longer, shipped to more third parties, and read by more people than the
database is.

---

## Backend — `abro-api/**`

| Gate | Tool |
|---|---|
| Lint and format | `ruff check`, `ruff format --check` |
| Types | `mypy --strict` |
| Tests and coverage | `pytest` against a testcontainers PostGIS instance, 85% floor |
| Patch coverage | Codecov patch gate — new code held to a higher bar than the average |
| Migration drift | `alembic revision --autogenerate` must produce an empty diff |
| Unsafe migrations | `squawk` |
| Layering | `import-linter` — `api → services → repositories → models`, no reverse imports |
| Complexity | `xenon` |
| Security | `bandit`, `pip-audit` |

## API contract

`spectral` lints the spec, `oasdiff` fails breaking changes against `main`, `schemathesis` fuzzes
against it, and a drift check confirms the generated TypeScript client still matches.

Breaking changes fail the build. Mobile clients update slowly and some users stay on old builds
for months.

## Web — `abro-web/**`

ESLint with `eslint-plugin-boundaries` encoding the layering (`Component → Hook → Service → API
client`, no network calls in components, no `any`, component ≤150 lines), Prettier, `tsc --noEmit`
at **zero errors**, Vitest at 80%, `knip` for unused files and exports, `size-limit` bundle
budgets, Lighthouse CI thresholds, Playwright end-to-end with `axe` accessibility checks.

## Mobile — `abro-mobile/**`

`tsc --noEmit` at zero, ESLint and Prettier, Jest unit tests, `expo-doctor`, a prebuild check.
Maestro end-to-end and EAS preview builds run nightly rather than per-PR.

## Infrastructure

`pulumi preview` diff gate, `checkov` on IaC, `hadolint` on Dockerfiles, `actionlint` on workflows,
`yamllint`, `shellcheck`, Trivy image scanning, SBOM via `syft` attached to releases.

## Security

CodeQL, Semgrep, `gitleaks`, OSV-Scanner, Dependency Review, OpenSSF Scorecard, all actions pinned
by commit SHA, `harden-runner` on every job. All free because the repository is public.

## Hygiene

commitlint, semantic PR-title check, `markdownlint`, `lychee` link checking, license compliance,
and Danger.js — which requires a linked issue and flags source changes arriving without tests.

## Nightly

Mutation testing, load tests, the full end-to-end suite, and Maestro against device profiles that
match what people actually carry in Ethiopia: low-RAM Transsion handsets, not flagships.
