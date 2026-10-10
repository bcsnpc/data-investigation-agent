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
