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
