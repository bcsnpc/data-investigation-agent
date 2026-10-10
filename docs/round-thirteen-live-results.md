# Round Thirteen live results

In progress. A ticket earns stability only after three outcome matches. Exact contract differences remain separately recorded; USER_SUPPLIED_FORM is never relabelled STATED to gain a match. No unfinished run is credited.

Round model dollar guard: $0.984035/100; 0 unsettled calls retain full reservations. Public rate-card accounting, not an invoice.

| Ticket | Repeat | Expected | Actual | Outcome match | Exact match | Harmful | Physical | Model calls | USD known + unknown bound | Seconds |
|---|---:|---|---|---|---|---|---:|---:|---:|---:|
| original family-D | 1 | NO_COMPARABLE_PATH | unavailable | False | None | False | 0 | 0 | 0.000000 + 0.000000 | 103.2 |

## Preserved local concurrency stop

.local\round-thirteen\live-original-f92727a\operator-stop.json: STOPPED_LOCAL_CONCURRENCY_DEFECT. Four admitted attempts preserved;23 unadmitted. Three provider calls,zero estate reads. No stability score from aborted attempts.
- family-B: ABORTED_AFTER_LOCAL_CONCURRENCY_DEFECT; D sqlite3.OperationalError database is locked at intake BEGIN IMMEDIATE; repeated historical-clock recording held writers. Operator stopped admission with provider calls settled and zero estate dispatches. Other attempts and unfinished tape journals preserved, never treated as completed or a match.
- family-A: ABORTED_AFTER_LOCAL_CONCURRENCY_DEFECT; D sqlite3.OperationalError database is locked at intake BEGIN IMMEDIATE; repeated historical-clock recording held writers. Operator stopped admission with provider calls settled and zero estate dispatches. Other attempts and unfinished tape journals preserved, never treated as completed or a match.
- family-C: ABORTED_AFTER_LOCAL_CONCURRENCY_DEFECT; D sqlite3.OperationalError database is locked at intake BEGIN IMMEDIATE; repeated historical-clock recording held writers. Operator stopped admission with provider calls settled and zero estate dispatches. Other attempts and unfinished tape journals preserved, never treated as completed or a match.
- family-D: FAILED_LOCAL_LOCK; D sqlite3.OperationalError database is locked at intake BEGIN IMMEDIATE; repeated historical-clock recording held writers. Operator stopped admission with provider calls settled and zero estate dispatches. Other attempts and unfinished tape journals preserved, never treated as completed or a match.

## Preserved four-attempt checkpoint (source912fce1)

Outcome/status agreement and exact contract agreement are separate. Reporting latency includes measured redundant local tape validation. The batch paused before the next cohort; these attempts are never replaced.

| Ticket/repeat | Expected outcome | Actual outcome/status | Outcome/status match | Exact match | Harmful | Physical | Model calls | USD | Procedure seconds |
|---|---|---|---|---|---|---:|---:|---:|---:|
| original family-A-r1 | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC / COMPLETED | True | False | False | 10 | 3 | 0.037316 | 734.6 |
| original family-B-r1 | NO_KNOWN_PATTERN | NO_COMPARABLE_PATH / COMPLETED | False | False | False | 1 | 1 | 0.008858 | 465.0 |
| original family-C-r1 | None | None / HELD | True | False | False | 0 | 1 | 0.008838 | 365.9 |
| original family-D-r1 | NO_COMPARABLE_PATH | None / HELD | False | False | False | 3 | 1 | 0.009905 | 578.8 |

USD1.048952/100; cumulative pot1268/2500, restoration95, rolling3000, diagnostic12. Zero completed three-repeat stability verdicts.

## Dated next eight attempts, 2026-10-10

All admitted attempts are preserved; fifteen original-fixture slots remain unadmitted. A completed procedure is not a delivered synthesis. Capture-attribution failures remain ungraded pending separate hash-bound corrections; the original reporting artifacts are unchanged. No three-repeat stability is earned.

