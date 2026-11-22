# Round 27 quality report

Round 27 is in progress. The delivery repairs have passed offline qualification, but their live quality has not yet been established. The 15-ticket proof cohort must recover at least 11 correct answers with no reviewed harmful answer before the remaining development work can continue. No calibration or held-out v5 run has started.

Both graders same vendor (OpenAI); independent of the investigator vendor (Anthropic). New grades use Sol, Astra and an independent Terra review of disagreements, including disagreements about the first wrong step. Historical grades retain their original provider and rules.

## Regression and repair

The saved-trace diagnosis found nine query failures among 96 old queries and nine among 129 new queries. The clearest regressions occurred after useful evidence had been collected: delivery structure and evaluator failures prevented an answer. The repair adds one saved-evidence reformat opportunity and separates hard factual failures from soft presentation failures. Soft-only failures allow at most two rewrites, then delivery with a warning. Wrong question, wrong target and unsupported claims remain hard failures. Read-only enforcement and evidence validation remain enabled.

The qualified image is `sha256:639f85b7741844317990ef854a5e4c16994e12a3e69357fab12d2caaf43d8666`, source `fa4f08ca`. Qualification passed 5,953 tests, with 53 skipped, zero failures or errors, and all eight image shards passed. See [qualification](round-twenty-seven-repair-qualification.json) and [diagnosis](regression-diagnosis-r27.md).

Screenshot vision remains Opus; an older passing screenshot trace used Terra. That is a separate comparison change, not an attributed delivery improvement. The contradictory historical grade for Older export movement 1 remains unchanged.

## Proof cohort

The [predeclared proof plan](round-twenty-seven-proof-plan.md) contains 15 cases: 11 static and four serialized fault cases. Three initial attempts stopped on an invalid provider key before reasoning, were sealed and recorded as authentication interruptions, and are unscored. Their original tapes and results remain preserved. Distinct replacement attempts use the owner-stored key verified by a metadata-only HTTP 200 check. No secret value was printed or written to a file.

Live proof grading and its gate are pending. No improvement percentage is claimed from offline tests.

## Pass 1 and pass 2

The earlier pass-1 checkpoint contains 42 measured attempts and eight not-run inputs. Original-image outcomes, repair-image outcomes and five plumbing reruns remain separate. The nine primary grades formerly blocked by AWS were completed using the newly approved OpenAI protocol: official, strict and reviewed each 1/9, harmful zero. One diagnostic first-wrong-step disagreement was independently reviewed. These nine cases are not the full pass-1 score. See [nine-case grading](round-twenty-seven-nine-grades.md).

Pass 2 has not started. The full 20-ticket guard must be measured before calibration.

## Calibration and v5

Neither has run. Calibration follows pass 2 and requires at least 7/10 reviewed correct and zero reviewed harmful. V5 remains sealed; admission requires confirmed available Anthropic credit, less the $3 reserve, to cover the actual calibration mean times 40 times 1.3. A partial v5 is prohibited.

## Budget and environment

The owner confirmed $120 Anthropic credit. The recorded cap is prior committed spend plus $117, with the $3 reserve excluded and the $14.34 calibration allowance protected during development. OpenAI is restricted to grading, reviews and release smokes, with its reserve and November 29 expiry retained. AWS is disabled. Current spend, evaluator hard/soft totals, context-gap counts and final release results will be reported from saved records after the cohorts close.

The expired fixed-connection secret was rotated under owner approval without new identities or grants. Native readbacks returned fixture 8,765, billing 600 and application-load fixture 7,661. The original 360-row source and schema hashes were verified, temporal history remains enabled, and no injection was active when the static proof pilot began. Final injection, automatic-update and disk readbacks remain required before release.

### Corrected proof checkpoint, 2026-11-22 00:43 UTC
Nine of the predeclared 15 cases are saved and fully graded/reviewed: official5/9, strict5/9, reviewed5/9, harmful0. These are partial denominators; the 11/15 gate is not decided. Five correct: application baseline, billing MRR, billing invoices, repeated-Gold record, screenshot02. Four unresolved failures: family quantity, absent-everywhere record, screenshots01 and03. Two static and four serialized fault cases remain. All six initially indexed captures passed seal and audit-batch hash checks; later saved captures will be indexed likewise. Proof investigation spend so far $12.269985, grading/review $1.241640. The separate policy-blocked pilot and three authentication interruptions remain preserved and excluded from this proof score. Sourceb692051f/image6e570bed remains pinned; the release-only smoke patch has separate full qualification. Current rows and call-cost/cache breakdown: round-twenty-seven-proof-progress.json.
