# Context Pack Diff

The context-pack diff command compares two public context-pack fixtures and
renders a report-only diff.

```bash
monolith-core context-pack-diff \
  --base examples/synthetic-vault/context-pack.json \
  --candidate examples/synthetic-vault/context-pack-expanded.json
```

The command does not mutate either pack. It does not edit notes, write vault
files, connect to synced folders, call external models, create issues, dispatch
workers, run schedulers, or publish notifications.

## Output

The report lists:

- `added_card_ids`: cards present only in the candidate pack
- `removed_card_ids`: cards present only in the base pack
- `unchanged_card_ids`: cards present in both packs

It also includes counts for each group, plus public pack ids and relative
fixture paths.

## Fixture

The synthetic candidate pack lives at:

- `examples/synthetic-vault/context-pack-expanded.json`

The synthetic diff report lives at:

- `examples/synthetic-vault/context-pack-diff.json`

The schema lives at:

- `schemas/context-pack-diff.schema.json`

This gives maintainers a public-safe way to review context-pack changes before
promoting them into downstream adapter workflows.
