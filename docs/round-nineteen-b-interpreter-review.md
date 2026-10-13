# Round Nineteen B: interpreter proposal review

Reviewed offline on 2026-10-13. The live batch completed four model attempts and
returned 26 **contract-valid proposals**, not 26 established dependencies. No
estate read, model call or graph mutation was made for this review.

The retained task-file SHA-256 is
`a168f436065f5f31f363e73b42bc59b8fb412ba533cf8ee742a333e53e82868a`.
The original result SHA-256 is
`1361336e80ca0905514c6a6c9140b30e7d096a3d532462bb360c56e9f83435df`.
The full private per-edge review is
`.local/round-nineteen-b/interpreter-01-offline-audit.json`; the original result
and all four captures remain unchanged.

## Exactness and evidential support are separate checks

All 26 edges pass the closed graph record schema. Their quoted bytes equal the
specified lines and Unicode offsets in the hash-pinned input source. Their
endpoints exist in both the supplied slice and the retained v3 graph. Every
edge remains `INFERRED`, `NOT_VERIFIED`, `execution_established: false`, and
`deployment_binding: NOT_ESTABLISHED`.

That validation guarantees quote integrity. It does **not** establish that the
quoted lines contain every declaration needed to resolve an endpoint.

| Task | Recipe | Proposals | Self-contained mapping spans | Missing citation support |
|---|---|---:|---:|---|
| 0 | Silver invoices, first owner | 6 | 1 | Five column edges cite SELECT on line 8 without INSERT destination/column order on line 7. |
| 1 | Gold invoice activity, first owner | 7 | 0 | Six column edges cite INSERT/SELECT on lines 5–6 without the FROM alias binding on line 7; `h.plan_id` also requires line 8. The join edge cites line 8 without the declaration of alias `i` on line 7. |
| 2 | Silver invoices, second owner | 6 | 6 | The selected lines 7–8 contain both INSERT target and ordered SELECT source. |
| 3 | Gold invoice activity, second owner | 7 | 0 | Same omitted alias declarations as task 1. |
| Total | | 26 | 7 | 19 insufficient standalone citations. |

The full retained code supports the proposed invoice mappings, but nineteen
original citations omit necessary context. This review does not expand their
spans, rewrite their quotations, or silently accept their explanations as
evidence. No proposal was published while that review remains unresolved.

Seven proposals could be considered as undeployed authoring-recipe inferences,
subject to a current graph endpoint check. They cannot establish a deployed
procedure, a verified boundary, complete lineage, or semantic correctness.
The remaining nineteen need a separately recorded correction of the source
citation before publication. A future generic validator needs to resolve the
cited statement's target-column order and aliases through an installed parser;
string/name matching alone would not establish that relationship. The current
language-neutral exact-span validator does not implement that semantic check.

## MRR remains separate

These sources describe `silver.invoices` and `gold.invoice_activity`, including
the join to `bronze.account_plan_history`. They do not describe the native MRR
path through Subscriptions and Plans. None of the 26 proposals is eligible for
attachment as an MRR procedure hop. No inference removes that existing gap.
