# Provider response reliability and source-query evaluation

2026-09-18. Follow-up to [PR #205](https://github.com/bcsnpc/data-investigation-agent/pull/205).
Current delivery claims belong in [current status](current-delivery-status.md).

## Failure diagnosis

The provider adapter previously collapsed incomplete responses, refusals and
invalid decision formats into ValueError. It now preserves only allowlisted
failure categories and numeric usage, including failures before a decision is
received. Incomplete/refused/invalid responses remain non-executable. Their
reservations are never refunded; known usage is settled and missing usage stays
uncertain. Only the existing explicitly enabled connection/timeout recovery can
schedule another call. An output-limit failure is not automatically retried.

[OpenAI reasoning documentation](https://developers.openai.com/api/docs/guides/reasoning)
explains that reasoning and visible output share the response limit, and an
incomplete response can identify max_output_tokens as its reason. We used that
signal rather than guessing the cause from a generic exception.

Four known-context, no-data-execution replays used 4,000 output tokens and medium
reasoning. Three returned decision-schema-valid SQL proposals. One returned
OUTPUT_TOKEN_LIMIT with exactly 4,000 output tokens and 14,560 input tokens.
Thus an output-limit failure was reproduced on the source-ready context, but the
old ValueError cannot retrospectively be assigned this cause with certainty.
The replay preserves observed context from session
09e8b35e-889b-4995-8a82-6f52d96dd78d with a reconstructed 600-second remaining
clock. It is not a byte-identical historical request or frozen acceptance.

The experimental quality profile now reserves up to 8,000 output tokens per
call under the user's existing budget authorization. Defaults, per-session call
and cumulative-input bounds, reader access and SQL policy are unchanged. An
8,000-token replay and complete known-domain investigations evaluate this choice;
no model superiority or unfamiliar-domain pass is implied.

## Query admission finding

One otherwise structured SQL proposal mixed unaggregated summary columns with
an aggregate and no GROUP BY. [Microsoft's T-SQL grouping rules](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-group-by-transact-sql)
require the relevant nonaggregate output columns to be grouped. A narrow AST
check now rejects this clear invalid pattern locally, with actionable feedback,
before spending a source read. It does not rewrite a query or choose business
semantics. Grouped, scalar, nested and window queries retain their existing
admission behavior; native SQL remains responsible for full semantic validation.

All fixtures are the already known v3 domain. No new scenario-specific query,
metric branch, expected value or executable mapping was added to runtime context.
## Known-domain live results

The 8,000-token source-ready replay returned a structured SQL proposal in 27.787
seconds, using 14,560 input tokens and 2,668 output tokens (1,869 reasoning tokens).
It passed the current local query validator; no data query was executed by replay.
One successful replay is not statistical evidence of improved reliability.

Transformation session `065e6077-4b27-4f7d-b632-c11bb4cfec2c` completed with eight
planner calls, two native reads, five metadata lookups and no SQL reads. It
reproduced 53,145, including 39,601 receipts and 13,544 issues. It classified a
possible sign-handling problem as LIKELY_TECHNICAL_DEFECT while acknowledging that
intended metric semantics were unknown and join fanout remained untested. This is
partial investigation evidence, not a correctness pass: the classification depends
on an unestablished business interpretation. The absence of provider errors does
not establish investigation quality. Linear notebook paging also spent calls on
less relevant source content before using literal search.

Validation: 943 local regression tests passed after all backend changes, including
provider failure accounting and mixed aggregate query admission cases. No browser
UI was changed or dedicated local browser suite rerun. Further live evaluations
and delivery state are recorded in current status.


Ambiguity session `7fb2540d-c788-44cc-a1eb-37830c0a51b1` completed in seven planner
calls with two native reads and four context lookups. It compared 8,580 with and
without the reason-code filter, inspected the SQL schema, searched the notebook
for the code and read the matching excerpt. Its BUSINESS_CONTEXT_REQUIRED outcome
left the undocumented meaning and intended inclusion rule unresolved, with scoped
filter/RLS limits. This is useful known-domain uncertainty handling, not proof
that every external document was searched or unfamiliar-domain acceptance passed.

The original daily policy was restored after the live tests, preserving all 282
usage rows. Reader permissions, SQL free-limit/AutoPause and cloud-call limits
were unchanged. The next quality gap is transformation test selection and claim
qualification; a completed session alone must not count as a correct diagnosis.
