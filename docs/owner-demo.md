# Owner portal demo — 2026-10-11, America/Chicago

**Live demonstration blocked; offline portal inspected.** The isolated copy is
`D:\dia-round-fifteen-demo`, branch `feat/round-fifteen-owner-demo`. Its catalog,
inventory and future capture folder are separate. No original record, context
pin, estate value, credential, permission or budget counter was changed.

## One start command

From PowerShell, run the following once with a fresh folder name:

```powershell
Set-Location D:\dia-round-fifteen-demo
C:\Users\chait\anaconda3\python.exe scripts/owner_demo.py --source-manifest D:\dia-round-eleven-links\.local\round-fourteen\original-pipeline-control-24000-original-inventory\estate.json --folder .local/owner-demo --port 8791
```

This creates read-only SQLite backups in the isolated copy and opens the portal
with an ephemeral local access key. It does not copy credentials. Existing
relative profile/library references remain references only. Execution is disabled,
so it cannot issue an estate request or model request. Do not append `--live`:
that option deliberately refuses before preparation or any live admission.
The server occupies the terminal; Ctrl+C stops it. A used destination folder
refuses rather than overwriting its records. No other terminal step is required
for this offline view.

## What to open and submit when live isolation is supported

1. Open the browser tab titled **Investigator · Investigations** at
   `http://127.0.0.1:8791/`.
2. Choose **New investigation**. Use the preserved original family-A form:
   report **Inventory Health e1b8e1**, page **Inventory Health**, visual
   **Movement Units**, comparison **application source**, and this unchanged
   description (no reported value was given):

   > In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.

   Its original sealed form is under
   `.local/round-twelve-e/live-forms-c377331/original-family-A/input-and-expectation.json`;
   only the form fields are used for submission. Do not replace it with a billing
   ticket, a broadest visual guess or an authored simplified complaint.
3. A successful future live run should show progress and then the recorded
   transformation finding: **7,661 → 8,765**, with the retained left-join
   mechanism, distinct input/output roles, and the snapshot/surface limitations.
   This is expected demonstration behavior from prior recorded evidence,
   **not a result earned by this Round Fifteen demo**.
4. Read both outputs before using the ticket's comment/agreement step. Agreement
   is a user's discussion response, not validation of business correctness.

The present portal explicitly says **“This host shows history and scope previews.
Live execution is disabled.”** Do not submit a live ticket here or interpret
copied historical rows as a new demo. The original family-A submission, fresh
progress, finding and comment/agreement flow were **not run** this round.

## Why the live demo is blocked

`UsageGovernor.reserve(db, ...)` and `settle(db, ...)` use the same SQLite
transaction as the session lifecycle. The accounting tables live in the catalog.
Copying that catalog forks the rolling allowance, daily counters and pot; sharing
it allows the demo to mutate original session records and discovery pins.
Neither satisfies the user's isolation and unchanged-budget requirements.

A safe implementation needs a neutral shared-accounting port, with coordinated
SQLite transactions against only the budget tables and recording/replay support
for that arrangement. It needs tests proving that two isolated session catalogs
share the same ordinary allowance, model counters and pot without resetting them
or touching each other's sessions/pins. No temporary reconciliation, table copy,
counter reset or separate pot was used to bypass this missing interface.

The approved shared dollar guard remains **$190**, with **$10 protected**, and
the shared physical pot remains **4,000**, with **95 restoration requests
protected**. The isolated launcher never admits live work, so this section spent
**0 estate requests, 0 model calls, $0**. The 23:30 Central live-admission cutoff
is enforced if live mode is requested. No identity, scope or secret changed.

## Verification transcript

- Created a separate git worktree at 9d6b4b8.
- Backed up source catalog and inventory through SQLite's read-only backup API;
  original rows remain untouched. Hashes and source manifest hash are retained
  privately in `.local/round-fifteen/owner-demo-offline-v2/isolation.json`.
- First offline startup refused a now-absolute profile/library reference:
  `ValueError: SQL session profile must be a relative path`. It made no request.
  The isolated launcher now retains those constrained relative references;
  tests cover no credential copy and unchanged source manifest.
- Second offline startup opened Edge through the existing portal launcher.
  Browser control inspected the visible portal and **New investigation** form.
  Its visible state explicitly disabled execution and said live listing was not
  connected. The catalog copy contains historical fixture/billing entries; none
  were scored as a fresh run.
