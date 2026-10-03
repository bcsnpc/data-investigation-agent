# Question-first probes and per-run reuse

2026-10-03. PR C follows merged #315?#317. No investigation runs, cloud reads,
model calls, config/policy/grant/fixture changes or ledger rows in this PR.
All engine freezes are invalidated.

The declared-context probe runs before its candidate baseline. Admission is per
probe rather than an all-or-nothing pair, so a remaining slot can establish the
requested context even if the baseline cannot run. A partial pair never becomes
a reproduction verdict. Each cap-blocked job retains its target, purpose and what
it would establish; both narratives render those facts. A later presentation
quantity blocked by the same diagnostic cap is retained as a nonexecuted process
receipt, rather than throwing away preceding evidence.

One per-adapter-run cache holds original successful semantic query receipts.
Its key includes the canonical compiled expression, resolved assets, report
binding, context revision/hash, policy and reader. All native probe kinds use it;
reused observations are rebuilt with their own declaration context, while the
original result and receipt remain the read evidence. Failed, truncated,
contradictory or missing-required-field reads are not cached. Distinct compiled
queries remain distinct. No semantic containment or result-equality admission.
Each reuse produces a distinct zero-read event with the prior result and receipt.

Five new tests prove three candidate visuals use one declared read and one
baseline read, declared-first ordering, one-slot partial evidence with the stopped
baseline named in both outputs, all remaining jobs named at zero slots, and reuse
for value-existence and ordinary quantity probes. Older tests that supplied data
by call position now supply it by scope; hostile original-evidence tests still
mutate the declared observation rather than a position. A changed test transport
uses a new run cache, not a silent in-run reread. Targeted reproduction38, cells13,
scoped16, adapter46, procedure43, lower18, failure21 and narrative7 tests are
recorded on the PR along with exact-head CI. Full-suite results follow there.

No planner directory layout or retrieval cap changes. Post-read process evidence
names the skipped work; it is not extra initial estate directory material. PR D
(scoped inventory consumer and refusal-output defects) remains next, then three
unchanged recorded tickets. No live reproduction or acceptance pass claimed.
