# Round Fifteen owner portal trial

2026-10-11. Original family A, once, through the isolated portal. This is an agent-operated demonstration, not independent owner acceptance.

## Retained identities and accounting

Ticket `e573535d-041c-4cd9-bb7a-4f1c55b46046`; session `4086274e-43de-4daf-851a-24e4d35dcb59`. Frozen engine `1f9914e985b3ec09ea82894a551f071d84314cbcc7afba45b83b8942dd765e3f`, context `387f5991-3744-45dd-b8b7-c833d589c8d2`, context hash `93d367d0dd3b5e0d513c454fde92c8e1877796bfb731b9d6034faef572ccc2cc`, config `f2126c3371793b9e67bc226c360afdc13d0379a0ab0bf9bbe60292b43bd67644`.

The isolated catalog used the SAME shared dollar and physical/daily accounting files. Original records, counter rows and pins remained untouched. No identities, grants, estate objects, deployments or project secrets were created or changed. Four startup reader metadata controls preceded the run across two starts; one recovery startup control followed it (five controls in total). The run recorded 10 physical requests: four diagnostic reads and six guard requests. Diagnostic cap 12; usage 4. Three model calls settled: intake resolution, procedure judgment, mechanism synthesis. The procedure's planner_calls field is 1 and is not the total provider count.

## UI transcript

1. Started the isolated local portal and inspected its displayed report/page choices. Before A admission, four visuals were incorrectly labelled with their page name. No ticket was submitted; those two metadata controls remain recorded. A generic display port projected explicit retained visual titles, preserving lookup aliases.
2. Started the corrected portal. Selected Inventory Health e1b8e1; page Inventory Health; visual Movement Units; comparison The source system / application. Optional source value left blank. Entered the preserved original-family-A description without altering its request.
3. Submitted once. The ticket showed INVESTIGATING, no clarifying question. Its selected-facts panel retained the correct visual identity but displayed the combined lookup alias Inventory Health / Movement Units; this residual display defect is recorded.
4. Watched definition tracing and four investigation checks complete. Automatic completion had already started synthesis. Selecting Prepare findings from completed checks once raced that completion: the automatic finish tape succeeded, while the manual finish tape sealed a Conflict. No second synthesis was performed. Retained synthesis status is COMPLETED; ticket state FINDINGS_SHARED. The portal did not refresh automatically after composition.
5. Clicking Open ticket performed full navigation, losing the tab's memory-only ephemeral local access key. Back also required login. No key was extracted from process memory. The closed worker/server was stopped, and a generic in-place link handler was fixed and tested. Recovery starts the normal local portal against the same saved ticket; it is not a replacement investigation.

Screenshots of selections, submission and completed checks were captured through the browser tool. They were displayed in the working conversation; no sealed image file is claimed. Finding/comment inspection and replay status are recorded below when complete.

## Actual finding

TRANSFORMATION_LOGIC, PARTLY_ANSWERED. Values from retained actual path_order: 7,661 at L2 -> 8,765 at L1; 8,765 at L1 -> 8,765 at L0. The retained definition has a left join; actual duplicate matches, aligned snapshots, business intent and the unchecked source hops remain unestablished. No current-source faithfulness or freshness claim is earned.

## Business output, verbatim

```text
You asked: Description supplied by user:
In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.

Comparison selected by user:
The application
Answer to your question: Partly answered.
Regarding the requested comparison: Independent quantities were compared within the checked scope; remaining boundaries, timing and business intent are limited by the recorded evidence.
What the investigation established:

The reported calculation showed 8,765 for movements, matching its declared input. The refined data contained 7,661 for movements; the difference appears between the refined data and the serving data, in the step that matches movements with rates. Several matching rates can cause an entry to contribute more than once. We have not confirmed the repeated matches, whether the checks describe the same moment, whether this matching rule is intended, or how movements were first entered. For the reported calculation and the serving data, the two checks used different calculation engines. For the serving data and the refined data, the checks read different data sources; different calculation engines were not established, so a shared calculation fault could affect both. Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.
```