- Captured the visible offline portal through the browser screenshot tool in the
  working conversation. No fresh finding or completed investigation screenshot
  exists. The screenshot is not represented as a sealed live capture.
- Two isolation/refusal regression tests passed. Existing launcher tests were
  also run separately: three passed. Two earlier test invocations failed on an
  import path and a mutable mock/unclosed synthetic database; these setup
  failures were corrected and retained in the working transcript.
- Stopped the offline server after inspection; no background demo worker was
  left running.

This is a working offline portal start command plus an identified architectural
blocker, not a completed live owner demonstration or owner acceptance.

## Dated supersession — shared accounting implemented

The owner subsequently directed this round to use the same existing dollar and
pot ledgers from the isolated copy. The earlier blocker and offline inspection
above remain historical. The new optional `storage.shared_accounting` port
attaches that existing budget file to the isolated catalog connection. Only the
consumer-owned budget tables and journals are addressable; shared model,
discovery and ticket records cannot be read or changed. DELETE, DROP and changes
to reserved amounts are refused. Connection-private settlement guards also
refuse to release an existing reservation owned by another catalog. Ownership
keys are acquired only after a successful single reservation insert in the same
transaction, and persist only in the isolated catalog. Both files must retain DELETE journal mode;
the same SQLite transaction commits the session transition and reservation.
No copied accounting table governs live admission.

The recorder materializes a budget-only snapshot into the sealed private
bootstrap. Replay uses that snapshot locally and never attaches the live ledger.
Tests exercise two isolated catalogs sharing physical and model caps, joint
rollback, forbidden shared-record/reset access and exact external-delta replay.
An explicit existing-secret-root locator references the original DPAPI/MSAL and
CLI mechanism without copying it; every reader's identity checks remain intact.

The live start command, after current-source checks and approval, is:

```powershell
Set-Location D:\dia-round-fifteen-demo
C:\Users\chait\anaconda3\python.exe scripts/owner_demo.py --source-manifest D:\dia-round-eleven-links\.local\round-fourteen\original-pipeline-control-24000-original-inventory\estate.json --budget-manifest D:\dia-round-eleven-links\.local\round-fourteen\billing-pipeline-span-grounded-bb971f0\estate.json --context-id a6b6b130-e955-432d-8433-f2f7203302a2 --context-hash e3cce421b4b694b005d9643c40dd0c66035e7a35cf0b3af0495ae655ff3e9dd5 --folder .local/owner-live-demo --port 8791 --live
```

The second manifest supplies only already-approved current budgets, not billing
readers, definitions or data. The original fixture configuration and retained
source context remain the source. Preparation explicitly re-approves those
unchanged definitions only in the isolated catalog and records the new context,
configuration and source hashes. No cloud metadata is recollected. The server
uses the original shared dollar file, $190 ceiling and $10 margin. POST admission
and live catalog requests close at 23:30 Central with an explicit cutoff message;
already-admitted workers finish and their tapes close.
The live trial has not yet been admitted at this implementation checkpoint.

### Dated pre-admission visual-label finding

The first live portal startup charged two reader metadata controls (report and
page listings), with zero diagnostic reads or model calls. No family-A ticket
was submitted. Its dropdown displayed four different visuals as “Inventory
Health” because it used the first lookup alias, which happened to be the page
name. Selecting an internal URI would have concealed the problem from the owner.

The repair preserves lookup aliases exactly and projects explicit retained visual
titles through a separate display port. It does not subtract names by string
equality: a visual genuinely titled “Sales” on a page named “Sales” still displays
“Sales”. Untitled visuals are reported as unavailable rather than given an internal
ID. The ticket's selected facts use these same explicit titles. This is a UI
projection change, not another intake classifier or per-ticket patch.

## First live portal trial ? 2026-10-11

Original family A has now executed once through the portal, producing the actual 7,661/8,765 comparison and TRANSFORMATION_LOGIC, partly answered. Both explanations were read; a clearly agent-operated demo comment and agreement closed the isolated ticket. This required a normal local restart after the Open ticket link lost its memory-only key; the generic link repair and title repairs are recorded, so this is not a seamless unaided-owner claim. The full verbatim outputs, steps, costs and limitations are in [the live transcript](round-fifteen-owner-demo-trial.md). No independent owner acceptance or general estate capability is inferred from this one ticket.
