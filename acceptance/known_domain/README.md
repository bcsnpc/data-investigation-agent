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
