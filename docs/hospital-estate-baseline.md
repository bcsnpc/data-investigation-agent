# HealthNet baseline status

Build in progress. Local verification proves relational/financial invariants and deterministic rebuilds only. Small generator test6/6 passed. Full population generation is running. baseline.json contains25 independently evaluated local visual-equivalent SQL queries when local marts are built; native model/report and bookmark checks are not yet established. RLS role testing is pending. No hospital tickets, DIA runs or expectations were created.

## Full-population local checkpoint, 2026-10-30

Source relational and financial verification passed all 13 checks. Native
Azure source loading remains in progress. Native source-to-raw-to-mart-to-
model-to-report reconciliation, default/bookmark visual values and owner
RLS/OLS role testing remain pending; no native success is inferred from
local results. The older generated local marts are preserved; a separate
current-definition local rebuild is in progress from the same source
files. All 17 focused generator/artifact checks now pass. Reports contain
33 containers including text and slicers, two filtered bookmarks and one
drillthrough; field-binding checks pass, rendering is not yet verified.


## Full local relational baseline, 2026-10-30

These values are independently evaluated SQLite projections from the full seeded sources. They are **not native model/report visual checks**. Default and bookmark values served by Power BI, and native RLS results, remain pending. SQL for every local check is retained in baseline.json; native receipts will be added separately.

| Local mart | Rows | Canonical SHA-256 |
|---|---:|---|
| core_facility | 3 | `6c5d50f37b33d76543fa54b28dd9939840a35d8ce2f3905720d962b3c15fcde5` |
| core_department | 33 | `01bb76c70de5c0358d3c47f540668b5c9e62a9836988282e349505485e51a711` |
| core_provider | 360 | `e987fd561a7e03eba58ba0bb70df93f94f02fff8f12b9721d463e01c454cfd23` |
| core_provider_department_history | 396 | `2898518e2c48c374932e6f8f5debb938c7d76ed21136d11f2741b00bbc19f49b` |
| core_payer | 4 | `5ac613238248d94ba72430d7d081414ad903b919f13285d500ce30a7d9cfcb13` |
| core_payer_plan_history | 14 | `aff9500732d59780a1a8f838220c659afd1e70fc0424b127a1a508d0e0850a05` |
| stg_patient | 60,000 | `297986e08ee96a44b6417ec9b7dfb5f744501990951368ce36f3001642baa700` |
| mart_encounter | 249,575 | `fab5d9b2983ca74746f799b053f4ab2af346933f025f63a34c9909a1029144a4` |
| mart_ed_visit | 104,729 | `4a6c65aedd76b6730a53bbdde40c1a353f1e8f87e0355227fbda6e3674960f5a` |
| mart_order | 1,498,788 | `2a022db7164c3906095c83d67616a4145c46874ce35f1b33c92489dfb38fae63` |
| mart_charge | 505,322 | `f68912b12ee90dfa8dfdefc2d0b8ab898cfb0cc4d4cda12ae4e122dee395027d` |
| mart_claim | 289,614 | `cf204f66e08f8c1c9e501260b2d42b15b4e2ac650c429ff3bd293001946645d9` |
| mart_remittance | 536,956 | `6dbba62c8e7618d821dffc49878e79c19c254751aee31be2e7c8d266efc1a26c` |
| mart_payment | 256,716 | `531d0d9a837e029b3251b01e8d069bf2a7092acd043d4921fce828cf1473d8c6` |
| mart_adjustment | 268,700 | `f9e8d6313aeebf1f2c78dbe6542e2c960838a010d85bf92d2a370a14adb50ea2` |
| mart_ar_aging | 12,912 | `308ec3c27734f987ee9f95aad96b5586db8b31708cda504b4d78648adc9ce2b7` |
| mart_procedure | 16,333 | `88789c5348311bcccce247fa15ff7a87a00c5abefbc953843b6dfd3980c3107e` |
| mart_census_daily | 1,182 | `de25fa2c48712a385063390d5f9fdbb3bf8921513f118cb59c953f0ca45b7438` |
| mart_provider_productivity_daily | 95,018 | `3eb18a2598032678e9bbf44763e49077aeb996fab6da50f1bfb4b0bb3b8b6ef8` |

