# Fixture-authored numeric declared-context runs 4 and 5

Date: 2026-10-03 America/Chicago. #327 merged as `5da055e` after six green
checks. No engine or adapter code changed. Prior freezes remain invalidated;
these are known-domain fixture regressions, not unfamiliar-domain acceptance.

## Budgets, estate change and preserved failures

At 16:08:11 UTC the ordinary diagnostic rolling window was 25/60, with 35
available (older reservations aged out from the previously reported 38). There
is no persisted rolling metadata window in this implementation: discovery uses
separate per-scan limits of 160 operations, 600 seconds and 32 MiB. No roll time
exists for that per-scan budget. The prior 95-physical-read scan fit; this scan
actually used 94 operations and 100 physical reads: 93 HTTP metadata requests
and seven SQL catalog commands. It completed within the unchanged time/byte
bounds. No degraded recollection, allowance increase, new credits, reset,
refund, permission change or deadline extension.

The publisher admin@skynwhy.com changed only the target card's literal date
predicate from 2026-09-14 to 2026-09-15. No other report, model, data, bookmark,
page/slicer predicate or schedule changed. This was disclosed to make a numeric
declared result available: under all saved defaults on 14 September, the only
matching movement is ISSUE, excluded by the RECEIPT page restriction, so SUM is
BLANK. Both fixtures' figures are authored, not real user observations.

Two local harness startup failures are preserved: the default Python lacked
fabric_cli, then the direct reader helper lacked msal. Neither initiated an
estate request; the second left one conservative UNCERTAIN read reservation,
which was not refunded. The configured authentication/reader workers were then
used. Exactly one update was sent. Its operation reported Succeeded; a subsequent
result GET returned HTTP400 OperationHasNoResult. The harness stopped and retained
that failure. Completion was established from the successful-operation receipt,
not by resending the mutation; recollection independently confirmed the change.
Publisher verification used five HTTP metadata reads and two reader DAX baselines,
both 8,765, plus the one mutation. Ordinary reservations rose 25 to 33 (seven
initiated reads and the one uninitiated conservative reservation).

The new context is `35461b1d-b5a4-48ef-a61d-aa539403a188`, model revision 5,
scan `37923df5-83d6-425d-8eff-b4f691941bb5`, raw inventory
`bb360bc5-97f2-4354-9b00-7b30a9c8432f`. Context and discovery approval pin the
whole-config hash `19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6`.
All 16 definition parts, two pages, seven visuals and every predicate survived
collection and parseability checks; no missing or changed part against the
published update. The target event_day literal is `'2026-09-15'`; the conditional
bookmark remains unchanged, including its older date. The old `3ae7607b…`
context, its pinned config, 14-September derivation, prior run tables and 280
protected files were checked unchanged before the runs. After the runs, original
rows and files remain unchanged; ledger is an unchanged prefix plus six new rows:
two investigations, two local failures, one estate-change record and one scan.

## Independent arithmetic

No engine/compiler query supplied a figure. The evaluator reads the seeded
Bronze input, removes exact duplicates, and independently implements the retained
product-only left join and SUM of units. Both saved slicer defaults are ACTIVE.
The full derivation below names every surviving movement ID at every stage;
the final rows are movement 10 (North/Component 1/RECEIPT/15 September, 4 units)
and 238 (same scope, 12 units). Each matches exactly one product-rate row, so
the numeric quantity is 4 × 1 + 12 × 1 = 16. Page plus both slicers yields 92;
without report declarations yields 8,765. Run 5 uses 17, the first integer above
16 not equal to any candidate (16, 92 or 8,765).

Seed SHA256: `77b834a591918aa6faaa747c623c12dc54046907aa528fd29d8931e96a719b62`.

