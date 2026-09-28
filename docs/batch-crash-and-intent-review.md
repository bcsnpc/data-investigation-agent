# Batch crash refusals, intent review and H full-allowance attempt

2026-09-28 UTC. #287 merged as `c4cd6a8` after all six CI checks passed.
This changes the engine, so older freezes do not certify it. Original A-I runs,
receipts, outputs and ledger rows remain unchanged. No filtered lower comparison
was enabled or weakened.

## Defects fixed before capability work

**A: narrative synthesis assumed an assessment existed.** The horizontal run
ended at its four-diagnostic cap without a complete supported assessment. The
Azure narrative-only path copied required fields using unchecked dictionary
indexing, producing a generic KeyError. `narrative_source()` now checks the
complete assessment prerequisite and records BLOCKED with reason
`SYNTHESIS_ASSESSMENT_UNAVAILABLE`, zero synthesis calls and an explicit limit.
It does not let a prose generator classify unfinished evidence or invent support.

The saved A source fails this prerequisite explicitly in a network-disabled
local audit. The new runtime regression verifies no provider call, unchanged
observations, zero synthesis calls and the named refusal. This does **not** make
A complete: the original run still lacks a supported conclusion after its read
cap. The defect was the undisclosed precondition, not a missing field to default.

**C: the resolver's bounded refusal escaped the runtime.** The path was resolved
before the runtime's execution exception handler. `MeasurePathLimit` now names
the measured demand and bound. The runtime catches only that typed refusal,
persists `HELD / PATH_CONTEXT_LIMIT` and a `PROCESS_PATH_REFUSED` event, and makes
no data or planner call. It neither truncates evidence nor raises a budget nor
falls back into another procedure that evades that refusal.

The actual retained C catalog requires **14,813 characters**, against the unchanged
**12,000-character** bound. The saved-context audit reproduced the typed refusal;
the runtime regression verifies its persisted state/event and zero reads/calls.
C therefore still hits a context-capacity limit. This does not establish that a
larger projection would make the derived quantity faithfully comparable; that
would be separate capability work.

The two offline audit rows are appended separately to the ledger. No saved live
session was resumed under a changed engine.

## B, D and I: reasoning reported before classification changes

- **B is mixed:** “looks high” is a mismatch allegation, but its explicit task is
  to explain a ratio's numerator and denominator from definitions. Its selected
  vertical procedure genuinely cannot compile a lower equivalent ratio. Retain
  NO_COMPARABLE_PATH for that failed comparison; do not pretend this answers
  the component explanation. Definition/component decomposition remains missing.
  Relabelling this as a completed business handoff would conceal the unperformed
  technical task. No new ratio implementation or metric-specific route was added.
- **D is a comparison:** a stated North selection versus the global value.
  Filtered lower translation is genuinely NOT_COMPARABLE. Its classification,
  read refusal and compiler are unchanged. That capability still needs building.
- **I is business interpretation:** the meaning of Q49 and its intended effect.
  It was already tagged BUSINESS_QUESTION / NONE at intake, but its inferred
  grouping left zero independent equal comparisons. The generic vertical fallback
  misdescribed that question as a comparison task. Business-shaped questions now
  return NO_KNOWN_PATTERN when flow consistency cannot be verified, explicitly
  naming verified flow as the missing prerequisite and retaining unknown meaning.
  When the checked flow agrees, the existing BUSINESS_QUESTION handoff applies.

I cannot truthfully be relabelled BUSINESS_QUESTION on its old evidence: that
outcome requires a successful equal independent boundary comparison. This guard
was retained, not weakened. New tests cover single-layer and uncomparable business
paths, equal-flow specialist handoff, and the unchanged mismatch refusal. No
business code/name detection or scenario mapping is used. No intake prompt or
schema was changed. The underlying intent-routing limitation remains: the engine
cannot yet answer B's component request or I's meaning from business authority.

The context directory, initial planner payload and wire schemas are unchanged;
no per-entry context text was added. New refusal diagnostics are local records.
A changed business outcome is reflected in its existing conclusion contract,
not in an expanded retrieval directory.

