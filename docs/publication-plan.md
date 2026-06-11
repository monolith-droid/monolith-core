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

## v0.1 Follow-Up

- `v0.1.1`: stable id conventions for cards, indexes, context packs, branch
  returns, and findings.
- `v0.1.2`: public-safe Obsidian workflow guide that explains vault layout while
  keeping real vault discovery and mutation in private adapters.

## v0.2.0 Scope

- Public-safe memory scorecard schema and synthetic fixture.
- `monolith-core score` report-only CLI command.
- Context-pack completeness, index coverage, provenance coverage, branch-return
  coverage, and stale-card detection scores.
- Freshness metadata for synthetic cards through `last_reviewed` and
  `review_interval_days`.
- No private vault reads, no Drive sync, no scheduler, no external model calls,
  and no mutation of user files.

## First Issues

1. Define stable card and index ids. Done in `v0.1.1`.
2. Add stale-card detection to curator dry-run output. Covered first by the
   report-only scorecard in `v0.2.0`.
3. Add adapter examples that convert synthetic Obsidian-style notes into the
   public JSON contracts.
4. Add richer context-pack scoring. Covered first by the report-only scorecard
   in `v0.2.0`.
5. Add downstream dogfooding notes from private adapters without private data.

## Relationship To I/O Safety Kit

`I/O Safety Kit for OSS` controls side effects and safe output promotion.

`MONOLITH Core` controls durable memory structure and knowledge circulation.

They can integrate later, but each repo must remain understandable on its own.
