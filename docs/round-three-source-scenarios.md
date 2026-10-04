# Round Three: source-boundary scenarios

2026-10-04 UTC. Known-domain, fixture-authored tickets; prior freezes invalid.
This record preserves the first attempts after A1â€“A6 merged. It is not unfamiliar-domain acceptance.

## Implementation and review record

| PR | Invariant and validation |
| --- | --- |
| #361 | Human-approved rolling physical allowance 600 â†’ 1,000; Part B stays 500 and diagnostic cap 12. Before/after recorded; counters preserved. |
| #362 | A1: layer names come from declared roles, not relative positions; application and original-estate rendering regressions. |
| #363 | A2: quoted numeral roles separate figures from expected identifiers; named context resolves by asset kind; fixture intake tests and preserved live intake evidence. |
| #364 | A3: malformed audit rows are explicitly excluded; original receipt validated. Warehouse audit replaces lakehouse SQL audit as declared producer source. 131 focused tests; all six CI checks passed. |
| #365 | A4: freshness questions collect evidence for every declared job boundary despite an earlier transformation finding, with within-run receipt reuse. 107 focused tests plus eight receipt-registry tests. |
| #366 | A5: source consistency with an expected identifier requires original, attested membership reads at all reachable layers. Bounded counts, no row contents in the ledger; NULL is not absence. Nine membership and 34 synthesis regressions plus address/registry checks. |
| #367 | A6: mechanism paragraph must cite the divergent boundary; wrong-boundary prose is excluded, not repaired. Implemented evidence failures are named unavailable; freshness headers describe actual attempts. 98 focused and 57 synthesis/composition/preflight checks. |
| #368 | Pre-run correction: discovery SQLEndpoint inventory has no connectionString. Membership validates the declared binding server/endpoint against approved scope; mismatches still refuse. 32 focused tests and all six CI checks passed. Initial offline refusal preserved; no investigation had begun. |

All eight PRs merged with six green CI checks. No engine change or replacement investigation during the four-scenario batch.

## Estate, permission and audit source

The human declined the OneLake direct-read grant. The isolated ops Warehouse
`round_three_ops_audit_20261004` (`bea673e0-a206-461e-9b2f-1b3b827e80de`)
contains `dbo.load_run_audit`. Only the pipeline's accounting writer changed to a
T-SQL Script activity; CopyApplication retained its definition. The old lakehouse
audit table remains untouched and unused by the producer.

Exact approved grant:

```sql
GRANT SELECT ON OBJECT::[dbo].[load_run_audit] TO [investigator-reader@skynwhy.com];
```

