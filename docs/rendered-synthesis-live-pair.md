# Rendered synthesis: two live repeats

2026-09-27. PR #283 implementation `9d34109`; engine fingerprint
`f0676adcc3f59f3cfd5bde150ceb6d0a4d39f7ff66f77632db734ecd5de09767`.
#282 merged after six green checks. No engine/config/profile/policy/ticket change
between runs; no guard, permission, estate or cap change. Both runs are
KNOWN_DOMAIN_REGRESSION, not frozen unfamiliar-domain acceptance.

**Both runs completed through validated synthesis as TRANSFORMATION_LOGIC.**
The engine renders the discovered measure name and the complete observed path
before model mechanism prose. Mandatory claim, surface and snapshot limits follow.
There is no reference-only substitute and no silent cut.

| Run | Session | Diagnostics / cap | Physical / credits | Guards | Reuses | Synthesis |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | `c7019601-6f18-4a44-8cb8-1dcd36dc67ac` | 4 / 4 | 10 / 10 | 6 | 0 | COMPLETED, validated |
| R2 | `56a00578-875c-4c42-850e-040b0ab566ff` | 4 / 4 | 10 / 10 | 6 | 0 | COMPLETED, validated |

Each run made one intake call, one investigation definition-judge call and one
synthesis call. No retry or cap hold occurred. The four diagnostics were one
Power BI quantity, two Fabric SQL quantities and one endpoint metadata lookup.
SQL physical requests include two quantities plus six guards (identity, database
permissions and object permissions on each of two different databases). All ten
requests completed. Reuse saved zero against the ten-request estimate; no guard
could be reused across these different database/object scopes.

Both compared presentation/Gold at 8,765 = 8,765, then Gold/Silver at 8,765 versus
7,661. The latter renders Silver as upstream input and Gold as downstream output.
Both comparison receipts say CROSS_SURFACE_VERIFIED and SNAPSHOT_UNVERIFIED:
execution surfaces were distinct and attested, but served versions were not.
Agreement does not prove currency; timing was not excluded from the divergence.
Actual duplicate matches, intended grain, business intent and source correctness
remain unproved. Silver/Bronze was unchecked after termination; the application
binding is unresolved. This validates this known path twice, not generality.

## Approved credits

The user explicitly approved this new pair: ten expiring physical credits per run,
twenty total, with two-hour expiry. All twenty were charged, zero remain. Each
grant was scoped to its session and recorded before investigation with before/
granted/after readbacks. No credits were refunded, moved or enlarged.

| Batch | Granted / charged | Expires UTC |
| --- | --- | --- |
| `G-rendered-synthesis-R1-20260927-credits` | 10 / 10 | 2026-09-27T23:26:59.879465+00:00 |
| `G-rendered-synthesis-R2-20260927-credits` | 10 / 10 | 2026-09-27T23:29:26.443214+00:00 |

Ordinary limit stayed 60. Rolling ordinary charged readbacks were 92 -> 92
for R1 and 92 -> 92 for R2; all new reads used batch credits. Historical
UTC-day totals moved 109 -> 119 -> 129. These are counters, not changed ceilings.
Policy/config/profile/ticket hashes match before and after.

## Validation and preservation

1,307 local regression tests passed on this engine (SQLite ResourceWarnings, no
failures). Earlier focused failures were assertions tied to the removed fixed
technical/limitation templates; the revised contract tests and full suite passed.
No test relaxes output completion, provenance or snapshot limitations. See the
[contract and enum audit](rendered-synthesis-contract.md) for all producer fields,
guard findings, comparison to 3d2c5bf0 and the context cost/coverage audit.

One ledger row was appended per run. The earlier #282 failures and tapes are
unchanged. Original live results, approvals and recordings are retained under
`.local/rendered-synthesis-20260927/` and the referenced planner recordings.
[Public accounting and output hashes](runs/rendered-synthesis-live-pair.json) omit
query/result/provider prose. The four linked text artifacts below preserve each
full rendered explanation exactly, including every appended limit and action.

## R1 outputs, verbatim

### Business

[Exact UTF-8 text](runs/rendered-synthesis-R1-business.txt)

```text
The report showed 8,765 for movements, matching the total used to prepare it. An earlier check of movements returned 7,661; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not. Comparison 1 lacks a verified data version for the check nearer the report and the check further back. Agreement does not establish that either value is up to date. Comparison 2 lacks a verified data version for the check nearer the report and the check further back. Different update timing was not excluded as a cause of this difference.
```

### Technical

[Exact UTF-8 text](runs/rendered-synthesis-R1-technical.txt)

