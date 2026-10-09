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
confirmation/link/closure/reuse changes passed 142 targeted tests; their clean
full regression is pending. Do not weaken the committed-tape or engine-change
refusal to make the suite pass.

Phase B exports use existing identities and the unchanged estate pot; denied
exports are retained failures, never a reason to elevate. Phase C is a design
for review only. Neither is complete at this checkpoint.

No identity, permission, secret, estate fixture, policy counter or acceptance
expectation has changed. No model or estate request has been made. Engine bytes
changed, so earlier freezes are invalid. No investigation ledger row is added
for these offline component changes.
