# Silent-fallback audit

Updated 2026-09-25. This audit follows the stub-as-evidence and wrong-environment
defects. Its rule is that anything usable as evidence must be observed evidence or
an explicit unavailable/unknown state, never a default.

## Findings fixed before the correct-context run

| Surface | Prior behavior | Resolution |
| --- | --- | --- |
| Acceptance environment | Live ticket and live planner replay opened `development` regardless of the discovery environment | Fixed in #232: both require an explicit environment, preserve it in `ModelStore`, and have an isolation regression. |
| Truncated definition search | A no-match search could still be sent for negative model judgment if its retained result was truncated | It now returns `UNAVAILABLE`, `explains: null` and partial evidence without calling the model. Complete no-match searches remain genuine negative evidence. |
| Partition definition parsing | Missing coverage, malformed JSON, a missing referenced expression, multiple partitions and unsupported connection syntax could collapse to `NO_DECLARATION` | Missing/malformed content is `DEFINITION_UNAVAILABLE`; multiple/unsupported forms are `UNSUPPORTED_DECLARATION`; `NO_DECLARATION` remains only for complete absence. |
| Application-source declaration | The adapter assigned Silver-to-SQL `NO_DECLARATION` without implementing that inspection | Replaced with `CAPABILITY_NOT_IMPLEMENTED`; absence is no longer claimed. |
| Context search without discovery | Search returned an empty successful result when no environment context existed | It now raises an explicit context conflict. |
| Planner projection race | A missing latest context could silently produce an empty asset directory | Projection now requires the exact discovery version already admitted for the session. |

The parser and context fixes change error handling only. They add no planner
context content and do not authorize another scope, connection or tool.

## Reviewed defaults that are safe

- Connection configuration has an exact schema and no default workspace, SQL
  database, visibility schema, credential path or execution reader.
- Runtime admission binds model revision, context ID/hash, discovery version,
  configuration hash, reader scope, planner profile and usage policy. Mismatch is
  a conflict rather than an empty catalog.
- Discovery collectors may return `None` internally after an exception, but every
  such attempt writes `UNAVAILABLE` coverage. Partial coverage cannot remove an
  old asset, and only complete coverage can establish absence.
- Provider, query and worker exception handlers persist `HELD`, `FAILED`,
  `INTERRUPTED` or `UNAVAILABLE` plus a safe error category. They do not generate
  a negative business finding.
- Static report parsing remains `INCONCLUSIVE`; missing active bookmark, selection
  or RLS state cannot unlock presentation or defect conclusions.
- An absent native-reader observation is tolerated only for legacy injected
  transports. Discovered execution requires the configured reader and rejects a
  missing or different identity receipt.
- Scheduler `None`/`False` returns mean that no queued work exists. They are
  control-flow values and never enter investigation evidence.

## Proposal only

`context_search.latest` still uses `None` as its low-level optional return. Current
evidence-producing callers now either fail admission or translate it to an explicit
unavailable state. Replacing that primitive with a typed result across every
administrative and read-only caller would be a broader behavior/API migration; it
is proposed for a later cohesive change rather than bundled into this checkpoint.

No context payload fields were added. Golden directory entry counts, SQL-object
counts and payload characters remain unchanged: the retained recorded first-call
view is 28 entries, 11 SQL objects and 15,971 characters, while the synthetic
golden used by the projection regression is 28 / 11 / 5,744 before and after
fitting. The complete local suite passes all 1,078 tests.
