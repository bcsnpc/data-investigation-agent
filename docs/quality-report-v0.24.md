# Quality of frozen v0.24 — Round 25

Measurement is in progress. No final quality claim or release is made here. The investigator, prompts, models, caching and queries remain frozen to v0.24.

G1 currently has 9 independently double-graded outcomes, all correct; 95% Wilson interval 70.1–100%. Both graders report harmful 0 and full agreement. This is an interim subset of the requested 40 dev cases. Related variants share fixtures, so the Wilson interval is descriptive and does not establish accuracy on independent client estates.

| Cohort | Status | Accuracy |
|---|---|---|
| G1, unchanged v2 dev | 9/40 graded so far | 9/9, Wilson 95% 70.1–100% |
| G2, new held-out v4 — headline | Not started; native fact verification and sealing pending | Not measured |
| G3, unchanged R22 text | Not started; lower priority | Not measured |
| G4, prior R23 held-out v2 — regression | Not started; lower priority | Not measured |

The independent writer produced 60 unsealed drafts, including 12 free-text inputs, six unchanged real screenshots and all three estates. No new held-out wording has been opened. Native fact checks and oracle drafting are still in progress; an unverified scenario will not be sealed or scored.

## Interim measurements

The 9 graded tickets used $3.898022 for investigation, averaging $0.433114 and 26.1 estate requests per ticket. Native Azure job duration, including startup and publication, has median 213.0s and p90 299.0s. Authoring, grading and fixture-control costs are separate and will be reconciled in the final report.

Class results with separate verdict/layer/cause scores and Wilson intervals are retained in [the interim record](runs/round-twenty-five-g1-current-grades.json). No zeros or grader disagreements have appeared in this subset. Final failure groups, walkthroughs, cache usage and ranked next-round fixes await the complete measurement.

## Retained operational failures

The billing control first stopped on a 5-second PostgreSQL advisory-lock timeout before scoring. Its existing native failed job was reconciled and the original pipeline hash restored. The open one-request reservation was settled UNCERTAIN and remains charged. The normal billing bootstrap still returns the pre-existing 2011 CREATE SCHEMA error; it was not repaired. The waiting cohort completed and restored its original pipeline hash. A history precheck SQL timeout occurred before any source mutation; its original receipt remains, with a distinct continuation. A native billing boundary control used the fixture gateway configuration and was correctly denied SQL_CONNECTION_NOT_ALLOWED; one replacement used the existing billing route. No reader permission was broadened, and no scored engine result was retried for these controls.
