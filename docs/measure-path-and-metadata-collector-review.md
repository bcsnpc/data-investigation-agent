# Measure-path reachability and metadata collector options

Updated 2026-09-24. This is the post-#223 review requested before any
measure-path implementation. It uses the retained e1b8e1 catalog and recordings;
publisher truth is not planner context. No dependency-map layer, Microsoft adapter,
metadata identity or measure-path runtime behavior is implemented here.

## Faithful evidence transfer

Synthesis now preserves each sealed query's complete validated text, returned and
displayed row counts, up to two labelled result rows, derived group-key values and
explicit omitted-row counts. Explicit `content`/`find` definition lookups preserve
at most 2,400 characters of transformation excerpts with offsets and truncation
labels. Arbitrary asset metadata remains omitted. This restores predicates, keys
and deliberately retrieved transformation evidence without treating an unbounded
row dump as conclusion context.

Citation assembly now takes the ordered union of the outer assessment citations
and both support citation lists before validation. It grants no authority: unknown,
incomplete or excessive citations still fail the existing validators. A regression
uses the exact five receipt IDs from S7, whose valid intent citation was previously
absent from the outer list. Offline validation of S7's byte-retained function
arguments now succeeds as BUSINESS_CONTEXT_REQUIRED with five outer citations.

Rebuilding the nine frozen digests offline produced the following character sizes.
The input cap is 48,000 characters.

| Trial | Before | After | Cap used |
| --- | ---: | ---: | ---: |
| S1 | 14,590 | 28,795 | 60.0% |
| S2 | 15,166 | 27,967 | 58.3% |
| S3 | 15,488 | 28,771 | 59.9% |
| S4 | 12,216 | 23,514 | 49.0% |
| S5 | 13,472 | 29,230 | 60.9% |
| S6 | 14,288 | 28,530 | 59.4% |
| S7 | 10,618 | 17,571 | 36.6% |
| S8 | 12,515 | 28,538 | 59.5% |
| S9 | 12,024 | 22,824 | 47.6% |

All nine fit, but 36.6-60.9% is not a small fraction of the cap. The implementation
therefore retains two rows rather than four and fails at the existing total input
cap instead of silently clipping further. These measurements establish fit for
these nine receipts only. Investigation context is unchanged: all nine recorded
first calls remain 28 directory entries, 11 SQL objects and 15,067 characters.

## What the G planner can already reach

The selected measure is `Handled Quantity`; its retained expression is
`SUM('Activity'[units])`. The table partition is Direct Lake entity
`dbo.movement_values` through expression source `WarehouseSource`. The expression
source points to SQL endpoint `77c49180-2ef9-4558-837c-f50fdb1df8de`, associated
with the e1b8e1 Gold lakehouse in the native item-relations probe.

| Hop | Evidence already retained | Planner availability | Boundary |
| --- | --- | --- | --- |
| Ticket -> measure | Intake resolves the stable measure ID. | Present as `starting_measure_id`; the measure and DAX expression are in the initial `context` payload. | No new permission or lookup needed. |
| Measure -> semantic table/column | `semantic_graph` has deterministic `REFERENCES` edges to Activity and Activity[units], with `dependency_state=SUPPORTED`. | The expression is present initially. Exact graph edges are retrievable with existing `search` then `asset`; they are not summarized as an explicit path in the initial payload. | Parser coverage is reference analysis, not DAX evaluation or filter-propagation proof. |
| Table -> Gold entity | Activity metadata retains the Direct Lake partition: entity `movement_values`, schema `dbo`, expression source `WarehouseSource`. `model.bim` retains the endpoint ID. | Retrievable with existing `asset`, `find` and `content` lookups. The initial bounded model context omits table partition details. | The pieces are available but not composed into one obvious test target. |
| Gold entity -> notebook/Silver inputs | Derived graph records notebook `WRITES` to Gold `movement_values`, and Gold `DERIVED_FROM` Silver `stock_movements_e1b8e1` and `product_rates_e1b8e1`; notebook source excerpts are retrievable. | Existing `asset` lookup returns the edges; `find`/`content` returns the transformation. | Edge provenance is deterministic parser output, not executed contribution proof. |
| Silver -> Azure SQL application object | Azure SQL catalog contains `app.stock_movements_e1b8e1` and the planner can query it under approved scope. | SQL object is in the initial directory and retrievable by existing tools. | **Genuinely absent as an identity-backed lineage edge.** Similar suffix/name is not sufficient to bind it to the Silver table. |
| Reproduce measure | Governed DAX can execute the selected measure with current approved context. | Already available as a dynamic query or native candidate; no new permission needed. | It is available but neither explicitly represented as a progress obligation nor made salient as a contribution test. S1-S3 did not use it. |

The missing behavior does not justify a new general dependency-map service. Most
of the chain is already stored and retrievable. The immediate product gap is a
compact, explicit measure-path view plus a generic contribution-test affordance.
The Azure SQL hop remains a provenance gap and must stay labelled until a connector
provides a stable binding or separately collected metadata supplies one.

## Proposed first-class measure-path validation

Propose an existing-tool composition, not a scripted layer sequence:

