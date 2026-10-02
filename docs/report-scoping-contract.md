# Report-scoped declaration and value-resolution contract

2026-10-02, America/Chicago. PR A follows the user ruling in report-scoping.md.
No investigation run or estate request is part of this contract milestone.

## Scope correction

#304 resolved a literal against all reports belonging to a model. That could
bind the ticket's selection to another report's declaration. The original
lookup claims, recordings and ledger rows stay unchanged; dated corrections
are appended to its evidence document, target-contract document, README and
current status. A declaration on another report never establishes the context
of the figure the ticket names.

The pinned context actually contains **three** reports on this model, rather
than the two stated in the prompt: Inventory Health e1b8e1, Warehouse Performance
e1b8e1 and Declared predicate fixture 20261001. Inventory Health has zero retained
predicate nodes. The third report has eight predicate nodes and its ACTIVE North
entry is bfa80a808ae43f4a0399920c0f38ad9fdd594d3ab7119c3aab1b3f420b465ddb.
These counts are from local retained parts; no cloud call was made.

## Consumer contract

`report_scope.py` defines the additive versioned contract. The old unscoped
contract stays available to read historical records. The adapter has not yet
been switched to the new contract, and no run is authorised before PR C merges.

Report STATED requires an exact ticket span matching exactly one retained report
name, with its resolved native scoped ID. Partial/case-changed/fuzzy matches do
not resolve. Missing or ambiguous names produce REFUSED with named candidates.
An unnamed report is not silently marked STATED, even in a single-report catalog.

Each discovered declaration source carries its report identity. Its stable
identity hashes report, location and content. Conservation is per report: both
the discovered manifest and the entries must belong to the target report, every
manifest unit has exactly one disposition, and the active restriction set must
be exactly the ACTIVE entries' restrictions. A foreign entry fails conservation
regardless of whether its column and value match.

ACTIVE FULL_DOMAIN is explicit and has no restrictions. It is distinct from
an ACTIVE RESTRICTED entry with an empty IN value set, which matches no values,
and from an EXCLUDED conditional/unsupported entry. Viewer-changeable defaults
still carry their volatility and saved-default assumption. The existing legacy
nonempty-entry rule is unchanged for historical, unscoped validation.

Selection resolutions remain different facts:

- EVIDENCE: exactly one ACTIVE declaration in the stated report carries the
  literal, proved by the conserved inventory entry.
- OBSERVED: no ACTIVE declaration carries the literal; every scoped candidate
  grouping column has a complete value-existence receipt, and exactly one column
  contains it. The target references that successful receipt. Missing/failed,
  foreign-report or truncated checks cannot establish unique membership. Each
  receipt requires query-bound reader self-description, with PARTIAL coverage
  retained rather than upgraded.
- STATED: the ticket exactly names the column; the separate literal lookup audit
  preserves MATCH, MISMATCH or UNAVAILABLE. A mismatch cannot be labelled a match.
- REFUSED: unresolved report, declaration ambiguity, missing/nonunique observed
  value or incomplete observation coverage, with candidates and reason.

The request variant is not a resolution: it carries the stated report and exact
selection quote without guessing a column or claiming evidence. This allows
review before execution. A subsequent existence read belongs inside the governed
procedure, through the existing compiler/admission/receipts path and diagnostic
cap; contract-only PR A performs none. The model may translate a request but may
not emit EVIDENCE or OBSERVED.

The schema encodes stated lookup status/receipt cardinality together. Successful
resolution variants can only contain a STATED report binding. Enum values and
bounds come from the consumer contract. Engine-written renderers distinguish
observed row addressing from a declared report filter. PR B must wire them into
both final outputs; the new renderer has not executed live.

## Saved Inventory Health slicer

The retained part is
`definition/pages/688de76fce97549d9756/visuals/2d70e0f5e5fc596dae01/visual.json`.
Relevant fragments:

```json
{"visualType":"slicer","query":{"queryState":{"Values":{"projections":[{"field":{"Column":{"Expression":{"SourceRef":{"Entity":"Locations"}},"Property":"warehouse_name"}},"displayName":"Warehouse"}]}}},"objects":{"data":[{"properties":{"mode":{"expr":{"Literal":{"Value":"'Dropdown'"}}}}}]}}
```

There is no `objects.general` saved selection, no filterConfig predicate and no
syncGroup in that retained slicer. The parent page contains its display settings
and background objects, and no visualInteractions declaration. A full-domain
saved selection restricts nothing, so an unknown interaction cannot turn it into
a predicate. Per the ruling it will be ACTIVE FULL_DOMAIN with viewer-changeable
saved-default provenance in PR B. This is a saved-default fact, never proof that
the user has not moved the slicer. The previous UNSUPPORTED label is not silently
rewritten in any old observation.

## Validation and context cost

The full local suite passed 1,519 tests. A subsequent closed-schema amendment separates unresolved-report refusals from value refusals; all 21 focused contract tests and the required two generator tests pass on the final engine. Six final-head CI checks are recorded on the PR. Existing intake/planner payload code and their goldens
are unchanged: 28 directory entries and 11 SQL objects; twelve intake fixtures
retain their catalog coverage and payloads (1,050?1,952 characters, Family D
1,103). The additive contract is not attached to a live model request in PR A,
so planner payload characters before/after are unchanged. PR B must measure the
new wire cost when report binding is introduced into intake.

README/status updated. Engine bytes invalidate prior freezes. No fixture,
permission, config, policy, credit, usage-counter or ledger change. PR B then PR C
must merge before any rerun; authored tickets and all earlier failures remain.
