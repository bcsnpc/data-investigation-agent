# Round 24 — reach the data

Frozen evaluation complete; release checks in progress. Runtime frozen at `b78299f6aee852fd10d5c5776fe69087aaef86f2`, image `ghcr.io/bcsnpc/data-investigation-agent/offline-worker@sha256:595047cfadca5d7709e2463dc52d6438cbc80e3786763af89f6bf192b7652f86`. Draft/release PR [#431](https://github.com/bcsnpc/data-investigation-agent/pull/431). Execution date2026-10-28UTC; owner prompt dated2026-10-27.

Held-out v3: **18/20, harmful0**. Different-model second grade: **18/20, harmful0**, all-four-field agreement19/20. Every ticket delivered an ANSWERED result and sealed capture. Accuracy>=80% and zero-harm targets met; **the overall pass line is missed** because two classes scored zero and full-investigation median234.5s exceeds120s. There is no general production-readiness claim.

## Part 0: Start and budgets

R23 closed at merge6d91b7bc/v0.23; main44c1c60 was the branch base. Approved October146USD combined AI,12000physical (SCAN2500/INV9405/REST95); November onward150USD/9000 (2500/6405/95). All historical/uncertain charges retained; no reset/refund. Three dollars initially protected for independent grading. Per-ticket3USD actual provider usage, monthly pending commitments included. Azure platform cap20USD unchanged, no new paid resource/identity/grant/secret.

Latest native ledger: AI$112.986601/146USD October, against100USD credit warning and150USD November default; $33.013399 available including pending commitment rules. Physical10621/12000, categories{'RESTORATION': 37, 'INVESTIGATION': 8270, 'SCAN': 2244}, restoration58 remaining of95. Historical70restoration still charged separately. Native Azure cost refresh succeeded after429backoff; billing can lag and the private response stays local. No cap was bypassed or observation timestamp invented.

| Recorded monthly AI purpose | Charged USD |
|---|---:|
| investigator | $94.146616 |
| screenshot | $0.000000 |
| enrichment | $10.806285 |
| writer | $0.376174 |
| grading | $2.799767 |
| smoke | $3.132495 |
| unattributed historical | $1.725264 |

Purpose labels are reported as recorded. Screenshot lookup helpers deliberately share the investigator case budget and are charged under INVESTIGATOR; separate SCREENSHOT0 is not a claim of free vision calls. The99native usage records include helper calls as well as the91investigation model turns. Unattributed historical amounts remain included, never dropped or re-labelled in sealed evidence.

## Part A: Anthropic and plumbing

Investigator, screenshot, enrichment, writer, grader, smoke and classification use Anthropic through the closed gateway. The component audit test covers exactly the endpoints/purposes used and denies other operations. No current runtime Azure OpenAI constructor; archived synthetic wire fixtures are explicit offline test adapters, never a runtime fallback. Three early Anthropic smokes earned3/3PASS on the early image before scoring. Existing scheduled jobs/resources/identities are retained.

PostgreSQL uses short transactions outside network waits, token renewal, stale-socket detection, TCP keepalives/connect timeout and bounded safe/idempotent reconnects. Monthly physical aggregation now runs server-side instead of transferring the full reservation history while holding the lock. Original failures remain recorded. Cloud investigator has no practice-write scope: mutation controllers stayed local under the existing publisher/owner, recorded as an owner-action limitation; no credential was moved or permission widened.

## Part B: Model, caching, cost and speed

Opus5.5 with stable tools/system prefixes; changing results follow. Model-requested independent reads on distinct layers can overlap; duplicates return the existing evidence ID. Only selected target paths are supplied, with lossless identifier presentation and native schemas/definitions. Capture bytes remain unchanged. Native per-call token counters are in the grade receipt.

Dev cost$5.545856/15completed ($0.369724/ticket), cache64.24%. Held-out cost$10.011597/20 ($0.500580/ticket), cache**70.44%**, meeting70%. Access is the cost outlier at2.132835USD, below3USD. Native input tokens/call: median43165.00,p9081003.00,n=99.

Full multilayer native Azure-job median234.5s,p90388.0s,n=18; worker median199.13s. Job-record median179.00s,p90273.00s. Holds0. Native job time includes startup/publication; harness time additionally includes fixture admission, polling and artifact fetch and is reported separately. Inclusive phases overlap and must not be summed; native-query sum is cumulative query time, not parallel wall time.

| Phase | Median seconds | p90 seconds |
|---|---:|---:|
| route schema seconds | 45.13 | 51.72 |
| triage seconds | 28.01 | 33.55 |
| investigation wall seconds | 105.68 | 199.27 |
| model seconds | 42.48 | 55.94 |
| native query sum seconds | 41.36 | 99.61 |
| startup seconds | 25.41 | 29.11 |
| publication seconds | 14.25 | 16.82 |

Time targets missed. Largest opportunities: reuse/lazily fetch unchanged path schemas; initialize job-only answers before eager SQL schema work; issue independent scoped reads together. Startup is a smaller measured share. Optional warm-worker gross idle estimate5.832USD/month would exceed the existing19.878333USD platform estimate; nothing provisioned.

## Part C: Graph health and paths

Native declared-source completeness **0/80 ->7/80 ->9/80 (11.25%)**: fixture2/66, billing7/7, Microsoft sample0/7. Native copy/source addresses, explicit script/procedure producers and exact Direct Lake bindings provide provenance; definition existence is not execution proof. Break groups and reproducible commands are in [graph-health.md](graph-health.md). Largest remaining fixture group is inline-seeded notebooks without a declared external application source; no link invented. Legacy sample filters/interactions and missing native columns remain separate gaps.

Production offline route check: all40forms,39validASSEMBLED,one original UNKNOWN_REPORT refusal,zeroFAILED; stripped bookkeeping metadata gives the same result. All28R23 target/path failures and five walkthroughs are pinned to that route regression. Live held-out reached and delivered20/20, which does not mean20correct conclusions or complete graph coverage.

## Part D: Query quality

R23 official-zero first-query failures28: wrong object/member12, validator11,dialect2,conversion2,temporal-date1. Definition HTTP400 probes are separate. Current query records: dev5errors/75attempts; held-out12errors/120attempts, classes{'validator rejection': 4, 'wrong column or table': 7, 'endpoint error': 1}. These are all attempts, including corrected errors, not the same denominator as28zero-causing failures. Final held-out first-zero groups contain no query failure: both are conclusion errors.

Typed schemas, dialect examples, keys/relationships, retained definitions, scoped literal samples and native error/schema feedback support two corrections. Valid CTEs, casts, windows and scoped DAX definitions pass; writes/out-of-graph objects remain refused. Typed retained table schemas may be reused with provenance; views or missing types still obtain native schema/dependency evidence. Pipeline SQL procedure bodies and explicit calls now resolve natively; no guessed producer.

## Part E: Triage and job-record fast path

Current native failed/running facts are read first and cannot be dismissed by value agreement; current tool-discovered facts also require disposition before consistency. Superseded historical RUN_HISTORY is excluded. Failed-app, failed-billing and waiting held-out cases all score1/1; they used3,4,2model calls and0.320904,0.574513,0.242652USD respectively. Few-call behavior improved, but the under0.20USD and under120s job targets are missed. No security-membership permission was widened; retained definitions/data recreation remain distinct from unreadable membership.

## Part F: Automatic backtrack and grading

Primary Sonnet4.6, second Opus5.5; no investigator tools or first-grade judgments supplied to the second grader. Final dev and held-out second-graded100%. Initial12held-out monitor tasks and both grades were byte-verified/reused, only8new grades per model. Verdict/layer/cause held-out correctness={'cause_match': 18, 'layer_match': 19, 'verdict_match': 18}; handoff grades={'0': 15, '1': 0, '2': 5}, mean0.50/2.

Dev primary first-zero groups{'query': 1, 'reading results': 1}; final held-out{'conclusion': 2}. [failure-backtrack.md](failure-backtrack.md) contains saved tools/queries/results and up to3walkthroughs per assessment; only2held-out zeros exist, so2distinct zero walkthroughs are shown. Original scores/oracles/tapes unchanged. Both held-out graders give18/20,harm0,agreement19/20; their cause flag differs for the absent-record case. Owner review is requested without changing this phase's score.

## Part G: Scored proof

Dev v2 unchanged: requested40, completed15,25NOT_RUN at the absolute80% monthly physical stop. Primary13/15,harm0; second12/15,harm1,agreement13/15. The disputed failed-load consistency answer remains scored as originally graded; a generic saved-trace regression repaired its cause before the held-out freeze. No further dev pass after80%. This partial pass is not a full40-ticket improvement claim.

R23 comparisons: dev1/40and3/26,official held-out6/20,unscored Opus diagnostic5/13. R24 has a new held-out set and a3USD actual-cost case limit; R23's different caps/engine/coverage prevent a controlled model-only comparison. Fable comparison NOT_RUN; messy60free-text NOT_RUN because remaining physical headroom must cover cleanup/release and cannot admit60x40bounded requests. No broader free-text claim.

Held-out v3 was independently authored/sealed after native scenario checks. Wording was unopened at freeze. **Method limitation:** a CASE_OPEN diagnostic inadvertently displayed one intake description afterward while repairing pre-submission cost-observation metadata; no engine, model logic, ticket or oracle changed afterward. That unscored admission attempt was restored, and the ticket had only one actual scored submission. All20native scenarios were present during their scored ticket. No held-out result drove a fix.

| Class | All-three correct |
|---|---:|
| access export | 1/1 |
| application baseline | 1/1 |
| before temporal retention | 0/1 |
| billing invoices | 1/1 |
| billing mrr | 1/1 |
| failed application load | 1/1 |
| failed billing transform | 1/1 |
| fixture quantity | 1/1 |
| latency record | 1/1 |
| other collected definition | 1/1 |
| record absent everywhere | 0/1 |
| record repeated gold | 1/1 |
| screenshot record 01 | 1/1 |
| screenshot record 02 | 1/1 |
| screenshot record 03 | 1/1 |
| screenshot record 04 | 1/1 |
| source history | 1/1 |
| stale model | 1/1 |
| waiting application load | 1/1 |
| warehouse scope | 1/1 |

Zeros: before-temporal-retention concluded a definition explanation instead of the unavailable source-history boundary; absent-everywhere returned not-found instead of the expected source-consistency/as-designed label. Both explicitly qualified limitations and neither grader called them harmful. Preserve the terminology/grading disagreement for owner review. Pass line: accuracy/harmMET; every-class coverage and median-speedMISSED; cache targetMET.

## Part H: Restoration and release

All15canonical control records have clear restoration flags. Original source row/business-schema hashes matched, original pipelines/schedules restored, temporary access objects removed with native ownership checks, original catalog owner hash and roles restored. Automatic updatesON persisted after reload, own refresh171364e4-a1b6-493a-9867-f240a8d8aaaeCompleted, native7661verified. Temporal history deliberately staysON; legitimate audit/history rows remain. Original billing bootstrap2011CREATE_SCHEMAfailure remains a known build issue, not an un-restored injection.

Frozen full suite5,606tests/50skips/zero failures. Final premerge full suite: PASS 5606 tests. Final3smokes: THREE_GREEN.
PR remains draft until final checks. Merge, main validation and tag are not yet claimed.

Open items: two conclusion classes, route/schema latency, incomplete graph sources/sample semantics, local-only mutation controllers, private security-membership gap, old billing bootstrap idempotency and the preserved disputed dev harmful flag. Unused Azure OpenAI deletion/warm service require owner decisions; no such change was made. See [owner-actions.md](owner-actions.md), [scoring.md](scoring.md), native run receipts and [injections](../tests/tickets/injections.md).
