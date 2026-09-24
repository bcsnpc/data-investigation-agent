# G trajectory audit before the next experiment

2026-09-24. Offline review of the three #220 recordings; no new provider or data
calls. These are known-domain regressions, not acceptance evidence. This report
was written before changing ownership representation or limits.

## Finding

The difference is principally **test selection/order interacting with the read
ceiling**. It is not an absence of hypothesis revision. G2 and G3 both revised and
rejected hypotheses using observations. Their sixth reads ended execution before
another planner call could interpret the result or supply an assessment:
`AdaptiveRuntime.step` checks `cloud_calls >= limits.cloud_calls` before planning.
G1 chose a qualified STOP after five reads. Consequently these recordings cannot
establish a final-synthesis failure: G2/G3's final synthesis opportunity was
censored. G3's last read actually supplied new cross-system evidence.

G1 tested global cardinality early and left room to stop; G2 spent more reads on
overlapping details; G3 pursued a useful semantic-model membership check last.
G1 also had overlapping reads, so it was not uniformly more efficient. Selection
variance is visible, but three trajectories do not identify a general causal
effect or prove that G1's ordering will recur. No stopping-contract change follows
from this audit.

## Ordered actions side by side

D = discriminating against an explicit alternative; C = primarily confirmatory;
M = mixed. These are retrospective evaluator judgments, not execution gates or
semantic-containment rules. All SQL targets below are the existing isolated
`app.stock_movements_e1b8e1` and `app.inventory_adjustments_e1b8e1`.

| Call | G1 | G2 | G3 |
| --- | --- | --- | --- |
| 1 | Retrieve adjustment schema | Retrieve notebook metadata | Retrieve notebook metadata |
| 2 | Search stock movements | Search stock movements | Search stock movements |
| 3 | Retrieve stock schema | Find stock reference in notebook | Find adjustment reference in notebook |
| 4 | SQL D: global linked/unlinked groups, mismatch and multi-link counts | Find adjustment reference in notebook | Find stock reference in notebook |
| 5 | SQL M: individual mismatches and multi-link details | SQL D: sample stock/adjustment cardinality and units; schema prefetch | SQL D: linked types/reasons, exact matches and dates |
| 6 | Retrieve notebook metadata | SQL rejected: 16 SELECTs against cap 8; no read | SQL C: individual mismatch details |
| 7 | SQL D: stock duplicates versus adjustment-side fanout | SQL D: global uniqueness, null/zero and join cardinality | SQL D: deduplicated linked share versus all stock units |
| 8 | SQL C: independently aggregate both sides, recheck multiplicity | SQL C: repeat anomaly details | Retrieve notebook code excerpt |
| 9 | SQL C: sharpen global stock-duplicate negative check already covered by prior OR predicates | SQL D: orphan adjustment IDs | SQL D: distinguish one-to-one mismatches from cardinality artifacts |
| 10 | STOP: BUSINESS_CONTEXT_REQUIRED | SQL M: type/reason distribution, signed/null/zero quantities | SQL D: test reconciliation after per-movement aggregation |
| 11 | — | SQL C: linked row details with counts and reason codes; sixth read | Native D: selected source movement IDs in semantic Activity; sixth read |
| 12 | — | Not admitted: read ceiling | Not admitted: read ceiling |

## Hypothesis changes at each call

IDs are scoped to each run. Updates occur before the action on that row and can
only cite earlier observations. Unlisted hypotheses persist unchanged. The
companion structured audit retains every full claim, status and evidence ID.

