# Declaration refusal attribution

Date: 2026-10-02 UTC. Correction to the masked refusal in family D run
`6582f4a1-e8a0-4bb1-b8a3-c41286fa4e12`, preserved in draft #297.
No investigation run or ledger row occurs in this PR.

## Defect and changed behaviour

The procedure previously invoked inventory validation before checking whether
extraction had already refused. An ambiguous definition target therefore became
"Required declaration inventory missing or malformed". The inventory was not
malformed: the adapter had refused before constructing one.

The existing declaration `status` now discriminates collection from refusal.
UNDECLARED / UNAVAILABLE with an explicit reason terminate the side check before
inventory validation. Their original status, reason and optional unsupported-form
label survive unchanged. The procedure neither interprets native labels nor
makes a refused declaration eligible. Even a malformed unused inventory cannot
replace an earlier refusal.

DECLARED responses still require inventory validation, conservation and ACTIVE
coverage. A missing inventory raises the distinct `MissingInventory` exception,
producing DECLARATION_INVENTORY_ABSENT and "Required declaration inventory was
not supplied". A present malformed shape produces DECLARATION_INVENTORY_CONTRACT
and "Declaration inventory is malformed". Invalid declaration statuses and
refusals lacking a reason produce DECLARATION_RESPONSE_CONTRACT, rather than
pretending inventory validation occurred. No fallback eligibility or read was
introduced.

This separates three states: upstream refusal (input not produced), absent input
without such a refusal (producer contract failure), and supplied malformed input
(validation failure). The first refusal owns the user-visible message. It applies
to any adapter implementing this neutral procedure, not a ticket family or native
kind. The adapter and ticket/procedure wiring are unchanged here.

## Hostile producer tests

New tests supply upstream UNDECLARED and UNAVAILABLE refusals with both absent
and malformed unused inventory, and assert the exact original reason/status/form.
They patch inventory validation to fail if invoked, proving the refusal bypass
rather than only comparing a nicer string. A second hostile producer declares a
malformed inventory and must surface its exact validation error. A third declares
without supplying inventory and must surface the distinct absent-input error.
Invalid producer statuses and reasonless refusals are separately rejected. All
cases assert zero reproduction reads.

Validation: 38 reproduction, 25 inventory and 46 adapter tests pass. All 1,436 final regression tests passed
in 262.928 seconds. All 395 local documentation targets resolve; git diff --check
passes. Planner payload construction and directory
coverage are unchanged; the existing exact goldens remain in the regression suite.
README/current status/progress updated. Engine bytes changed, invalidating prior
freezes; no new freeze, investigation, provider/cloud calls, fixture change,
permission, credit or budget alteration.

## Preserved evidence and next work

The original family D outcome and verbatim outputs are not rewritten or upgraded.
Its one read, failed reproduction prerequisite and existing ledger row remain
exactly as recorded on draft #297. That draft stays open for the later runs round.
This is a correction to attribution, not evidence that reproduction executed.

The definition-target/reported-figure wiring is the next separate work item.
The BLANK, reported-empty and partial-attestation questions remain to be answered
before any runs. The original 14 September empty selection and pinned context are
preserved. The conditionally authorised fixture change is not performed here.
