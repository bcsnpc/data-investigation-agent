# Round 23 — make the engine work

Started 2026-10-26 from main af73a1b7e09813e9dd95792bf0852b134fda8ce7.
Round 22 is closed: PR #429 merged, validated merge 567a95b tagged v0.22,
final summary pushed. Its final dev 14/40 and held-out 5/20 (zero harmful)
remain unchanged. No Round 22 held-out wording is used for development.

The owner's later 2026-10-26 steer supersedes the November1 wait: live work is now authorized. Independent v2 dev pass 1 has restarted on the corrected single image; earlier partial startup attempts are preserved separately, not reported as a completed pass. Draft PR #430 is open.

## Part 0 ? start and budgets

Owner-approved 2026-10-26: investigator USD150/month (80% warning), USD1/ticket (USD0.50 warning); enrichment USD25 and Azure <=USD20 unchanged. Monthly requests are now 9,000: scan/collectors2,000, investigation6,905, restoration95 (restores only), effective October and every subsequent month.

The existing owner path applied and read back the authoritative PostgreSQL policy and both already-provisioned October/November model ceilings. No grants, credentials or resources changed; counters, reservations and violation flags were preserved. Source/config consume the new policy; older scheduled images retain their earlier source ceiling until deployment. [Exact before/after receipt](runs/round-twenty-three-budget-increase.json).

At 2026-10-27T01:31UTC, requests5,471/9,000: investigation3,607, scan1,794, restoration70. The later owner decision grants a fresh95 restoration allowance; the70cleanup requests remain in the gross total and original rows. [Reset receipt](runs/round-twenty-three-restoration-reset.json). October modelUSD10.202640/150; NovemberUSD0/150. These are observations, not future reservations.

## Part A — simplify

PG connections renew tokens before expiry, use short-lived operations, keepalives and bounded timeouts; dropped connections and lost keyed settlements retry once. Focused tests cover token renewal, socket loss, idle timing and idempotent settlement. Shared cap reservations remain authoritative; the historical local reporting mirror is off the dispatch path. Image completeness is checked at build. Cloud fixture mutation cannot use the read-only investigator, so the approved existing publisher/SQL-owner local fallback remains; the missing cloud mutation authority is recorded in owner-actions, without a grant. Lost Azure starts remain unestablished and unscored.

## Part B — guided intake

IntakeRequest/1 and catalog API/CLI are implemented. Full retained catalog projection treats inventory bookkeeping as optional warning fields. Screenshot lookup uses the actual attached image, visible fields and model-written native lookup; no screenshot pixels or personal values enter shared logs. A genuine unknown literal report ID now becomes a saved catalog question rather than an unsealed exception; it is never substituted.

## Part C — path triage

Ten path-local ledger-first checks run before reasoning. Only a named SCAN allocation exhaustion becomes unavailable triage; INV and total caps still refuse. The original scan allocation exhausted at2,000. The owner subsequently transferred500 October requests from investigation to scan (2,500/6,405/95 inside9,000); scheduled images must use the dated policy override. No automatic collection is relabelled as investigation. Only the three explicitly approved complete manual release smokes use investigation. Explicit model-selected history tools perform one bounded subject read under the separate investigation meter and existing reader/scanner GET scopes.

## Part D — AI investigation and query safety

The strongest discovered model writes investigative SQL/DAX. Original schemas, parser-based read-only checks, exact graph object scope, forced row bounds and deadlines remain. Successful repeated queries/tools reuse retained evidence. Path context, stable prefix, recitation, errors and checkpoints are retained. Native failed queries cannot establish absence. Per-ticket model exhaustion remains a real unresolved result, not a finding.

## Part E — generic investigation tools

Installed tools cover native SQL/DAX, retained definitions, lineage, candidates, record traces, history/refresh and security definitions. Existing manifest bindings now carry the declared application source and producer into route assembly; audit metadata remains evidence rather than a quantity boundary. Billing?s old manifest still has no declared system of record; equality must not silently invent that declaration. Live class coverage is partial and the official held-out targets were missed; permission and evidence-surface limitations are listed below and in owner-actions.

## Part F — business answer and engineer handoff

Delivered findings have a business answer and retained technical evidence. Every unresolved investigation carries its full private query text, results, stopping point, ruled-out checks and next checks. Engineer replies are stored as scoped, attributed ledger facts through the installed command. Partial32 handoff grades were16at2,9at1,7at0; these do not replace its0/32 answer score.

