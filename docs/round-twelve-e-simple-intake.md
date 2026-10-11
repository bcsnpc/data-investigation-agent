# Round Twelve E — accounting, live unblock and shared questionnaire

2026-10-10, America/Chicago. Draft #423; earlier failures, oracle, goldens and expectations remain unchanged. No identity, permission or secret changes.

## Section 0 evidence

A1 is complete and pushed in [the verbatim amendment record](oracle-amendment-a1.md). Each of original A-mention, E-mention and G-mention explicitly says “The global Handled Quantity currently shows 8765.” Old figure state NOT_STATED became NUMBER 8765 / EXACT, with the original ticket span preserved. Only those three reported-figure fields changed. New oracle SHA-256 bc2819f1ab12ae93d2203a519a6318a6f9ecbc1a3220a466e664a00c495a9a6b; old be029b56a6de27195dac507bfb5010f0ce7abc2732702d9a230e5f4a8d38406c retained superseded.

| Recorded output group | Old settlement | A1 settlement | Old harmful | A1 harmful |
|---|---:|---:|---:|---:|
| Dev complete |27/28|28/28|1|0|
| Held complete |18/21|20/21|2|0|
| Dev skipped |4/5|4/5|0|0|
| Held skipped |2/2|2/2|0|0|
| Dev controls |4/12|4/12|0|0|
| Held controls |1/7|1/7|0|0|

These are retained-response re-scores, not fresh held-out runs. The [billing review file](billing-unplanned-tickets-for-review.md) is already committed and pushed: independent07-12 verbatim, Recent Collections error and blank Top Accounts described, exact causes unproved. No sealed-defect inventory appears there and no billing investigation follows this step.

## Reservation correction

The old governor deliberately charged every full output reservation for the UTC day even after settlement. All274 today's calls have retained actual usage:198,965 output tokens, versus1,899,500 gross reservations. Zero active reservations, zero unknown output charges. DECIDED WITHOUT REVIEW: the problem is the conservative cumulative charge, not an unreleased in-flight latch. Derive admission from actual settled output plus active bounds. Preserve immutable reserved/actual rows and expose gross, charged and active totals separately. Missing usage after error/timeout keeps its full bound; do not infer zero cost. Calls and transmitted input characters stay charged, and real overruns remain VIOLATION with the existing acknowledgment/guard. No output allowance increase:1.5M remains sufficient.

Accounting version3 records this change. Historical accounting1/2 tapes retain conservative admission when replayed; their bytes and pinned producer contracts are unchanged. Synthetic tests cover actual-output release, error/timeout without usage, idempotency, admission against active work and retained real-overrun refusal.

## Session budget and discovery controls

Human approval: “approve to whatever limits we can increase for this session run”,2026-10-10. Bounded round ceiling1,500 ->1,800 for this session only; reserve95, rolling3,000, diagnostic12, model600calls/8Minput/1.5Moutput unchanged. Reason:18runs upper physical estimate288 exceeds ordinary remainder255;300 extra session slots cover that difference and live-list controls. Original manifest and approval bytes preserved; restore afterward with counters intact. This is not permission to bypass a cap or refill a failed run.

The original models were disabled by our rebuild's discovery projection: enterprise_discovery.publish disables enabled models absent from the scoped collection, incrementing revision without a separate disable event. Original model5b3eff46 last DISCOVERED_CONTEXT revision32 was enabled on2026-10-08T02:08:46.604774Z; the rebuilt-only collection then left revision33 disabled. The platform identity and permissions did not disable it. The retained original scoped inventory is explicitly readopted under the current configuration; this creates a new approval/context and re-enables original discovered definitions, without changing an estate grant.

Before adoption, the operator checks exact adapter options, identities and declared layer/resource access against their previously approved manifest. Any difference creates discovery-policy-diff.md and stops adoption. This is reapproval of unchanged retained definitions, not new metadata collection or proof of current serving. Live reader probes must still attest every read. Original/rebuilt phases are sequential because they share a catalog; each phase adopts its own approved scope before intake. Prior contexts and all failed attempts remain unchanged.

Full regression, live results and the new questionnaire remain pending at this preparation checkpoint. No fresh held-out pass.

## Section 0 and live unblock checkpoint, 2026-10-10

The full regression on frozen c377331 ran2,860 tests in872.011 seconds:2,859 passed and one obsolete test expected permanent full-reservation charging. Its corrected assertion checks gross and actual charging separately; all33 governance tests passed. Original failed log retained. Questionnaire source validation is separate and still running.

All18 live forms were attempted once. 16/18 delivered findings; the two C attempts retained `Conflict: Saved synthesis has no assessment` after completed deterministic registered-refusal synthesis. This is a delivery defect, not a missing refusal receipt. Offline validation of C's original state under the fix now yields HELD with no invented assessment and the original receipt untouched. No C replacement run occurred.

Fixed expectation scoring: 9/18 expected outcomes earned; exact structured contracts 0/18. Text-ticket expectations carry STATED report provenance; submitted forms correctly carry USER_SUPPLIED_FORM. That common difference is reported, not normalised away. Original B/H and rebuilt B return NO_COMPARABLE_PATH instead of the historic NO_KNOWN_PATTERN; rebuilt H matches NO_KNOWN_PATTERN. The rebuilt serving-only runs stop at the serving boundary because the selected lower binding's recorded verifier includes SAMPLE_MISMATCH; they cannot inherit the historic TRANSFORMATION_LOGIC expectation. No binding or expectation was changed to obtain a pass.