```text
Measure: Handled Quantity.
Boundary B1 agrees: L1 (fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values, upstream input) -> L0 (fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity, downstream output). Observed input 8,765; observed output 8,765. Values agree.
Boundary B2 diverges: L2 (fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1, upstream input) -> L1 (fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values, downstream output). Observed input 7,661; observed output 8,765. Values differ.
L0 = fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 = fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 = fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1

The implemented logic carries the movement quantity through a left join from movements to rates by product key, then derives value from quantity and cost. If more than one rate row matches a movement row, the same quantity is repeated across matches and the aggregate can rise at that step. The definition shows a possible mechanism, but it does not confirm repeated matches in the data, shared timing across checks, or business intent.

Claim limits:
Checked through fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1; stopped because reached.
Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity: the surface did not report it.
Unattested surface field engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity: the surface did not report it.
Unattested surface field object on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity: the surface did not report it.
Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values: the surface did not report it.
Unattested surface field engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values: the surface did not report it.
Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1: the surface did not report it.
Unattested surface field engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1: the surface did not report it.
Comparison 1: SNAPSHOT_UNVERIFIED; the upper and lower served data version is not attested to its quantity read; agreement does not establish that either value is current.
Comparison 2: SNAPSHOT_UNVERIFIED; the upper and lower served data version is not attested to its quantity read; different update timing was not excluded as a cause of the difference.
Unchecked fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 -> fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1: Investigation terminated before this boundary.
Unchecked fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
The definition shows a mechanism that can produce the higher total, but it does not show the actual match cardinalities or establish that duplicate join matches are present in this specific data.

Surface attestation limits:
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 7b43399f-505a-468b-b830-6f9110cf010b).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 7b43399f-505a-468b-b830-6f9110cf010b).
- Unattested object on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 7b43399f-505a-468b-b830-6f9110cf010b).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt 9ec03ffd-ab10-4522-bd8c-ca1d109cbb01).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt 9ec03ffd-ab10-4522-bd8c-ca1d109cbb01).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt 1a693090-31bf-4470-b467-218167841df9).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt 1a693090-31bf-4470-b467-218167841df9).

Comparison 1 lacks a verified data version for the check nearer the report and the check further back. Agreement does not establish that either value is up to date. Comparison 2 lacks a verified data version for the check nearer the report and the check further back. Different update timing was not excluded as a cause of this difference.

Snapshot attestation:
[{"lower": null, "reason": "QUERY_BOUND_VERSION_MISSING", "status": "SNAPSHOT_UNVERIFIED", "unverified_sides": ["upper", "lower"], "upper": null, "version": 1}, {"lower": null, "reason": "QUERY_BOUND_VERSION_MISSING", "status": "SNAPSHOT_UNVERIFIED", "unverified_sides": ["upper", "lower"], "upper": null, "version": 1}]

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

## R2 outputs, verbatim

### Business

[Exact UTF-8 text](runs/rendered-synthesis-R2-business.txt)

```text
The report showed 8,765 for movements, matching the total used to prepare it. An earlier check of movements returned 7,661; the difference appears in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not. Comparison 1 lacks a verified data version for the check nearer the report and the check further back. Agreement does not establish that either value is up to date. Comparison 2 lacks a verified data version for the check nearer the report and the check further back. Different update timing was not excluded as a cause of this difference.
```

### Technical

[Exact UTF-8 text](runs/rendered-synthesis-R2-technical.txt)

```text
Measure: Handled Quantity.
Boundary B1 agrees: L1 (fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values, upstream input) -> L0 (fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity, downstream output). Observed input 8,765; observed output 8,765. Values agree.
Boundary B2 diverges: L2 (fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1, upstream input) -> L1 (fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values, downstream output). Observed input 7,661; observed output 8,765. Values differ.
L0 = fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 = fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 = fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1

The measured quantity agrees between the report layer and the prepared total, while a lower movement table is smaller. The definition shows a left join from movements to rates by product_id before the value is calculated, and it states that matching rows may multiply because uniqueness is not assumed. When more than one rate matches a movement, the movement units can be carried into more than one joined row, which can raise the summed quantity without changing the carried units rule. This explains the observed gap as join multiplicity, but it does not confirm repeated matches in the data, a shared snapshot, or any business intent.

Claim limits:
Checked through fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1; stopped because reached.
Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity: the surface did not report it.
Unattested surface field engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity: the surface did not report it.
Unattested surface field object on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity: the surface did not report it.
Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values: the surface did not report it.
Unattested surface field engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values: the surface did not report it.
Unattested surface field connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1: the surface did not report it.
Unattested surface field engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1: the surface did not report it.
Comparison 1: SNAPSHOT_UNVERIFIED; the upper and lower served data version is not attested to its quantity read; agreement does not establish that either value is current.
Comparison 2: SNAPSHOT_UNVERIFIED; the upper and lower served data version is not attested to its quantity read; different update timing was not excluded as a cause of the difference.
Unchecked fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 -> fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1: Investigation terminated before this boundary.
Unchecked fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.
This explains the difference only through join multiplicity on product_id. The definition does not establish that duplicate matches actually exist in the data, nor that both sides use the same snapshot.

Surface attestation limits:
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 23c90f2a-bee8-428e-9f8c-8e7bc10a4480).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 23c90f2a-bee8-428e-9f8c-8e7bc10a4480).
- Unattested object on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity (receipt 23c90f2a-bee8-428e-9f8c-8e7bc10a4480).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt 5f84dca3-332a-47c1-b1a6-e5a8c3bb14f7).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values (receipt 5f84dca3-332a-47c1-b1a6-e5a8c3bb14f7).
- Unattested connection on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt 11922126-9582-431a-a8bd-868992cf2973).
- Unattested engine on fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1 (receipt 11922126-9582-431a-a8bd-868992cf2973).

Comparison 1 lacks a verified data version for the check nearer the report and the check further back. Agreement does not establish that either value is up to date. Comparison 2 lacks a verified data version for the check nearer the report and the check further back. Different update timing was not excluded as a cause of this difference.

Snapshot attestation:
[{"lower": null, "reason": "QUERY_BOUND_VERSION_MISSING", "status": "SNAPSHOT_UNVERIFIED", "unverified_sides": ["upper", "lower"], "upper": null, "version": 1}, {"lower": null, "reason": "QUERY_BOUND_VERSION_MISSING", "status": "SNAPSHOT_UNVERIFIED", "unverified_sides": ["upper", "lower"], "upper": null, "version": 1}]

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```
