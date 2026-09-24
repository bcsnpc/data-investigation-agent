# Proposed compact ownership and reasoning evaluation

2026-09-23. Proposal only, following the completed
[revert and six recorded runs](ownership-revert-evaluation.md). No replacement
ownership implementation, generation setting or allowance has been changed.

## Compact ownership: reuse the existing handle prefix

Adding a separate `connection_key` field to each entry would still cost O(N)
characters. Instead, replace the existing one-character `a` prefix in wire handles
with a connection key: for example, `s12` refers to asset 12 on connection `s`.
The suffix remains globally unique and the server retains the exact identity map.
This replaces characters already present; it adds no per-entry field or label.
All handle references and tool-schema enums must change together, without changing
asset identity, query text, permissions or admission. No names infer bindings.

Emit the connection registry once per payload. Illustrative representation:

```json
{
  "connections": {
    "s": {"system": "AZURE_SQL", "connection": "<approved server/database>", "schemas": ["<approved schema>"]},
    "f": {"system": "FABRIC_METADATA", "connection": "<approved workspace>", "schema": "UNKNOWN", "sql_endpoint": "NOT_ESTABLISHED"},
    "p": {"system": "POWER_BI", "connection": "<selected model scoped identity>", "schema": "N/A", "sql_endpoint": "NOT_ESTABLISHED"},
    "a": {"system": "UNKNOWN"}
  },
  "context_entry_points": [{"id": "s12", "kind": "SqlObject", "name": "<discovered qualified name>"}]
}
```

Registry values come from approved connection profiles and exact catalog membership,
not fixture/domain mappings. Fabric metadata scope does not imply that its items
share a queryable SQL endpoint. Native reads remain bound to the selected model.
Unrepresented ownership stays UNKNOWN; aliases never grant access. A bounded key
space must not silently merge distinct connections or drop directory entries.
The added representation scales with approved connections/schema descriptions,
not the number of directory entries within those scopes.

## Measured cost and the necessary coverage guard

An offline serialized prototype used actual scoped connection identities from the
recorded F call 1; the placeholders above were not used to understate cost.
No provider or data tool was called for the prototype.

| Recorded F call 1 | Reverted engine | Proposed registry/prefix |
| --- | ---: | ---: |
| Directory entries | 28 | 28 |
| SQL object entries | 11 | 11 |
| Recorded pre-wire payload characters | 14,538 | 15,015 |
| Compact wire-payload characters | 9,734 | 10,210 |
| Serialized SDK request bytes | 28,217 | 28,780 |

Added compact wire cost is **476 characters** for 1, 7, 14 and 28 directory
entries with the same registry; pre-wire cost is 477 characters. Prefix substitution
preserves handle lengths and unique resolution. These are character/byte measurements,
not a claim that every tokenizer assigns constant billed-token cost. The recorded
pre-wire measurement includes generation settings appended after runtime fitting;
coverage checks remove those settings before applying the 48,000-character fitter.

**A smaller header alone is unsafe.** Naively adding it and rerunning the existing
fitter reduces coverage on three of the 53 recorded calls:

| Recorded call | Original entries / SQL objects | Naive header plus fitter |
| --- | ---: | ---: |
| G1 call 8 | 14 / 4 | 10 / 3 |
| G2 call 11 | 8 / 2 | 4 / 1 |
| G3 call 10 | 17 / 6 | 13 / 4 |

Proposed guard: ownership is optional enrichment. Add the fixed registry only when
it fits alongside the already-retained context. Otherwise retain the original
payload and handles and replace the existing lookup instruction with a shorter,
explicit ownership-omitted notice; connection context can still be retrieved.
Do not run a second fitter that pays for ownership by discarding directory entries.
This choice trades ownership visibility on saturated prompts for preserved evidence
coverage, without increasing the limit or silently claiming complete ownership.

The local prototype asserts unchanged pre-wire and wire directory/SQL counts for
all **53** recorded calls, staying within the original per-call ceiling. Its guard
omits the registry on **five** saturated prompts, including two that already had
no directory entries. Production adoption would require the same golden and boundary
tests, alias round trips and omission telemetry before any live evaluation. The
revert's production golden test already protects 28 / 11; the proposed registry and
guard exist only in the local measurement harness. Receipt:
`.local/ownership-revert-live-20260923/ownership-proposal-cost.json`.

## Token and reasoning recommendation

The completed six-run batch used **682,986 input tokens** (13,952 cached) and
**86,514 output tokens**, including **62,100 reasoning tokens**, across all 53
recorded planner responses. The largest response was **4,670**, below the existing
8,000-token allowance. No output-limit or provider failure occurred. These are
planner-only usage totals; intake and infrastructure are separate. Conservative
planner reservations were 424,000 output tokens and were not refunded.

The evidence supports testing better reasoning effort, but does **not** show that
raising the output cap alone would fix the observed failures. G2/G3 stopped at six
cloud reads; more input/output tokens cannot directly remove that boundary. The
stopping-contract proposal remains evaluated and not adopted.

Recommendation, after separate authorization: compare **medium versus high effort**
with **16,000 output tokens in both arms**, three repeated G trials per arm. Matching
output allowances isolates effort; the added allowance gives high effort room
rather than forcing a longer visible answer. Keep 48,000 per-call input characters,
384,000 cumulative characters, 12 planning calls, six cloud reads, 120-second provider
timeout, 1,800-second deadline and 65-second serial pacing unchanged. Report actual
usage, timeouts, tests, qualified conclusions and budget stops; do not adopt high
effort from one favorable result. No input increase is recommended from this batch.

This needs a reviewed change to the shared generation/reservation maximum (currently
8,000) as well as experimental configuration; editing configuration alone would be
rejected. Existing daily counters/limits stay intact. Six worst-case 12-call runs
would reserve 1,152,000 planner output tokens plus intake; schedule only when the
unchanged daily allowance is available. Do not reset counters or raise the daily
policy to fit the experiment.

GPT-5.4 supports medium and high reasoning effort. Output allowance includes reasoning
and visible output; more allowance is capacity, not a requirement to spend it.
See [official model reference](https://developers.openai.com/api/docs/models/gpt-5.4)
and [reasoning-token guidance](https://developers.openai.com/api/docs/guides/reasoning).

A reasonable **planning allowance is $5 per trial, $30 for the six-run comparison**,
subject to checking the actual Azure meter before approval. At the published OpenAI
reference rates of $2.50/M input, $0.25/M cached input and $15/M output, this completed
planner batch corresponds to about **$2.97**; a 12-call run fully using 16,000 output
tokens per call would cost **$2.88 in output alone**, plus input. These are illustrative
OpenAI reference calculations, **not Azure billing receipts or an enforced dollar
cap**. Azure pricing/credits and actual input usage must be checked before execution.
[Published reference rates](https://developers.openai.com/api/docs/models/gpt-5.4).

No proposal above has been applied. No further live run, freeze or fresh variant follows this report.