Investigation requests 100; retained receipt accounting reports 44 diagnostics and 42 guards. Both zero-request C refusals have no diagnostic receipt counter, recorded as unavailable rather than defaulted. Models: 38 calls and 316149 transmitted input characters. Each case's cost, wall time, unchanged expected projection and exact differences are in [the live table](round-twelve-e-live-results.md) and [structured record](round-twelve-e-live-results.json). Time includes durable capture, not just cloud latency. No run reached diagnostic cap12.

Two application pre-warms each used two physical controls, separately recorded as controls with diagnostic count0. Including those four, the pot moved1,150 to1254/1,800; reserve95 intact. Temporary1,800 restoration remains due after this session's remaining dev work; rolling3,000 and model600calls/8Minput/1.5Moutput remain unchanged.

Retained approvals, zero metadata requests: original context b8d15e64-a003-41bf-924a-0ab9006599d0 pins config b240cef651374de86fbf2d43708d412641097e1ee40071eb5122eda550460661; rebuilt context2f662903-b06e-407e-b5a1-de1eaded8968 pins adebadf73fe62d6f8cab4001a9081e6cd95804767fc4bcf2eb6e15dafe721c33. Scope checks passed before each approval. These are approvals of unchanged retained definitions, never recollection or proof of current serving.

The live expectation gate did not pass, so an owner-unaided successful demo is not claimed. Questionnaire implementation and fresh dev-only scoring continue; held-out and billing are untouched. Draft423 remains draft and prior freezes are invalid.

## Questionnaire and final session report, 2026-10-10

The shared questionnaire now drives web/chat/API, with retained submitted facts,
progress, ticket links, discussion, reviewed screenshot replies and existing
close/reply/handoff paths. See [the schema](intake-schema.md). The isolated browser
checks exercised web and chat submissions, reopening their ticket page and a
retained comment. They made no estate/provider requests; no owner-unaided live
acceptance is claimed. Live visual titles remain a named access gap; approved
retained titles are labelled. Cross-report/page investigations hold rather than
substituting a one-report walk. Optional source values remain separate user claims.

Fresh questionnaire dev first pass: complete5/28 zero-question settlements,
6questions,3illegitimate,16harmful; visual-skipped0/6,1question,1illegitimate,3harmful.
The generic Nothing-route correction removed harmful admissions. Frozen corrected
pass: complete24/28,1question,1illegitimate,0harmful; skipped4/6,0/0/0. After the
picked-comparator guard, one fresh affected H-noisy attempt settled. Final affected-
dev combined column: complete25/28,skipped4/6; zero questions, illegitimate questions
and harmful admissions in both;12unmappable records. It combines45 unchanged rows
from1e1fb33 and one fresh row from02cff87, not a new full frozen pass. All originals
and tapes retained. [Full dev table and refusal reasons](round-twelve-e-questionnaire-dev.md).
Held-out, oracle, goldens and expectations unchanged; no billing runs.

The frozen questionnaire full suite passed2,877 tests in1,064.243seconds. Final
source02cff87 passed159 focused tests in30.722seconds, including wrong-cell guards.
The earlier full2860 result with its obsolete assertion and the corrected33test
result remain recorded. No claim that the2877run covered the subsequent guard.

Both manifests restored from1,800 to1,500. Reserve95,rolling3,000,diagnostic12,
model600calls/8Minput/1.5Moutput unchanged. Counters retained. Pot1,150->1,254/1,500,
net151 outside reserve; rolling137->241/3,000. Session actual104 physical requests
(100investigations+4prewarm controls); dev0estate reads. Session116model calls,
1,317,628input characters,85,692actual output tokens. Daily390calls,4,784,121input
characters,284,657actual charged output versus2,710,500gross reserved; zero active
reservations and zero unknown output charge. The original acknowledged violation
and real-overrun guard remain. No identity, permission or secret changes.

Restoration first re-used the old discovery idempotency key and correctly refused
with `Conflict: Scan key policy differs`. The original manifest was already
restored; no estate request occurred. Retrying under a config-hash-qualified key
completed unchanged-scope retained reapproval. Previous contexts and approval
records preserved, not edited. Restored original context0bc41d66-4fd8-4902-8931-d5609cd8d615
pins c9a27319e94d12e27ba797104a3b31f072d98f7302b1666f18937c91c93b65c0;
rebuilt context73852267-63fb-4e2d-ac57-288a249979da pins
5e2a45cb0d9c21d688d8f1aec6f7cd4e56dab01638e4139aac3af30dab58d3b7.
This is zero-read adoption of retained definitions, not recollection.

DECIDED WITHOUT REVIEW: a declaration of no specific comparator cannot become a
wrong-number claim. An unresolved description cannot cause that selected field to
be asked again; the safe result is refusal, with original picks retained. The
rejected alternative guessed a complaint route and caused the first dev harms.
The failed separate-worktree dev startup lacked its local Python path and made
zero provider/estate calls; it remains preserved. Source line-ending alignment
before the frozen dev run changed no normalized content; earlier bytes and its
record are retained locally. No live fixture or expectation was adjusted.

The live gate remains failed:16/18 delivered,9/18 outcomes,0/18 exact contracts.
The [demo handoff](round-twelve-e-demo-handoff.md) lists the available launcher and
remaining gaps; a successful unaided demo is not ready. #423 remains draft and
prior freeze invalid. No merge and no replacement live attempts.