- PAGE_FILTER movement type RECEIPT: 270 surviving movements: 1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19, 21, 22, 23, 25, 26, 27, 29, 30, 31, 33, 34, 35, 37, 38, 39, 41, 42, 43, 45, 46, 47, 49, 50, 51, 53, 54, 55, 57, 58, 59, 61, 62, 63, 65, 66, 67, 69, 70, 71, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89, 90, 91, 93, 94, 95, 97, 98, 99, 101, 102, 103, 105, 106, 107, 109, 110, 111, 113, 114, 115, 117, 118, 119, 121, 122, 123, 125, 126, 127, 129, 130, 131, 133, 134, 135, 137, 138, 139, 141, 142, 143, 145, 146, 147, 149, 150, 151, 153, 154, 155, 157, 158, 159, 161, 162, 163, 165, 166, 167, 169, 170, 171, 173, 174, 175, 177, 178, 179, 181, 182, 183, 185, 186, 187, 189, 190, 191, 193, 194, 195, 197, 198, 199, 201, 202, 203, 205, 206, 207, 209, 210, 211, 213, 214, 215, 217, 218, 219, 221, 222, 223, 225, 226, 227, 229, 230, 231, 233, 234, 235, 237, 238, 239, 241, 242, 243, 245, 246, 247, 249, 250, 251, 253, 254, 255, 257, 258, 259, 261, 262, 263, 265, 266, 267, 269, 270, 271, 273, 274, 275, 277, 278, 279, 281, 282, 283, 285, 286, 287, 289, 290, 291, 293, 294, 295, 297, 298, 299, 301, 302, 303, 305, 306, 307, 309, 310, 311, 313, 314, 315, 317, 318, 319, 321, 322, 323, 325, 326, 327, 329, 330, 331, 333, 334, 335, 337, 338, 339, 341, 342, 343, 345, 346, 347, 349, 350, 351, 353, 354, 355, 357, 358, 359.

- ACTIVE saved warehouse slicer default North: 107 surviving movements: 2, 6, 10, 13, 14, 19, 22, 25, 26, 41, 45, 49, 53, 54, 59, 61, 62, 65, 67, 69, 74, 77, 79, 81, 83, 85, 89, 102, 105, 106, 107, 111, 114, 115, 118, 121, 122, 125, 129, 134, 137, 139, 142, 145, 147, 149, 155, 158, 159, 161, 170, 177, 182, 183, 190, 191, 194, 195, 205, 206, 213, 214, 217, 218, 221, 225, 231, 237, 238, 245, 246, 253, 254, 255, 259, 262, 265, 278, 279, 291, 293, 294, 295, 297, 299, 301, 302, 305, 307, 310, 313, 315, 318, 319, 321, 325, 326, 327, 329, 334, 335, 338, 349, 350, 354, 357, 359.

- ACTIVE saved product slicer default Component 1: 6 surviving movements: 10, 74, 107, 111, 238, 255.

- VISUAL_FILTER event day 2026-09-15: 2 surviving movements: 10, 238.

The code shares no extraction/compose/compiler path with the investigator.
It shares the intended fixture assumptions: the seed is the retained input,
the documented deduplication/join/SUM definitions apply, and both saved defaults
apply. These are named assumptions, not independence of business intent. A match
could fail if publication/collection lost or altered a predicate, the adapter
compiled a different scope, native serving diverged from the seeded/transformed
data, the measure/relationships differed, or the independent arithmetic was
wrong. No expected answer was injected into runtime configuration. The first
numeric match was therefore not guaranteed by implementation or shared code.

## Per-run evidence

Both runs have report STATED with a ticket quote, and North EVIDENCE from the
active saved declaration (DECLARED_BY_DEFINITION), not name guessing. Figures
are NUMBER with EXACT precision and source spans retained. Each candidate's
inventory has nine declarations; validation re-read original receipts and ran
the engine's conservation/ACTIVE-coverage validation. Counts per candidate:
control 0 ACTIVE/9 CONDITIONAL/0 UNSUPPORTED; page-plus-slicers 3/6/0;
target visual 4/5/0. The conditional entries are recorded and excluded, not
silently skipped. The four active target restrictions are RECEIPT page filter,
North saved warehouse slicer, Component 1 saved product slicer, and 15 September
visual date; saved slicers are viewer-changeable assumptions.

