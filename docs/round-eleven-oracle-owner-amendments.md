# Owner and reviewer oracle amendments: diff before sealing

Recorded 2026-10-09. Decisions supplied in `oracle-approval.md` by owner
Chiranjeevi Bhogireddy and independent reviewer Claude. The conditional approval
requires the amendments and a field-by-field diff before sealing. This is that
diff checkpoint; no oracle has been sealed or used for a score.

All 68 records have changes, including question reasons and evidence provenance.
The exact before/after values for every changed field are in
[oracle-approval-diff.md](../acceptance/oracle/oracle-approval-diff.md) and
[oracle-approval-diff.json](../acceptance/oracle/oracle-approval-diff.json).
The reviewed originals are preserved byte-for-byte as the before-owner-review
JSON and Markdown files. No original golden record, expectation or split changed.

The substantive amendments are:

- A chooses APPLICATION, with no comparator question.
- E/G short freshness/application asks do not require a displayed target.
- R1 collapses inconsequential card/total choices only where complete retained
  definitions establish the same requested measure and declared restrictions.
- R2 supplies family intent for consequential questions, including D's North
  matrix row and H's Received Units card, without inventing reported figures.
- Both conflicting-figure cases ask FIGURE once and retain both values, with no
  selected primary. Unknown-report cases ask once and retain the cannot-tell hold.
- Change-over-time remains the sixth, unsupported route; no current-state route
  is substituted and no clarification is required.
- The three stated figures are exact 16. The hiding-rows target is the card with
  the retained `event_day` declaration, not a card selected because of its value.
- Business refusals have no applicable reported figure. I retains technical
  APPLICATION work and a separate BUSINESS_VALIDATION handoff.
- Unsupported-filter, nonexistent-column and relative-date limitations retain
  holds rather than substitute a supported context.

## R1 evidence and the catalog projection gap

The synthetic intake catalog retains titles and query field references but omits
`definition/report.json` and the predicates. Parsing that projection refused
MISSING_PARENT_DEFINITION; its missing predicates were not treated as no filters.
The complete preserved local catalog supplied the missing evidence, without an
estate request. Each equivalence record carries its context ID/hash, all candidate
IDs and the independently extracted restrictions. Context body hashes are checked
before parsing. Every candidate must parse completely, with no UNSUPPORTED entry,
and every restriction set must agree. Model/measure identity alone cannot pass.
The retained contexts also distinguish the two cards on Saved predicate selections:
only the extra-predicate card declares `event_day = 2026-09-15` in this context.
This is definition evidence, not a value query or snapshot-currency assertion.

## One target exception and nine undetermined records

R5's description for `refusal-unsupported-relative` does not identify a unique
card. Round Nine translation filters contains:

1. Handled Quantity - unfiltered, on Top-N verification.
2. Handled Quantity - page and slicers, on Saved predicate selections.
3. Handled Quantity - extra visual predicate, on Saved predicate selections.

Those are different declared contexts. The revised record names all three IDs,
leaves its target UNDETERMINED and keeps HOLD_UNLESS_RELATIVE_DATE_TRANSLATION_VERIFIED.
The reported 16 is never used to choose the card. This exception is disclosed
rather than silently assigning the third card or assuming equivalence.

Nine records retain an undetermined field: question-change-days,
question-change-week, refusal-two-figures, refusal-two-figures-total,
refusal-unidentified-visual, refusal-unidentified-measure,
refusal-unsupported-filter, refusal-unsupported-relative and
refusal-nonexistent-column. The diff lists each field and its reason. These are
the unsupported/held cases, not permission to manufacture a clarification answer.

## Validation and recording

Five oracle tests pass: original seals/partition conservation, exact field-diff
coverage, R1 evidence requirements, cannot-tell/time-change/business rules, and
the preserved original draft hash. Intake, engine and adapter code are unchanged.
The earlier 2,672 full regression result remains its dated result; no fresh full
suite or conversational quality claim is made here.

Zero model calls and zero estate reads. No budget, identity, permission, secret,
fixture, golden, acceptance expectation or split change. PR #423 remains draft.
No live work or simulator scoring follows this pre-seal diff checkpoint. The
original reviewed draft remains identifiable by SHA-256
0bce64af7690c4fc86b7e9bfd2e796d80dfc5a3aadf1154f605cac21254e11dd.
