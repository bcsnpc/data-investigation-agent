# Declared predicates: native adapter and compiled quantities

Date: 2026-10-01. Tracking: #193 and #199. Second of three separate work items.
#294 merged as `25e2aa8` after six green checks; its intersection design is unchanged.

The Microsoft adapter now advertises declared_context_reproduction and reads
predicates only from the model's pinned, integrity-checked discovery context.
It rechecks enablement, context ID/hash and model revision before extraction and
each value read. Neither context_search.latest nor a report API is used for this
capability. Definition evidence records context ID, model revision, selected
part, active source part IDs/hashes and excluded declarations. Both query receipts
carry context ID/revision, applied resolved restrictions and the definition reference.

## Active versus conditional evidence

One selected scalar card supplies the context. A caller may supply the opaque
DefinitionPart ID in definition_target_id; without it exactly one matching
measure visual must exist. Multiple matching visuals refuse by name and candidate
IDs. Reports, pages and visuals are never merged into one scope. Existing intake
does not yet carry a reviewed definition target or numeric reported figure;
production ticket integration and recorded reproduction remain separate work.

Report/page/selected-visual categorical filters with actual predicates apply.
Saved slicer predicates apply only where a retained DataFilter interaction names
that slicer and selected card. A NoFilter interaction is recorded as excluded.
Field references without a predicate are recorded, never turned into a selection.
Bookmarked states are stored alternatives, recorded with their source hashes,
parsed restrictions (or unsupported form/raw declaration), and explicit exclusion:
STORED_BOOKMARK_REQUIRES_INVOCATION. Their different same-column value never enters
the active intersection. An invoked bookmark is explicitly named in receipt
evidence as an open explanation for non-reproduction; invocation remains unknown.
The original definition and both read observations retain those exclusions.
The neutral engine's fixed open-selection limitations and INCONCLUSIVE
presentation_context remain unchanged; no active-selection claim is introduced.

No judgment call classifies an unknown declaration as active. Missing/default/
highlight/ambiguous slicer interactions, synchronized slicers, conditional page
bindings, slicer choice-list filters, selector-dependent/inverted selections and predicates
outside supported active locations refuse with named reasons. These conservative
limits mean some legitimate report contexts are currently undeclared. Static
metadata alone still cannot establish ad-hoc selections, security equivalence,
personalized visuals or a shared served snapshot.

The Microsoft [page schema](https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json)
defines page filters and distinct DataFilter/NoFilter/Default/highlight interactions.
[Bookmark documentation](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-bookmarks)
describes saved filter/slicer states applied by invoking a bookmark. These support
separating declarations rather than inferring a current user selection.

## Extraction, representation and compilation

Native Where/Condition/In/literal tuples are parsed only in adapters/report_predicates.py.
Column references resolve through native aliases and an exact unique semantic
table/member in the pinned model catalog; the neutral field_id is that fully
scoped catalog identity, never the display name. Strings, bounded integer,
boolean and exactly representable finite numeric literals are supported under
the declared column type. Date/time, blank literals, lossy numbers, tuple In,
measure expressions and other unknown shapes refuse before reproduction reads.

The adapter catches native range/negation/relative-date/comparison/Top N or other
unsupported condition shapes and names them. It also refuses extraction/rendering,
unknown applicability, missing bindings and parser limits. The engine retains its
independent whole-set refusal for neutral operators/structured values it cannot
represent or intersect. No unsupported active member is dropped while the rest
proceeds. Refusal invalidates any previous admission for that measure.

Catalog-bound references and decoded typed literals construct a native expression;
query_dax.compile_query and flexible_tools.build bind and admit both complete
queries before any baseline dispatch. flexible_tools.run rechecks the same context,
policy and identity at dispatch, executes the isolated transport, verifies its
identity evidence and seals the terminal receipt. This is a generic binding/compiler
path for unfamiliar report columns and values, with no metric formula, date-column
branch, family route or expected value. Local code does not evaluate the measure.

The engine's composed list emits at most one filter argument per native column
path; a duplicate path is independently refused. Nonempty sets become a membership
filter; an empty set becomes FILTER(VALUES(resolved_column),FALSE()), not an omitted
argument. Both readings self-report identity on the same semantic surface and
remain WITHIN_LAYER_CHECK. The undeclared-context reading is not an unrestricted
or true total. The lower filtered-scope refusal and vertical/DEFECT gates are untouched.

## Validation and limits

Thirty-two adapter tests pass, plus 34 neutral reproduction tests, 43 process
flow tests, 11 unchanged planner projection goldens and two required generator
tests. Tests use synthetic pinned metadata, temporary receipt databases and
injected native responses; no service execution or offline investigation replay
occurred. The first test attempt exposed a missing scan_id in the synthetic
fixture, corrected in the fixture rather than production code. The first full-suite attempt was interrupted to fix that refusal passthrough;
its local log is preserved. Final validation passed all 1,393 tests in 443.899 seconds.

