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

Strict full-contract matching also checks provenance/resolution fields. For example, original PIPELINE I-r3 retained a qualified TRANSFORMATION_LOGIC finding but expected `report_binding: STATED` versus observed `USER_SUPPLIED_FORM`. Zero strict matches does not mean every matching pipeline finding is wrong or harmful. Expectations remain unchanged. Billing's latest failures are substantive: no full requested explanation was delivered.

The two harmful agent findings remain scored: A-r3 asserted actual duplicate join matches without proof; C-r3 invented a SUM for a subtraction measure. Later generic qualification fixes do not erase them. Prior Round Thirteen harmful findings are separate historical results, not additional Round Fourteen harms. See [fixture pair results](round-fourteen-original-paired-results.md) and [original hybrid results](round-fourteen-original-hybrid-results.md).

## Billing comparison

The independent cohort is nine sealed tester tickets (01–06, 13–15), each tested as a form and an unchanged free-text twin: 18 inputs. The 18 owner-authored tickets are separate and were not run here. Six unplanned rendering tickets (07–12) are excluded from scored billing expectations.

| Latest column | Reached technical investigation | Full contract matches | Harmful technical findings | Physical / diagnostic | Model calls |
|---|---:|---:|---:|---:|---:|
| PIPELINE, reference/grounding revision | 0/18 | 0/18 | 0 | 0 / 0 | 29 |
| HYBRID, same reference/grounding revision | 1/18 | 0/18 | 0 | 1 / 1 | 172 |
| Stronger HYBRID, remaining holds only | 1/17 | 0/17 | 0 | 1 / 1 | 194 |

PIPELINE forms all held; free text had two holds and seven clarifying states. HYBRID FORM01 completed NO_COMPARABLE_PATH / NOT_ANSWERED: a semantic-only 950 read, with no lower binding and no explanation of the application's 700/600 invoice amounts. The other 17 inputs held; none of the nine free-text twins reached investigation. Its incremental rate-card estimate was $6.899322. This is a qualified non-answer, not an invoice reconciliation success.

The earlier shared-intake columns (PIPELINE 1/18 admissions; HYBRID 2/18 admissions) remain recorded separately. The latest change did not improve admissions over those earlier revisions. Early pure billing AGENT had six attempted inputs and no delivered answer; its remaining queue was stopped when the owner switched to hybrid. See [pipeline records](round-fourteen-billing-span-pipeline-results.json), [hybrid records](round-fourteen-billing-span-hybrid-results.json) and [billing history](round-fourteen-billing-paired-results.md).

## Stronger model and availability

The account's deployed-model listing returned five successful deployments. GPT-5.5 (`investigator-intake-f-55`, 2026-04-24) is the strongest existing deployment. GPT-6 Astra is **offered** in the paginated account catalog but has no deployment. The initial first-page interpretation is preserved with a dated correction; it was not a complete catalog. No new deployment, identity, permission or credential was provisioned.

The stronger check changes agent decisions only to the existing GPT-5.5 deployment. Extraction, resolution and pipeline tools remain on GPT-5.4. Its higher rate is reserved and settled explicitly, with a protected $10 margin under the unchanged $100 guard. This tests the existing stronger deployment, not GPT-6 Astra. Receipts, full catalog and deployment distinction are in [the model inventory](round-fourteen-azure-model-inventory.json).

All 17 remaining inputs ran once: eight forms and nine free-text twins. All ended HELD. FORM14 reached a technical investigation and made one diagnostic read, then its proposed claim cited an unknown evidence ID and was refused; it exhausted the step cap. No additional answer was delivered. FORM01's prior completed qualified non-answer was not rerun. This selected hold cohort is not a replacement 18-input accuracy column.

Five forms and the final free-text input exhausted the step cap. FORM04 refused the business-rule route; FORM06 asked for a visual; FORM15 asked about business intent. Eight free-text inputs stopped on a report question or unresolved-name terminal note despite the already named report. Seven actually posted the fixed report question with the single catalog-backed Subscription Billing name; CHAT04 posted no question and repeated the tool's opaque ambiguous-name blocker. No new false duplicate-report question or choice-ID display was posted. This is failure to settle and route, not evidence that the user omitted the report.

Of 194 model calls, 164 GPT-5.5 and 27 GPT-5.4 calls have known provider usage; three additional GPT-5.5 calls retain conservative uncertain charges. Known receipt-priced cost is $13.751094, plus $1.631635 retained for those uncertain calls: $15.382729 increment to the shared guard. No uncertain charge was refunded to buy another attempt. Exact per-input reviews are in [stronger results](round-fourteen-billing-stronger-results.json); all 18 original inputs are shown side by side in [the billing comparison](round-fourteen-billing-final-comparison.md).

## Questions and presentation defects

Two earlier questions falsely claimed multiple Subscription Billing reports when the sealed catalog held one. They remain defects in the original tapes. Question construction now lets the model choose a missing-fact kind; engine code supplies fixed wording and catalog-backed choices. Tests retain both false-question cases. Copied provenance quotes were replaced by token references whose text is extracted exactly in code; ambiguity and referent-preservation refusals remain.

