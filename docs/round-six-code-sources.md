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

### Runtime qualification and approval controller, 2026-10-05

The committed context-bound checkpoint passed **1,945 regression tests**.
Runtime integration now treats the older retained-definition path as a candidate,
not verification. A missing, stale, differently scoped or forged proof blocks the
lower read. Code retrieval receipts preserve reported native/logical identity;
binding identity is the declared CodeSource ID and path. The served `.platform`
logicalId is the all-zero GUID, not the native item ID. Those are not substituted.

Declared samples are produced only from exact served copy mappings. The approval
controller verifies them before creating a separate immutable manifest-hash-pinned
approval. A reader pass requires that approval, validates all authorized locations
before fetching, shares one fetched unit across boundary proposals, and retains
failed verification attempts. Application verification uses the existing isolated,
guarded SQL route. Operator live setup and actual estate execution remain pending.

Offline re-analysis of the already-recorded definition response made **zero reads**.
The refined units expression refuses because whole-row deduplication includes
strings whose SQL comparison semantics have not been established as equivalent.
The serving units expression compiles under only its declared input catalogs but
has **not executed or verified**. The earlier fifteen syntactic compilations did
not test this type-equivalence precondition; they remain recorded, not acceptance.
An intermediate analysis supplied unused catalogs and returned an ambiguous-catalog
refusal; the subsequent scoped analysis corrects that driver error separately.
Append writes and conditional SQL target creation also refuse, since they cannot
establish equivalence of the whole target independently of prior target state.

DECIDED WITHOUT REVIEW: refused unestablished string equivalence rather than
assuming collation/padding or weakening the deduplication contract to earn a pass.
The fixture may consequently leave an inferred boundary unbound. That is a finding,
not authority to amend the code or expected outcomes during a live list.

Final full regression, unchanged archived column and the offline schema/rule report
must precede any live reader pass. Pot remains21/400, reserve60, ordinary stop340;
rolling248/1500 is last observed, not a new current-window reading. No live probe,
provider request, fixture change, identity change, refund or reset in this checkpoint.
Previous freezes remain invalid.

### Offline integration checkpoint, 2026-10-05

At `36fa77a`, **1,966 regression tests passed** (the preserved unittest log ends
OK). The subsequent exact-object-address correction passed nine verification-route
and nine application-quantity tests. The offline live-controller preflight found
that the declared copy target lacks a Delta location while its exact discovered
object ID is present. Approval now carries that object ID; the adapter resolves
only that exact object inside its declared workspace and connection. No path is
constructed from display names. The failed preflight remains preserved, with zero
reads; the corrected preflight resolves both authorized boundary samples.

Planner directory coverage remains two entries, one SQL object, 7,540 characters
before and after the manifest authorization projection, asserted by the golden
view test. Code credential declarations never enter worker configuration.
The control sample is an already-recorded ungrouped control-page cell. The declared
copy uses a newly recorded approval-sample address, not a historical backfill.
Neither receives a ticket figure as an expected value; precision is explicitly exact.

The initial archived-column invocation used the wrong private-input root and
correctly returned fifteen MISSING_PRIVATE_REPLAY_INPUTS blocks, with zero reads.
The corrected invocation uses the same pinned source files as the earlier passed
column; it is still running. This is an operator invocation correction, not tape
modification or a replacement live run. No live section has started.

## Offline report before the live section, 2026-10-05

Full runtime checkpoint: 1,966 tests passed. Subsequent exact-address correction: 18 focused tests passed. The reader tape test passed with live probes forbidden and the source file removed, reproducing its FALSIFIED receipt and all three charged synthetic physical requests; the new ledger output is canonical. Original ledger rows remain readable and unchanged. Static plain selection, two-key join, dropping filter, aggregation, rename, arithmetic, dynamic-model handoff and deliberately false-binding cases are covered offline. No estate or provider read in these tests.

The consumer ProposedBinding schema, verbatim:

