# Contributing

## Before your first change

1. Read [`docs/PRODUCT_CONTEXT.md`](docs/PRODUCT_CONTEXT.md) and [`AGENTS.md`](AGENTS.md). The
   invariants in `AGENTS.md` apply to humans too.
2. Skim [`docs/adr/`](docs/adr/). Those decisions are settled — if you disagree with one, open an
   issue rather than a pull request.
3. Set up your environment with `make setup`, then `make up`.

## Picking work

Take an issue labelled `ready`. Issues are written to be sufficient on their own: file paths,
schemas, endpoint contracts, acceptance criteria and a test plan are all specified. Assign
yourself before starting.

Work the `M0 Foundations` milestone first — everything else depends on it.

If an issue turns out to be underspecified or ambiguous between two materially different designs,
say so in a comment and apply `needs-human`. That is a defect in the issue, not something to paper
over with a guess.

## Making the change

**One pull request closes exactly one issue.** Branch from `main` as
`<type>/<issue-number>-<slug>`, for example `feat/42-trip-publish-endpoint`.

Commits follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat(booking): hold seats for 15 minutes during checkout
fix(pricing): reject contributions above the 120% cap
chore(ci): pin actions to commit SHAs
```

Run `make verify` before pushing. It runs the same gates CI does and is far faster than waiting
for a red build.

## Pull requests

The template asks for a linked issue, a summary of the change, and how you verified it. All three
are load-bearing:

- **Closes #N** in the description, so the issue closes on merge.
- **Tests alongside source.** Danger.js flags a PR that changes `app/` or `src/` without touching
  tests. If that is genuinely correct for your change, say why in the description.
- **Screenshots for UI changes**, including the Amharic rendering. Ge'ez script has different
  metrics from Latin and layouts break in ways that are invisible if you only ever look at
  English.

Every required gate must be green. Do not merge your own PR if you are an automated agent — see
[`AUTOPILOT.md`](AUTOPILOT.md) for why the implementer and the reviewer are deliberately separated.

## Reviewing

Look for the things the gates cannot check:

- Does it match the business rule in the issue, and does the issue match `docs/PRODUCT_CONTEXT.md`?
- Are the edge cases in the test plan actually tested, or just asserted to work?
- Would this behave correctly with no network connection, and on a low-end Android device?
- Does anything here quietly become a legal problem — pricing, driver monitoring, data retention?
