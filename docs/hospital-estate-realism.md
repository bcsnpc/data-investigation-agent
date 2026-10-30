# HealthNet realism and licensing

All rows, people, staff, identifiers, facilities, addresses and payer names are synthetic. Seed 20261030 fixes the source population. Benchmarks guide distributions; they are not copied patient records. The generation period is 2025-10-01 through 2026-10-29 (394 days), allowing a partial October-to-October comparison. It does not establish two complete calendar years.

| Distribution | Generator target / range | Basis |
|---|---|---|
| Completed inpatient length of stay | service means Medicine 6.3, Cardiology 5.0, Orthopedics 3.6, Surgery 4.7, Obstetrics 2.4, Pediatrics 2.8, ICU 8.0 days; gamma shape 2, 0.5?45 days | Assumptions; context: Medicare FFS mean 5.6 days in 2022 ([MedPAC](https://www.medpac.gov/wp-content/uploads/2024/07/July2024_MedPAC_DataBook_SEC-1.pdf)); not an all-payer population estimate |
| Occupancy | 880 beds (450/280/150); no overlapping assignments; report measured occupancy rather than force a target | Fictional capacity assumption; [AHA hospital context](https://www.aha.org/statistics/fast-facts-us-hospitals) |
| Season / weekday | winter arrival weight 1.14; weekend 0.92 | Explicit assumptions |
| ED arrival hour | overnight 0.35; morning 0.8; daytime/evening 1.35; late evening 0.7 | Explicit assumptions, weighted per hour |
| ED door to provider | lognormal median 25 minutes, sigma 0.8; missing for LWBS | Assumption; CDC reports 40.6% seen within 15 minutes, so this synthetic wait profile is intentionally slower ([CDC](https://www.cdc.gov/nchs/fastats/emergency-department.htm)) |
| ED length of stay | nonadmitted lognormal median 180 minutes, sigma 0.55, 25?1500 min; admitted includes actual bed wait | Assumption; ED boarding is not forced into the nonadmitted distribution |
| LWBS | 2.5% of nonadmitted ED arrivals, not all arrivals | Assumption; actual denominator reported |
| ED admissions | 11.5% | CDC 2022 all-ED context, same public source above |
| Readmissions | 12% attempt among new IP admissions; only actual preceding same-service discharges qualify within 30 days | Assumption; actual eligible rate can be lower; not a CMS risk-adjusted metric |
| Transfers | 2.4% attempted ED interfacility, requiring a real preceding different-facility discharge within one day | CDC transfer context; actual linked transfer rate may be lower |
| Orders / encounter | 6 at full size, LAB75% / imaging12% / pharmacy13% | Assumptions |
| Turnaround | median LAB55, imaging90, pharmacy35 minutes; lognormal sigma0.5; STAT half routine | Assumptions, completed only |
| Cancel / void / unfinished | 4% cancel, 1.5% void, 2% in-progress/ordered, plus explicit reentries | Assumptions |
| STAT | 40% for ED; 12% other encounters | Assumptions |
| Charges | lognormal IP median $28,000; other encounters $1,800; two component charges, occasional zero/bundle | Fictional gross charges, not payment or cost benchmarks |
| Payer mix | Medicare37%, Medicaid24%, commercial31%, self-pay8%, before reference remapping | Assumptions; remapped plans alter historical/current-reference groupings |
| Initial denial | 12% assigned; report adjudicated claims only, unresolved final subset | Assumption near 11.81% cited in [HFMA chapter February2026](https://www.hfma.org/wp-content/uploads/2026/02/february2026-speaksnewsletter-firstillinois.pdf); not an HFMA national causal standard |
| Denial categories | seven synthetic categories, approximately balanced by account index | Assumption; no X12 CARC copied |
| Days to bill / pay | generated service-to-bill delay; payment 14?39 days after bill; late charges4?34 days; disclose right censoring | Assumptions; compare measured outputs, not asserted benchmarks |
| A/R | exact posted charges + signed adjustments ? signed payments, daily aging by facility/payer | Definition choice aligned with [HFMA MAP definitions](https://www.hfma.org/data-and-insights/map-initiative/map-keys/); no target fabricated |
| Adjustments / writeoff | total58% gross: usually contractual; qualifying older accounts split10% gross to bad debt at90days; small charity offsets refunds | Assumptions; not cost accounting |
| Late charges | 5% selected, capped at source as-of date | Assumption; distinguish late and cross-month counts |
| Providers | 300 physicians +60 APC; 25% at0.5FTE; specialty-linked attendance; 36 transfers April16 | Assumptions; actual daily visits and workload reported, not national productivity norms |
| Procedure workload | uniform2?12 fictional workload units; never described as licensed RVU | Assumption |

## Code sets

- ICD-10-CM: four diagnosis identifiers (I10, E11.9, J18.9, R10.9), with our own generic descriptions. ICD-10-PCS: 0WQF0ZZ, documented in the [CMS public v38 code reference](https://www.cms.gov/icd10m/version38-fullcode-cms/fullcode_cms/P0764.html). This is a pinned demonstration subset, not a claim of current-year coding compliance. [ONC identifies ICD-10-CM/PCS as publicly available without a license](https://healthit.gov/resources/cartos-oncs-terminology-service/); [CMS code hub](https://www.cms.gov/medicare/coding-billing/icd-10-codes).
- CPT is licensed by AMA ([license FAQ](https://www.ama-assn.org/practice-management/cpt/cpt-licensing-frequently-asked-questions-faqs)); use PRC synthetic identifiers only. No CPT descriptors.
- NUBC is licensed ([NUBC licensing](https://www.nubc.org/license)); use synthetic revenue centre identifiers only.
- CARC/RARC: use DN-SYN and SYN-RMK identifiers/categories only; no redistribution of [X12 code lists](https://x12.org/codes).
- Drug identifiers SYN-DRUG, DRGs SYN-DRG and workload weights are synthetic. No HCPCS/CDT, real MS-DRG weights or RxNorm release imported. [RxNorm terms](https://www.nlm.nih.gov/research/umls/rxnorm/docs/termsofservice.html) distinguish public NLM normalized content from proprietary source vocabularies; avoid that ambiguity entirely here.

Actual distributions and checks are emitted in verification.json for each generated volume. A tiny test sample proves invariants, not population-rate conformance. Native source/raw/model/report reconciliation remains a separate requirement.
