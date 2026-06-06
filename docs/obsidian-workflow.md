# Obsidian Workflow

MONOLITH Core can be mapped into an Obsidian vault without making the public
core depend on a real private vault. The public repository uses only synthetic
fixtures; private adapters decide how to read, sync, or write real notes.

## Public-Safe Vault Layout

A small Obsidian-compatible layout can mirror the synthetic fixture:

```text
MONOLITH-Core-Demo/
  cards/
    card-agent-memory.md
    card-branch-return.md
  indexes/
    index-synthetic-core.json
  context-packs/
    pack-monolith-core-mvp.json
  branch-returns/
    branch-synthetic-oss-maintainer.json
```

The public fixture keeps JSON under `examples/synthetic-vault/` so CI can
validate it deterministically:

```text
examples/synthetic-vault/
  cards/
    card-agent-memory.json
    card-branch-return.json
  index.json
  context-pack.json
  branch-return.json
```

Both shapes use the same public ids. A private adapter may translate between
Markdown notes and JSON contract files, but the public core only validates the
contract data.

## Card Notes

Each card note should represent one reusable idea.

Synthetic Markdown sketch:

```markdown
---
card_id: card-agent-memory
tags:
  - agent-memory
  - obsidian
  - context-recovery
source_refs:
  - synthetic:memory-model
---

# Agent Memory Belongs In Durable Notes

Long-running agent workflows should recover context from indexed notes and
cards instead of relying on chat memory alone.
```

The equivalent public fixture is
`examples/synthetic-vault/cards/card-agent-memory.json`.

## Index Notes

An index is the machine-readable map an agent can search before it starts work.

Synthetic filename:

```text
indexes/index-synthetic-core.json
```

The index should point to stable `card-` ids and relative synthetic paths, not
local absolute paths or private vault locations.

## Context Packs

A context pack is a small startup bundle for a task.

Synthetic filename:

```text
context-packs/pack-monolith-core-mvp.json
```

Use context packs to answer: "What should the agent load before doing this
task?" Keep the pack short enough for a human to inspect.

## Branch Returns

A branch return report links project-specific work back to shared memory.

Synthetic filename:

```text
branch-returns/branch-synthetic-oss-maintainer.json
```

It should reference the index and cards that were used, then list findings that
could update core knowledge later. Public examples must stay synthetic.

## Private Adapter Boundary

MONOLITH Core stops at public contracts and dry-run validation.

Private adapters begin when a workflow needs to:

- discover a real Obsidian vault
- read private Markdown notes
- write or rename notes
- sync through Google Drive or another file service
- run a scheduled curator
- call external models
- publish notifications
- carry user-specific paths, approval ids, credentials, or service endpoints

Those adapters should keep their own approval, authentication, and side-effect
boundaries. Public MONOLITH Core should remain useful without any private data
or external service.

## Local Validation

Validate the synthetic public fixture:

```bash
python -m monolith_core validate --root examples/synthetic-vault
```

This confirms that ids, references, context packs, and branch-return links are
structurally usable before a private adapter maps them into a real vault.