```json
{
  "$defs": {
    "node": {
      "anyOf": [
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "COLUMN"
            },
            "name": {
              "maxLength": 128,
              "minLength": 1,
              "type": "string"
            }
          },
          "required": [
            "kind",
            "name"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "LITERAL"
            },
            "value": {
              "maxLength": 500,
              "type": [
                "string",
                "number",
                "boolean",
                "null"
              ]
            }
          },
          "required": [
            "kind",
            "value"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "DECIMAL"
            },
            "value": {
              "maxLength": 128,
              "pattern": "^[+-]?[0-9]+(?:\\.[0-9]+)?$",
              "type": "string"
            }
          },
          "required": [
            "kind",
            "value"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "ADD"
            },
            "left": {
              "$ref": "#/$defs/node"
            },
            "right": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "left",
            "right"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "SUBTRACT"
            },
            "left": {
              "$ref": "#/$defs/node"
            },
            "right": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "left",
            "right"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "MULTIPLY"
            },
            "left": {
              "$ref": "#/$defs/node"
            },
            "right": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "left",
            "right"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "DIVIDE"
            },
            "left": {
              "$ref": "#/$defs/node"
            },
            "right": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "left",
            "right"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "EQ"
            },
            "left": {
              "$ref": "#/$defs/node"
            },
            "right": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "left",
            "right"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "NE"
            },
            "left": {
              "$ref": "#/$defs/node"
            },
            "right": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "left",
            "right"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "GT"
            },
            "left": {
              "$ref": "#/$defs/node"
            },
            "right": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "left",
            "right"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "GE"
            },
            "left": {
              "$ref": "#/$defs/node"
            },
            "right": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "left",
            "right"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "LT"
            },
            "left": {
              "$ref": "#/$defs/node"
            },
            "right": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "left",
            "right"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "LE"
            },
            "left": {
              "$ref": "#/$defs/node"
            },
            "right": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "left",
            "right"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "AND"
            },
            "left": {
              "$ref": "#/$defs/node"
            },
            "right": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "left",
            "right"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "OR"
            },
            "left": {
              "$ref": "#/$defs/node"
            },
            "right": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "left",
            "right"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "SUM"
            },
            "operand": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "operand"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "COUNT"
            },
            "operand": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "operand"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "MIN"
            },
            "operand": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "operand"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "MAX"
            },
            "operand": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "operand"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "AVG"
            },
            "operand": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "operand"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "kind": {
              "const": "NOT"
            },
            "operand": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "operand"
          ],
          "type": "object"
        }
      ]
    },
    "relation": {
      "anyOf": [
        {
          "additionalProperties": false,
          "properties": {
            "columns": {
              "items": {
                "maxLength": 128,
                "minLength": 1,
                "type": "string"
              },
              "maxItems": 128,
              "minItems": 1,
              "type": "array"
            },
            "kind": {
              "const": "SCAN"
            },
            "table": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            }
          },
          "required": [
            "kind",
            "table",
            "columns"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "columns": {
              "items": {
                "additionalProperties": false,
                "properties": {
                  "expression": {
                    "$ref": "#/$defs/node"
                  },
                  "name": {
                    "maxLength": 128,
                    "minLength": 1,
                    "type": "string"
                  }
                },
                "required": [
                  "name",
                  "expression"
                ],
                "type": "object"
              },
              "maxItems": 128,
              "minItems": 1,
              "type": "array"
            },
            "input": {
              "$ref": "#/$defs/relation"
            },
            "kind": {
              "const": "PROJECT"
            }
          },
          "required": [
            "kind",
            "input",
            "columns"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "input": {
              "$ref": "#/$defs/relation"
            },
            "kind": {
              "const": "FILTER"
            },
            "predicate": {
              "$ref": "#/$defs/node"
            }
          },
          "required": [
            "kind",
            "input",
            "predicate"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "input": {
              "$ref": "#/$defs/relation"
            },
            "keys": {
              "items": {
                "maxLength": 128,
                "minLength": 1,
                "type": "string"
              },
              "maxItems": 128,
              "minItems": 1,
              "type": "array"
            },
            "kind": {
              "const": "DEDUPE"
            }
          },
          "required": [
            "kind",
            "input",
            "keys"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "how": {
              "enum": [
                "LEFT",
                "INNER"
              ]
            },
            "keys": {
              "items": {
                "maxLength": 128,
                "minLength": 1,
                "type": "string"
              },
              "maxItems": 128,
              "minItems": 1,
              "type": "array"
            },
            "kind": {
              "const": "JOIN"
            },
            "left": {
              "$ref": "#/$defs/relation"
            },
            "right": {
              "$ref": "#/$defs/relation"
            }
          },
          "required": [
            "kind",
            "left",
            "right",
            "how",
            "keys"
          ],
          "type": "object"
        },
        {
          "additionalProperties": false,
          "properties": {
            "columns": {
              "items": {
                "additionalProperties": false,
                "properties": {
                  "expression": {
                    "$ref": "#/$defs/node"
                  },
                  "name": {
                    "maxLength": 128,
                    "minLength": 1,
                    "type": "string"
                  }
                },
                "required": [
                  "name",
                  "expression"
                ],
                "type": "object"
              },
              "maxItems": 128,
              "minItems": 1,
              "type": "array"
            },
            "groups": {
              "items": {
                "maxLength": 128,
                "minLength": 1,
                "type": "string"
              },
              "maxItems": 128,
              "minItems": 0,
              "type": "array"
            },
            "input": {
              "$ref": "#/$defs/relation"
            },
            "kind": {
              "const": "AGGREGATE"
            }
          },
          "required": [
            "kind",
            "input",
            "groups",
            "columns"
          ],
          "type": "object"
        }
      ]
    }
  },
  "anyOf": [
    {
      "additionalProperties": false,
      "properties": {
        "boundary": {
          "additionalProperties": false,
          "properties": {
            "from_layer": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            },
            "to_layer": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            }
          },
          "required": [
            "from_layer",
            "to_layer"
          ],
          "type": "object"
        },
        "expression": {
          "additionalProperties": false,
          "properties": {
            "column": {
              "maxLength": 128,
              "minLength": 1,
              "type": "string"
            },
            "relation": {
              "$ref": "#/$defs/relation"
            }
          },
          "required": [
            "relation",
            "column"
          ],
          "type": "object"
        },
        "extractor": {
          "const": "STATIC"
        },
        "location": {
          "additionalProperties": false,
          "properties": {
            "cell": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            },
            "content_hash": {
              "pattern": "^[0-9a-f]{64}$",
              "type": "string"
            },
            "item": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            },
            "line_end": {
              "minimum": 1,
              "type": "integer"
            },
            "line_start": {
              "minimum": 1,
              "type": "integer"
            },
            "path": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            }
          },
          "required": [
            "item",
            "path",
            "cell",
            "line_start",
            "line_end",
            "content_hash"
          ],
          "type": "object"
        },
        "sources": {
          "items": {
            "additionalProperties": false,
            "properties": {
              "columns": {
                "items": {
                  "maxLength": 128,
                  "minLength": 1,
                  "type": "string"
                },
                "maxItems": 128,
                "minItems": 1,
                "type": "array"
              },
              "table": {
                "maxLength": 500,
                "minLength": 1,
                "type": "string"
              }
            },
            "required": [
              "table",
              "columns"
            ],
            "type": "object"
          },
          "maxItems": 16,
          "minItems": 1,
          "type": "array"
        },
        "target": {
          "additionalProperties": false,
          "properties": {
            "column": {
              "maxLength": 128,
              "minLength": 1,
              "type": "string"
            },
            "table": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            }
          },
          "required": [
            "table",
            "column"
          ],
          "type": "object"
        }
      },
      "required": [
        "boundary",
        "sources",
        "target",
        "expression",
        "location",
        "extractor"
      ],
      "type": "object"
    },
    {
      "additionalProperties": false,
      "properties": {
        "boundary": {
          "additionalProperties": false,
          "properties": {
            "from_layer": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            },
            "to_layer": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            }
          },
          "required": [
            "from_layer",
            "to_layer"
          ],
          "type": "object"
        },
        "confidence": {
          "maximum": 1,
          "minimum": 0,
          "type": "number"
        },
        "expression": {
          "additionalProperties": false,
          "properties": {
            "column": {
              "maxLength": 128,
              "minLength": 1,
              "type": "string"
            },
            "relation": {
              "$ref": "#/$defs/relation"
            }
          },
          "required": [
            "relation",
            "column"
          ],
          "type": "object"
        },
        "extractor": {
          "const": "MODEL"
        },
        "location": {
          "additionalProperties": false,
          "properties": {
            "cell": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            },
            "content_hash": {
              "pattern": "^[0-9a-f]{64}$",
              "type": "string"
            },
            "item": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            },
            "line_end": {
              "minimum": 1,
              "type": "integer"
            },
            "line_start": {
              "minimum": 1,
              "type": "integer"
            },
            "path": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            }
          },
          "required": [
            "item",
            "path",
            "cell",
            "line_start",
            "line_end",
            "content_hash"
          ],
          "type": "object"
        },
        "sources": {
          "items": {
            "additionalProperties": false,
            "properties": {
              "columns": {
                "items": {
                  "maxLength": 128,
                  "minLength": 1,
                  "type": "string"
                },
                "maxItems": 128,
                "minItems": 1,
                "type": "array"
              },
              "table": {
                "maxLength": 500,
                "minLength": 1,
                "type": "string"
              }
            },
            "required": [
              "table",
              "columns"
            ],
            "type": "object"
          },
          "maxItems": 16,
          "minItems": 1,
          "type": "array"
        },
        "target": {
          "additionalProperties": false,
          "properties": {
            "column": {
              "maxLength": 128,
              "minLength": 1,
              "type": "string"
            },
            "table": {
              "maxLength": 500,
              "minLength": 1,
              "type": "string"
            }
          },
          "required": [
            "table",
            "column"
          ],
          "type": "object"
        }
      },
      "required": [
        "boundary",
        "sources",
        "target",
        "expression",
        "location",
        "extractor",
        "confidence"
      ],
      "type": "object"
    }
  ]
}
```