## Part G — independent tickets, dev, held-out and messy input

Independent v2 tickets and expectations were sealed at25339ea before investigation. All40 dev forms now pass the complete offline catalog/route check:39 open query layers and one unknown report ID refuses, with no catalog exception. Actual and stripped-bookkeeping catalogs open identical layers. The single-image restart is recorded in [the admission receipt](runs/round-twenty-three-dev-pass1-restart.json); The preserved partial attempt was independently graded0/32,harmful0, with8notrun; it is not a completed40-case score. See [partial result](round-twenty-three-dev03-partial.md). The completed single-image dev04 independently scored **1/40, harmful0**, investigator costUSD21.580202. See [complete result](round-twenty-three-dev04.md). Its forty original outcomes and expectations are unchanged. The next image groups context representation, fresh path-local facts, SQL CONVERT and PostgreSQL transaction fixes. Dev05 then completed26 baseline forms on one image, independently3/26 with harmful0 (14 fault forms not run), USD14.328799. See [partial pass](round-twenty-three-dev05-partial.md). The two dev06 column-route follow-ups reached native reads but both stopped at their model cap; independent grading is0/2,harmful0, both handoffs2/2, USD1.121265 ([receipt](runs/round-twenty-three-dev06-partial-grade.json)). No complete40-case improvement is claimed. At7162/9000 requests, further dev admissions ended to preserve held-out, messy-input, cleanup and release capacity. The first pre-freeze full suite failed5498 tests with1failure/1error; originals remain recorded. Packaging policy and scheme-neutral address fixes passed51 focused tests. Corrected07a0f92 full5505/50skip and separate112acceptance/52subtests passed, image2f22b43d published and freeze pushed asd5a3c8e. The once-only held-out run independently scored6/20, harmful0, with no engine change or expectation edit. Six answered,13stopped at the unchanged ticket model cap, and one history case retained a native interrupted network error. [Per-ticket and class receipt](runs/round-twenty-three-held-out-grade.json). Mean investigator costUSD0.5157291/ticket (USD10.314582total), excluding independent grading and setup controls. Completed multilayer investigations: median187.081s worker-body/254.955s full harness, p90232.101s/292.355s; those5runs exclude one delivered single-layer security answer. The receipt separately groups all6ANSWERED,13BLOCKED and1INTERRUPTED timings. Raw independent zero groups:10wrong-conclusion,2query-error,2triage. Unresolved handoffs:10graded2,4graded1; these never replace answer accuracy. Accuracy80%, every-class coverage and the under2-minute full-investigation target were missed. These v2 tickets differ from R22, so6/20 is not directly comparable with R22?s5/20. The owner skipped the unchanged60-text messy run because it would mostly measure the cost cap. Its prepared inputs are retained; zero messy runs are admitted. Instead, one separately labelled unscored26-static diagnostic is prepared: claude-opus-5-5, USD3 actual-usage case stop, October hard cap subsequently lowered to USD96 with USD3 reserved for independent grading. The owner additionally approved diagnostic-only stable-prefix caching; native cache usage is recorded and the uncached diagnostic preparation remains unused. Ticket and asset bytes, intake, context presentation and investigator loop remain unchanged. New diagnostic admissions stop below USD4 remaining and completed cases receive an independent diagnostic grade. Held-out workers stay on their frozen image. The diagnostic never replaces the Round23 score.

## Part H — restoration, validation and release

Final scored/diagnostic engine7d32316 passed5521 tests/50skips; image984bebba. A separate release-runner startup fix4b547f1 then passed54 focused tests and the complete5522-test/50-skip suite, zero failures/errors (775.421s). Published release image0c49608909bd74399c90c6baa9d50590a4421801f3ea9814052af363ebe15583; daily06UTC, six-hour graph and half-hour collector schedules all read back on it with unchanged configuration/resources/identity. The first manual smoke failed before any capture or investigation because binding froze per_execution=False while validation required True; its native startup failure remains recorded. Three corrected consecutive smokes, merge and postmerge validation are in progress. No official outcome or expectation was re-run or edited for that release-only fix. All dev04 failed/waiting definitions, latency source rows and schedules, history rows, stale rows/automatic-update setting and access objects were restored with retained hash evidence. Stale model own refresh completed and native baseline7661 returned. Access catalog owner payload and permissions match their originals. Temporal history remains on.

## Final results

