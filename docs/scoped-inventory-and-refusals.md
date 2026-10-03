# One scoped inventory validator and honest refusal delivery

Implemented 2026-10-03 UTC after PR C #318 merged at `dad5ba7`.

The unscoped declaration-inventory validator is deleted. Extraction emits the
report-scoped shape, including report identity, source identity and effect. Active
restrictions still have exactly one source: ACTIVE inventory entries. Resolution,
reproduction and synthesis all call `report_scope.validate_inventory`, with the
binding and retained report catalog. Historical target shapes remain readable;
new evidence validation never falls back to an unscoped inventory. Missing
inventory remains distinct from a malformed inventory. The scoped function owns
conservation, ACTIVE coverage, effect, volatility and assumption validation.

The permanent AST audit enumerates the twelve inventory-validation call sites
across seven modules and requires the single function. A synthesis test supplies
an original scoped inventory, then a foreign report identity; the latter is
rejected. Existing hostile-producer tests are migrated to the scoped schema,
including unsupported declarations, missing dispositions, missing restrictions
and invalid consumer enum values.

## Why the receipt registry did not prevent this

PR #312 centralised receipt-kind recognition, dispatch and terminal refusal
rendering. It explicitly did not validate each kind's content. The registry sent
DECLARED_CONTEXT_DEFINITION to context synthesis, whose content validator still
accepted only the older inventory shape. Registering the kind therefore could
not prove that the inventory contract was conserved. The inventory schema should
not be duplicated in the registry: registry dispatch selects the content route,
and that route now invokes the same scoped validator as every other consumer.
The AST and synthesis tests protect that link. Recognition is never validation.

## Why the business identifier test missed the URI

The normal business-composition validator tested identifier form, but the
separate deterministic refusal renderer copied the technical reason into both
outputs and called no narrative validator. `narrative_form.validate` also had no
identifier-form check. The shared form guard now applies to all business
narratives, including refusals. Technical details and original reasons remain in
the receipt and technical output. Business refusal wording is engine-rendered
from the explicit refusal category, with a safe generic blocker for historical
technical reasons. Identifier-bearing ticket text is retained verbatim in the
technical explanation; the business question uses a safe procedural description.
Tests reject URIs, qualified names, underscores, bracketed names, paths and
receipt identifiers, while allowing plain Sales and Customers.

## Refusal audit

Selection resolution now distinguishes AMBIGUOUS (multiple matches), UNAVAILABLE
(missing coverage, cap, or refused probe), VALUE_ABSENT (completed non-match), and
UNSUPPORTED (unknown declaration form). A missing named column is unavailable;
a nonunique named column is ambiguous. Zero legacy ACTIVE matches are unavailable;
multiple matches remain ambiguity. Missing and multiple visual targets have
separate forms. Missing/unnamed reports are unavailable; multiple exact report
names are ambiguous. No refusal is weakened or upgraded into a finding.

No initial directory or planner catalog construction changed: directory entry and
SQL-object coverage are unchanged by this PR. Scoped inventory and business
refusal changes apply to retained evidence and output paths, not catalog budgets.

Validation results and all six CI checks are recorded on the PR. Failed local
migration attempts are retained under `.local/`. No investigation or offline
investigation replay, estate request, provider call, fixture/config/policy/grant
change or ledger row. These engine changes invalidate prior freezes. The three
unchanged live tickets wait until this PR merges.
