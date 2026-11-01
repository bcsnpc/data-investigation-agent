# Quality of frozen v0.24 â€” Round 25

## Current measurement

Saved-result snapshot: 2026-11-01T03:32:12.127605+00:00. Raw-reviewed is the headline; official and strict remain unchanged. G2 is the completed new held-out set (60/60 accounted for). G3 and G4 remain in progress until their requested totals are accounted for. Partial cohort figures must not be presented as full-set accuracy.

| Cohort | Official primary (95% Wilson) | Strict (95% Wilson) | Raw-reviewed (95% Wilson) | Raw harmful | Requested |
|---|---|---|---|---:|---:|
|G1|37/40 (80.1â€“97.4%)|34/40 (70.9â€“92.9%)|35/40 (73.9â€“94.5%)|2|40|
|G2|37/60 (49.0â€“72.9%)|32/60 (40.9â€“65.4%)|36/60 (47.4â€“71.4%)|0|60|
|G3|6/41 (6.9â€“28.4%)|2/41 (1.3â€“16.1%)|3/41 (2.5â€“19.4%)|3|60|
|G4|not run|not run|not run|not measured|20|

### Same original R22 splits

The original dev and held-out sets remain separate. Interim numerators use only graded tickets; requested counts show pending coverage. Historical R22 scores are official primary, not retrospectively raw-reviewed.

| Original split | Requested | R22 official (95% Wilson) | R25 official | R25 strict | R25 raw-reviewed |
|---|---:|---|---|---|---|
|dev|40|14/40 (22.1â€“50.5%)|6/32 (8.9â€“35.3%)|2/32 (1.7â€“20.1%)|3/32 (3.2â€“24.2%)|
|heldout|20|5/20 (11.2â€“46.9%)|0/9 (0.0â€“29.9%)|0/9 (0.0â€“29.9%)|0/9 (0.0â€“29.9%)|

G1 is unchanged dev v2. G3 compares unchanged R22 text (14/40dev and5/20held-out); G4 is a regression comparison with R23's6/20. The prior R24 official18/20 remains unchanged. Related variants share fixtures, so Wilson intervals describe this observed sample, not independent client-estate accuracy.

## Grader agreement and correctness dimensions

Core agreement means verdict, layer, cause and harm flags. Full assessment additionally includes handoff quality, partial status and first failing step. It is not honest to label the higher core rate as agreement on the entire assessment. All G2â€“G4 assessment disagreements require fresh independent Claude review; no operator adjudication.

| Cohort | Core agreement (95% Wilson) | Full assessment agreement (95% Wilson) | Raw verdict | Raw layer | Raw cause | Pending raw reviews |
|---|---|---|---|---|---|---:|
|G1|37/40 (80.1â€“97.4%)|8/40 (10.5â€“34.8%)|35/40 (73.9â€“94.5%)|35/40 (73.9â€“94.5%)|35/40 (73.9â€“94.5%)|0|
|G2|51/60 (73.9â€“91.9%)|13/60 (13.1â€“33.6%)|42/60 (57.5â€“80.1%)|44/60 (61.0â€“82.9%)|37/60 (49.0â€“72.9%)|0|
|G3|31/41 (60.7â€“86.2%)|7/41 (8.5â€“31.3%)|3/41 (2.5â€“19.4%)|8/41 (10.2â€“34.0%)|7/41 (8.5â€“31.3%)|0|

Operator blinding was partly broken by the earlier two staging/status fragments and an additional G3 access status dump that included saved outcome text. These exposures are disclosed in decisions.md and the round summary. No investigator logic or expectation was changed afterward. G1's original raw reviews remain; G2â€“G4 disagreements are decided by independent Claude calls receiving only the owner-approved packet.

## Class results

Every cell includes its95% Wilson interval. Original case-family IDs are retained; G2 also has a verdict-label grouping in its JSON receipt.