The comparison rule, verbatim:

> Compile both expressions before either read. Both observations must be completed, bound to the same retained context, cell address and explicitly declared precision. Compare their numeric quantities at that precision, or BLANK with BLANK. Equal is VERIFIED only for that sampled quantity and scope; unequal is FALSIFIED. A compilation, read, identity or context failure is UNVERIFIED, never evidence of equality. No inferred tolerance.

Specific pre-live limits: filtered/grouped lower quantities, undeclared division semantics, string comparison/deduplication equivalence and append/conditional writes refuse. Embedded literal seed data is withheld from model fallback. The serving units expression compiles but is unexecuted; the refined expression refuses compilation. These are not verification verdicts from data. Both measurements and inferred claims remain sampled and SNAPSHOT_UNVERIFIED unless value-bound snapshot evidence establishes otherwise. The unchanged archived column is still running under pinned historical producers; it is not current-engine acceptance.

DECIDED WITHOUT REVIEW: approval retains the declared application-to-landing edge and enables the two original code boundaries in a separate experimental manifest. There were no explicit original notebook bindings to remove: they were legacy retained-definition candidates. The verifier will use the saved control-page cell and exact precision without an authored target value. The isolated copy receives a new approval sample address, not an alteration of old receipts. A fresh discovery scan is required to approve the changed whole-config policy; reusing or narrowing its old hash was rejected.

