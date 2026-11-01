# Quality of frozen v0.24 - Round 25

## Plain-language result

On the new 60-ticket held-out set, DIA is fully correct on 36/60 after independent raw review:60%, with a 95% Wilson interval of 47.4-71.4%. No harmful answer was confirmed in that set. The official primary score is 37/60; the stricter both-graders score is 32/60. Related variants share fixtures, so this is sample uncertainty, not a client-estate reliability guarantee.

The largest weakness is free-text intake and target selection. On the unchanged R22 questions, raw-reviewed correctness is 3/40 dev and 0/20 held-out; the original R22 official results were 14/40 and 5/20. Three harmful answers in this regression remain counted. Structured-form success must not hide this loss. G1dev is 35/40 raw with 2 harmful answers; G4, the previously used R23 regression set, is 16/20 raw with 0 harmful, compared with R23's unchanged official 6/20. These cohorts are kept separate.

Read-only enforcement, secrets and budgets stayed on. The investigator, model, prompt and caching behaviour stayed frozen; two documented budget-policy/accounting compatibility files are the only runtime exceptions. No quality fix is implemented here. The results do not establish dependable general investigation quality. Earlier checkpoint versions remain in Git and the run ledger.

## Current measurement

Saved-result snapshot: 2026-11-01T08:54:17.072823+00:00. Raw-reviewed is the headline; official and strict remain unchanged. G2 is the completed new held-out set (60/60 accounted for). G3 is complete (60/60); G4 remains in progress until all20 are accounted for. Partial cohort figures must not be presented as full-set accuracy.

| Cohort | Official primary (95% Wilson) | Strict (95% Wilson) | Raw-reviewed (95% Wilson) | Raw harmful | Requested |
|---|---|---|---|---:|---:|
|G1|37/40 (80.1-97.4%)|34/40 (70.9-92.9%)|35/40 (73.9-94.5%)|2|40|
|G2|37/60 (49.0-72.9%)|32/60 (40.9-65.4%)|36/60 (47.4-71.4%)|0|60|
|G3|6/60 (4.7-20.1%)|2/60 (0.9-11.4%)|3/60 (1.7-13.7%)|3|60|
|G4|18/20 (69.9-97.2%)|15/20 (53.1-88.8%)|16/20 (58.4-91.9%)|0|20|

### Same original R22 splits

The original dev and held-out sets remain separate. All original tickets are now graded; the dev and held-out denominators are complete. Historical R22 scores are official primary, not retrospectively raw-reviewed.

| Original split | Requested | R22 official (95% Wilson) | R25 official | R25 strict | R25 raw-reviewed |
|---|---:|---|---|---|---|
|dev|40|14/40 (22.1-50.5%)|6/40 (7.1-29.1%)|2/40 (1.4-16.5%)|3/40 (2.6-19.9%)|
|heldout|20|5/20 (11.2-46.9%)|0/20 (0.0-16.1%)|0/20 (0.0-16.1%)|0/20 (0.0-16.1%)|

G1 is unchanged dev v2. G3 compares unchanged R22 text (14/40dev and5/20held-out); G4 is a regression comparison with R23's6/20. The prior R24 official18/20 remains unchanged. Related variants share fixtures, so Wilson intervals describe this observed sample, not independent client-estate accuracy.

## Grader agreement and correctness dimensions

Core agreement means verdict, layer, cause and harm flags. Full assessment additionally includes handoff quality, partial status and first failing step. It is not honest to label the higher core rate as agreement on the entire assessment. All G2-G4 assessment disagreements require fresh independent Claude review; no operator adjudication.