| Ticket/repeat | Expected outcome | Procedure outcome/status | Synthesis | Physical | Model calls | USD | Seconds | Original reporting status |
|---|---|---|---|---:|---:|---:|---:|---|
| original family-F-r1 | CONSISTENT_TO_BOUNDARY | None / None | NONE | 0 | 1 | 0.009093 | 136.3 | RETAINED_ATTEMPT |
| original family-H-r1 | NO_KNOWN_PATTERN | NO_KNOWN_PATTERN / COMPLETED | BLOCKED | 1 | 1 | 0.009375 | 256.5 | CAPTURE_BLOCKED |
| original family-E-r1 | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC / COMPLETED | COMPLETED | 10 | 3 | 0.035338 | 328.7 | CAPTURE_BLOCKED |
| original family-G-r1 | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC / COMPLETED | COMPLETED | 10 | 3 | 0.036595 | 335.6 | CAPTURE_BLOCKED |
| original family-C-r2 | None | None / HELD | COMPLETED | 0 | 1 | 0.008838 | 237.5 | CAPTURE_BLOCKED |
| original family-B-r2 | NO_KNOWN_PATTERN | NO_COMPARABLE_PATH / COMPLETED | BLOCKED | 1 | 1 | 0.009068 | 264.9 | CAPTURE_BLOCKED |
| original family-A-r2 | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC / COMPLETED | COMPLETED | 10 | 3 | 0.035620 | 334.6 | RETAINED_ATTEMPT |
| original family-I-r1 | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC / COMPLETED | RUNNING | 10 | 3 | 0.037379 | 337.7 | RETAINED_ATTEMPT |

F-r1 refused intake with DESCRIPTION_SUBJECT_UNRESOLVED; no investigation read occurred. H-r1 stopped synthesis before a provider call; I-r1 received a provider response but failed during governed settlement. H originally retained only TapeError; its detailed budget-journal cause was established separately offline. I retained TAPE_BUDGET_DELTA_BEFORE_DIFFERS natively. Neither is credited with delivered findings. A-r2 delivered a scoped transformation explanation. E/G delivered qualified findings; E repeats timing limitations, a recorded presentation defect rather than an expanded causal claim.

The journal serializes SQLite REAL timestamps with fewer significant digits than their stored binary64 value. Strict comparison correctly refuses the changed before-image. New recording needs a lossless, versioned producer; tolerating a timestamp difference was rejected. No original journal or tape is edited.

USD1.230258/100,76 model calls,zero unsettled dollar reservations; cumulative pot1310/2500,restoration95,rolling3000,diagnostic12 unchanged. I left one governed model reservation active after the checkpoint failure; recovery remains pending and counters are preserved. No new admission until recording and settlement accounting are safe.

Dated scope correction, 2026-10-10: the8/8 offline checkpoint covers two workspace operations per first-cohort ticket. A later session-identity audit found a third, separate agent.run tape for each ticket; those four procedure tapes were absent from that inventory and are pending replay. The eight matches and their seals remain true, but they do not establish complete capture closure. The original map is unchanged; an expanded, separately hashed map will include every operation.


Dated semantic correction, 2026-10-10: the first four attempts on 242f20e completed recording with no capture diagnostics. D-r2 remained HELD with a retained OperationalError while saving a receipt; its message is withheld, so a lock cause is not established. F-r2 completed CONSISTENT_TO_BOUNDARY but labelled the requested supported explanation PARTLY_ANSWERED as a comparison. Boundary equality does not establish that mechanism: this is one harmful answer-coverage overclaim, with no confident wrong causal finding identified. F is paused; the original delivered output and automatic audit are preserved, with a separate dated review correction. E-r2 and G-r2 completed TRANSFORMATION_LOGIC synthesis; neither establishes currency or business intent. These four used 30 physical requests. The next already-admitted cohort drains before the operator pause; no replacement runs. Current shared model spend USD1.367360/100 (89 calls, no unsettled dollar reservation at the checkpoint). Completed-attempt physical accounting is at least1340/2500; concurrent requests are reported from their own receipts when settled. Reserve95, rolling3000 and diagnostic12 remain unchanged.


