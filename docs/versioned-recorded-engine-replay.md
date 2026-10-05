# Versioned recorded-engine replay

2026-10-05 UTC. Tape schema validation is not current-engine compatibility.
The earlier 2/15 gate applied new intake/request producers to old sealed inputs;
ten failures surfaced at a later budget settlement, masking the earlier provider
failure. Current intake adds value_roles and sorts request dictionary keys.
Old archived-engine requests do neither. No payload field may be dropped from
new investigation input to manufacture an old replay pass.

The recorder now emits bounded-worker-tape-v2 and retains the immutable Git
engine revision in its sealed envelope. v1 envelopes remain readable, with
unchanged seals. A test records v1, advances the recorder to v2, replays v1 and
asserts its original bytes are unchanged. No response or budget event is invented.

The acceptance helper executes an explicitly pinned Git engine in an isolated
subprocess with sockets blocked, preserving byte-exact request/final matching.
Legacy v1 recordings use separately hash-bound replay-revision annotations;
these identify a tested compatibility revision, not a retrospective claim that
that exact Git commit was recorded. Both executed and recorded engine identities
remain in the report. Schema version and engine revision are distinct dimensions.
Missing historical events still block; current-engine requalification is a
separate test and cannot be claimed from historical replay.

This is offline machinery. No estate call, cap change or live replacement.
Prior freezes invalid. The fifteen-case regrade and reasons are recorded before
resuming D/G/H/EMPTY/source consistency, each once under the unchanged stop rule.
