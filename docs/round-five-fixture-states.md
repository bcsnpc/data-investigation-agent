# Round Five E: fixture-state binding and offline grading

2026-10-05 UTC. Sections 1-3 only. No cloud requests, fixture mutations,
identity changes, pre-warm or live investigation. Round Five remains 218/400;
rolling allowance 1,500 and diagnostic cap 12 unchanged. Prior freezes invalid.

## State, not recollection identity

The human withdrew context-ID equality as an acceptance criterion. All fifteen
v4 cases now name a fixture state. Their historical context pins remain reference
provenance, not equality oracles. The fixture manifest declares inventory-baseline,
report-14sep, report-15sep, source-baseline, source-gap, source-latency and
source-unreachable, including predicates/mutations/reachability and independent
arithmetic references. No expected arithmetic is projected into tools, prompts
or quantity contracts. The whole-manifest discovery hash still changes.

A context ID cannot identify data state: source-gap and source-latency shared
metadata while different rows/times were present. The new operator registry records
an explicit state/context approval with its evidence reference; it never infers
state from a context or grants discovery approval. The runner selects the latest
approved retained context for the named state and refuses without an approval.
Two approved contexts for one state satisfy the same case; a different state
refuses with both names. An altered definition under one name also refuses.
Model enablement, immutable context integrity, whole-config discovery approval
and denies remain in force. No actual state approvals were fabricated this turn.

New tapes record the state declaration hash, actual context ID/hash and approval
reference together. The validator rejects a state bound to a context that was
not selected. Old tapes are unchanged: separate retrospective associations bind
known fixture controller/derivation evidence to session ID, source artifact hash,
tape hash and actual retained context. They are labelled retrospective, not native
recording or snapshot attestation. There is no global context-to-state inference.

## Original estate roles

The retained legacy configuration has only three source-fixture roles. The
current authoritative installation manifest already declares the original
SEMANTIC/SERVING/REFINED/LANDING assets. We reuse those explicit declarations;
we do not infer a role from position or names or amend old configuration receipts.
Historical A/E payloads had an empty layer-label map. A separate dated grading
view now joins exact asset identities to those current declared roles, including
when the old map was empty. Original receipts, labels and narrative bytes remain
unchanged. The role checks concern explicit current estate declarations; this
is not a claim that historical prose natively carried them. Unknown assets still
have no role and fail. Future live execution requires current discovery approval
under the changed installation; no recollection was performed in this offline step.

## Intentional expectation changes

PR #372 changed declared-question-kind/evidence coverage after the reference runs.
Only these answer-category expectations change; neither outcome changes:

| Case | Previous | Current | Basis |
| --- | --- | --- | --- |
| E | NOT_ANSWERED | PARTLY_ANSWERED | #372: inspected processing evidence is qualified partial freshness coverage |
| Source gap | NOT_ANSWERED | ANSWERED | #372: supported delivery finding answers the declared delivery question, with retained limits |

Each case retains the date, PR number, previous/current category and reason.
No expectation was changed to accommodate I or source consistency's failed run.

## Regrade column

Same original fifteen: 11 replayable, 8 accepted after state/role/intentional
category changes, versus 1 accepted previously. Four old recording gaps and
three substantive original failures remain (F missing outputs, I different
outcome/path, source consistency missing the application comparison).

| Ticket | Original tape regrade | Retained evidence selected now |
| --- | --- | --- |
| family-A | PASSED | PASSED |
| family-B | PASSED | PASSED |
| family-C | PASSED | PASSED |
| family-D | TAPE_UNRECORDED_IDENTITY:10543e9a-8a9e-4ac2-9596-e9cc127c209e | TAPE_UNRECORDED_IDENTITY:10543e9a-8a9e-4ac2-9596-e9cc127c209e |
| family-E | PASSED | PASSED |
| family-F | business_output:MISSING_OUTPUT; technical_output:MISSING_OUTPUT | PASSED |
| family-G | TAPE_UNRECORDED_BUDGET_INPUT | TAPE_UNRECORDED_BUDGET_INPUT |
| family-H | TAPE_UNRECORDED_BUDGET_INPUT | TAPE_UNRECORDED_BUDGET_INPUT |
| family-I | STRUCTURE:boundaries; STRUCTURE:layers_reached; STRUCTURE:outcome | PASSED |
| reproduction-16 | PASSED | PASSED |
| reproduction-empty | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE | TAPE_EVENT_DIFFERS:BUDGET:PROVIDER_RESPONSE |
| source-consistent | STRUCTURE:answer_category; STRUCTURE:boundaries; STRUCTURE:outcome; business_output:ANSWER_CATEGORY_CHANGED; technical_output:ANSWER_CATEGORY_CHANGED | STRUCTURE:answer_category; STRUCTURE:boundaries; STRUCTURE:outcome; business_output:ANSWER_CATEGORY_CHANGED; technical_output:ANSWER_CATEGORY_CHANGED |
| source-gap | PASSED | PASSED |
| source-latency | PASSED | PASSED |
| source-unreachable | PASSED | PASSED |

F's later completed synthesis **was recorded**, session ae3436f4-3f72-4b7d-9e60-823a69ad83b0.
It byte-exactly replays and passes the unchanged CONSISTENT_TO_BOUNDARY expectation.
I's Q49 run e726e66c-17d1-4171-a6d3-ccb978aa800c also byte-exactly replays and
passes the unchanged TRANSFORMATION_LOGIC expectation under inventory-baseline.
Its different recollection ID is not a different fixture state. Both are existing
live evidence, not new live attempts; their earlier failed runs remain preserved.
Using these two existing tapes gives 10/15 accepted, still 11/15 replayable.

Remaining: D unrecorded identity; G/H unrecorded budget input; EMPTY pre-canonical
provider request bytes; source consistency stopped at CONSISTENT_TO_BOUNDARY
rather than the earned CONSISTENT_TO_SOURCE because its application quantity
failed. The old 40613 and later post-connect OSError attempts remain separate.
No failed result was upgraded and no output was backfilled from fixture arithmetic.
F and I require no new live attempt merely to obtain recording evidence.

## Tests and stop

Five state-selection/role-view tests, 19 manifest tests, 24 tape tests and ten
gate tests passed. A real synthetic process records, validates and byte-exactly
replays its state/context pair; a mismatched pair refuses. State arithmetic never
enters runtime configuration (except the changing whole-manifest approval hash).
Directory coverage remains 2 entries / 1 SQL object / 7,540 characters before/after.

Original ledger prefix preserved; 15 first grading rows, 15 role-view grading rows,
two retained replay rows and two grading rows appended, all zero requests.
The first role-view implementation updated only existing labels and exposed A/E's
empty map; the corrected view supplies exact declared identities. Both grading
stages remain in the ledger rather than rewriting the first result.

Stop at the requested section-3 checkpoint. Section 4 error retention, declared
serverless resume/pre-warm and per-layer worker deadline are **not implemented**
in this PR. No section-5 run. #376 stays draft at 10/15; CI also lacks its private
replay inputs and must not treat missing inputs as a pass. No new freeze or
unfamiliar-domain acceptance claim. README verification claims are not advanced.
