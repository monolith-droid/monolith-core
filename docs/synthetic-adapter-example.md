# Synthetic Adapter Example

The synthetic adapter example shows how a reviewed Markdown-like note can map
to the public MONOLITH Core JSON contracts.

```bash
monolith-core adapter-example --note examples/synthetic-vault/adapter-note.md
```

The command is report-only. It does not discover real vaults, read private
notes, sync Google Drive folders, mutate files, call external models, dispatch
workers, run schedulers, publish notifications, or carry local absolute paths.

## Input

The synthetic note lives at:

- `examples/synthetic-vault/adapter-note.md`

It uses a small frontmatter shape for demonstration only. Private adapters may
use richer parsing internally, but public MONOLITH Core keeps this example
deterministic and synthetic.

## Output

The generated report contains three public contracts:

- `card`: a knowledge card object
- `index`: a one-entry knowledge index object
- `context_pack`: a one-card context pack object

The fixture lives at:

- `examples/synthetic-vault/adapter-example.json`

The schema lives at:

- `schemas/adapter-example.schema.json`

This gives downstream adapters a public-safe target shape while keeping real
vault discovery, file writes, account metadata, and raw logs outside the public
repository.
