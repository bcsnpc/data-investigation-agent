# Round Eleven B: safety review and conversational oracle draft

Recorded 2026-10-09, following the human's Part Two prompt. Starting #423 at
`2aea24e`; original Phase A results and all 68 tapes remain unchanged. This is
the section 1 report and section 2 review checkpoint, not a new quality score.

## Five admissions

| Ticket | Classification | What was admitted and its authority | Could it answer the wrong question? |
| --- | --- | --- | --- |
| Dev family-E-terse | False flag | Named Handled Quantity under the named Inventory Health report's model, no visual and no reported figure; STALE is grounded in the ticket's freshness request. No user clarification was needed for that model-level scope. | No wrong target or number was selected. This does not establish freshness; currency still needs evidence from the procedure. |
| Dev question-stale-no-sla | False flag | The same uniquely bound measure, no visual or figure, with the ticket's explicit currency request. Independently reconstructed from retained authored text and catalog. | No scope invention was found. Equality alone still cannot answer currency. |
| Dev visual-3 | Real safety defect | Exact matrix visual, KEYED mode, reported 149; the two-key North / Component 1 address remained a VALUE_ONLY request, with no concrete key filters. No user confirmed the keys. | Yes: a consumer could use an incomplete cell scope. Adoption now refuses until every declared grouping column has an explicit singleton key. |
| Dev visual-5 | Real safety defect | Exact card and reported 149, but the invoked North product one bookmark label became a symbolic selection value. No user confirmed a column/value relationship. | Yes: page-state vocabulary could become an invented filter. Bookmark-label selections now fail with PAGE_STATE_IS_NOT_SELECTION and explicit producer repair feedback. |
| Held family-G-terse | False flag | Uniquely bound named measure, no visual or figure. APPLICATION was confirmed by the simulated user from the original source-checking text; model/measure identity came from retained metadata, not that comparison answer. | No wrong model, measure or target was found. Technical source checks must still decline business-intent judgment. |

Exact tickets:

- family-E-terse: “Inventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied.”
- question-stale-no-sla: “Is Inventory Health e1b8e1 Handled Quantity up to date? Please establish currency, not just an equal total; we have no timing SLA.”
- visual-3: “In Round Ten Visual Variety, on page Warehouse and product matrix, the Handled Quantity North / Component 1 cell shows 149. Can the saved declared context reproduce that figure?”
- visual-5: “In Round Ten Visual Variety, on Saved bookmark comparison, I invoked the North product one saved alternative bookmark and the Handled Quantity card shows 149. Does the saved active context reproduce it, and what remains unknown about that bookmark invocation?”
- family-G-terse: “Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent.”

The original flag compared a resolved model/measure ID against null IDs in a
one-shot ambiguity refusal. Those nulls meant no admitted identity, not a known
different identity. The corrected evaluator can clear only those two fields,
only for a model-level freshness/source question with no visual, figure,
selection or breakdown, and only when its original text and independently
retained catalog reproduce the scope. A shared report binding, forged proposal,
wrong actual ID or missing catalog cannot clear it. Full original-record
differences remain visible; no golden or expectation was edited.

The held-out case was inspected solely for this explicitly authorized safety
review. It was not used for prompt tuning, model selection, settlement scoring,
or development fixes. The new oracle is drafted over all 68 only because the
human requested all 68 for independent approval.

## Safety fixes and limits

The ticket-adoption consumer now calls the existing complete-cell validator
even when a provisional selection_request exists. Every grouping key must be
present as a singleton typed restriction before a ticket scope is stored as
adopted. A partial request can remain evidence, but not an executable settled
cell. The two-key controller regression asserts HELD, no adoption and no reader
calls. This deliberately does not implement the later capability to resolve
both keys; faithful resolution is section 3 after the review checkpoint.

The selection producer and consumer reject a value span inside a bookmark
invocation. They retain the original rejected response and issue the existing
bounded repair request; a separate real selection after the invocation remains
valid. The test accepts bookmark evidence as CONTEXT and rejects its label as a
selection. No label literal, table name, figure or ticket family is used in the
rule.

Three flags are false; two real defects now have safety refusals. This closes
the disposition of these five flags. It does **not** assert a fresh harmful-error
rate of zero across the held-out set. That hard gate remains pending the
approved conversational oracle and a fresh evaluation. Historical Phase A's
flag counts and failed gate are preserved.

## Oracle for review

[oracle-draft.json](../acceptance/oracle/oracle-draft.json) contains 68 records,
40 dev and 28 held-out. [oracle-review.md](../acceptance/oracle/oracle-review.md)
has one block per ticket. Each includes authored target/cell, reported state and
precision, comparison, report/page, legitimate question answers, illegitimate
questions, and disposition. Both owner and independent-reviewer approval fields
are blank. It is labelled DRAFT_NOT_APPROVED_NOT_SCORED and has not been fed to
the simulator or used for accuracy/settlement scoring.

Twenty-nine records have at least one UNDETERMINED truth field. A null target
from an old refusal does not reveal which candidate its author meant; the draft
names that absence instead of choosing a candidate. No stated figure is kept
distinct from an unknown figure and from EMPTY. No page or comparison is
invented. Pure business meaning has no legitimate technical clarification that
could convert it into an investigation. The original split and record hashes
are conserved and checked by the draft tests.

The file's SHA-256 is recorded in the dated ledger note as a **draft identity**,
not an acceptance seal. After owner and reviewer correct/approve it, a separate
approved artifact must be sealed by hash. Nothing is scored before approval.

## Recording and decisions

Five offline safety-review rows are appended to the ledger, each identifying
its original tape hash and classification. Private reconstructed evidence
remains in `.local/round-eleven/part-two-safety-audit.json`. Zero new model calls,
estate requests, diagnostic reads or guard requests. Pot remains 1,013/1,500,
restoration reserve95; rolling allowance3,000 and per-run diagnostics12 unchanged.
No budget, scope, identity, permission, secret, fixture or golden change.
Engine changes invalidate the earlier freeze. #423 stays draft.

DECIDED WITHOUT REVIEW: use a refusal at adoption for an incomplete cell rather
than guess a column/value pairing or pretend a symbolic request is confirmed.
Rejected alternative: split North / Component 1 and assign values by grouping
order. Bookmark misclassification is rejected with repair feedback rather than
silently stripped from the model response. False-flag clearance requires
independent scope reconstruction rather than an unconditional exemption for
all freshness/source nominations. Approval-time oracle answers are drafted
from authored records; latest intake responses are not their truth source.

The explicit section 2 “Stop and report” is this checkpoint. The later exact-key
capability, redundant-question work, automatic start and demo are not claimed
complete or run here. They follow the human review; no demo exception was used
to spend estate requests before this report.

Validation checkpoint: 141 focused safety/controller/oracle checks passed (the
additional bookmark-order test passed with all 42 extraction tests). The first
full run finished 2,671 tests with 14 TAPE_UNCOMMITTED_ENGINE errors: the recorder
correctly refused to seal a dirty source tree. Its log is preserved at
.local/round-eleven/part-two-regression.log. A parallel fail-fast run overlapped
source edits and refused changed engine identity; it is not a clean regression
result. A committed-source full rerun follows; neither refusal was bypassed.
