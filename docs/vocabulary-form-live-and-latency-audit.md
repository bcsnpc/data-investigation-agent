# Vocabulary form: two live runs and reader freshness audit

2026-09-27. Engine `bfa5e9c`; six implementation CI checks passed. No engine, grant or configuration change during the batch or read-only audit. No freeze or unfamiliar-domain claim.

Both known-domain repeats completed TRANSFORMATION_LOGIC with validated synthesis. Each used four reads: one Power BI DAX, two Fabric SQL, one endpoint-metadata request. Each used one intake call, one investigation definition-judge call and one synthesis call. Neither needed the new retry; this does not establish live retry reliability. Both compared report/Gold (8,765 = 8,765), then Gold/Silver (8,765 versus 7,661): two cross-surface comparisons, zero within-layer substitutes. Reader identity was reported on all three quantity probes; SQL additionally reported the database. Seven fields across the three surfaces remain unattested, listed verbatim below.

The walk stopped at the interpreted transformation. Silver-to-Bronze was unchecked because investigation terminated; Bronze-to-application remains unresolved because the fixture initializes literal rows. Presentation freshness was skipped. Actual repeated rate matches, shared snapshot, source correctness and business intent remain unproven. The first technical narrative says "higher upstream total" although Gold is downstream of Silver: that directional wording is inaccurate and preserved, not repaired.

## Approved allowance and restoration

Approval: eight additional reads total, four per run, temporary ceiling70, immediate restoration to60. Readback: 60 -> 70 -> 60. Actual recorded investigation usage: 62 -> 70 (eight reads); no resets or refunds. The separately requested reader audit made one additional metadata call after restoration, recorded separately as CAPABILITY_AUDIT; total resource requests for this task: nine, not eight. It changed no standing policy.

## One reader refresh-history request

One GET, no retries, as investigator-reader@skynwhy.com using its isolated cached Power BI token. Token account/tenant/audience/principal matched configuration; no elevated fallback. The user-supplied Viewer/ReadExplore grant description was not re-enumerated (that would require more calls).

`https://api.powerbi.com/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/datasets/3484a2bc-98c5-4cef-be5c-a6215484075e/refreshes?$top=1`

HTTP **403**, exact body:

```json
{"error":{"code":"Unauthorized","message":"Api accessed by user <eupi>8a582d2a-ecb4-4320-bf72-75a529a0d382</eupi> with insufficient privileges. request is unauthorized, identity None."}}
```

RequestId: `ab623583-499c-4643-bfa4-e202eb43c7a7`. This tests and confirms refusal for this identity, model and endpoint now; it does not prove that every metadata endpoint is inaccessible. The literal "identity None" is part of the service error, not evidence that a different account was used.

## What the code already has, and what latency still needs

- `metadata_connectors.FabricMetadataConnector.get_refresh_history` retrieves paginated item `/jobs/instances`. `metadata_inventory.collect_fabric` stores those responses for notebooks, pipelines and copy jobs and marks expected frequency UNKNOWN when no verified schedule contract exists. These are discovery-time metadata receipts, not live execution-reader requests.
- `MicrosoftProcessAdapter.job_history` selects retained run_history observations by the lower layer's transformation_asset_id. It returns NOT_APPLICABLE without a target, otherwise CURRENT if any detail is truthy or UNAVAILABLE. It neither compares timestamps nor tests job success; even a truthy error detail can satisfy that condition. CURRENT therefore does not establish freshness.
- Current retained fixture history is one Manual RunNotebook, Completed, start 2026-09-18T18:12:02.4546073, end 2026-09-18T18:13:23.9191421, failureReason null. This snapshot contains timing evidence, not a due time or authoritative expected cadence.
- `ingestion()` chooses the first declared_source only, not each boundary's output. `read_onelake_commit.py` reads Delta log listing and one commit using the separate metadata identity. It retains timestamp, operation, parameters and metrics, then maps AVAILABLE to CURRENT; no comparison and no GAP classification occurs. The listing is bounded to100 and does not follow continuation, so its selected commit is not a generally certified latest commit.
- Existing run c2658c88 already captured Gold commit timestamp1789755182943 (2026-09-18T18:13:02.943Z), WRITE,406 output rows. That lies within the retained notebook run interval; it is compatible with a write during that run. It neither proves an overdue load nor binds every input version to that output. No fresh Delta request was made in this audit.
- To establish load latency, bind the job to the relevant boundary, identify the last successful run and consumed input version/watermark, compare upstream availability with the downstream commit/run completion, and establish when delivery was due (schedule/SLA or other authoritative expectation). An old commit alone can reflect an unchanged source. A source change after the last run can show pending work, but does not by itself show a missed deadline. Freshness and completeness of retained history also need to be stated.
- Existing transports can supply some of that metadata without creating a new permission model. Already-authorized Gold commit access is demonstrated, but per-layer history access and full coverage are not established by this audit. More metadata reads may be needed even if no new grants are needed. Ingestion-gap evidence additionally needs source/capture completeness or watermarks tied to output; numOutputRows alone cannot establish missing records.
- The engine branches require LATENT for REFRESH_LATENCY/LOAD_LATENCY and GAP for INGESTION_GAP. The current adapter declares no presentation_freshness and emits neither LATENT nor GAP. A successful refresh-history read alone would still not implement the comparison contract. No latency implementation was performed.