Windows before live: Round Six21/400,60 reserved, ordinary stop340; rolling248/1500 last observed. No claim that this stale observation is the current rolling total. No live reader or inferred ticket has executed.

### Policy approval correction before live, 2026-10-05

The earlier pre-live plan said a fresh scan was required. An audit of the existing approval path and the two manifests established that the only changes are inference.enabled and the two may_infer_from_code switches: reader identities, credentials, workspace, connections, schema, layers, budgets and fixture states are unchanged. DECIDED WITHOUT REVIEW: re-approved the exact retained metadata through Discovery under the new whole-config hash, as the prior round did, rather than recollect unchanged metadata and consume exploratory requests. No hash scope was narrowed. This is approval, not new remote metadata-freshness evidence. Original contexts and recorded runs remain unchanged; new projected contexts are separate.

Retained context `785a8fea-f49c-4e7e-b48f-1cae765410dc`, hash `1676c296228589d96856d508a3981c4f8c756f1474c6a06e5eca0364bf17bd9a`. New approved context `8741fd7e-548b-4d0a-9c0d-378f3fd24a00`, hash `739af474020bedf1dac0e9268229542834e853ee9260619bd913968e1bdb6c84`; whole configuration hash `bbd11984ded8f1e3d4053fb7e2a21b8077b52db153c1f9c9c9c7cb4579b928b7`. Zero physical or diagnostic reads. Before/after approval listings and new model-context IDs are recorded locally in inferred-policy-approval.json. The separate sampled lineage approval has not yet been earned; it still requires the declared copy comparison.

