# Hermes-Style Curation Loop

The public curation loop is report-only:

1. Read a public-safe or local fixture root.
2. Validate cards, index, context pack, and branch-return report.
3. Propose curation actions.
4. Emit a report.
5. Perform no mutation unless a private adapter explicitly adds that authority.

This keeps MONOLITH Core useful for CI and documentation while leaving real
Obsidian, Drive, scheduler, and notification authority outside the public core.