| Cohort / case family | Official | Strict | Raw-reviewed |
|---|---|---|---|
|G1 / v2-access-export|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-application-baseline|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-before-temporal-retention|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|
|G1 / v2-billing-invoices|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-billing-mrr|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-failed-application-load|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-failed-billing-transform|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-fixture-quantity|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-latency-record|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-other-collected-definition|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-record-absent-everywhere|2/2 (34.2â€“100.0%)|1/2 (9.5â€“90.5%)|2/2 (34.2â€“100.0%)|
|G1 / v2-record-repeated-gold|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-screenshot-record-01|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-screenshot-record-02|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-screenshot-record-03|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-screenshot-record-04|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-source-history|2/2 (34.2â€“100.0%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|
|G1 / v2-stale-model|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-waiting-application-load|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G1 / v2-warehouse-scope|1/2 (9.5â€“90.5%)|1/2 (9.5â€“90.5%)|1/2 (9.5â€“90.5%)|
|G2 / v4-access-export|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|
|G2 / v4-application-baseline|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|1/3 (6.1â€“79.2%)|
|G2 / v4-before-temporal-retention|2/3 (20.8â€“93.9%)|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|
|G2 / v4-billing-invoices|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|3/3 (43.9â€“100.0%)|
|G2 / v4-billing-mrr|3/3 (43.9â€“100.0%)|3/3 (43.9â€“100.0%)|3/3 (43.9â€“100.0%)|
|G2 / v4-failed-application-load|3/3 (43.9â€“100.0%)|3/3 (43.9â€“100.0%)|3/3 (43.9â€“100.0%)|
|G2 / v4-failed-billing-transform|3/3 (43.9â€“100.0%)|3/3 (43.9â€“100.0%)|3/3 (43.9â€“100.0%)|
|G2 / v4-fixture-quantity|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|
|G2 / v4-latency-record|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|
|G2 / v4-other-collected-definition|3/3 (43.9â€“100.0%)|3/3 (43.9â€“100.0%)|3/3 (43.9â€“100.0%)|
|G2 / v4-record-absent-everywhere|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|
|G2 / v4-record-repeated-gold|1/3 (6.1â€“79.2%)|1/3 (6.1â€“79.2%)|1/3 (6.1â€“79.2%)|
|G2 / v4-sample-business-meaning|3/3 (43.9â€“100.0%)|0/3 (0.0â€“56.1%)|2/3 (20.8â€“93.9%)|
|G2 / v4-sample-technical|3/3 (43.9â€“100.0%)|3/3 (43.9â€“100.0%)|3/3 (43.9â€“100.0%)|
|G2 / v4-screenshot-billing-invoices|1/1 (20.7â€“100.0%)|1/1 (20.7â€“100.0%)|1/1 (20.7â€“100.0%)|
|G2 / v4-screenshot-billing-mrr|1/1 (20.7â€“100.0%)|1/1 (20.7â€“100.0%)|1/1 (20.7â€“100.0%)|
|G2 / v4-screenshot-fixture-01|1/1 (20.7â€“100.0%)|1/1 (20.7â€“100.0%)|1/1 (20.7â€“100.0%)|
|G2 / v4-screenshot-fixture-02|1/1 (20.7â€“100.0%)|1/1 (20.7â€“100.0%)|1/1 (20.7â€“100.0%)|
|G2 / v4-screenshot-fixture-03|1/1 (20.7â€“100.0%)|1/1 (20.7â€“100.0%)|1/1 (20.7â€“100.0%)|
|G2 / v4-screenshot-fixture-04|1/1 (20.7â€“100.0%)|1/1 (20.7â€“100.0%)|1/1 (20.7â€“100.0%)|
|G2 / v4-source-history|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|
|G2 / v4-stale-model|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|
|G2 / v4-waiting-application-load|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|
|G2 / v4-warehouse-scope|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|
|G3 / R17-01|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / R17-02|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / R17-03|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / R17-04|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / R17-05|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / R17-06|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / R17-07|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / R17-08|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / R17-09|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|1/1 (20.7â€“100.0%)|
|G3 / R17-10|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / R17-11|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / R17-12|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / access-export-1|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|
|G3 / access-export-2|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / access-export-3|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / baseline-S01|2/2 (34.2â€“100.0%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|
|G3 / baseline-S02|2/2 (34.2â€“100.0%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|
|G3 / baseline-S03|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|
|G3 / failed-billing-transform|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|
|G3 / failed-fixture-load|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|
|G3 / fourth-failed-billing-transform|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|
|G3 / history-source-900201|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|
|G3 / history-source-900202|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / history-source-900203|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / latency-900501|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|
|G3 / latency-900502|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|
|G3 / latency-900503|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / waiting-billing-load|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / waiting-billing-transform|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|0/1 (0.0â€“79.3%)|
|G3 / waiting-fixture-load|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|

### Expected verdict classes

Grouping uses exact sealed oracle labels; no expectation or score change. Case families above remain separately available.

| Cohort / expected verdict class | Official (95% Wilson) | Strict (95% Wilson) | Raw-reviewed (95% Wilson) | Raw harmful |
|---|---|---|---|---:|
|G1 / access difference|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|0|
|G1 / as designed|16/16 (80.6â€“100.0%)|15/16 (71.7â€“98.9%)|16/16 (80.6â€“100.0%)|0|
|G1 / different question|1/2 (9.5â€“90.5%)|1/2 (9.5â€“90.5%)|1/2 (9.5â€“90.5%)|0|
|G1 / failed job|4/4 (51.0â€“100.0%)|4/4 (51.0â€“100.0%)|4/4 (51.0â€“100.0%)|0|
|G1 / latency|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|0|
|G1 / not found|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|0|
|G1 / refresh stale|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|0|
|G1 / source changed history|2/2 (34.2â€“100.0%)|0/2 (0.0â€“65.8%)|0/2 (0.0â€“65.8%)|2|
|G1 / transformation logic|6/6 (61.0â€“100.0%)|6/6 (61.0â€“100.0%)|6/6 (61.0â€“100.0%)|0|
|G1 / waiting on job|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|2/2 (34.2â€“100.0%)|0|
|G2 / access difference|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|0|
|G2 / as designed|14/17 (59.0â€“93.8%)|14/17 (59.0â€“93.8%)|15/17 (65.7â€“96.7%)|0|
|G2 / as designed; historical value not found (no retained version before 2026-10-23)|2/3 (20.8â€“93.9%)|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|0|
|G2 / different question|3/6 (18.8â€“81.2%)|0/6 (0.0â€“39.0%)|2/6 (9.7â€“70.0%)|0|
|G2 / failed job|6/6 (61.0â€“100.0%)|6/6 (61.0â€“100.0%)|6/6 (61.0â€“100.0%)|0|
|G2 / latency|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|0|
|G2 / not found|0/4 (0.0â€“49.0%)|0/4 (0.0â€“49.0%)|1/4 (4.6â€“69.9%)|0|
|G2 / refresh stale|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|0|
|G2 / source changed history|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|0|
|G2 / transformation logic|6/9 (35.4â€“87.9%)|6/9 (35.4â€“87.9%)|6/9 (35.4â€“87.9%)|0|
|G2 / waiting on job|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|2/3 (20.8â€“93.9%)|0|
|G3 / access difference|0/4 (0.0â€“49.0%)|0/4 (0.0â€“49.0%)|0/4 (0.0â€“49.0%)|0|
|G3 / as designed|6/15 (19.8â€“64.3%)|2/15 (3.7â€“37.9%)|3/15 (7.0â€“45.2%)|3|
|G3 / failed job|0/6 (0.0â€“39.0%)|0/6 (0.0â€“39.0%)|0/6 (0.0â€“39.0%)|0|
|G3 / latency|0/5 (0.0â€“43.4%)|0/5 (0.0â€“43.4%)|0/5 (0.0â€“43.4%)|0|
|G3 / not found|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|0/3 (0.0â€“56.1%)|0|
|G3 / source changed history|0/4 (0.0â€“49.0%)|0/4 (0.0â€“49.0%)|0/4 (0.0â€“49.0%)|0|
|G3 / waiting on job|0/4 (0.0â€“49.0%)|0/4 (0.0â€“49.0%)|0/4 (0.0â€“49.0%)|0|

## Observed cost, cache and timing

Native provider settlements supply usage; missing capture usage is never substituted with zero. Investigation costs exclude authoring, grading, controls and smokes. Native duration is the Azure execution start-to-end interval, separate from worker wall time. It does not establish complete ticket admission-to-delivery time: per-ticket admission and queue timestamps were not recorded in the immutable case journals. Do not use it to claim the end-to-end time target. Unavailable times are not estimated. Exact timing groups (investigations, operational-only answers and holds) are in the linked JSON reports.

| Cohort | Usage-observed tickets | Investigation USD | USD / usage-observed ticket | Cache-read ratio | Native observed / missing | Native median / p90 seconds |
|---|---:|---:|---:|---:|---|---|
|G1|40|16.526970|0.413174|67.49%|36 / 4|245.0 / 317.0|
|G2|50|23.898689|0.477974|69.21%|43 / 7|206.0 / 307.0|

G2 has 10 unsealed native exceptions with unavailable usage; these remain graded but are outside the usage-observed denominator.


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

## Archived earlier checkpoints

# Quality of frozen v0.24 - Round 25

Current G1 final (40): **raw-reviewed35/40 (87.5%, Wilson73.9-94.5%)**, official37/40 (80.1-97.4%), strict34/40 (70.9-92.9%). **Two raw-confirmed harmful history answers remain counted.** Owner31Oct lifted the history measurement pause; all3G2history will be measured. G2-G4 assessment disagreements will be adjudicated by fresh independent Claude calls, not the exposed operator. G2 headline remains pending.

G1 investigation-only cost $16.526970 ($0.413174/ticket); native median245s,p90 317s (36observed/4unavailable); worker median207.7s,p90 285.3s (40observed); cache-read ratio67.49%. One lost start response was recovered from its original sealed answer without resubmission; its native execution details remain unknown.

## Earlier checkpoint: 31 graded G1 outcomes

Measurement is in progress. The primary and secondary graders disagree materially on the history family, so the current primary score must not be presented as a clean quality pass. No investigator, prompt, model, caching or query change has been made.

The raw-reviewed headline for the 31 double-graded G1 tickets is **26/31** (95% Wilson 67.4-92.9%), with **2 harmful historical-question answers**. Official primary is 28/31 (75.1-96.7%); strict is 25/31 (63.7-90.8%). Raw review supports the second grader on both history disagreements; the history family is paused. Original grades and expectations remain unchanged.

| Completed G1 | Official primary | Strict | Raw-reviewed (headline) |
|---|---|---|---|
| Correct / graded | 28/31 | 25/31 | 26/31 |
| 95% Wilson | 75.1-96.7% | 63.7-90.8% | 67.4-92.9% |
| Harmful flags | 0 | 2 (either grader) | 2 confirmed |

R24's held-out official score remains18/20. Retrospective raw review finds the secondary right on the absent-record cause, and both graders overly strict on its verdict label under the existing substance-based contract. The earlier raw review is preserved with a dated correction; no ticket, expectation, official score, engine run or provider grade was changed. [Saved-capture review](runs/round-twenty-five-r24-held-disagreement-raw-review.json).

Agreement is 28/31 (95% Wilson 75.1-96.7%). Related variants share fixtures; these intervals describe the observed sample and do not establish accuracy on independent client estates.

| Cohort | Status |
|---|---|
| G1, unchanged v2 dev | 31/40 double-graded so far; remaining cases pending |
| G2, new held-out v4 - headline |60 native-verified tickets sealed at c61a5c3e; prepared, not run |
| G3, unchanged R22 text |60 unchanged text inputs prepared; not run |
| G4, prior R23 held-out v2 - regression |20 unchanged sealed inputs prepared; not run |

The independent writer produced60 new tickets:48forms,12free text, six real screenshots and all three estates. Every oracle is native-fact verified and the set was sealed at commit c61a5c3e before any G2 execution; wording remains unopened by the engine developer. Original drafts and all pre-seal oracle versions survive. Wrong-page selections were preserved and independently reviewed. Fresh native fault checks remain required at execution. [Seal](runs/round-twenty-five-v4-seal.json).

| Class (G1 interim) | Official primary (95% CI) | Strict (95% CI) | Raw-reviewed (95% CI) |
|---|---|---|---|
|v2-access-export|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-application-baseline|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-before-temporal-retention|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|v2-billing-invoices|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-billing-mrr|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-failed-application-load|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-failed-billing-transform|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-fixture-quantity|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-latency-record|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-other-collected-definition|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|1/1 (20.7-100.0%)|
|v2-record-absent-everywhere|2/2 (34.2-100.0%)|1/2 (9.5-90.5%)|2/2 (34.2-100.0%)|
|v2-record-repeated-gold|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-source-history|2/2 (34.2-100.0%)|0/2 (0.0-65.8%)|0/2 (0.0-65.8%)|
|v2-stale-model|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-waiting-application-load|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|2/2 (34.2-100.0%)|
|v2-warehouse-scope|1/2 (9.5-90.5%)|1/2 (9.5-90.5%)|1/2 (9.5-90.5%)|

The warehouse-scope-v2 benchmark zero is an authored report-ID contract finding; it remains in the unchanged denominator and is not demonstrated engine scope-comparison failure. See the native catalog/hash audit.

## Current failure pattern

Both history cases compare current source47 against landing/model41 and choose latency. They explicitly admit that no retained source history was read. The second grader correctly distinguishes that current-state observation from proving a historical edit. The primary treats the two verdict classes as interchangeable and passes both. Both explanations are preserved in [the per-ticket record](runs/round-twenty-five-g1-current-grades.json), with [raw-output review](runs/round-twenty-five-history-raw-review.json) and [saved-trace backtrack](failure-backtrack.md). This is an interpretation disagreement, not lost projection bytes or an altered expectation; no engine rerun or silent score override was made.

The native current-state numbers are supported. The unsupported step is presenting latency as the answer to the historical-change question. The answer footer also reports job details unavailable after the narrative has named a successful job window. These belong in the next-round fix list; the engine remains frozen here.

The two pre-retention cases are different: current16 was readable at all compared layers, but attempts to read an unavailable audit object replaced the necessary source-history check. They exhausted the tool/time limit without a retention-boundary answer. Raw review supports the secondary grader on the first bad query and the incomplete handoff. The five current raw zeros therefore comprise four engine failures and one input-contract finding; all benchmark scores remain unchanged. [Backtrack index and three walkthroughs](failure-backtrack.md).

## Timing, costs and retained operational failures

The 31 double-graded cases used **$13.325343** for investigation, averaging **$0.429850** per ticket. Native Azure duration, including startup and publication, had median227.5s and p90299s (nearest rank) for the 28/31 executions with native start/end times. Missing native end times are not estimated. Provider-settled cached input was4,794,667 of7,111,716 input tokens: **67.42%**. Every case cost matched its authoritative reservation settlements. Authoring, grading and fixture controls are separate. [Per-ticket observed costs, timing and cache](runs/round-twenty-five-g1-observed-cost-timing-cache.json).

| Timing group | Tickets | Native durations observed | Native median / p90 seconds | Worker wall median / p90 seconds |
|---|---:|---:|---|---|
|full investigation|25|25|236.0 / 299.0|193.64776847400003 / 270.064544503|
|hold|3|0|not available|226.12211136400003 / 234.758102028|
|operational status without layer queries|3|3|188.0 / 190.0|154.97200069000002 / 159.73575022|

The billing control first stopped on a 5-second PostgreSQL budget lock before scoring. Its existing failed job was reconciled and the original pipeline hash restored. One open request was settled UNCERTAIN and remains charged. The normal billing bootstrap still returns its pre-existing2011 CREATE SCHEMA error; it was not repaired. Waiting completed and restored its original hash. The first history precheck timed out before mutation; its distinct continuation delivered both cases and restored the original360-row/source-schema hashes plus a successful real load. A billing boundary probe correctly rejected a fixture-policy connection; one replacement used the unchanged billing reader route. The first latency case failed on a PostgreSQL lock before delivery and preserved a partial capture; its source row/schedule were restored, and its one new-case replacement completed. Both latency cases are sealed, the owned source row and schedule were removed, and original row/schema hashes matched. No identity or permission was changed.


October checkpoint: further investigation admissions defer because37 investigation requests remain against the unchanged40-request case bound. Remaining9G1 precede G2/G3/G4 in November; this is not a completed Round25 result. All250 owned model reservations (including31 engine case IDs) are settled, all injections are restored, and no local worker/grader remains active. AI account134.455715/146USD; SCAN2291/2500, INV9368/9405, REST45/95 with50restoration requests left; historical70kept. No cap or reserve was changed.
