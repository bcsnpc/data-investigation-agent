# Round Nineteen B: final graph coverage

Readback: 2026-10-13 18:20:17 UTC. This is a read-only PostgreSQL and
hash-verified private definition readback, followed by offline analysis. No
estate/model requests or graph changes were made for this report.

| Estate | Baseline nodes / edges | Final nodes / edges | DECLARED edges before → after | UNKNOWN edges before → after | Original starts present |
|---|---:|---:|---:|---:|---:|
| Fixture | 1,163 / 1,696 | 1,144 / 1,759 | 1,568 → 1,650 | 128 → 109 | 76 / 76 |
| Billing | 388 / 759 | 402 / 789 | 725 → 741 | 34 → 48 | 7 / 7 |

Both snapshots have zero VERIFIED edges. All 83 original visual/slicer starts
remain. Zero starts reach a declared system-of-record column, zero reach a
terminal physical column, and zero have a complete VERIFIED path. These are
coverage results, not proof that the business values are incorrect.

## Three concrete blockers

1. **The semantic-to-storage binding is absent.** Sixty-six fixture starts and
   all seven billing starts encounter `NO_DECLARED_SOURCE_CONTINUATION`.
   Sixty-two fixture starts reach semantic-column leaves and 52 reach
   semantic-table leaves (overlapping sets); all seven billing starts reach
   both. For example, `Invoiced Amount` reaches `Billing[amount]`, node
   `43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b`,
   whose retained `sourceColumn` is `amount`, but which has no outgoing
   dependency edge. The retained Billing table partition says
   `mode=directLake`, `type=entity`, `expressionSource=BillingServingSource`,
   `schemaName=gold`, `entityName=invoice_activity`. The current extractor's
   `model_parts` handles M partitions, but does not bind these entity
   partitions to the physical table/column identities. Physical columns
   exist elsewhere: 272 fixture and 138 billing SqlColumn/WarehouseColumn/
   LakehouseColumn nodes. They are not reachable from these starts. Therefore
   terminal-physical zero is a genuine missing graph link, not an artifact of
   requiring every branch to succeed. None of the columns is explicitly
   marked `system_of_record`; that separate declaration gap also prevents
   claiming source coverage.
2. **Twelve fixture visuals have no supported explicit field reference.**
   Their UNKNOWN edge says exactly: `No supported explicit field reference
   was found in the retained visual query.` For example, visual
   `6b1bb066d22d5e9a9cc3`, node
   `2f8ecca7495ba81df990d98132832e5ca398073eecf7f1136ba74cb6c391b20f`,
   stops at boundary
   `86d94d7bd92f52028d30509e9906e28ba9d43fc81609211676a8ef8aa63316bd`.
   This is an unsupported retained-query shape, not evidence of a missing
   visual, a permission error, or an incorrect measure.
3. **One reached calculation has unresolved engine endpoint kinds.**
   `Fixture Calculated Quantity`, node
   `77bacc9a5e280e87224220e0684650c53e5862758c7527b749d4a9bab104a52c`,
   retains an UNKNOWN calculation gap. Its successful CALCULATIONS receipt
   actually contains rows21/22: the measure references `RoundTenCalculated`
   with `REFERENCED_OBJECT_TYPE=CALC_TABLE` and `value` with
   `REFERENCED_OBJECT_TYPE=CALC_COLUMN`. Those endpoints did not resolve into
   graph links. The static text `Engine-resolved expression dependencies
   have not been collected.` is consequently too broad for this current
   observation: the rows were collected, but their endpoints remain
   unresolved. The graph and original evidence are unchanged; this is an
   explicit diagnosis, not a silent correction of the retained gap.

The start counts overlap: a start can have a semantic leaf and an UNKNOWN
branch. Fixture stops are 66 with missing continuation and 13 with UNKNOWN
edges; billing stops are seven with missing continuation.

## INFO evidence and confidence

All seven models have four retained successful metadata queries each:
CALCULATIONS, RELATIONSHIPS, MEASURES and COLUMNS. The 28 receipts are
`SUCCEEDED`, their assets `COLLECTED`: 267 retained rows across the six fixture
models and 93 across billing. Empty relationship results on applicable models
are successful zero-row observations. Successful metadata collection earns
DECLARED dependency evidence where endpoints resolve; it does not earn a
VERIFIED path or establish deployed notebook/procedure behavior. No inference
was promoted and no equality comparison was treated as semantic proof.

## Every attempted owner, versus owners represented in the graph

A separate bounded read of all 67 `graph_owner_collection` records establishes:

| Estate | Owners attempted | Latest CURRENT | Latest UNAVAILABLE |
|---|---:|---:|---:|
| Fixture | 58 | 28 | 30 |
| Billing | 9 | 7 | 2 |
| Total | 67 | 35 | 32 |

All 32 latest unavailable records say `GRAPH_DEFINITION_KIND_UNAVAILABLE`.
No latest owner record is left REFRESHING or has the earlier identity-collision
error. Earlier errors and interrupted-job evidence remain retained.

The graph report's **11 fixture + 1 billing unavailable owners is a different
denominator**: `GraphRepository.records` requests availability only for owners
represented by current graph nodes, edges, or definition-source ownership.
Twenty of the 32 unavailable owners are absent from that represented-owner
set. The 12 must never be reported as the full 67-owner scan disposition.
Successful alternative container/schema collection can add schema under other
owners without changing an unavailable item's own latest definition-refresh
result. Neither count establishes a complete path.

## Receipts

- Final report: `.local/round-nineteen-b/coverage-final01/report.json`, SHA-256
  `4424b04f57aea913a5ee8c788512fd1de3f3c763a76034fd0f9ffc51fa355f6e`.
- Graph files, model-owner assets and exact INFO receipt IDs are alongside it;
  the report pins both graph hashes and baseline partition hashes.
- All-owner health and point-in-time PG activity:
  `coverage-final01/final-owner-health-and-pg-activity.json`, SHA-256
  `fc865ab9125fe77aee7f4e2370b3119edf0262bbd01ac091a076dfbdb9df2f3d`.
  Its derived `owner-health-summary.json` lists every owner and latest event.
  The same read saw no other database sessions and zero granted advisory
  locks; that observation is not a substitute for fresh launch admission.

Part A is closed. These missing links and unsupported forms are findings for
subsequent work, not authorization to change graph scope in this round.
