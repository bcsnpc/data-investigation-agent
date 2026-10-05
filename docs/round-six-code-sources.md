# Round Six B — code sources and transformation reader

2026-10-05, America/Chicago. This report continues the human's
`round-six-b-code-sources.md`; the original Round Six reader and live-gate work
remain required. The earlier write-scope stop is preserved in
[Round Six A](round-six-transformation-reader.md), and is superseded only by
the explicit code-identity decision below. No investigation identity changed.

## Section 2 checkpoint: identity, definition fetch and credential scan

The human authorized three sources: `GIT_REPOSITORY` (recommended read-only
repository access), `LOCAL_PATH` (exported code), and `PLATFORM_ITEM_API` (a
separate write-scoped code identity, explicitly accepted as a limitation).
The identity decision was to create `investigator-code-reader`, Contributor
only on the fixture workspaces, code-definition reads only, never investigation
execution. All pre-existing readers retain their scopes.

Created application `2dd2f5c3-f7af-4804-b79e-6019e63efa60`, application object
`050b0404-80bf-4b36-a06c-ea90a94e71ca`, service-principal object
`dc89155f-9a9a-4daa-9c20-7eff55818ccd`. Credential storage is the existing local
Windows DPAPI mechanism, expires 2026-11-04; no credential enters the repository,
reports or tapes. No Graph API permission was added to the application.

Before listing: no role assignment for that service principal. Exact grant:

```http
POST https://api.fabric.microsoft.com/v1/workspaces/149f8d99-1c66-4a0a-9624-759be002bb60/roleAssignments
```
```json
{"principal":{"id":"dc89155f-9a9a-4daa-9c20-7eff55818ccd","type":"ServicePrincipal"},"role":"Contributor"}
```

After listing, exactly this assignment for the new principal:

```json
{"id":"dc89155f-9a9a-4daa-9c20-7eff55818ccd","principal":{"id":"dc89155f-9a9a-4daa-9c20-7eff55818ccd","displayName":"investigator-code-reader","type":"ServicePrincipal","servicePrincipalDetails":{"aadAppId":"2dd2f5c3-f7af-4804-b79e-6019e63efa60"}},"role":"Contributor"}
```

The exact unchanged before/after listings and control-plane requests are sealed
locally in `code-reader-identity.json`, with its hash in the ledger. Creation,
credential creation and role verification used seven physical control requests.
No identity/grant error occurred. An initial Python dependency preflight failed
before authentication or any identity operation; it remains recorded separately.
The permission model follows Microsoft's
[workspace-role API](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/add-workspace-role-assignment).

Both requested transformation hops are in notebook
`7ccafe59-0460-4c8a-a691-bfdfa75a2b25`, workspace
`149f8d99-1c66-4a0a-9624-759be002bb60`. The definition contains explicit writes
to landing `09ba0ef9…`, refined `ba24d52c…` and serving `b0ab76f7…` containers.
The original and isolated app-load publication scripts declare this same
workspace. There was no second workspace ID to grant or second notebook to fetch.

The first definition POST returned HTTP202, with regional operation Location
and Retry-After20. The new transport refused its own overly narrow host/wait
assumptions before getting code. That failed attempt, three physical requests
including authentication, remains unchanged. A separately recorded continuation
queried that **same** operation on the documented public API, then obtained its
result; no second definition POST. It used four physical requests including
authentication. Microsoft's [operation contract](https://learn.microsoft.com/en-us/rest/api/fabric/articles/long-running-operation)
and [state route](https://learn.microsoft.com/en-us/rest/api/fabric/core/long-running-operations/get-operation-state)
support polling by operation ID. The transport now constructs the public API
URL and never sends credentials to a response-supplied regional host; a regression
test covers the recorded twenty-second interval.

| Exported part | Bytes | SHA-256 |
| --- | ---: | --- |
| notebook-content.py | 20,197 | `313e90c9e25e1e1e844aac5383bfb3c01c4bd11684faeaabf48c207c623cf0c1` |
| .platform | 312 | `eaa125159f007e0c73ba73b5d9baedffe9d0f23bd6602ba0915cae7277465ef3` |

Fetched 2026-10-05T18:15:08.544777Z as the new service principal, whose token
object/application IDs were checked. `fixture-code/7ccafe59…/` retains those
bytes and separate provenance metadata. All eight scan patterns returned zero
matches on both decoded parts: password=, secret=, token=, sig=,
SharedAccessSignature, private-key headers, AccountKey= and JWT token shapes.
Identifiers/connection definitions are permitted. The notebook also contains
synthetic fixture seed rows; it is not customer data. Those rows must not become
runtime evaluator truth or a model-fallback answer oracle.

The successful continuation tape replayed in a copy of its pre-read catalog,
including admission/settlement decisions, with the HTTP requester set to fail
if invoked. Zero replay requests. Original failed and successful artifacts are
preserved under `.local/round-six-20261005/`; local tape evidence is not committed
as raw investigation artifacts. No investigation run occurred at this checkpoint.

## Implementation and current verification

The manifest has a closed, per-kind CodeSource and boundary code locations.
API sources require `CODE_READ_REQUIRES_WRITE_SCOPE` and a separately declared
code identity. Neither code locations nor credentials enter investigation worker
configuration. Unrecognized source kinds and extra fields refuse with field
names. Normalization retains code cells and locations without executing code.
Local metadata presence is taped, so deleting both export files after recording
cannot silently lose identity during replay. Local file and sidecar reads each
count as a physical retrieval; remote transports meter each HTTP request.

Offline: nine source-contract tests, five definition-transport tests, three Git
transport tests, nineteen manifest tests and three platform-neutrality tests pass.
Manifest golden-context comparison: directory entries2→2, SQL entries1→1,
payload7540→7540 characters. Synthetic tests do not access the estate. The
actual fixture manifest declares LOCAL_PATH; inference remains disabled until
the extractor/verifier exist. Prior engine freezes are invalidated by these changes.
Git-hosted fixture verification, the full transformation reader, inferred-lineage
ledger and second fifteen-ticket column are not yet completed.

## DECIDED WITHOUT REVIEW

- Grant one actual workspace: both installations' declared publisher workspace
  is the same149f8d99 ID. Rejected guessing a second ID or broadening to another
  workspace merely to match the wording “two workspaces.”
- Fetch one combined notebook once. Rejected fetching an unrelated notebook
  or issuing duplicate POSTs for two hops located in one definition.
- Continue the already accepted operation after the transport's protocol
  refusal. Rejected reissuing the definition fetch; all charges/failures retained.
- Keep the original fixtures' inference disabled until verification exists.
  Rejected presenting a code-location declaration as a verified binding.

## Windows at this checkpoint

Round Six before code fetch:7/400; after failed initiation and successful
continuation: **14/400**, ordinary-work stop340, restoration reserve60.
Rolling at 18:15UTC: **241/1500** in24h (aging records account for its decrease).
Diagnostic cap12 unchanged. Zero investigation planner calls; no counter reset,
refund, new data mutation or investigation-reader elevation.
