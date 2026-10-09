# Round Eleven: smart intake and ticket lifecycle

Started 2026-10-09 UTC / 2026-10-08 America/Chicago. This is work in
progress on draft #423, not a Phase A result or a release claim.

Round Ten F's best held-out result remains 9/28. Interactive clarification
replaces the attempt to settle every consequential field in a single model
response. The existing 40/28 split and golden records remain unchanged.
The split was evaluated in earlier rounds; it is not newly unseen evidence.

## Current implementation

- Competing reported figures are checked before catalog resolution or role-based
  exclusion. A model's `COMPARISON` or `CONTEXT` label cannot erase a conflicting
  reported value. Both actual responses from the unsafe admission are retained
  in a small regression fixture, linked to the original tape's SHA-256
  `fd4ffd25c040d12c056d15dd3aefc9b715cbd251a156bb91eba5340380d5dde8`.
  The original tape is untouched.
- Extraction can retain schema-valid, verbatim spans without requiring scope
  resolution to succeed. The legacy resolver remains available; both entry points
  send identical provider requests. A missing target does not discard a paid
  extraction or itself trigger a second model call.
- A recorded target/figure choice now has a consumer resolution path. Choice
  meanings are retained before asking; every offered choice has exactly one
  value. The proof requires the actual retained user answer and original request
  hash. Resolution preserves the original extraction and all competing figures;
  a model response cannot introduce confirmation authority. Missing keyed-cell
  restrictions still refuse. This is an internal bridge, not an exposed API.
  Report/page and comparison bridges remain unfinished and explicitly refuse;
  their confirmations cannot silently disappear.