All fifteen archived tapes now passed, zero network calls and physical requests. Each used its pinned historical producer; the inferred column remains unexecuted. Round Six21/400, reserve60, ordinary stop340; rolling213/1500 at the fresh pre-live local usage check. Final current regression remains running. Draft PR #406 contains this implementation, not a completed live claim.

### Final offline checkpoint, 2026-10-05

The final current implementation at `3e6c94f8b0fe896df81a4dd4370fca063c34a3ee` passed **1,967 regression tests** in 599.822 seconds, actual subprocess exit zero. The retained fifteen-tape archived column passed **15/15**, with zero estate reads, under its pinned historical producers. This establishes the offline checkpoint, not a live inferred-lineage pass. The authorized single sampled reader control started after this checkpoint; its result is pending.

### Live reader control, 2026-10-05

The single authorized control completed its extraction and recording, **not successful inference**. Its declared application-to-landing sample agreed at **7,661 on both sides** and earned sampled VERIFIED, ENGINE_INDEPENDENT; both attestations were PARTIAL with connection unattested, and snapshots remain SNAPSHOT_UNVERIFIED. No identity or permission changed.
The two original boundaries emitted fifteen STATIC proposals: six into the refined table, nine into serving. **All fifteen are UNVERIFIED.** Refinement units refuses cross-language string deduplication; serving units read 8,765 at the target but its source probe failed. Thirteen other columns are outside the selected measure and receive explicit compilation refusals. No extra column is silently promoted to a binding.
Every proposal uses CodeSource `fixture-code`, path `7ccafe59-0460-4c8a-a691-bfdfa75a2b25/notebook-content.py`, cell `1`, content SHA-256 `313e90c9e25e1e1e844aac5383bfb3c01c4bd11684faeaabf48c207c623cf0c1`. Location line ranges are shown below.
| Boundary | Target column | Lines | Verdict | Reason |
| --- | --- | --- | --- | --- |
| original-landing ? original-refined | movement_id | 14?14 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |
| original-landing ? original-refined | warehouse_id | 14?14 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |
| original-landing ? original-refined | product_id | 14?14 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |
| original-landing ? original-refined | units | 14?14 | UNVERIFIED | Cannot compile faithfully: Deduplication equivalence is not established across code and execution languages; no assumed string collation or padding |
| original-landing ? original-refined | event_day | 14?14 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |
| original-landing ? original-refined | movement_type | 14?14 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |
| original-refined ? original-serving | movement_id | 18?18 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |
| original-refined ? original-serving | warehouse_id | 18?18 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |
| original-refined ? original-serving | product_id | 18?18 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |
| original-refined ? original-serving | units | 18?18 | UNVERIFIED | The source read did not complete. |
| original-refined ? original-serving | event_day | 18?18 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |
| original-refined ? original-serving | movement_type | 18?18 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |
| original-refined ? original-serving | rate_version | 18?18 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |
| original-refined ? original-serving | unit_cost | 18?18 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |
| original-refined ? original-serving | movement_value | 18?18 | UNVERIFIED | Cannot compile faithfully: This proposal is not the quantity established by the selected cell; no substitute measure is invented |