1. Add a deterministic `measure_path` context lookup for the selected measure. It
   composes current semantic references, partition/expression-source binding and
   existing graph traversal into bounded path candidates. Each hop carries asset
   IDs, relation, provenance, coverage and a gap. It stops at the last proven edge.
2. Advertise two generic test capabilities when eligible: `reproduce_measure` and
   `test_contribution`. The first produces a governed DAX receipt for the selected
   measure/context. The second compares a planner-selected anomaly population at
   an upstream proven object with the measure's contributing population or scoped
   aggregate, using existing SQL/DAX validators and receipts. It does not certify
   cross-system equivalence by itself.
3. Put a compact progress signal in planner context: whether the reported measure
   has been reproduced and whether any suspected upstream mechanism has a completed
   contribution test. Planner instructions should prefer a discriminating missing
   test when it matters, while preserving the planner's choice and allowing valid
   conclusions that need neither test.
4. Never bridge a path by name. When the final application-source binding is absent,
   expose `UNRESOLVED_BINDING` and allow an exploratory read only as unbound evidence.
   A conclusion must state that limitation.

This proposal is domain-generic and has no family, table, layer or measure branch.
It does not mandate SQL, DAX or a fixed order. Before implementation, golden-view
tests must measure directory entries, SQL-object entries and payload characters;
coverage may not fall. Implementation and the nine reruns await review.

## Fabric item-relations estate comparison

Step 4 had already been executed as 8 of the 18 read-only probes in #223. All four
items were probed upstream and downstream; every response was HTTP 200, including
empty results. Referenced workspaces were normalized and remained within the
approved workspace. Empty beta responses remain `EMPTY_RESPONSE`, not proof of
no remote relation.

| Item | Upstream / downstream relations | Comparison with derived graph |
| --- | --- | --- |
| Semantic model | 2 / 2 | Adds model -> SQL endpoint association. Report -> model pairs overlap derived report `USES` edges. |
| Report | 3 / 0 | Its model association overlaps derived bindings; empty downstream is retained as an API observation only. |
| Notebook | 1 / 0 | Notebook -> Gold `Datasource` is the same item pair as derived `WRITES`, but the relation meaning differs and is not write proof. It misses parsed table/column transformation edges. |
| Gold lakehouse | 0 / 5 | Adds SQL endpoint -> lakehouse `CascadeDelete` topology. Empty upstream does not negate parsed notebook and Silver-table lineage. |

The API adds useful item topology but misses DAX references, table/column edges,
notebook operations and the Azure SQL application path. If adopted later, it belongs
behind a replaceable optional adapter, preserving exact relation types, per-surface
coverage and the derived graph fallback. No production dependency on the beta API
is proposed.

## Separate metadata collector options

The execution reader remains Read + Build on approved models and SELECT on approved
SQL objects. It is never elevated for metadata convenience.

| Option | Collector authorization | Isolation and provenance | Unlocks | Does not unlock |
| --- | --- | --- | --- | --- |
| A. Current read-only baseline | Existing item-read metadata identity plus isolated execution readers. | Current connection profiles and coverage receipts. | Definitions where already authorized, item relations, job history, OneLake metadata, execution receipts. | INFO.CALCDEPENDENCY, refresh history requiring model Write, database-wide SQL dependency catalog. |
| B. Customer-managed metadata collector | Separate non-execution identity; narrowly approved item metadata/definition access, model Write only if the customer explicitly accepts it for metadata APIs, and database `VIEW DEFINITION` plus catalog-view SELECT without application DML. | Separate credential/profile and transport; metadata-only allowlist; cannot enter tool execution registry. Every record carries collector ID, native scope, collection time, API, coverage and authorization class. | Optional calc-dependency/XMLA export where supported, refresh history, SQL module/view dependency metadata. | Business intent, runtime visual/RLS state, external notebook semantics, causal proof, or authority to execute investigation queries. |
| C. Customer-pushed metadata export | Customer scanner exports approved dependency/refresh artifacts to an immutable import boundary; investigator has no privileged credential. | Signed/hash-addressed import, source timestamp, scanner version, declared scope and completeness. Import is context only and cannot authorize endpoints. | Similar metadata in environments that prohibit standing elevated identities. | Real-time freshness, undeclared scope completeness, query execution or semantic truth. |

Recommended product posture is A by default, C for restrictive enterprises, and B
only as an explicit optional connection. B must split Fabric/Power BI and SQL grants
when their administrators differ. Revocation or stale coverage removes eligibility
for fresh claims but does not erase historical records. None of the options makes
the collector a publisher fallback or permits mutations, refresh triggers, notebook
runs, report edits, DDL/DML, or use of collected text as instructions.

No Write grant was made or requested. INFO.CALCDEPENDENCY remains outside the
required path. Purview and Fabric Data Agent remain outside required lineage and
execution for the limitations already recorded in
[the Microsoft capability review](microsoft-native-capability-review.md).

Validation: **1,029 local regression tests passed**, including exact S7 citation
assembly, bounded excerpt/row projection and the existing golden planner views.
The required two generator tests and a 223-target local documentation-link audit
also passed. No browser or live-cloud run was needed for this backend/offline review.
