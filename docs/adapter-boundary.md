# Adapter Boundary

MONOLITH Core is only the public contract and dry-run validator.

Adapters may connect the contract to real systems, but those adapters must own
their own approval, authentication, and side-effect boundaries.

Private adapter examples:

- local Obsidian vault discovery
- Google Drive sync
- scheduled Hermes curator execution
- desktop-to-Mac handoff
- notification delivery

Public MONOLITH Core should stay useful without any of those integrations.