- The adapter parses shared report links and a bounded, faithful `eq`/`in`
  conjunction subset. Apostrophes, native escaped identifiers and literal types
  are retained. Unsupported syntax, incomplete conjunctions and unestablished
  bookmark/filter precedence refuse the whole declaration. Bookmarks remain
  references until resolved from collected evidence. Parsing is not binding or
  execution and does not claim the user's current selection. Native syntax is
  documented in [Microsoft Learn's URL filter contract](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-url-filters).
- The consumer owns the three clarification fields, offered-choice identities,
  normalized highlight bounds, lifecycle states and user-only closure rule.
  Answers bind the exact retained question hash; answering is not dispatch.
- Durable ticket state uses the installation's existing evidence store, sealed
  bodies, idempotency keys and optimistic revisions. Restart preserves questions
  and confirmations; an old reply cannot answer a newer batch.
- Reuse addresses include context, scope and cell. A changed address misses the
  cache, and an existing receipt cannot be overwritten through the retain path.
  Reuse now requires its purpose: a request for current values never uses a
  historical receipt. Historical explanations carry a retained-evidence
  qualification. Named-owner closure requires the owner from the handoff.
- Optional closed `intake` and `ownership` manifest sections cover ordered route
  choices, confirmation fields, maximum rounds, screenshot retention using the
  estate recording policy, vocabulary aliases and ownership selectors. Existing
  manifests remain valid. A second configuration exercises non-default choices.
- Draft PR pushes do not start the provider CI evaluation. Scheduled and manual
  evaluation entry points remain available. This prevents the unplanned duplicate
  provider calls observed in Round Ten F.

The target/figure bridge is tested through the existing intake validator. The
controller, report/page and comparison bridges, governed dispatch, workspace API
and UI remain unfinished.
There has been no 68-ticket evaluation, screenshot export or live investigation
in this round. No success rate is claimed.

## DECIDED WITHOUT REVIEW

1. Distinct reported figures require clarification conservatively even when they
   might concern separate reports. Rejected alternative: trust extraction roles
   to establish separate referents. The actual unsafe tape disproves that trust.
   The clarification integration must retain the user's resulting authority;
   it must not discard a candidate and call the result a model resolution.
2. Disable provider evaluation on draft PR pushes. Rejected alternative: cancel
   each duplicate job after it starts, which already lost evidence of additional
   provider calls. Ready PR, manual and scheduled gates remain genuine evaluations.
3. Use the existing installation evidence store for durable tickets. Rejected
   alternative: create a parallel raw SQLite database, bypassing privacy-projected
   capture. A projected ticket round-trip test checks no raw value is written,
   and dependent hashes remain valid after cold loading.
4. Do not assume every retained visual is executable. The current metadata has
   explicit unsupported forms and the compiler imposes faithful-scope conditions.
   Candidate evaluation must report unavailable forms and retain their errors;
   a matching value is only a candidate, never target-selection authority.
5. A follow-up about today's values is a new observation, even if its scope and
   cell equal an old receipt's address. Rejected alternative: regard an equal
   address as evidence of currency. Historical evidence can explain an earlier
   result; it cannot establish what a surface serves now.
6. Refuse a URL declaration when its unsupported part or bookmark/filter
   precedence cannot be represented faithfully. Rejected alternative: keep the
   supported prefix or select a precedence without evidence.

## Next integration and evaluation

The resolver must preserve extraction independently from resolution failures,
offer retained candidates, accept confirmed fields through the governed intake
contract, and revalidate scope before dispatch. Uniquely resolved evidence may
settle a field; configuration-required confirmation takes precedence. A missing
figure remains an explicit state, not an invented number.

Findings and handoffs must come from validated saved investigation evidence,
not from caller-supplied outcome labels. Existing freshness and snapshot limits
remain. Evidence reuse must be applied by the runtime, not merely exist in a
ticket cache. API and UI integration follows these consumer checks.

Before provider calls, record the Phase A allowance and the exact bounded model
pass plan. Develop on the development partition only. The simulated user may
use sealed records to answer a question only when the original ticket contained
that information; it may not volunteer a missing target, figure or comparison.
Count individual questions as well as rounds. Report harmful admissions,
one-round settlement and mean questions per class, including unresolved cases.

## Validation checkpoint

The targeted run passed 142 tests, including wrong-cell, comparison-span,
figure precision, cell-address and sealed split checks. A broad 2,489-test run
failed with 13 errors and one failure while the source was dirty and being
edited: tape creation refused `TAPE_UNCOMMITTED_ENGINE`, and source changes
invalidated engine-pinned operations. This run is retained in
`.local/round-eleven-regression.log`; it is not a clean regression result.
Dated clean result: after committing and freezing `4175ced`, all 2,493 tests
passed in 450.659 seconds. The failed run above remains unchanged. Subsequent
confirmation/link/closure/reuse changes passed 142 targeted tests and the clean
`e200e8b` full regression passed 2,512 tests in 451.597 seconds. Do not weaken the committed-tape or engine-change
refusal to make the suite pass.

Phase B exports use existing identities and the unchanged estate pot; denied
exports are retained failures, never a reason to elevate. Phase C is a design
for review only. Neither is complete at this checkpoint.

No identity, permission, secret, estate fixture, policy counter or acceptance
expectation has changed. No model or estate request has been made. Engine bytes
changed, so earlier freezes are invalid. No investigation ledger row is added
for these offline component changes.

## Dated controller integration checkpoint — 2026-10-09 UTC

Report/page and comparison confirmations now pass through the consumer contract.
Report bindings name `USER_CONFIRMED` provenance without inventing an original
quotation. Application, stale and looks-wrong choices reach the procedure;
other-report and business-meaning choices refuse before adapter work. The
original subject is preserved independently from the comparison choice.

The text controller persists one choice batch and adopts the selected scope
from retained extraction without another provider reservation. Replies contain
only question and choice IDs. Catalog changes hold; old source records stay
unchanged. Every occurrence of a repeated numeral remains in the confirmed
inventory, and a user cannot strip approximate wording to manufacture exactness.
Thirty-three targeted controller/confirmation tests pass. Full regression on
this checkpoint remains pending.

Tape v5 adds terminal `ticket_submit` and `ticket_reply` operations and pins
their configuration. V1–V4 remain supported under their original contracts;
no old tape is rewritten. The replay driver dispatches the actual controller.
These new operations still need a committed-source record/replay check.

The controller is not yet exposed in the workspace API/UI. Link application,
structured inputs, keyed-cell choices, routing packages, runtime evidence reuse,
the 68-case evaluation and phases B/C are unfinished. Projected interactive
capture refuses before any raw fallback; existing atomic projected runs are
unchanged. No provider or estate requests, budget changes or scope changes here.

DECIDED WITHOUT REVIEW: retain quote-occurrence inventory only in the new
user-confirmed resolution path. Rejected alternative: choose the first repeated
quote, which cannot establish the user's referent and changes legacy tape bytes.
The metadata-only choice planner labels grouped candidates as total-cell-only;
it does not silently replace an unrepresentable keyed address with a total.

## Lifecycle and capture checkpoint ? 2026-10-09 UTC

The authenticated workspace exposes durable text submission, closed choice replies,
history, scope review, run attachment, composition, findings, user closure and
recorded owner handoffs. Technical findings route on sharing when one configured
owner resolves; consistency disputes route to a business owner. Nothing is sent.
Retained explanations are qualified as historical, without a new read.

V5 distinguishes read completion from narrative completion. The actual original
read return closes the old capture before ticket composition starts its own tape;
missing original capture refuses instead of reconstructing a return. A permanent
synthetic integration test records five tapes (submission, reply, preview/create/run,
attachment, finish) and replays each with zero network requests. Legacy v1?v4
contracts are unchanged. Missing-capture refusals replay too.

The successful consumer-validated retry is authoritative while the rejected
extraction remains retained. The production resolver now supplies the missing
non-verbatim retry evidence. Confirming a visual with exactly one declared measure
can settle that measure without fabricating an original metric quotation;
multimeasure ambiguity still refuses. Seventy-four focused checks passed before
the last handoff/measure additions; those additions passed 21 and 64 focused checks.
Full regression is pending. The prior c48841e full run had one v3 version-pinning
failure among 2,536 checks; explicit v4/v5 matching fixes it and its focused test
passes. Both original failure and log remain preserved.

Phase A is not complete: keyed choices, link/structured submission integration,
changed-question frames, current-evidence reuse and the 68-case quality evaluation
remain unfinished. Interactive privacy-projected capture refuses before any raw
fallback. Screenshots and OTHER_REPORT design remain subsequent work. No new
provider or estate requests, no counter/budget/scope/golden changes. No live-run
ledger row. Existing held-out records were already scored in Round Ten; a later
Round Eleven held pass is not a never-seen corpus. #423 remains draft.

DECIDED WITHOUT REVIEW: represent original read-stage completion separately in
v5, rejecting the alternative of pretending read completion already includes two
narratives or rewriting the original return after synthesis.

## Clarification audit and correction ? 2026-10-09 UTC

Committed lifecycle source5a67e9b passed all2,558 regression tests in796.038s,
Python exit0; log retained privately. Source was held fixed for the whole run.

A development-only audit re-used Round Ten's sealed GPT-5.5 response bytes;
it is not a fresh provider evaluation or the68-ticket gate. The40 cases offered
88 individual questions (mean2.2): family57/26, question9/3, refusal18/7,
visual4/4. Eight adopted a scope under that conservative client. Missing original
referents were not volunteered; the client withheld a report/page it could not
identify from its original-golden representation. That abstention method itself
requires improvement before a quality score. Every synthetic exchange and state
transition is taped. Original tapes and split unchanged. No new provider calls,
no estate requests, no production reservations; audit governors are isolated.

Corrections from this audit: the NUMBER offer now includes the exact discovered
report/page container and readable names. Choosing it settles the container by
metadata rather than asking again. Foreign containers fail validation. Legacy
offers lacking the optional fields retain their previous meaning. Candidate
lists narrow only through literal primary report names and uniquely resolved
measure metadata; competing values and target choices remain explicit. Full
report names omitted by extraction may be recovered literally inside the primary
ask, excluding comparator references. Multiple names stay ambiguous. Business
meaning refusals no longer reopen as visual questions; unresolved business-owner
binding is named rather than fabricated.

The live production resolver's non-verbatim retry is now tested through Intake,
not merely an exception double: exact second response proceeds, two invalid
responses stop after two charged synthetic admissions. The rejected response
remains retained alongside the validated replacement. Latest related focused
checks passed138,74,22 and16 tests in their respective runs. These are overlapping
checks, not summed as unique tests. Latest-source broad regression and v5 replay
remain pending after these additions.

Workspace state labels now reflect actual lifecycle state, owner states permit
retained replies, historical-use qualification is displayed, and sign-out clears
ticket content. JavaScript syntax check passes; visual QA remains pending.
Phase A still incomplete/ungraded; no screenshot or live family run. Pot1013/1500,
restoration95, rolling260/3000 at05:11Z; daily300 calls/4,674,051input/450,000output
reservations unchanged. No cap/identity/secret/fixture/golden change. #423 draft.

DECIDED WITHOUT REVIEW: derive container identity from the selected visual's
retained declaration, rejecting a redundant independent report/page question.
Never use a reported-value match as identity authority. Retained-response audit
results are development diagnostics, rejecting the alternative of presenting
historical samples as fresh model-quality scores.


## Explicit comparison and keyed-cell checkpoint, 2026-10-09 UTC

The controller settles a comparison from a validated verbatim primary ask only
when its subject and wording explicitly agree on freshness or the application
source. Secondary comparisons and competing routes remain open. Estate-required
confirmation overrides this settlement. The original provider wire is unchanged;
an internal request-proof variant is recomputed at adoption and rejects model
authority, changed spans, hashes, kinds and routes.

Grouped visual offers now include a keyed cell only when the same typed selection
producer used by intake establishes every grouping key as a singleton. The user
selects the offered cell; mentions, missing keys and empty intersections do not
become addresses. This refactors the scope parser rather than adding a parallel
key parser. Total and keyed choices remain distinct.

104 focused tests passed, including wrong-cell, competing-figure, confirmation
and extraction checks. This is not a fresh 68-record grade. The second
development-only retained-response audit conserved its originals separately in
.local/round-eleven/retained-dev-audit-v2: 40 cases, 9 adopted scopes, 52 offered
questions (1.30 per ticket), versus the earlier 8 and 88. Unanswerable choices
remain unanswerable; no absent referent was volunteered. The audit predates the
keyed-offer change and uses historical provider responses, so it establishes
redundant-question reduction, not model quality or the Phase A gate.

Zero new model calls and zero estate reads. No budget, identity, secret, fixture
or golden change. #423 remains draft; Phase A is incomplete and ungraded, and
prior freezes remain invalid.

DECIDED WITHOUT REVIEW: use explicit retained question evidence to settle narrow
comparison routes, rejecting inference from vertical/horizontal triage. Reuse the
intake scope producer for keyed offers, rejecting a second parser whose keys
could drift from the consumer.


## Policy defaults and restart evidence, 2026-10-09 UTC

The configured default comparison is now applied only when no named comparator
is present. It is labelled ESTATE_COMPARISON_POLICY, with request and configuration
hashes, not USER_CONFIRMED. Explicit request evidence takes precedence and
must-confirm policy forces a question. Business intent and temporal comparisons
remain excluded; OTHER_REPORT still requires the separate design.95 focused
checks passed for this policy checkpoint.

Attached interactive runs now seal the actual completed read return immediately
and persist only a hash-pinned pointer to the original capture. Cold resume
checks its hash, recording-root location, tape validity and session identity; it
does not reconstruct a return from newer state. Legacy investigation recording
retains its original lifecycle.31 focused tests passed, including changed bytes
and wrong-session refusals. The first test run failed cleanup because the
synthetic SQLite double left connections open on Windows; the double now closes
connections explicitly. End-to-end cold-resume/replay verification is pending
on this committed source.

Work continues in D:/dia-round-eleven-intake on the same #423 remote branch,
while the full regression at5ae814c runs in the unchanged prior worktree. No new
model/estate requests or budget, identity, secret, fixture or golden changes.
Phase A remains incomplete and ungraded; #423 stays draft, freezes invalid.

DECIDED WITHOUT REVIEW: distinguish a configured estate default from a user
comparison choice, rejecting fabricated confirmation. Preserve the actual
read-stage FINAL at completion for restart, rejecting retrospective reconstruction
from an investigation state that may already contain synthesis.


## Model-level asks and business-owner routing, 2026-10-09 UTC

Three independent v5 replay tests passed onfefa8e5, including a cold-resume
workflow that removes the in-memory capture cache before composition. Every
original capture remained unchanged; all replay requests were offline. Historical
v4 replay also passed.

The development audit exposed no-figure freshness questions being forced to
select an unnamed report visual. A report name can anchor the model without
nominating a display: FRESHNESS/SOURCE_CORRECTNESS with no figure, visual request
or selected/grouped scope now retain the report binding and start at the model.
Figure-bearing asks still require a target; selected scope and explicit visuals
still use the existing target refusals. The first broadening affected unrelated
discrepancy tests; it was narrowed to these two subjects.117 related tests passed
after that correction, including wrong-cell and comparison-span guards.

Pure business intent retains the original UNIMPLEMENTED_ROUTE intake refusal,
then records BUSINESS_VALIDATION only when retained metadata identifies one
measure and configuration names one business owner. Its package contains the
ask, available definition and explicit absence of value/pipeline comparisons.
It does not invent a number, consistency finding or receipts. Missing/ambiguous
ownership remains HELD; delivery is RECORDED_NOT_SENT. Replies to an intent-only
handoff are retained without assuming technical findings exist.99 focused tests
and a later26-test reply check passed (overlapping, not summed).

Zero new provider calls or estate reads. No allowance, identity, secret, fixture
or golden changes. Phase A remains incomplete/ungraded; #423 draft, prior
freezes invalid. URL/structured input, aliases, changed-question frames and the
fresh68-record evaluation remain pending; no screenshot/live-family claim.

DECIDED WITHOUT REVIEW: preserve model-level freshness/source questions without
asking users to invent a visual, rejecting a blanket relaxation for other kinds.
Route intent-only tickets using definition/owner evidence while explicitly
refusing technical findings, rejecting invented end-to-end consistency.


## Fresh development text checkpoint, 2026-10-09 UTC

Frozen source fda65b8 completed all40 dev tickets:50 real provider calls,48
individual questions (mean1.20),11 adopted intake scopes, zero estate requests.
Every case has a capture and an append-only ledger row, including refusals.
The28 held records were not tuned or evaluated in this round; they were already
evaluated in Round Ten, so their historical exposure is disclosed.

| Class | Tickets | Adopted | Questions | Mean questions | Model calls |
| --- | ---: | ---: | ---: | ---: | ---: |
| family | 26 | 10 | 33 | 1.27 | 33 |
| question | 3 | 1 | 4 | 1.33 | 5 |
| refusal | 7 | 0 | 8 | 1.14 | 8 |
| visual | 4 | 0 | 3 | 0.75 | 4 |

This is exploratory development evidence, not a full quality score. Seven adopted
records match every observed golden field except the runner's omitted nominated
kind. The runner also omits final refused-intake records and uses a conservative,
incomplete report/page answer simulator. Consequently full structured accuracy,
correct-refusal coverage and harmful-error rate are ungraded. The two no-figure
freshness admissions differ from unchanged historical target-ambiguity goldens;
this is a declared model-start change, not an amended expectation. Both D
admissions carry an extra grouping dimension compared with their sealed records;
target, figure and selected filter match, but this is not a full structured pass.
Do not use eleven admissions as eleven correct answers.

Private evidence: .local/round-eleven/fresh-dev-v2/{plan.json,results.json,
audit-score.json} and each case's audit.tape.json. Prior attempts remain unchanged.
Reservations increased300->350 calls,4,674,051->5,299,181 input characters,
450,000->525,000 output tokens. Thus50 calls reserved625,130 input characters;
today's8,000,000 input limit and600 call limit are unchanged. Estate pot remains
1,013/1,500 with95 reserved; rolling ordinary usage was0/3,000 at the final
read through normal window expiry, with no reset. Investigation cap12 unchanged.

The exploration found successful extractor responses discarded when a later
consumer route gate refused. Extraction now persists independently of admission;
its latest successful resolver response is distinguished from the first failed
attempt and revalidated before any use. Known UNIMPLEMENTED_ROUTE refusals do
not reopen irrelevant visual/comparison questions. Invalid retained wire-schema
evidence produces RETAINED_EXTRACTION_SCHEMA_INVALID rather than escaping as a
controller crash.130 focused intake/clarification tests passed, including original
wrong-cell, competing-figure and comparison referent guards. The preceding clean
5ae814c full regression passed2,573 tests; this newer source has not yet earned
that full result.

Visual QA is pending: connected-surface inventory was empty and opening the
in-app browser returned `Browser is not available: iab`. No UI or export result
is inferred from that. Phase A is incomplete, #423 stays draft, prior freezes
invalid. URLs/structured fields, aliases, changed-question frames, the corrected
68-case evaluator and the acceptance gate remain pending. No screenshot,
OTHER_REPORT implementation, live family, rebuild or billing run occurred.

DECIDED WITHOUT REVIEW: retain successful extraction separately from admission,
rejecting a second model call solely to recover discarded evidence. Preserve
unimplemented-route refusals instead of asking a user to repair an engine gap.
Treat the first fresh40-case pass as exploratory and repair its scorer before
claiming quality; rejected treating adopted records as full matches or changing
goldens to make the count improve.


### Retained-record scoring recovery and grain audit

The exploratory scorer was repaired offline by reading hash-verified original
consumer records and recovering nominated kind from each sealed provider response.
It now reports12/40 matches against unchanged original structured records,
including semantic refusals. This is NOT12 successful ticket completions: some
matching source records still wait for comparison clarification. Zero new model
or estate calls. Private consumer-record-score.json retains every difference.
The initial scorer failures (wrong SQLite hash column and a nested-base64 provider
body) occurred locally and charged no reads; the recovered score replaces no tape.
The interactive one-round/harmful-error gate remains ungraded.

The two D records exposed a duplicate grain nomination: words inside the named
visual were also treated as an independent grouping request. Intake now uses
that quotation for visual identification, retains the discovered grouping on
the cell address, and does not add it as a second diagnostic query breakdown.
An independent grouping quotation still adds the requested dimension. Both
cases have regression tests; no target, filter or lower-scope refusal is weakened.

DECIDED WITHOUT REVIEW: distinguish a visual label from a separately stated
breakdown, rejecting silent query-grain changes caused by extracting the same
visual-title words twice. Original nominations remain in retained extraction.


### Subject-only clarification checkpoint

Definition, component, transformation-mechanism and filter-effect questions
without an external comparator now carry ticket-subject-route-v1 evidence:
DECLARED_SUBJECT, kind, exact primary span and request hash. They do not invent
an application comparison, a looks-wrong complaint or freshness request. Any
retained comparator, explicit comparator wording, business meaning or temporal
comparison leaves the original refusals/questions intact. Must-confirm policy
still overrides. The intake consumer recomputes the proof from original text
and extraction before admission; a model cannot supply its own authority.
135 related checks passed, followed by30 focused checks after tightening the
comparator wording guard. These suites overlap. No new provider or estate calls.

DECIDED WITHOUT REVIEW: a request to explain a local definition/filter has a
subject, not an absent external comparison. Reject asking users to select an
application/staleness route merely to explain the requested definition. This
additive proof preserves legacy user-confirmation and sealed replay contracts.
The fresh40-case evaluation above predates this fix; no improved score is claimed.
Phase A still incomplete/ungraded, #423 draft, freezes invalid.


## Evaluator correction, 2026-10-09 UTC

Offline evaluator code now records the original case hash and every structured
difference. It separates a source record that matches its golden from a ticket
that is actually settled: a waiting clarification is not a settled refusal.
It uses the complete public model visual inventory for report choices, never
supplies a missing target/page/figure, preserves exact figure precision, and
requires exactly one matching choice. A missing comparator stays missing;
freshness wording such as up-to-date may answer the original freshness choice.
Consequential differences remain review flags, never silently graded harmless.
The module does not declare the Phase A gate green or a zero harmful-error rate.
Eight evaluator regressions and six existing scoring regressions passed. The
first synthetic test used an integer instead of the consumer's precision object;
it was corrected to EXACT and no sealed expected record changed. CI now runs
these new controller/evaluator and related intake suites offline.

A reuse-only dev audit of the same40 sealed fresh responses, oncc8b0d7 with the
corrected simulator, offered43 questions (mean1.075) and adopted9 scopes. Twelve
tickets settled within one round under the conservative counter (including
three appropriate terminal semantic refusals):30%, not85%. Per-class one-round
rates: family8/26, question1/3, refusal3/7, visual0/4. Original-record matches12/40.
This is reused-provider-byte debugging, NOT a fresh quality evaluation. Zero
new provider or estate requests; originals retained. Evidence is in
.local/round-eleven/retained-fresh-dev-scored-v5. Prior fresh records remain
unchanged, including D; the stricter simulator did not treat a report-context
question as an application/looks-wrong answer merely to get it through intake.
That reveals a remaining clarification gap: internal report comparisons can
fall between the external comparison choices. It does not justify inventing
a comparison or relaxing the lower filtered-scope refusal.

A full regression runs on unchangedcc8b0d7 inD:/dia-round-eleven-intake while
evaluator work continues inD:/dia-round-eleven-eval; its pending result is not
claimed for newer code. Phase A remains incomplete, #423 draft. No held-out
tuning, screenshot/export, live family, fixture or reader-scope change occurred.

DECIDED WITHOUT REVIEW: make the simulator abstain on unclear comparison
semantics, rejecting the earlier broad keyword inference for family D. Count
settled tickets rather than merely adopted/source-matching records. Preserve
review flags instead of declaring a zero harmful-error rate from incomplete
provenance scoring. Add the evaluator/controller tests to hosted offline CI
instead of relying only on local discovery.


## Missing-information replies and full checkpoint regression

The frozencc8b0d7 full regression completed2,591 tests in775.245s, exit0.
This covers the intake retention, visual-label grain and subject-route changes;
it is not claimed for the later evaluator or unavailable-reply extension.

The closed reply union now accepts either one retained choice or an explicit
`unavailable:true` answer for each asked field. Those variants cannot be mixed
in one answer, and every other answer is still checked against its original
offer. Unavailability never enters confirmation or settles a field. It records
a USER_INFORMATION_UNAVAILABLE hold, retains the offer/evidence, does not adopt
a scope and makes no provider/data call. A later answer can resume that same
offer and same ticket; no additional model interpretation is needed. Idempotent
repeated replies and stale-revision protection remain. The workspace UI offers
'I cannot tell from the information I have' separately from target choices.
63 protocol/controller/confirmation/state tests and JavaScript syntax passed;
the distinct-event tape replay test is pending until this source is committed.
The previous63-test result and new full checkpoint result are separate.

No simulator silently takes this action on behalf of a real user. The frozen
fresh40 and reuse-only40 results are unchanged; no new quality claim, provider
call, estate read, budget/scope/golden change or live run follows. #423 draft,
Phase A incomplete/ungraded, freezes invalid.

DECIDED WITHOUT REVIEW: permit an explicit missing-information answer instead
of forcing selection of a potentially wrong cell/comparison. Treat that answer
as unavailability, never authority. Preserve the retained offer for later human
resume rather than creating a replacement ticket or pretending the scope settled.
# Dated optional-input checkpoint — 2026-10-09 UTC

Optional number and report/page descriptions now enter a labelled derived input
document. The original request survives unchanged, with each user field's exact
interval and content hash recorded separately. No numeral, precision, target or
comparison is generated by the document builder. Plain text keeps its bytes.
The combined consumer bound is shared; oversized input refuses, never truncates.
The workspace exposes optional fields and obtains comparison labels/order from
the estate configuration rather than a second frontend vocabulary.

Validation: 175 tests passed across smart intake (30), input document (4),
confirmation (20), workspace/API (25), route (6), question intake (37),
extraction (39), and protocol (14). JavaScript syntax and git diff whitespace
checks passed. One new assertion initially expected the later provenance error;
the consumer correctly refused earlier during extraction recomputation with
"Request comparison evidence differs". The assertion now checks that earlier
refusal; no validation was relaxed. Browser rendering remains unverified because
no browser surface is available in this session.

A supplied comparison has USER_SUPPLIED_INPUT authority and a request-bound
proof, not a fabricated clicked-choice confirmation. The consumer recomputes
that proof against the retained request. Disabled choices refuse before a model
call; estate must-confirm still asks. If text explicitly asks for freshness while
the optional field supplies the application, neither wins: the engine retains
both declarations and asks the comparison question before scope adoption.
OTHER_REPORT still refuses the unimplemented route; it does not start a
one-report walk. This checkpoint does not provide the pending link integration.

DECIDED WITHOUT REVIEW: retain optional field text in an explicitly derived
document instead of making the model invent quotations in the original textbox.
Reject an overriding-precedence rule for conflicting comparison declarations;
ask for the user's choice. No acceptance/golden, fixture, scope, secret, budget
or counter changed. Zero new provider calls and zero estate reads. Current
Phase A quality remains ungraded and below goal in the exploratory dev sample;
#423 remains draft, and all prior engine freezes are invalidated.

Append-only verification correction: the unavailable-reply checkpoint's pending
committed-source replay was subsequently completed on 1e38b1f: two tests passed
in 13.875s, including independently replayed submission/unavailability/resume
captures and preserved legacy-v4 replay, with zero network requests. The full
2,591-test pass applies only to cc8b0d7, not this newer optional-input source.

Dated follow-up, 2026-10-09 UTC: committed 0cd56b2's optional-input synthetic
submission replayed independently with matched=true and zero network requests.
It retains the original structured request and admits its comparison only via
ticket-comparison-input-v1. This is capture/replay verification, not a fresh
model-quality result. Full regression on this engine source is running.

Verification correction: the initial final documentation patch introduced three
extra blank lines at EOF, so its final diff check reported whitespace warnings.
Those lines are removed in this follow-up; the earlier clean check had preceded
that documentation patch. No code or evidence validation changed.

Dated lifecycle-score correction, 2026-10-09 UTC: a source record that matches
an expected refusal does not prove the ticket settled. The scorer now requires
retained ticket history before crediting a terminal refusal and explicitly
excludes USER_INFORMATION_UNAVAILABLE pauses from one-round settlement. A
regression retains an exactly matching original record while asserting that
the unavailable user reply remains unsettled. Nine evaluator tests and six
original scoring tests passed, zero provider calls or estate reads.

Earlier completed score files remain unchanged. Their 12/40 record agreement
and exploratory settlement counts are historical, not a current Phase A pass;
they did not retain the lifecycle history newly required for refusal credit.
DECIDED WITHOUT REVIEW: require lifecycle evidence for the disposition rather
than treating the word HELD as proof of successful settlement. An inability to
answer must never improve the quality gate. #423 stays draft, freezes invalid.

Dated resume checkpoint, 2026-10-09 America/Chicago: the full optional-input
test process no longer exists and its preserved log has no final test count or
OK/FAILED footer. Record it as INTERRUPTED, not a pass. Existing unrelated
notebook/kernel processes were inspected and left untouched. The earlier
cc8b0d7 2,591-test pass remains the last completed full checkpoint.

An explicit visual-content question now uses DECLARED_SUBJECT, just like an
intrinsic definition/filter question. A narrowly revalidated what/which/how-many
ask with no named comparator or timing request does not need the user to invent
an application/staleness comparison. The target still comes from the original
consumer and its evidence, never this route. Named external/temporal comparisons,
ambiguous targets and estate-required confirmation remain open/refused. Eight
request-route tests and 31 smart-controller tests passed, zero provider calls
or estate reads. Existing golden records and completed samples are unchanged.

DECIDED WITHOUT REVIEW: route a content question by its stated intrinsic
subject instead of asking for an irrelevant external comparison. Reject making
LOOKS_WRONG the automatic substitute. This does not implement comparisons
between two cells/reports, and does not remove filtered-scope refusals. Phase A
remains incomplete and ungraded; #423 draft, freezes invalid. Browser inventory
was checked again and returned apps=[] and browsers=[]; visual UI verification
remains unavailable, with no estate export attempted.

Dated dev-only retained-response audit, 2026-10-09 America/Chicago: source
4565752 re-used the same 40 development response tapes into a separately named
v6 capture. No new model sample or estate request occurred; held-out was not
opened. Runtime proposals adopted 10 scopes; the scorer credits 13/40 one-round
settlements (32.5%, including three retained semantic refusals). Original full
consumer-record agreement stays 12/40. Individual questions are 42, mean1.05.
Lifecycle history is retained for every row. This does not reach the goal and
does not grade harmful-error rate; consequential review flags are not a proof
of safety. Forty separate offline ledger rows carry the new tape hashes.

| Dev class | Tickets | One-round settled | Questions | Mean questions |
| --- | ---: | ---: | ---: | ---: |
| Family | 26 | 8 | 28 | 1.077 |
| Question | 3 | 1 | 3 | 1.000 |
| Refusal | 7 | 3 | 7 | 1.000 |
| Visual | 4 | 1 | 4 | 1.000 |

The visual-class improvement removes one irrelevant comparison question; it
does not settle unknown targets or internal two-cell comparisons. No missing
seal information was volunteered by the simulator. The current quality gate
is still incomplete, #423 draft, freezes invalid, no live run allowed. Original
v5 audit/scores and every earlier failed or interrupted result are untouched.

Dated full checkpoint, 2026-10-09 America/Chicago: unchanged source4565752
completed 2,620 tests in611.109s, OK. The earlier interrupted optional-input
log remains untouched. This pass covers the optional-input, unavailable-reply,
score-history and content-subject changes, not the later restatement work.

Dated changed-question lifecycle checkpoint: RESTATE_QUESTION reopens the same
ticket from a waiting clarification, hold, findings or handoff. The original
request is unchanged. Prior questions, choices, confirmations, scope, findings,
handoff and source/session identifiers are archived under the question version;
the existing evidence addresses remain. Current request authority comes only
from the new user text and its fresh, governed extraction. Old figure/cell and
comparison authority cannot resolve a new ambiguous ask; an old run cannot be
attached as the new investigation. Current-value reuse remains forbidden.

If extraction fails, the ticket holds with its exception type/message and the
source request key, retaining the prior version. Stale revisions refuse before
calling a model. The workspace provides this reply outside the findings block,
so a waiting clarification can also change its question. No delivery is sent,
no ticket is agent-closed, and no estate read is started by this action.
98 focused controller/input/confirmation/intake tests passed; JavaScript syntax
and whitespace checks passed. The committed-source capture/replay is pending.
One synthetic test initially supplied a mismatch record without a mismatch ask;
its ticket was corrected. A second failure exposed retained choice_context,
which is now archived and removed from active authority, with a permanent test.

DECIDED WITHOUT REVIEW: treat an explicit user restatement as a new question
version on the same ticket, with a fresh clarification allowance and the prior
question's count retained in prior_clarifying_rounds. Reject both borrowing old
choices and forcing a new ticket. This does not reset model/read budgets or
change diagnostic caps. An explanation of the old result still returns only
qualified historical evidence. General link-context integration, aliases and
the current 68-ticket quality/lifecycle gate remain incomplete; #423 draft,
freezes invalid. Zero new real provider calls/estate requests, scopes, secrets,
fixtures or golden changes.

Dated restatement replay follow-up, 2026-10-09 America/Chicago: committed
92f1e36 produced separate synthetic ticket_submit and ticket_respond captures.
Both replayed independently with matched=true and network_requests=0. The
second capture re-enters intake from the retained waiting ticket, keeps its
original request and ID, archives the prior question version, and resolves the
new source question. No real model call or estate read occurred. This closes
the preceding pending capture check, not the current quality/lifecycle gate.


Dated evaluator/container correction, 2026-10-09 America/Chicago: the simulated
user previously allowed REPORT_PAGE only with a null page, even where the sealed
visual uniquely established a native page. It now answers only that exact
retained container. Duplicate visual bindings, other pages and unresolved or
held sealed targets remain unanswerable. The simulator was not loosened to
invent targets from expected refusals. Twelve evaluator tests passed.

Source7e3db02 reused the same forty development response tapes into a separate
v7 audit. Results remain ten adopted scopes, thirteen one-round settlements
(32.5%, including three semantic refusals), forty-two questions (mean1.05),
and twelve original full consumer-record matches. Per-class results match the
v6 table above. This correction did not improve these development cases.
Forty new tape hashes have separate appended ledger rows; original captures
and ledger entries remain untouched. No model call or estate request occurred,
held-out remains untouched, harmful-error rate is ungraded, and no intake gate
pass is claimed. The later vocabulary wiring is not included in this audit.

Dated estate vocabulary wiring: operator-declared synonyms for measure and
column names now join the retained intake catalog and its existing name scorer.
Their provenance is DECLARED_BY_CONFIGURATION, with the exact declarations and
hash retained on each member. Canonical destinations require exact declared
names; a synonym never creates a metric, column, filter value, precision or
query. Duplicate canonical destinations remain ambiguous. Native definition
synonyms remain distinct in origin and are retained too. Extraction receives
the names without changing the ticket; its original verbatim quotes still
pass through the scope validator. This does not implement report/page-title
aliases, URL-context binding or any data-value synonym substitution.

Ten new tests cover snapshot integration, original-consumer validation,
unchanged inputs/catalog identities, declaration provenance, ambiguity,
configuration rejection and context bounds. The synthetic two-member context
keeps one measure and one column before/after: name-list characters32->55,
serialized extraction payload349->372. Over-bound name contexts refuse whole;
no directory/catalog entry is dropped. The test is wired into CI.

DECIDED WITHOUT REVIEW: apply estate vocabulary at the catalog boundary rather
than replacing user words. Reject text substitution because it would falsify
span provenance, and reject selecting one duplicate canonical name because the
operator vocabulary is no new target authority. Configuration still needs its
normal whole-config approval; this work changes no estate configuration,
approval, golden, secret, identity, permission or budget. Phase A remains
incomplete, #423 draft and all earlier freezes invalid. No live read follows.

Validation follow-up:39 extraction tests (including sealed wrong-cell and
competing-figure cases),37 intake tests,10 clarification tests,10 vocabulary
tests and21 manifest tests passed after the vocabulary wiring. The earlier
36 controller,20 confirmation and12 evaluator checks passed before it.
Full regression on the combined source is pending; the earlier2,620 pass
was on4565752 and is not a result for these new bytes.


Dated reproduction-route correction: two dev tickets explicitly ask whether
saved context reproduces a figure. Their kind and referent resolved, but the
subject-route recognizer required what/which/how-many and asked an unrelated
external-comparison question. Can/does/whether reproduction asks now settle
DECLARED_SUBJECT only inside the retained primary ask and the existing no-named-
comparator guard. They do not select a cell, assume an application comparator,
request freshness or claim a reproduced result. Estate confirmation policy
still overrides. Thirty-seven controller and nine route tests passed. A test
adopts the named card/16 scope with one mocked intake call and no estate read;
comparison and background-text tests still refuse subject settlement.

The first two new negative tests failed because their synthetic ticket omitted
the Report quote their fixture supplied. The test input was corrected to retain
that quote; provenance validation was not weakened. Original failed audit and
provider tapes are untouched. Full regression remains on frozen9422f43 in the
other worktree, not on this later route correction. Current quality gate is
incomplete, #423 draft, freezes invalid. Zero real provider or estate requests,
no altered goldens, expectation, configuration, access, secret or budget.


Dated retained-response follow-up: sourcebdf8037 completed forty independent
v8 development captures using the same old provider responses. No new model
sample or estate request. Twelve scopes adopted; fifteen one-round settlements
(37.5%, including three semantic refusals), thirty-nine questions (mean0.975),
twelve original full consumer-record matches. Forty new ledger rows retain the
separate tape hashes. No earlier evidence was rewritten.

| Dev class | Tickets | One-round settled | Questions | Mean questions |
| --- | ---: | ---: | ---: | ---: |
| Family | 26 | 8 | 28 | 1.077 |
| Question | 3 | 1 | 3 | 1.000 |
| Refusal | 7 | 3 | 7 | 1.000 |
| Visual | 4 | 3 | 1 | 0.250 |

Compared withv7, visual-1 andvisual-4 adopted their uniquely established scopes
with no question; visual-3 still needs a number/target answer but no invented
comparison. No result value was read and these are not reproduced-value claims.
The remaining classes did not improve. Family meanquestions still exceeds1.0;
settlement still falls short85%; harmful-error grade remains
REQUIRES_PROVENANCE_REVIEW. Current68 quality is incomplete, held-out not opened,
#423 draft and freezes invalid. The alias/reproduction changes therefore do not
authorize screenshot exports, rehearsal or fifty-ticket estate runs.


Dated hosted validation checkpoint: Validation run37951535051 completed success
on head21a78b275f7778a136ff18be0ab621055e545b62. Its generator-tests job executed
237 test-module commands totaling2,356 unit checks, with zero FAILED summaries;
portal, PowerShell syntax and recorded model-step checks also passed. Local log:
.local/round-eleven-ci-21a78b2-generator.log. Current-intake-evaluation remains
skipped because the PR is draft; this is not a current intake quality pass.
Historical earned/known-domain replay jobs were still pending at this read.

The separate all-at-once local discovery run remains active on frozen9422f43
in D:\dia-round-eleven-eval, session5521, with its output retained in
.local/round-eleven-regression-vocabulary.log. Resource warnings are present,
there is no final test summary yet, and no local full-suite pass is claimed.
Later reproduction-route tests and hosted21a78b2 validation are separate from
that frozen run. Do not overwrite its log or mistake it for validation of the
later source. No provider/estate request occurred; #423 remains draft, Phase A
incomplete and prior freezes invalid.


Dated link-reference checkpoint, 2026-10-09 America/Chicago:
plain supplied report/page links now carry a closed DECLARED_REFERENCE binding,
separate from name quotations and clicked confirmations. The adapter resolves
native identifiers only against the retained catalog. The proof pins the input
request, exact source interval and report catalog; the consumer recomputes that
proof before extraction validation. A link cannot choose among competing visuals,
override a named conflicting report, or let a confirmed cell escape its page.
The optional local-workspace link field is wired to that same contract.

Predicate-bearing links and invoked bookmarks remain explicitly HELD before a
provider call: their context cannot yet be applied faithfully. Nothing drops
those restrictions and executes a broader read. This is partial Phase A link
support, not completion; URL discovery from arbitrary pasted prose and faithful
URL/bookmark context application remain pending. No screenshot exports or live
investigation follows this checkpoint.

The shared report-binding union gained a new explicitly discriminated variant;
its supplied-reference proof has its own ticket-report-reference-v1 version.
Existing STATED/USER_CONFIRMED bindings and their recorded bytes are unchanged.
DECIDED WITHOUT REVIEW: retain those historical versions and extend the union
rather than relabel old tapes or encode a supplied link as a fabricated clicked
choice. Rejected alternative: invent a report-name quote from a URL identifier.

Validation: 197 focused checks passed across input reference (14), smart
controller (41), clarification (10), extraction (39), legacy intake (37),
confirmation (20), report contract (22), link parser (8), and optional inputs (6).
Wrong-cell, comparison-span and competing-figure checks remain in those suites.
JavaScript syntax and git diff whitespace checks passed; browser presentation
was not visually tested. Initial test failures are preserved in the working
history: the missing-authority refusal originally occurred after extraction;
the check now runs first. A new catalog-coverage test initially addressed a
nonexistent wire.models key; it now checks the actual compact wire and catalog.

Synthetic context-cost check (same catalog before/after): report entries1/1,
visual entries2/2, declared names4/4, visual titles2/2; compact payload434/587
characters and complete provider body10,481/10,637. The added characters are the
user's labelled link, not per-entry ownership or catalog truncation. A regression
test asserts both the catalog and compact names/titles survive unchanged.

Dated correction to the earlier pending local-suite entry: frozen9422f43 completed
2,639 tests in1,011.310seconds, OK, with ResourceWarnings preserved in
.local/round-eleven-regression-vocabulary.log. That pass covers the vocabulary
checkpoint, not the later reproduction or link changes. The focused checks above
cover those newer paths; no new full-suite result is attributed to them.

Zero new real model calls or estate requests; no budget, identity, scope, fixture,
golden or acceptance expectation change. Last retained dev audit remains15/40
one-round settlements,39questions, family mean1.077; harmful-error grading and
the 68-case quality gate remain incomplete. #423 stays draft; freezes invalid.
