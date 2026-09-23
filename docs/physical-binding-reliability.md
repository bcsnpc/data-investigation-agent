# Compiler binding and physical-context reliability

2026-09-23. Issue #199; follows accepted #218. Known-domain work only.
Implementation and evidence: [PR #219](https://github.com/bcsnpc/data-investigation-agent/pull/219).

## Decision and scope

The stopping-contract hypothesis was evaluated and rejected. Its proposed fields,
method and negative results remain in [the review record](stopping-criteria-review.md).
No completion-basis/reason field or experimental stopping instruction is adopted.
This change addresses compiler correctness, rejection feedback and physical
membership only. There is no required SQL step, connection preference, query
rewrite, scope expansion, permission change or cross-system adapter.

## Compiler correction

The SQL compiler now reuses a binding for an identical typed literal, keeping text,
integer and decimal values separate. It preserves original expressions, so repeated
SELECT/GROUP BY CASE expressions retain identical bound forms. The old 60 literal
occurrence limit remains, as do all other admission limits. Validator version is
bounded-tsql-v3. Saved receipts and historical runs are not rewritten.

The exact G call-10 proposal is retained as a regression fixture. Tests compare
its qualified CASE expression to the parameterized expression with literals
restored only in test code, assert identical SELECT/GROUP BY bound forms, and
check type/value separation. Offline recompilation against the actual saved
candidate and pinned catalog succeeds with four parameters instead of ten.
No live read was used to confirm this deterministic fix. Receipt:
`.local/physical-binding-20260923/G-recompiled.json`.

## Rejection feedback and physical membership

Complexity errors retain the measured SELECT/join counts and caps. Unavailable
object errors identify the searched approved SQL connection/schema, requested
object, a bounded list of same-name catalog retrieval targets, and a scoped search.
Hints never choose a replacement name or establish identity by name equality.
Cross-connection candidates explicitly cannot be joined through this SQL path;
separately authorized reads may be compared with equivalence limitations.

Search results, asset/child lookups, definition excerpts, semantic context, domain
profile tables and directory entries identify physical ownership and known schema.
An unobserved schema remains UNKNOWN; lakehouse names do not imply dbo or an
established SQL endpoint. Compaction preserves binding labels and actionable
rejection fields. Advertised SQL capability identifies its actual configured
connection and approved schema. Existing execution admission remains authoritative.

Offline replay of F calls 10/11, G call 6 and I call 6 confirms that original
queries stay rejected and unchanged while feedback becomes actionable. F/G
complexity reads SELECTs 9/8 and joins 3/4. F receives exact catalog hints; I sees
Fabric ownership instead of an implicit Azure SQL binding. E's accessible notebook
history remains present after projection. These checks execute no data tools.
Receipt: `.local/physical-binding-20260923/rejection-replays.json`.

## SELECT-count review

The cap stays at eight SELECT nodes and four joins. CASE expressions themselves
do not add SELECT nodes. The recorded F/G proposals exceeded the cap because of
nested SELECTs (CTEs/scalar subqueries), not CASE branches alone. These are
structural-complexity guardrails, not reliable estimates of resource cost: row
counts, indexes, selectivity and execution plans are not represented by this count.
One SELECT can scan a large table; several small subqueries need not be expensive.
There is no measured execution-cost basis here for raising the cap, and it was
not tuned to admit F/G. No new live cost experiment was performed.

## Validation and re-baseline

Six focused binding/feedback tests, 36 flexible-query tests and nine projection
tests passed. The first full-suite run caught a missing-SQL-configuration error
in capability display (1 error in 1,008 tests); the display now leaves absent
connection/schema unknown, and all nine domain-profile tests pass. The final
full-suite rerun passed all **1,008 tests** in 362.588 seconds. Two generator tests
pass; 63 local documentation targets resolve and the staged secret scan is clean.

The completed re-baseline is E/F/G/I plus two extra G trials, under the same model,
profile, generation settings, catalog, policy and serial 65-second pacing as #218.
Every attempt is recorded and labelled KNOWN_DOMAIN_REGRESSION, with its own
ledger row. Deployment readback confirms GPT-5.4 2026-03-05, GlobalStandard 100
units, 100,000 TPM / 1,000 RPM. No configuration changes are needed or made.
Counters, reservations and deadlines remain intact. No freeze, fresh variant or
unfamiliar-domain claim follows. Original F-paced and baseline F remain failed.

## Six live results: source investigation did not improve

The engine stayed at commit `2b1a908`, runtime fingerprint
`67ad1260b9c6bb9cde70cf2ae426c568001548cd566da882da37a46fdac2c096`.
All six used the existing e1b8e1 tickets, catalog context
`ffbc0be4-225a-47d9-a280-4c0a456646d6`, GPT-5.4 2026-03-05, medium reasoning,
8,000 output tokens, 48,000 per-call input characters, 120-second provider timeout,
one allowed metered connection recovery, serial 65-second pacing and recording.
The existing 12-call / 6-cloud / 384,000-input-character / 1,800-second run limits
were unchanged. No live read was run solely to verify the deterministic SQL fix.

| Trial | Planner calls | SQL reads | Native reads | Lookups (distinct) | Local rejections | Stop | Wall seconds |
| --- | ---: | ---: | ---: | ---: | --- | --- | ---: |
| E | 6 | 0 | 0 | 5 (5) | 0 | TOOL_UNAVAILABLE | 473.859 |
| F | 9 | 0 | 2 | 4 (4) | 3 DAX member | NO_PROGRESS | 610.972 |
| G1 | 12 | 0 | 1 | 7 (7) | 4 DAX member | BUDGET_LIMIT | 831.001 |
| I | 11 | 0 | 2 | 7 (7) | 0 | ENOUGH_DIAGNOSTICS | 1,489.558 |
| G2 | 10 | 0 | 2 | 7 (7) | 1 DAX member | BUDGET_LIMIT | 704.854 |
| G3 | 5 | 0 | 0 | 3 (2) | 2 DAX member | NO_PROGRESS | 358.811 |
| Total | 53 | 0 | 7 | 33 (32) | 10 DAX member | Five unresolved; I business context required | 4,469.055 |

Reads count successful receipts only. Every row has zero hypothesis-ID, text-bound,
schema-prefetch and other repairs, zero redundancy refusals and zero result-equality
overlap. The rejection breakdown is zero schema-contract, prerequisite, redundancy
and complexity rejections, with ten `other` rejections, all specifically unknown
DAX members. No measured complexity error occurred live. The offline F/G replays
retain SELECTs **9/8** and joins **3/4**, proving the new feedback without claiming
that a live planner used it. One SQL proposal (E) was admitted and failed at query
execution; 0/1 local SQL rejection is not a source-execution success rate.

E again queried `app.dataset_runs` after inferring an unestablished link from a
semantic-model ID. SQL cold-start error 40613 triggered the existing connection
retry; query error 229 then held the run. Its available notebook history did not
prevent the unsupported registry assumption. No grant was added.

**F did not establish the upstream mechanism.** It reproduced Extended Value
57,043 and observed 406 native rows versus 360 distinct movement IDs (46 excess
rows), then failed three proposed DAX diagnostics. Offline parsing of the exact
saved proposals stops at calculated aliases `[Row Count]` / `[RowCount]`.
The current binder resolves catalog members, not these virtual-column references.
This is a concrete supported-grammar/feedback limitation; the data hypothesis was
not disproved. No source read tested the join mechanism. F stays FAILED/UNRESOLVED,
alongside the preserved original baseline F and F-paced failures.

I reached BUSINESS_CONTEXT_REQUIRED. Its two native reads showed current measure
behavior under reason-code filters and an explicit movement-ID selection, while
its explanation kept Q49 meaning and intended inclusion rules unknown. No
cross-system SQL join was proposed. This is a supported limited answer, not
verification of business intent. One `APIConnectionError` was recovered through
the existing charged recovery; all other trials had zero provider errors. A
45-second evaluator wait returned after 782.003 seconds during I, consistent with
an unexplained host scheduling/suspend delay. The cause is not established. I's
actual wall time is retained without subtraction, deadline extension or replacement;
it is not a clean latency comparison. See local `wait-anomaly.json` and recordings.

## G variance and comparison with #218

G's three fresh sessions produced **1, 2 and 0 successful reads**, respectively,
all native and no SQL. Planner calls were **12, 10 and 5**; local DAX rejections were **4, 1 and 2**.
Two stopped at BUDGET_LIMIT and one at NO_PROGRESS; all remained UNRESOLVED.
Wall time ranged from 358.811 to 831.001 seconds. G1/G3 rejected calculated aliases
`[activity_rows]` / `[adjustment_rows]`; G2 rejected an unqualified `[movement_id]`
reference in a virtual-table expression. Exact queries and failing tokens are
retained in the local DAX audit. G2 obtained useful native adjustment/movement
observations, but no trial inspected the requested live SQL source entries.
Three samples show materially different paths and a recurring source-read gap;
they do not estimate a reliable success probability.

| Metric | #218 full nine-family baseline | #218 E/F/G/I | New E/F/G1/I | All six new trials |
| --- | ---: | ---: | ---: | ---: |
| Planner calls | 51 | 34 | 38 | 53 |
| Successful SQL / native reads | 3 / 11 | 3 / 4 | 0 / 5 | 0 / 7 |
| Retrieval / test proposals | 22 / 22 | 19 / 15 | 23 / 13 | 33 / 18 |
| Local rejections | 8 | 6 | 7 | 10 |
| SQL proposals / local SQL rejections | 9 / 4 | 9 / 4 | 1 / 0 | 1 / 0 |
| Schema-prefetch repairs | 2 | 2 | 0 | 0 |
| Redundancy refusals / result overlap | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Provider errors | 0 | 0 | 1 | 1 |
| Planner input characters | 1,261,082 | 961,138 | 1,203,732 | 1,693,697 |
| Reserved planner output tokens | 408,000 | 272,000 | 304,000 | 424,000 |
| Summed wall seconds | 3,678.879 | 2,426.119 | 3,405.390 | 4,469.055 |

The matched four-family comparison avoids treating repeated G trials as extra
coverage. Wall times include intake and I's timing anomaly, but exclude between-run
pacing. Planner-call totals include the recovered failed provider attempt; retrieval
and test counts count returned decisions. #218's two schema-prefetch repairs create
two extra context observations beyond its 22 planner retrievals. The new batch has
eight cloud reservations: seven successful reads plus E's failed read. None were
refunded. Fewer SQL rejections here reflect fewer SQL proposals, not proven better
query selection or admission. The compiler fix remains independently established
offline; SQL proposals did **not** produce successful source reads in this batch.

## Measured context cost and remaining findings

Ownership labels consume the existing directory budget. In recorded F call 1,
directory entries fell from **28 to 11**, including SQL object entries from **11
to 3**. Both requests expose directory truncation, and catalog search still covers
the same approved estate. The pre-wire payload grew from 14,441 to 17,364 characters;
recorded request size grew from 27,902 to 31,236 bytes. This is a measured retrieval
coverage tradeoff, not proof that the labels caused the changed action choices.
No context cap or presentation was changed during the six trials.

The remaining evidence points are virtual DAX reference binding/actionable grammar
feedback, repeated failed test selection, directory representation cost, and E's
unsupported freshness-registry assumption. They are findings for review, not
implemented follow-ups. The stopping-contract experiment remains evaluated and not
adopted. Work stops after this report; no freeze, variant or unfamiliar-domain claim.

## Audit trail and policy readback

| Trial | Session ID | Local result suffix under `.local/unknown-domain-v4/runs/` |
| --- | --- | --- |
| E | `991d1a3c-b033-4b61-941e-512a617bf4aa` | `E-physical-binding-20260923-1.json` |
| F | `1dae46fa-2891-40ca-b47d-024c7d63786f` | `F-physical-binding-20260923-2.json` |
| G1 | `45ce4a4e-40c9-40c9-8b22-ebd16b965d0c` | `G-physical-binding-20260923-3.json` |
| I | `68e232a1-f630-422b-9dcd-8957eb64ef43` | `I-physical-binding-20260923-4.json` |
| G2 | `25d6c073-f248-413f-bdca-7608e1328cb4` | `G-physical-binding-20260923-5.json` |
| G3 | `24dd8975-5aea-4645-a9c2-0064824804bb` | `G-physical-binding-20260923-6.json` |

All 53 recorded planner calls load with recording hash verification. The prior 111
ledger rows remain unchanged; exactly six unique rows were appended, one per trial,
with rejection detail fields. Runtime fingerprint, generation settings and daily
policy stayed constant. Usage records increased from 399 to 466 (six intake calls,
53 planner attempts and eight cloud reservations). Final UTC-day reservations are
129 planner calls, 24 cloud calls, 3,856,655 input characters and 934,500 output tokens;
limits remain 240 / 60 / 8,000,000 / 1,500,000. No reservations remain active and no
usage violation is recorded.

Before/after readbacks confirm unchanged GlobalStandard 100, 100,000 TPM / 1,000 RPM
and GPT-5.4 2026-03-05. No configuration, permissions or SQL free-limit settings
changed. Local evidence is under `.local/physical-binding-rebaseline-20260923/`:
`manifest.json`, `summary.json`, `comparison.json`, `postflight.json`,
`capacity-after.json`, `dax-rejection-audit.json`, `context-size-comparison.json`
and `wait-anomaly.json`. Pre-run capacity receipt:
`.local/physical-binding-20260923/capacity-readback.json`. Raw tapes remain local;
[the ledger](runs/ledger.jsonl) contains the content-free per-run counters.

Final evidence validation: 204 local documentation targets resolve, `git diff --check`
passes, and the staged evidence secret scan is clean. No dedicated browser session
was rerun locally. PR #219 tracks CI and merge state for the final documentation head.
