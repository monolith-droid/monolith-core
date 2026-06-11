# Downstream Dogfooding

Downstream dogfooding is the path from a private MONOLITH or Mac adapter back
to public MONOLITH Core.

The adapter may run against real Obsidian vaults, synced folders, schedulers,
or host-specific automation. MONOLITH Core should only receive the generalized
lesson: a schema improvement, a deterministic fixture, a dry-run command, or a
documentation update that can be reviewed without private context.

## Loop

1. Run the private adapter against the real workflow.
2. Keep raw logs, paths, transcripts, approvals, and runtime state private.
3. Extract the smallest reusable lesson.
4. Replace private evidence with synthetic evidence.
5. Open a public issue or PR against MONOLITH Core.
6. Validate the public fixture in CI.
7. Let the private adapter adopt the new public contract.

The public repository should never be the system of record for private
operations. It is the public contract and test bench that private adapters can
reuse.

## What Can Become A Public Issue

Good public issues describe a reusable behavior without exposing the private
source that revealed it.

Examples:

- A private adapter found that stale cards need `last_reviewed` and
  `review_interval_days`; public action: add freshness fields, scorecard docs,
  and a synthetic stale-card fixture.
- A Mac adapter needed the same context pack on another host; public action:
  document relative ids and portable context-pack references.
- A Windows wrapper preserved empty `blockers` and `warnings` arrays; public
  action: add a schema or fixture that keeps empty arrays as arrays.
- A curator dry run produced too much output for review; public action: add a
  report-only summary shape with counts, warnings, and next actions.
- A branch-return report was hard to trace back to cards; public action: add a
  validation rule or documentation for finding-to-card references.

Each issue should include:

- the public behavior to improve
- a synthetic example or fixture path
- the command that should validate the behavior
- a short note about which private details were intentionally omitted

## What Must Stay Private

Private adapter findings must not be copied directly into MONOLITH Core when
they contain operational context or authority.

Keep these private:

- raw Obsidian notes, vault contents, or unredacted transcripts
- Google Drive file ids, folder ids, synced paths, or account details
- local absolute paths, host names, user names, and machine-specific storage
  layouts
- approval ids, scheduler names, task ids, worker dispatch details, and
  cutover state
- tokens, secret names with values, API keys, cookies, and service endpoints
- external model prompts or responses that contain private project data
- raw failure logs whose sequence reveals private workflows
- notification channels, Discord server details, or human contact routes

If a private finding cannot be expressed as a synthetic fixture or general
contract improvement, it belongs in the private adapter repository.

## Public-Safe Translation Pattern

Use this pattern before opening a public issue or PR:

```text
Private observation:
  A real adapter failed because a context pack referenced a note that moved in
  the synced vault.

Public translation:
  A synthetic context pack can reference a missing card id.

Public artifact:
  Add a fixture and validation message for missing context-pack card ids.

Private details omitted:
  Real path, note title, sync provider metadata, timestamp sequence, and raw log.
```

The translation should preserve the lesson, not the private evidence.

## Adapter Return Checklist

Before a private adapter finding becomes public work, confirm:

- the issue can be understood without private MONOLITH knowledge
- examples are synthetic and deterministic
- paths are relative to the public fixture
- commands are dry-run or validation-only
- no secret, account, endpoint, approval, scheduler, or runtime authority is
  included
- the resulting public contract can be adopted by more than one private adapter

When the checklist passes, the public loop can be:

```bash
monolith-core validate --root examples/synthetic-vault
monolith-core score --root examples/synthetic-vault --as-of 2026-06-11
```

That keeps the public repository useful for real downstream work while keeping
the real downstream systems outside the public boundary.
