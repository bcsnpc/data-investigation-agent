# Round Ten E: pinned ground truth and resolver investigation

Recorded 2026-10-08. PR #423 remains draft. This checkpoint uses retained
definitions and sealed failures only: **zero model calls and zero estate reads**.
The new-versus-old 68-record comparison has not started; no live quality or
adoption claim follows from the offline tests. Engine changes invalidate prior freezes.

## Section 1: independent visual enumeration

The auditor reads the visual definitions and their measure projections, rather
than trusting a golden's target list. Its regression test deliberately replaces
every annotated candidate list with an empty list and obtains the same counts.
Original and rebuilt definitions give identical counts and display titles:

| Family | Visuals projecting the subject | Primary matches | Resolution evidence |
| --- | --- | --- | --- |
| A | Movement Units card; Activity by warehouse matrix | 1 | Explicit current global value excludes the grouped matrix. |
| B | Receipt Share card; Activity by warehouse matrix | 1 | Explicit current global value. |
| C | Net Movement Units card; Activity by warehouse matrix | 1 | Explicit current global value. |
| D | Movement Units card; Activity by warehouse matrix | 2 | North can restrict either; the global total is the comparator. |
| E | Movement Units card; Activity by warehouse matrix | 2 | Freshness question does not name a visual. |
| F | Movement Value card; Activity by warehouse matrix | 2 | A total can appear on a card or a matrix; it does not select one. |
| G | Movement Units card; Activity by warehouse matrix | 2 | Source-entry question does not name a visual. |
| H | Received Units card; Activity by warehouse matrix | 2 | The first measure is the subject; the second is the comparator. |
| I | Movement Units card; Activity by warehouse matrix | 2 | Meaning/implementation question does not name a visual. |

For example, D's retained card has `queryState.Values.projections[].field.Measure`
with `SourceRef.Entity = Activity` and `Property = Handled Quantity`. The matrix
projects that same measure and `Locations.warehouse_name`, displayed as Warehouse.
The card definition content SHA-256 is
`f4b6534eac7ac14ef490e6b2d27df4b50a13b4b34c684fc5470ffb1ab4632ae9`;
the matrix's is
`d035e4340a20b0c4499f7f6027d077d11e07a04d8d483cb937018ec0d3da5b1c`.
Full parts, locations and hashes are retained in
`.local/round-ten-20261007/part-b/part-e/{original,rebuilt}-ground-truth.json`.

### Authorized amendments

A-C's expectations were correct. D-I's ambiguity expectations were also correct
for their original wording. Section 1 explicitly authorizes naming a visual in
those tickets: D now names Activity by warehouse matrix; E/G/I Movement Units
card; F Movement Value card; H Received Units card. Both estate copies are
amended, with independently authored structured expectations for the stated
referent and selection. No query or model response supplied those expectations.
All fifty variant records are structurally unchanged.

The original nine, including the six ambiguity cases, remain in
`acceptance/model_steps/intake-round-ten-e-original-nine.json` as permanent tests.
Private before-files retain original bytes: original SHA-256
`9820fb1bb730add8886e75672e7c154ec8274638ad2bf7cf62ab7e0c54cbf6b0`;
rebuilt SHA-256 `e655435b3a982dcde88bf6e71672fa4603ca3e0d3706984d0d29b3b047c1adf7`.
Twelve dated before/after text and target records are in `golden-amendments.json`.
Existing acceptance outcomes and historical tapes are untouched.

### What the historical passes established

The six preserved Round Six H intake proposals have no `target_visual`; their
intake filter lists are empty. Historical E's session envelope retains a report
binding, `comparison_mode: NONE`, empty filters and no target visual. Its exact
saved run SHA-256 is
`4cc6d2e0079dcd8cd00773e109a517a07cc2f255776c93411f96dfba48f8572d`,
also pinned in the inferred bundle inventory. Those passes used the default
measure scope without resolving the user's visual. They cannot establish that
an unnamed card was the user's referent, nor override today's two candidates.
This is a qualification of the historical evidence, not a retrospective regrade.

I's unchanged subject nomination is SOURCE_CORRECTNESS. Resolving its explicitly
named visual does not authorize an answer about intended business correctness.
The earlier mid-note flagged that potential conflation; it did not establish a
new classification. No kind/outcome expectation was changed to resolve it.

## What the code investigation found and changed

* The old split discarded a measure in setup when the question said "its".
  Non-comparator measure mentions now remain possible referents. This grants no
  visual-selection authority.
* The extracted question span was incorrectly treated as the only place a
  primary target could appear. Primary visual references may precede that span;
  references classified as background or comparators still cannot select it.
* An extracted partial report name could discard a suffix that was present in
  the ticket. A complete declared spelling is recovered only at that exact
  quoted location, never borrowed from another sentence.
