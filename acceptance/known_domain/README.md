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