| Local check | Result / result-set digest |
|---|---|
| operations/Midnight Census | `[[565]]` |
| operations/Bed Occupancy % | `[[0.6822767651130596]]` |
| operations/Encounters | `[[249575]]` |
| operations/Unique Patients | `[[57764]]` |
| operations/Admissions | `[[46942]]` |
| operations/Discharges | `[[248855]]` |
| operations/ALOS by Service | `7 rows; SHA-256 d69a5ea998d051c63677e768f5c5ed28a2e7b76d5192176f27e2c8d15b2e694b` |
| operations/ED Arrivals by Hour | `24 rows; SHA-256 783955b4feca9b0f1a42fd280d55b336dc0513d199d766d4405e0267751ad844` |
| operations/ED Door-to-Provider | `[[25]]` |
| operations/LWBS % | `[[0.02211421860229736]]` |
| operations/Orders by Type and Status | `15 rows; SHA-256 9586cc58816c4a74f77c77f21700b05f239e2d4e1d76da36199bafa40f8445b0` |
| operations/Turnaround by Type | `[["IMAGING",89.85135964853866],["LAB",54.91373931516771],["PHARMACY",34.99581122000411]]` |
| operations/Patient Detail | `100 rows; SHA-256 38abecd04e326eae2759bac360165c9b097964853aecf88e9826a7f5882ad1a4` |
| revenue/Gross by Service Month | `13 rows; SHA-256 1bb9589aa6a0ca3457beac5d69e8131695ad998eba62c6d04b1d5fdec26d5453` |
| revenue/Gross by Post Month | `13 rows; SHA-256 9b4a67df5ae9025b416be9795ca58d4813feebf1657dcc570fe1347473641832` |
| revenue/Collections by Month | `13 rows; SHA-256 ce19849d651f9ccb1b7d62f16b549beb65c9ccdaf84741ffae6b424e4e7440d3` |
| revenue/Net Revenue | `[[81305963474]]` |
| revenue/Payer Mix | `[[1,72025075427],[2,62342922341],[3,43893382115],[4,15338186045]]` |
| revenue/Denials by Category | `8 rows; SHA-256 f5fccd44618005db9b132604b7d4b9a20db2917735bbe6580708c6eee5c03c1a` |
| revenue/Initial Denial Rate | `[[0.12066662945038711]]` |
| revenue/Final Denial Rate | `[[0.028582168874601407]]` |
| revenue/A/R Aging | `[["0-30",4279283153],["31-60",2226791548]]` |
| revenue/Writeoffs | `[["BAD_DEBT",-1406818801],["CHARITY",-5855000],["CONTRACTUAL",-110880928653]]` |
| productivity/Visits per Doctor | `360 rows; SHA-256 edd254b1d93d63e9e555eeec5dc0b3d163b210f0c7cc531c41fc9699e31c4b5c` |
| productivity/Procedure Workload | `271 rows; SHA-256 d3ce26e4b4e6bd130496635fd667c90f78df050803d942a31d903fbecb463051` |
| productivity/Orders per Doctor | `361 rows; SHA-256 78ebb8ff760db85ad42928f56e899b7fd98e2922d93fc685b68943d520286fe5` |
| productivity/Department Leaderboard | `25 rows; SHA-256 9a12e9720600cc1540eff1dbd78108200125ba03d8c5a337215cce618fd2d2f1` |
| productivity/Workload per FTE | `360 rows; SHA-256 73f17d06192d9f188ae137f67b6835d7a9f92d3cc78717cbc50120cabe0d8286` |

These local checks do not yet cover every generated visual or filtered bookmark. In particular, scalar checks and result-set hashes cannot replace native visual filtering/reconciliation. No missing native number is estimated.

### First native raw/preparation reconciliation, 2026-10-30 (America/Chicago)

These owner SELECTs ran through the Warehouse SQL endpoint against hn_raw after billing pipeline 4b3a5889 completed. They are native observations, not estimates.

| Native raw check | Rows | Amount (integer cents) |
|---|---:|---:|
| Billing charge | 505,322 | 193,599,565,928 |
| Billing payment | 256,716 | 74,799,888,773 |
| Billing adjustment | 268,700 | -112,293,602,454 |
| Billing A/R snapshots | 12,912 | 6,506,074,701 on 2026-10-29 |

