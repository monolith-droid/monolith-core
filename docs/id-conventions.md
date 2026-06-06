# ID Conventions

Stable ids are the address system for MONOLITH Core memory. Agents should be
able to recover cards, indexes, and context packs from ids without relying on
chat history.

## Format

All public ids use lowercase words separated by hyphens:

```text
<type>-<short-topic>[-<optional-scope>]
```

Allowed characters:

- lowercase ASCII letters
- digits
- hyphens between words

Do not use spaces, underscores, uppercase letters, dates as the only meaning,
local paths, private project names, approval ids, service names, or personal
identifiers.

## Prefixes

Use a type prefix so an id remains understandable outside its original file.

| Object | Prefix | Example |
| --- | --- | --- |
| Knowledge card | `card-` | `card-agent-memory` |
| Knowledge index | `index-` | `index-synthetic-core` |
| Context pack | `pack-` | `pack-monolith-core-mvp` |
| Branch return report | `branch-` | `branch-synthetic-oss-maintainer` |
| Branch finding | `finding-` | `finding-context-recovery` |

## Card IDs

Card ids should describe the reusable idea, not where it was discovered.

Good:

```text
card-agent-memory
card-branch-return
card-release-checklist-context
```

Avoid:

```text
Card_AgentMemory
20260606-note
c-users-name-private-vault-card
approval-12345
```

## Index IDs

Index ids name the collection being searched.

Good:

```text
index-synthetic-core
index-maintainer-workflows
```

Index entries must reference existing `card-` ids.

## Context Pack IDs

Context pack ids name the startup context an agent should load for a task.

Good:

```text
pack-monolith-core-mvp
pack-release-prep
pack-issue-triage
```

Context packs should remain task-oriented and small enough to inspect.

## Stability Rules

- Do not rename ids casually; ids are durable references.
- If a card is superseded, prefer a new card id and keep the old id available
  until adapters can migrate.
- Keep private adapter ids out of public fixtures unless they are synthetic and
  useful to all users.
- Treat `source_refs` as evidence pointers, not as replacement ids for cards.

## Validation

The CLI validates id prefixes and character shape:

```bash
monolith-core validate --root examples/synthetic-vault
```

Invalid ids fail closed with a `validation_error` status.