Before: no database principal/object grant. After: EXTERNAL_USER, object SELECT
GRANT on this table only. Publisher/control-plane administrator was
`admin@skynwhy.com`; investigation reads remained on investigator-reader and
orderops_investigator. No OneLake, workspace, write, administrator or other-object
grant. Exact control-plane listings, approval and identity-manifest update are in
[A3's delivery record](audit-row-validation.md).

The first Warehouse run `ac4b3e8d-9cdb-427e-a9dc-380ac15a50ec` recorded its own
360 read / 360 copied counters. The reader's configured audit producer retrieved
the same run and activity times. This establishes successful own accounting for
that run, not a source capture watermark or snapshot alignment.

## Delta versus lakehouse SQL finding

Administrator fixture diagnostics established committed audit rows independently
of the reader SQL endpoint. The first was still absent from reader SQL at
05:33:47.963836 UTC after committing at 05:27:27.704 UTC: **at least
6m20.259836s**. Later SQL exposed both rows; the exact convergence time was not
observed. This is the named Microsoft mechanism `LAKEHOUSE_SQL_AUDIT_SYNC_LAG`,
with receipts in [A3](audit-row-validation.md), not an inferred writer failure.
Audit tables live in a Warehouse, never behind a lakehouse SQL endpoint.

## Independent derivation and fixture operations

Arithmetic used the retained authored Bronze seed literal, not the engine's
compiled query or a served answer. Definition hash
`5f61cd4e0cdac7801df4bfdd0ca74f053fed0ef143a66b6eab4f2d0a3616f011`:
360 movements; warehouse sums 2,948 + 2,084 + 2,629 = **7,661**. Record 900099
does not occur in the seed. Gap: 7,661 + 11 = 7,672 at application, 7,661 after
the controlled post-load omission. Latency: 7,661 + 17 = 7,678 at application,
7,661 in the last load. Consistent and unreachable tickets use 7,661 and the
same expected identifier. All figures/tickets were authored for this fixture,
not reported by a real user.

Role configuration was explicitly applied and reapproved before investigation:
full config hash `ee6066720fe687e5c46daa03e951b73efb035fbbcf9b74b68ef9833163d182c7`,
context `3693ce4e-ffcb-4cdb-b1e8-7662ebeea8ba`, scan
`32ddf623-14c0-4fa9-843d-b31757f86124`. This reapproval used retained metadata,
with original acquisition provenance preserved, and made **zero cloud requests**;
it is not a new live global rescan. Semantic / landing / application roles and
business names are declared, not inferred from path position.

The gap fixture inserted only movement 900002, 11 units, application change
16:35:11.2617794 UTC. Pipeline `cd38c792-a779-4edb-88b9-abd6ec49b375` then copied
361/361, activity 16:35:53.9626954â€“16:36:16.1089576 UTC. The isolated notebook
removed that row after copying: Delta 16 â†’ 17, rows 361 â†’ 360, units 7,672 â†’
7,661. Administrator exit-value evidence describes fixture manipulation; it is
not substituted for reader evidence. The reader producer independently retrieved
the Warehouse audit run and its exact own counters/times.

After the gap run, movement 900002 was deleted from the application and pipeline
`234ec7cc-0324-49e0-86c9-764202be00dc` restored the landing baseline, own 360/360,
activity 16:48:01.1024494â€“16:48:22.2386045 UTC. The latency fixture then inserted
only movement 900001, 17 units, at 16:49:46.8593410 UTC, **after** that load.
No load was invoked before the latency investigation. That row was removed
afterwards.

## Run evidence

The sections below are completed from the preserved first-attempt records.

| Scenario | Outcome | Diagnostic / 12 | Physical | Guards | Guard reuses | Intake / investigation planner / judge / synthesis |
| --- | --- | --- | --- | --- | --- | --- |
| R3_GAP | INGESTION_GAP | 10 | 23 | 13 | 8 | 1 / 0 / 0 / 1 |
| R3_LATENCY | LOAD_LATENCY | 10 | 23 | 13 | 8 | 1 / 0 / 0 / 1 |
| R3_CONSISTENT | NO_COMPARABLE_PATH | 2 | 2 | 0 | 0 | 1 / 0 / 0 / 1 |
| R3_UNREACHABLE | NO_COMPARABLE_PATH | 2 | 2 | 0 | 0 | 1 / 0 / 0 / 1 |

All four execution statuses and synthesis statuses were COMPLETED; this does not mean all four requested outcomes were earned. Every run used engine hash `4bd6a3ca7623da92049bb700f94697b7810b143bd92d876009c071ab0ba40331`. One attempt each, no replacement, cap increase, refund or reset.

### R3_GAP

Session `68043c99-dd9b-401e-ba45-0a89ae5daa00`. Outcome `INGESTION_GAP`; synthesis validated. [Original-receipt-derived evidence](runs/R3_GAP-evidence.json), original private result SHA256 `55edc9c4847b5340567c4285b0f8e63d6be0047255cda9871551a283d7f15ca5`.

Two engine-independent boundaries: semantic 7,661 = landing 7,661; application 7,672 ≠ landing 7,661. Warehouse audit matched own 361/361 copy output and activity times for cd38c792. Complete bounded key/version comparisons found one source row absent, zero different-version rows. Source modification predates the completed load; the producer returned GAP. The controlled fixture independently established post-load removal, but aggregate copy counters alone do not prove individual delivery. Reader classification retains the SQL synchronization/snapshot caveat. The question header incorrectly says Not answered; this is a preserved output finding, not a changed outcome. The model mechanism also reverses application/semantic terminology despite the correct deterministic spine.

Probe surfaces (engine, identity and object are same-query self-reports; connection remains UNATTESTED). Coverage is PARTIAL, required three-field consistency MATCHED. Engine-independent grading does not establish snapshot identity.

| Receipt | Tool / purpose | Engine | Identity | Object | Attestation |
| --- | --- | --- | --- | --- | --- |
| 41097593-85d8-426c-98a3-e42b7ab4fc08 | bounded_dax / BASELINE | OLAP Server | investigator-reader@skynwhy.com | 0c89889c-6fe6-49ab-91e9-4b00a51070e6 | PARTIAL / MATCHED |
| 21bee0e7-a99d-4a4d-9111-95848b2ad726 | bounded_fabric_sql / BASELINE | Microsoft Azure SQL Data Warehouse | investigator-reader@skynwhy.com | round_two_bronze_20261003 | PARTIAL / MATCHED |
| 4a4c8ef8-27ac-44e7-917f-9f3fe6c9f506 | bounded_sql / BASELINE | Microsoft SQL Azure | orderops_investigator | ordersops | PARTIAL / MATCHED |
| 16f1dbc9-7d3e-458c-b023-f6719acf45a4 | bounded_fabric_sql / bounded read | Microsoft Azure SQL Data Warehouse | investigator-reader@skynwhy.com | round_three_ops_audit_20261004 | PARTIAL / MATCHED |
| 00ac9a80-728a-4172-ad16-e3fc6456e6bd | bounded_sql / bounded read | Microsoft SQL Azure | orderops_investigator | ordersops | PARTIAL / MATCHED |
| 2adc0fc0-ce00-46c1-8ab5-a87c99b7a2a4 | bounded_sql / bounded read | Microsoft SQL Azure | orderops_investigator | ordersops | PARTIAL / MATCHED |
| 859e67de-03e7-4218-8665-b5bae4d6a346 | bounded_fabric_sql / bounded read | Microsoft Azure SQL Data Warehouse | investigator-reader@skynwhy.com | round_two_bronze_20261003 | PARTIAL / MATCHED |
| 0896a61e-b5b5-41cb-a582-93f649c88913 | bounded_fabric_sql / bounded read | Microsoft Azure SQL Data Warehouse | investigator-reader@skynwhy.com | round_two_bronze_20261003 | PARTIAL / MATCHED |

Per run: one DAX value query; seven SQL diagnostic value queries (one landing total, one application total, one Warehouse audit, two application pages and two landing pages); two reader endpoint-metadata requests. Thirteen SQL guard/identity requests are overhead; eight permission guard reuses. Ledger reads_sql=20 includes the seven SQL diagnostics and thirteen guards, reads_other=2 records metadata. Metadata receipts report discovered endpoint connection strings, not query-bound self-attestation. No skipped resolved comparison, no within-layer comparison; optional refresh timing remains unavailable and both boundaries SNAPSHOT_UNVERIFIED.

Honesty check: Independent seed arithmetic did not guarantee intake scope, current surface values, metadata availability, audit selection, receipt attestation, or synthesis. A different served quantity, stale/missing audit row, unmatched attestation, incomplete page set, or refused synthesis could have prevented this outcome. The declared preconditions and observed receipts were checked; no expected label was injected into the runtime.

**Business output, verbatim**

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. Recent movements are missing. Please trace this figure to the application and establish whether a completed load left anything out.
Answer to your question: Not answered.
Regarding the original question: No recorded completion check establishes an answer to this request.
What was found instead:

The checked reported calculation value was 7,661. Some expected information has not arrived in the checked process. The recorded successful load finished at 2026-10-04T16:36:16.1089576Z; its own activity reported 361 rows read and 361 rows written. The newest application change read was 2026-10-04 16:35:11.2617794; 1 source rows were absent and 0 carried different versions in the destination. The observed source changes predate that load, so this is a delivery difference requiring operational investigation. The checks do not establish whether they describe the same moment; different update timing remains possible. For the reported calculation and the landing table, the two checks used different calculation engines. For the landing table and the application, the two checks used different calculation engines. Recommended action: Ask the operations owner to investigate the missing delivery using the recorded evidence.
```

**Technical output, verbatim**

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. Recent movements are missing. Please trace this figure to the application and establish whether a completed load left anything out.
Answer to your question: Not answered.
Regarding the original question: No recorded completion check establishes an answer to this request.
What was found instead:

Measure: Movement Units.
B2 diverges: L2 (app.stock movements round two 20261003 in ordersops; role APPLICATION, upstream input) 7,672 -> L1 (dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING, downstream output) 7,661.
B1 agrees: L1 (dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING, upstream input) 7,661 -> L0 (Movements in Application load fixture 20261003; role SEMANTIC, downstream output) 7,661.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for model-only or layer-only named context.

The measure carries the intermediate movements table total straight through to the application layer with no change. The compared source relation is larger than that intermediate table, so the missing movements arise before or during transfer into that intermediate table rather than from aggregation within the application measure.

Run cd38c792-a779-4edb-88b9-abd6ec49b375: The recorded successful load finished at 2026-10-04T16:36:16.1089576Z; its own activity reported 361 rows read and 361 rows written. The newest application change read was 2026-10-04 16:35:11.2617794; 1 source rows were absent and 0 carried different versions in the destination. The observed source changes predate that load, so this is a delivery difference requiring operational investigation.

Layers:
L0 - Movements in Application load fixture 20261003; role SEMANTIC: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements
L1 - dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003
L2 - app.stock movements round two 20261003 in ordersops; role APPLICATION: sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945

Limits:
- Unattested connection on L0 (receipt 41097593-85d8-426c-98a3-e42b7ab4fc08).
- Unattested connection on L1 (receipt 21bee0e7-a99d-4a4d-9111-95848b2ad726).
- Unattested connection on L2 (receipt 4a4c8ef8-27ac-44e7-917f-9f3fe6c9f506).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- Delivery row comparisons do not exclude Fabric SQL analytics endpoint synchronization delay; query-bound matching snapshots are unavailable.

Recommended action: Ask the operations owner to investigate the missing delivery using the recorded evidence.
```

### R3_LATENCY

Session `577a3cec-35ff-4637-bb9f-665a361bdf9a`. Outcome `LOAD_LATENCY`; synthesis validated. [Original-receipt-derived evidence](runs/R3_LATENCY-evidence.json), original private result SHA256 `70b0dbf8a1ef3fbd4361faa3e1a43fee08a562dce75bfae063721cc08009d297`.

Two engine-independent boundaries: semantic 7,661 = landing 7,661; application 7,678 ≠ landing 7,661. Warehouse audit matched own 360/360 and times for 234ec7cc. Source changed at 16:49:46.8593410 UTC, after load completion 16:48:22.2386045 UTC. Complete bounded key/version comparisons found one missing source row, zero different versions. The producer returned LATENT and the outcome LOAD_LATENCY. Refresh timing unavailable; current snapshots unestablished. Actual freshness evidence was attempted and rendered, so the currency question is partly answered rather than declared proven current.

Probe surfaces (engine, identity and object are same-query self-reports; connection remains UNATTESTED). Coverage is PARTIAL, required three-field consistency MATCHED. Engine-independent grading does not establish snapshot identity.

| Receipt | Tool / purpose | Engine | Identity | Object | Attestation |
| --- | --- | --- | --- | --- | --- |
| 3cea229c-dadc-427d-9a42-310b39819cfd | bounded_dax / BASELINE | OLAP Server | investigator-reader@skynwhy.com | 0c89889c-6fe6-49ab-91e9-4b00a51070e6 | PARTIAL / MATCHED |
| 89fe2ad9-bac0-4e58-8a01-a197eb63cde7 | bounded_fabric_sql / BASELINE | Microsoft Azure SQL Data Warehouse | investigator-reader@skynwhy.com | round_two_bronze_20261003 | PARTIAL / MATCHED |
| 81ef9564-8186-4815-952d-a13f9c19f5b3 | bounded_sql / BASELINE | Microsoft SQL Azure | orderops_investigator | ordersops | PARTIAL / MATCHED |
| f2b4e30d-cc8e-4768-9a1f-a52bdb6128af | bounded_fabric_sql / bounded read | Microsoft Azure SQL Data Warehouse | investigator-reader@skynwhy.com | round_three_ops_audit_20261004 | PARTIAL / MATCHED |
| 514ce4b5-58b4-4ff6-9351-70616a221e55 | bounded_sql / bounded read | Microsoft SQL Azure | orderops_investigator | ordersops | PARTIAL / MATCHED |
| e709e872-3df7-4071-a932-0f8658dd5a0f | bounded_sql / bounded read | Microsoft SQL Azure | orderops_investigator | ordersops | PARTIAL / MATCHED |
| c2a65578-84ae-444b-a185-0bbd3c196376 | bounded_fabric_sql / bounded read | Microsoft Azure SQL Data Warehouse | investigator-reader@skynwhy.com | round_two_bronze_20261003 | PARTIAL / MATCHED |
| a96f3157-350d-4cc7-b325-b1716f34b7ff | bounded_fabric_sql / bounded read | Microsoft Azure SQL Data Warehouse | investigator-reader@skynwhy.com | round_two_bronze_20261003 | PARTIAL / MATCHED |

Per run: one DAX value query; seven SQL diagnostic value queries (one landing total, one application total, one Warehouse audit, two application pages and two landing pages); two reader endpoint-metadata requests. Thirteen SQL guard/identity requests are overhead; eight permission guard reuses. Ledger reads_sql=20 includes the seven SQL diagnostics and thirteen guards, reads_other=2 records metadata. Metadata receipts report discovered endpoint connection strings, not query-bound self-attestation. No skipped resolved comparison, no within-layer comparison; optional refresh timing remains unavailable and both boundaries SNAPSHOT_UNVERIFIED.

Honesty check: Independent seed arithmetic did not guarantee intake scope, current surface values, metadata availability, audit selection, receipt attestation, or synthesis. A different served quantity, stale/missing audit row, unmatched attestation, incomplete page set, or refused synthesis could have prevented this outcome. The declared preconditions and observed receipts were checked; no expected label was injected into the runtime.

**Business output, verbatim**

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units and looks stale. Please check whether the application changed after the last successful load.
Answer to your question: Partly answered.
Regarding whether the reported information is current: Timing or processing evidence was inspected, but it does not establish that the reported information is current. Refresh history was unavailable to the diagnostic reader. The load accounting was read and established a successful completed load; that alone does not establish currency. Source delivery evidence established that the source changed after the last load.
What the investigation established:

The checked reported calculation value was 7,661. A scheduled update has not yet delivered the information needed by the reported number. The recorded successful load finished at 2026-10-04T16:48:22.2386045Z; its own activity reported 360 rows read and 360 rows written. The newest application change read was 2026-10-04 16:49:46.8593410; 1 source rows were absent and 0 carried different versions in the destination. The source changed after that load finished, so another load is required before checking delivery. The checks do not establish whether they describe the same moment; different update timing remains possible. For the reported calculation and the landing table, the two checks used different calculation engines. For the landing table and the application, the two checks used different calculation engines. Recommended action: Check the number again after the scheduled update finishes.
```

**Technical output, verbatim**

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units and looks stale. Please check whether the application changed after the last successful load.
Answer to your question: Partly answered.
Regarding whether the reported information is current: Timing or processing evidence was inspected, but it does not establish that the reported information is current. Refresh history was unavailable to the diagnostic reader. The load accounting was read and established a successful completed load; that alone does not establish currency. Source delivery evidence established that the source changed after the last load.
What the investigation established:

Measure: Movement Units.
B2 diverges: L2 (app.stock movements round two 20261003 in ordersops; role APPLICATION, upstream input) 7,678 -> L1 (dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING, downstream output) 7,661.
B1 agrees: L1 (dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING, upstream input) 7,661 -> L0 (Movements in Application load fixture 20261003; role SEMANTIC, downstream output) 7,661.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for model-only or layer-only named context.

The semantic measure is computed from rows in the movements table that currently align with the staged movements delivery, while the application side movements relation holds a higher rowwise total. This places the divergence at the handoff between the application relation and the staged delivery, with the semantic layer carrying forward the staged value rather than the newer application value.

Run 234ec7cc-0324-49e0-86c9-764202be00dc: The recorded successful load finished at 2026-10-04T16:48:22.2386045Z; its own activity reported 360 rows read and 360 rows written. The newest application change read was 2026-10-04 16:49:46.8593410; 1 source rows were absent and 0 carried different versions in the destination. The source changed after that load finished, so another load is required before checking delivery.

Layers:
L0 - Movements in Application load fixture 20261003; role SEMANTIC: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements
L1 - dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003
L2 - app.stock movements round two 20261003 in ordersops; role APPLICATION: sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945

Limits:
- Unattested connection on L0 (receipt 3cea229c-dadc-427d-9a42-310b39819cfd).
- Unattested connection on L1 (receipt 89fe2ad9-bac0-4e58-8a01-a197eb63cde7).
- Unattested connection on L2 (receipt 81ef9564-8186-4815-952d-a13f9c19f5b3).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
- Delivery row comparisons do not exclude Fabric SQL analytics endpoint synchronization delay; query-bound matching snapshots are unavailable.

Recommended action: Check the number again after the scheduled update finishes.
```

### R3_CONSISTENT

Session `74d0c0ed-8aa9-4bb1-b6c5-db37709e8f7c`. Outcome `NO_COMPARABLE_PATH`; synthesis validated. [Original-receipt-derived evidence](runs/R3_CONSISTENT-evidence.json), original private result SHA256 `89e95e607bfec2642513dec34fee40330b5f965e26e023f9d85f2033717eb47e`.

Intake correctly recorded 7,661 as FIGURE and 900099 as IDENTIFIER, bound the named semantic model, and carried the expected record. It also added movement_id to dimension_ids although the ticket requests the displayed total. That changed the execution to grouping: two DAX reads, no SQL read, no independently compared boundary. Membership refused the grouped scope rather than manufacturing absence. The lower whole-entity compiler refusal remains intact. This exposes intake adding grouping without a scope quote; it is not a failed access grant or a proved missing connection.

It did not establish 900099 absent at every layer and did not earn CONSISTENT_TO_SOURCE. The authored seed says absent, but that evaluator fact was never substituted for missing reader membership evidence.

Probe surfaces (engine, identity and object are same-query self-reports; connection remains UNATTESTED). Coverage is PARTIAL, required three-field consistency MATCHED. Engine-independent grading does not establish snapshot identity.

| Receipt | Tool / purpose | Engine | Identity | Object | Attestation |
| --- | --- | --- | --- | --- | --- |
| f654f022-21d0-48a5-9302-fba388106586 | bounded_dax / BASELINE | OLAP Server | investigator-reader@skynwhy.com | 0c89889c-6fe6-49ab-91e9-4b00a51070e6 | PARTIAL / MATCHED |
| 85e8bdb1-9ff3-457d-8f3a-77a00db7a749 | bounded_dax / BASELINE | OLAP Server | investigator-reader@skynwhy.com | 0c89889c-6fe6-49ab-91e9-4b00a51070e6 | PARTIAL / MATCHED |

Per run: two DAX diagnostics; zero SQL, metadata or guard requests. The DAX group query is within the model and is not a cross-boundary comparison. Both resolved boundaries were skipped; reasons are in the technical output below. No snapshots were verified. No live membership result was obtained.

Honesty check: Independent seed arithmetic did not guarantee intake scope, current surface values, metadata availability, audit selection, receipt attestation, or synthesis. The predicted outcome did fail: intake introduced grouping, preventing faithful lower comparison. No ticket edits or replacement run were used to erase that finding.

**Business output, verbatim**

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement numbered 900099 that is absent from the authored application fixture. Please trace the displayed total to the application so I know whether this is a pipeline question or an application question.
Answer to your question: Not answered.
Regarding the original question: No recorded completion check establishes an answer to this request.
What was found instead:

The checked declared layer value was 7,661. The available evidence did not establish a boundary comparison with the total used to prepare the report. A difference between the report and its input therefore remains possible. The original entries, unchecked selections, update timing and intended business rules remain outside what these comparisons establish. Recommended action: Ask the system owner to provide the missing connection information or read access identified in the limits.
```

**Technical output, verbatim**

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement numbered 900099 that is absent from the authored application fixture. Please trace the displayed total to the application so I know whether this is a pipeline question or an application question.
Answer to your question: Not answered.
Regarding the original question: No recorded completion check establishes an answer to this request.
What was found instead:

Measure: Movement Units.
No independently compared boundary was established.
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for model-only or layer-only named context.

The measure is evaluated from the movements table. The retained materials also include an application quantity only at whole entity scope, while the request groups results by movement, so the materials do not provide a common movement level comparison between the displayed total and the application record.

Layers:
L0 - Movements in Application load fixture 20261003; role SEMANTIC: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements
L1 - dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003
L2 - app.stock movements round two 20261003 in ordersops; role APPLICATION: sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945

Limits:
- Checked through L0; stopped because capability unavailable.
- Unchecked L0 -> L1: NO_INDEPENDENT_LOWER_READ.
- Unchecked L1 -> L2: Declared application quantity supports only whole-entity scope without filters or grouping..
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.

Recommended action: Ask the system owner to provide the missing connection information or read access identified in the limits.
```

### R3_UNREACHABLE

Session `74062b6c-a4c5-4a7f-847b-a45b2573eb2a`. Outcome `NO_COMPARABLE_PATH`; synthesis validated. [Original-receipt-derived evidence](runs/R3_UNREACHABLE-evidence.json), original private result SHA256 `cbd3ed0091324cfaa20fc8c75e700bc80c60081e4277dc51fb6d96a6ce3dcf6a`.

Intake correctly recorded 7,661 as FIGURE and 900099 as IDENTIFIER, bound the named semantic model, and carried the expected record. It also added movement_id to dimension_ids although the ticket requests the displayed total. That changed the execution to grouping: two DAX reads, no SQL read, no independently compared boundary. Membership refused the grouped scope rather than manufacturing absence. The lower whole-entity compiler refusal remains intact. This exposes intake adding grouping without a scope quote; it is not a failed access grant or a proved missing connection.

The exact same ticket was used. Configuration changed only system_of_record.reachable to false, with recorded full-hash reapproval against retained metadata: hash `462a22d7f9b87e79a390098dc8fcc56408fa11f0dfd7f03fffacb526335cb9c1`, context `0cce013c-1c15-4b4c-a128-265fb8bb2ab8`, zero cloud requests. No application read occurred. The run stopped at semantic, not landing; therefore it did not earn CONSISTENT_TO_BOUNDARY or retrieve the Warehouse load account into its outputs. It cannot claim fidelity to the last load.

Probe surfaces (engine, identity and object are same-query self-reports; connection remains UNATTESTED). Coverage is PARTIAL, required three-field consistency MATCHED. Engine-independent grading does not establish snapshot identity.

| Receipt | Tool / purpose | Engine | Identity | Object | Attestation |
| --- | --- | --- | --- | --- | --- |
| f5d01503-6ae0-44fb-94db-8ac493edeb18 | bounded_dax / BASELINE | OLAP Server | investigator-reader@skynwhy.com | 0c89889c-6fe6-49ab-91e9-4b00a51070e6 | PARTIAL / MATCHED |
| 3d6a37c7-ce37-4645-a968-ec111bcf6130 | bounded_dax / BASELINE | OLAP Server | investigator-reader@skynwhy.com | 0c89889c-6fe6-49ab-91e9-4b00a51070e6 | PARTIAL / MATCHED |

Per run: two DAX diagnostics; zero SQL, metadata or guard requests. The DAX group query is within the model and is not a cross-boundary comparison. Both resolved boundaries were skipped; reasons are in the technical output below. No snapshots were verified. No live membership result was obtained.

Honesty check: Independent seed arithmetic did not guarantee intake scope, current surface values, metadata availability, audit selection, receipt attestation, or synthesis. The predicted outcome did fail: intake introduced grouping, preventing faithful lower comparison. No ticket edits or replacement run were used to erase that finding.

**Business output, verbatim**

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement numbered 900099 that is absent from the authored application fixture. Please trace the displayed total to the application so I know whether this is a pipeline question or an application question.
Answer to your question: Not answered.
Regarding the original question: No recorded completion check establishes an answer to this request.
What was found instead:

The checked declared layer value was 7,661. The available evidence did not establish a boundary comparison with the total used to prepare the report. A difference between the report and its input therefore remains possible. The original entries, unchecked selections, update timing and intended business rules remain outside what these comparisons establish. Recommended action: Ask the system owner to provide the missing connection information or read access identified in the limits.
```

**Technical output, verbatim**

```text
You asked: In Application load fixture 20261003, Movement Units shows 7,661 units. I expected a movement numbered 900099 that is absent from the authored application fixture. Please trace the displayed total to the application so I know whether this is a pipeline question or an application question.
Answer to your question: Not answered.
Regarding the original question: No recorded completion check establishes an answer to this request.
What was found instead:

Measure: Movement Units.
No independently compared boundary was established.
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for model-only or layer-only named context.

The check reaches the Movements table and stops there. A further link from that table to a stock movements relation is recorded but not read through, and the declared record source beyond that relation is configured unreachable, so no application read occurs. The displayed total therefore traces only as far as the Movements table within the model rather than through to the authored application fixture.

Layers:
L0 - Movements in Application load fixture 20261003; role SEMANTIC: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements
L1 - dbo.stock movements round two 20261003 in round two bronze 20261003; role LANDING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003
L2 - app.stock movements round two 20261003 in ordersops; role APPLICATION: sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945

Limits:
- Checked through L0; stopped because capability unavailable.
- Unchecked L0 -> L1: NO_INDEPENDENT_LOWER_READ.
- Unchecked L1 -> L2: The declared system of record is configured unreachable; no application read was attempted..
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.

Recommended action: Ask the system owner to provide the missing connection information or read access identified in the limits.
```

## Restoration, costs and limits

Application reachability restored with full config hash
`ee6066720fe687e5c46daa03e951b73efb035fbbcf9b74b68ef9833163d182c7`, context
`73e882da-54e1-4320-9149-bd947463ca56`, scan
`dab2e576-e268-44d6-917e-df4313b02d69`. Retained-metadata reapproval, zero cloud
requests. Original contexts and recorded runs unchanged.

Final independent reader verification returned application **7,661**, landing
**7,661**, isolated model **7,661**, original model **8,765**. Four diagnostic
queries, six guards, ten physical requests, no model call. See
[reader verification](runs/R3-final-baseline-reader-verification.json).
The private verification helper calculated its seal before adding the physical
count annotation; original artifact remains unchanged and a zero-read ledger
annotation records that defect. Its preserved SHA256, not that earlier seal,
identifies the exported evidence. Usage is from charged reservations, not four
outer helper calls: all ten physical requests are recorded.

Part B **466/500**, rolling allowance last observed **590/1,000**; diagnostic cap
**12 unchanged**. Four investigations: 24 diagnostic requests, 50 physical,
26 guard overhead, four intake and four synthesis calls, zero investigation
planner and judge calls. The four runs reserved 38,000 output tokens; actual
provider usage is in each ledger row. This batch beginning after A6 used 76
physical requests overall (390 → 466), including fixture/control-plane work,
restoration and verification. Earlier Warehouse/A3 requests remain recorded.
No credit refill, counter reset or allowance change during these scenarios.

Two additional pipeline runs in this round each reported copy cpuCoreMs 240,000,
InvokeCopy AzureIR 0.016666666666666666 hours and Script AzureIR
0.016666666666666666 hours. These are served activity meters, not a fabricated
currency price or total-capacity charge. The first Warehouse verification had
cpuCoreMs 480,000 and InvokeCopy 0.03333333333333333 hours, plus Script
0.016666666666666666 hours. No schedules, refresh/reframe or other estate edits.

Own choices: separate ops Warehouse; retained-metadata reapproval with explicit
provenance; restore gap before latency; preserve the identical consistency ticket
for configured-unreachable; stop without patching intake to obtain the two
missing outcomes. Disagreement/qualification: matching copy counters do not prove
which individual rows arrived, and engine independence does not prove aligned
snapshots. The controlled omission is fixture truth, separate from reader proof.

Open findings: unexpected intake grouping blocks the two terminal consistency
scenarios; the gap question header denies an answer despite its delivery finding;
the model's gap mechanism paragraph reverses direction despite a correct rendered
spine; generic business refusal/action does not name the grouped-scope refusal;
source and unreachable outcomes remain unearned live in this round. The requested
audit account could not be rendered for the unreachable run because the walk
stopped before the landing comparison. No new source-outcome generality or
unfamiliar-domain acceptance claim.