## Preserved eight-attempt242f20e cohort, 2026-10-10

The batch ended after B-r3/H-r2 capture-attribution audits blocked on an unrelated recording; an operator pause for F had also been queued. Twenty original-fixture slots are now admitted; C/D/E/F/G/H/I-r3 remain unadmitted. F-r3 is paused by the harmful-coverage stop rule. No admitted attempt is replaced.

| Ticket/repeat | Expected | Actual | Synthesis | Harmful coverage | Physical | Model calls | USD | Seconds | Native capture status |
|---|---|---|---|---|---:|---:|---:|---:|---|
| family-D-r2 | NO_COMPARABLE_PATH | None / HELD | COMPLETED | not identified | 3 | 1 | 0.010100 | 418.8 | RETAINED_ATTEMPT |
| family-F-r2 | CONSISTENT_TO_BOUNDARY | CONSISTENT_TO_BOUNDARY / COMPLETED | COMPLETED | YES (dated root correction) | 7 | 2 | 0.019586 | 470.1 | RETAINED_ATTEMPT |
| family-G-r2 | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC / COMPLETED | COMPLETED | not identified | 10 | 3 | 0.034575 | 474.4 | RETAINED_ATTEMPT |
| family-E-r2 | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC / COMPLETED | COMPLETED | not identified | 10 | 3 | 0.035925 | 477.0 | RETAINED_ATTEMPT |
| family-B-r3 | NO_KNOWN_PATTERN | NO_COMPARABLE_PATH / COMPLETED | COMPLETED | not identified | 1 | 2 | 0.018613 | 374.9 | CAPTURE_BLOCKED |
| family-H-r2 | NO_KNOWN_PATTERN | NO_COMPARABLE_PATH / COMPLETED | COMPLETED | not identified | 1 | 2 | 0.019573 | 379.6 | CAPTURE_BLOCKED |
| family-I-r2 | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC / COMPLETED | COMPLETED | not identified | 10 | 3 | 0.037121 | 481.8 | RETAINED_ATTEMPT |
| family-A-r3 | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC / COMPLETED | COMPLETED | not identified | 10 | 3 | 0.037698 | 486.9 | RETAINED_ATTEMPT |

USD1.443449/100,95calls,zero unsettled dollar reservations; pot1362/2500,reserve95,rolling3000,diagnostic12. These eight used52physical requests and19model calls. Capture closure and exact revision replay are separate pending checks. Earlier incorrect zero-harm automatic audits remain unchanged; the root F correction is appended. No confident wrong causal finding has been identified in reviewed delivered outputs.

## Original-fixture final six, 2026-10-10

These are the remaining unpaused slots, not replacements. Original F-r3 is PAUSED_UNADMITTED. All six returned; capture closure resolved both pending recordings with conservation and zero blocked entries. The repeats span recorded engine revisions; they are not three repeats of one final frozen revision.

| Ticket/repeat | Expected | Actual | Synthesis | Physical | Model calls | USD | Seconds | Harmful found |
|---|---|---|---|---:|---:|---:|---:|---|
| family-C-r3 | None | None / HELD | COMPLETED | 0 | 1 | 0.008853 | 324.9 | no new harmful claim identified |
| family-D-r3 | NO_COMPARABLE_PATH | None / HELD | COMPLETED | 2 | 1 | 0.010100 | 386.8 | no new harmful claim identified |
| family-G-r3 | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC / COMPLETED | COMPLETED | 10 | 3 | 0.035676 | 486.4 | no new harmful claim identified |
| family-E-r3 | TRANSFORMATION_LOGIC | NO_COMPARABLE_PATH / COMPLETED | COMPLETED | 14 | 2 | 0.023818 | 543.3 | no new harmful claim identified |
| family-H-r3 | NO_KNOWN_PATTERN | NO_COMPARABLE_PATH / COMPLETED | COMPLETED | 1 | 2 | 0.019483 | 260.7 | no new harmful claim identified |
| family-I-r3 | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC / COMPLETED | COMPLETED | 10 | 3 | 0.035088 | 351.8 | no new harmful claim identified |

