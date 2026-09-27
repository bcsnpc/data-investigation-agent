# Rendered technical facts and shared response vocabularies

2026-09-27. #282 merged after six green checks. Both prior synthesis failures remain
unaltered. This engine change invalidates earlier freezes; it makes no unfamiliar-
domain claim. No guard, permission, estate, diagnostic cap or ordinary allowance
is changed.

## Guard finding, before implementation

The SQL guard does not prove that a SQL session has a read-only switch. Database
`sys.fn_my_permissions(NULL, 'DATABASE')` rejects effective permissions outside
the existing read/metadata allowlist. `sys.fn_my_permissions(@object, 'OBJECT')`
rejects permissions other than SELECT and VIEW DEFINITION for each object.
Those checks inspect write-capable permissions at two scopes; they are not three
identical checks. A separate identity self-report identifies the live principal
and database. ApplicationIntent=ReadOnly is not treated as enforcement.

The cache already reuses the database check per connection/credential/database
and the object check per exact object in that scope. The prior runs crossed two
databases, so neither permission check was reusable. Keep that cost and the
object-specific checks unchanged. Actual SELECT ability is established by the
read itself, not by the negative write-permission checks.

## Technical prose

The old engine itself supplied the empty sentence about a fixed boundary account.
It was not spontaneous model phrasing. The new technical output starts with an
engine-rendered spine: the discovered measure name, each input/output layer,
receipt-backed quantities, agreement/divergence and the exact divergent boundary.
The name is captured from the approved model context, not guessed from ticket text.
Historical contexts without the name display the measure identifier explicitly.

The model supplies bounded mechanism and uncertainty commentary. The schema and
local validation share the same restrictions against repeating numeric quantities
or path ordering, and against referring to an account instead of explaining its
contents. Mandatory claim, surface and snapshot limitations remain rendered from
the original evidence. Nothing is silently truncated.

Reference run 3d2c5bf0 correctly stated the report/source agreement and deeper
8,765/7,661 difference, but its final model paragraph was cut off. The new renderer
restores those concrete comparisons and direction deterministically without
reintroducing truncation or asking the model to reconstruct ordering.

## Enumerated-vocabulary audit

| Contract field | Source and treatment |
| --- | --- |
| Synthesis business text | Exact deterministic `business_text` enum; exposed from the same generated schema used by validation. |
| Synthesis evidence IDs, all three statement locations | IDs selected from the frozen evidence; the exact schema enums are exposed, not separately maintained lists. |
| Synthesis technical text | Removed the fixed-template enum. Bounded mechanism/limits prose; engine renders path facts. |
| Synthesis additional limitation text | Removed the false singleton enum. Bounded free prose; mandatory limits are engine-owned and not round-tripped through the model. |
| Judge judgment | EXPLAINS / DOES_NOT_EXPLAIN / INDETERMINATE come from the same SCHEMA consumed by `validate`; producer instructions expose its exact enum. |
| Judge explanation/limitation | Free prose with shared consumer bounds and sentence-completion validation; no enumerated vocabulary. |
| Outcome, action, capabilities, roles, visibility/baseline and intent enums | Original procedure-owned assessment, absent from the live narrative response schema. The model cannot redeclare them. Historical local injected-provider compatibility remains validated separately. |

`contract_vocabulary` recursively exposes every enum in each exact wire schema,
including future nested fields. Tests traverse all enums, verify producer and
consumer identity, and ensure a new enum appears automatically. No duplicated
producer vocabulary is maintained. The provider still receives strict schema
output; local validation remains mandatory because prior responses violated the
wire schema. Supplying identical vocabularies removes contract drift, not the
possibility of a provider malfunction.

## Context cost and coverage

Saved R1 synthesis context audit: directory entries 0 -> 0; SQL directory objects
0 -> 0 (this digest has no search directory). Evidence entries 7 -> 7; sealed SQL
quantity entries 2 -> 2, byte-identical evidence list. Payload characters
15,550 -> 15,586 for the measure-name field. Instructions 1,450 -> 3,646 characters
include generated enum choices. Recorded request 21,544 bytes; reconstructed new
request 25,026 bytes. These are local shaping measurements, not a live response.
No entry is dropped to make room. Tests also retain a populated directory unchanged.

## Validation and live work

Focused vocabulary, synthesis, path, prose, bounds and freshness tests pass.
Full regression and two authorized live repeats are pending. The user approved
20 new batch credits, ten per run with two-hour expiry. Diagnostic cap remains
four; ordinary allowance remains 60. Each grant, use and expiry will be recorded.
