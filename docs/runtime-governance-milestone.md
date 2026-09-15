# Governed adaptive runtime milestone

Tracked by [#165](https://github.com/bcsnpc/data-investigation-agent/issues/165), after merged PR #164. This groups shared usage controls, cancellation, receipt recovery, progress stopping and operator interfaces in one change. It does not add causal proof or change Azure SQL billing configuration.

## Shared reservations

New live Azure adaptive sessions require an explicit `--usage-policy`. The supplied [development policy](../infra/runtime/development-usage-policy.json) allows, per UTC day, 12 planner attempts, six cloud read actions, 150000 serialized payload characters and 18000 reserved output tokens. It permits one locally active planner reservation and stops after two consecutive observations without nonblank metric values.

The ledger is shared by governed adaptive sessions using the same catalog database and environment. New request keys and clarification successors do not reset it. Policies must match the configured environment; their hashes are pinned into each session. A policy change invalidates active session admission.

A planner reservation charges one attempt, its dynamic payload size and the full 1500-token output allowance before calling Azure. A cloud reservation charges one action before creating its child run. Ledger reservation and session transition commit together under the SQLite write transaction. A stable reservation key cannot be reused with another amount.

Reservations are never refunded, including cancelled, failed and uncertain work. Actual available token counts are retained separately. Reported output above the reservation records a violation and blocks subsequent reservations that UTC day. A new UTC day starts a new bucket without deleting history.

These are **request allowances, not verified provider spend or SQL compute caps**. Character counts cover the dynamic serialized payload, not system instructions/schema or exact token billing. SQL connection recovery remains one admitted read with separately retained connection attempts. Other tools, old ungoverned sessions, other catalog databases and manual portal activity are outside this ledger. Free-overage settings, service tier and source data are unchanged.

The concurrency limit bounds locally reserved planner work. Explicit recovery/cancellation records uncertainty and releases local ownership; it cannot prove that a remote provider stopped processing. Reservations are not erased or automatically replayed.

## Cancellation and recovery

Cancellation is a durable state transition, not a promise to terminate an already-running Azure request.

| Timing | Behavior |
| --- | --- |
| Before planning | Mark cancelled; no planner call |
| During planning | Fence the late response so it cannot dispatch an action |
| Before child creation/link | Cancel a child that appears in the race window before dispatch |
| Child created, not dispatched | Cancel the child; normal admission rejects execution |
| Remote read dispatched | Fence commits, retain outstanding uncertainty and prevent silent replay |
| Terminal receipt later available | Explicit reconciliation adopts it for history while keeping the session cancelled |

History remains readable. Repeated cancellation and receipt adoption are idempotent. Unknown completion stays held at the dispatch boundary. A known failed query remains a known failure.

## Progress stopping

After the configured number of consecutive completed observations without nonblank metric values, the runtime stops with `NO_PROGRESS`. Empty groups and all-BLANK metrics count; a dimension label alone does not. Zero is informative. A nonblank observation resets the counter.

This is a conservative stop, not proof that no further explanation exists. Equal values on different assets are not collapsed. Candidate uniqueness, depth limits, session budgets and deadlines still apply. No verified cause follows from this stop.

## Operator controls

Add `--usage-policy infra/runtime/development-usage-policy.json` to approved live adaptive runs. The existing CLI supports these mutually exclusive controls alongside its usual configuration, database and environment arguments:

- `--usage-status --usage-policy <path>` inspects the local ledger without Azure key retrieval, LLM calls or data reads.
- `--session-id <id> --cancel --approve` cancels a session without fetching an Azure key.
- `--session-id <id> --reconcile-cancelled --approve` adopts an already captured terminal receipt without restarting work.

Usage-limit holds do not auto-resume. A separately approved session still shares the ledger. Completed histories can be inspected without a policy; new live sessions cannot omit it.

The local admin host supplies a control-only controller with no planner/query transports. Its `--usage-policy <path>` option enables ledger visibility. Admin routes are `GET /api/v2/admin/usage` and `POST /api/v2/admin/models/{model_id}/adaptive-sessions/{session_id}/cancel` with an empty JSON object. Reader credentials cannot use them. Model/session scope is checked first. There is no new execution endpoint, browser control or Azure deployment.

## Verification and remaining work

The focused suite covers shared limits, output reservation/overrun, UTC-day rollover, policy changes, missing live policy, uncertainty accounting, concurrency, atomic rollback, idempotent keys, cancellation races, receipt adoption, no-progress stopping and admin authorization. All **528 script tests passed**, including 23 focused governance tests, now included in CI. Operator entry-point syntax checks passed.

Live session `72e6bd71-c9ea-471d-bf0d-816bcf42ea73` used two Azure planner calls and two successful reads, each returning 100000. The UTC 2026-09-15 ledger recorded two planner reservations, two cloud reservations, 3660 payload characters and 3000 reserved output tokens; all four reservations settled. Repeat execution added no receipts or reservations. Queued session `24002312-b885-4d50-9758-06e6a5606286` was cancelled without a cloud call. Local evidence is retained in `.local/governance-live-evidence.json` and `.local/governance-regression.log`. No defect or expected-behavior classification was certified.

Remaining major work: authoritative context/version/equivalence and causal proof, frozen-engine native generality acceptance, and the complete ticket workflow with reviewed routing. Provider-wide monetary governance and distributed multi-catalog enforcement are not delivered.