Each run made four physical DAX diagnostic reads against cap four; zero guards,
SQL quantity reads or other diagnostic surfaces. Read windows: R4 33→37/60;
R5 37→41/60. Metadata discovery used its separate 94/160-operation scan budget,
100 physical reads. One intake model call per run; zero investigation-planner,
judge or synthesis model calls. No boundary was compared or verified. Both sessions are HELD with
TOOL_UNAVAILABLE and PROCESS_FAILED/ValueError, while deterministic refusal synthesis COMPLETED with
REGISTERED_REFUSAL_DELIVERY. There is no vertical outcome classification.
The separate within-layer answering-cell labels are REPRODUCED (16) and
NOT_REPRODUCED (17), which supply the question header/action. This is not two
completed vertical investigations.

**Native-address gap, not backfilled:** each run's three visual evaluations
carry native compiled cell addresses. The separate shared undeclared-context
baseline does not. Current engine validation requires the addressed lower cell
but admits the unaddressed upper baseline. Thus the user's every-fresh-receipt
address condition is not satisfied, despite synthesis validating. Neither receipt
was modified or derived retrospectively; this is reported as a contract gap.

All probes report engine `OLAP Server`, identity
`investigator-reader@skynwhy.com`, object
`3484a2bc-98c5-4cef-be5c-a6215484075e`, bound to the VALUE_QUERY. Declared
connection is `149f8d99-1c66-4a0a-9624-759be002bb60`, UNATTESTED.
Each attestation is PARTIAL, with engine/identity/object ATTESTED and no
contradiction. These are WITHIN_LAYER_CHECK comparisons, not independent lower
reads or snapshot-verified results. Per-probe receipt identities follow:

### R4 `46826851-6d68-4f25-a894-243c9e61f8f5`

| Read receipt | Quantity | Native cell address | Attestation |
| --- | ---: | --- | --- |
| `73c79b0a-0c75-4113-b8c6-a172731c8e3c` | 8765 | `676f93893c17ba42fa2e5d05bd89c671ef7a3f615c58f59df6b9f646188342e6` | PARTIAL; engine/identity/object match; connection unattested |
| `f36020d7-ee2b-4585-b201-b846ec130871` | 8765 | **MISSING — shared baseline** | PARTIAL; engine/identity/object match; connection unattested |
| `173bb128-9e29-4665-8ffe-1cf35902c9b8` | 92 | `1c94ef3abb68f28cd7723d6928e73e6beafc7382d9de1d7633ecb353f5191f45` | PARTIAL; engine/identity/object match; connection unattested |
| `466f7f61-98f0-4e7b-ae8e-20f812ab9d32` | 16 | `68005673deb755335aec10d34c484b89530a95e36b2de4332473b622cbdf21f3` | PARTIAL; engine/identity/object match; connection unattested |

All original-receipt and inventory validations passed. Each of the three candidates has undeclared-context value 8,765; declared values are 8,765 / 92 / 16.

#### business output, verbatim

```text
You asked: In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate reports Handled Quantity as exactly 16. I selected warehouse North. Check whether the saved declared report context reproduces this figure and explain what remains unknown about my selections.
Answer to your question: Yes — the saved declared context reproduces the reported figure.

The answering visual "Handled Quantity - extra visual predicate" produced 16.
The applied selections were event day: 2026-09-15; movement type: RECEIPT; product name: Component 1; warehouse name: North.
These saved restrictions reproduce the reported figure of 16; this explains its reproduction by declared report design, not whether that design is intended.
The same calculation without applying report declarations returned 8,765; this is not an unrestricted total.
Adding the event day restriction takes 92 to 16.
Other visual "Handled Quantity - page and slicers" produced 92.
Other visual "Handled Quantity - unfiltered" produced 8,765.
Assumed: viewer-changeable selections at their saved defaults; their current positions were not established.
An invoked bookmark or stored alternative was not established.
Active user selections, row-level security and a difference further back remain unestablished.
The checks are not tied to a shared data version; they do not establish currency or business correctness.
Recommended action: If the saved restrictions (event day: 2026-09-15; movement type: RECEIPT; product name: Component 1; warehouse name: North) are unintended, request an enhancement to the report selections, not a change to the data.
```

