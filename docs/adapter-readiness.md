# Adapter Readiness

`monolith-core adapter-readiness` checks whether a synthetic adapter profile
respects the public/private boundary before its generalized lesson becomes a
public issue, schema, fixture, test, or release note.

```bash
monolith-core adapter-readiness \
  --adapter examples/synthetic-vault/adapter-readiness.json
```

The profile separates two cross-platform lanes:

- `implementation`: public contracts, deterministic validation, and report
  rendering.
- `operations`: array preservation, side-effect reporting, and public handoff
  behavior.

Both lanes must remain report-only. They cannot claim authority over real
vaults, external services, schedulers, notifications, or secrets. Absolute
paths, parent-directory traversal, service URLs, and account-specific markers
fail closed. The report returns only generic blocker ids and never echoes the
rejected reference.

## Private-to-Public Handoff

1. Keep the original private observation and evidence in the adapter system.
2. State the reusable behavior without host, account, service, or vault data.
3. Reproduce it with a synthetic profile or fixture.
4. Run `adapter-readiness` and retain its public-safe report.
5. Open a public issue before changing schemas or CLI behavior.
6. Validate the resulting fixture in CI and return the public contract to the
   private adapter.

The public core remains a contract and test bench. It never becomes the system
of record or execution authority for private operations.