| Cohort | Core agreement (95% Wilson) | Full assessment agreement (95% Wilson) | Raw verdict | Raw layer | Raw cause | Pending raw reviews |
|---|---|---|---|---|---|---:|
|G1|37/40 (80.1-97.4%)|8/40 (10.5-34.8%)|35/40 (73.9-94.5%)|35/40 (73.9-94.5%)|35/40 (73.9-94.5%)|0|
|G2|51/60 (73.9-91.9%)|13/60 (13.1-33.6%)|42/60 (57.5-80.1%)|44/60 (61.0-82.9%)|37/60 (49.0-72.9%)|0|
|G3|50/60 (72.0-90.7%)|8/60 (6.9-24.2%)|3/60 (1.7-13.7%)|8/60 (6.9-24.2%)|7/60 (5.8-22.2%)|0|
|G4|16/20 (58.4-91.9%)|3/20 (5.2-36.0%)|18/20 (69.9-97.2%)|19/20 (76.4-99.1%)|17/20 (64.0-94.8%)|0|

Operator blinding was partly broken by the earlier two staging/status fragments and an additional G3 access status dump that included saved outcome text. These exposures are disclosed in decisions.md and the round summary. No investigator logic or expectation was changed afterward. G1's original raw reviews remain; G2-G4 disagreements are decided by independent Claude calls receiving only the owner-approved packet.

## Class results

Every cell includes its95% Wilson interval. Original case-family IDs are retained; G2 also has a verdict-label grouping in its JSON receipt.