The conservation identity holds exactly: 193,599,565,928 - 112,293,602,454 - 74,799,888,773 = 6,506,074,701 cents. This does not assert that every claim-line rounding definition equals the account balance.

Native MPI preparation contains 60,000 rows and 59,400 distinct survivor IDs. Native Dataflow output contains 14 payer-history and 396 department-mapping rows. These counts agree with the local independently evaluated projections. Receipt: `.local/hospital-estate/billing-native-checks01.json`, served owner admin@skynwhy.com. Clinical/raw full reconciliation and model/report checks are still pending at this checkpoint.

### Full-size reset verification, 2026-10-30 (America/Chicago)

A second complete build in a fresh directory used seed20261030 and the full volumes (60,000 patients,250,000 encounters,1,500,000 order lines). All32 source row counts and canonical hashes match, and generation.json is byte-identical. The13 source invariants pass again. All19 local mart row counts/hashes and all28 independent local baseline query results match the first current build. This is a complete local reset test; it does not substitute for the native report/model checks. Local receipts: reset-v2/generation.json,verification.json,baseline.json and reset-comparison.json under .local/hospital-estate. No native source was reset during this test.

### Final native visual query baseline, owner date 2026-10-30

All three final model refreshes Completed. The 34 visual containers yield 62 default/bookmark contexts: 56 data queries and 6 static text contexts. These are native model queries compiled from the authored visual fields and categorical bookmark filters; browser rendering and role simulation are separate checks. Tables are deterministic windows of at most 100 rows, with the full result cardinality returned by the same query. A window hash does not claim to hash the full population. Receipt: `.local/hospital-estate/powerbi-owner.json`, `visual_baselines_final`.

