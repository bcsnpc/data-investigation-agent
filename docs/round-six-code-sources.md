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
Hosted local/Git verification passed in Actions run37355558213 at
`6a1e00c83ea7c48113894d48b3ba57fddf2959f3`, both yielding the fetched hash.
It consumed exactly two local-file retrievals and two repository GETs. Four
slots were reserved before dispatch and settled afterward, no refunds. The full
transformation reader, inferred-lineage ledger and second fifteen-ticket column
are not yet completed. Definition-API replay is currently local, not hosted.

CI additionally re-executes the definition transport against a fixture-only
HTTP excerpt from those preserved recordings (`api-recorded-operation.json`).
It checks the exact three method/endpoint pairs and yields the fetched code hash,
without network or authentication. The excerpt is explicitly derived and hash
links to both original attempts; it is **not** represented as a complete private
budget tape. Original tape replay (admission and settlement included) passed
locally. No raw catalog, credential, authentication body or provider content is
committed as fixture transport material.

The first ordinary CI run failed the scoped-inventory structural test because
the new code-source validator reused a reserved function name. Renamed it to
`validate_sources`; the original test and report-inventory validation remain
unchanged. Failure logs retained; no acceptance expectation was changed.

The Git test manifest is `infra/estates/fixture-code-git.json`, pointing at this
repository's code-source branch. Hosted verification uses the built-in Actions
secret `GITHUB_TOKEN`, explicitly scoped by workflow `contents: read`; it is
ephemeral, no write scope or new long-lived token is stored. The separate job
compares local and pinned-commit Git content, retains source receipts on failure
as well as success, and caps that batch at four physical retrievals (two local
files and two repository requests). A branch ref is pinned to the hosted checkout
commit. Other hosts are explicitly unavailable with this installed adapter.

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
- Use the existing generated read-only Actions secret `GITHUB_TOKEN` for CI.
  Rejected storing the local operator's broader GitHub credential as a code token.
  No new standing credential or investigation identity scope is introduced.
- Commit only fixture definition HTTP projections for the hosted API-path test,
  explicitly marked as a derived transport excerpt. Rejected committing private
  live budget/catalog artifacts or silently describing an excerpt as a full tape.
  The actual successful full tape remains sealed and separately replayed locally.

## Windows at this checkpoint

Round Six before code fetch:7/400; after failed initiation and successful
continuation: **14/400**, ordinary-work stop340, restoration reserve60.
The hosted source check adds four: **18/400** initiated/reserved and settled.
Rolling after that check: **245/1500** in24h (aging records account for its decrease).
Diagnostic cap12 unchanged. Zero investigation planner calls; no counter reset,
refund, new data mutation or investigation-reader elevation.


## Reader implementation checkpoint ? 2026-10-05

#405 merged at41ebe282eff19f9b88bc580644ba0e469d5b3e97. Its seven checks and
the actual main checks are green. The code-source transport work is delivered;
the full transformation reader and inferred acceptance column are not yet earned.

The new neutral core extracts bounded read/transform/write expressions from
Python and SQL, with static-first model handoff. Selection, two-key joins, filters,
aggregation, rename, arithmetic and whole-row deduplication have offline tests.
Partial-key deduplication refuses because the surviving row is unspecified.
Literal-seeded writes have no inferred upstream source. Multi-cell notebook
locations retain cell-local line spans. A model cannot claim STATIC provenance,
verification, a different target or a location outside retained code.

The consumer schema is committed verbatim in
[transformation-proposed-binding.schema.json](transformation-proposed-binding.schema.json).
Its verifier comparison rule, verbatim:

> Compile both expressions before either read. Both observations must be completed, bound to the same retained context, cell address and explicitly declared precision. Compare their numeric quantities at that precision, or BLANK with BLANK. Equal is VERIFIED only for that sampled quantity and scope; unequal is FALSIFIED. A compilation, read, identity or context failure is UNVERIFIED, never evidence of equality. No inferred tolerance.

The SQL verification route calls the existing guarded process probe and carries
the actual cell address, original receipt, values and quantity-bound attestation.
It refuses filtered/grouped lower reads and cross-connection expressions. It
does not substitute the transformed source expression into the ordinary walk.
An immutable lineage ledger retains VERIFIED/FALSIFIED/UNVERIFIED attempts;
changed or unavailable code hashes yield STALE views without rewriting rows.
Selection prefers declared bindings and refuses different context/cell/precision
or ambiguous verified expressions. The manifest approval and runtime resolver
integration remain pending; these modules are not yet a live capability.

### Dated replay qualification

The earlier successful definition continuation was replayed with its budget
events under the current transport. Its v3 code_reader tape did not pin a
committed producer revision. It is not archived-producer replay, and the previous
local replay claim must be read with that limit. The original tape is unchanged.
The new v4 recorder requires a clean committed producer for code_reader and
code_verifier; older versions remain readable under their original rules.
The committed HTTP excerpt remains explicitly a derived transport projection.

### Static fixture inspection and accounting correction

A direct local code inspection bypassed the meter once. That request was charged
retrospectively and the inspection repeated through the metered source (code and
.platform, two requests). All three remain charged. The script found17 writes:
six literal-seeded and11 read-backed. Selected targets produced six and nine
column proposals, with ten other read-backed writes visible in each extraction.
These are proposals, not verified bindings. No estate data probe occurred.

Round Six21/400, ordinary stop340, reserve60; rolling248/1500 last observed.
No diagnostic/provider request, counter reset, refund or new identity change.
Prior engine freezes are invalid. Full regression and archived15-tape replay
are pending on this implementation checkpoint; no live section starts here.


### Resumed checkpoint, 2026-10-05

The interrupted full regression completed at `fa809a3`: **1,933 tests passed**.
The fifteen unchanged archived tapes also passed, with zero network calls and
zero physical requests. Each replay used its historical producer revision;
this is the existing column, not the new inferred-reader column.

Post-checkpoint tests exposed and corrected two integration hazards: the SQL
probe returns a quantity object containing a numeric string, rather than a
primitive integer; and an older verified ledger sample could be selected after
a later falsification of the same proposal and sample. Both now have regression
tests. Unrelated proposed columns cannot reuse the selected measure's cell.
Nonfinite literals and division without declared type/zero semantics refuse.
Endpoint resolution follows exact locations and container endpoint declarations,
never display-name matching.

A separate immutable approval record now invokes the same verifier for every
configured declared edge. Missing samples refuse before reads; failed attempts
remain in the ledger, and a falsified edge prevents approval with both values.
Reopening an approval recomputes its verdict from the original observations and
checks the whole manifest hash. Synthetic approval tests pass. Production
approval orchestration, application-side verification and runtime resolver
integration remain unfinished. No live investigation was attempted.

These changes invalidate previous engine freezes. Round Six remains **21/400**,
ordinary stop340, reserve60; rolling **248/1500 last observed**, not a new
control-plane read. No scope, allowance, fixture or counter changed.

A further focused check found that a verifier could annotate the caller's context
without comparing it to the actual probe context. Compilation now requires the
installed model's retained context, and the result must retain the same context
and cell address from the original probe evidence. Mismatches remain failed with
the original address visible; two focused regression tests cover this.

The resumed broad regression log was interrupted after these code changes; it is
preserved at `.local/round-six-20261005/resumed-reader-regression.txt` and is not a
pass. Focused route tests8/8, independent lower-read tests18/18 and process read
receipt tests3/3 passed after the change. No investigation or estate read.