* Matching now records its score, runner-up and basis. The policy is in
  `acceptance/model_steps/intake-resolution-policy.json`: threshold 0.72,
  required lead greater than 0.12, declared alias 1.2, normalized exact 1.0,
  token containment 0.9. Other overlap uses token Dice similarity. Case,
  punctuation, underscores, camel case and simple plural forms are normalized.
  Close alternatives refuse; score similarity never establishes lineage.
* Page names are retained separately from visual titles. A page narrows the
  directory; it does not have to uniquely identify a visual by itself.
* A typo repair is permitted only for a retained closed value list of at most
  32 entries, with a unique edit-distance-one candidate. There is no guessed
  estate-wide value list or value read in this resolver.
* A selected value with no stated/resolvable column is now carried through the
  existing report-scoped request contract. The column hint remains nonbinding;
  the procedure must resolve it from evidence. No filter is guessed or dropped.
* Repeated words inside a selection now bind inside the quoted relationship,
  instead of to the earliest occurrence elsewhere in the ticket.

### DECIDED WITHOUT REVIEW

The split's keyword-based shape/mode reconstruction was rejected: it discarded
the already established closed-pair contract and misread questions whose
allegation appeared in setup. Extraction v2 uses the consumer's single triage
field, with the same three valid pairs as the historical producer. A regression
rejects `MISMATCH_COMPLAINT:NONE` in the wire schema. The alternative was another
longer keyword list; that would repeat the over-refusal failure.

The independent top-level reported state was removed. Each figure already
carries its state and verbatim evidence, and code derives the result from those
figures. The alternative was more retries for two representations disagreeing.

The manifest and governor's input-character **validation ceiling** now share
one constant (100 million); other ceilings retain 10 million. This does not
grant an allowance. The authorized old/new benchmark may need more than the
previous hard 10-million configuration maximum because original requests are
large and counters are retained. Its actual bounded allowance and before/after
record must be established before any provider call. No allowance was raised
in this checkpoint. Rejecting the authorized benchmark at an arbitrary parser
maximum was the rejected alternative.

## Verification and remaining work

Focused checks cover partial names, ambiguity, aliases, closed-list typos,
setup referents, repeated selection words, unresolved column requests, page
narrowing, report-binding revalidation, wrong-cell and comparison exclusion.
The latest integrated focused batch passed 107 tests; the intake discovery
batch passed 182. These are offline correctness checks, not current model
accuracy. Full committed regression and the new/old fresh evaluation remain.

The previous intake is pinned at `8d7f118`, the engine behind the composite 32/50
record. Its benchmark revision `45958a0` changes only the same input-budget
validation bound/schema, adds the shared constant and its test; all intake,
adapter, provider and resolver sources remain byte-identical to `8d7f118`.
DECIDED WITHOUT REVIEW: use identical authorized budget validation for both
designs rather than defer the baseline until another UTC day. The rejected
alternative would add a needless day/timing difference to a fair comparison.
The baseline's prompt, schema, decoding and consumer rules are not upgraded.
The composite 32/50 was not a fresh full-column
intake evaluation. Section 4 will run both designs afresh against identical
amended goldens, retain failures, and record transmitted request sizes.
Hosted evaluation of prior head `f29dbb1`, run 37834006827, is still in progress
at this checkpoint; its result remains unclaimed. No identity, permission,
credential, secret, fixture or estate approval changed.

The complete committed `448ac15` regression passed 2,443 tests in 420.400s.
Subsequent review found that the external scoring-policy file must also be
included in the engine fingerprint; its new test changes the threshold file
alone and requires a different fingerprint. An uncommitted-tree process-replay
check correctly refused `TAPE_UNCOMMITTED_ENGINE`; it must pass on the committed
follow-up before any model batch. No refusal is bypassed.

Dated follow-up: committed `5fa67fa` passed all 33 fingerprint and process-tape
tests in 18.900s. PowerShell's redirected native stderr produced an error-shaped
wrapper; the retained test log ends in `OK`. It was not a replay refusal.

DECIDED WITHOUT REVIEW: report primary-span and comparison-span semantic
accuracy as unscored. The sealed goldens have no expected span annotations,
and this part prohibits adding them. Inventing annotations, or calling verbatim
validity semantic accuracy, was rejected. Full structured match remains the
pass condition. Target-derived report/page binding is labelled as such; it does
not claim separate page-span interpretation. The field scorer preserves these
distinctions and cannot upgrade a provider failure to a correct semantic hold.

At 2026-10-08T20:49:02Z, section 4's authorized input allowance changed from
9,000,000 to 23,000,000 in the benchmark-only manifest. Before/after charged
input is unchanged at 8,959,498. Maximum additional input is 13,600,000: 136
attempts per design, bounded by 20,000 characters for the candidate and 80,000
for the historical baseline. The benchmark expires at 2026-10-09T06:00:00Z;
the standing manifest remains unchanged. Calls, output reservations, ordinary
estate allowance, pot, restoration reserve and diagnostic cap are unchanged.
Both passes retain the same model deployment and 65-second pacing. UTC counters
may roll naturally; no counter is reset or refunded.