Name lookup uses the selected page's definitions. Three legacy visual-ID fallback paths were removed, and a newly observed PIPELINE CHAT02 page-URI leak was retained and fixed before subsequent admissions. Questions use visible names; unnamed or indistinguishable candidates are refused rather than displaying identifiers. However, redundant questions about an already named report/figure remain. Stronger FORM04's terminal hold also leaked evidence IDs and registry terminology; CHAT04 repeated opaque ambiguity wording despite one catalog report. Those residual defects are recorded and left unfixed under the owner's stop-intake-fixes decision.

## Every hold, capture and verification

[The grouped hold/refusal index](round-fourteen-hold-causes.md) covers every preserved held, refused, clarifying, failed or environment-affected attempt in the 199-artifact current map, including completed NO_COMPARABLE_PATH refusals. Its JSON includes exact stop reasons, review explanations and artifact hashes. Group labels describe the primary retained cause; contributing citation, route and settlement problems remain in each explanation. Historical revisions and environmental exclusions are not pooled into an accuracy denominator.

The latest PIPELINE 18, HYBRID 18 and stronger 17 have sealed captures with zero pending observations and zero capture exclusions. Earlier pre-admission recorder/native/disk failures remain explicit exceptions. Hash-verified transparent LZX compression preserved all logical evidence bytes, original reviews and outputs. Earlier selected exact replays passed, but historical CLOCK blockers remain; this is **not** an all-tapes replay pass. No original tape was edited to match a newer producer.

The unchanged production source used for the stronger comparison (`8c329c913ff2d885012193dd1b2451b214cb2b1159d649c3e213322081968d0a`) passed **3,362 tests**, native exit 0, 1,436.787 seconds wall time. The prior reference/grounding source passed 3,356. No further intake code change followed the stronger check. Local report generation is not another investigation or model call.

## Closing spend and windows

The shared model guard closes at **$87.703910 / $100**. This includes preceding work and conservative uncertain charges; it is a rate-card ledger, not a provider invoice or independently verified credit balance. $12.296090 remains under that guard, including the protected $10 margin. Twelve uncertain calls remain conservatively charged: nine historical calls ($3.620897) and three new GPT-5.5 calls ($1.631635). No current model reservation is open. The one historical cloud reservation remains explicitly recorded; it was not a new stronger-run reservation and was not silently refunded.

| Window at 2026-10-11 22:01:37 UTC | Usage / limit |
|---|---:|
| Round Fourteen physical pot | 2,592 / 4,000 |
| Protected restoration capacity | 95 still available, untouched |
| Ordinary rolling 24-hour physical requests | 1,239 / 3,000 |
| UTC-day model calls | 1,773 / 2,000 |
| UTC-day input characters | 73,190,504 / 80,000,000 |
| UTC-day gross reserved output tokens | 12,338,000 / 20,000,000 |
| UTC-day charged output tokens | 1,485,152 |

The regular billing HYBRID closed at pot 2,588 and shared guard $72.321181. Availability listing then used three physically counted control requests; the stronger cohort used one diagnostic request, closing pot 2,592. The rolling counter can decrease as old requests expire; that is not a refund or reset. Per-investigation diagnostic cap 12 remains unchanged; stronger actual maximum was one. No cap, ordinary allowance, scope or secret was raised for the stronger check.

The 199 indexed preserved attempts contain 1,641 model calls, 408 physical requests and $77.856015 known receipt-priced usage across historical comparison columns. Those totals exclude other controls/earlier setup work and uncertain charges, so they are not substituted for the cumulative guard. [The closing window](round-fourteen-final-window.json) retains the exact policy hash, charged/reserved counters and allowance state. The catalog contains 77 model/version entries across both pages, with five existing deployments; all three inventory controls are receipted.

## Causes requiring design changes

1. Primary figure, comparator and component amounts still require reliable role assignment across multi-number tickets. Exact span references solve transcription, not this interpretation problem.
2. Description, plan-change and filter questions lack a complete admitted route. Business-rule requests bundled with safe factual questions can cause the whole ticket to refuse; the asks need separate treatment without weakening the prohibition on judging business correctness.
3. Settlement state is not reliably propagated: the agent may ask again about a known report or figure. Repeated resolution and evidence fetches then exhaust the step cap. Stronger reasoning alone does not repair this state/progress problem.
4. Billing's semantic-only binding cannot provide application reconciliation or an attested lower walk. No model can manufacture the missing source and audit evidence.
5. Delivery requires persisted evidence IDs and complete coverage. The agent often refers to unpersisted tool citations; a typed, progress-aware handoff is needed, rather than a larger cap or looser validator.
6. Terminal holds should render user-facing names and reasons deterministically. The residual registry/ID dump is not a reason to relax grounded-question rules.
7. Capture growth and historical exact-replay CLOCK failures remain infrastructure work. Lossless compression preserved bytes; it does not establish that every tape replayed.

No further intake fixes are authorized in this round. Golden records, expectations and previous scores have not been revised to make these attempts pass. The conditional demo and adoption gate are NOT_EARNED. Draft #423 remains draft; the freeze is invalid. The final per-attempt map retains artifact hashes, source revisions, exact reasons and reviews; completed NO_COMPARABLE_PATH refusals are distinguished from unadmitted holds.
