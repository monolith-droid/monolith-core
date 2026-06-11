# Growth Idea Queue

The growth idea queue is a public-safe list of possible MONOLITH Core
improvements. It lets a maintainer turn downstream dogfooding lessons into a
small ranked backlog without importing private adapter data.

```bash
monolith-core growth-queue --queue examples/synthetic-vault/growth-ideas.json
```

The command is report-only. It does not mutate notes, create issues, dispatch
workers, call external models, read private vaults, or connect to synced
folders.

## Idea Fields

Each idea is intentionally small:

- `idea_id`: stable public id.
- `title`: short human-readable name.
- `summary`: reusable lesson or improvement.
- `source_refs`: public-safe sources such as synthetic fixtures, docs, or
  branch-return findings.
- `status`: `candidate`, `adopted`, or `deferred`.
- `public_safety`: `synthetic` or `generalized`.
- `impact`, `effort`, `confidence`: integers from 1 to 5.
- `next_action`: the next small public-safe PR candidate.

Ideas that require raw logs, real notes, Google Drive metadata, approval ids,
secret values, scheduler authority, external endpoints, or local absolute paths
must stay in a private adapter queue.

## Ranking

`growth-queue` ranks only `candidate` ideas:

```text
priority_score = min(100, (impact * confidence / effort) * 4)
```

The score is not an automatic approval. It is a deterministic way to choose the
next small public issue or PR. Human review and repository tests still decide
what ships.

## Fixture

The synthetic input fixture lives at:

- `examples/synthetic-vault/growth-ideas.json`

The schema lives at:

- `schemas/growth-idea-queue.schema.json`

The fixture includes an already adopted downstream dogfooding docs idea and two
candidate improvements, including a repair-plan report. That keeps the public
example close to real MONOLITH learning while preserving the private boundary.
