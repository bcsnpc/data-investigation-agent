# Estate configurations

`fixture.json` and `billing.json` are client-style examples of the existing
`estate-manifest-v1` contract. They use the same `estate_manifest.load()` and
adapter projection as every installation; no example-specific loader exists.

These files describe reference-estate identities and routes, not permission
grants or current discovery approvals. They contain names and credential
references, never passwords, tokens or keys. Paths are repository-relative.
Copy a configuration to your installation directory, supply your actual scoped
identity references and connections, and collect and approve its context before
execution. Example budget numbers are not an approval to spend against a new
ledger. Live installations must point at their existing shared accounting store
and carry the approved round policy.

The fixture example includes its declared application/load audit path. The
billing example faithfully retains the previously declared semantic layer and
its unresolved-binding limitations; this round does not invent verified billing
paths from names. Report/page/visual/measure definitions are discovered into the
catalog, not duplicated as runtime defaults in these files.

Historical observed string semantics, verifier receipts and fixture expected
arithmetic were deliberately not copied into the examples. They remain in the
original evidence/configuration; a new installation must earn its own evidence.
The older `infra/estates/` configurations remain immutable historical inputs to
tests and recorded runs. Nothing silently redirects an installation to these
new examples.

Validate locally, without any estate or model call:

```powershell
$env:PYTHONPATH = 'scripts'
python -c "from investigator.estate_manifest import load; load('estates/fixture.json'); load('estates/billing.json'); print('Both valid')"
```

The checked-in examples retain currently supported local credential-reference
forms. Schema validation establishes configuration consistency, not readiness
or cloud authentication. Cloud credentials and preflight must be selected
explicitly; there is no fallback to an operator or publisher identity.