Scores, class coverage, harmful count, handoff quality, failure groups, timings,
cost, owner actions, budget use, restores and open items: _pending_.

## Owner-requested diagnostic, grading audit and backtrack

Cached Opus diagnostic (unscored):5/13 attempts independently correct,0 harmful under the original grader;13 requested tickets not run. Ten attempts made model calls; three stopped before a successful call. USD3.933922 inference; native cache-read ratio65.8694%, no admitted investigation-prefix cache assertion failed. Same ten model-executed IDs cost USD0.3933922/ticket versus FableUSD0.5652407, with model/cache/cap differences preventing a causal model-only comparison. [Diagnostic receipt](runs/round-twenty-three-opusdiag02-cached-partial-grade.json).

Separate dev-only grading audit:113 outcomes, five disagreements; original criteria totals9verdict/13layer/11cause. The second model flags one borderline harmful assertion that a historical version exists; official scores are unchanged, but that history family is paused from further diagnostics. All five cases and both reasons are in [the audit](grading-audit.md). Current read-only evidence corroborates24 dev expectations;16 full causes remain unverified, not disproved. An unknown literal report ID in warehouse-scope-v2 requires owner review; no expectation was edited.

[First-wrong-step backtrack](failure-backtrack.md):104 zero-scored preserved dev outcomes across40 tickets, including all earlier passes, latest Fable and Opus. First supported step: budget26, target28, query28, triage10, tool choice10, conclusion1, write-up1. All104 are itemized with original grader reasons, query/results and visible decisions; five walkthroughs cover distinct failure types. Saved traces only: zero new estate reads/model calls and no code/score/expectation changes. Recorder omissions and the one unsealed partial UNKNOWN_REPORT trace are explicit limitations.

## Per-family results (official grades unchanged)

Each cell is correct/attempted; NR is not run. Partial passes and the unscored Opus diagnostic are separate columns. A family is a base ticket class with v1/v2 dev variants and v3 held-out variant.

| Family | dev03 | dev04 | dev05 | dev06 | Held-out | Opus diagnostic |
|---|---:|---:|---:|---:|---:|---:|
| access-export | NR | 0/2 | NR | NR | 1/1 | NR |
| application-baseline | 0/2 | 0/2 | 2/2 | NR | 1/1 | 0/2 |
| before-temporal-retention | 0/2 | 0/2 | 0/2 | NR | 0/1 | 1/2 |
| billing-invoices | 0/2 | 0/2 | 0/2 | NR | 0/1 | 0/2 |
| billing-mrr | 0/2 | 0/2 | 0/2 | NR | 0/1 | 2/2 |
| failed-application-load | 0/2 | 0/2 | NR | NR | 0/1 | NR |
| failed-billing-transform | 0/2 | 0/2 | NR | NR | 0/1 | NR |
| fixture-quantity | 0/2 | 0/2 | 0/2 | NR | 0/1 | 0/2 |
| latency-record | NR | 0/2 | NR | NR | 0/1 | NR |
| other-collected-definition | 0/2 | 0/2 | 0/2 | NR | 0/1 | NR |
| record-absent-everywhere | 0/2 | 1/2 | 0/2 | NR | 0/1 | 1/1 |
| record-repeated-gold | 0/2 | 0/2 | 0/2 | NR | 0/1 | NR |
| screenshot-record-01 | 0/2 | 0/2 | 0/2 | 0/1 | 1/1 | NR |
| screenshot-record-02 | 0/2 | 0/2 | 0/2 | 0/1 | 1/1 | NR |
| screenshot-record-03 | 0/2 | 0/2 | 0/2 | NR | 0/1 | NR |
| screenshot-record-04 | 0/2 | 0/2 | 0/2 | NR | 1/1 | NR |
| source-history | NR | 0/2 | NR | NR | 0/1 | NR |
| stale-model | NR | 0/2 | NR | NR | 0/1 | NR |
| waiting-application-load | 0/2 | 0/2 | NR | NR | 0/1 | NR |
| warehouse-scope | 0/2 | 0/2 | 1/2 | NR | 1/1 | 1/2 |

## Held-out verdict classes

| Expected verdict class | Correct / attempted |
|---|---:|
| access difference | 1/1 |
| as designed | 4/8 |
| different question | 1/1 |
| failed job | 0/2 |
| latency | 0/1 |
| not found | 0/1 |
| refresh stale | 0/1 |
| source changed history | 0/1 |
| transformation logic | 0/3 |
| waiting on job | 0/1 |
