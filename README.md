# MONOLITH Core

MONOLITH Core is a small, public-safe toolkit for durable agent memory.

It treats an Obsidian vault as a long-term memory layer for AI-assisted work:
knowledge is split into cards, indexed into context packs, and checked through
a branch-return contract so project-specific findings can flow back into shared
core knowledge.

The first release line is intentionally local and dry-run only. It validates
synthetic cards, indexes, context packs, and curator reports. It does not read
private vaults, connect to Google Drive, execute schedulers, call external
models, publish messages, or mutate user files.

## Why This Exists

Coding agents are strongest when they can recover context reliably. Chat history
and model memory are not enough for long-running projects. Maintainers need a
small, inspectable structure that records what the agent should know next time:

1. One idea becomes one knowledge card.
2. Cards are indexed by stable ids and source references.
3. Context packs collect the cards needed for a task.
4. Curator reports show what was reviewed, merged, or deferred.
5. Branch-return checks ensure project work flows back to shared memory.

## Core Concepts

- **Knowledge card**: one durable unit of reusable information.
- **Knowledge index**: a machine-readable map of card ids, tags, and sources.
- **Context pack**: a task-specific bundle of cards for agent context recovery.
- **Branch return**: a report that links project findings back to core memory.
- **Hermes-style curator**: a periodic, report-only loop that proposes updates
  without silently mutating private knowledge.

See [ID conventions](docs/id-conventions.md) for the stable card, index, and
context-pack id rules.

See [Obsidian workflow](docs/obsidian-workflow.md) for a public-safe vault
layout and the private adapter boundary.

See [Downstream dogfooding](docs/downstream-dogfooding.md) for the path from
private MONOLITH or Mac adapter findings back to public-safe issues and PRs.

See [Growth idea queue](docs/growth-idea-queue.md) for a report-only way to
rank public-safe self-growth candidates.

## Quick Start

```bash
python -m pip install -e .
monolith-core validate --root examples/synthetic-vault
monolith-core pack --index examples/synthetic-vault/index.json --pack examples/synthetic-vault/context-pack.json
monolith-core branch-return-check --report examples/synthetic-vault/branch-return.json
monolith-core score --root examples/synthetic-vault --as-of 2026-06-11
monolith-core growth-queue --queue examples/synthetic-vault/growth-ideas.json
monolith-core curate-dry-run --root examples/synthetic-vault --out reports/curator-report.json
```

## Public Safety Boundary

MONOLITH Core is the public core. Private adapters are separate.

The public core may include synthetic fixtures, schemas, dry-run validators, and
documentation. It must not include private MONOLITH runtime state, real Drive
contents, private Obsidian notes, tokens, approval ids, external service
endpoints, scheduler authority, or user-specific paths.

For side-effect control, pair this project with
[I/O Safety Kit for OSS](https://github.com/monolith-droid/io-safety-kit-for-oss).

## Roadmap

- `v0.1.0`: schemas, synthetic vault, validation CLI, branch-return check.
- `v0.1.1`: stable id conventions for cards, indexes, and context packs.
- `v0.1.2`: public-safe Obsidian workflow guide.
- `v0.2.0`: memory scorecard, context-pack scoring, and stale-card detection.
- `v0.2.1`: downstream dogfooding docs and public-safe growth idea queue.
- `v0.3.0`: adapter guide for local Obsidian vaults without private data leaks.
- `v1.0.0`: stable card/index/context-pack contracts.
