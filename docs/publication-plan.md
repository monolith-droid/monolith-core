# Publication Plan

This project should become a separate public repository:

`monolith-droid/monolith-core`

## v0.1.0 Scope

- README with Obsidian-backed durable agent memory narrative.
- Public-safe schemas for cards, indexes, context packs, and branch-return
  reports.
- Synthetic vault fixture.
- Dry-run CLI validation.
- CI on Python 3.9 and 3.13.
- No private adapters, no Drive connection, no scheduler authority, no external
  model calls, no notification publishing.

## First Issues

1. Define stable card and index ids.
2. Add stale-card detection to curator dry-run output.
3. Add a public-safe Obsidian workflow guide.
4. Add richer context-pack scoring.
5. Add downstream dogfooding notes from private adapters without private data.

## Relationship To I/O Safety Kit

`I/O Safety Kit for OSS` controls side effects and safe output promotion.

`MONOLITH Core` controls durable memory structure and knowledge circulation.

They can integrate later, but each repo must remain understandable on its own.
