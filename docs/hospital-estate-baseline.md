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