| Model / visual | Context | Native result |
|---|---|---|
| revenue / A/R aging at latest snapshot | default | `[{"[A/R Balance]":43654.18,"mart_ar_aging[aging_bucket]":"61-90"},{"[A/R Balance]":22267915.48,"mart_ar_aging[aging_bucket]":"31-60"},{"[A/R Balance]":42792831.53,"mart_ar_aging[aging_bucket]":"0-30"}]` |
| revenue / A/R aging at latest snapshot | Commercial payers | `[{"[A/R Balance]":3312.95,"mart_ar_aging[aging_bucket]":"61-90"},{"[A/R Balance]":2358529.0,"mart_ar_aging[aging_bucket]":"31-60"},{"[A/R Balance]":4353533.01,"mart_ar_aging[aging_bucket]":"0-30"}]` |
| revenue / Gross service date vs post date | default | `13 returned / 13 total; window SHA-256 d15069174bae40640c5fb931d172e8981adebb22a2eb585e9b98a48f618a2007` |
| revenue / Gross service date vs post date | Commercial payers | `13 returned / 13 total; window SHA-256 9b14de3168402d1b5b859eb4d52aed66ddd40f512e70108ba5860d2a11b00ab0` |
| revenue / Original denied dollars by category | default | `8 returned / 8 total; window SHA-256 56f9423e7520432a7afbb586d0e148c1cecd18fcd13ae5999cddf62fb8291f82` |
| revenue / Original denied dollars by category | Commercial payers | `8 returned / 8 total; window SHA-256 435b510e6a7f54f9a92a3b35e6d98d1dc39b2e28abb8c736606d57a6a8704424` |
| revenue / Net Revenue | default | `[{"[Net Revenue]":813059634.74}]` |
| revenue / Net Revenue | Commercial payers | `[{"[Net Revenue]":186990499.73}]` |
| revenue / Denial definitions and writeoffs | default | `[{"[Denial Rate ($)]":0.05145372557138885,"[Final Denial Rate]":0.028582168874601407,"[Initial Denial Rate (count)]":0.12066662945038711,"[Writeoffs]":14068188.01}]` |
| revenue / Denial definitions and writeoffs | Commercial payers | `[{"[Denial Rate ($)]":0.05248571641372662,"[Final Denial Rate]":0.028684841222288794,"[Initial Denial Rate (count)]":0.12143401416172617,"[Writeoffs]":2778492.39}]` |
| revenue / Payer | default | `[{"core_payer[payer_group]":"Medicare"},{"core_payer[payer_group]":"Medicaid"},{"core_payer[payer_group]":"Commercial"},{"core_payer[payer_group]":"SelfPay"}]` |
| revenue / Payer | Commercial payers | `[{"core_payer[payer_group]":"Commercial"}]` |
| revenue / Charge Rows | default | `[{"[Charge Rows]":505322}]` |
| revenue / Charge Rows | Commercial payers | `[{"[Charge Rows]":113978}]` |
| revenue / Initial Denial Rate (count) | default | `[{"[Initial Denial Rate (count)]":0.12066662945038711}]` |
| revenue / Initial Denial Rate (count) | Commercial payers | `[{"[Initial Denial Rate (count)]":0.12143401416172617}]` |
| revenue / Gross Charges | default | `[{"[Gross Charges]":1935995659.28}]` |
| revenue / Gross Charges | Commercial payers | `[{"[Gross Charges]":438933821.15}]` |
| revenue / Month | default | `13 returned / 13 total; window SHA-256 35fb927d5971177c8a82147c1493eb01478d731b48e0f738f8b8227802026974` |
| revenue / Month | Commercial payers | `13 returned / 13 total; window SHA-256 35fb927d5971177c8a82147c1493eb01478d731b48e0f738f8b8227802026974` |
| revenue / Facility | default | `[{"core_facility[name]":"HealthNet North"},{"core_facility[name]":"HealthNet Central"},{"core_facility[name]":"HealthNet South"}]` |
| revenue / Facility | Commercial payers | `[{"core_facility[name]":"HealthNet North"},{"core_facility[name]":"HealthNet Central"},{"core_facility[name]":"HealthNet South"}]` |
| revenue / Payer mix by service-date charges | default | `[{"[Gross Charges]":720250754.27,"core_payer[payer_group]":"Medicare"},{"[Gross Charges]":623429223.41,"core_payer[payer_group]":"Medicaid"},{"[Gross Charges]":438933821.15,"core_payer[payer_group]":"Commercial"},{"[Gross Charges]":153381860.45,"core_payer[payer_group]":"SelfPay"}]` |
| revenue / Payer mix by service-date charges | Commercial payers | `[{"[Gross Charges]":438933821.15,"core_payer[payer_group]":"Commercial"}]` |
| revenue / Collections | default | `[{"[Collections]":747998887.73}]` |
| revenue / Collections | Commercial payers | `[{"[Collections]":163878752.95}]` |
| revenue /  | default | `Static text; no data query` |
| revenue /  | Commercial payers | `Static text; no data query` |
| productivity / Month | default | `13 returned / 13 total; window SHA-256 35fb927d5971177c8a82147c1493eb01478d731b48e0f738f8b8227802026974` |
| productivity /  | default | `Static text; no data query` |
| productivity / Department | default | `33 returned / 33 total; window SHA-256 f34aef1153c26b36a99316d8f95f653bb40c9713853716dafa7744d1bc07930b` |
| productivity / Department and doctor leaderboard | default | `100 returned / 435 total; window SHA-256 b35b095aee67bfa8700c8d8fad0ec9c4318a1ffdcc64ca8b6c9248b850e0f313` |
| productivity /  | default | `Static text; no data query` |
| productivity / Doctor encounters | default | `100 returned / 249575 total; window SHA-256 7d10df676ba5dc69989c1c49435b3047184303717a0c3cbb89a97d96617a7afe` |
| operations / Admissions, discharges and readmissions | default | `[{"[30-day Readmission %]":0.1179753738656214,"[Admissions]":46942,"[Discharges]":248855,"[Visits]":249575}]` |
| operations / Admissions, discharges and readmissions | North ED only | `[{"[30-day Readmission %]":null,"[Admissions]":null,"[Discharges]":47413,"[Visits]":47441}]` |
| operations / ED arrivals by local hour | default | `24 returned / 24 total; window SHA-256 3786eb6f6c45d01cd85cbb1b8adcd2824c876e8afb0d21770fa7cea2987445c5` |
| operations / ED arrivals by local hour | North ED only | `24 returned / 24 total; window SHA-256 6f74588f0a2fb901074170695f5cda937db7e293fdb12c10d3bbaf250451afa6` |
| operations / Order lines by type and status | default | `15 returned / 15 total; window SHA-256 ee70494651dc1905b1a62314de1899029fb3043ca55f84535f22c50fd1318d95` |
| operations / Order lines by type and status | North ED only | `15 returned / 15 total; window SHA-256 caf91866b315227305f327379b418412a8ba6a8968a88f9c54ef720b140b9a02` |
| operations / ALOS by service line | default | `7 returned / 7 total; window SHA-256 44c13f1930783b63e6f625a8978fa6bd4ffeba6641cc13b660bb3b196719139e` |
| operations / ALOS by service line | North ED only | `[]` |
| operations /  | default | `Static text; no data query` |
| operations /  | North ED only | `Static text; no data query` |
| operations / Month | default | `14 returned / 14 total; window SHA-256 721558f3193f4e0b84de495eb31d372dd8c52248d67a8ae00026e0d011bb3ba3` |
| operations / Month | North ED only | `14 returned / 14 total; window SHA-256 721558f3193f4e0b84de495eb31d372dd8c52248d67a8ae00026e0d011bb3ba3` |
| operations / ED Door-to-Provider (median) | default | `[{"[ED Door-to-Provider (median)]":25}]` |
| operations / ED Door-to-Provider (median) | North ED only | `[{"[ED Door-to-Provider (median)]":25}]` |
| operations / Bed Occupancy % | default | `[{"[Bed Occupancy %]":0.6822767651130596}]` |
| operations / Bed Occupancy % | North ED only | `[{"[Bed Occupancy %]":0.6821827411167513}]` |
| operations / Masked synthetic patient rows | default | `100 returned / 249575 total; window SHA-256 7d4963edb6b70fc28236dfabc62c4a4ac5d0d86e6e79288eb22e77057409c522` |
| operations / Masked synthetic patient rows | North ED only | `100 returned / 249575 total; window SHA-256 7d4963edb6b70fc28236dfabc62c4a4ac5d0d86e6e79288eb22e77057409c522` |
| operations / LWBS % | default | `[{"[LWBS %]":0.02211421860229736}]` |
| operations / LWBS % | North ED only | `[{"[LWBS %]":0.02419558625336927}]` |
| operations / Midnight Census | default | `[{"[Midnight Census]":565}]` |
| operations / Midnight Census | North ED only | `[{"[Midnight Census]":294}]` |
| operations / Facility | default | `[{"core_facility[name]":"HealthNet North"},{"core_facility[name]":"HealthNet Central"},{"core_facility[name]":"HealthNet South"},{"core_facility[name]":null}]` |
| operations / Facility | North ED only | `[{"core_facility[name]":"HealthNet North"}]` |
| operations / Resulted order turnaround | default | `[{"[Order Turnaround (minutes)]":54.91373931504355,"mart_order[order_type]":"LAB"},{"[Order Turnaround (minutes)]":34.995811218998035,"mart_order[order_type]":"PHARMACY"},{"[Order Turnaround (minutes)]":89.85135964806508,"mart_order[order_type]":"IMAGING"}]` |
| operations / Resulted order turnaround | North ED only | `[{"[Order Turnaround (minutes)]":49.84960095277702,"mart_order[order_type]":"LAB"},{"[Order Turnaround (minutes)]":31.674760868713008,"mart_order[order_type]":"PHARMACY"},{"[Order Turnaround (minutes)]":81.68544984499088,"mart_order[order_type]":"IMAGING"}]` |
| operations / Department | default | `34 returned / 34 total; window SHA-256 657bd3ef973a49c6d841e2dfea8b62844467bf7197c0af554bc64c838da60214` |
| operations / Department | North ED only | `[{"core_department[name]":"North ED"},{"core_department[name]":"Central ED"},{"core_department[name]":"South ED"}]` |

