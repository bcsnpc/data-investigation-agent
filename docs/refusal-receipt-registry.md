# Registered receipt shapes and refusal delivery

Date: 2026-10-02. Follow-up to merged #311 (`71a3e2f`).

Synthesis accepts process shapes from `process_receipts.REGISTRY`; query receipt
tables derive from the same registry. Original validators still check declared
reproduction, selection resolution, cross-surface grades, snapshots and sealed
query receipts. Registration is not permission to conclude. Unknown shapes fail
with their name. Refusals render deterministically, with no provider call and no
replacement classification, using the earliest retained reason. Intake ASK/HELD
records expose both outputs through the same renderer. Held walks carry explicit
refusal receipts. Supported findings retain the existing validated synthesis path.

Tests cover every registered shape's terminal display, each refusal stage,
earliest attribution, a hostile unknown shape, producer check-kind literals,
original resolution validation and the actual synthesis runtime's zero-call
refusal path. No registry or rendering vocabulary is added to model payloads;
a golden test requires byte-identical evidence/digest after registry expansion.
Directory entry/SQL-object coverage remains unchanged (28/11 in the existing
planner goldens). Existing digest payload characters are unchanged for an
existing supported run; newly admitted refusal records are retained in full.
No fixture, policy, permission, read cap or historical receipt changed.
Engine bytes changed; all earlier freezes remain invalidated.

## Offline preserved-run synthesis

Three NEW offline counterfactual runs use the original raw session states and
sealed receipts through a read-only SQLite connection; socket connections were
blocked. Zero estate reads and zero model calls. One ledger row per offline run.
The original three live failures, BLOCKED syntheses, tapes and ledger rows are
unchanged. These outputs say what those runs would have delivered with this
renderer; they do not assert that the old runs delivered them.

### R1 ? offline-refusal-4ec919a5-73fd-45fa-9b59-7f83a0ae251c

Source: `f90928fb-732a-4bf7-a5f2-f72419c87ace`.

Business Output (verbatim counterfactual):

```text
You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.
Answer to your question: Not answered.

The investigation stopped during selection resolution.
Reason: Unsupported declared restriction form VALUE_EXISTENCE_RESULT; faithful translation required.
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
```

Technical Output (verbatim counterfactual):

```text
You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.
Answer to your question: Not answered.

The investigation stopped during selection resolution.
Reason: Unsupported declared restriction form VALUE_EXISTENCE_RESULT; faithful translation required.
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
```

### R2 ? offline-refusal-29b44329-f143-4993-a9db-64bc4e276670

Source: `480a603a-aea6-426d-9135-6eeb96ea2f83`.

Business Output (verbatim counterfactual):

```text
You asked: In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate shows nothing (the visual is empty) for Handled Quantity. I selected warehouse North. Check whether the saved declared report context reproduces what the visual shows and explain what remains unknown about my selections.
Answer to your question: Not answered.

The investigation stopped during selection resolution.
Reason: Target ambiguity: no scoped grouping column can test the stated value.
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
```

Technical Output (verbatim counterfactual):

```text
You asked: In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate shows nothing (the visual is empty) for Handled Quantity. I selected warehouse North. Check whether the saved declared report context reproduces what the visual shows and explain what remains unknown about my selections.
Answer to your question: Not answered.

The investigation stopped during selection resolution.
Reason: Target ambiguity: no scoped grouping column can test the stated value.
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
```

### R3 ? offline-refusal-a7cd953d-4933-4cc2-be88-6aa4c2094536

Source: `cb751286-0cb1-4926-bacd-c686ced5ddbb`.

Business Output (verbatim counterfactual):

```text
You asked: In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate shows 9 for Handled Quantity. I selected warehouse North. Check whether the saved declared report context reproduces what the visual shows and explain what remains unknown about my selections.
Answer to your question: Not answered.

The investigation stopped during selection resolution.
Reason: Target ambiguity: no scoped grouping column can test the stated value.
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
```

Technical Output (verbatim counterfactual):

```text
You asked: In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate shows 9 for Handled Quantity. I selected warehouse North. Check whether the saved declared report context reproduces what the visual shows and explain what remains unknown about my selections.
Answer to your question: Not answered.

The investigation stopped during selection resolution.
Reason: Target ambiguity: no scoped grouping column can test the stated value.
No explanation of the reported difference was established.
Recommended action: Resolve the stated blocker before a new investigation.
```

## Why the original read counts differed

This was not lookup memoization. `report_resolution._prepare` first searches
ACTIVE declarations for the exact selection value. If none matches, it tries
only report-scoped grouping columns. R1's retained table visual exposes a
warehouse-name grouping column, so the whole quoted phrase was looked up once;
the returned BLANK did not satisfy the adapter's existence-result contract.
R2/R3's fixture cards expose no grouping column, and no ACTIVE predicate carries
the whole phrase, so they refused before dispatch. The run-local compiled quantity
cache is a different primitive, was not reached and cannot explain these counts.
Value/descriptor separation is the next separate PR. No live reruns here.
