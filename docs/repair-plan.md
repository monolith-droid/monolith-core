# Repair Plan

The repair plan command turns public validation and scorecard problems into a
small report-only repair checklist.

```bash
monolith-core repair-plan --root examples/synthetic-vault --as-of 2026-07-15
```

The command does not repair files. It does not edit notes, create issues,
rename paths, dispatch workers, run schedulers, call external models, read
private vaults, connect to synced folders, or publish notifications.

## Inputs

`repair-plan` reads the same public synthetic fixture as `validate` and
`score`:

- `cards/*.json`
- `index.json`
- `context-pack.json`
- `branch-return.json`

It can produce steps from:

- validation blockers such as missing index entries or unknown card refs
- scorecard failures such as missing freshness metadata
- scorecard warnings such as stale cards
- loader errors that prevent scoring

## Output

The report keeps two concepts separate:

- `source_passed`: whether the source validation or scorecard passed
- `passed`: whether MONOLITH Core successfully generated a repair report

That lets maintainers run repair planning against a broken public fixture
without treating report generation itself as a failure.

## Fixture

The synthetic output fixture lives at:

- `examples/synthetic-vault/repair-plan.json`

The schema lives at:

- `schemas/repair-plan.schema.json`

The fixture uses a future `as_of` date to produce a stale-card repair step
without changing the valid synthetic vault. Real private logs and vault data
remain outside the public repository.
