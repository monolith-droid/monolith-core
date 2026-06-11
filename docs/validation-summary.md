# Validation Summary

The validation summary command renders a compact report-only view of the
public synthetic vault validation result.

```bash
monolith-core validation-summary --root examples/synthetic-vault
```

The command does not mutate files. It does not edit notes, write vault files,
connect to synced folders, create issues, dispatch workers, run schedulers,
call external models, publish notifications, or read private data.

## Inputs

`validation-summary` reads the same public synthetic fixture as `validate`:

- `cards/*.json`
- `index.json`
- `context-pack.json`
- `branch-return.json`

## Output

The summary groups validation results into:

- `counts`: card, index entry, context-pack card, and branch-return finding
  counts
- `blockers`: validation blockers from the source validation result
- `next_actions`: compact report-only follow-up actions

The report keeps two concepts separate:

- `source_passed`: whether the source validation passed
- `passed`: whether MONOLITH Core successfully generated a validation summary

That lets maintainers create a summary for a broken public fixture without
treating summary generation itself as a failure.

## Fixture

The synthetic output fixture lives at:

- `examples/synthetic-vault/validation-summary.json`

The schema lives at:

- `schemas/validation-summary.schema.json`

This gives maintainers a small public-safe status report before promoting
validation fixes, repair plans, or downstream adapter lessons.
