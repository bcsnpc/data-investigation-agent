# Report-filter capability: code and platform audit

Date: 2026-10-01 (client date). Design only; implementation is not authorized.
#289 merged after six successful checks at `13e5f4b90e82b2ecec72a78d0201428348b4dcc2`.
Saved E outputs were pasted verbatim to the user and remain in
[runs/question-account-E-business.txt](runs/question-account-E-business.txt) and
[runs/question-account-E-technical.txt](runs/question-account-E-technical.txt).
No live investigation, estate request, model call, credit grant, engine change,
config change or new acceptance result accompanies this audit.

## 1. What is retained and what is parsed

[expand_definition](../scripts/metadata_inventory.py) retains every received part
as DefinitionPart; page.json and visual.json additionally become ReportPage and
ReportVisual with complete JSON metadata. Receiving a part and understanding its
execution semantics are separate capabilities. Missing/denied definitions remain
gaps; a missing file is not an empty filter state.

| Context | Retained evidence | Implemented interpretation today | Required interpretation |
| --- | --- | --- | --- |
| Report/page/visual filters | report.json, page.json, visual.json; filterConfig and visual query | report_definition_evidence.bundle exposes raw configs and queries; no predicate composition or evaluation | Versioned PBIR semantic-query parser, model-ID-bound fields, typed literals, predicate and coverage status |
| Slicer defaults | Complete visual JSON, when returned | report_slicer_context.assess identifies one native column through queryState.Values.projections; accepts separately supplied all/values; does not decode saved selections | Saved selection predicate, visual interaction and sync-slicer applicability to the target visual |
| Report bookmarks | Every returned bookmark part is retained generically | No bookmark state parser or process projection | Explicit bookmark selection plus its report/page/visual state and suppressData/target-visual options |
| RLS definitions | Complete model.bim retained | Raw roles can be read; the lower-quantity compiler refuses models declaring roles; no effective-user role evaluator | Treat roles as security evidence, not ordinary report filters; establish identity compatibility or retain the gap |
| Drillthrough | pageBinding and filterConfig | Existing helper supports one specific legacy order drillthrough requirement, not general predicates; process adapter records pages requiring runtime context | Generic declared binding, with a supplied parameter value and inherited context; no metric/domain branch |