## Technical output, verbatim

```text
You asked: Description supplied by user:
In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.

Comparison selected by user:
The application
Answer to your question: Partly answered.
Regarding the requested comparison: Independent quantities were compared within the checked scope; remaining boundaries, timing and business intent are limited by the recorded evidence.
What the investigation established:

Measure: Handled Quantity.
Roles reached in path resolution: L0 (SEMANTIC), L1 (SERVING), L2 (REFINED), L3 (LANDING). These labels do not establish successful reads.
B2 diverges: L2 (stock movements e1b8e1 in warehouse silver e1b8e1; role REFINED, upstream input) 7,661 -> L1 (movement values in warehouse gold e1b8e1; role SERVING, downstream output) 8,765.
B1 agrees: L1 (movement values in warehouse gold e1b8e1; role SERVING, upstream input) 8,765 -> L0 (Activity in Warehouse Operations e1b8e1; role SEMANTIC, downstream output) 8,765.
ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison. (receipt boundary-1-comparison).
OBJECT_DISTINCT: comparable quantity-bound object self-reports differ; this verifies a data-path boundary, not engine-level independence. Shared computation faults are not excluded. (receipt boundary-2-comparison).
Declared-context reproduction unavailable: Declared-context reproduction is undeclared for question kind FIGURE_DIFFERENCE.

The retained definition applies a left join between movements and rates on product key before deriving a value column. When more than one rates row matches a movement row, the unchanged quantity column may be repeated across joined rows, which increases the summed quantity across the checked boundary while the later equality is preserved.

Layers:
L0 - Activity in Warehouse Operations e1b8e1; role SEMANTIC: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity
L1 - movement values in warehouse gold e1b8e1; role SERVING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b0ab76f7-20c7-410e-90e4-2c4eb104059a/table/movement_values
L2 - stock movements e1b8e1 in warehouse silver e1b8e1; role REFINED: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/ba24d52c-fcf9-4f1f-a377-f4d38547d887/table/stock_movements_e1b8e1
L3 - stock movements e1b8e1 in warehouse bronze e1b8e1; role LANDING: fabric://149f8d99-1c66-4a0a-9624-759be002bb60/09ba0ef9-7342-4179-a49e-1fc8adf48d82/table/stock_movements_e1b8e1

Limits:
- Unattested connection on L0 (receipt 494d50c0-e6a3-4107-aef9-00e013922bdf).
- Unattested connection on L1 (receipt 7469da98-2106-4394-b04f-5bf07cf28724).
- Unattested connection on L2 (receipt e2d1ccc5-ead3-4d85-a11d-42b2e5357cba).
- SNAPSHOT_UNVERIFIED for B1, B2: the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.
- Checked through L2; stopped because reached.
- The definition shows a mechanism that can cause the difference, but it does not establish that duplicate matches actually occurred for these data, and it does not establish other business rules or a shared snapshot.
- Unchecked L2 -> L3: Investigation terminated before this boundary.
- Unchecked L3 -> unresolved upstream: No declared upstream read for this quantity (literal initialization or derived/unsupported column).
- Quantities trace unchanged integral columns; joins may multiply rows and whole-row deduplication may remove them. Key uniqueness and intended grain are not established.

Recommended action: Ask the responsible business owner whether this behavior is intended; request a change if it is not.

Previous runs: same ticket 022cfcc6-b6db-4a2e-8891-5cba88426995, 08d83cd7-2a49-4948-be61-6ce289a9324b, 0ebb1fd9-1be6-4d80-b5fe-95ffb474a66e, 15128277-242b-4b08-ad18-dad91d6089b3, 288b5c79-de67-483f-835a-7652c66d5da3, 37272838-7954-4a6f-a42e-c2c8f58158ef, 53036702-cc99-4d4f-8c6e-8cdf1d8a9478, 595dd549-aec8-4979-9faa-bdb739d97d57, 5cd46575-ea32-4b95-98b2-c6172dbc4523, 6a89e98b-1b6b-4c6f-80d2-c493ecb9a09a, 77ffd137-8061-4372-b323-5ee71a521b47, 964c94e9-3daa-4aac-a3e0-9a7351d1e1e3, 9a0cda78-6fb0-43f4-a744-d2d6fca63697, 9b7330e0-bf1a-4447-8739-e1a2c5b9516f, a8b69c12-db94-41c6-a85c-e81d9e43f3a4, ae42f998-2b2c-4832-9d05-f90cb7b7c233, bc32732d-4fba-46ae-9763-4522a1b3cda4, be3a2e07-66dd-49b6-b07b-4cdf29a83aa4, be6bdff8-7cdc-4132-ba1e-28507307e361, cd5c63de-b100-4f44-8a33-eddf12262935, d240c4a6-c34f-4765-9a8d-e7647e8cc0f1, e938f3eb-a853-4e51-b775-836a66e8a7b4, f64d90cd-0573-43c9-8a2a-a6cdce7fff86.
```

