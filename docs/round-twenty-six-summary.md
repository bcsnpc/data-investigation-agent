# Round 26: front door and providers

Status: measurements closed; final release checks in progress, not yet merged or tagged. The owner ended development after dev06. No further dev loop or expectation change is authorised.

## Quality results

The final failed-only cohort has **3/28 correct under independent saved-evidence review**, official5/28 and strict2/28. Official harmful1; secondary/reviewed harmful0. The official flag was disputed by the independent reviewer; neither record was removed. Dev02's two reviewed harmful answers remain. These are selected rerun cohorts, not accuracy on the original80tickets or a held-out score.

| Final cohort class | Cases | Official | Strict | Reviewed projection |
|---|---:|---:|---:|---:|
| Static |14|0|0|0|
| Source history |3|0|0|0|
| Access |2|2|2|2|
| Latency |4|0|0|0|
| Waiting |1|1|0|1|
| Stale |4|2|0|0|
| Total |28|5|2|3|

Outcomes:11NEEDS_INPUT,5UNRESOLVED,1BLOCKED,11ANSWERED. An ANSWERED label is not a correctness score. Median lifecycle249.73seconds/P90453.16seconds includes admission/startup/polling; it is not pure investigation time. Actual model cost for these28investigations isUSD21.015183, excluding grading/audit. See [results](round-twenty-six-dev06-results.json), [model costs](round-twenty-six-dev06-model-costs.json) and [backtrack](round-twenty-six-dev06-backtrack.md).

| Pass | Official | Strict | Reviewed projection | Reviewed harm |
|---|---:|---:|---:|---:|
| Dev01 main selected cohort |20/52|incomplete coverage|incomplete coverage|incomplete coverage|
| Dev01 deferred stale, separately |2/4|0/4|0/4|0|
| Dev02 |5/30|4/30|5/30|2|
| Dev03 preliminary subset |0/2|0/2|0/2|0|
| Dev04 subset |1/3|1/3|1/3|0|
| Dev05 subset |0/3|0/3|0/3|0|
| Dev06 final |5/28|2/28|3/28|0|

Dev01 main official harm1 remains recorded. Images/cohorts differ; this table is not a controlled trend, and passes are not summed into an80-case score. Prior delivered answers, partial captures and uncertain charges remain unchanged.

## Freeze, Opus calibration and held-out gate

Runtime source ca249b730f463661b1d8ad7cf1e7a1794cd0073a; engine-reference fix e696ce33. Pinned image:

`ghcr.io/bcsnpc/data-investigation-agent/offline-worker@sha256:e59d3d97ee706a1666650b4dfbc7b1f7020ee044274ed73862c81d9d822a4770`

Fresh frozen qualification42929942388 on documentation headccdcd8ff passed5,909tests/53skips/zero failures/errors and all eight image-contract shards. Runtime source diff from the pin is empty; no replacement image was published. The numeric XML artifact was downloaded through GitHub and SHA256-verified. The interrupted duplicate local suite is preserved as interrupted, not called a pass. See [freeze](round-twenty-six-engine-freeze.json) and [qualification](round-twenty-six-frozen-qualification.json).

Ten public dev free-text calibration cases completed on frozen e59, selected before their Opus answers as five prior Astra passes and five failures. **Independent reviewed projection2/10, official2/10, strict2/10; reviewed/official harmful2.** Nova secondary4/10,harm0; full-score agreement8/10. Eight disagreements including harm, partial, first-step or handoff fields received fresh independent Sol review. Outcomes6ANSWERED,3NEEDS_INPUT,1BLOCKED. The quality gate failed; v5 stays sealed and no further dev loop is authorised. Ten unique native executions and seals are retained; original local pre-start failures remain unscored. Azure Activity Log proved the last uncertain attempt never started before its first actual native run was admitted. [Calibration](round-twenty-six-calibration-final.md), [saved-trace backtrack](round-twenty-six-opus-calibration-backtrack.md).

Actual calibration investigation AI costUSD5.473769 (USD0.547377/ticket), excluding grading/audits and historical unknown charges;136physical requests. The22Opus reasoning calls averageUSD0.112025/call with66.32%cached input;14Sol intake calls average0.048898/71.77%;8Astra intake-fallback calls0.290582/73.41%. Native timing is available for6/10only: median183.5seconds/P90313seconds, excluding local admission/download. Missing native end times remainnull. The planning-only full40 mean×52 estimate isUSD28.463599; it is not an admission or a claim that all provider headroom suffices.

