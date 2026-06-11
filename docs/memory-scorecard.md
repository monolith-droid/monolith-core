# Memory Scorecard

The memory scorecard is a report-only health check for a public MONOLITH Core
fixture. It turns the synthetic vault into small scores that an agent or
maintainer can review before relying on a context pack.

```bash
monolith-core score --root examples/synthetic-vault --as-of 2026-06-11
```

The command does not mutate the vault. It does not read private notes, Drive
folders, schedulers, external models, notifications, or user-specific paths.

## Scores

- `score-index-coverage`: every card is present in the knowledge index.
- `score-context-pack-completeness`: the context pack references the known card
  set needed for context recovery.
- `score-provenance-coverage`: every card has public-safe source references.
- `score-branch-return-coverage`: branch-return reports link findings back to
  known cards.
- `score-stale-card-detection`: cards include `last_reviewed` and
  `review_interval_days` so stale cards can be detected.

Low scores are public-safe improvement signals. Private adapters can use the
same shape downstream, but they must translate private findings into synthetic
or generalized evidence before proposing public changes.

## Fixture

The synthetic fixture lives at:

- `examples/synthetic-vault/scorecard.json`

The schema lives at:

- `schemas/memory-scorecard.schema.json`

The fixture intentionally contains no private MONOLITH runtime state, no real
Obsidian vault content, no Google Drive data, no approval ids, and no local
absolute paths.
