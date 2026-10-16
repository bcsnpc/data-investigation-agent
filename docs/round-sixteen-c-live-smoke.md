# Round Sixteen C: preserved live smoke

2026-10-12. Fixture-authored typed claims, one attempt each; not independent tester tickets and not a scored capability evaluation. Original source `7f101b4`; the later renderer correction is not applied to these retained outputs.

| Claim | Status / checked result | Diagnostic / cap | Physical | Guard/identity overhead | Seconds |
|---|---|---:|---:|---:|---:|
| page-consistency | HELD / NOT_COMPARABLE | 2/12 | 2 | 0 | 241.92 |
| multiplicity | COMPLETED / OBSERVED_EQUAL | 3/12 | 9 | 6 | 263.41 |
| record-value | COMPLETED / OBSERVED_EQUAL | 3/12 | 9 | 6 | 186.56 |

All three finished in **845.815 seconds** of the original 900-second batch. Total **22 physical requests: 8 diagnostic, 12 permission/identity overhead, 2 serverless pre-warm controls**. No model or planner calls. The application first returned SQL40613 (paused), then connected after the recorded five-second resume wait; both connection attempts were charged as controls. No allowance was raised. Pot **2742 -> 2764/4000**, reserve **95**, rolling **601 -> 618/3000** (older requests expired during the window).

The page compared 92 with 16, but its declared restrictions differ, so it correctly refused a same-context finding. Multiplicity observed 360 rows, 360 distinct nonblank keys, zero repeated-key and zero blank-key rows at APPLICATION, LANDING and SEMANTIC. Record 1 occurred once with units 16 at each of those layers. These equal observations do not establish snapshot alignment or business correctness.

All eight value probes report PARTIAL surface coverage: engine, identity and object attested and matched; connection unattested. Page uses two DAX probes. Each other claim uses one DAX probe, one lakehouse SQL probe and one Azure SQL application probe. Every comparison remains SNAPSHOT_UNVERIFIED.

The live outputs expose three renderer defects: no recommended action, page output omitted its two receipt-specific connection limits, and HELD reason was null despite an evidenced restriction mismatch. These are fixed offline with regression tests; no replacement run and no rewriting of the original outputs. No harmful causal/defect finding was observed in this bounded smoke.

Initial setup stopped on storage before any ticket was submitted, followed by a local existing-directory error. Both originals are retained. After hash-preserving compression of closed isolated databases, the same plan continued inside its original deadline; no admitted ticket was repeated. Shared live ledgers were not compressed or copied for guard decisions.

Private result SHA-256: `adf8af858cca6a194b9cbf551d8ae55fcf283c0a68cba85ec355f17f066e793d`.

## page-consistency

Session: `5c2a4a5c-bf71-4f9e-9728-84e1643522af`. Original reason: `None`.

### Business output (verbatim)

Confirmed request: You are asking about Handled Quantity. By 'Handled Quantity', you mean Handled Quantity. Using Warehouse Operations e1b8e1. On Declared predicate fixture 20261001. On Saved predicate selections. Direction: different. Compared with no other comparison. Scope: the page. The request remains unresolved. Checked 2 addressed visual(s) in Declared predicate fixture 20261001. No pair supported a same-context comparison; different restrictions, metrics or unavailable cells were not called defects. Comparing Handled Quantity - page and slicers and Handled Quantity - extra visual predicate: 92 versus 16 under different declared restrictions. Limits: These observations use the retained definitions and the admitted reader. The checks may describe different moments; timing has not been ruled out. A differing declared context or observed value does not establish a cause or business correctness. Scoring requires a readiness assessment for the actual requested capability and scope.

### Technical output (verbatim)

Confirmed request: You are asking about Handled Quantity. By 'Handled Quantity', you mean Handled Quantity. Using Warehouse Operations e1b8e1. On Declared predicate fixture 20261001. On Saved predicate selections. Direction: different. Compared with no other comparison. Scope: the page. The request remains unresolved. Checked 2 addressed visual(s) in Declared predicate fixture 20261001. No pair supported a same-context comparison; different restrictions, metrics or unavailable cells were not called defects. Comparing Handled Quantity - page and slicers and Handled Quantity - extra visual predicate: 92 versus 16 under different declared restrictions. Evidence receipts: 2db89eb1-3586-4766-a2fe-e247a8c61f28, 5b2f3fbd-e9fa-4235-9e47-074c893fefe5. Limits: These observations use the retained definitions and the admitted reader. SNAPSHOT_UNVERIFIED: query-bound served versions were not aligned; timing was not excluded. A differing declared context or observed value does not establish a cause or business correctness. Scoring requires a readiness assessment for the actual requested capability and scope.