V5 remains sealed, wording unopened and zero scored admissions. Seal commit a744dcae; ticketSHA2560b7f11b7d74cadaf6ccfcc5d82716bb5444956b0f2b56442d6b87c41a5418767; expectationSHA2566bc8d9c233fa6e15c4d42f75e51c7e042eafded34492e2b13df424111738f92b. It needs calibration≥70%/harm0, then full40coverage at actual Opus mean×40×1.3 and the lower available Anthropic credit/ledger balance minusUSD3. OpenAI helper/grading/release and physical headroom also remain bounded. Never partial v5. The latest owner forbids another dev loop: failed calibration keeps v5 sealed and closes the round. Held-out overall/form/free-text/class scores and intervals are **not available**, not0/40. Regression v4/R22held-out runs have not been admitted in this closing phase; no new comparison with R25 is earned.

## Provider benchmark (not the held-out headline)

| Earlier common-image column | Official | Harm | Actual USD/ticket | Median lifecycle s | Reasoning cached input |
|---|---:|---:|---:|---:|---:|
| Sol→Astra unresolved-only |13/40|1|0.442175|193.32|61.27% Sol /45.47% fallback|
| Astra-only |28/40|0|0.685846|203.23|65.00%|
| Opus |34/38|0|0.390287|206.82|68.67%|

Two Opus stale cases were not admitted after the credit-purpose restriction; unequal full denominators are disclosed. On the common26static cases the columns are5/26,19/26,23/26, all harm0. Opus is the provisional quality-first choice, not a fully qualified40-case default. Cross-vendor primary graders were used, with mixed primary-grader batches disclosed. Selected-outcome costs exclude original environment-failure costs that stay charged in the ledger; timings omit two Opus records without usable lifecycle logs. [Benchmark](round-twenty-six-provider-benchmark.json), [final usage](round-twenty-six-benchmark-usage-checkpoint.json).

Actual reasoning cost per call: SolUSD0.028479; its Astra fallback0.223914; Astra-only0.152410; Opus0.091293. Sol intake28/40 versus Astra28/40 and Terra21/40 selects Sol by readiness then cost:USD0.024139/call,88.04%cached, against Astra0.123874/18.37% and Terra0.010282/86.74%. One Astra intake fallback gives29/40,USD7.733820total/0.193346per ticket. Engine-revision differences mean this intake comparison is observational. Terra synthetic screenshot0.000753 and corrected structured summary0.000535 per call are not live-estate quality scores and were below caching size. Original failed-summary charge remains.

Saved dev06 grading costs: Nova Pro primary28calls averagedUSD0.006448/call (1.98%cached); Sol secondary29returned calls including the preserved schema-rejected response averagedUSD0.015157/call (5.30%cached);24fresh Sol disagreement-review calls averagedUSD0.018411/call (0%cached). These are returned normalized usage records, not refunds of unknown charges. Benchmark screenshot Terra12calls averagedUSD0.005174/call,0%cached; summaries used the separately labelled synthetic transport check. See [grading costs](round-twenty-six-dev06-grading-costs.json).

OpenAI/Anthropic adapters and configured per-step/tenant gateway policy are implemented; Azure OpenAI has fake-endpoint/API-key tests only, no live deployment claim. Native cache-read ratios use summed cached input/total input; stable prefixes and later-call contracts are tested. Nova is a bounded helper/grader, not an investigator. Approved single Bedrock Haiku test returned404after23.732seconds, no retry; guard is restored and credit coverage is unknown.

## Intake, conclusions and Round27

The11native Round25exception receipts (ten COMPARISON_DETAILS_REQUIRED, one transport URLError) have generic regressions. Fuzz/shape/fallback tests pass in the full suite; this is not proof of universal live settlement. Final dev06 still has11intake holds and one separate DAX-function BLOCKED result.

The25final failures group into11intake blocks;6unresolved/query/budget stops;5ANSWERED results that do not establish the requested conclusion;3stale answers rejected on the fixed named-cause requirement. The latter measured7,661versus7,692 and supplied refresh/load times and a settings pointer under PartD's API-limitation fallback. The fixed expected cause remains automatic updatesOFF. Neither expectations nor scores were changed to hide that discrepancy.

