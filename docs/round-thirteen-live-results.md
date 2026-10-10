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
