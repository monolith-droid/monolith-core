# Contributing

MONOLITH Core is intentionally small and public-safe.

Good contributions:

- improve schemas
- add synthetic examples
- improve validation messages
- document adapter boundaries
- add tests for context-pack or branch-return behavior

Do not submit private vault contents, real Google Drive data, secrets, tokens,
local absolute paths, service endpoints, approval ids, or private runtime logs.

Before opening a pull request:

```bash
python -m pip install -e .
python -m pytest
python -m monolith_core validate --root examples/synthetic-vault
```