#### technical output, verbatim

```text
You asked: In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate reports Handled Quantity as exactly 16. I selected warehouse North. Check whether the saved declared report context reproduces this figure and explain what remains unknown about my selections.
Answer to your question: Yes — the saved declared context reproduces the reported figure.

What else was checked: the vertical walk stopped during process walk.
Reason: TOOL_UNAVAILABLE.

Completed within-layer cells:
Cell fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995/part/definition%2Fpages%2F8b067ecb975e5af7a39b%2Fvisuals%2Fa32b6a48db655ac8a4f2%2Fvisual.json (UNGROUPED): WITHIN_LAYER_CHECK (declared-reproduction-68005673deb755335aec10d34c484b89530a95e36b2de4332473b622cbdf21f3): undeclared-context value 8765; declared-context value 16. The declared selections reproduce the reported figure of 16; they account for that figure without requiring a difference further back. The stated report declares a restriction carrying North; resolution EVIDENCE.
Adding the event day restriction takes 92 to 16.
Other Handled Quantity - page and slicers (UNGROUPED, receipt declared-reproduction-1c94ef3abb68f28cd7723d6928e73e6beafc7382d9de1d7633ecb353f5191f45): declared-context value 92; undeclared-context value 8,765.
Other Handled Quantity - unfiltered (UNGROUPED, receipt declared-reproduction-676f93893c17ba42fa2e5d05bd89c671ef7a3f615c58f59df6b9f646188342e6): declared-context value 8,765; undeclared-context value 8,765.
Limits:
- Assumed: viewer-changeable selections at their saved defaults; their current positions were not established.
- An invoked bookmark or stored alternative was not established.
- Active user selections, row-level security and a difference further back remain unestablished.
- The checks are not tied to a shared data version; they do not establish currency or business correctness.
Recommended action: If the saved restrictions (event day: 2026-09-15; movement type: RECEIPT; product name: Component 1; warehouse name: North) are unintended, request an enhancement to the report selections, not a change to the data.
```

### R5 `3469a7bb-5b21-4385-81e0-db0e792d5a1b`

| Read receipt | Quantity | Native cell address | Attestation |
| --- | ---: | --- | --- |
| `cfc3246b-e588-4666-903f-5bfbb86a5039` | 8765 | `676f93893c17ba42fa2e5d05bd89c671ef7a3f615c58f59df6b9f646188342e6` | PARTIAL; engine/identity/object match; connection unattested |
| `d83e2ae2-a925-4104-90f2-c71145fbdf68` | 8765 | **MISSING — shared baseline** | PARTIAL; engine/identity/object match; connection unattested |
| `43a9f261-1d48-46c0-9776-4000d5000883` | 92 | `1c94ef3abb68f28cd7723d6928e73e6beafc7382d9de1d7633ecb353f5191f45` | PARTIAL; engine/identity/object match; connection unattested |
| `0a9562d0-8315-4c64-a934-459357d9330d` | 16 | `68005673deb755335aec10d34c484b89530a95e36b2de4332473b622cbdf21f3` | PARTIAL; engine/identity/object match; connection unattested |

All original-receipt and inventory validations passed. Each of the three candidates has undeclared-context value 8,765; declared values are 8,765 / 92 / 16.

#### business output, verbatim