Planner context shaping is unchanged: directory coverage remains 28 entries /
11 SQL objects / 5,543 characters, and all exact projected/wire goldens pass.
Native extraction/rendering stays in the adapter. One neutral engine passthrough
now preserves the adapter's existing unsupported_form refusal label; no platform
noun, interpretation or parsing was added to the engine. Optional evidence is additional synthesis material, not directory content.

README/current status/progress are updated. Prior freezes are invalidated by
adapter bytes. No estate mutation, discovery rescan/re-approval, permission,
policy, credit, live investigation, provider call, fixture ticket or ledger row.
A subsequent authorized live run is still needed to establish actual native
reproduction; synthetic compiler tests are not that evidence. Stop after PR2.


A full suite passed 1,391 tests before the final oversized-integer guard. The
final 32 adapter tests and two generator tests pass after that guard; a final
full-suite rerun passed all 1,393 tests. CI now explicitly runs both declared-reproduction
modules, since the repository workflow enumerates test files rather than running
unittest discovery globally. The guard uses the shared exact-integer consumer
bound; it does not introduce a separate numeric allowance.


The final applicability guard requires a retained categorical List/Dropdown
slicer mode, one resolved column projection and matching saved-selection field.
A non-enumerable mode without an IN predicate still refuses the whole active set
rather than vanishing while page filters execute. The release-suite attempt
before this guard was interrupted and its log preserved; the final suite passed.


## Dated PR B correction: inventory is the source (2026-10-01)

The earlier adapter and 0b audit assumed completeness when a declaration kind was
not recognised. That claim is withdrawn, not removed from the historical text.
#296 merged the required neutral contract at `7ec4a40`. All four required pieces
are present on that main revision: the declaration inventory, conservation and
ACTIVE-coverage validation, consumer-owned volatility/assumption enums, and
engine-rendered saved-default qualifications. PR B rebases #295 onto that revision;
it does not change or extend those engine files.

Extraction first inventories native declarations from the selected report's
collected JSON parts. Each has a content/location-derived identity and exactly
one disposition. Unknown containers, visual kinds, predicates and applicability
remain UNSUPPORTED, including forms without a recognised IN predicate. The active
set is a flattening of ACTIVE entries' restrictions; no independent active-set
builder or reconciliation path remains. Collection status and eligibility are
separate: a DECLARED collection can contain an UNSUPPORTED entry, which the
engine refuses before either quantity read. Combined inventory bounds also
reach the consumer refusal without causing a preflight composition exception.

Bookmarks are recorded CONDITIONAL and excluded. Saved slicer defaults remain
ACTIVE with VIEWER_CHANGEABLE volatility and SAVED_DEFAULT assumption, selected
from the consumer schema. Reproduction qualifies the assumed saved positions;
non-reproduction explicitly names a moved saved-default selection alongside the
other retained open possibilities. Native provenance is opaque evidence; the
engine's neutral refusal identifies UNSUPPORTED_DECLARATION and the declaration
IDs. It neither interprets native kind strings nor forwards them into model
prose. The merged opaque-provenance test still checks identical engine behaviour
under two different native strings.

The original 32 adapter tests were reviewed. Unsupported-form tests now assert
inventory dispositions and the engine's pre-read gate, rather than confusing
collection status with eligibility. Prerequisite/target ambiguity tests retain
named early refusals. Compiler, explicit empty intersections, unfamiliar catalog
bindings, isolated reader attestation, cache/context checks and unchanged lower
filtered-scope refusal retain their original invariants. Fourteen additional
tests cover inventory derivation/conservation, unknown containers and the
permanent unfamiliar selection-bearing visual, volatility and qualifications,
and deliberately hostile producers. These producers omit ACTIVE coverage,
introduce untraced restrictions, omit/duplicate dispositions or inventory entries,
add UNSUPPORTED entries to otherwise valid sets, and emit invalid consumer enums.
Every such case is refused before a data read. No new visual-kind recognition was
added for the synthetic audit case.

An extraction-only check against the already collected context
`3ae7607b-5a5e-46c6-8e1b-195dbabc9cae`, revision 4, found four ACTIVE declarations
and five CONDITIONAL entries. Both slicer defaults are ACTIVE, VIEWER_CHANGEABLE,
and SAVED_DEFAULT. The five conditional entries are bookmark predicate nodes and
the bookmark index, not five separate bookmarks. The consumer validated this
inventory; no quantity was evaluated and no ticket was authored. PR3's reported
figure must be derived under the full active set including both saved defaults,
not merely page and visual filters.

Validation: all 1,432 regression tests passed in 275.391 seconds, including 46
adapter tests. All 392 local document targets in the four updated documents
resolved; git diff --check passed.
Planner goldens retain 28 directory entries, 11 SQL objects and 5,543 projected
characters. The adapter does not add planner-directory content. This is offline
compiler/contract evidence, not native reproduction or unfamiliar-domain acceptance.
No investigation run, model call, metadata read, estate change, permission, budget,
credit or ledger row. Earlier frozen attempts remain invalidated by adapter bytes.
