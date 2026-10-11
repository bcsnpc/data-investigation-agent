# Round Fourteen final report

Closing report, 2026-10-11. PIPELINE remains the default. Agent and hybrid testing did not earn adoption: no full answer contract passed, and pure agent mode delivered two harmful fixture claims. Billing produced no harmful technical finding, but mostly failed to answer. A safe hold is not a successful answer.

## Fixture comparison

| Column | Coverage | Outcome/status matches | Full contract matches | Harmful | Physical requests | Model calls |
|---|---|---:|---:|---:|---:|---:|
| PIPELINE | 27 slots; 24 fresh attempts plus three eligible Round Thirteen D baselines | 20/27 | 0 | 0 | 142 fresh | 57 fresh |
| AGENT | 27 scored slots; environmental attempts retained separately | 7/27 | 0 | 2 | 136 | 581 |
| HYBRID | 22 preserved artifacts, 16 ordinary scored attempts; queue stopped by owner | Four completed conservative findings; no additional gap closed | 0 | 0 | 116, including excluded work | 211, including excluded work |
| Stronger hybrid | Not run on fixture; owner requested remaining billing holds only | Not measured | Not measured | Not measured | 0 | 0 |

These are different denominators and mixed producer revisions, not a common accuracy score or evidence of three-repeat stability. The fixture PIPELINE's fresh rate-card estimate is $0.657765; pure AGENT's is $26.745599. Reused historical baselines were not charged again. The original HYBRID queue's remaining I-r2 and all third repeats are NOT_RUN by owner decision. Rebuilt HYBRID is NOT_RUN: its required exact verification replay failed FINAL:CLOCK and its profile was not published.

The two harmful agent findings remain scored: A-r3 asserted actual duplicate join matches without proof; C-r3 invented a SUM for a subtraction measure. Later generic qualification fixes do not erase them. Prior Round Thirteen harmful findings are separate historical results, not additional Round Fourteen harms. See [fixture pair results](round-fourteen-original-paired-results.md) and [original hybrid results](round-fourteen-original-hybrid-results.md).

## Billing comparison

The independent cohort is nine sealed tester tickets (01–06, 13–15), each tested as a form and an unchanged free-text twin: 18 inputs. The 18 owner-authored tickets are separate and were not run here. Six unplanned rendering tickets (07–12) are excluded from scored billing expectations.

| Latest column | Reached technical investigation | Full contract matches | Harmful technical findings | Physical / diagnostic | Model calls |
|---|---:|---:|---:|---:|---:|
| PIPELINE, reference/grounding revision | 0/18 | 0/18 | 0 | 0 / 0 | 29 |
| HYBRID, same reference/grounding revision | 1/18 | 0/18 | 0 | 1 / 1 | 172 |

PIPELINE forms all held; free text had two holds and seven clarifying states. HYBRID FORM01 completed NO_COMPARABLE_PATH / NOT_ANSWERED: a semantic-only 950 read, with no lower binding and no explanation of the application's 700/600 invoice amounts. The other 17 inputs held; none of the nine free-text twins reached investigation. Its incremental rate-card estimate was $6.899322. This is a qualified non-answer, not an invoice reconciliation success.

The earlier shared-intake columns (PIPELINE 1/18 admissions; HYBRID 2/18 admissions) remain recorded separately. The latest change did not improve admissions over those earlier revisions. Early pure billing AGENT had six attempted inputs and no delivered answer; its remaining queue was stopped when the owner switched to hybrid. See [pipeline records](round-fourteen-billing-span-pipeline-results.json), [hybrid records](round-fourteen-billing-span-hybrid-results.json) and [billing history](round-fourteen-billing-paired-results.md).

## Stronger model and availability

The account's deployed-model listing returned five successful deployments. GPT-5.5 (`investigator-intake-f-55`, 2026-04-24) is the strongest existing deployment. GPT-6 Astra is **offered** in the paginated account catalog but has no deployment. The initial first-page interpretation is preserved with a dated correction; it was not a complete catalog. No new deployment, identity, permission or credential was provisioned.

The stronger check changes agent decisions only to the existing GPT-5.5 deployment. Extraction, resolution and pipeline tools remain on GPT-5.4. Its higher rate is reserved and settled explicitly, with a protected $10 margin under the unchanged $100 guard. This tests the existing stronger deployment, not GPT-6 Astra. Receipts, full catalog and deployment distinction are in [the model inventory](round-fourteen-azure-model-inventory.json).

## Questions and presentation defects

Two earlier questions falsely claimed multiple Subscription Billing reports when the sealed catalog held one. They remain defects in the original tapes. Question construction now lets the model choose a missing-fact kind; engine code supplies fixed wording and catalog-backed choices. Tests retain both false-question cases. Copied provenance quotes were replaced by token references whose text is extracted exactly in code; ambiguity and referent-preservation refusals remain.

Name lookup uses the selected page's definitions. Three legacy visual-ID fallback paths were removed, and a newly observed PIPELINE CHAT02 page-URI leak was retained and fixed before subsequent admissions. Questions use visible names; unnamed or indistinguishable candidates are refused rather than displaying identifiers. However, redundant questions about an already named report/figure remain. Stronger FORM04's terminal hold also leaked evidence IDs and registry terminology. That residual defect is recorded and left unfixed under the owner's stop-intake-fixes decision.

## Causes requiring design changes

1. Primary figure, comparator and component amounts still require reliable role assignment across multi-number tickets. Exact span references solve transcription, not this interpretation problem.
2. Description, plan-change and filter questions lack a complete admitted route. Business-rule requests bundled with safe factual questions can cause the whole ticket to refuse; the asks need separate treatment without weakening the prohibition on judging business correctness.
3. Settlement state is not reliably propagated: the agent may ask again about a known report or figure. Repeated resolution and evidence fetches then exhaust the step cap. Stronger reasoning alone does not repair this state/progress problem.
4. Billing's semantic-only binding cannot provide application reconciliation or an attested lower walk. No model can manufacture the missing source and audit evidence.
5. Delivery requires persisted evidence IDs and complete coverage. The agent often refers to unpersisted tool citations; a typed, progress-aware handoff is needed, rather than a larger cap or looser validator.
6. Terminal holds should render user-facing names and reasons deterministically. The residual registry/ID dump is not a reason to relax grounded-question rules.
7. Capture growth and historical exact-replay CLOCK failures remain infrastructure work. Lossless compression preserved bytes; it does not establish that every tape replayed.

No further intake fixes are authorized in this round. Golden records, expectations and previous scores have not been revised to make these attempts pass. The conditional demo and adoption gate are NOT_EARNED. Draft #423 remains draft; the freeze is invalid. The final per-attempt map retains artifact hashes, source revisions, exact reasons and reviews; completed NO_COMPARABLE_PATH refusals are distinguished from unadmitted holds.
