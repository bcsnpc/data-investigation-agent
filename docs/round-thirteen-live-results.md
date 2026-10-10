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