### Native Revenue owner role tests, 2026-10-30

Existing owner admin@skynwhy.com used Fabric Security -> Test as role, one role at a time; no role membership was added. Native visible Charge Rows / Gross Charges: Executive505322 /1935995659.28; HospitalManager258476 /996453130.76; DepartmentHead39458 /354517815.12; Doctor0 /Blank. All four match their independently computed slices. DepartmentHead's facility-only A/R visual is empty as intended. Productivity and Operations are not yet claimed security-verified.

A/R definition caveat: A/R Balance chooses MAX(snapshot_date) within the current context. Grouping by aging_bucket can therefore retain an older nonempty bucket, while the global latest snapshot query excludes it. The native aging visual includes61-90=$43654.18 as well as0-30=$42792831.53 and31-60=$22267915.48; the independent fixed-global-date baseline has only the latter two. This is a context-definition difference, not equal reconciliation; the model expression and both observations are retained explicitly.

### Release visual baseline after reference repair, owner date 2026-10-30

This supersedes the earlier display-definition checkpoint without deleting it. There are36 visual containers and64 contexts:58 native data queries and6 static text contexts. Productivity now includes Visits and Unique Patients cards so role checks expose an exact visible encounter count. Every query completed after the report repair; model processing reused the unchanged final refreshes. Full native rows (100-row window plus total cardinality) remain in `visual_baselines_release` locally.

