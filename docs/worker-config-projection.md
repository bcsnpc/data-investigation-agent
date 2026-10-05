# Schema-owned native worker configuration

2026-10-05 UTC. Fix for D run 33e5be52; original run and receipts unchanged.
The worker previously serialized the runtime config, leaking _estate into a closed
consumer schema. It now constructs only consumer-owned required configuration
fields, with native Fabric fields projected from the same schema ownership.
Manifested requests must match a reachable declared semantic layer by exact
workspace/model address, and the worker reader is narrowed to that model after
checking the existing scope. No global lookup, scope grant or metadata fallback.
Runtime budgets, lineage, layer roles and arbitrary future top-level metadata do
not cross the native worker boundary. The general manifest remains closed: the
projection test injects an extra manifest key directly without weakening validation.

Tests exercise both actual serialized transport input and worker load_config
acceptance, including arbitrary runtime/manifest keys and undeclared-target refusal.
22 reader tests pass. No live run, estate change or ledger row. Prior freezes
invalidated. Replay audit and offline grading precede any resumed live list.
