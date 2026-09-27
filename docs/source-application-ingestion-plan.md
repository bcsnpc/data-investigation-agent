# Proposed source-application ingestion — design only

2026-09-27. No connection, pipeline, Copy Job, grant, schedule or fixture is
created by this proposal. Implementation requires review of this plan.

## Estate correction

The retained fixture notebook initializes Bronze from literal rows. It does not
read Azure SQL. Its declared quantity path therefore ends at Bronze. The Azure
SQL database exists, but is outside this fixture's ingestion lineage: the 25
successful Azure SQL reads reported in #226 do not establish otherwise. Preserve
those receipts and their historical claims with this dated qualification.

## Recommended declared binding

Use a Fabric **Copy Job**, initially a bounded full copy, with an approved reusable
Azure SQL connection ID. Explicit source mappings select the six isolated
`app.*` fixture tables; `app.*` is not a wildcard permission grant. Destination
mappings declare a new isolated Bronze lakehouse, tables and columns. A separate
ingestion identity receives only the reviewed source read and destination write
permissions. Investigator credentials remain read-only. Credentials stay in the
managed connection, never the notebook or investigator context.

The Copy Job definition contains `externalReferences.connection` and mappings.
Discovery can resolve that exact connection to its safe connector/server/database
description, then resolve each declared schema/table inside approved scope.
Definition and connection responses are DISCOVERED evidence; deterministic
normalization of those references produces DETERMINISTICALLY_DERIVED edges with
DECLARED_BY_DEFINITION binding authority, hashes and receipt references. This is
not similarity matching. See the [Copy Job definition](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/copyjob-definition)
and [connection API](https://learn.microsoft.com/en-us/rest/api/fabric/core/connections/get-connection).

A pipeline Copy activity is an alternative when orchestration requires it. Its
declared source/destination and connection references yield the same provenance
when fully resolved. It needs a Copy-activity definition adapter: the existing
pipeline parser follows InvokeCopyJob activities, not every Copy activity shape.
A pipeline that invokes the Copy Job and then the transformation notebook on
success can supply orchestration later. Neither orchestration order nor success
alone certifies a consistent source snapshot. See the [pipeline definition](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/datapipeline-definition).

**Native relations exposure must be measured, not promised.** The item relations
API documents item-to-item dependencies and `Datasource` soft dependencies. An
external Azure SQL connection is not necessarily a Fabric item. The first approved
estate checkpoint must record the actual Copy Job/pipeline upstream relations and
connection definition. If the API does not expose Azure SQL under Datasource,
report that gap; do not fabricate a native relation. Definition + exact connection
reference is a discoverable declared binding, but is not a native Datasource edge.
If native Datasource exposure is mandatory, stop at that checkpoint for review.
See [upstream relations](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-upstream-relations%28beta%29).

## Engine and discovery work

1. Integrate bounded connection-reference collection into enterprise discovery.
   `collect_lineage_evidence.py` already reads Copy Job connection references and
   safe connection details; `lineage_graph.py` already normalizes those mappings.
   The enterprise collector obtains definitions/history, but currently gathers
   native upstream relations for semantic models, not this complete ingestion
   path. Add per-surface coverage for job/pipeline relations and referenced
   connections. Retain gaps for denied definitions/connections and unresolved
   mappings. Never collect credentials or expand approved server/database/schema.
2. Project executable lineage with separate source object, copy mapping, producer
   job, destination object and column mappings. Require exact scoped identities
   and one unambiguous declared mapping. Preserve transformation/scope/grain and
   provenance. Resolve the application layer only when these declarations exist.
3. Compile a faithful source quantity from the declared column mapping and query
   it through the dedicated Azure SQL reader. Add process surface self-reporting
   and receipts for identity, database/object and supported server/engine facts;
   retain unattestable fields. No publisher fallback or name-search rescue.
   Computed expressions, filters, delete handling or changed grain that cannot be
   translated faithfully produce NOT_COMPARABLE.
4. Pin the extended context and chosen depth ceiling before a run. Metadata
   eligibility does not grant execution permission. Compare Bronze/source only
   under a supported capture scope and source cut, with snapshot limits explicit.

Full copy is the first proposal because it avoids prematurely choosing watermark
semantics. Six sequential copies do not create a transactionally consistent
six-table snapshot. Use an approved quiesced fixture window or a source snapshot/
capture-cut design before asserting cross-table consistency. Later incremental
copy must specify update/delete/late-arrival handling; watermark and CDC modes
have different guarantees. See [incremental Copy Job](https://learn.microsoft.com/en-us/fabric/data-factory/incremental-copy-job).

## Cost and invalidation

Estate work: restore/prove source availability, prepare reviewed isolated tables,
create the managed connection and bounded copy mapping, load new Bronze, run its
downstream transformations and refresh the corresponding model. The audit's
Azure SQL connection returned 40613; reachability is not presently established.
Do not interpret this proposal as approval for a firewall or permission change.
Use a separate fixture and retain the old literal-seeded artifacts and receipts.

Re-approval: a new connection declaration changes the whole-file policy hash and
requires approval under the current gate; do not narrow it. Collect and publish a
new context revision and record calls/hash/context ID. Even when the approved
scope remains sufficient, old context is not evidence for newly built mappings.
The last broad re-approval recorded 88 metadata/catalog operations. Budget discovery
under its approved collection policy and record its usage separately; do not assume
the investigation's current 60-read daily allowance covers that scan. Plan a scoped
scan with honest coverage or seek a specific budget decision if required. This
proposal changes no allowance.

Invalidated evidence: old expected fixture totals and captured generation claims
cannot certify the new ingestion path. Payload changes invalidate byte-exact
replay tapes. Engine changes invalidate prior freezes; subsequent tests remain
known-domain regressions until separately approved unfamiliar-domain acceptance.
No historical usage, failures or ledger rows are reset or overwritten.

Fabric bills full-copy Copy Job at 1.5 CU-hours per optimization-resource hour;
incremental copy uses a different rate. Estimate full copy as `1.5 × resources ×
elapsed hours`, plus downstream Spark compute, OneLake storage, Azure SQL work
and applicable transfer charges. A dollar total is not defensible without the
capacity/region price and measured duration/resources. Start with one bounded
load, inspect capacity metrics, and review cost before adding a schedule. A trial
balance is not proof of zero cost. See [Copy Job pricing](https://learn.microsoft.com/en-us/fabric/data-factory/pricing-copy-job).

## Outcomes that still need implementation

The binding makes source comparisons possible. It does **not** by itself enable
LOAD_LATENCY or INGESTION_GAP. Today `job_history()` never emits LATENT and
`ingestion()` never emits GAP; the latter inspects a Gold commit, not a complete
source-to-Bronze delivery contract.

LOAD_LATENCY needs the bound job/activity, last successful downstream capture,
matching source cut and evidence of newer relevant source state not yet loaded.
An old timestamp, failed job or elapsed time alone is insufficient. A promised
SLA requires separate authoritative policy.

INGESTION_GAP needs expected capture membership and actual delivery under the
same keys/scope/cut, with deletion, late-event and duplicate rules explicit. A
successful job or commit alone cannot prove complete ingestion. Unavailable
history, incomparable cuts or an undocumented rule must remain a scoped gap.
Per-mapping job/activity records can support these checks, but availability and
permissions must be probed. Do not silently provision a monitoring database.
See [Copy Job monitoring](https://learn.microsoft.com/en-us/fabric/data-factory/copy-job-workspace-monitoring)
and [Copy activity monitoring](https://learn.microsoft.com/en-us/fabric/data-factory/monitor-copy-activity).

Proposed delivery sequence after approval: native/declared metadata proof;
reviewed isolated estate load and re-approval; generic binding/reader execution;
then separately tested LATENT/GAP evidence rules and controlled failure cases.

The current walk's judge/support text-bound mismatch and failed-process evidence
persistence must also be resolved before subsequent live validation. Wiring the
estate is not a substitute for fixing those reported runtime contract failures.
