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

Ten path-local ledger-first checks run before reasoning. Only a named SCAN allocation exhaustion becomes unavailable triage; INV and total caps still refuse. The scan allocation is now exhausted at2,000, so no automatic collection is relabelled or resumed. Explicit model-selected history tools perform one bounded subject read under the separate investigation meter and existing reader/scanner GET scopes.

## Part D — AI investigation and query safety

The strongest discovered model writes investigative SQL/DAX. Original schemas, parser-based read-only checks, exact graph object scope, forced row bounds and deadlines remain. Successful repeated queries/tools reuse retained evidence. Path context, stable prefix, recitation, errors and checkpoints are retained. Native failed queries cannot establish absence. Per-ticket model exhaustion remains a real unresolved result, not a finding.

## Part E — generic investigation tools

Installed tools cover native SQL/DAX, retained definitions, lineage, candidates, record traces, history/refresh and security definitions. Existing manifest bindings now carry the declared application source and producer into route assembly; audit metadata remains evidence rather than a quantity boundary. Billing?s old manifest still has no declared system of record; equality must not silently invent that declaration. Live class coverage and blocked permission needs are still pending the complete scored passes.

## Part F — business answer and engineer handoff

Delivered findings have a business answer and retained technical evidence. Every unresolved investigation carries its full private query text, results, stopping point, ruled-out checks and next checks. Engineer replies are stored as scoped, attributed ledger facts through the installed command. Partial32 handoff grades were16at2,9at1,7at0; these do not replace its0/32 answer score.

## Part G — independent tickets, dev, held-out and messy input

Independent v2 tickets and expectations were sealed at25339ea before investigation. All40 dev forms now pass the complete offline catalog/route check:39 open query layers and one unknown report ID refuses, with no catalog exception. Actual and stripped-bookkeeping catalogs open identical layers. The single-image restart is recorded in [the admission receipt](runs/round-twenty-three-dev-pass1-restart.json); The preserved partial attempt was independently graded0/32,harmful0, with8notrun; it is not a completed40-case score. See [partial result](round-twenty-three-dev03-partial.md). The completed single-image dev04 independently scored **1/40, harmful0**, investigator costUSD21.580202. See [complete result](round-twenty-three-dev04.md). Its forty original outcomes and expectations are unchanged. The next image groups context representation, fresh path-local facts, SQL CONVERT and PostgreSQL transaction fixes. Dev05 then completed26 baseline forms on one image, independently3/26 with harmful0 (14 fault forms not run), USD14.328799. See [partial pass](round-twenty-three-dev05-partial.md). The two dev06 column-route follow-ups reached native reads but both stopped at their model cap; independent grading is0/2,harmful0, both handoffs2/2, USD1.121265 ([receipt](runs/round-twenty-three-dev06-partial-grade.json)). No complete40-case improvement is claimed. At7162/9000 requests, further dev admissions ended to preserve held-out, messy-input, cleanup and release capacity. The final candidate has focused65 tests green; full regression and publication are running before freeze.

## Part H — restoration, validation and release

Release validation remains pending. All dev04 failed/waiting definitions, latency source rows and schedules, history rows, stale rows/automatic-update setting and access objects were restored with retained hash evidence. Stale model own refresh completed and native baseline7661 returned. Access catalog owner payload and permissions match their originals. Temporal history remains on.

## Final results

Scores, class coverage, harmful count, handoff quality, failure groups, timings,
cost, owner actions, budget use, restores and open items: _pending_.
