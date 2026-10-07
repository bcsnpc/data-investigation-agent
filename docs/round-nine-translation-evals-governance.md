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


## Governance/retention offline checkpoint (2026-10-06)

The governance table now maps implemented controls, evidence and human approval
points, explicitly distinguishing unfinished redaction and region work from
existing output vocabulary validation. The manifest optionally declares tape
and ledger retention; omission means indefinite, preserving old manifests.
`python scripts/dia.py retain` plans without mutation; `--apply` explicitly
expires files/rows and durably audits original hashes separately. Unknown dates,
unfinished tapes and unfamiliar sidecars stay. Changed hashes refuse before
mutation. Seven retention tests and nineteen existing manifest tests pass.
Tests delete only temporary synthetic files. No fixture tape or ledger row has
been removed, no fixture manifest or approval changed. New retention fields do
not enter planner payloads; the manifest coverage test still reports 2 directory
entries, 1 SQL entry and 7,563 payload characters before/after.

DECIDED WITHOUT REVIEW: retain undated/unfamiliar evidence rather than estimating
an expiry, keep deletion audit separate from the expiring ledger, and require an
explicit apply command. Retention is not a licence to alter sealed replay inputs
or immutable release bundles. Column redaction, provider-region pinning, evals,
rebuild, demo and translation runtime/native-definition wiring remain pending.


## Native definition and validation checkpoint (2026-10-06)

Commit `4e61a5e` passed all 2,100 regression tests in an isolated committed
checkout (604.466 seconds, exit 0). Newer native-definition and retention code
has focused validation, not a claimed full-suite pass. The corrected pinned
local replay sweep passed archived15/15 and inferred15/15 with zero estate
requests. The original wrong-root sweep ended archived0/15 (missing inputs),
inferred15/15 and is preserved unchanged.

The native filter adapter now independently compiles a narrow retained PBIR
Top-N subquery and day-relative Between form. Six definition tests pass;
translation total is45. Top-N requires the definition's own final key ordering,
refusing an unestablished tie-break. UTC anchor and day offsets become fixed
literals; a day-span on the column is preserved, while a bare timestamp column
never gains rounding. Additional active context, calendar units and unfamiliar
forms refuse until compiled faithfully. Malformed collected declarations refuse
rather than crash. No unsupported inventory entry is reclassified as active;
these separate verification routes are not enabled in the investigation walk.

The first new tests had two incorrect compiler-interface expectations (parent
table IDs and an absent volatility field); the first attempt failed with one
failure/one error, the second with one error. The tests now assert actual bound
member IDs and non-null compiled identity for the frozen date query. No compiler
behavior was weakened. Final45 focused translation tests pass.

