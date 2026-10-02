# Explicit absence, reported states and attestation coverage

Date: 2026-10-02 UTC. Parent: #298, `bdbbf22`. This is one absence/value work item,
as explicitly requested. Draft #297 and its historical evidence remain intact.

## Before-code Family D attempt

The existing ticket was submitted unchanged on `bdbbf22`, before any engine
changes. Intake `27a21705-5712-4edc-beb3-19d767ffd7c7` stopped at NEEDS_INPUT:

> What exact warehouse identifier or value does the report filter use for “North” (for example the warehouse_name text or a warehouse_id)?

Business output: **not generated**. Technical output: **not generated**. Synthesis
never ran, so there are no narrative outputs to quote. No investigation session
was created and no outcome was classified. The ledger records NOT_INVESTIGATED,
not NO_COMPARABLE_PATH or a successful refusal-attribution test.

| Resource or evidence | Observed |
| --- | --- |
| Intake model calls | 1; 13,787 input and 76 output tokens |
| Investigation planner / synthesis calls | 0 / 0 |
| DAX / SQL / estate metadata reads | 0 / 0 / 0 |
| Diagnostic / physical / guard requests | 0 / 0 / 0 |
| Probe execution surfaces and attestation | NOT_RUN |
| Rolling ordinary reads before / after | 8 / 8; allowance remains 60 |

The expected single DAX request was not reached. Neither an inventory complaint
nor a target-ambiguity refusal was observed: **#298 remains unverified live**.
There was no replacement run, inferred warehouse field, intake bypass, policy
increase or credit grant. The request/response and usage snapshots are preserved
under `.local/absence-contract-20261002/`; one ledger row was appended. Run
`6582f4a1` and its row in draft #297 were not changed.

## The contract fixes

`Probe` no longer defaults its measured result to None. Its absence is a typed
`NoValue(NOT_OBTAINED)` or `NoValue(FAILED)`. An OBSERVED probe cannot be constructed
without an explicit measured value and receipt identity. Explicit None, or a
normalized quantity containing None, is measured BLANK; zero is measured zero.
An UNAVAILABLE probe cannot carry a measured result. Rejected attestation keeps
the original read evidence but gives the probe an explicit failed value state.
Typed result cells missing their value field are rejected, not normalized to BLANK.

The reported-figure consumer owns closed NUMBER, EMPTY and UNSPECIFIED variants.
NUMBER and EMPTY require exact character offsets and the verbatim ticket span.
The intake wire supplies candidate spans; the consumer derives the number and
precision instead of letting a producer choose a tolerance. Multiple plausible
spans refuse with a named clarification. Interpretation of which spans are
plausible remains model judgment and user-reviewed evidence, not semantic proof.
Dates, identifiers, thresholds and unrelated quantities are not automatically
reported figures merely because they contain digits.

An exact number compares exactly. Decimal digits and a stated K/M/B scale determine
the digit position for reduced-precision comparison. Rounding is nearest digit,
ties to even, stated explicitly in both outputs; a reduced-precision match is
qualified as weaker than an exact match. An approximate integer without
determinable stated precision refuses. No tolerance is supplied, widened or
inferred. EMPTY compares with native BLANK and never with zero. UNSPECIFIED gives
the no-reported-figure unavailability before extraction or inventory validation.
An omitted state is a contract absence, not UNSPECIFIED and not EMPTY.

The schemas are extended explicitly at intake, review and envelope validation.
Reviewed figure evidence cannot be replaced by an unreviewed preview field.
Definition-target selection and the final procedure forwarding remain the next
wiring work; this PR does not claim that production intake now executes a
reproduction. No additional estate run or fixture change was performed.

## What partial attestation buys

Attestation now has separate consistency and coverage. MATCHED means full
coverage. PARTIAL means every reported/required field agrees while other declared
fields remain unattested. Missing required identity or any contradiction refuses;
partial is not a fallback for either failure.

Within-layer reproduction may use PARTIAL: two complete, governed receipts must
use the same declared engine/connection/object, the same self-reported account,
the same measure and the exact compiled restrictions. It establishes only what
that declared route returned under those selections. Every unattested field and
saved-default/precision assumption remains qualified. It does not establish the
server's model identity, currency or an independent boundary.

PARTIAL is **not sufficient for CROSS_SURFACE_VERIFIED**. Both surface triples
must be established by their own answers, not merely selected by the client.
Incomplete coverage records NOT_COMPARABLE with
SURFACE_COVERAGE_INSUFFICIENT_FOR_CROSS_SURFACE_COMPARISON. Outcome validation
also requires full coverage and matched consistency. This is a substantive
eligibility restriction: the current Microsoft adapter cannot produce a new
verified cross-surface boundary with its present self-report routes. Synthetic
positive comparison tests now use a producer that actually reports all fields;
separate hostile tests preserve the identity-only refusal.

