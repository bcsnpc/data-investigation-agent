# Retained cloud controls: fixture and billing preflight

Use each estate's approved cloud manifest, not its unmodified workstation
example. Preserve the exact sanitized `PLATFORM_HEALTH` and
`PLATFORM_AUTH_PREFLIGHT` JSON reports from the deployed worker. Pin the bytes
before importing their facts:

```powershell
$healthHash = (Get-FileHash -Algorithm SHA256 -LiteralPath .local/platform-health.json).Hash.ToLowerInvariant()
$authHash = (Get-FileHash -Algorithm SHA256 -LiteralPath .local/platform-auth.json).Hash.ToLowerInvariant()
python scripts/preflight_installation.py --manifest .local/cloud-fixture.json --platform .local/client-platform.json --platform-health-receipt .local/platform-health.json $healthHash --authentication-receipt .local/platform-auth.json $authHash --output .local/preflight-fixture-001.json
python scripts/preflight_installation.py --manifest .local/cloud-billing.json --platform .local/client-platform.json --platform-health-receipt .local/platform-health.json $healthHash --authentication-receipt .local/platform-auth.json $authHash --output .local/preflight-billing-001.json
```

These commands perform no new authentication, estate or model request. The hash
is an integrity pin, not a signature or proof of origin: the operator must select
the actual retained worker reports. The CLI refuses changed bytes, wrong report
kinds, another worker's health result or a non-control receipt. It preserves the
original files and refuses to overwrite an output report.

A successful immutable health Blob roundtrip can establish `blob.access` and
worker authentication for storage. PostgreSQL row counts do not establish exact
migration correctness; run the separately bounded `--check-shared-state` control
when needed. Vault metadata listing does not establish a versioned secret read.
Reader-cache token refreshes appear as separate `authentication_facts`; they do
not fill Execute Queries, layer read, model-generation, scanner or tenant-setting
checks. Model-key availability likewise does not establish model API access.
Missing actual permission/query receipts therefore remain **MISSING**, and the
installation remains **NOT_READY**. An authentication result for the same user
can be relevant to both estates, but grants on one model/database never transfer
to another.

For the approved existing-user exception, the cloud authentication command and
exact per-client gateway channels are documented in
[cloud-existing-reader-cache.md](cloud-existing-reader-cache.md). Only the
already-declared Power BI and SQL audiences are acquired. General Fabric and
OneLake discovery remain unavailable through these scoped caches. Do not add
an audience or fall back to an operator to make preflight green. Retained pinned
definitions may support the separately validated route; they are not a fresh
scanner-access receipt. An application source still naming a local DPAPI
credential is not cloud executable. Leave its route unavailable until its
existing credential has an approved supported cloud transport; do not substitute
the delegated Fabric user, code reader, worker MI or another database's grant.
