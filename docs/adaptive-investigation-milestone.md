# Evidence-led diagnostic investigation milestone

PR #164 is merged. New live sessions additionally require the [shared usage policy](runtime-governance-milestone.md); cancellation and progress controls build on this original milestone.

Implemented in [PR #164](https://github.com/bcsnpc/data-investigation-agent/pull/164), tracked by [#163](https://github.com/bcsnpc/data-investigation-agent/issues/163), following merged PR #162. This adds an adaptive diagnostic loop to the [durable typed runtime](v2-diagnostic-milestone.md). It does not complete the general investigator or causal verification gates.

## What changes

Previously, an operator supplied the entire sequence of actions. Now an operator reviews a scope envelope and the planner selects one admitted candidate at a time. The next prompt includes saved observations and hypothesis updates. The backend owns candidate admission, scope, budgets, dispatch and outcome facts.

Candidates come from the selected catalog measure and its supported dependency graph. Approved dimensions become available after scalar observations. Source tests are explicitly included in the reviewed envelope; their association with a measure is a declaration, not semantic equivalence. There is no metric-name whitelist or fixed native/source order. Context-changing or incomplete dependency analysis leaves a gap instead of pretending child context is valid.

The planner can:

- Select an unattempted candidate for a native scalar, dependency, dimensional or source read.
- Open, refine or reject an unverified hypothesis with references to existing observation IDs.
- Ask a clarification question and stop execution.
- Stop when the remaining admitted tests are not useful.

The planner cannot submit SQL/DAX, alter filters, invent evidence references, dispatch an unknown tool, promote a hypothesis to a verified cause or route a defect. Azure uses the existing configured Responses transport with a new protocol and prompt, not the legacy two-metric planner. The adaptive mode forces one strict decision function with parallel calls disabled, following [official function-calling guidance](https://developers.openai.com/api/docs/guides/function-calling). The adapter still rejects multiple or ambiguous decisions; this callback proposes an action and has no direct execution authority. Legacy text-schema callers retain their existing behavior.

## Durable lifecycle

`READY -> PLANNING -> EXECUTING -> READY` repeats while useful admitted work remains. Terminal/held states include `COMPLETED`, `NEEDS_INPUT` and `HELD`. Completion means diagnostic work stopped, not that a cause was proven.

Before a planner call, the session reserves its attempt and input-character allowance. Before a cloud action, it reserves a call and a stable child-run key. The existing typed runtime persists the actual dispatch and receipt. The session consumes the child receipt into a shared observation history.

Engine, local model context, candidate catalog, connection configuration and planner endpoint/deployment profile are pinned. A changed admission blocks more reads. Provider model-version changes behind an unchanged deployment are not independently proven by this profile hash.

| Interruption | Handling |
| --- | --- |
| Planner response not committed | Explicit recovery holds unknown planner completion; no silent paid retry |
| Cloud budget reserved but no child created | Stable key permits creation only while original admission and deadline remain valid |
| Child created before session link | Recovery finds that same child by its unique request key |
| Child completed before session consumed it | Adopt the saved receipt without another cloud read |
| Remote completion uncertain | Keep the reservation and hold; do not resend |
| Late worker after recovery | Fencing prevents its session commit |
| Scope clarification | Explicitly approved successor session with predecessor/scope reference; no old evidence becomes eligible automatically |

SQL query timeout (-2 at query stage) and native network timeout/error responses retain uncertain completion. SQL 40613 recovery remains limited to the existing connection-stage policy. No changes to SQL tier, free-overage settings or source data.

## Envelope and limits

The envelope contains `model_id`, `revision`, `context_id`, `measure_id`, native `filters`, approved `dimension_ids`, approved `source_tests`, the user's `symptom`, and `limits`.

Each source test contains `measure_id` and an existing catalog-bound source `plan`. All model/context/revision fields must match. Dependency traversal is bounded; dimensions preserve the approved native filters.

Limits are explicit per session:

| Field | Allowed range |
| --- | --- |
| `cloud_calls` | 1-10 |
| `planner_calls` | 1-6, including failed/uncertain calls |
| `wall_seconds` | 60-1800 |
| `input_characters` | 1000-80000 cumulative serialized prompt characters |
| `max_depth` | 0-4 dependency edges |

At most 24 reachable measures, four approved dimensions, eight source tests and 100 total candidates are admitted. Each candidate can be attempted once. Planner payloads are limited to 32000 characters and at most 20 rows per observation; truncation is explicit. Saved facts retain the bounded tool receipt values. Input characters are not a token or billing guarantee. Azure output is capped at 1500 tokens per planner call; actual available usage counts are retained without keys or raw provider payloads.

Before starting a call, sufficient time must remain for the adapter bound: 45 seconds for planning, 120 seconds for native workers, and 300 seconds for the SQL recovery envelope. These checks do not cancel an already-running remote query or establish exact cloud billing. Shared adaptive request allowances are now implemented in the governance milestone; provider-wide spend governance remains pending. This is an explicitly approved local operator workflow, not an unattended hosted scheduler.

## Run and inspect

Use the Python environment containing the existing OpenAI dependency:

```powershell
& .local/llm-env/Scripts/python.exe scripts/run_adaptive_investigation.py `
  --config infra/metadata/development.json `
  --database .local/model-admin-verify/native-diagnostics.sqlite `
  --environment development `
  --envelope .local/reviewed-envelope.json --request-key unique-review-key `
  --azure-settings infra/llm/development.json `
  --usage-policy infra/runtime/development-usage-policy.json --approve
```

`--azure-settings` retrieves the existing resource key through the signed-in local Azure CLI, keeps it in memory, and restores prior environment variables afterward. Alternatively, omit it and use the existing Azure OpenAI environment variables. Never commit credentials or generated session output.

Use `--session-id <id> --status-only` to inspect without any LLM or cloud read. Use `--session-id <id> --recover --approve` for explicit reconciliation; recovery executes at most the already-reserved pending action and then returns. Use `--session-id <id> --approve` to continue a READY session. Include the same planner settings for continued admission.

After a clarification, provide a new reviewed envelope with `--predecessor <old-session-id>`, a new request key and approval. The previous session remains immutable history. The first envelope still requires an operator to resolve metric/filter scope; general business-ticket resolution and screenshot context confirmation are not delivered here.

## Shared evidence and outcome

Admin-authenticated read-only routes:

- `GET /api/v2/admin/models/{model_id}/adaptive-sessions/{id}/business`
- `GET /api/v2/admin/models/{model_id}/adaptive-sessions/{id}/technical`

Both views share the same session, scope, context, facts and outcome hash. Switching projections performs no cloud queries. Technical projection adds scope, decisions and budgets. Business projection adds plain-language status. These are backend projections, not a new deployed UI.

All numeric facts and diagnostic differences come from saved tool observations. A difference between operator-associated native/source values is explicitly non-comparable until proof exists. Hypotheses remain marked unverified. Expected behavior, technical defects, freshness defects and application defects cannot be certified by this milestone. Full context/version/equivalence/causal adapters and authoritative business expectations remain required.

## Verification and remaining acceptance

The focused suite exercises evidence-dependent branching and hypothesis refinement/rejection, source-first plans, dimensional admission, duplicate suppression, clarification successors, shared projections, invalid evidence/tool injection, budgets, changed profiles/contexts, deadline checks, crash recovery, concurrency and uncertain query completion. These tests use injected evidence/planner responses and do not establish frozen-engine live generality.

**Validation:** all 505 script tests passed, including 33 focused adaptive tests. The focused suite is included in CI.

Live session `2787a74c-8505-439f-8eea-065e0093aa9a` completed with two planner calls and two cloud reads. Power BI receipt `56ec69ea-3172-4f59-80bf-028c26750518` returned 100000; SQL receipt `f08eb2a7-4de8-458d-b035-68988c86b9c5` returned 100000. The second planner invocation received the first saved observation and selected SQL. The runtime then stopped with `NO_ADMITTED_TEST`; classification remains `INSUFFICIENT_EVIDENCE`. Recorded planner usage for this successful run is 2113 input and 128 output tokens. This is one smoke run, not a reliability or hidden-generality result. It preceded the final known-failure recovery classification refinement; the normal execution/transport path was unchanged.

Re-executing that completed session changed neither native/source receipt counts nor adaptive event counts. Business and technical projections had identical outcome hash `a9f36acd6640a68b4c7c75006a485ef1e44b17a728e746225cdfa6e41837cfb3`. Local records: `.local/adaptive-live-summary.json`, `.local/adaptive-repeat-proof.json`, `.local/adaptive-regression-final.log`.

The earlier session `67ab9d3b-3de2-408e-9418-f6060bbc0bc1` held after one planner attempt and zero cloud reads. Three additional provider-only diagnostic probes established that the text-schema response contained multiple proposed future actions. The strict single-function protocol fixed the live integration without accepting those ambiguous responses. These diagnostic provider calls are additional to the successful session's recorded usage; their total usage is not asserted here.

 All eight product acceptance families, repeated hidden native evaluations, complete causal verification, authoritative ownership/impact and the unified ticket UI remain pending. F and G now have implementation foundations; their full exit gates are not claimed complete.
