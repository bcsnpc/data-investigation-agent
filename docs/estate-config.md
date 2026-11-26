# Estate configuration (Round 28A)

The public contract is `estate-config/1`; its closed schema is exported as
`config/estates/estate-config.schema.json`. Validate without network access:

```powershell
python scripts/dia.py estate validate config/estates/practice-fixture.json
python scripts/dia.py estate validate config/estates/example-hospital.json
```

`practice-fixture.json` wraps the exact native installation retained with R27's
normal deployment input. It does not grant access, renew funding, change a ledger,
or deploy anything. Historical fields in that retained manifest remain historical;
current shared budget and gateway policies still govern execution.

| Field | Meaning |
| --- | --- |
| `id`, `name`, `enabled`, `status` | Installation identity; disabled drafts cannot execute. |
| `references` | Tenant, subscription and resource group references. |
| `installation` | Existing validated manifest: sole authoritative native addresses, workspace/model bindings, identity references, gateway adapter options and existing engine budget policy. No separate address defaults. |
| `connectors` | Enabled platform references to installed adapters, readers and object IDs; descriptive discovery rules use the existing installed metadata ports. |
| `layers` | Source, Bronze, Silver, Gold, model and report mapped to connector/object references or declared discovery. Missing layers fail validation. |
| `source_of_truth`, `deepest_reachable` | Declared layer roles; they do not assert a successful read. |
| `identities` | Managed-identity/service-principal references, with tenant and secret-name references. No impersonation or owner fallback. |
| `secrets` | Vault name and secret names only. Existing nested credential references may pin a secret version. Validation never resolves a secret. |
| `model` | Provider/model matching the installed binding, secret-name reference and declared limits. |
| `limits` | Positive ordered per-ticket/day request and cash declarations, plus monthly cash. These are not a replacement for the existing authoritative ledger's admission policy or an authorization to raise its limits. |
| `optional_sources` | Catalog, ontology and glossary remain off; this round does not implement new adapters. |
| `deployment` | Retained job-name declarations only; no runner/deployment cleanup in the narrowed scope. |

The existing `estate_manifest.load`/installation builder accepts this config and
projects its native installation without changing it. Existing legacy manifests
remain readable for frozen tapes. `DIA_ESTATE_CONFIG` is an optional trusted process
setting for investigation runtime validation; it is never an HTTP/ticket option.
The saved replay uses it, while retaining each tape's original path and read results.

The hospital example contains placeholders, `enabled: false`, no native installation
and no credentials. Its dry run reports `DRAFT_DISABLED`; it cannot execute.

Onboarding draft: approve the client's existing read-only identities and gateway
scope, name existing Key Vault references, fill the native installation and layer
references, validate offline, then arrange a separately approved first live check.
Do not reuse practice identities or infer bindings by similar names.
