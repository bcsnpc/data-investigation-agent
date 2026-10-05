# Known-domain acceptance gate

Strict draft gate, not a passing suite. Fifteen expectations conserve the full
requested roster. Run:

```powershell
python acceptance/known_domain/check.py --output .local/acceptance-check
```

The output directory must be new. `--fixture-root` selects the protected local
recording/catalog bundle. `--ledger` is only for a deliberately recorded offline
batch; CI does not modify the ledger. Missing inputs or incomplete replay return
nonzero. No canned narrative substitutes for replay. Original files are read-only;
the existing replay harness copies databases before mutation and compares provider
requests byte-exactly. Sockets remain blocked. Change an acceptance file only with
its reason stated in that PR. See docs/round-four-acceptance-gaps.md.

Dated 2026-10-05: cases pin immutable context ID/hash. Reproduction cases grade the addressed cell and answer line, retaining walk outcome separately. The protected bundle must contain known-domain-runs/<ticket_id>.json with its preserved session and tape_path, and the referenced sealed tapes/databases. Missing inputs fail closed. Mechanism grading uses an explicit provider-mechanism field or its sealed provider response, never paragraph position. Engine-only refusal text is labelled engine-only. Eleven original tapes replayed; only 16 passes corrected pinned acceptance. The gate remains draft; no historical tape is rewritten.

2026-10-05 Round Five D: version 3 expectations contain structured outcomes, answer categories, resolution kinds, ordered boundary grades/equality, reached quantity surfaces and addressed reproduction verdicts. No whole sentence or old run timestamp is an oracle. Nine checker tests cover wording invariance and structural changes. Cases retain reference_session_id as provenance; a new attempt has its own session ID and must match the ticket/model hash and immutable context. The replay runner validates its sealed actual context against the file and never retargets old evidence. Live selection uses investigator.acceptance_context.select_store directly from the same file. Old 11/15 matched replays were regraded with zero estate requests: only 16 passes. D/G/H require re-recording; EMPTY pre-canonical bytes cannot be repaired. #376 remains draft.
2026-10-05 grading correction: entity binding `kind=REPORT` is not a resolution kind. The earlier v3 projection conflated these fields and falsely reported `STRUCTURE:resolutions`. Only an explicit `resolution_kind` enters that comparison now; changing STATED to EVIDENCE still fails. Ten checker tests pass, including entity-kind independence. Zero-request corrected grading remains 11/15 replayable, 1/15 accepted. Earlier grading records remain preserved.

2026-10-05 Round Five E supersession: v4 cases name fixture state, with prior context pins retained only as reference provenance. The authoritative fixture manifest defines predicates/mutations/reachability and independent arithmetic. The runner requires an explicit approved state/context association, never infers state from recollection identity, and records both in new tapes. Historical tapes remain unchanged; separate associations bind run/tape hashes and recorded contexts and are labelled retrospective.

Current declared roles are a dated grading view over unchanged old receipts. E's answer category NOT_ANSWERED → PARTLY_ANSWERED and source gap NOT_ANSWERED → ANSWERED are explicitly recorded #372 changes; outcomes unchanged. Original fifteen grade 8/15. Existing F and Q49 I tapes byte-exactly replay and pass, making selected evidence 10/15, still 11 replayable. No new live runs; D/G/H/EMPTY recording gaps and source consistency remain. #376 remains draft. See docs/round-five-fixture-states.md after the fixture-state implementation PR merges. This replaces earlier context-ID acceptance claims, not their historical evidence.

Dated replay separation, 2026-10-05 UTC: v2 tapes seal a committed engine revision. Legacy v1 uses separately hash-bound historical-replay-bindings.json entries identifying a tested compatibility revision, not a retrospective exact-recording claim. The checker executes that revision with sockets blocked and exact request/final matching; it does not apply current producers to historical input or substitute saved outputs. Current-engine requalification remains the live list. G/H missing budget checkpoints and D missing identity still block. The new fifteen regrade is in progress; no15/15 claim.
