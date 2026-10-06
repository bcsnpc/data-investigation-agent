# Round Nine: translation, evals and governance

Started 2026-10-06, America/Chicago, from merged main `c96884c` (#419).
This is an implementation checkpoint, not completion of Round Nine.

## Offline translation checkpoint

The consumer-owned `TranslationProposer` interface accepts a closed proposal:
definition hash, kind, target engine, expression, discovered objects, canonical
grouping and the original run timestamp for relative definitions. It has no
verdict field. Object membership is checked before compilation; the platform
adapter must also resolve every expression reference through its governed compiler.
This module never executes expression text directly.

The verifier compiles both plans before admitting any probe. Filter witnesses
require complete selected key sets, explicit adapter normalization, and a
length-framed binary SHA-256 hash plus count. Typed keys distinguish null, zero,
text and boolean; duplicate keys and truncated sets refuse. A same-surface filter
check requires the same engine/connection/object. Measure witnesses require at
least three distinct retained cell addresses and an independently attested
boundary. Original results, context, addresses and quantity-bound surface
attestation are checked, rather than accepting wrapper annotations.

Equal comparisons produce VERIFIED only for their recorded scope/sample;
unequal comparisons preserve both observations as FALSIFIED. Compilation,
execution or evidence failures remain UNVERIFIED. All remain
SNAPSHOT_UNVERIFIED; sampled agreement does not prove global equivalence.
Probes use the existing approval-verification budget class, not investigation
diagnostics. Physical admission still belongs to the isolated adapter route.

An extra measure cell uses an existing, natively addressed original cell
observation plus one new proposed-side probe. Missing or differently addressed
native evidence refuses; it is never retrospectively rebound. The append-only
translation ledger checks receipt seals and recomputes successful/falsified
verdicts. Cache reuse is definition/context/metadata/scope/time/cell specific;
changes expose STALE without editing history. A later failed reverification
prevents reuse of the earlier successful entry for that cell.

Twenty-four focused tests pass with SQLite in memory and synthetic query-bound
receipts; zero estate/network/provider requests. Independent native definitions
and deliberately wrong candidates cover Top-N, a pinned date window and an
ALL-like measure across three retained cells. These test the verifier and
contract, not the live model's first-proposal quality or a platform adapter.

## Integration finding and remaining work

The existing lineage proof contract (`lineage_binding.verify` and
`binding_sample.verify`) establishes bounded quantity/profile witnesses, not
row-key mapping. The manifest's `lineage.bindings` carries layer IDs and declared
provenance, not a verified column-key map. Treating either as a verified key
binding would promote sampled agreement into unsupported row identity.
The draft therefore keeps cross-boundary filters UNVERIFIED. It does not
declare the new capability or bypass existing UNSUPPORTED restrictions.

Still required for section 1: adapter-governed native/proposed compilation and
result extraction, an explicitly evidenced key-binding contract, recorded model
transport integration, and runtime use/reverification of ledger entries. The
section 1e report is provisional until these integration tests exist. No live
Top-N/date/measure trial has occurred.

Sections 2–7 (golden model-step evals, OTLP converter, governance/retention/
redaction, rebuild plan, bounded live verification and demo command) have not
been implemented in this checkpoint. No fixture, permission, identity, secret,
policy, approval context or acceptance expectation changed.

## DECIDED WITHOUT REVIEW

- Begin with a separate default-unused verification core; do not make the
  investigation consume translations before adapter integration is proved.
  No existing planner payload builder changed, so directory and SQL-object
  coverage and payload characters are unchanged by this checkpoint. Future
  wiring must measure all three and add the standing coverage regression test.
- Do not reuse bounded lineage profiles as key-binding evidence. The alternative
  would falsely certify selected-row equivalence from aggregate agreement.
- Preserve query-bound snapshot requirements and refuse missing extension-cell
  addresses. Standalone metadata or address backfill would weaken prior rulings.
- Round Nine's authorized pot is 200 with 40 reserved and rolling limit 1,500.
  No live admission or credit grant has occurred, so no budget configuration or
  discovery approval has been changed yet. Round Eight's closing rolling usage
  of 363 is historical, not a current measurement.

Engine bytes changed; all prior freezes remain invalid. No unfamiliar-domain,
live translation or general capability acceptance is claimed.

## Validation and budget record

The first full discovery sweep ran 2,076 tests and failed with eleven errors.
Ten were TAPE_UNCOMMITTED_ENGINE and one was Engine or connection changed:
the sweep began while draft engine files were being edited. This is a preserved
failed check, not a regression pass. After committing a stable checkpoint, the
affected tape (28), code-definition (5), repository-code (3) and adaptive (33)
suites passed; proposer tests (11) also passed. The final translation suite
passed all 24 tests, including malformed attestation refusal. These are targeted
reruns, not a claimed clean full 2,081-test sweep.

The initial replay sweep used an absent archived-input directory and reported
MISSING_PRIVATE_REPLAY_INPUTS. Its log and output remain preserved. A corrected
sweep uses `.local/round-five-i-20261005/inputs` and the pinned inferred inputs.
Both sweeps are still running at this checkpoint; no 15-by-2 pass is claimed.
PR #420 remains draft; hosted checks are pending, no merge.

At 2026-10-06T22:53:50Z (5:53 PM Chicago), the existing rolling physical window
is 315/1,500. Natural expiry lowered it from Round Eight's historical 363;
no reset or refund. Round Nine has spent 0/200, with 40 authorized for reserve
but not yet installed as batch credits or round policy. Investigation cap stays
12; diagnostic and provider calls are zero. The existing Round Eight reserve
remains untouched. Failed and successful test records were appended to the ledger.
