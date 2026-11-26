# DIA v0.27 quality report

> Owner decision, November26: **wait for the SQL free allowance to renew on December1 00:00UTC (November30,6p.m.Chicago); continue offline only**. Paid SQL continuation is not approved. The earlier decision-pending request is resolved. Confirmation remains pending21/25, not a final gate; source restoration/load verification is first after renewal. Calibration/v5 and merge/tag remain pending. See `round-twenty-seven-source-renewal-resume.md`.


> Latest recovery, 2026-11-26: confirmation is **pending21/25**, not complete or running. Reviewed outcomes so far:14fully correct,2usefulhandoffs,0harmful; guard14/16measured (20required). Azure SQL ordersops paused at its November free allowance (42119), blocking verification of the downstream restoration and the remaining four fault cases. Source rows/schema hashes were restored before pause; downstream restore is not yet verified. No paid database setting was changed. Owner decision is pending. Original confirmation image remains unchanged; three repairs are being qualified offline only. Calibration remains deferred to confirmedDec1balance and a passing full confirmation, and v5 stays sealed. All older checkpoint/closure paragraphs below are historical; PR435 remains draft, no merge/tag.


> Current checkpoint, November 26 UTC: owner prioritizes the complete 25-ticket confirmation. The corrected conservative forecast is $38.612307; with the protected $3 reserve it fits the lower $56 cash estimate. The earlier forecast omitted evaluator cache-write premiums; the correction and ledger readback are recorded in round-twenty-seven-owner-confirmation-priority.json. Confirmation is running on frozen source6731ead4, with static Batch and serial fault controls. Calibration is deferred until the confirmed December 1 balance and a passed confirmation gate. V5 remains sealed. Older completed-result sections below are historical until the final confirmation report is published.

**The quality gate was not established.** Paid pass 2 finished at 26/48 reviewed correct, 14 useful handoffs and 5 harmful answers. Paid pass 3 stopped at 21 of 39 required outcomes: 14 correct, 1 useful handoff and 1 harmful answer. Its guard was 11/13 measured, with all 20 required. Confirmation, fresh calibration and held-out v5 did not run. V5 remains sealed.

The owner explicitly directed closure when the whole-run funding gate cannot be met. This is an engineering release without a passed quality benchmark. All earlier outcomes, disagreements and harmful findings remain recorded.

## Recorded paid results

| Cohort | Reviewed fully correct | Useful handoff | Harmful | Guard |
|---|---:|---:|---:|---|
|Pass 1, complete 50|5/50|20|1|separate fixed selection|
|Pass 2, complete 48|26/48|14|5|17/20;FAIL|
|Pass 3, partial 21 of 39|14/21|1|1|11/13measured,20required;NOTPASSED|

Pass1 official/strict4/50; reviewed5/50. Pass2 official/strict/reviewed26/48. Partial pass3 official/strict/reviewed14/21. These are different repeated cohorts, never pooled into one accuracy number. See the immutable pass reports for individual outcomes and image splits. R17-05 remains harmful in the paid partial pass; the exact-question evaluator did not reject its wrong-target handoff. Free results do not erase that finding.

## Free-model engineering work — not a quality gate

| Separate cohort | Fully correct | Useful handoff | Harmful | Accounting |
|---|---:|---:|---:|---|
|Kimi proof|8|5|0|13 measured; 2 environment-unscored|
|OriginalSuperVL pass|14|13|1|30 measured of 32; 1 uncertain start, 1 not run; 2 other incorrect|
|Native-reference repair|1|3|0|4 replacements, separate|

The original harmful failed-job result came from dropped early native evidence; its distinct rerun graded correct after the generic fix. The original remains harmful. Other repair and screenshot cohorts remain separately reported in the OpenRouter checkpoint. Two stale cases were skipped at closure because browser control was unavailable; the uncertain original was not resubmitted. These results are not Opus confirmation, calibration or v5.

## Cost cuts and funding gate

Saved Opus cache-read share: investigation68.6627%,intake55.0831%,evaluator2.0583%. Caching already applied to the stable system and admitted investigation toolbox; the helper's actual tool schema now also has a cache breakpoint, under the existing cache switch. Prefix content is not rebuilt from mutable counters or timestamps. No new generated cache trial was charged.

The static-only Batch API preparation includes reserved requests, recorded owned submission IDs, bounded polling/results, no retry after an unknown POST, and50% batch rate cards including cache rates. Fault cohorts stay normal. The existing cache TTL is five minutes, whereas asynchronous batches can take up to 24 hours and successive tool-dependent waves may miss that TTL. Batch cache hits are best-effort; no live Batch saving has been measured. A pending batch must resume its saved ID instead of resubmission. This is prepared transport/API code; no whole confirmation was admitted or executed through it.

The25-ticket whole confirmation forecast is$37.568245 with static Batch, conservative cache-miss treatment and1.3margin. Saved cache-hit equivalent is$18.008947, reported as a sensitivity estimate rather than guaranteed future cost. Protect calibration$14.34 plus$3 cash reserve: total required$54.908245 against the conservative owner cash estimate$46, short$8.908245. Organization usage GETreturned401 because the workspace key is not an Admin API key; the exact Console balance was not independently readable. The lower owner estimate was used instead of inventing a cash readback. No partial confirmation. The optimistic estimate would fit if historical cache hits persisted; it is not the admission estimate because that timing has not been demonstrated for Batch.

Calibration retains the protected rounded$14.34 estimate, based on14saved nonzero current-round cases at mean$1.102982 and10×1.3=$14.338768. Fresh calibration has no actual usage because it never ran; caching savings on unknown fresh questions are not assumed. Its predeclared IDs remain:

