# Planner settings and investigation reliability

2026-09-18. Research and evaluation supporting issues #193 and #199.
Current delivery claims belong in [current status](current-delivery-status.md).

## Research and decisions

[OpenAI evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
separates tool selection, argument correctness and final outcome quality. We now
compare next-action proposals on identical saved context before paying for another
full investigation. This is diagnostic evaluation, not unfamiliar-domain acceptance.

[GPT-5.4 documentation](https://developers.openai.com/api/docs/models/gpt-5.4)
identifies `none` as its default reasoning effort. Our existing adapter omitted
an explicit setting. We test `medium` against `none` rather than assuming that
changing model names or adding prompt rules will solve test selection.
[Azure reasoning guidance](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/reasoning)
explains that reasoning and visible output share the output-token limit. Therefore
the experiment uses 4,000 output tokens, with the full allowance reserved before
each call. This is an opt-in experiment; the default mini deployment is unchanged.

[OpenAI latency guidance](https://developers.openai.com/api/docs/guides/latency-optimization)
describes the latency cost of output generation and repeated requests. More
reasoning can cost latency; our evaluation records duration and token usage.
The configurable 120-second timeout is a bounded experiment, not evidence that
provider timeouts have been eliminated. SDK retries remain disabled and uncertain
calls retain their reservations.

[Anthropic's tool evaluation guidance](https://www.anthropic.com/engineering/writing-tools-for-agents)
emphasizes realistic evaluations, tool-call/error metrics and accepting multiple
valid paths. We do not score success simply because SQL was chosen, nor force a
Power BI-to-SQL sequence. A relevant native uniqueness test or metadata lookup
can be useful. [Context engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
supports selective context retrieval instead of loading an entire estate. Existing
bounded retrieval stays in place; no new agent framework or domain mapping is added.

## Implementation and evaluation boundary

Operator generation settings are validated and included in the planner profile
hash. Their output cap is reserved by the shared usage governor; the runtime
checks the configured timeout against the remaining deadline before dispatch.
Existing callers retain 45 seconds and 1,500 tokens unless explicitly configured.
A changed profile cannot resume an existing session. Query permissions and SQL
free-limit settings are unchanged.

`acceptance/unknown_domain/replay_planner.py` compares none/medium reasoning with
matched 4,000-token and 120-second limits, paces calls, and preserves failures and
usage. Data-tool execution is disabled. Responses pass the decision schema, but
that does not establish that a proposed query compiles or a diagnosis is correct.

The initial replay reconstructs the six-observation prefix of known v3 session
`2337130f-66f5-4014-95a3-b601d2d338a3`, including inspected notebook logic. Typed
candidates are omitted and 1,000 seconds of remaining time is supplied. Thus it is
a controlled dynamic-action comparison, not a byte-for-byte historical replay.
No expected numerical result, defect label or required source path enters the prompt.
Full live investigation must follow before promoting a setting on quality grounds.


## Initial paired proposal results

Two trials per setting used identical reconstructed context. With `none`, both
proposed the same receipt-minus-issue native calculation (8.778s / 466 output
tokens and 4.759s / 468 tokens), overlapping existing observations. With `medium`,
one selected an actual source-schema lookup (9.722s / 739 tokens); the second
failed with APITimeoutError after 21.968s. The 120-second configuration did not
eliminate timeout behavior. The original four results and their reservations are
preserved in `.local/unknown-domain-v3/reasoning-comparison.json`.

This small, fixed-order sample supports testing explicit reasoning; it does not
establish statistical superiority, complete investigations or a timeout fix.
A source lookup is a useful prerequisite here, not a universal required path.
An additional safe exception-class chain now distinguishes connection/read causes
when available, without retaining provider messages or request contents. Failed
calls retain separate reservations; the later opt-in recovery is recorded explicitly. Full known-domain evaluation follows separately.


## First full reasoning trial and bounded recovery

Session `6d2930eb-7505-46ae-908f-bbfe4bf2139a` reproduced 53,145, retrieved the
notebook, recovered from one rejected hypothesis update, then stopped UNRESOLVED
on its fifth planner call. It had one native read and no SQL reads. The safe error
chain was APITimeoutError -> ReadTimeout -> ReadTimeout. A 120-second setting did
not prevent the provider response timeout. No cause or setting superiority was
established.

Read-only Azure deployment inspection showed GlobalStandard capacity 10 with
10,000 tokens/minute and 100 requests/minute. The queried ModelRequests series
reported HTTP 200 entries and no 429 series in that interval; metrics are aggregate
and cannot identify the cause of an individual client timeout. No capacity,
permissions, SQL limits or paid resources were changed.

The [official Python SDK](https://github.com/openai/openai-python#retries)
documents retry configuration. We keep SDK retries disabled so attempts cannot
escape the usage ledger. Instead an operator can explicitly enable at most one
runtime recovery per session, only for a planning-call timeout/connection failure
before a proposal is received. It records the error, keeps the uncertain charge,
and returns to ordinary admission/deadline/budget checks before a new reservation.
No query or external-action dispatch is retried. Defaults remain zero recoveries.
`quality-gpt54-reasoning.json` opts into one recovery for subsequent evaluation.
Tests cover charged recovery, repeated failure stopping and daily-budget refusal.


## Context retention finding

The next full trial, `125414e5-43ea-491d-afb0-9f0f0850551a`, completed with
BUSINESS_CONTEXT_REQUIRED after 11 planner calls, one native read, no SQL reads
and no provider recovery. It reproduced 53,145 and discussed positive issue/receipt
contributions, but did not test the upstream join cardinality. Repeated overlapping
notebook excerpts consumed calls. This is a limited interpretation, not a verified
cause or an investigation-quality acceptance pass.

Inspecting the actual planner projection exposed a generic context-loss bug:
a prior content receipt was compacted to identity/notice fields after the next
context observation, dropping all of its source text. The notice then suggested
looking it up again. Retrieved transformation evidence therefore disappeared from
subsequent prompts even though its original receipt remained intact.

The correction retains up to 2,500 characters across older content receipts,
prioritizing recent excerpts. Asset identity, content hash, context version,
original offset/pagination and retained-end offset remain visible. Omitted text
is explicitly labelled; immutable receipts are unchanged. The newest context
response keeps its existing bounds. This improves evidence continuity without
loading whole notebooks or directing the planner toward a particular domain or
query. Duplicate hypothesis updates also receive specific feedback rather than
an ambiguous invalid-hypothesis error. The same optional generation settings now
flow through both the CLI and local workspace entry points.

Session `c91bd287-9ebc-41ec-8def-4c36318f465b` reached both real source schemas,
but ended UNRESOLVED / BUDGET_LIMIT after 11 planner calls and one native read,
with no SQL execution. Two duplicate hypothesis updates and one overlong text
update were rejected. The next planner payload exceeded the 32,000-character
per-call ceiling (36,001 characters even without typed candidates); cumulative
input was 265,078 of the allowed 384,000. This was not cumulative-budget exhaustion.

These observations led to two further generic corrections:

- The provider-facing hypothesis schema now uses one nullable slot per admitted
  hypothesis ID. Non-null slots decode into the existing persisted update list;
  identity cannot appear twice in separate list entries. Backend validation stays
  in place. Claim, question, assessment, query and result-row bounds are exposed
  in the response schema rather than relying only on rejection after generation.
- Operator generation policy supports a bounded per-call payload allowance. The
  default remains 32,000 characters; this quality profile uses 48,000, under the
  user's authorization to increase LLM input/output size. The cumulative 384,000
  character limit, twelve planner calls, six cloud reads and SQL policy remain.
  Tests show the larger per-call allowance cannot bypass cumulative admission.

A two-call trial `f327f6b0-99d2-49a7-a287-0bcc064013e7` was explicitly cancelled
before the payload-limit adjustment. Its in-flight planner response was fenced;
usage and the cancellation remain in the catalog. It is an interrupted experiment,
not a scored success or evidence that the final engine failed.

All v3 trials remain known-domain regressions. Changed engine code requires a new
freeze and fresh variant for unfamiliar-domain acceptance.