## R1 ? ce27fd08-e1b6-44a8-ba48-28c008a941bc

Business explanation, verbatim:

```text
The report showed 8,765 for movements, matching the total used to prepare it. An earlier check of movements returned 7,661; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

Technical explanation, verbatim (including attestation limits and action):

```text
The checked measure total equals the gold movement_values total at 8765, while the silver stock_movements_e1b8e1 total is 7661. The shown notebook logic left-joins stock movements to product rates on product_id before deriving movement_value, and that join explicitly does not assume uniqueness, so multiple rate matches can multiply carried-through units and account for the higher upstream total. This supports a transformation-stage explanation for the difference between the checked tables, but it does not establish that repeated matches occurred in this run, that the compared reads share one snapshot, that the lower-table entries are correct, or that this behavior matches business intent.

Surface attestation limits:
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 63decc9c-a9de-4e94-8cd6-f4db95bd8b6b).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 63decc9c-a9de-4e94-8cd6-f4db95bd8b6b).
- Unattested object on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 63decc9c-a9de-4e94-8cd6-f4db95bd8b6b).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt ca151e53-d5d0-441f-9cc4-4d1828946893).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt ca151e53-d5d0-441f-9cc4-4d1828946893).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt 12e80044-2ab8-4be6-8034-70deffffdf04).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt 12e80044-2ab8-4be6-8034-70deffffdf04).

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

## R2 ? c697f79f-75a8-4bf1-a2d7-45df7b837f47

Business explanation, verbatim:

```text
The report showed 8,765 for movements, matching the total used to prepare it. An earlier check of movements returned 7,661; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

Technical explanation, verbatim (including attestation limits and action):

```text
Handled Quantity returns 8765 in the semantic model, and the same aggregate is present in dbo.movement_values, so the reported total agrees with that prepared table at the checked boundary. Summing dbo.stock_movements_e1b8e1 returns 7661, and the displayed notebook definition shows a left join from movements to rates on product_id before deriving movement_value, with an explicit note that matching rows may multiply because uniqueness is not assumed. That implemented join pattern is compatible with the higher total above the source movements, but the evidence does not establish actual duplicate matches, a shared snapshot, deduplication behavior, source-entry correctness, or business intent.

Surface attestation limits:
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 5dce81ac-3306-44ce-957a-0e3c661e542b).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 5dce81ac-3306-44ce-957a-0e3c661e542b).
- Unattested object on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 5dce81ac-3306-44ce-957a-0e3c661e542b).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt 31f959b5-8e42-4780-97d8-45e6be406467).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt 31f959b5-8e42-4780-97d8-45e6be406467).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt 17e806aa-4915-495d-9139-e07e6f5ecba6).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt 17e806aa-4915-495d-9139-e07e6f5ecba6).

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

Complete structured outputs, judges, metrics, authorization and audit receipt: [machine-readable evidence](runs/vocabulary-form-two-and-refresh-audit.json). Both original recorded tapes and session files remain unchanged.