Serving source failure is retained as **OSError, errno22, ?Invalid argument?, operation flush, tape_worker.py line32**, worker timeout150 seconds. The recorded worker-start to failed-flush interval exceeds the configured150-second deadline, but the tape does not directly establish which event closed the pipe. This is a recording/worker failure, not a numerical disagreement or proof of a platform query refusal. Recording expanded to128,269,844 bytes and465 events. Its timing contribution is an open finding; the failed request remains charged. No retry, deadline extension, or rule change.
The control admitted **8/12 diagnostic operations**: four endpoint metadata operations and four SQL verification probes. It charged **25 physical requests**, including two pre-warm controls, two local code/identity reads and nine permission guards (all established, zero reused). The last physical reservation is UNCERTAIN. Three quantity probes succeeded; one failed. Zero provider/planner calls. The pre-warm first encountered40613, waited5 seconds, then connected; it is control evidence, not a diagnostic.
Windows: Round Six **21?46/400**,60 reserved, ordinary stop340. The actual live rolling observations were **200?220/1500**; the earlier213 preflight was taken before further historical requests expired, so adding25 to it is not the current rolling total. All original observations, errors, receipts and the sealed tape remain unchanged.
DECIDED WITHOUT REVIEW: proceed to the first requested ticket once with the failed inferred bindings retained, rather than retrying the reader or granting a bare inferred label. Stop the live ticket list on the first changed outcome, as instructed. No inferred acceptance pass or15?2 claim.

### First changed outcome: live list stopped, 2026-10-05

Family A, session `572ffd5b-d064-405a-b756-8227aa453b81`, completed intake, procedure and synthesis; its sealed tape validated. The original unchanged ticket passed intake in one call. There were **zero investigation planner calls**, zero definition-judge calls and one successful synthesis call. The procedure compared native presentation8,765 against serving SQL8,765, ENGINE_INDEPENDENT, PARTIAL surface coverage (connection unattested), SNAPSHOT_UNVERIFIED. It could not cross serving?refined because the current ledger contains no VERIFIED binding for that quantity.
Expected **TRANSFORMATION_LOGIC**; observed **CONSISTENT_TO_BOUNDARY**. Offline grading, zero reads, reports STRUCTURE:boundaries, STRUCTURE:layers_reached and STRUCTURE:outcome. This is the requested first changed-outcome stop. It is not an acceptance pass, and the expectation was not changed. The tape confirms the path was truncated at the failed serving units binding, before the earlier divergent boundary could be read. This finding follows from the retained UNVERIFIED result; it does not prove the transformation ceased to exist.
The run charged **9 physical requests**, **3/12 diagnostic reads**, **3 permission guards**, zero guard reuse. Physical categories: one DAX, four SQL (including guards), four other (code and ingestion metadata). All nine requests completed. Round Six **46?55/400**; rolling **220?223/1500** in the recorded before/after windows. No budget increase, replacement attempt, write, identity or permission change. No fixture mutation occurred, so no restoration mutation was needed.
Remaining families B?I, EMPTY,16 and both requested source controls **did not run**, because the first outcome changed. Source latency/unreachable were not requested as fresh repeats and are not relabelled as inferred passes. Their archived tapes remain evidence under their original producers. The second column is not earned; **15/15?2 is not achieved**.
| Ticket | Archived declared column (pinned producer) | New inferred column |
| --- | --- | --- |
| family-A | PASSED | FAILED ? changed outcome |
| family-B | PASSED | NOT RUN ? stopped at A |
| family-C | PASSED | NOT RUN ? stopped at A |
| family-D | PASSED | NOT RUN ? stopped at A |
| family-E | PASSED | NOT RUN ? stopped at A |
| family-F | PASSED | NOT RUN ? stopped at A |
| family-G | PASSED | NOT RUN ? stopped at A |
| family-H | PASSED | NOT RUN ? stopped at A |
| family-I | PASSED | NOT RUN ? stopped at A |
| reproduction-16 | PASSED | NOT RUN ? stopped at A |
| reproduction-empty | PASSED | NOT RUN ? stopped at A |
| source-consistent | PASSED | NOT RUN ? stopped at A |
| source-gap | PASSED | NOT RUN ? stopped at A |
| source-latency | PASSED | NOT REPEATED ? outside requested13 |
| source-unreachable | PASSED | NOT REPEATED ? outside requested13 |

