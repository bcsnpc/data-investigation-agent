# R28 generic fixes — development branch

Branch `round-twenty-eight-fixes` starts at PR #436 head `ef9fde1769cba46d0be2d96f508ed1ad04c7c415`. Draft PR #437 contains these repairs. The official HealthNet test image, sealed tickets/answers, controls, results and grades are unchanged. There are no Anthropic calls, permission changes, injections, merge or tag in this task.

## Repairs

1. **Smaller prompts, full retained evidence.** Setup follows exact native bindings rather than expanding every model with a common owner. Intake receives selected or ranked candidate names; investigation receives their paths and dependencies. Native definition bodies become hash-pinned evidence references; `get_evidence` retrieves the original body without an estate read. Unknown references remain intact. The stored catalog and case retain the complete original evidence.
2. **Bounded delivery repair.** At most two delivery repair attempts are dispatched. Rejections at an unchanged query-evidence frontier are bounded. A no-tool response after rejection ends in an explicit unresolved handoff instead of another generation with the same evidence. Read-only checks, evidence IDs and target checks remain enforced.
3. **Named setup targets.** No figure-only expansion across the estate. Explicit targets win; report/page fallback contains at most three paths and records whether discovery was exhaustive. It never silently picks one of truncated candidates.
4. **Safe string functions.** SQL and DAX accept explicit safe string operations including `RIGHT`, `LEFT`, trimming, length and replacement. Arbitrary UDFs, external reads, execution, writes and DDL remain refused.
5. **Check form candidates first.** User-facing names are checked in the selected native report/page before asking. Two or three tied visual candidates can receive bounded native value probes; resolution requires every probe to succeed and exactly one precision match. Probe evidence persists into investigation. Explicit parent/target conflicts remain questions. HN-013's saved form still conflicts with its selected page; its offline replay remains `NEEDS_INPUT / VISUAL_OUTSIDE_PAGE`. No ticket-specific override was added.
6. **Discovery readiness.** `dia estate validate` now requires a hash-pinned discovery bundle. It fails on missing columns, native dependencies, exact source-to-named-SQL bindings, model-read receipts or the RLS route. Configuration shape alone cannot claim readiness. Validation itself performs no network reads. The recorded HealthNet metadata bundle passes: 1,828 assets, three models, 28 model-table bindings, zero gaps. This is metadata/read-receipt completeness, not a new data-quality claim.

## Qualified revision

Source `2ab99c8f35dca8fbff6fbd7f60a5751cc41aad63`:

- Full repository: **6,257 passed, 54 skipped**.
- Image shards: **8/8 passed**.
- [Qualification workflow](https://github.com/bcsnpc/data-investigation-agent/actions/runs/45932901043).
- New development image: `ghcr.io/bcsnpc/data-investigation-agent/offline-worker@sha256:3c6d30b68b20df08d60d9d65d94699554e6c94e26142834c9048a11336c0344f`.

The persistent Azure worker template and frozen official test image were not updated. New executions use only a development execution override.

## Saved-trace proof and its limits

Attempted all 123 saved practice traces and all 18 saved, graded HealthNet traces with network connects forbidden. No new model decisions or query results were generated. Both PR #436 head and the repair source used the same replay harness.

| Replay result | PR #436 head | Repair |
| --- | ---: | ---: |
| Complete | 72 | 69 |
| Missing saved boundary | 34 | 39 |
| Replay failure | 24 | 22 |
| No investigation case | 11 | 11 |

**65 traces complete on both revisions without any saved-reply reuse: 61 keep their replay classification and four change.** Four additional complete pairs keep their classification but require the harness to repeat the identical saved formatting reply twice; they are reported separately, not strict replay proof. The other 72 are not claimed as classification passes. Saved-response replay is not a fresh quality score or byte-exact tape replay. Missing saved reads, tool-phase divergence and pre-investigation holds are disclosed in the per-case report.

| Saved case | Baseline replay | Repair replay | New stop |
| --- | --- | --- | --- |
| Practice dev01 history-source-900201 | ANSWERED | UNRESOLVED | Delivery rejection without new reads |
| Practice dev02-advisory history-source-900201 | ANSWERED | UNRESOLVED | No new reads/tool call after rejection |
| HN-002 | BLOCKED | UNRESOLVED | No new reads/tool call after rejection |
| HN-024 | ANSWERED | UNRESOLVED | Target not a unique observed match; bounded rejection |

These are stricter termination changes, not claimed new correct answers. All historical outputs remain intact.

## Offline prompt sizes

Measured every comparable saved investigation/evaluator request with local `tiktoken` `o200k_base`. These are comparative token counts, **not Anthropic billing tokens**. They include calls that fetch full evidence; some grow.

| Calls | Median before | Median after | Total input reduction | Calls that grew |
| --- | ---: | ---: | ---: | ---: |
| Practice, 725 | 36,197 | 28,765 | 20.08% | 173 |
| HealthNet, 90 | 63,610.5 | 36,153.5 | 36.67% | 2 |

The [per-call CSV](../acceptance/round_twenty_eight_fixes/prompt-sizes-per-call.csv) includes character and token counts. The [per-case replay report](../acceptance/round_twenty_eight_fixes/saved-replay-report.json) includes all attempted traces and limitations. No private model reasoning or expected answers is published.

## Free-model development check

Selected only already-run-and-graded baseline tickets: HN-001, HN-002, HN-003, HN-008, HN-011, HN-013, HN-024 and HN-026. HN-009 and every unrun or controlled ticket are excluded. All AI steps are pinned to OpenRouter `nvidia/nemotron-3.5-super-vl:free`; the development gateway has no Anthropic endpoint. These results are DEV-only and must not replace the frozen HealthNet scores.

Before each pair: disk floors, recorded discovery completeness, shared budget headroom and both SQL free allowances are checked. The forecast is at most 320 physical requests, with the existing 40-request per-case cap. There is no restoration request or allowance increase. OpenRouter's no-generation key/model checks returned 200; the reported free allocation is 1,000 calls/day, with the existing 20 requests/minute queue and concurrency two.

Live results and development grades will be appended after capture recovery.