### Capture seals

- `9b974d4c-c695-4cce-bb43-fae09176b2b1`: `d4e89692a6141bfbd1d99b1ae041e55bc0d9042d6b3a1dfcd917163234fab5cc`
- `6176dd70-ea5f-46e1-b96e-8fbb072f8db3`: `a49117f3b1126b892c417aa1725cd7bcd35dd276ab0aa4e3c65273851a69bbaf`
- `f9e6b0c2-31a5-4a0a-a24d-b5c87e44dc89`: `737cbf56faabaf7804a6303362eb0b1c6a28b14ba9d64629342d7c3d568dd395`

### Probe receipts

- `2db89eb1-3586-4766-a2fe-e247a8c61f28`: PARTIAL; engine/identity/object matched; connection unattested.
- `5b2f3fbd-e9fa-4235-9e47-074c893fefe5`: PARTIAL; engine/identity/object matched; connection unattested.

## multiplicity

Session: `b7ce05b4-d2a0-4b16-b5bd-1680fda88249`. Original reason: `None`.

### Business output (verbatim)

Confirmed request: You are asking about Movement Units. By 'Movement Units', you mean Movement Units. Using Application load fixture 20261003. Direction: more or extra. Compared with the source application. Scope: particular records. The bounded checks completed. application has 360 rows and 360 distinct nonblank declared keys; 0 rows repeat those keys and 0 rows have blank keys. landing table has 360 rows and 360 distinct nonblank declared keys; 0 rows repeat those keys and 0 rows have blank keys. reported calculation has 360 rows and 360 distinct nonblank declared keys; 0 rows repeat those keys and 0 rows have blank keys. The checked results agree between application and landing table. The checked results agree between landing table and reported calculation. Limits: The checks may describe different moments; timing has not been ruled out. Observed differences do not establish a defect, business correctness, or its cause. Global counts cover the declared record key; NULL/BLANK key rows are counted separately and excluded from distinct nonnull keys. Business-key intent and whether duplicates are erroneous were not established. Equal global counts do not establish that the member keys or record values are equal. The reader did not self-report all connection properties; the exact attestation limits are retained.

### Technical output (verbatim)

Confirmed request: You are asking about Movement Units. By 'Movement Units', you mean Movement Units. Using Application load fixture 20261003. Direction: more or extra. Compared with the source application. Scope: particular records. The bounded checks completed. APPLICATION: application has 360 rows and 360 distinct nonblank declared keys; 0 rows repeat those keys and 0 rows have blank keys. LANDING: landing table has 360 rows and 360 distinct nonblank declared keys; 0 rows repeat those keys and 0 rows have blank keys. SEMANTIC: reported calculation has 360 rows and 360 distinct nonblank declared keys; 0 rows repeat those keys and 0 rows have blank keys. APPLICATION to LANDING: The checked results agree between application and landing table. LANDING to SEMANTIC: The checked results agree between landing table and reported calculation. Evidence receipts: f29fd6e6-9ab0-4add-b1a6-b6e449b90f64, 94f8f9d7-2302-4db9-a326-903abd9aa5ec, 5f023265-45b4-459c-ad90-74d50ab8afc6. Limits: SNAPSHOT_UNVERIFIED: query-bound served versions were not aligned; timing was not excluded. Observed differences do not establish a defect, business correctness, or its cause. Global counts cover the declared record key; NULL/BLANK key rows are counted separately and excluded from distinct nonnull keys. Business-key intent and whether duplicates are erroneous were not established. Equal global counts do not establish that the member keys or record values are equal. Surface fields not self-reported for receipt 5f023265-45b4-459c-ad90-74d50ab8afc6: connection. Surface fields not self-reported for receipt 94f8f9d7-2302-4db9-a326-903abd9aa5ec: connection. Surface fields not self-reported for receipt f29fd6e6-9ab0-4add-b1a6-b6e449b90f64: connection.

### Capture seals

