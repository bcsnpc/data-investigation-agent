# Rendered synthesis spine

Dated implementation, 2026-10-03 America/Chicago. Prior freeze invalidated.

PR #320 merged as 1682a28 after six green checks, preserving all three failed deliveries. R1 was HELD with a process ValueError and cell-identity synthesis failure; R2/R3 had valid original evidence but oversized provider views. This change does not reclassify those runs.

Synthesis validates original sealed receipts and inventories locally. The model receives only citation IDs and a deterministic per-candidate spine: restrictions, values, reported state/precision, comparison grade, attestation summary, resolution kinds, declaration counts and engine-owned qualifications/open set. Raw query text, raw self-report columns, full declaration payloads and inventories never enter the Azure narrative call. Complete local rendering remains separate from the provider view and original-evidence validation remains unchanged.

R2's preserved local digest remains 90,146 characters. Its provider spine becomes **13,083 characters**, with all three candidates and eighteen citation identities retained, no elisions, against the unchanged 48,000 bound. This is a read-only size calculation, not a synthesis run or ledger event. No provider or estate call occurred.

Oversize spines elide whole named display units. If any provider content is elided, the engine renders both outputs from the complete supported local assessment without a model call and explicitly names the omitted provider content. No evidence is silently truncated, no eligibility gate weakened, no conclusion manufactured from an unfinished run, and no input bound raised. Validation failures still refuse: this fixes provider-view size, not invalid evidence.

## Semantic surface attestation ceiling

The current reader's semantic value statements report engine, identity and model object; connection cannot be self-reported through the tested route. DISCOVER_SESSIONS was refused in #300. PARTIAL with those three matching fields is therefore this reader/surface's tested ceiling, not a permission gap to chase. It suffices for qualified same-route within-layer checks. Under #302, a comparable quantity-bound engine difference establishes the stronger independence grade; an object-only difference is weaker. Connection omission and unverified snapshots remain named. This does not upgrade any historical receipt or claim full coverage.

Validation: three new spine tests cover ten candidates with ten restrictions each well below the bound, raw-evidence exclusion with unchanged originals, and named bounded elision. Thirty-three existing synthesis tests passed. Full CI tracks the PR. No investigation, offline synthesis, new ledger row, policy/config/cap/credit/fixture/grant change. Cell/read addressing is the next separate PR; only then may the three preserved attempts be re-synthesised offline.