DECIDED WITHOUT REVIEW: use Microsoft's retained PBIR semantic-query schema,
not the differently shaped embedded-report SDK serialization. Refuse unspecified
Top-N tie ordering and additional context rather than inventing either. Published
relative-date filters use UTC; pin that anchor, preserving exact declared date
span semantics. Sources: [PBIR visual schema](https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json),
[filter schema](https://developer.microsoft.com/json-schemas/fabric/item/report/definition/filterConfiguration/1.2.0/schema-embedded.json),
[semantic query schema](https://developer.microsoft.com/json-schemas/fabric/item/report/definition/semanticQuery/1.3.0/schema.json),
[relative-date semantics](https://learn.microsoft.com/en-us/power-bi/visuals/desktop-slicer-filter-date-range).

No estate reads or provider calls, fixture/configuration/identity changes, or
budget admission in Round Nine. Runtime wiring, complete binding production,
evals, redaction/provider-region, rebuild/demo and live verification remain
pending. Draft #420 remains open; no freeze or acceptance claim.


## Dated correction: translated measure cell scope (2026-10-06)

Audit found a defect in the draft measure route: it applied a keyed restriction
on native DAX but reused the complete proposed SQL unchanged. The injected
transport returned the same constant for both, so the three-cell route test
passed without demonstrating faithful source scope. That earlier test result
remains historical; it did not establish scoped translation. No live read or
persisted investigation proof used this default-unused route.

The route now refuses any nonempty base/cell restriction before reads until
verified column bindings can compile it on SQL. A permanent test checks zero
reads and zero verification budget charged for the keyed three-cell sample.
Unrestricted native/SQL probes still retain their original addressed values;
that transport test does not claim three-cell verification. Generic core tests
continue to exercise independently evaluated three-cell verification and
falsification. Forty-five translation tests pass after the correction.

The revised negative test also exposed misuse of revalidate() on UNVERIFIED
compiler refusals: there are no observations to replay. It now explicitly rejects
those as having no observation proof; the ledger already only revalidates
VERIFIED/FALSIFIED evidence. The intermediate test error is preserved below.
Existing lower-walk filtered refusal stays untouched. This is a capability gap to
build, not a reason to stamp an unfiltered statement with a keyed cell address.
No live section6 trials begin while their faithful scope wiring is incomplete.


## Pinned demo entry point (2026-10-06)

`python scripts/dia.py demo --manifest <estate.json> --case <acceptance-case.json>`
starts the existing loopback workspace after selecting the exact approved
fixture context and pinning every consumer. Execution defaults off; `--live`
explicitly enables existing governed execution. It uses the existing local
INVESTIGATOR_WORKSPACE_TOKEN, never creates a secret or retrieves a provider key
in read-only mode. Four tests cover refusal before serving, pin ordering,
read-only behavior and required case selection. The server was mocked; no local
or cloud service was started. Live stage/binding displays still need work; this
command alone is not the full demo-readiness milestone.

At23:59:13Z, rolling273/1500 with1227 available; natural expiry, no reset/refund.
Round Nine0/200,40 authorized reserve not configured, investigation cap12. The
previous Round Eight restoration credit is untouched. No new provider or estate
request, fixture state, approval context, identity, secret or policy change.
Current corrected engine624ca67 has a full committed regression sweep running;
its result is not yet claimed. Separate earlier4e61a5e pass remains historical.

### Provider terms, 2026-10-06 America/Chicago

Three offline tests passed: closed region provenance, explicit unknown legacy region, whole-hash invalidation. Manifest-backed recorder configuration now carries provider/deployment/endpoint/region without credentials. The fixture was not modified and its region remains UNDECLARED; old tapes remain UNRECORDED, never retroactively attested. Nineteen manifest tests passed: directory 2?2, SQL 1?1, payload 7,563?7,563 characters. No estate/provider call, scope change or policy change. Prior freezes remain invalid. DECIDED WITHOUT REVIEW: retain legacy manifests with explicit unknown region instead of guessing it from an endpoint. New declared regions require cited owner deployment evidence.

### Stage and ledger views, 2026-10-06 America/Chicago

The isolated committed 624ca67 engine passed 2,113 tests in 593.676 seconds. Subsequent stage-observation changes have four focused tests, the OTLP converter five, binding display two, and the workspace 24. START is saved before a procedure call so polling sees progress while the call runs; FINISH preserves the actual exception type. Stage attribution never changes calls, values or eligibility. New trace stage attribution uses these saved events; old tapes retain inclusive WALK timing rather than inventing source/reproduction timings. The existing technical screen lists recorded ledger locations, verdicts and both original quantities/profiles, with current eligibility explicitly NOT_EVALUATED. Browser verification and live narrative footer remain pending. No estate/provider read, credential or scope change. Freeze invalidation remains. DECIDED WITHOUT REVIEW: display recorded ledger verdicts separately from runtime eligibility; a read-only view cannot establish code freshness without a fresh proof.

### Technical stage footer checkpoint, 2026-10-06 America/Chicago

Manifest-backed recordings now append and persist one engine-rendered cost/time footer after the recorded synthesis operation ends. It uses the exporter arithmetic on already recorded events and original returned state; no new clock, query, provider call or price. Recorded provider/deployment/region provenance also reaches trace attributes. Seven trace tests and one real-SQLite persistence test pass. Both return views and subsequent reads agree, business prose and observations unchanged, repeat attachment does not duplicate it. Historical tapes remain untouched and their producer configurations do not enable the footer. Replay performs the same declared footer step using only consumed events; no future event is read for its counts. Currency cost remains explicitly unrecorded because no installation price is pinned.

A 34-test synthesis check had one failure: its last setup returned ADMISSION_CHANGED instead of BUDGET_LIMIT while engine files were being edited concurrently. This check is preserved, not counted as passed. A stable committed rerun follows. No estate/provider calls or policy change; prior freezes invalid.

### Intake goldens and stable synthesis, 2026-10-06 America/Chicago

The committed 7ab0c0b synthesis suite passed all 34 tests with no concurrent edits, after the retained admission failure. Sixty intake texts and structured expected records are explicitly authored in acceptance/model_steps/intake.json, with all nine families, all nine subjects, typos, forwarded noise, selection versus subject, numeric/EMPTY/unspecified figures, grouping and six semantic holds. Four scorer tests pass. The CLI accepts --model-version, reports per-field accuracy, retries, holds, separately expected/correct semantic holds and the score delta. Missing cases fail and mixed model versions refuse. No actual provider evaluation or accuracy score is claimed. Reader/synthesis/translation model-step sets and human readability flags remain pending.

DECIDED WITHOUT REVIEW: provisional score-drop ratchet two percentage points, with a reason in acceptance/model_steps/thresholds.json; not a production-quality or statistical guarantee. No model call, estate read, policy or scope change. Prior freezes invalid.


Dated scorer-integrity refinement, 2026-10-06 America/Chicago: provider/transport
HELD earns zero field credit, including null expected values. Every score pins
the canonical golden-set SHA-256, and changing expectations invalidates baseline
comparison. Four focused scorer tests pass. No provider evaluation or model
accuracy is claimed; zero model calls and estate requests.


Dated stable integration validation, 2026-10-06 America/Chicago: isolated
commit `5907162` passed all 2,134 regression tests in 373.661 seconds.
The later scorer-integrity refinement passed its four targeted tests.
This establishes offline regression health, not model accuracy, browser
behaviour, translation activation or live acceptance. Zero Round Nine estate
requests and provider calls; authorized pot remains unconfigured.


Dated model-evaluation checkpoint, 2026-10-06 America/Chicago: nine reader code
cases now carry authored expected bindings (three Round Six synthetic examples,
six new dynamic-name/UDF examples). The first test assumed two constant-name
forms required a model; both already compile statically. That failed assertion
is preserved and corrected to check their exact authored static bindings. The
other four new examples require fallback. No provider score is claimed for this
set. Precision/recall counts invalid and duplicate proposals, before verification.

The fifteen sealed inferred-column tapes yielded fourteen composition responses,
plus family C's explicit no-call case. Current wire/form/token checks pass13/14:
92.857% validity and7.143% rejection; no prior score delta. Source-latency's model
paragraph uses an unqualified "semantic layer" despite supplied role tokens; the
earned output used deterministic delivery wording. This is an independently
recorded response's validation failure, not a failed earned outcome, and not
causal correctness scoring. Originals and gate expectations remain unchanged.
Ten exact paragraphs and checked boundary facts are exported for HUMAN review;
all three flags per item are null, no grader or fabricated human score. A human
input request is pending while independent offline work continues.

Sixteen focused evaluation/path tests pass. A test insertion first misplaced
four human-grade assertions, producing NameError; that failed check is retained,
and the corrected same assertions pass. Zero Round Nine provider or estate calls.
The complete regression checkpoint remains5907162/2134. Model-step release gate,
new provider scores, translation activation, redaction and rebuild remain pending.


Dated intake-evaluation runner and budget checkpoint, 2026-10-06 America/Chicago:
the synthetic-catalog runner uses the original intake procedure (including its
single correction paths, validators and settlement), the existing governor and
real durable usage counters. No native/source transport or investigation can
execute. Its integration test plus24 workspace tests pass25/25 with injected
responses; this is not a provider score. The plan reports60 cases, at most120
metered model calls, zero estate requests; it loads only the existing local Azure
credential mechanism and creates no identity, permission or secret.

The authorized Round Nine200/40-reserved pot is now declared in a new private
manifest, with the original Round Eight manifest unchanged. Rolling allowance1500,
investigation cap12 and daily model allowances are unchanged; counters were not
reset. Configuration before/after and hashes are in the ledger. New manifest hash
83dcf739486e99ae63b5b2c7fe1234c4269308deee47fd1e0094dd09f5a76665.
No discovery reapproval has occurred: this local configuration is not execution
authority for estate reads. Local rolling observation254/1500 at00:52:45Z,
model reservations0 for the new UTC day; Round Nine estate/provider spending0.


Dated first intake evaluation, 2026-10-06 America/Chicago: all60 cases ran once
against the authored synthetic catalog, through the original intake validation
and settlement path.53PROPOSED,6NEEDS_INPUT,1HELD; no correction retries and no
replacement. Overall authored-field match94.861%, question kind83.333%,
triage fields88.333% each, filters91.667%. All six should-hold cases did so.
The first-baseline/drop-only scorer says PASSED because all cases were attempted
and no earlier delta exists; that is NOT an adjudicated accuracy pass or the
complete four-step quality gate. No expectation was changed to match responses.
Triage expectations for plain component/freshness questions, and empty filter
expectations for explicit column selections, require review against the consumer
instructions. Compound source/discrepancy questions also overlap the current
subject vocabulary. The v1 score, full synthetic results and its hash are retained.

G3's original HELD/RESOLUTION_UNCERTAIN is preserved. Its provider returned
HTTP200/status completed,167 output tokens, not an output or transport failure.
An offline replay of the exact structured response raises:
`ValueError: Only a quoted SELECTION may enter measurement scope`.
The response labelled900099 MENTION and IDENTIFIER, yet also supplied it as
`target_request`; it was refused before any preview/read. The guard prevented
inventing a selection. This diagnostic makes no replacement response or refund.

Exactly60 model calls,136753 input tokens,7096 output tokens,143849 total tokens;
served reasoning tokens0. The intake wire used its existing1500-token default
and no explicit reasoning setting, rather than the investigation profile's
8000/medium settings. No setting was changed to improve this score. Charged
output reservations90000 are distinct from actual output7096; counters retained.
Existing credential lookup used the existing local Azure mechanism, with no
credential or scope created. Round Nine physical estate requests0/200,40 reserved;
rolling248/1500 at the saved batch close. Original negative/partial responses,
sealed tapes and one ledger row per evaluated case are retained.


| Step | Recorded model/deployment | First score | Delta |
| --- | --- | --- | --- |
| Intake | investigator-quality-54 |94.861% authored-field match,60cases; six intended holds, one unexpected hold; expectation review pending | No prior baseline |
| Reader MODEL extractor | Not run | Nine code cases and scorer prepared; no provider precision/recall claimed | Unavailable |
| Synthesis | investigator-quality-54 |13/14 current token/form validity; family C has no model paragraph; ten human reviews ungraded | No prior baseline |
| Translation proposer | Not run | Synthetic verifier tests exist; first-proposal model score pending | Unavailable |


Dated reader-evaluation admission, 2026-10-06 America/Chicago: isolated 5f09cec regression passed 2167 tests in 368.972s. MODEL evaluation shares the runtime consumer-derived schema and candidate validation, preserves rejected raw proposals, seals every attempted case, and stops on budget admission without replacements. Eleven focused tests passed; one initial test assertion confused the unchanged const MODEL wire with an enum and was corrected, not the runtime contract. Nine provider calls maximum; no binding verification or estate reads. Existing medium/8000/120 profile is retained. The extraction refactor changes no wire payload.


Dated reader MODEL negative baseline, 2026-10-06 America/Chicago: nine cases
attempted once, all HTTP400 before extraction. Exact retained provider error:
`Invalid schema for response_format 'transformation_code_proposals': In context=('anyOf', '0', 'properties', 'kind'), schema must have a 'type' key.`
This is a producer-schema defect, not nine incorrect extraction decisions.
Precision/recall/F1 are zero; correct semantic refusals0/2; provider failures9.
The initial drop-only score incorrectly said PASSED. An append-only correction
records FAILED; provider failures now fail even a first-baseline gate.
Original tapes, rejected responses, reservations and initial score stay unchanged.
No replacement provider request has been made. Nine8000-token reservations are
charged, with no reported actual token usage and no refunds. Combined UTC-day
model reservations69, output reservations162000; Round Nine estate0/200 with40
reserved, saved rolling197/1500 (window expiry, not reset).

DECIDED WITHOUT REVIEW: add explicit string types to consumer-owned binding
kind/extractor/join vocabularies and their fixed wire identity fields. This
preserves accepted values and derives the provider wire from the same contract.
A recursive test refuses any const/enum node lacking its type. Twenty-two focused
reader/lineage/scorer tests pass; full regression on this change remains pending.
The initial reader assertion expected the old typeless shape and failed once;
it was updated to the consumer's explicit type, without changing expected bindings.
The official [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs)
documents nested anyOf branches under its supported schema subset; the HTTP400
above is the direct evidence for this missing-type rejection.
Human readability grades remain pending; the human confirmed they are coming.
Prior freezes invalid. No estate scope, secret, fixture or allowance changed.
