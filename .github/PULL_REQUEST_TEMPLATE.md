## Linked issue

Closes #

<!-- One pull request closes exactly one issue. If you fixed something else along the
way, open a separate issue and link it here instead. -->

## Summary

<!-- What changed and why. The reviewer should not have to read the diff to find out. -->

## Verification

<!-- How you know it works. `make verify` is the floor, not the answer. -->

- [ ] `make verify` passes locally
- [ ] Tests cover the acceptance criteria in the issue, including its edge cases
- [ ] Any model change ships with an Alembic migration
- [ ] API changes are additive — no field removed or repurposed

## Screenshots

<!-- UI changes only. Include the Amharic rendering as well as English: Ge'ez metrics
differ from Latin and layouts break in ways that are invisible in English alone. -->

## Invariants touched

Tick anything this change comes near, so the reviewer knows where to look hardest.

- [ ] Money — amounts stay integer santim, proportions go through the money helpers
- [ ] Time — backend stores aware UTC, conversion stays in `packages/@abro/time`
- [ ] Search — gazetteer name queries go through `am_normalize()`
- [ ] Corridor queries — `ST_DWithin` paired with `_ST_Expand(...) &&`, direction checked
- [ ] Logging — no phone numbers, Fayda identifiers, OTP codes or payment references
- [ ] i18n — every new string exists in both `en` and `am`
- [ ] None of the above
