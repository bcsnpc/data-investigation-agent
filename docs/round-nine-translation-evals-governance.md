# Round Nine: translation, evals and governance

Started 2026-10-06, America/Chicago, from merged main `c96884c` (#419).
This is an implementation checkpoint, not completion of Round Nine.

## Offline translation checkpoint

The consumer-owned `TranslationProposer` interface accepts a closed proposal:
definition hash, kind, target engine, expression, discovered objects, canonical
grouping and the original run timestamp for relative definitions. It has no
verdict field. Object membership is checked before compilation; the platform
adapter must also resolve every expression reference through its governed compiler.
This module never executes expression text directly.

The verifier compiles both plans before admitting any probe. Filter witnesses
require complete selected key sets, explicit adapter normalization, and a
length-framed binary SHA-256 hash plus count. Typed keys distinguish null, zero,
text and boolean; duplicate keys and truncated sets refuse. A same-surface filter
check requires the same engine/connection/object. Measure witnesses require at
least three distinct retained cell addresses and an independently attested
boundary. Original results, context, addresses and quantity-bound surface
attestation are checked, rather than accepting wrapper annotations.

Equal comparisons produce VERIFIED only for their recorded scope/sample;
unequal comparisons preserve both observations as FALSIFIED. Compilation,
execution or evidence failures remain UNVERIFIED. All remain
SNAPSHOT_UNVERIFIED; sampled agreement does not prove global equivalence.
Probes use the existing approval-verification budget class, not investigation
diagnostics. Physical admission still belongs to the isolated adapter route.

An extra measure cell uses an existing, natively addressed original cell
observation plus one new proposed-side probe. Missing or differently addressed
native evidence refuses; it is never retrospectively rebound. The append-only
translation ledger checks receipt seals and recomputes successful/falsified
verdicts. Cache reuse is definition/context/metadata/scope/time/cell specific;
changes expose STALE without editing history. A later failed reverification
prevents reuse of the earlier successful entry for that cell.

Thirty-two focused tests pass with SQLite in memory and synthetic query-bound
receipts; zero estate/network/provider requests. Independent native definitions
and deliberately wrong candidates cover Top-N, a pinned date window and an
ALL-like measure across three retained cells. These test the verifier and
contract, not the live model's first-proposal quality or a platform adapter.

## Integration finding and remaining work

The existing lineage proof contract (`lineage_binding.verify` and
`binding_sample.verify`) establishes bounded quantity/profile witnesses, not
row-key mapping. The manifest's `lineage.bindings` carries layer IDs and declared
provenance, not a verified column-key map. Treating either as a verified key
binding would promote sampled agreement into unsupported row identity.
The draft now requires a separate complete-key witness for cross-boundary filters:
an explicit ordered column correspondence with declaration provenance, original
query-bound receipts on both independent surfaces, matching complete normalized
key universes, retained context, scope and both definition hashes. Unknown columns,
stale or falsified proofs and selected keys outside that universe refuse. This
bounded witness does not establish global semantics or aligned snapshots. It does not
declare the new capability or bypass existing UNSUPPORTED restrictions.

The provider wire derives its supported structure and stated bounds from the
consumer schema. Verification answers are removed from model input. Translation
model calls use existing reservations, failure usage and recording; the service
preserves falsifications and reuses current cell proofs without a model or read.
New-cell verification still requires the original addressed native observation.
The existing physical query admission now recognizes closed translation and
key-binding addresses; no absent address becomes a baseline.

Still required for section 1: adapter-governed native/proposed compilation and
result extraction, live key-binding production, and investigation runtime wiring. The
section 1e report is provisional until these integration tests exist. No live
Top-N/date/measure trial has occurred.

Sections 2–7 (golden model-step evals, OTLP converter, governance/retention/
redaction, rebuild plan, bounded live verification and demo command) have not
been implemented in this checkpoint. No fixture, permission, identity, secret,
policy, approval context or acceptance expectation changed.

## DECIDED WITHOUT REVIEW

- Begin with a separate default-unused verification core; do not make the
  investigation consume translations before adapter integration is proved.
  No existing planner payload builder changed, so directory and SQL-object
  coverage and payload characters are unchanged by this checkpoint. Future
  wiring must measure all three and add the standing coverage regression test.
- Do not reuse bounded lineage profiles as key-binding evidence. The alternative
  would falsely certify selected-row equivalence from aggregate agreement.
- Use a separate complete-key witness with an explicit discovered-column mapping;
  never infer correspondence from equal aggregate totals or similar column names.
  It stays limited to the recorded universe and scope.
- Derive provider wire structure and bounds from the consumer contract. The
  installed Azure route strips unsupported wire keywords while retaining local
  validation and stating those exact bounds in instructions; it never strips fields.
  See [official structured-output guidance](https://developers.openai.com/api/docs/guides/structured-outputs).
- Preserve query-bound snapshot requirements and refuse missing extension-cell
  addresses. Standalone metadata or address backfill would weaken prior rulings.
- Round Nine's authorized pot is 200 with 40 reserved and rolling limit 1,500.
  No live admission or credit grant has occurred, so no budget configuration or
  discovery approval has been changed yet. Round Eight's closing rolling usage
  of 363 is historical, not a current measurement.

Engine bytes changed; all prior freezes remain invalid. No unfamiliar-domain,
live translation or general capability acceptance is claimed.

## Validation and budget record

The first full discovery sweep ran 2,076 tests and failed with eleven errors.
Ten were TAPE_UNCOMMITTED_ENGINE and one was Engine or connection changed:
the sweep began while draft engine files were being edited. This is a preserved
failed check, not a regression pass. After committing a stable checkpoint, the
affected tape (28), code-definition (5), repository-code (3) and adaptive (33)
suites passed; proposer tests (11) also passed. The final translation suite
passed all 24 tests, including malformed attestation refusal. These are targeted
reruns, not a claimed clean full 2,081-test sweep.

The initial replay sweep used an absent archived-input directory and reported
MISSING_PRIVATE_REPLAY_INPUTS. Its log and output remain preserved. A corrected
sweep uses `.local/round-five-i-20261005/inputs` and the pinned inferred inputs.
Both sweeps are still running at this checkpoint; no 15-by-2 pass is claimed.
PR #420 remains draft; hosted checks are pending, no merge.

At 2026-10-06T22:53:50Z (5:53 PM Chicago), the existing rolling physical window
is 315/1,500. Natural expiry lowered it from Round Eight's historical 363;
no reset or refund. Round Nine has spent 0/200, with 40 authorized for reserve
but not yet installed as batch credits or round policy. Investigation cap stays
12; diagnostic and provider calls are zero. The existing Round Eight reserve
remains untouched. Failed and successful test records were appended to the ledger.


## Dated integration checkpoint (2026-10-06)

Stable commit `8de0e84` passed 2,089 regression tests in a separate committed
checkout (697.063 seconds, exit 0). Seven hosted checks passed, including replay
37545322267. This does not cover subsequent adapter/tracing changes. The initial
failed sweep and wrong-input replay attempt remain preserved.

Thirty-nine focused translation tests pass: 32 core/provider/service, four native
filter adapter and three measure-route tests. Adapter tests use actual governed
compilers/receipt storage with injected transports, not live engine evaluation.
Empty key sets retain a marked attestation row excluded from the key hash.
Truncated sets refuse. Three measure cells retain independent addresses;
disagreement falsifies. Provider admission uses the wire's same input projection.
New-cell extension without an existing candidate refuses before a model call.
Retained Top-N/date native compilation and runtime activation remain pending;
the filter route requires an independent compiler from its caller.

The file-only OTLP exporter validates official generated protobuf definitions
and span-tree/time invariants. Four tests pass; fifteen-tape export is in progress.
SQL physical requests may link only at logical completion; guards carry separate
receipt IDs. Export preserves those links and sealed event pointers. Missing
receipt IDs remain UNRECORDED. Family A exports all ten physical probe spans.
Historic finer source/reproduction timing was not recorded and is not invented.
A technical stage-cost footer helper exists but live output wiring is pending.

DECIDED WITHOUT REVIEW: pin official generated OTLP definitions in a separate
tracing requirements file; export locally, with no collector or external upload.
Local dependencies were installed in an isolated directory, leaving the existing
protobuf installation unchanged. See [OTLP file export](https://opentelemetry.io/docs/specs/otel/protocol/file-exporter/)
and [protocol package](https://pypi.org/project/opentelemetry-proto/1.45.0/).
Historic currency cost is UNRECORDED: token counts lack a pinned price. Stage
cost/time is inclusive where only top-level operations were recorded.

Zero Round Nine estate reads/provider calls; no fixture, identity, secret or
policy change. Prior freezes invalidated. PR #420 remains draft, unmerged.

Dated trace export completion: all fifteen archived tapes converted and passed
official schema/tree validation, zero new estate requests. Their 139 probe spans
match every retained physical total; family C did not retain a physical total.
Original tapes remain untouched. Export files and detailed totals are private
under `.local/round-nine-20261006/trace-export/`. Live footer wiring remains pending.
