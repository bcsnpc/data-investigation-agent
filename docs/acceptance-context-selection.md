# Acceptance-file context selection

2026-10-05 UTC. The runner reads the immutable context ID/hash from its acceptance file, never from a manually maintained parallel pin map. select_store loads that file, checks any explicitly invoked context before work, opens the retained context with ModelStore, and checks its hash. A mismatch reports both IDs/hashes. Existing enablement, denies and whole-config discovery approval remain in force.

Two tests cover early successor refusal and file-owned pin selection. Existing immutable-context ModelStore tests cover retained old-context selection without changing the current catalog. No live run or ledger row. No policy, fixture, identity or grant change. Prior freezes invalidated. README acceptance claims unchanged while earned results remain unrestored.