| Cohort / case family | Official | Strict | Raw-reviewed |
|---|---|---|---|
|G1 / v2-access-export|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-application-baseline|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-before-temporal-retention|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G1 / v2-billing-invoices|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-billing-mrr|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-failed-application-load|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-failed-billing-transform|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-fixture-quantity|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-latency-record|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-other-collected-definition|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-record-absent-everywhere|2/2 (34.2-100.0%)|1/2 (9.5-90.5%)|2/2 (34.2-100.0%)|
|G1 / v2-record-repeated-gold|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-screenshot-record-01|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-screenshot-record-02|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-screenshot-record-03|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-screenshot-record-04|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-source-history|2/2 (34.2-100.0%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G1 / v2-stale-model|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-waiting-application-load|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G1 / v2-warehouse-scope|1/2 (9.5-90.5%)|1/2 (9.5-90.5%)|1/2 (9.5-90.5%)|
|G2 / v4-access-export|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|
|G2 / v4-application-baseline|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|1/3 (6.1-79.2%)|
|G2 / v4-before-temporal-retention|2/3 (20.8-93.9%)|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|
|G2 / v4-billing-invoices|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|3/3 (43.9-100.0%)|
|G2 / v4-billing-mrr|3/3 (43.9-100.0%)|3/3 (43.9-100.0%)|3/3 (43.9-100.0%)|
|G2 / v4-failed-application-load|3/3 (43.9-100.0%)|3/3 (43.9-100.0%)|3/3 (43.9-100.0%)|
|G2 / v4-failed-billing-transform|3/3 (43.9-100.0%)|3/3 (43.9-100.0%)|3/3 (43.9-100.0%)|
|G2 / v4-fixture-quantity|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|
|G2 / v4-latency-record|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|
|G2 / v4-other-collected-definition|3/3 (43.9-100.0%)|3/3 (43.9-100.0%)|3/3 (43.9-100.0%)|
|G2 / v4-record-absent-everywhere|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|
|G2 / v4-record-repeated-gold|1/3 (6.1-79.2%)|1/3 (6.1-79.2%)|1/3 (6.1-79.2%)|
|G2 / v4-sample-business-meaning|3/3 (43.9-100.0%)|0/3 (0.0-56.1%)|2/3 (20.8-93.9%)|
|G2 / v4-sample-technical|3/3 (43.9-100.0%)|3/3 (43.9-100.0%)|3/3 (43.9-100.0%)|
|G2 / v4-screenshot-billing-invoices|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G2 / v4-screenshot-billing-mrr|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G2 / v4-screenshot-fixture-01|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G2 / v4-screenshot-fixture-02|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G2 / v4-screenshot-fixture-03|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G2 / v4-screenshot-fixture-04|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G2 / v4-source-history|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|
|G2 / v4-stale-model|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|
|G2 / v4-waiting-application-load|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|
|G2 / v4-warehouse-scope|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|
|G3 / R17-01|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / R17-02|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / R17-03|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / R17-04|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / R17-05|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / R17-06|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / R17-07|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / R17-08|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / R17-09|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|1/1 (20.7-100.0%)|
|G3 / R17-10|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / R17-11|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / R17-12|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / access-export-1|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / access-export-2|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / access-export-3|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / baseline-S01|2/2 (34.2-100.0%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / baseline-S02|2/2 (34.2-100.0%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / baseline-S03|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|G3 / blocked-model-movement-1|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / blocked-model-movement-2|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / blocked-model-movement-3|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / different-day|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / different-product|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / different-warehouse|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / failed-billing-load|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / failed-billing-transform|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / failed-fixture-load|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / fourth-design-model-formula|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / fourth-failed-billing-transform|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / history-source-900201|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / history-source-900202|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / history-source-900203|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / latency-900501|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / latency-900502|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / latency-900503|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / older-export-movement-1|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / older-export-movement-2|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / older-export-movement-3|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / stale-product1|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / stale-total|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G3 / stale-warehouse3|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / waiting-billing-load|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / waiting-billing-transform|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G3 / waiting-fixture-load|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|G4 / v2-access-export|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-application-baseline|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G4 / v2-before-temporal-retention|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G4 / v2-billing-invoices|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-billing-mrr|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-failed-application-load|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-failed-billing-transform|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-fixture-quantity|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-latency-record|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-other-collected-definition|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-record-absent-everywhere|1/1 (20.7-100.0%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G4 / v2-record-repeated-gold|1/1 (20.7-100.0%)|0/1 (0.0-79.3%)|1/1 (20.7-100.0%)|
|G4 / v2-screenshot-record-01|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-screenshot-record-02|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-screenshot-record-03|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-screenshot-record-04|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-source-history|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-stale-model|1/1 (20.7-100.0%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|
|G4 / v2-waiting-application-load|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|G4 / v2-warehouse-scope|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|

### Expected verdict classes

Grouping uses exact sealed oracle labels; no expectation or score change. Case families above remain separately available.

| Cohort / expected verdict class | Official (95% Wilson) | Strict (95% Wilson) | Raw-reviewed (95% Wilson) | Raw harmful |
|---|---|---|---|---:|
|G1 / access difference|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|0|
|G1 / as designed|16/16 (80.6-100.0%)|15/16 (71.7-98.9%)|16/16 (80.6-100.0%)|0|
|G1 / different question|1/2 (9.5-90.5%)|1/2 (9.5-90.5%)|1/2 (9.5-90.5%)|0|
|G1 / failed job|4/4 (51.0-100.0%)|4/4 (51.0-100.0%)|4/4 (51.0-100.0%)|0|
|G1 / latency|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|0|
|G1 / not found|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0|
|G1 / refresh stale|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|0|
|G1 / source changed history|2/2 (34.2-100.0%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|2|
|G1 / transformation logic|6/6 (61.0-100.0%)|6/6 (61.0-100.0%)|6/6 (61.0-100.0%)|0|
|G1 / waiting on job|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|0|
|G2 / access difference|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|0|
|G2 / as designed|14/17 (59.0-93.8%)|14/17 (59.0-93.8%)|15/17 (65.7-96.7%)|0|
|G2 / as designed; historical value not found (no retained version before 2026-10-23)|2/3 (20.8-93.9%)|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|0|
|G2 / different question|3/6 (18.8-81.2%)|0/6 (0.0-39.0%)|2/6 (9.7-70.0%)|0|
|G2 / failed job|6/6 (61.0-100.0%)|6/6 (61.0-100.0%)|6/6 (61.0-100.0%)|0|
|G2 / latency|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|0|
|G2 / not found|0/4 (0.0-49.0%)|0/4 (0.0-49.0%)|1/4 (4.6-69.9%)|0|
|G2 / refresh stale|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|0/3 (0.0-56.1%)|0|
|G2 / source changed history|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|0|
|G2 / transformation logic|6/9 (35.4-87.9%)|6/9 (35.4-87.9%)|6/9 (35.4-87.9%)|0|
|G2 / waiting on job|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|2/3 (20.8-93.9%)|0|
|G3 / access difference|0/4 (0.0-49.0%)|0/4 (0.0-49.0%)|0/4 (0.0-49.0%)|0|
|G3 / as designed|6/17 (17.3-58.7%)|2/17 (3.3-34.3%)|3/17 (6.2-41.0%)|3|
|G3 / different question|0/4 (0.0-49.0%)|0/4 (0.0-49.0%)|0/4 (0.0-49.0%)|0|
|G3 / failed job|0/8 (0.0-32.4%)|0/8 (0.0-32.4%)|0/8 (0.0-32.4%)|0|
|G3 / latency|0/5 (0.0-43.4%)|0/5 (0.0-43.4%)|0/5 (0.0-43.4%)|0|
|G3 / not found|0/10 (0.0-27.8%)|0/10 (0.0-27.8%)|0/10 (0.0-27.8%)|0|
|G3 / refresh stale|0/4 (0.0-49.0%)|0/4 (0.0-49.0%)|0/4 (0.0-49.0%)|0|
|G3 / source changed history|0/4 (0.0-49.0%)|0/4 (0.0-49.0%)|0/4 (0.0-49.0%)|0|
|G3 / waiting on job|0/4 (0.0-49.0%)|0/4 (0.0-49.0%)|0/4 (0.0-49.0%)|0|
|G4 / access difference|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|0|
|G4 / as designed|7/8 (52.9-97.8%)|6/8 (40.9-92.9%)|6/8 (40.9-92.9%)|0|
|G4 / different question|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|0|
|G4 / failed job|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|0|
|G4 / latency|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|0|
|G4 / not found|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0|
|G4 / refresh stale|1/1 (20.7-100.0%)|0/1 (0.0-79.3%)|0/1 (0.0-79.3%)|0|
|G4 / source changed history|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|0|
|G4 / transformation logic|3/3 (43.9-100.0%)|2/3 (20.8-93.9%)|3/3 (43.9-100.0%)|0|
|G4 / waiting on job|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|0|

## Observed cost, cache and timing

Native provider settlements supply usage; missing capture usage is never substituted with zero. Investigation costs exclude authoring, grading, controls and smokes. Native duration is the Azure execution start-to-end interval, separate from worker wall time. It does not establish complete ticket admission-to-delivery time: per-ticket admission and queue timestamps were not recorded in the immutable case journals. Do not use it to claim the end-to-end time target. Unavailable times are not estimated. Exact timing groups (investigations, operational-only answers and holds) are in the linked JSON reports.

| Cohort | Usage-observed tickets | Investigation USD | USD / usage-observed ticket | Cache-read ratio | Native observed / missing | Native median / p90 seconds |
|---|---:|---:|---:|---:|---|---|
|G1|40|16.526970|0.413174|67.49%|36 / 4|245.0 / 317.0|
|G2|50|23.898689|0.477974|69.21%|43 / 7|206.0 / 307.0|

G2 has 10 unsealed native exceptions with unavailable usage; these remain graded but are outside the usage-observed denominator.

|G3|59|9.630812|0.163234|60.18%|13 / 46|200.0 / 323.0|

G3 has 1 unsealed native exceptions with unavailable usage; these remain graded but are outside the usage-observed denominator.

|G4|20|8.387129|0.419356|67.66%|20 / 0|212.0 / 291.0|

## Failure walkthroughs and next-round priorities

1. Historical change: the G1 history answers read current source47 against landing/model41 and chose latency without reading retained history. Those observations did not establish the requested historical edit. Two raw-confirmed harmful answers remain counted. Owner lifted the source-history pause for measurement; no harm was removed.
2. Stale model: all three G2 stale answers recreated7661 against source/landing7692 and identified the semantic-model split. The automatic-update fact port was unavailable, so the specific OFF setting was not established. Independent review calls this a triage gap, honest partial evidence and zero under the all-three rule, not a harmful confident finding.
3. Input admission: two application-baseline variants raised native COMPARISON_DETAILS_REQUIRED and exited1 before delivery. Each has ten preserved partial artifacts and no final seal. They are graded native exceptions, not retried as Blob404 plumbing failures, and their unknown usage is not fabricated.
4. Access and bounded investigation: G2 access produced an intake hold and two tool/time-limit outcomes. Exact raw-review reasons and query traces remain linked; no permission was expanded to improve scores.

5. Temporal queries: the active investigative route accepts native FOR SYSTEM_TIME AS OF and ALL on approved tables; the default bounded compiler rejects temporal Version nodes unless explicitly enabled. The pre-retention traces instead attempted invalid OPTION(FOR TIMESTAMP AS OF) syntax or unavailable catalog objects. These were rejected before dispatch and do not establish a retention policy. Record the query/tool/capability gap; do not widen the validator or change an expectation in this round. See runs/round25-temporal-validator-routes.json.

The waiting zero is timing-confounded: its job completed during the third investigation and the answer correctly reported completion, while the sealed expectation still required waiting. The independent reviewer retained the zero against that expectation. No oracle change or replacement run occurred.

G3 original-history review: three delivered answers checked current Bronze/Silver/Gold/model rows but never read the retained application temporal history that fresh controls had established. Job-history calls used unsupported subjects, and one answer followed a different current-data path. The fourth ticket held at intake. All four score zero, without a raw-confirmed harmful cause claim. This is a route/tool/intake failure, not proof that temporal syntax is universally blocked. The original saved evidence and fresh independent reasons are retained.

Priorities are drawn from backtracks only, with the owner-directed free-text intake regression first; grounded causal reasoning, decisive native triage facts, bounded query choice and explicit handoff follow. None is implemented in this frozen measurement round.


## Ranked fixes for the next round

Owner-directed order; evidence comes from saved backtracks and independent harm reviews. No fix is implemented in this frozen round.

1. Restore free-text intake and target selection. Put the G3 free-text regression first: keep the unchanged original R22 dev40 and held-out20 beside their original14/40 and5/20 scores. Missing-report questions, comparison admission and wrong-path selection prevent many tickets from reaching their relevant evidence; structured-form results must not conceal this weakness.
2. Ground causal findings in evidence actually read. Do not replace a measure/count explanation with an unsupported ETL defect, and do not infer historical source edits from current source-versus-landing differences. Retain every independently confirmed harmful answer.
3. Use supported native queries and the decisive path evidence before exhausting tools. Pre-dispatch rejection of invalid OPTION(FOR TIMESTAMP AS OF) syntax is not proof of a retention limitation; the active temporal route accepts native FOR SYSTEM_TIME syntax.
4. Supply the decisive native triage fact, particularly Direct Lake automatic-update state. Finding the numerical boundary alone does not establish the specific setting that caused it.
5. Deliver the requested supported conclusion, or a precise remaining gap. Keep recreation, current-state absence, historical evidence and business-intent questions distinct.

G3 harm pauses are lifted for measurement by owner decision. Previously delivered outcomes remain counted; no answer is rerun to improve its score.
## Evidence and restoration

[G1 grades](runs/round-twenty-five-g1-current-grades.json), [G2 grades](runs/round25-g2-current-grades.json), [G2 backtracks](runs/round25-g2-backtrack.json), [measurement image index](runs/round25-measurement-image-index.json), [G2 stale restoration](runs/round25-g2-stale-final-restoration.json). Source and definition hashes, native load completion and model totals are separate checks; no unmeasured full Bronze row hash is claimed. Temporal history stays on. At G2 closeout the fixture was restored to360source rows/model7661/automatic updatesOn. Later G3/G4 controls have their own restoration records; this historical closeout does not assert that an in-flight cohort is already restored.


## First-wrong-step groups

These are the saved graders/reviewers' first failing-step labels, not a new operator regrade. Native transport exceptions and benchmark confounds are retained separately in the receipts.

| Cohort | Zero-score groups |
|---|---|
|G2|intake: 14, query: 4, conclusion: 3, triage: 3|
|G3|intake: 40, reading results: 2, target: 8, conclusion: 7|
|G4|triage: 1, conclusion: 2, query: 1|

G1 has five raw zeros: two conclusion failures, two query failures, and one authored invalid-input contract finding. G2 includes a waiting-job expectation timing confound; it is not silently counted as an engine success. G3 includes one native URLError99 without a delivered answer.

## Timing by kind

Native durations are Azure execution start-to-end, not product admission-to-delivery. Worker timing and a separately recorded harness interval are available below. Harness intervals include fresh fixture admission, Azure CLI dispatch/polling and artifact retrieval; resumed polling timers are excluded. They must not be presented as pure product latency. Missing observations are not replaced with estimates.

| Cohort / kind | Native observed | Native median / p90 seconds | Fresh harness observed | Harness median / p90 seconds |
|---|---:|---|---:|---|
|G1 / full investigation|33|246.0 / 317.0|33|312.8 / 356.3|
|G1 / hold|0|unavailable / unavailable|3|294.5 / 295.3|
|G1 / operational status without layer queries|3|188.0 / 190.0|3|223.5 / 224.6|
|G2 / full investigation|39|213.0 / 310.0|39|287.1 / 395.0|
|G2 / hold|0|unavailable / unavailable|7|182.1 / 290.0|
|G2 / operational status without layer queries|4|173.5 / 188.0|4|203.6 / 225.4|
|G3 / full investigation|13|200.0 / 323.0|13|232.9 / 396.5|
|G3 / hold|0|unavailable / unavailable|46|89.5 / 190.7|
|G3 / operational status without layer queries|0|unavailable / unavailable|0|unavailable / unavailable|
|G4 / full investigation|19|213.0 / 298.0|19|259.0 / 344.1|
|G4 / hold|0|unavailable / unavailable|0|unavailable / unavailable|
|G4 / operational status without layer queries|1|180.0 / 180.0|1|217.5 / 217.5|

[Recorded harness intervals](runs/round25-recorded-harness-intervals.json) retain journal hashes. The native full-investigation medians exceed120seconds; no end-to-end speed target is claimed.

## Measurement and evidence limitations

The 180 requested outcomes comprise 169 sealed results and 11 retained unsealed native exceptions (ten G2 comparison-contract exceptions and one G3 transport exception). All 11 remain in the scoring denominators. Their unavailable capture usage is not estimated as zero. Two extra original Azure start responses remain unestablished, with no artifacts observed; their uniquely recorded replacements supply the requested scored outcomes. A separate G1 original answer was recovered from its seal without rerun, but its Azure execution binding/timing remains unestablished. No unknown original attempt is relabelled a pass or failure.

Operator blinding was partly broken. In addition to the earlier staging/status fragments, recovery commands accidentally printed saved answer fragments and an expanded split-report structure. No investigator or expectation tuning followed. Every G2-G4 assessment disagreement was decided by a fresh independent Claude call with only the approved saved-evidence packet, not by the operator. Primary/secondary packets use explicitly labelled bounded row/history samples where needed; raw disagreement review uses full saved evidence. Short aliases and exact pools are reversible; labelled samples are not claimed lossless.

The active native temporal query route accepts FOR SYSTEM_TIME syntax. Invalid OPTION(FOR TIMESTAMP AS OF) and unavailable objects were rejected before dispatch; this does not establish a retention policy. No validator fix was made. The R24 retrospective absence audit is separate: secondary is right on cause, and both original verdict labels were too strict under the substance rule. Its official 18/20 and all original records remain unchanged.

[All 180 image/outcome bindings](runs/round25-measurement-image-index.json), [frozen-runtime check](runs/round25-final-frozen-runtime.json), [33-control closeout](runs/round25-injection-closeout.json), [final native estate readback](runs/round25-final-estate-readback.json). Source360business/schema hashes match; Bronze aggregate 360 / 7,661 and native model 7661 agree; automatic updatesOn and temporal historyOn. A full Bronze row hash remains unestablished. Local controller counters exclude separately metered nested cloud probes; shared monthly ledger totals are authoritative. No all 180 exact-replay claim is made; prior CI replay gates remain separate.
