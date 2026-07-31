# Instructions for AI coding agents

Read this before touching anything. It is short because everything in it matters.

Human contributors should read it too — the invariants are not agent-specific.

---

## The one-issue rule

**One pull request closes exactly one issue.** Do not fix an unrelated bug you noticed, do not
refactor a neighbouring module, do not upgrade a dependency because it looked old. Open a new
issue instead and link it.

Read the *entire* issue before starting, including the escalation section. Issues here are
written to be sufficient: file paths, schemas, endpoint contracts, acceptance criteria and a test
plan are all specified. If something genuinely is not specified, that is a signal — see
"When to stop" below.

Before opening the PR, run `make verify`. It runs the same gates CI does, and it is much faster to
find a failure locally.

---

## Invariants

These are not style preferences. Each has an automated gate behind it, and each corresponds to a
class of bug that has cost real products real money.

### Money is integer santim

Every monetary amount is an integer count of santim (1 ETB = 100 santim). **No floats, anywhere,
for any reason.** Not in the database, not in a Pydantic schema, not in a TypeScript interface,
not in a test fixture.

Where a proportion must be applied — a service fee, a partial refund — use the money helpers.
Never do the arithmetic inline. Splitting an amount across parties uses the allocation helper,
which guarantees the parts sum back to the whole; rounding each part independently leaks value.

### The backend stores UTC and knows nothing about the Ethiopian calendar

All calendar and 6-hour-clock conversion lives in `packages/@abro/time` and nowhere else. The
backend uses timezone-aware UTC datetimes. `datetime.now()` and `datetime.utcnow()` are banned —
the first is machine-local, the second lies about being UTC.

Ethiopians count hours from dawn, so 09:00 EAT is spoken as "3:00 in the morning". A six-hour
error is a passenger left at a terminal and a refund. See ADR 0007.

### Every user-facing string exists in both `en` and `am`

No hardcoded strings in components. The i18n parity gate fails if the two catalogs' key sets
differ. Ge'ez numerals are fine for dates and wrong for money and seat counts.

### Amharic search goes through `am_normalize()`

`ሀ/ሐ/ኀ`, `ሰ/ሠ`, `አ/ዐ` and `ጸ/ፀ` are pronounced identically and Ethiopians spell them
interchangeably. A query that compares raw Amharic text will silently return nothing for a large
share of real users, and it will look like it works when you test it. Every gazetteer name query
goes through the normalisation function, and both Amharic and Latin transliteration are indexed.

### Corridor queries must be indexed and directional

Two rules, both enforced by a gate:

- `ST_DWithin` against a route must be paired with its `_ST_Expand(...) &&` companion predicate,
  or the GiST index is not used and the query degrades to a sequential scan over every trip.
- Corridor matching must include the `f_dropoff > f_pickup` direction check. Without it, a
  passenger travelling Adama→Addis matches a driver going the other way.

See ADR 0004.

### Never log PII

No phone numbers, Fayda identifiers, OTP codes, or payment references in logs. The logging
configuration redacts known keys and +251 number patterns as a backstop, but do not rely on it.

### Every external provider sits behind an interface with a mock

Payments, OTP, eKYC, push. A developer must be able to run and test the whole system with no
credentials, because production credentials require a registered Ethiopian business. `mock` is the
default everywhere except staging and production.

### API changes are additive

Mobile clients update slowly and some users will be on old builds for months. Do not remove or
repurpose a field. The `oasdiff` gate fails breaking changes.

### Migrations are real

Alembic from the first commit. Model changes without a matching migration fail the drift gate.
Destructive migrations fail the `squawk` gate. Do not work around either.

---

## When to stop and escalate

Apply the `needs-human` label, comment starting with `@johnbekele` explaining precisely what you
need, and move to another issue. **The run continues; you are not blocked, this one item is.**

Escalate, always, without attempting a workaround:

- **A missing secret or credential.** Say which variable, where to obtain it, and where it goes.
- **Anything destructive or hard to reverse** — dropping a column or table, deleting an endpoint,
  rewriting history, force-pushing, changing authentication semantics.
- **Spending money or creating an external account.**
- **A security judgement call** — loosening validation, widening data exposure, changing roles.
- **Anything touching the price cap, the anti-commercialisation monitor, or the ledger.** These
  are legal and financial infrastructure, not features. See ADR 0006.
- **Requirements genuinely ambiguous between materially different designs.** Do not pick one and
  hope. Two plausible readings of an issue means the issue is wrong.
- **CI still red after three fix attempts on the same PR.**

Never merge with failing or pending required checks. Never bypass branch protection. Never commit
a secret. Never touch production.

---

## Conventions

- **Commits** follow Conventional Commits. The PR title is linted the same way.
- **Layering** is enforced by `import-linter` on the backend and ESLint boundaries on the clients:
  `api → services → repositories → models`, and `Component → Hook → Service → API client`.
  Components never call the network. Server state never lives in `useState`.
- **Size limits**, carried over from the predecessor project and encoded in ESLint: components
  ≤150 lines, hooks ≤100, services ≤200. A file over the limit is a refactoring signal.
- **No `any`.** No `# type: ignore` without a comment explaining why.
- **Vocabulary** comes from `docs/DOMAIN_GLOSSARY.md`. Use "trip", not "ride". Use "contribution",
  not "fare" — that one is a legal distinction, not a stylistic one.
- **Comments** explain constraints the code cannot express. Do not narrate what the next line
  does, and do not explain your change to the reviewer in a comment; that belongs in the PR.

## Where to look things up

| Question | File |
|---|---|
| What are we building and why? | `docs/PRODUCT_CONTEXT.md` |
| How is the system shaped? | `docs/ARCHITECTURE.md` |
| What does this word mean? | `docs/DOMAIN_GLOSSARY.md` |
| Why was this decided? | `docs/adr/` |
| What will CI check? | `docs/CI_GATES.md` |
| How do I run it? | `docs/RUNBOOK.md` |
