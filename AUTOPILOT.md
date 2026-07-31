# abro autopilot playbook

A staged, headless agent pipeline that turns issues into merged pull requests. Adapted from the
Pokojowo playbook, which has been running daily in production.

| Stage | Job | Merges? |
|---|---|---|
| 1. Plan | Turn vague `autopilot` idea issues into detailed `ready` child issues. Never writes code. Skipped when there are no unplanned ideas. | No |
| 2. Implement | Rework `changes-requested` PRs, otherwise ship the oldest `ready` issue: branch `auto/<n>-<slug>`, full local gate battery, open a PR. Skipped when the queue is empty. | **Never** |
| 3. Review | Critically review every open `autopilot` PR, wait for CI, merge the green and clean ones, send problems back with `changes-requested`. Always runs. | Yes, only this stage |

**The separation is deliberate.** The implementer never merges its own work, only the reviewer has
merge authority, and branch protection makes merging a red build impossible for both of them.

## Issue lifecycle

```text
You open an issue and label it `autopilot` — however vague.
  └─ Stage 1 posts a plan, splits it into child issues labelled `ready` + `autopilot`,
     and marks the parent `autopilot-done`.
       └─ Stage 2 implements one child per run and opens a PR.
            └─ Stage 3 reviews and merges → issue closed, labelled `autopilot-done`
                 └─ or `changes-requested` → Stage 2 reworks it on the next run.
```

Already well specified? Label it `ready` + `autopilot` directly and Stage 2 picks it up next run.
Pause anything by labelling it `needs-human`.

## Escalation

Escalation means the `needs-human` label plus a comment beginning `@johnbekele`, which triggers a
GitHub notification. **The run always continues with other work** — one blocked item does not stop
the pipeline.

The full escalation list lives in [`AGENTS.md`](AGENTS.md) and applies to every stage. The
abro-specific additions worth repeating here:

- **Anything touching the price cap, the anti-commercialisation monitor, or the ledger.** These
  are legal and financial infrastructure. See ADR 0006.
- **Anything requiring a real provider credential.** Production SMS, Chapa merchant onboarding and
  Telebirr all need a registered Ethiopian business. Use the `mock` provider and escalate rather
  than trying to obtain access.
- **Any change to how a departure time is computed or displayed.** Ethiopian clock errors are
  six hours wide and easy to introduce.

## Project invariants for every stage

Beyond the general rules in `AGENTS.md`:

- Money is integer santim. Never a float, anywhere.
- The backend stores UTC and contains no Ethiopian calendar code. Conversion lives only in
  `packages/@abro/time`.
- Every user-facing string exists in both `en` and `am`.
- Gazetteer name queries go through `am_normalize()`.
- Corridor queries pair `ST_DWithin` with `_ST_Expand(...) &&` and include the
  `f_dropoff > f_pickup` direction check.
- API changes are additive — mobile clients update slowly.
- Model changes ship with an Alembic migration.
- Every external provider stays behind its interface, with `mock` as the default.

## Hard safety rules

- Never merge with red or pending required checks. Never bypass branch protection.
- Never commit a secret. `.env` stays untracked.
- Never touch production deployments or production data.
- Never create external accounts, spend money, rotate credentials, or delete external resources.
- Never run destructive database operations outside the local development database.

## Gate battery before any PR

`make verify` — the same set CI runs. See [`docs/CI_GATES.md`](docs/CI_GATES.md) for the full
list, including the six abro-specific gates that catch this product's characteristic bugs.

## Ops

- **Required checks on `main`** are defined in `.github/workflows/ci.yml`.
- **Pause the pipeline** by labelling individual issues `needs-human`, or by disabling the
  scheduled run.
- **Model and time-cap tuning** lives in the runner's own configuration, outside this repository.
