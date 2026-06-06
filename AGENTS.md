# MONOLITH Core Agent Rules

This project is intended to become a separate public repository. Keep it
public-safe, synthetic, and independent from private MONOLITH runtime data.

## Boundaries

- Do not copy private Obsidian notes, Google Drive contents, approval ids,
  runtime state, service endpoints, transcripts, secrets, or local absolute
  paths into this project.
- Use synthetic examples only.
- Keep all core commands local, deterministic, and dry-run by default.
- Treat real vault, Drive, scheduler, external model, and notification support
  as private adapter responsibilities unless a future public-safe adapter is
  designed explicitly.

## Shape

- `src/monolith_core/`: public Python package.
- `schemas/`: machine-readable contracts.
- `examples/synthetic-vault/`: safe fixtures for docs, tests, and demos.
- `docs/`: human-facing design notes.
- `tests/`: public CI tests.

Before finishing code changes, run:

```bash
python -m pytest
python -m monolith_core validate --root examples/synthetic-vault
```
