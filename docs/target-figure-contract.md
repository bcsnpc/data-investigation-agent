# Target resolution and server-owned reported figures

2026-10-02, America/Chicago. PR A of the user's two-PR instruction.
Parent: main `42b736b`; section 0's quantity-bound self-report is unchanged.

## Closed target contract

`definition_target` is a consumer-owned, closed discriminated record, or null
when no target resolution has been supplied. Historical proposals without this
new field remain readable; absence is not converted into an evidence resolution.

| Resolution | Required content | Consumer validation |
| --- | --- | --- |
| EVIDENCE | Column ID, inventory entry ID, exact stated-value ticket span | Conserved inventory; referenced entry ACTIVE and restricting that column |
| STATED | Column ID, exact ticket span | Closed shape and exact span; named-column interpretation remains intake judgment |
| REFUSED | Exact ticket span, zero or multiple distinct candidate column IDs | One candidate cannot be represented as an ambiguity refusal |

The model-facing wire schema explicitly excludes the resolution record. It cannot
emit EVIDENCE. `definition_target.evidence()` is a deterministic consumer-side
constructor, requiring authoritative inventory/active-set inputs and validating
them before returning a record. A separate shape validator admits the persisted
record to the envelope; shape alone is not inventory provenance verification.
PR B must provide the pinned inventory lookup and named-column binding before
accepting a resolution. This PR does not perform those lookups or claim that a
reported selection now resolves against the estate.

The new target identifies a **column**, as requested. The adapter's pre-existing
`definition_target_id` selector identifies a **retained visual definition part**.
They are distinct identities, not aliases. PR B must select a unique applicable
visual using the resolved evidence; it must not pass a column ID as a visual ID
or invent a target when several visuals remain possible.

## Figure forwarding

Reviewed intake already owns NUMBER/EMPTY/UNSPECIFIED, span provenance and stated
precision. Preview now takes that record from the saved server-side intake, with
no client resend. An old client may resend the identical record; replacements
and unreviewed figure injection remain refused. The process scope copies the
figure and target record without changing either. No precision, tolerance or
absence defaults were added.

Tests exercise the actual saved intake, preview, session admission and process
dispatch, capturing the scope at the adapter's declared-context boundary without
executing a cloud read. Exact, reduced-precision, EMPTY and UNSPECIFIED records
are identical there. Removing either forwarding step makes the test fail.
PR B still owns the direct no-figure attribution test and target-selection wiring.

## Surface-kind confirmation

DAX self-reports ProviderName from INFO.PROPERTIES in the quantity statement.
SQL self-reports the product prefix of @@VERSION in its quantity statement.
Both are ENGINE_PRODUCT descriptors under #302, not engine version descriptors.
Version strings never establish difference, even when placed in the engine slot;
the existing hostile grading tests enforce that. Section 0's statements, compiler
admission, self-report bindings, permissions and snapshot rules did not change.
The combined quantity statements remain not live-verified.

## Validation and limits

Eight new tests cover missing kind, missing entry, conditional provenance,
unconserved inventory, wrong column, exact span, refusal shape, closed model
schema, and end-to-end server-only forwarding. Thirty existing intake tests pass.
The model-facing payload, directory entries, SQL-object entries and payload
characters are unchanged: the new consumer-only property is removed before wire
serialization. Existing byte-exact twelve-case intake golden tests verify this.

README and current status updated. Engine bytes changed and invalidate previous
freezes. No investigation runs, model/cloud requests, ledger rows, fixture changes,
policy changes or historical evidence edits. Draft #297 stays open. Stop after
PR A merges; PR B is the next separately reported stage.
