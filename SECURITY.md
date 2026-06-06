# Security Policy

MONOLITH Core is dry-run by default. The public package should not read secrets,
connect to external services, mutate private vaults, run schedulers, or publish
notifications.

Please report issues that could cause private data to leak into public fixtures,
reports, examples, or logs.

Private adapters must own their own approval, authentication, and side-effect
boundaries. The public core should remain useful without private credentials.