The six used37 physical requests and12 model calls. All26 original attempts used145 physical requests and53 model calls, separately from development and the aborted pre-admission concurrency cohort. Shared model USD1.576467/100,107 calls; pot1399/2500, restoration95,rolling285/3000 at the captured final window,diagnostic12 unchanged.

A and G have three matching expected terminal outcomes and three delivered syntheses. I has three matching terminal outcomes but only two delivered syntheses; the first settlement failure remains preserved. B produces NO_COMPARABLE_PATH on all three against unchanged NO_KNOWN_PATTERN expectations. C holds on the complete-path size bound in all three. D holds on local persistence in all three. E changes TRANSFORMATION_LOGIC -> TRANSFORMATION_LOGIC -> NO_COMPARABLE_PATH; the last Gold quantity was never read after its object guard succeeded and local persistence failed. H changes NO_KNOWN_PATTERN -> NO_COMPARABLE_PATH -> NO_COMPARABLE_PATH. F has an intake refusal, then the retained harmful coverage overclaim, then an unadmitted pause. No fixture-wide stability, exact-contract, complete-replay or demo success is claimed.

E-r3 has14 charged physical requests but13 process receipt rows. Sequence4 has a sealed successful guard response and no original settlement event; a separately hash-pinned ordinary settlement correction preserves the charge and original artifacts, without filling the missing receipt. D-r3 message/error-code absence prevents a proved lock attribution. The rebuilt preflight starts only after original workers drain.


## Rebuilt reader preparation, 2026-10-10

The current-context verification completed at32 of its33 permitted approval probes:15SOURCE,15TARGET and2METADATA. It charged74physical requests, including2prewarm control connections; investigation diagnostics and model calls were zero. A paused-source40613 was retained, followed by a successful connection after a recorded5second wait. This is preparation evidence, not an investigation success. Whole-manifest SHA256d4966050d5a26c18652e41847a34548b3b832c18ff0648b68d1e1569861615a7 and config hash0955d9c025e37bcf625ef299050d3dab6140082a1d408fdabc46f3957d5c7684 stayed unchanged; current enterprise context6f5d1a66-6570-40a4-af9c-8e25311f1a30 and the appended evidence-profile ledger were pinned. The captured window before rebuilt investigations was1473/2500physical,95restoration remaining,359/3000rolling. All24unpaused rebuilt attempts are admitted under the ordinary diagnostic12cap; the three F slots remain unadmitted. First four are in progress, no stability claim.


## Rebuilt pause and dated root correction, 2026-10-10

Eight attempts completed before the operator pause reached a cohort boundary. The second cohort was already admitted, so it drained without cancellation or replacement. Sixteen remaining slots in that batch were not admitted; D and F remain paused on both estates and chat. Original F had one harmful answer-coverage overclaim; rebuilt D has one harmful unsupported technical blocker/role claim. No confident wrong business causal conclusion was identified in this cohort, but hard-zero harmful output is not earned. Original automatic audits and delivered outputs remain unchanged; separate hash-linked root reviews append the correction.

