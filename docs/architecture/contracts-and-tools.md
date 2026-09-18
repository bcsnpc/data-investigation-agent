# Context, tool and evidence contracts

Target contracts follow [review sections D-F](enterprise-discovery-pivot.md).
Existing tools remain reusable; generated-query execution is planned, not implied
by this document. See [status](../current-delivery-status.md).

| Boundary | Required contract |
| --- | --- |
| Connection | Approved roots, identity reference, policy/version, cadence/budgets; no secrets |
| Scan | Coverage/gaps per surface, times, completion, raw inventory references and calls |
| Graph | Scoped asset IDs, immutable versions, evidence-backed edges, provenance, change closure |
| Context pack | Relevant definitions/relationships/reports/transforms, inferred/confirmed context, omissions |
| State | Question/targets/context, observations/hypotheses, attempted tests, gaps, impact and stop |
| Tool request | Registry tool, scoped connection/assets, validated query/plan, purpose and limits |
| Receipt | Actual target/identity/query, timestamps, typed result/failure, completeness, budget/replay key |
| Outcome | Qualified claims, classification, alternatives/context gaps, impact and observation references |

SQL proposals must parse as one SELECT/CTE query in the target dialect. Resolve
aliases/CTEs/joins to approved tables/views; reject DDL/DML/EXEC/SELECT INTO, multiple
statements, external access and unknown functions. Cap joins/rows/bytes/time/calls.
DAX proposals are bounded read-only queries against approved models with validated
structure/references. Unknown grammar fails closed. Native Power BI executes DAX;
no second DAX engine. TOP alone does not bound database work.

Keep a small registry: context discovery/retrieval; native measures/dependencies/
dimensions; bounded SQL/DAX; profiles, duplicates, nulls, keys and time windows;
transform/run/watermark/application inspection; lineage and ownership. Prefer
existing builders but do not require a Python template per question.

Preserve decimal/BLANK/null types, date boundaries and units. Identity, scope and
completeness control comparability; samples cannot prove complete missing-key counts.
Native success does not prove source semantic equivalence. Graph reachability is
potential impact, not measured impact. Planner text cannot fabricate receipts,
change permissions or execute captured notebook code. Reviewed external drafts
remain separate from investigation execution.
