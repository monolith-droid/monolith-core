# Changelog

## 0.2.1 - 2026-06-11

- Add downstream dogfooding guidance for translating private adapter findings
  into public-safe issues, fixtures, and docs.
- Add a public-safe growth idea queue schema and synthetic fixture.
- Add `monolith-core growth-queue` for report-only self-growth candidate
  ranking.

## 0.2.0 - 2026-06-11

- Add a public-safe memory scorecard schema and synthetic fixture.
- Add `monolith-core score` for report-only memory health checks.
- Score index coverage, context-pack completeness, provenance coverage,
  branch-return coverage, and stale-card detection.
- Add synthetic freshness metadata to knowledge cards.

## 0.1.2 - 2026-06-06

- Add a public-safe Obsidian workflow guide.
- Document a synthetic vault layout for cards, indexes, context packs, and
  branch-return reports.
- Clarify where private adapters begin for real vaults, Drive sync, schedulers,
  external models, notifications, and user-specific paths.

## 0.1.1 - 2026-06-06

- Add stable id conventions for cards, indexes, context packs, branch returns,
  and findings.
- Validate public id prefixes and lowercase hyphenated id shapes in the CLI.
- Add schema patterns and tests that protect the id convention.

## 0.1.0 - 2026-06-06

- Add initial public-safe MONOLITH Core scaffold.
- Add synthetic vault fixtures for knowledge cards, index, context pack, and
  branch-return report.
- Add local dry-run CLI commands:
  - `validate`
  - `pack`
  - `branch-return-check`
  - `curate-dry-run`
- Add schemas, docs, tests, and CI workflow.