## Family E: interpretation and original outputs

The original E output is a qualified mechanism finding, not a freshness answer.
It describes a left-join mechanism at a real divergent boundary, while explicitly
leaving matching snapshots and actual duplicate matches unestablished. It never
establishes an SLA violation or how old the served value is. Treating its
TRANSFORMATION_LOGIC label as completion of E's freshness task would change the
subject. Its original business and technical outputs are retained verbatim in
[runs/nine-family-E-business.txt](runs/nine-family-E-business.txt) and
[runs/nine-family-E-technical.txt](runs/nine-family-E-technical.txt), and pasted
verbatim in the user-facing report. They were not regenerated.

## H: new single attempt

The user withdrew the relative-cost guard and granted the same allowance as
A/E/G: 16 physical credits, one new session, six-hour expiry, four diagnostics,
existing 12 investigation calls, and ordinary allowance 60. The original HELD H
run stays unchanged. This is a separately authorized attempt, not a refill.

New run **7a591ed4-8516-4633-901a-7d48a5eb7459**, 04:29:25-04:38:12 UTC:

| Item | Actual / cap |
| --- | --- |
| Diagnostic operations | 2 / 4 |
| Physical requests | 2 / 16 |
| Guards / guard reuse | 0 / 0 |
| Investigation planner calls | 7 / 12 |
| Intake / synthesis provider calls | 1 / 0 |
| Total recorded provider requests | 8 |
| Runtime state / stop | COMPLETED / NO_PROGRESS |
| Outcome | UNRESOLVED |
| Synthesis | BLOCKED / SYNTHESIS_ASSESSMENT_UNAVAILABLE |

Both reads were native DAX as the isolated reader on the same selected model;
there was no source read, independent boundary comparison, snapshot verification,
or definition-judge call. The first read returned Inbound=6,425, Outbound=2,340,
Handled=8,765 and Balance=4,085. The second read grouped movement types. These are
native observations, not a validated expected-behavior conclusion or business rule.

Five rejected steps are preserved, in order:

1. `Decision contract rejected: Unknown assessment evidence`
2. `Contribution query must read the declared upstream object`
3. `Decision contract rejected: Unknown assessment evidence`
4. `Decision contract rejected: Recommended action does not match outcome`
5. `Decision contract rejected: Unknown assessment evidence`

The last three were uninformative and triggered the existing no-progress stop.
No diagnostic, credit, planner-call or deadline cap was raised. There is no H
relative-cost guard in this attempt. Synthesis made zero provider calls and now
states the missing-assessment prerequisite explicitly rather than recording a
KeyError. No validated output pair exists; none was regenerated or substituted.
This is a useful negative result: physical capacity was available, but the
planner did not produce a valid supported conclusion before no-progress refusal.

The new 16-credit grant was recorded before the first estate request, with
before/granted/after readbacks. **Two charged; fourteen unused; expiry
2026-09-28 10:29:25.031124 UTC.** Credits were unexpired at report time and cannot
be used for another attempt. Config, profile, policy and ticket hashes matched
before/after. Tested engine fingerprint:
`a7cba971e9ea895daf43d52fa3dce68f2d8592af18c7a635305d5e8dbd612530`.

[Structured H evidence](runs/H-full-allowance-result.json) includes the grant,
counts, recording IDs, refusal reasons and original DAX receipts. Local artifacts
remain under `.local/H-full-allowance-20260928/`; all eight request/response tapes
are preserved. One new live ledger row was appended, alongside the two offline
A/C audit rows. No prior row or session was edited.

## Validation

The full unittest runner reported **1,319 tests passed** in 472.787 seconds.
PowerShell returned a nonzero wrapper status while redirecting ResourceWarnings;
the full original log is preserved at .local/batch-crash-regressions.log.
The focused synthesis suite passed 32 tests and the final process suite passed
43 tests. Offline saved-input audits made zero provider or estate calls.