DECIDED WITHOUT REVIEW: charge the historical benchmark's full transmitted
request instead of its old payload-only estimate. This accounting-only harness
override changes no prompt, schema, resolver, decoding or consumer decision.
Prepared and sealed request sizes must agree after every case, or the benchmark
stops with its evidence preserved. Allowing the historical design to undercount
the larger wire body was rejected. Both designs make fresh calls; none of the
composite 32/50's answers is reused.

The historical body's sizing estimate was checked against the actual transport
builder with a fake client, making zero network requests. Its corrected first
68 requests total 3,725,618 characters (25,580 to 59,495 each); the earlier
preview omitted the tool description and understated each request by 74.

Dated in-progress reference audit: the newly authored resolved nine contain
additional issues that must not be disguised as model failures. H explicitly
compares two distinct measures but the section-1 amendment copied A's VERTICAL
triage. D's authored record expects an immediate typed restriction, whereas the
existing contract also represents a still-unresolved column as a report-scoped
selection request. Further reading confirmed I is deliberately treated by the
existing tested rule as a mixed technical request about implemented effects on
the metric, while authoritative meaning is declined; its nomination is not
changed. The fifty remain
unchanged. No further expectation is changed during this pass; both designs are
graded against the same references. Any eventual adoption decision must name
these reference limits and must not weaken the intent refusal to earn a score.

The first candidate tapes expose primary/global scope labelled COMPARISON and
misspelled measures unresolved after the single recorded retry. These are
preserved failures, not evidence that stronger matching has succeeded. The
candidate stays fixed through section 4; no estate reads follow an unearned gate.

DECIDED WITHOUT REVIEW, 2026-10-08T21:06:45Z: stop the partial candidate pass
after tracing a deterministic defect, rather than spend the rest of the pass on
known-broken scope wiring. The engine-change fence stopped further dispatch;
13 recorded outcomes and 16 provider requests remain intact, including the final
zero-provider RESOLUTION_UNCERTAIN refusal. Seventeen reservations remain charged:
input 8,959,498 -> 9,105,448, output reservations 383,000 -> 408,500;
actual transmitted input was 137,474. No refund, replacement investigation or
estate read occurred. The historical pass was not launched by the stopped
sequencer. This partial pass is exploratory evidence, not the full comparison.

The visual-only exclusion rule was incorrectly reused for primary figures,
selections, groupings, dates and identifiers. Primary facts stated in setup now
survive a broad context span; context and comparator evidence still cannot
choose a visual, and comparator quantities cannot become the reported figure.
Four regression cases cover setup figure/selection preservation, background
visual refusal, comparator figure exclusion and unsatisfied setup date scope.
Selected-scope explanation is also technical context; its wrong nomination
gets the existing single recorded correction. Conversely the verb "check"
alone cannot turn a sole business-rule decision into technical work. Subject
instructions are shared by extraction and the consumer, avoiding drift without
passing the consumer's SELECTION vocabulary into the extractor's different role
enum. Seventy-three focused tests pass, including wrong-cell and comparison guards.

The corrected full pass and fresh historical pass still have the same unchanged
references. All 16 exploratory calls count inside a hard 272-provider-request
experiment allowance; no new call or input allowance is granted. The corrected
candidate uses a distinct request namespace so saved failures cannot be reused
as fresh results. Failed module-name invocations in verification are retained;
the correctly named focused batch passed.

Additional resolver review found two selection defects before the corrected
candidate pass. A runner-up below the acceptance threshold was ignored even
when it defeated the required margin; it now causes ambiguity. Word-reordered
aliases were incorrectly given exact-alias priority; they now receive ordinary
token-overlap scoring. The policy parser checks every setting's type and
priority ordering, including finite numeric weights and the configured one-edit
maximum. Three regression tests cover these cases; the focused total is now
76 passing tests. No configured threshold or golden changed.


Further section 3 exploration, 2026-10-08: measure candidates were ranked independently per model, then their winners counted. This discarded the global score margin. The resolver now ranks all measures inside the already declared report scope once, using a model/measure composite identity; a declared alias beats a competing ordinary name only by the configured margin. A regression validates the resulting consumer record. Containment now requires the quoted tokens to be contained by the candidate; a generic candidate that omits an informative quoted word gets its ordinary overlap score. No threshold, golden or expectation changed.

Closed metadata value repair is restricted to text and boolean domains. A typed boolean survives to the validated filter; numeric and date literals are not corrected into a nearby metadata value. Tests cover a one-edit text repair with provenance, typed boolean, unchanged numeric literal, and setup grouping/record-identifier preservation. Every fix remains offline.

The earlier integrated regression overlapped source edits and failed the engine/tape integrity fences. It is retained as a failed verification attempt, not counted as a passing suite. The final committed source is tested again without concurrent engine edits. The historical benchmark runs in its separate immutable worktree; its provider timeout and target refusals remain recorded. No estate reads, identity, permission or secret changes.
