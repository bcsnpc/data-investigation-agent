# Question subjects, separate read budgets and retained stops

Date: 2026-10-03. Autonomous round A2–A4; A5 and the unchanged nine-family
measurement remain pending. Engine bytes changed; prior freezes are invalidated.

Intake nominates a subject from the consumer-owned closed vocabulary and supplies
a verbatim ticket quote; the consumer resolves and validates its span. Current
wire proposals require that subject. Historical/manual contracts remain readable;
an absent subject never authorises reproduction. Unknown subjects are refused.
Route declarations advertise VERTICAL and NONE as implemented and HORIZONTAL as
unimplemented. An unimplemented nomination is held at intake with its reason,
without an investigation planner call or estate read. Intake interpretation itself
still uses one separately recorded model call. A capability-gap walk no longer
falls back to open investigation.

Declared-context reproduction runs for a visual-content question, or after a
blocked walk when a selection and report context are supplied. Freshness and
source-correctness questions without that fallback make no reproduction reads;
the undeclared receipt names their question kind. A visual still establishes its
presentation baseline before the optional reproduction side check. The restricted
probe precedes the undeclared-context probe within reproduction, preserving #318.

The run diagnostic ceiling contains disjoint WALK and REPRODUCTION allocations.
When reproduction is potentially applicable it receives min(4, floor(cap / 2));
the walk receives the remainder. Unused slots are not transferred. Thus cap four
is two plus two, and the configured cap twelve is eight plus four. Without
reproduction, the walk owns the entire diagnostic ceiling. Physical overhead and
the rolling estate allowance still bind independently.

UsageHold is a BUDGET_STOP, never PROCESS_FAILED. A context-local journal retains
original observation objects as produced, including when a procedure does not
return. The stop receipt requires conserved phase/run accounting, the admission
reason and named pending probes; both producer and consumer enforce that shape.
Technical delivery lists retained evidence and the probes not run. The blocker
appears once; completed within-layer cells survive a later walk stop. Genuine
crashes remain process failures. Optional metadata and failure refinement must
propagate a UsageHold rather than consume it as an unavailable finding.

## Context cost and regression

On the recorded E intake payload, adding the subject/route declarations changes
wire payload characters **28,760 → 29,044**. Both views retain five models,
37 measures, 91 columns and nine reports. Intake has no investigation directory
or SQL-object directory; investigation planner payload shaping is unchanged.
The coverage regression tests all twelve synthetic family payloads. Old tapes
and their responses remain unchanged; tests explicitly migrate synthetic responses
to the new wire contract instead of editing the fixtures.

**E and G regressed because a capability was added in front of the walk.**
Reproduction consumed their cap before the lower comparison. The broad exception
handler then mislabelled UsageHold as a process failure and lost walk observations,
although query receipts remained sealed. #330 preserves those runs as they occurred.
The new subject eligibility and sub-budgets address that ordering regression; the
new journal addresses evidence retention. Raising capacity in #331 was not this fix.

Validation: the focused subject/budget tests and migrated intake, reproduction,
receipt and failure tests run offline; full regression and six CI checks are
recorded on the PR. No investigation run, estate request, provider call, fixture
change, permission change or ledger run row in this implementation milestone.