[Round27 backtrack](round-twenty-six-round27-backtrack.md) lists25tickets that failed every graded appearance, with at least two appearances; missing runs do not count as failures. A separate fresh code-blind Sol review received only public dev wording, fixed expectations and saved native/control evidence, not engine code, DIA answers or prior grades. Preferred final reviews:7expectationsSOUND,18UNVERIFIABLE in the bounded packets; all25inputs judged sound in wording, not proof that all opaque addresses are valid. Original limited reviews and uniform native-refresh supplements remain. No expectation was changed. First-wrong-step labels in the final25failures are intake6,target5,query error3,query validation2,triage1,wrong conclusion7 and conclusion1; the two conclusion labels total8. These are first-error classifications, distinct from terminal outcome groups.

Independent disagreement review is a **saved-evidence projection**, not claimed as all raw provider tape bytes. Packets preserve literal query/numeric/business fields, label bounded history/row samples and hash omissions;24,000-character limits remain. All graders' verdict/layer/cause/harm decisions are retained.

## Platform, budget and cleanup

PostgreSQL root cause remains unestablished. Measured credits286–288, average CPU9.5–19.6%, maximum12/50connections and zero failed connections do not establish capacity exhaustion. Short-lived connections, keepalives/timeouts, narrow account queries and idempotent-safe retry are implemented. No tier or role was widened. Local closing CLI calls were slow under laptop memory pressure; direct worker ARM GET took185.60seconds. Those pre-database/pre-start timeouts are not called PostgreSQL failures. Local startup tolerance and exact-resource GET spelling compatibility do not change the frozen engine, cloud runtime, model/estate deadlines or budget caps.

Authoritative post-calibration/pre-release snapshot: AnthropicUSD51.719843/120.575301; OpenAI170.173757/180; Bedrock0.852297/5round-total,Nova-only; combined222.745897USD. These are shared ledger totals, not only the final calibration. Committed equals charged at this observation. Owner-reported Anthropic cash74.32 is not Admin-API verified; preserve3cash margin, calibration/v5-only purpose and auto-reloadOFF. Physical9,853/14,500:INV7,658/11,905;SCAN2,144/2,500;REST51/95,44remaining. No counters reset. Release smokes and later scheduled activity will be reported separately.

Approved cache/build cleanup completed46removal paths and52matching source/configuration/lock hashes. Observed C15.10GiB/D25.66GiB free. The standalone D interval gained8.96GiB net, excluding earlier partial Flutter cleanup; C drive movements include paging and are not pure cleanup savings. Active runtime/installer, a locked previous runtime and the three mixed-content conditional cache directories remain. No evidence folder was deleted or archived. Owner-approved eligible evidence archiving follows merge/tag only, with dependency audit, upload checksums and protection for runtime/seals/ledgers/RESUME. [Cleanup receipt](round-twenty-six-owner-cleanup.json).

All dev06 injections are restored: original360-row source business hash0a78462d4e4dfd7bf66aeda89cd4d4757f2149fb00d61a14a597922216049a0b; business-schema hashbf740fed4ff464295e4ccc9642380fc576dc5013411a1c2e8f2fd91ba822bbbd; original real copy completed; DirectLake automatic updatesON independently reopened/read back, scheduleOFFunchanged; own refresh e0773fcf-6fb9-456a-bd08-44839e3a539f Completed; native model7,661. Temporal history staysON, so no whole-database-byte-identical claim. Four latency schedules/rows, three isolated access objects and waiting Wait-only definition are removed/restored with recorded hashes. Original waiting pipeline hash89cf27eb761019bc6e4edf027511ccc3411a4a385650dcb006fb7a85cddd1259. [Injection log](../tests/tickets/injections.md).

Owner actions/open items: check OpenAI credit expiry; check AWS Bills for the approved Haiku attempt (coverage unknown); resolve weak free-text/technical conclusion quality and public stale-contract discrepancy in the next round; investigate PostgreSQL with evidence rather than infer a cause or increase tier. No API/MCP/UI or hospital-estate expansion was started.

## Release

Release is not yet complete. Three manual smoke inputs are prepared on frozen e59; they use OpenAI because the later Anthropic purpose restriction permits only calibration/v5. This is an explicit difference from original default-provider smoke wording, not an Opus smoke claim. Full final-head qualification, smoke outcomes, ready/CI/merge commit, exact-merge validation, tag and summary-main receipts will be recorded before declaring released.