| Model / visual | Context | Native value or result-window hash |
|---|---|---|
| revenue / A/R aging at latest snapshot | default | `[{"[A/R Balance]":43654.18,"mart_ar_aging[aging_bucket]":"61-90"},{"[A/R Balance]":22267915.48,"mart_ar_aging[aging_bucket]":"31-60"},{"[A/R Balance]":42792831.53,"mart_ar_aging[aging_bucket]":"0-30"}]` |
| revenue / A/R aging at latest snapshot | Commercial payers | `[{"[A/R Balance]":3312.95,"mart_ar_aging[aging_bucket]":"61-90"},{"[A/R Balance]":2358529.0,"mart_ar_aging[aging_bucket]":"31-60"},{"[A/R Balance]":4353533.01,"mart_ar_aging[aging_bucket]":"0-30"}]` |
| revenue / Gross service date vs post date | default | `13 returned / 13 total; SHA-256 d15069174bae40640c5fb931d172e8981adebb22a2eb585e9b98a48f618a2007` |
| revenue / Gross service date vs post date | Commercial payers | `13 returned / 13 total; SHA-256 9b14de3168402d1b5b859eb4d52aed66ddd40f512e70108ba5860d2a11b00ab0` |
| revenue / Original denied dollars by category | default | `8 returned / 8 total; SHA-256 56f9423e7520432a7afbb586d0e148c1cecd18fcd13ae5999cddf62fb8291f82` |
| revenue / Original denied dollars by category | Commercial payers | `8 returned / 8 total; SHA-256 435b510e6a7f54f9a92a3b35e6d98d1dc39b2e28abb8c736606d57a6a8704424` |
| revenue / Net Revenue | default | `[{"[Net Revenue]":813059634.74}]` |
| revenue / Net Revenue | Commercial payers | `[{"[Net Revenue]":186990499.73}]` |
| revenue / Denial definitions and writeoffs | default | `[{"[Denial Rate ($)]":0.05145372557138885,"[Final Denial Rate]":0.028582168874601407,"[Initial Denial Rate (count)]":0.12066662945038711,"[Writeoffs]":14068188.01}]` |
| revenue / Denial definitions and writeoffs | Commercial payers | `[{"[Denial Rate ($)]":0.05248571641372662,"[Final Denial Rate]":0.028684841222288794,"[Initial Denial Rate (count)]":0.12143401416172617,"[Writeoffs]":2778492.39}]` |
| revenue / Payer | default | `[{"core_payer[payer_group]":"Medicare"},{"core_payer[payer_group]":"Medicaid"},{"core_payer[payer_group]":"Commercial"},{"core_payer[payer_group]":"SelfPay"}]` |
| revenue / Payer | Commercial payers | `[{"core_payer[payer_group]":"Commercial"}]` |
| revenue / Charge Rows | default | `[{"[Charge Rows]":505322}]` |
| revenue / Charge Rows | Commercial payers | `[{"[Charge Rows]":113978}]` |
| revenue / Initial Denial Rate (count) | default | `[{"[Initial Denial Rate (count)]":0.12066662945038711}]` |
| revenue / Initial Denial Rate (count) | Commercial payers | `[{"[Initial Denial Rate (count)]":0.12143401416172617}]` |
| revenue / Gross Charges | default | `[{"[Gross Charges]":1935995659.28}]` |
| revenue / Gross Charges | Commercial payers | `[{"[Gross Charges]":438933821.15}]` |
| revenue / Month | default | `13 returned / 13 total; SHA-256 35fb927d5971177c8a82147c1493eb01478d731b48e0f738f8b8227802026974` |
| revenue / Month | Commercial payers | `13 returned / 13 total; SHA-256 35fb927d5971177c8a82147c1493eb01478d731b48e0f738f8b8227802026974` |
| revenue / Facility | default | `[{"core_facility[name]":"HealthNet North"},{"core_facility[name]":"HealthNet Central"},{"core_facility[name]":"HealthNet South"}]` |
| revenue / Facility | Commercial payers | `[{"core_facility[name]":"HealthNet North"},{"core_facility[name]":"HealthNet Central"},{"core_facility[name]":"HealthNet South"}]` |
| revenue / Payer mix by service-date charges | default | `[{"[Gross Charges]":720250754.27,"core_payer[payer_group]":"Medicare"},{"[Gross Charges]":623429223.41,"core_payer[payer_group]":"Medicaid"},{"[Gross Charges]":438933821.15,"core_payer[payer_group]":"Commercial"},{"[Gross Charges]":153381860.45,"core_payer[payer_group]":"SelfPay"}]` |
| revenue / Payer mix by service-date charges | Commercial payers | `[{"[Gross Charges]":438933821.15,"core_payer[payer_group]":"Commercial"}]` |
| revenue / Collections | default | `[{"[Collections]":747998887.73}]` |
| revenue / Collections | Commercial payers | `[{"[Collections]":163878752.95}]` |
| revenue /  | default | `Static text` |
| revenue /  | Commercial payers | `Static text` |
| productivity / Month | default | `13 returned / 13 total; SHA-256 35fb927d5971177c8a82147c1493eb01478d731b48e0f738f8b8227802026974` |
| productivity /  | default | `Static text` |
| productivity / Department | default | `33 returned / 33 total; SHA-256 f34aef1153c26b36a99316d8f95f653bb40c9713853716dafa7744d1bc07930b` |
| productivity / Unique Patients | default | `[{"[Unique Patients]":57764}]` |
| productivity / Department and doctor leaderboard | default | `100 returned / 435 total; SHA-256 b35b095aee67bfa8700c8d8fad0ec9c4318a1ffdcc64ca8b6c9248b850e0f313` |
| productivity / Visits | default | `[{"[Visits]":249575}]` |
| productivity /  | default | `Static text` |
| productivity / Doctor encounters | default | `100 returned / 249575 total; SHA-256 7d10df676ba5dc69989c1c49435b3047184303717a0c3cbb89a97d96617a7afe` |
| operations / Admissions, discharges and readmissions | default | `[{"[30-day Readmission %]":0.1179753738656214,"[Admissions]":46942,"[Discharges]":248855,"[Visits]":249575}]` |
| operations / Admissions, discharges and readmissions | North ED only | `[{"[30-day Readmission %]":null,"[Admissions]":null,"[Discharges]":47413,"[Visits]":47441}]` |
| operations / ED arrivals by local hour | default | `24 returned / 24 total; SHA-256 3786eb6f6c45d01cd85cbb1b8adcd2824c876e8afb0d21770fa7cea2987445c5` |
| operations / ED arrivals by local hour | North ED only | `24 returned / 24 total; SHA-256 6f74588f0a2fb901074170695f5cda937db7e293fdb12c10d3bbaf250451afa6` |
| operations / Order lines by type and status | default | `15 returned / 15 total; SHA-256 ee70494651dc1905b1a62314de1899029fb3043ca55f84535f22c50fd1318d95` |
| operations / Order lines by type and status | North ED only | `15 returned / 15 total; SHA-256 caf91866b315227305f327379b418412a8ba6a8968a88f9c54ef720b140b9a02` |
| operations / ALOS by service line | default | `7 returned / 7 total; SHA-256 44c13f1930783b63e6f625a8978fa6bd4ffeba6641cc13b660bb3b196719139e` |
| operations / ALOS by service line | North ED only | `[]` |
| operations /  | default | `Static text` |
| operations /  | North ED only | `Static text` |
| operations / Month | default | `14 returned / 14 total; SHA-256 721558f3193f4e0b84de495eb31d372dd8c52248d67a8ae00026e0d011bb3ba3` |
| operations / Month | North ED only | `14 returned / 14 total; SHA-256 721558f3193f4e0b84de495eb31d372dd8c52248d67a8ae00026e0d011bb3ba3` |
| operations / ED Door-to-Provider (median) | default | `[{"[ED Door-to-Provider (median)]":25}]` |
| operations / ED Door-to-Provider (median) | North ED only | `[{"[ED Door-to-Provider (median)]":25}]` |
| operations / Bed Occupancy % | default | `[{"[Bed Occupancy %]":0.6822767651130596}]` |
| operations / Bed Occupancy % | North ED only | `[{"[Bed Occupancy %]":0.6821827411167513}]` |
| operations / Masked synthetic patient rows | default | `100 returned / 249575 total; SHA-256 7d4963edb6b70fc28236dfabc62c4a4ac5d0d86e6e79288eb22e77057409c522` |
| operations / Masked synthetic patient rows | North ED only | `100 returned / 249575 total; SHA-256 7d4963edb6b70fc28236dfabc62c4a4ac5d0d86e6e79288eb22e77057409c522` |
| operations / LWBS % | default | `[{"[LWBS %]":0.02211421860229736}]` |
| operations / LWBS % | North ED only | `[{"[LWBS %]":0.02419558625336927}]` |
| operations / Midnight Census | default | `[{"[Midnight Census]":565}]` |
| operations / Midnight Census | North ED only | `[{"[Midnight Census]":294}]` |
| operations / Facility | default | `[{"core_facility[name]":"HealthNet North"},{"core_facility[name]":"HealthNet Central"},{"core_facility[name]":"HealthNet South"},{"core_facility[name]":null}]` |
| operations / Facility | North ED only | `[{"core_facility[name]":"HealthNet North"}]` |
| operations / Resulted order turnaround | default | `[{"[Order Turnaround (minutes)]":54.91373931504355,"mart_order[order_type]":"LAB"},{"[Order Turnaround (minutes)]":34.995811218998035,"mart_order[order_type]":"PHARMACY"},{"[Order Turnaround (minutes)]":89.85135964806508,"mart_order[order_type]":"IMAGING"}]` |
| operations / Resulted order turnaround | North ED only | `[{"[Order Turnaround (minutes)]":49.84960095277702,"mart_order[order_type]":"LAB"},{"[Order Turnaround (minutes)]":31.674760868713008,"mart_order[order_type]":"PHARMACY"},{"[Order Turnaround (minutes)]":81.68544984499088,"mart_order[order_type]":"IMAGING"}]` |
| operations / Department | default | `34 returned / 34 total; SHA-256 657bd3ef973a49c6d841e2dfea8b62844467bf7197c0af554bc64c838da60214` |
| operations / Department | North ED only | `[{"core_department[name]":"North ED"},{"core_department[name]":"Central ED"},{"core_department[name]":"South ED"}]` |

### Native Productivity owner role tests and drill-through, 2026-10-30

| Single simulated role | Visible encounter rows / Visits | Unique Patients |
|---|---:|---:|
| Executive |249575|57764|
| HospitalManager |127666|51022|
| DepartmentHead |19475|16114|
| Doctor |3031|2956|

All4encounter counts match independent expected slices. These are native owner Test as role observations, not unrestricted DAX queries with added WHERE filters. Local UI observation record:productivity-role-ui-observations.json. No native role members were added. The named-doctor drill-through carries provider10/NorthMedicine/SynthDoctor010 and1335visits into masked encounter detail, matching the originating row. Operations role tests still pending at this checkpoint.

### Masked patient-name detail completion, 2026-10-30

The Doctor encounters visual now includes existing mart masked_given_name and masked_family_name alongside masked_mrn. Native model baseline re-read:100returned / 249575total; SHA-256 of the exact returned rows including cardinality=e5f96b9b2094c0aa02952ef0860b3aacdbe69f0a526bb7b5b06894bb4915f71e. This supersedes only the earlier detail-window hash; no source/model data or security changed. Receipt:masked-detail-baseline.json.