| Rebuilt case | Actual outcome | Answer category | Physical requests | Model calls |
| --- | --- | --- | ---: | ---: |
| A-r1 | TRANSFORMATION_LOGIC | PARTLY_ANSWERED | 11 | 3 |
| B-r1 | NO_COMPARABLE_PATH | NOT_ANSWERED | 2 | 2 |
| C-r1 | HELD / PATH_CONTEXT_LIMIT | NOT_ANSWERED | 0 | 1 |
| D-r1 | NO_COMPARABLE_PATH | NO_REPORTED_FIGURE | 4 | 2 |
| E-r1 | TRANSFORMATION_LOGIC | PARTLY_ANSWERED | 11 | 3 |
| G-r1 | TRANSFORMATION_LOGIC | NOT_ANSWERED | 11 | 4 |
| H-r1 | NO_KNOWN_PATTERN | NOT_ANSWERED | 2 | 2 |
| I-r1 | TRANSFORMATION_LOGIC | NOT_ANSWERED | 11 | 3 |

These are outcome projections, not full sealed-contract passes. USER_SUPPLIED_FORM remains distinct from the old expectation's STATED provenance. No expectation is rewritten to conceal that difference. B's action refers to connection/access although its actual blocker is non-additive compilation; that is a retained detail defect. E's engine-rendered freshness header repeats processing-history facts; freshness remains explicitly unestablished. Neither defect is silently repaired in the historical output.

D's accepted mechanism calls its semantic object L2 while the rendered spine calls it L0. It also attributes the stop to a needed connection field. Native required attestation fields were engine, identity and object, all established; connection was non-required and unattested. The actual refusal is unsupported filtered-scope translation. The defect is two independently derived alias maps plus provider-written engine-status facts, not evidence of a permission failure. A single engine-owned registry and a restriction on provider status assertions are being tested offline. The filtered-scope refusal remains intact.

The eight attempts used52physical requests and20model calls. Current pot1525/2500, restoration95 unchanged, rolling411/3000, modelUSD1.816658/100 with no outstanding dollar reservations at the checkpoint. Approval-time reader verification remains separate:32/33probes,74physical requests,zero model calls. Capture closure resolved2 and3pending files across the two cohorts, conservation confirmed and0blocked; this is capture completeness, not replay proof. Complete rebuilt replay, billing/chat/matrix and immutable publication remain pending. The draft is not merged; demo is not earned.


## Dated CI and verifier correction, 2026-10-10

The 6ce5b4f generator CI failed the unchanged display-label independence test. The new layer registry included local display names in the model payload. The repair keeps the engine alias map shared, sends only role-bearing identity and term data to synthesis, and enriches the local narrative with display names afterwards. The original CI failure is retained. Freshness question headers now render identical engine-owned facts once while retaining every evidence ID; distinct reasons remain distinct. These are generic reporting repairs, not changed ticket expectations.

The second reader verification completed 32 of 33 approval probes with 74 physical requests, including two pre-warm controls, zero investigation diagnostics and zero model calls. The operator pause admitted zero of the 14 planned investigation slots. Captured closing window: pot 1,599/2,500, restoration reserve 95, rolling reads 485/3,000; shared model spend remains USD 1.816658/100. The two legacy verifier captures remain unportable because their bootstrap and external dependencies were not sealed before execution. No retrospective pin or replay pass is claimed.

The isolated prior-source a36cf40 full regression completed 3,043 tests, native exit 0. The in-memory repair check passed 57 tests; its first harness attempt failed two tests by bypassing their patched module references, and that transcript remains preserved. Actual integrated-source verification is reported separately after completion. Today-only model allowances were restored to 600 calls, 8,000,000 input characters and 1,500,000 output-token reservations, with counters unchanged. Restoration changes the whole configuration hash; a fresh budget-only discovery adoption and current-source reader verification are required before rebuilt admission. No identity, permission, secret, golden, oracle or expectation changed. Draft #423 remains draft and the current freeze is invalidated.

Integrated source check:71 tests ran,70passed and one newly added test had a NameError from a missing module alias. The test now uses the existing imported digest function;11 corrected registry/freshness tests passed, native exit0. The unchanged CI regression passed in the integrated run. All initial failures and transcripts are retained. Fresh committed-source full regression and hosted CI remain pending; no full current-source pass is claimed.