| Call | G1 updates | G2 updates | G3 updates |
| --- | --- | --- | --- |
| 1 | Open h1 adjustment-linked entries, h2 unidentified stock source | Open h1 unintended notebook materialization, h2 unidentified stock source | Open h1 source discovery, h2 remapped adjustments, h3 unknown intent |
| 2 | None | Refine h2 from notebook metadata | Refine h1/h3 from notebook metadata |
| 3 | Refine h2: exact source identified | Refine h2: source found, implementation untested | Refine h2: union/remap hypothesis, still untested |
| 4 | Open h3 linked mismatch/multiplicity, h4 unrelated stock dominance | Open h3: direct consumption versus mere reference | None |
| 5 | Refine h3/h4 from global counts: real evidence update | Open h4 one-to-many links, h5 zero/null semantics | Open h4 eligible stock types, h5 unit alignment |
| 6 | None | Open h6 fanout, h7 global null/zero; proposed test rejected | Open h6 specific mismatches; mainly detail refinement |
| 7 | Open h5 stock versus adjustment duplicates | Refine h4 from sample: movement 167 has two adjustments | Open h7 linked contribution, h8 negligible contribution alternative |
| 8 | Refine h5: observed adjustment-side multiplicity | Refine h3 metadata limit, h5/h7 null/zero, h6 measured 361 versus 360 join rows | Open h9: inspect actual union/remap code |
| 9 | Open h6 stock duplicates; h5 largely restated | Open h8 orphan alternative | Refine h6 cardinality alternative, h9 no union visible in inspected excerpt |
| 10 | Refine h1/h3/h5; reject h6 using global empty result | Open h9 heterogeneous adjustments; reject h8 using empty orphan result | Open h10 stock magnitude, h11 reconciliation after aggregation |
| 11 | — | Refine h4 global multiplicity, h9 heterogeneous signs/reasons | Refine h4/h5/h10; reject h6 cardinality explanation and h11 reconciliation; reject h8 negligible-share claim; open h12 Activity membership |

G3's h8 rejection establishes an arithmetic share, not an authoritative business
materiality threshold. Its h6 rejection narrows the explanation for mismatches;
it does not prove that mismatches are defects. The h11 comparison cannot establish
that stock quantities and adjustment quantities are intended to be equal.

## Evidence at exhaustion and the next useful distinction

**G1:** 29 linked movement IDs, 30 adjustment rows, no orphan IDs, one multi-link,
331 unlinked stock rows, and no stock duplicates in the global negative check.
It explicitly stopped with unknown adjustment intent and incomplete downstream
lineage. It did not demonstrate that adjustment records prove incorrect stock.

**G2:** 360 distinct stock IDs, 30 adjustments over 29 IDs, one multi-link, 361
rows in the tested left join, one zero adjustment, no null adjustment units and
no orphans. Type/reason and row details do not settle whether adjustments are
consumed by Activity or whether any entry violates an intended rule. The best
remaining discriminating check is actual Activity construction/consumption and
a matched source-to-native cohort, rather than another adjustment marginal.
Authoritative intent is still required to call source entries incorrect.

**G3:** 28 one-to-one linked IDs still have no exact unit match; one ID has
multiple adjustments. Linked source units are 495/5,783 RECEIPT and 141/1,878
ISSUE. Aggregating adjustments does not reconcile these quantities. The inspected
notebook region loads stock and writes adjustments separately; absence of a union
in that excerpt is not proof about every downstream path. Its final native result
shows all 12 selected source IDs in Activity, one row each. This final evidence
never reached a subsequent planner turn. The next distinction is the actual
adjustment-to-Activity contract and matched contribution, not another mismatch
aggregate. The reason-group query uses MIN(reason_code) for multi-reason IDs;
those groups must not be treated as authoritative business categories.

## Reproducibility

| Run | Session | SQL/native | Calls | Local rejects | Stop |
| --- | --- | --- | ---: | ---: | --- |
| G1 | c3e4959a-35ed-4785-9b6f-c5d9643a3e61 | 5/0 | 10 | 0 | ENOUGH_DIAGNOSTICS |
| G2 | d789ea5d-0249-4829-b146-d2a7ba7d403b | 6/0 | 11 | 1 | BUDGET_LIMIT |
| G3 | ccd13ccb-ca0f-4e0f-819b-54f0813ce7c3 | 5/1 | 11 | 0 | BUDGET_LIMIT |

Recordings are under `.local/planner-recordings`; original run results are under
`.local/unknown-domain-v4/runs/G-ownership-revert-20260923-{3,5,6}.json`.
The structured offline audit is `.local/g-arms/trajectory-audit.json`, containing
ordered decisions, accumulated structured hypotheses and receipt references.
No private reasoning content is requested or reconstructed.