- `35ae28d3-2f1c-4f52-ad5e-d8f5166929ba`: `a14ca3c7326da1db92b84f0ea8dfe2bc78a9b92049a56b5798e5091029df8fd6`
- `8fce3350-04ac-46a3-8e75-43288a4fe5de`: `e3080b8d55758790ab6cf7c518ff44377828a616366458479e4e22b0cae92c8e`
- `c479c21b-8a20-440c-bfbd-825167f4bc55`: `a66f9a30c792ba06b66fbaafc537af6f2ebabe0849f159d103cfd58aa0fb93b4`

### Probe receipts

- `f29fd6e6-9ab0-4add-b1a6-b6e449b90f64`: PARTIAL; engine/identity/object matched; connection unattested.
- `94f8f9d7-2302-4db9-a326-903abd9aa5ec`: PARTIAL; engine/identity/object matched; connection unattested.
- `5f023265-45b4-459c-ad90-74d50ab8afc6`: PARTIAL; engine/identity/object matched; connection unattested.

## record-value

Session: `ccdc5e86-f3af-4ac7-91a2-8e78da2b57ad`. Original reason: `None`.

### Business output (verbatim)

Confirmed request: You are asking about Movement Units. By 'Movement Units', you mean Movement Units. Using Application load fixture 20261003. Field to trace: units. Direction: a record with a wrong field. Compared with the source application. Example records: 1. Scope: particular records. The bounded checks completed. Record 1 has 1 rows in application. The checked units is 16. Record 1 has 1 rows in landing table. The checked units is 16. Record 1 has 1 rows in reported calculation. The checked units is 16. The checked record 1 result agrees between application and landing table. The checked record 1 result agrees between landing table and reported calculation. Limits: The checks may describe different moments; timing has not been ruled out. Observed differences do not establish a defect, business correctness, or its cause. Only the named example keys were checked; unknown extra keys and whole-table multiplicity were not assessed. The reader did not self-report all connection properties; the exact attestation limits are retained.

### Technical output (verbatim)

Confirmed request: You are asking about Movement Units. By 'Movement Units', you mean Movement Units. Using Application load fixture 20261003. Field to trace: units. Direction: a record with a wrong field. Compared with the source application. Example records: 1. Scope: particular records. The bounded checks completed. APPLICATION: Record 1 has 1 rows in application. The checked units is 16. LANDING: Record 1 has 1 rows in landing table. The checked units is 16. SEMANTIC: Record 1 has 1 rows in reported calculation. The checked units is 16. APPLICATION to LANDING: The checked record 1 result agrees between application and landing table. LANDING to SEMANTIC: The checked record 1 result agrees between landing table and reported calculation. Evidence receipts: f2c5b176-8cb2-48c4-a66e-9c4b665c81d7, 70c3d3f0-e6bf-4d01-8a10-fbbe90a69510, 741ec5f5-e2fa-427c-b443-0406540211b5. Limits: SNAPSHOT_UNVERIFIED: query-bound served versions were not aligned; timing was not excluded. Observed differences do not establish a defect, business correctness, or its cause. Only the named example keys were checked; unknown extra keys and whole-table multiplicity were not assessed. Surface fields not self-reported for receipt 741ec5f5-e2fa-427c-b443-0406540211b5: connection. Surface fields not self-reported for receipt 70c3d3f0-e6bf-4d01-8a10-fbbe90a69510: connection. Surface fields not self-reported for receipt f2c5b176-8cb2-48c4-a66e-9c4b665c81d7: connection.

### Capture seals

- `ac55da7b-742d-419a-9e8e-779e24983446`: `677b2f979966e69d69959d42d544e658911f21f054de75eb197b7600f8f41a29`
- `7aff2013-3a47-4416-a524-9ce17bacf52e`: `bd7e5404579610db434533c1105e23cbeec7a18e7d18ddd77e8cebead92c7b82`
- `37f8f326-5e6a-4af2-a2e3-a59a8d12708e`: `bd1b634ffaaa8210a7dd8dade4cafd511bf54a455d751d7b1bee0673d52e4fac`

### Probe receipts

- `f2c5b176-8cb2-48c4-a66e-9c4b665c81d7`: PARTIAL; engine/identity/object matched; connection unattested.
- `70c3d3f0-e6bf-4d01-8a10-fbbe90a69510`: PARTIAL; engine/identity/object matched; connection unattested.
- `741ec5f5-e2fa-427c-b443-0406540211b5`: PARTIAL; engine/identity/object matched; connection unattested.
