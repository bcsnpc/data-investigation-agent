# Round Sixteen Part C: bounded claim checks

2026-10-12. The new confirmed-claim API and UI can execute deterministic checks using the existing readers, read guards, physical-request accounting and immutable tapes. These checks establish observations; they do not promote a difference into a business defect or a causal explanation. Whole-estate scoring remains subject to Part D's readiness gate.

## Implemented scope

| Requested check | Implemented | Remaining limit |
|---|---|---|
| Missing or extra records | Per-example presence and counts across an explicitly declared direct Copy chain; independent first-change history for every supplied key | At most six exact integral example keys; unknown extra keys, transformed paths and causal inspection are not implemented here |
| Multiplicity | Total rows, distinct nonblank declared keys, blank-key rows, repeated-key rows, and optional example counts at each admitted layer | Equal counts do not establish equal membership; the declared key's business meaning and whether repetition is erroneous remain unproved |
| Record value | Exact typed field value where one unique record exists, with blank, absence, duplicate ambiguity and failed reads distinct | Only faithfully mapped physical fields on the direct Copy chain; no arbitrary aggregate is substituted for a duplicated record |
| Decomposition | Bounded direct additive totals by a declared integral dimension, with group counts and explicit saturation refusal | Date grouping and translated dimensions across transformations remain unsupported |
| Page consistency | Retained scalar visuals, each accounted for; comparisons require the same measure and compiled declared restrictions | Grouped cells need an explicit address; screenshot filters are not yet compiled; no claim about the rendered browser state |
| Page freshness | Successful refresh/load timestamps from the existing optional metadata and declared audit/history ports, with provenance | Missing timestamps stay unknown; retained history is not proof of the latest actual load and no lateness deadline is invented |

The former intake and investigation routes remain available. The new claim controller refuses an unsupported legacy admission rather than substituting a page comparison for a definition, business-rule or filter-context question. The new controller's COMPLETED label means its bounded observation checks completed, not that a causal ending was earned.

## Consumer checks

The controller loads the retained confirmation and revalidates its interpretation against current catalog identities. Clients cannot send a query or choose a route at the execution endpoint. Once-only request keys return the retained execution instead of repeating reads. The ordinary session admission supplies the unchanged diagnostic cap of 12 and wall deadline.

An independently compiled request must match each original sealed receipt, including the addressed keys, field, mapping, scope, query and expected surface. A producer's positive flag or a valid seal for a different query is insufficient. Every missing preceding layer prevents a first-change claim. One key's earlier change cannot hide another key's later first change. Empty paths and disconnected observations cannot establish agreement.

Both explanations are engine-rendered from the confirmed request and checked facts. They include values and layer roles, missing work, receipts in the technical explanation, and the snapshot limitation. There is no model composition call. Difference alone never becomes a defect claim. Original guarded failure details and read receipts remain retained even if execution or rendering fails.

Tape version 14 adds confirmed-claim execution and requires both explanations for completed, partial and held returns. Version 13 continues to replay claim intake under its own contract. Provider and estate evidence bytes are unchanged.

## DECIDED WITHOUT REVIEW

- Reused the proven declared Copy/key admission for new record projections. Extending it by assuming a transformed or filtered equivalence was rejected; those requests refuse explicitly.
- Kept new checks observational until a causal proof exists. Automatically selecting one of the requested causal endings from a numeric difference was rejected.
- The smoke uses three fixture-authored typed claims, not independent tester tickets or model-intake accuracy evidence. This separates execution-path verification from Part B's unresolved extraction accuracy.
- Housekeeping normally waits until part close. Closed capture databases may be compressed before the next admission only to preserve the unchanged 10 GiB floor; logical hashes are checked, originals are not deleted, and shared live ledgers are not compressed.

Validation, the once-only smoke, replay and accounting are appended below when the part closes. Draft #423 remains open; prior freeze invalid.

## Live smoke and offline corrections

The three once-only smoke inputs completed within the original 15-minute batch: page consistency HELD on 92 versus16 under different restrictions; global multiplicity observed360 rows and360 distinct nonblank keys at all three layers; record1 had units16 at all three layers. These are fixture-authored typed claims, not independent tester accuracy evidence. The [live report](round-sixteen-c-live-smoke.md) preserves both outputs, receipt IDs, original null HELD reason and tape seals.

22 physical requests comprised8 diagnostic,12 permission/identity overhead and2 pre-warm controls. Pot2742->2764/4000,reserve95; rolling601->618/3000. Model calls0. Source7f101b4 full regression passed3,659 tests. The smoke exposed missing recommended actions, missing page receipt-specific connection limits, and a null HELD reason; the generic renderer correction passes36 focused tests without changing original evidence.

An archived intake replay exposed request-key-order dependence: canonical JSON reordered submitted fields while the producer emitted facts in dictionary insertion order. Current construction now iterates canonical field order. A24-permutation test requires byte-identical facts, and a full synthetic claim submit/confirm tape test replays a canonicalized request. All34 intake/tape tests passed. The original live tape remains unchanged and is not retrospectively called replay-green. No expected fact/value is weakened or reordered to mask the difference.