Both outputs, verbatim, from the preserved live result:

Business output:

```text
You asked: In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.
Answer to your question: Partly answered.
Regarding the requested comparison: The compared path agreed through the named checked depth; the application beyond it was not read, so the remaining question belongs to the application owner.
What the investigation established:

The checked reported calculation value was 8,765. A separate check of the serving data agreed. This rules out a difference at that checked boundary, but does not prove the original records are correct. The original entries, unchecked selections, update timing and intended business rules remain outside what these comparisons establish. For the reported calculation and the serving data, the two checks used different calculation engines. Recommended action: Ask the owner of the unchecked part of the process to investigate the remaining gap.
```

Technical output:

```text
You asked: In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.
Answer to your question: Partly answered.
Regarding the requested comparison: The compared path agreed through the named checked depth; the application beyond it was not read, so the remaining question belongs to the application owner.
What the investigation established:

Measure: Handled Quantity.
B1 agrees: L1 (movement values in warehouse gold e1b8e1; role SERVING, upstream input) 8,765 -> L0 (Activity in Warehouse Operations e1b8e1; role SEMANTIC, downstream output) 8,765.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind FIGURE_DIFFERENCE.

The recorded check matches the quantity at L1 (SERVING) with the quantity at L0 (SEMANTIC), and the value carries across that layer step without change.

Layers:
L0 - Activity in Warehouse Operations e1b8e1; role SEMANTIC: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1; role SERVING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1; role REFINED: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipt 18a3a3ae-93e7-4268-9ee7-f7c3db4f00c4).
- Unattested connection on L1 (receipt ef90a52f-ada9-4c10-99f6-35bbfccc3683).
- SNAPSHOT_UNVERIFIED for B1: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L1; stopped because no lineage.
- Unchecked L1 -> L2: Neither a declared nor a current verified inferred binding matches the selected quantity and scope..
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.

Recommended action: Ask the owner of the unchecked part of the process to investigate the remaining gap.
```

### End-of-round findings and decisions

The static reader extracted actual code declarations but did not recover an executable inferred boundary. Refinement needs established deduplication semantics; serving needs a source probe that completes within its existing worker contract. The128 MB tape and budget materialization overhead are measured operational findings, not permission or numerical failures. No live attempt was repeated to conceal either. The completed A output remains scoped to serving; its header refers the remaining question to the application owner even though this original branch has not established an application pointer. That ownership phrasing is an open output finding, not proof that the application owns this particular missing boundary.
DECIDED WITHOUT REVIEW: approved inventory-baseline against the new projected model context `841e425e-fe17-4bb0-9d06-b4623f49de5b`, hash `ed63c086dbfac8dd2421268223358394406f90ba6974b86441ee8d194257bb0f`, with the explicitly retained policy approval and unchanged fixture as provenance. Reusing the earlier whole-config approval or claiming a fresh recollection was rejected.
Optional section4 changes were deferred. No core allow-list, ticket-history or platform-limit behavior was changed during the live attempts. Manifest reader/setup/STALE documentation is included in this implementation. Prior freezes remain invalid and no unfamiliar-domain claim is made.
Draft PR #406 contains the implementation and these preserved negative results. Its existing hosted archived check passed15/15; the new inferred column failed on its first ticket, so the PR is not represented as a completed two-column gate and is not merged.
Final recorded windows: **Round Six55/400**,60 reserved, ordinary stop340; **rolling223/1500** at21:41:03 UTC. Failed/uncertain requests remain charged. Original receipts, contexts, prior tapes and expectations remain untouched.
