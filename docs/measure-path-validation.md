# Measure-path validation and contribution-test capabilities

Updated 2026-09-24. Tracking: [#193](https://github.com/bcsnpc/data-investigation-agent/issues/193).
This implements the reviewed #224 proposal on the known-domain reliability branch.
It is not a frozen or unfamiliar-domain acceptance result.

## Delivered behavior

`LOOKUP measure_path` projects the selected measure, its parsed DAX references,
bounded table/column metadata, exact graph edges, relevant definition handles and
explicit gaps. Every returned relation retains its provenance. Partition entity,
schema and expression-source labels remain definition facts; the lookup never joins
them to another asset by name. The projection is capped at 24 references/edges,
eight definition handles and 12,000 encoded characters.

The SQL/DAX capability advertisements now name two generic operations:

- `reproduce_measure` submits planner-authored DAX for the selected measure and
  declared ticket scope through the existing DAX compiler, reader policy and
  receipt path. On an unseen model, the measure ID comes from intake and the query
  must compile against that model; no measure name or expression template is built
  into the engine.
- `test_contribution` takes the selected measure and a planner-selected discovered
  upstream object. The planner still authors the diagnostic. The existing SQL or
  DAX compiler must resolve the declared object in the compiled read before normal
  dispatch admission. On an unseen estate, the object must come from its discovered
  catalog; there is no table, join, layer or ticket-family branch.

These labels do not grant permission, certify equivalence or force an action order.
A synthetic regression runs a contribution test before measure reproduction. The
planner payload reports completed reproduction and contribution counts solely for
observability. `score_run.py` and the append-only ledger expose the same counts.

The support contract now asks current providers to state whether mechanism-to-measure
connection is established, not asserted, or blocked by scope, capability, permission,
budget or eligibility. A cause label needs either cited connection evidence or a
specific establishment barrier. Uncertainty may remain `NOT_ASSERTED`. Historical
saved assessments retain their earlier readable contract.

## External-source binding result

The earlier eight item-relations reads already included both directions for the
model, report, notebook and Gold lakehouse. They returned model/SQL-endpoint,
report/model, notebook/Gold and endpoint/Gold relations, but no external Azure SQL
source relation. Reinspection of the retained notebook definition found embedded
Silver inputs and the Silver-to-Gold transformation; it did not contain code that
loads Silver from Azure SQL or a stable application-object identity. Therefore no
`INFERRED_FROM_CODE` edge can be created honestly. The lookup exposes
`UNRESOLVED_EXTERNAL_SOURCE_BINDING`; similar SQL object names remain unbound.

The dependency-map proposal is deferred indefinitely: the audit found four of the
five requested hops already present, and this bounded view makes them salient. The
optional metadata-collector designs remain unimplemented. No Write grant, execution
reader elevation, Microsoft runtime adapter or permission change was made.

## Context cost and validation

The retained corrected G S1 first call measured 28 directory entries, 11 SQL
objects and 15,067 pre-wire payload characters. Adding the named capability
descriptions and two zero-valued progress counters produces 28 entries, 11 SQL
objects and 15,971 characters: **+904 characters**, with no directory loss. The
lookup itself is on demand and adds nothing to the initial payload. A golden-view
regression asserts directory and SQL-object coverage before and after the added
context.

**1,035 local regression tests passed.** Tests cover unseen synthetic names,
bounded identity-only path projection, contribution-target compiler binding,
sequence independence, progress/score/ledger signals, support admission and
historical assessment compatibility. The nine recorded G trials remain next;
failures and partial results will be preserved under `KNOWN_DOMAIN_REGRESSION`.