Microsoft documents the PBIR file layout and persistent filter/slicer metadata;
its [page schema](https://raw.githubusercontent.com/microsoft/json-schemas/main/fabric/item/report/definition/page/2.0.0/schema.json)
and [visual schema](https://raw.githubusercontent.com/microsoft/json-schemas/main/fabric/item/report/definition/visualContainer/2.0.0/schema.json)
define cumulative filter levels. The [filter schema](https://raw.githubusercontent.com/microsoft/json-schemas/main/fabric/item/report/definition/filterConfiguration/1.2.0/schema-embedded.json)
distinguishes field/type metadata from the actual semantic filter predicate. A
field declaration without a predicate cannot be treated as a selected value.
[PBIR documentation](https://learn.microsoft.com/power-bi/developer/projects/projects-report).

The [bookmark schema](https://raw.githubusercontent.com/microsoft/json-schemas/main/fabric/item/report/definition/bookmark/1.0.0/schema.json)
contains explorationState, filters and sections; options can suppress data changes
or restrict target visuals. Enumerating bookmarks never proves which was active.
RLS table permissions contain DAX row filters in [TMSL roles](https://learn.microsoft.com/en-us/analysis-services/tmsl/roles-object-tmsl?view=sql-analysis-services-2022).
Role definitions do not establish a report user's effective membership.

Read-only historical sample: inventory.sqlite scan
`968f8867-4714-4e49-aad9-35603a747294`, COMPLETE on 2026-09-15, contains 81 DefinitionParts,
4 pages, 45 visuals and 14 slicers. Its one filterConfig is a drillthrough field
with name/field/type/howCreated, no filter predicate. There are zero bookmark
parts, and its model.bim omits roles. This sample establishes actual retained
shapes, not the completeness or runtime selections of family D's newer domain.

MicrosoftProcessAdapter.presentation_context currently enumerates all registered
reports, examines at most 20 pages per report, records metadata/slicer requirements,
and always returns INCONCLUSIVE. It neither applies predicates nor executes DAX.
A new check must select one explicit report/page/visual and disclose incomplete
parts or truncated coverage, rather than silently using the first report.

## 2. The proposed reproduction test

Introduce a receipt-backed declared-context check independent of boundary walking:

1. Bind selected model, measure, report, page and target visual by existing stable
   identities. Capture the user's reported numeric quantity, its exact quote,
   units, formatting/rounding and time context. Do not invent a number from prose.
2. Parse only a supported versioned subset of the retained predicates. Assemble
   report + page + target visual + applicable saved slicers; apply an explicitly
   chosen bookmark using its documented data/visual scope. Preserve each source
   reference, hash, scope and origin. Unknown operators, parameters, interactions
   or missing values block a faithful evaluation; they are not ignored.
3. Evaluate the actual native measure twice: declared context and no added report
   context. Prefer two named scalar expressions in one bounded DAX request, with
   one reader identity and surface attestation. Both retain the reader's RLS;
   unfiltered means no added report predicates, not unrestricted data.
4. Compare both against the quoted reported quantity using explicit numeric and
   display semantics. Declared matches and unfiltered differs => declared context
   is sufficient to reproduce the difference. Both match => context is not
   discriminating. Neither matches => this declaration did not reproduce it.
   Missing figure => only the scope effect can be established, not reproduction.

Native evaluation is technically available: native_diagnostics.build emits
CALCULATETABLE/ROW with metadata-bound TREATAS or typed in/range filters;
filter_scope.compile_filter supports string/int64/decimal/boolean/dateTime literals.
The adapter already runs a filtered presentation baseline. What is absent is a
PBIR/URL-to-scope compiler, selected report/visual context in the process contract,
a structured reported quantity, a two-context test, and its support contract.
The existing compiler rejects duplicate filters on a column; it cannot be fed
report/page/visual clauses without first composing their intersection faithfully.
[CALCULATE semantics](https://learn.microsoft.com/en-us/dax/calculate-function-dax)
include replacement of existing filters, so composition must preserve intersection
and measure-defined behavior, not concatenate or overwrite predicates blindly.

Initial supported subset: explicit categorical membership and exactly representable
fixed ranges on resolved columns. TopN, tuple/hierarchy/custom slicers, measure
filters, relative dates without a fixed anchor, visual calculations, field
parameters, grouping-dependent calculations and ambiguous bookmark overrides
remain unsupported until their native semantics can be reproduced. The native
measure, not a local formula evaluator, remains authoritative.

This is a WITHIN_LAYER_CHECK: two reads on the same semantic model are not an
independent boundary comparison. Current PRESENTATION_LOGIC support requires a
cross-surface comparison. The proposed contract must explicitly admit context
reproduction evidence for that outcome without relabelling these reads as
CROSS_SURFACE_VERIFIED or relaxing the invariant for any boundary outcome.
Retain SNAPSHOT_UNVERIFIED where served versions are unavailable; a combined
request alone does not satisfy the existing query-bound version contract.

## 3. What the check cannot establish

A positive reproduction supports: the declared context can produce the stated
figure under the diagnostic reader at this time. It does not establish that this
was the user's active state, or exclude a coincidental match or update timing.
Ad-hoc/persistent selections, cross-highlighting, cross-filtering, drill state,
personal bookmarks and personalised visuals are absent from static definitions.
RLS for another user is not reproduced by passing ordinary predicates.

Microsoft's [filters API](https://learn.microsoft.com/en-us/javascript/api/overview/powerbi/control-report-filters),
[slicer API](https://learn.microsoft.com/en-us/javascript/api/overview/powerbi/control-report-slicers)
and [bookmark API](https://learn.microsoft.com/en-us/javascript/api/overview/powerbi/report-bookmarks)
can inspect a cooperating embedded report session. Static definition collection
is not that session; capturing it is a separate, optional future capability with
explicit session/identity provenance. No browser capture is proposed for this
first implementation. Viewer + Build remains subject to RLS according to
[Microsoft's RLS documentation](https://learn.microsoft.com/power-bi/enterprise/service-admin-rls).
Execute Queries supports DAX; its impersonation field is not permission to become
the complainant, and the existing reader must not be elevated.

Engine-rendered limits should name the tested report/page/visual and predicate
origin, reader identity, missing runtime state, formatting uncertainty, version
uncertainty, and every excluded context component. A failed faithful compilation
remains INCONCLUSIVE, with the unsupported component named.

## 4. Shared URL context

A visible report URL filter can be accepted as USER_DECLARED_URL evidence,
distinct from DECLARED_BY_DEFINITION. Parse locally; do not fetch or trust its
host as authorization. Bind workspace/report/page to already approved catalog
identities, validate the supported OData subset, decode escaping with limits,
resolve typed fields, preserve the original quote/hash, and require scope review.
Reject ambiguous duplicate parameters, unknown fields/operators and opaque share
or bookmark state; do not silently replace existing declared filters.
[Microsoft's URL-filter documentation](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-url-filters)
describes typed filters, conjunction with existing filters, ten expressions and a
2,000-character limit. A shared link is a declaration, never proof it was opened
or that no additional selection was made. A bookmark identifier requires a
matching retained bookmark; opaque encoded runtime state needs a separately
specified capture route. Today's question_intake does not open or parse URLs.

## 5. Reachable outcomes and control flow

The capability is called presentation_context; the actual taxonomy outcome is
PRESENTATION_LOGIC, not PRESENTATION_CONTEXT. A bounded native context test could
make PRESENTATION_LOGIC reachable through its own faithful reproduction contract.
It should run when the ticket asks about presentation context, even if no lower
boundary can be compared. Presently it runs only after the first successful
independent comparison diverges; D stops before that point.

A successful declared-context reproduction can classify that scoped explanation.
A negative result rules out only the evaluated declaration. It cannot rule out
unknown runtime context. Thus this capability alone does not make DEFECT reachable
for the complainant's actual report state. A future fully captured/reviewed context
could rule out presentation effects within that specified scope, but all current
independent-comparison, definition, job, capability and attestation gates remain.
At deeper divergences the existing engine only requires step-5 competing checks;
the presentation_context blocker is specifically on the first boundary. Declaring
a capability without a completed negative check is never an exclusion proof.

Also examine ordering before implementation: the transformation-free direct-source
REFRESH_LATENCY rule currently runs before presentation_context. Declared context
must be made explicit in quantity/scope equivalence before a presentation difference
is attributed to stale serving. Do not bypass its no-filter/direct-source guards,
and do not infer a freshness explanation from two differently scoped quantities.

## 6. What this does for D, and what remains separate

Saved D session resolves warehouse_name in North, successfully reads the scoped
native baseline once, then records NO_COMPARABLE_PATH because the lower adapter
refuses filtered scope. Its ticket contains no numeric reported figure. A new
within-model test could compare North with the global evaluation and explain the
selection's effect, preserving USER_DECLARED provenance. It could answer that
part of D without claiming continuity below the model.

To resume D's vertical walk, a separate filtered-equivalence capability is required:
map the selected dimension through declared relationships/keys to each lower
surface; preserve value typing, relationship direction, unknown members, blank
semantics, grain, scope, joins, multiplicity and deduplication; establish compatible
security. Use a declared join/semijoin only when equivalence is demonstrable.
Name similarity or a same-named column is insufficient. Every unsupported mapping
stays NOT_COMPARABLE. The current filtered refusals at evaluate/_lower_quantity
remain unchanged. A report-context implementation does not solve this second task.

## Proposed delivery and acceptance (awaiting review)

First implement only declaration parsing, provenance/completeness and the native
context-reproduction procedure plus a distinct support contract. Add offline
fixtures for cumulative/repeated-column filters, bookmark targeting, URL origins,
RLS limits, missing values, unsupported constructs, reported-number rounding and
positive/negative/discriminating cases. Assert within-layer evidence cannot certify
a boundary or a global DEFECT. Report planner-context size and directory coverage
before/after if any context is added. Then a separately authorized bounded live
case can test reproducibility. Filtered lower-scope translation is a separate
milestone and never a prerequisite to reporting partial context findings.

This audit changed documentation only. No new engine tests were needed; local
links, whitespace and unchanged-engine diff are checked before publishing.
