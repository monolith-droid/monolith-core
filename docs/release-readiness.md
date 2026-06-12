# Release Readiness

The release readiness command combines the public report-only signals that a
maintainer should check before publishing a MONOLITH Core release.

```bash
monolith-core release-readiness \
  --root examples/synthetic-vault \
  --queue examples/synthetic-vault/growth-ideas.json \
  --base-pack examples/synthetic-vault/context-pack.json \
  --candidate-pack examples/synthetic-vault/context-pack-expanded.json \
  --as-of 2026-06-12
```

The command does not publish a release. It does not create issues, edit files,
write vault data, connect to synced folders, dispatch workers, run schedulers,
call external models, publish notifications, or read private data.

## Checks

`release-readiness` combines four public checks:

- validation summary source status and blocker count
- memory scorecard status, overall score, and low-score count
- growth queue candidate availability
- context-pack diff counts

The report keeps release readiness separate from mutation:

- `passed`: whether the public release signals are ready
- `mode`: always `report_only`
- `mutation_performed`: always `false`

Warnings can still be present on a ready report. For example,
context-pack additions are useful to review before release but do not block the
synthetic fixture release by themselves.

## Fixture

The synthetic output fixture lives at:

- `examples/synthetic-vault/release-readiness.json`

The schema lives at:

- `schemas/release-readiness.schema.json`

This gives maintainers a compact final status report before promoting a public
release while keeping private adapter details outside the public repository.
