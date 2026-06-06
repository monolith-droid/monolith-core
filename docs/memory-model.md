# Memory Model

MONOLITH Core treats durable agent memory as public, inspectable structure:

- one information unit per card
- stable card ids
- index entries that point to cards
- context packs for task startup
- branch-return reports for lessons learned in project work

The public core validates structure. Private adapters decide where real notes
live and how they are synced.