The current DAX route reports identity through USERPRINCIPALNAME. The documented
[Execute Queries response](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries)
contains rows/results/errors/labels, not a query-bound engine, workspace or model
identity; it explicitly excludes INFO and DMV queries. The dataset ID in the
request URL is a client declaration, not a server self-report. Thus this adapter's
DAX probes are permanently partial under that route contract. Metadata exists
through other interfaces, but [INFO metadata permissions](https://learn.microsoft.com/en-us/dax/info-functions-dax)
and the previously tested XMLA refusals do not establish a reader-accessible,
query-bound replacement. This does not assert that every future interface or
platform lacks self-attestation. No new platform probe or permission was used.

Historical MATCHED labels, boundary records and outputs remain exactly as recorded.
Their unattested fields were always present; the new policy does not retroactively
turn those client declarations into full server evidence.

## Sweep and disposition

| Site | Finding and treatment |
| --- | --- |
| Probe result / receipt | Omission collided with BLANK; explicit absence and mandatory measured receipt now prevent it. |
| Typed quantity cell | Missing value became None; omission now rejects, explicit null stays BLANK. |
| Reported figure | None conflated missing figure with empty result; closed states, provenance and stated precision now distinguish them. |
| Attestation | Partial field agreement looked fully MATCHED; consistency/coverage separated and eligibility explicit. |
| Inventory active set | Missing restrictions defaulted to []; now the consumer rejects omission, while an explicitly empty set remains distinct. Conservation/disposition/unknown-form enforcement remains unchanged. |
| Declared source partition | Missing source_type was accepted as entity; explicit entity declaration is now required for faithful compilation. |
| Presentation/definition judgment | Missing status could count as a completed negative check. Explicit COMPLETED, a boolean judgment and evidence are required; omitted/unknown judgment cannot explain or exclude a mechanism. |
| Job-history check | Missing status or evidence could silently pass the competing-explanations gate; explicit successful completion evidence or explicit nonapplicability is required. Existing failed/in-progress/not-run timestamp classification remains. |
| Ingestion | An available commit was labelled CURRENT. Now explicit commit path/content are required for COMMIT_OBSERVED; neither completeness nor currency is asserted. Missing content is UNAVAILABLE; timestamp zero remains a legitimate value. |
| Freshness / baseline / optional snapshot | Different: absence already becomes NOT_ESTABLISHED, UNAVAILABLE or SNAPSHOT_UNVERIFIED, never current or verified. Matching explicit context remains mandatory for comparison-based freshness. |
| Bindings and retrieval hints | Reviewed/scoped resolution is still required for execution. Same-name feedback is explicitly a retrieval hint, not a binding or permission. Missing schema is UNKNOWN; absence is not inferred equivalence. |
| Empty restriction intersection / empty result table | Different: these are explicit collected values, not omitted fields. Empty IN stays a real predicate; a non-scalar table remains a table, not a scalar BLANK or zero. |
| Observation envelope defaults | Different: the engine records completion of its own observation construction, not a missing upstream measurement or judgment. Upstream probe/result and judgment eligibility are checked separately; an absent evidence object produces no observation. These defaults cannot supply a measured value or an eligible omitted judgment. |

Hostile-producer tests cover omitted value/receipt, explicit absence, BLANK/zero,
omitted figure state/provenance, two candidates, widened precision, omitted active
set, missing completion evidence/status, incomplete commit responses and partial
self-reports. Existing inventory hostile-producer and filtered-lower refusal
tests remain. No domain mapping or expected fixture value was added to the engine.

## Context cost and validation

The investigation planner's directory/projector was not changed. Its golden
directory retains 28 entries and 11 SQL objects; the existing golden coverage
tests still assert those counts. Intake payloads across all twelve immutable
synthetic cases remain byte-identical: 1,050–1,952 characters before and after.
Family D is 1,103 / 1,103. The response schema grows from 1,350 to 1,661 characters
for the single-model cases; the added instructions/schema are contract cost,
not per-object directory cost. Model/column counts are unchanged. The tests
explicitly adapt response copies; captured fixtures and recorded tapes are not edited.

Validation is recorded on the implementation PR, including the full regression
suite and six required CI checks. Intermediate failed test runs remain in local
logs. One Windows subprocess-budget test failed in a full run and then all 18
budget tests passed in isolation; no budget, cap or timeout was raised to make
that test pass. Final checks are required before merge.

Engine bytes changed: **all prior freezes are invalidated**. There is no fresh
freeze, unfamiliar-domain acceptance claim or successful live reproduction.


## Dated finding: reader self-description (2026-10-02, America/Chicago)

The [least-privilege probe set](surface-self-description-probes.md) supersedes the earlier
claim that the Microsoft reader routes cannot report engine/connection/object
metadata. SQL served its engine/version, session ID, network address and
protocol. Both REST/DAX INFO.PROPERTIES and XMLA DISCOVER_PROPERTIES served
OLAP Server, version 17.0.91.20, server name and catalog; REST/DAX returned
the model GUID, XMLA its name. ProductName/ProductVersion filters returned
empty, then property-name enumeration found the actual descriptor names.
XMLA session/connection DMVs were permission-refused; those failures do not
make all property metadata unavailable. Old receipts remain partial because
they never asked for these fields; retrospective corrections merged in #300
remain true. Current #299 FULL-coverage validation is unchanged.

Thirteen metadata query requests were recorded: 3 SQL, 4 REST/DAX, 6 XMLA;
ordinary rolling use 8 to 21 of 60. No retries, credits, cap/policy/config
changes, grants, fixture changes or investigation model calls. The report
proposes demonstrated difference on comparable query-bound self-reported
fields with explicit omissions; this is a proposal, not an implemented
standard or a requalification of any historical outcome. Intake and wiring
remain queued; draft #297 and Family D evidence remain unchanged.