```text
You asked: In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate reports Handled Quantity as exactly 17. I selected warehouse North. Check whether the saved declared report context reproduces this figure and explain what remains unknown about my selections.
Answer to your question: No — the saved declared context does not reproduce the reported figure.

The answering visual "Handled Quantity - extra visual predicate" produced 16.
The applied selections were event day: 2026-09-15; movement type: RECEIPT; product name: Component 1; warehouse name: North.
This is not the reported figure of 17.
The same calculation without applying report declarations returned 8,765; this is not an unrestricted total.
Adding the event day restriction takes 92 to 16.
Other visual "Handled Quantity - page and slicers" produced 92.
Other visual "Handled Quantity - unfiltered" produced 8,765.
A moved slicer, an invoked bookmark, user selection, row-level security or a genuine difference further back remains possible; none was excluded.
The checks are not tied to a shared data version; they do not establish currency or business correctness.
Recommended action: Supply the current slicer positions, invoked bookmark, other selections and viewing account to narrow the remaining possibilities.
```

#### technical output, verbatim

```text
You asked: In Declared predicate fixture 20261001, on Saved predicate selections, the card Handled Quantity - extra visual predicate reports Handled Quantity as exactly 17. I selected warehouse North. Check whether the saved declared report context reproduces this figure and explain what remains unknown about my selections.
Answer to your question: No — the saved declared context does not reproduce the reported figure.

What else was checked: the vertical walk stopped during process walk.
Reason: TOOL_UNAVAILABLE.

Completed within-layer cells:
Cell fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995/part/definition%2Fpages%2F8b067ecb975e5af7a39b%2Fvisuals%2Fa32b6a48db655ac8a4f2%2Fvisual.json (UNGROUPED): WITHIN_LAYER_CHECK (declared-reproduction-68005673deb755335aec10d34c484b89530a95e36b2de4332473b622cbdf21f3): undeclared-context value 8765; declared-context value 16. The declared selections do not reproduce the reported figure of 17. The stated report declares a restriction carrying North; resolution EVIDENCE.
Adding the event day restriction takes 92 to 16.
Other Handled Quantity - page and slicers (UNGROUPED, receipt declared-reproduction-1c94ef3abb68f28cd7723d6928e73e6beafc7382d9de1d7633ecb353f5191f45): declared-context value 92; undeclared-context value 8,765.
Other Handled Quantity - unfiltered (UNGROUPED, receipt declared-reproduction-676f93893c17ba42fa2e5d05bd89c671ef7a3f615c58f59df6b9f646188342e6): declared-context value 8,765; undeclared-context value 8,765.
Limits:
- A moved slicer, an invoked bookmark, user selection, row-level security or a genuine difference further back remains possible; none was excluded.
- The checks are not tied to a shared data version; they do not establish currency or business correctness.
Recommended action: Supply the current slicer positions, invoked bookmark, other selections and viewing account to narrow the remaining possibilities.
```

## What this establishes and what remains

The capability executed against retained, collected estate predicates for an
empty fixture-authored figure (earlier) and a numeric fixture-authored figure
(now). It is not verified against a real user-reported number or a new unfamiliar
domain. Saved defaults, bookmark invocation, active user selections, RLS,
snapshot alignment, business correctness and lower-layer equivalence remain
unestablished. Both outputs qualify defaults; neither calls the match confirmed.
The non-match names moved slicer first and recommends supplying selections.
The shared-baseline address gap and the unresolved process ValueError remain.
The filtered lower refusal was not changed, but is not established as this run's cause.
No fixes, fresh freeze, new domain, replacement attempt or fixture-data change.
Stop after these runs as requested.

## Dated correction to the live progress explanation

2026-10-03: the initial progress update attributed HELD to filtered lower scope.
That attribution is withdrawn. Both actual envelopes have empty filters and
dimensions. The saved STOPPED event says TOOL_UNAVAILABLE and PROCESS_FAILED
retains only ValueError; the runtime discards the exception message and traceback
at adaptive_runtime.run_process's broad exception handler. No precise failing
step, boundary skip reason or support-validator failure can be established from
those records. The generic refusal output says only that the process walk stopped.
It must not be read as a demonstrated filtered-scope limitation or a cap refusal.
Each run reached exactly cap four; no cap was raised and no replacement was run.
No cross-surface comparison or vertical classification was retained. Fixing error
provenance or tracing the actual failure is separate work, not a change in this PR.