## Saved comment and agreement

The normal restart used a new ephemeral loopback session key, with no estate identity/secret change. The existing A ticket was opened from Recent tickets; no replacement was submitted. Both actual explanations were inspected. One comment was saved:

> Agent-operated demo check: I can read both explanations. The comparison is partly answered, with 7,661 and 8,765, and the unchecked source and timing limits remain explicit. This is UI verification, not owner approval of the business rule.

The agreement control was clicked once; a saved-ticket refresh visibly showed CLOSED and You: CLOSED. This exercises the USER-labelled demo workflow only. It does not stand in for an independent owner agreeing with the business conclusion. The original admission, read stage, judgment/composition, comment and close captures are preserved.

A recovery idle-worker traceback is retained verbatim: `sqlite3.OperationalError: database is locked`, at `workspace.run_session_once` -> `ModelStore.connect` context exit -> `budget_replay_transaction.commit`. It did not change A's completed result. The shared snapshot materialization path is being tested for lock lifetime; no caps, counters or guards were bypassed. The server was stopped after the ticket and both controls sealed; no demo worker remains alive.

## Screenshot evidence limitation

Browser screenshots show selections, submission/check progress, the actual business paragraph, technical comparison spine, and saved comment. The supported browser API returns the screenshot bytes to the tool conversation but provides no documented save-to-local-file method. No durable PNG artifact or screenshot checksum is claimed. The same visible facts are transcribed above and backed by the sealed operation tapes; screenshot publication remains limited to the working conversation.

## Owned usage and shared windows

Demo-owned total: 15 physical requests (4 diagnosis + 6 guards + 5 metadata controls), 3 model calls, 26,927 bounded input characters, 8,591 actual input tokens and 1,131 actual output tokens. Cost rows cost-1901 through cost-1903 settle to $0.038444 under the configured rate-card guard. Every demo-owned reservation is SETTLED. Comment and close produced zero estate reads/model calls. The intake and two composition calls are not counted as three investigation-planner calls: the retained procedure planner_calls is one.

At 2026-10-11 23:28:33 UTC, shared pot usage was 2,641/4,000; restoration 95 untouched; ordinary rolling usage 1,054/3,000. Shared daily model usage: 1,776/2,000 calls, 73,217,431/80,000,000 input characters, 1,486,283/20,000,000 charged output tokens. Shared guarded dollar charge: $87.742354/$190, with the $10 margin preserved. A different root control reservation was still open; it was not owned or altered by the demo. These are time-labelled shared snapshots, not costs attributed by subtracting concurrent windows.

The closed bootstrap files were compressed only after sealing, with before/after SHA-256 equality. The sealed-run compression restored free space from 10,324,647,936 to 11,858,485,248 bytes, zero estate/model calls. The earlier closed-preflight compression similarly retained hashes. Replay clones are compressed and hash-checked sequentially to preserve the 10-GiB admission floor. Replay progress is reported separately; sealing alone is not a replay-pass claim.