R17-03-v1, R17-06-v1, R17-07-v1, R17-12-v1, access-export-1-v1, access-export-1-v2, baseline-S01-v2, baseline-S02-v2, baseline-S03-v1, different-warehouse-v1.

Confirmation list fixed before admission:

| Ticket | Prepared transport | Conservative forecast |
|---|---|---:|
| form-v2-access-export-v1 | NORMAL_FAULT_OR_UNKNOWN | $0.655130 |
| form-v2-access-export-v2 | NORMAL_FAULT_OR_UNKNOWN | $0.603390 |
| form-v2-application-baseline-v1 | BATCH | $0.367752 |
| form-v2-application-baseline-v2 | BATCH | $0.381947 |
| form-v2-billing-invoices-v2 | BATCH | $1.018237 |
| form-v2-billing-mrr-v1 | BATCH | $2.711484 |
| form-v2-failed-application-load-v1 | NORMAL_FAULT_OR_UNKNOWN | $1.090444 |
| form-v2-failed-billing-transform-v1 | NORMAL_FAULT_OR_UNKNOWN | $2.105613 |
| form-v2-fixture-quantity-v1 | BATCH | $0.695451 |
| form-v2-latency-record-v1 | NORMAL_FAULT_OR_UNKNOWN | $1.024274 |
| form-v2-other-collected-definition-v2 | BATCH | $1.904074 |
| form-v2-record-absent-everywhere-v1 | BATCH | $1.353039 |
| form-v2-record-repeated-gold-v2 | BATCH | $2.215672 |
| form-v2-screenshot-record-01-v1 | BATCH | $0.861034 |
| form-v2-screenshot-record-02-v1 | BATCH | $0.387055 |
| form-v2-screenshot-record-03-v1 | BATCH | $3.328286 |
| form-v2-screenshot-record-04-v1 | BATCH | $0.675338 |
| form-v2-source-history-v2 | NORMAL_FAULT_OR_UNKNOWN | $1.779746 |
| form-v2-waiting-application-load-v2 | NORMAL_FAULT_OR_UNKNOWN | $0.724761 |
| form-v2-warehouse-scope-v1 | BATCH | $1.256693 |
| form-v2-warehouse-scope-v2 | NO_TOKEN_RECORD | $1.430000 |
| text-R17-05-v1 | BATCH | $1.585809 |
| text-R17-08-v1 | BATCH | $2.745177 |
| text-R17-10-v1 | BATCH | $5.245314 |
| text-older-export-movement-1-v2 | BATCH | $1.422525 |

## Gates

Confirmation: NOTRUN,wholefundinggatefailed; no new guard score. Calibration: NOTRUN,confirmationnotpassed. v5: SEALED,NOTRUN; no official/strict/reviewed score or Wilson interval exists. No partial v5 and no Dec1grant assumed. Round28first action: verify Dec1balance and fund the whole prerequisite confirmation/calibration, then evaluate the whole v5 gate; a grant alone does not establish the earlier gates.

## Simplification and compatibility

64feature flags became3measured evaluator switches.61proven fixes are unconditional. Historical default-true specs remain no-ops; off-mode ablations are refused. Historical baseline-only tests are source fixtures, not silently rewritten expectations. Executable source LOC: engine68,705 to 68,804; tracked harness21,767 to 21,765; tests71,591 to 71,572. Physical lines include comments/blanks; two prepared transport modules account for the net engine increase. Local controllers are excluded from these three tracked-code categories; their reference audit is separate. Two unused generators totaling5,274bytes were exact-archived and committed; policy blocked their deletion, so no local deletion is claimed.

All123saved(status,after)classifications unchanged against qualifiedc7a06c1f:85finished,29historicalnegative/incomplete,9withoutcase. This is not123successful exact replays. No live estate reads or generation were made by compatibility replay. The templating audit is an inventory only and does not change runtime behavior.

## Restoration and release

Fresh read-only source/schema hashes match the360-row baseline; model7,661 and a completed native refresh are recorded in round-twenty-seven-close-restoration.json. All saved control restoration flags are false. Temporal history remainsON by prior decision. No new injection or Fabric toggle was performed at closure. The automatic-update setting is last owner-reportedON; current browser readback is unavailable and is explicitly an owner action, never claimed as tool verification.

Release validation, three full daily smokes, merge and tag are recorded in the final summary and machine receipts. Release smoke generation uses only the permitted$0synthetic free provider, because OpenAI is grading-only under the latest direction. A smoke is infrastructure/regression evidence, not an Opus quality score. No sealed expectation was changed.


## Source-blocked confirmation checkpoint, 2026-11-26

The required full25 confirmation is **not complete**, so no confirmation gate result is claimed. Of21 independently graded outcomes,14 are fully correct,2 useful handoffs and0 harmful; the guard is14 correct of16 measured, with20 required. Four cases (latency, waiting, two access cases) remain unadmitted. The21 outcomes cost Anthropic$8.666603 in actual recorded usage. There are no open budget reservations. The provider account has$44.333397 remaining commitment after the$3 cash reserve; this is ledger headroom, not a fresh Console cash reading.

The remaining blocker is the practice source resource allowance: ordersops returnedSQL42119, and Azure confirmsPaused/useFreeLimit=true/AutoPause untilDec1. The current source business/schema hashes were restored before it paused; the original360 downstream copy failed3161 and model7661 has not yet been reverified. No paid-overage setting or permission changed. Owner decision is pending. Original and recovery records are preserved.

Three generic repairs are being qualified offline, separately from the immutable original confirmation image. None is live-proven and no corrected quality score is inferred from unit tests. Calibration stays deferred to confirmedDec1balance and a passing full confirmation; v5 remains sealed. PR435 staysdraft/unmerged and v0.27 is not tagged at this checkpoint.
