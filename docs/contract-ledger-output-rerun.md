# Contract, ledger and business-output live repeat

PRs #264, #265 and #266 were merged unchanged after six green checks each. Follow-ups are #267 (consumer-owned producer bounds), #268 (receipt-first accounting and appended correction) and #269 (substantive enforced business output and this run).

## Result

Run `3d2c5bf0-9e5c-4fcc-ba19-8b017a47e4b7` completed as `TRANSFORMATION_LOGIC`; synthesis ran once and validated. This is one known-domain ticket, not unfamiliar-domain acceptance, source correctness, or proof that the implementation is intended. The definition judgment identifies a compatible mechanism; it does not prove actual duplicate matches, their products, or a shared snapshot.

| Boundary | Observed quantities | Result |
| --- | --- | --- |
| Power BI report to Gold | 8,765 / 8,765 | CROSS_SURFACE_VERIFIED, equal |
| Gold to Silver | 8,765 / 7,661 | CROSS_SURFACE_VERIFIED, different |
| Silver to Bronze | No Bronze read | Stopped at the explained divergence |
| Bronze to application | Not executed | No declared upstream read: Bronze is literal-initialized |

There were two verified cross-surface comparisons and zero within-layer comparisons. Power BI attested identity; its engine, connection and object were not independently attested. Both Fabric SQL queries attested identity and database object; engine and connection were not independently attested. All three query receipts are sealed. The fourth read was endpoint metadata. Presentation freshness was skipped because the isolated reader lacks that metadata access. Job/ingestion checks after the explained divergence did not run.

Reads: one DAX, two Fabric SQL, one Fabric endpoint metadata; all four completed and were journalled before support validation. One investigation planner call (the definition judge), one intake call and one synthesis call. Daily cloud reservations increased 42 to 46; planner reservations 22 to 25. Config, policy, permissions, depth ceiling and per-run limits were unchanged. Three tapes and every receipt are preserved. Reference token cost: $0.081620 (not an Azure bill).

The technical provider prose ends mid-sentence at exactly 1,000 characters, as received. No application clipping occurred. The appended attestation list and action are complete. This is a remaining prose-quality defect despite successful schema/evidence validation; no second run or post-run engine patch was made.

## Business output - verbatim

The checked report value was 8,765. An independent check of the information feeding the report agreed, but a comparison further back found a different total. This rules out a report-to-input difference within these checks, but does not prove the original records are correct. A documented processing rule can explain the difference, but its intended meaning, earlier information and update timing remain unverified. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.

## Technical output - verbatim

The measure returned 8,765, and an independent SQL sum of dbo.movement_values also returned 8,765, so the checked report-to-input boundary agreed [66413822-628a-4740-8f4b-967480346081, 34382890-fcd5-4d02-9f3e-034530989fda, boundary-1-comparison]. A deeper SQL comparison found dbo.stock_movements_e1b8e1 summed to 7,661, so the difference appears between movement_values and stock_movements_e1b8e1, not at the checked report boundary [b57c29c6-7777-45d6-8f12-d24658b9819d, boundary-2-comparison]. The displayed notebook definition shows movement_values is built from stock_movements_e1b8e1 with a left join on product_id to product_rates_e1b8e1, with an explicit note that matching rows may multiply; that join provides a concrete mechanism that could increase an additive units total, while the derived movement_value column itself is separate [transformation-definition-4d96c181-bbe3-45ea-a415-cd8427849b73]. Observed aggregate agreement does not establish source-record correctness, duplicate-row,

Surface attestation limits:
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 66413822-628a-4740-8f4b-967480346081).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 66413822-628a-4740-8f4b-967480346081).
- Unattested object on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 66413822-628a-4740-8f4b-967480346081).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt 34382890-fcd5-4d02-9f3e-034530989fda).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt 34382890-fcd5-4d02-9f3e-034530989fda).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt b57c29c6-7777-45d6-8f12-d24658b9819d).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt b57c29c6-7777-45d6-8f12-d24658b9819d).

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.

## Definition judge - verbatim

Judgment: `EXPLAINS`

Explanation (460 characters):

The supplied definition includes a left join on `product_id` with an explicit note that matching rows may multiply and uniqueness is not assumed. That provides a concrete mechanism by which rows from `stock_movements_e1b8e1` can be duplicated in `movement_values`, increasing a whole-entity additive total from 7661 to 8765. The derived `movement_value` column does not by itself change totals of the source quantity, but the join-induced row multiplicity can.

Limitation:

The definition shows a mechanism that can cause the increase, but it does not establish that duplicate matches actually occurred, which products caused them, or whether both sides are from a common snapshot.

## Validation and retained history

The full local run executed 1,231 tests; its only failures were twelve intake golden subcases whose old schemas lacked the newly required bounds. The test-only schema migration was then updated without editing fixtures or tapes; all four intake regression tests passed. A final full rerun is in progress. The two required generator tests also passed.

The original 223 ledger rows are unchanged. One explicit correction reconciles the failed `0154df11` run to four reads while keeping its failure. This live repeat adds one new run, with receipt-first counts. No previous failure was relabelled as successful.

Full output objects, attestations, sealed receipt references, judgment, limits and accounting: [live artifact](runs/contract-ledger-output-live.json).
