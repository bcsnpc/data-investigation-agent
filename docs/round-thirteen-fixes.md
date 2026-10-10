# Round Thirteen — fix phase in progress

2026-10-10. Starting commit `1db7526`; draft #423 stays draft. No oracle,
golden, held-out split, sealed expectation, identity or permission is changed.
Engine edits invalidate the earlier freeze.

## Controls and dollars

The owner authorized a $100 round-wide model-spend ceiling and a cumulative
estate pot of 2,500, reason “final live testing before credits expire”. Both
fixture manifests now declare 2,500 instead of 1,500. Rolling remains 3,000;
investigation diagnostics remain 12. The configured restoration allocation is
100; five restoration requests were already used, leaving the recorded 95.
It was not reduced. Model concurrency is four instead of one, as required for
the initial parallel batch. Daily model call/token allowances remain unchanged.
Before-images and grant records are retained privately and counts/hashes are
appended to `docs/runs/ledger.jsonl`.

`model_spend.py` admits every configured provider request against one SQLite
dollar ledger shared by all round processes and catalogs. Admission reserves
an upper bound before transport; successful usage settles once, and missing
usage keeps the bound. It does not refund failed requests or permit another
process to change the ceiling. Three synthetic tests pass, including 80
concurrent attempts. A separate 80-call fake-usage test confirms the existing
governor commits exactly 80 planner and 80 physical requests with no active
reservation left behind. No estate or real model calls were used by these tests.

Dollar accounting is a **public rate-card estimate**, not Azure invoice
attestation: GPT-5.4 Global Standard input $2.50/M, output $15/M; over 272K input,
$5/M and $22.50/M. Cached input is conservatively charged as ordinary input.
Source: [Microsoft Foundry March 2026 rate table](https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-mar-2026/).
The guard includes schemas/instructions and bounds input with UTF-8 bytes plus
framing capacity. Image requests refuse until their cost bound is established.
Zero real model calls so far: charged estimate $0. Estate pot remains 1,254;
rolling last recorded 241/3,000. A live counter check is required before reads.

The first preparation attempt stopped on an incorrect assertion that the
configured reserve was 95; the before-image showed 100 configured and 95
remaining. No manifest was changed by that failed attempt. The correction
preserves the 100 allocation and does not invent a new restoration allowance.

## Causes and changes under verification

- Both I overclaims: the selected application comparator was treated as an
  additional technical ask and promoted an unresolved business-meaning question
  to partly answered. Coverage now preserves a primary business-only ask as
  not answered; explicitly mixed asks retain separate subject coverage.
  Delivery revalidates both rendered question accounts before sharing.
  Eighty-two focused tests passed; preserved I output accounts now fail the
  new guard rather than being silently upgraded.
- Both C delivery exceptions: the registered-refusal delivery fix was already
  present at the starting commit. Offline checks against both preserved failed
  states confirm it delivers HELD without inventing an assessment. No duplicate
  repair and no replacement historical run.
- B/H attribution: their source bindings were actually resolved. Ratio and
  filtered expressions lack faithful lower-quantity compilation. The adapter
  now names unsupported compilation, preserving the refusal; 30 lower-read and
  depth tests passed. The sealed expectation remains fixed. This is not a claim
  that the missing capability was implemented.
- Rebuilt early stops: VERIFIED inferred profiles belong to older model
  contexts. Current-context mismatch correctly bars reuse. Context identity is
  not removed from the gate. Current-context verification and prevention of
  unnecessary context churn are being examined separately.
- Questionnaire: seven not-measurable cases lost the measure-only route; the
  three lost complete settlements concern keyed matrix addresses and request
  routing. The number 149 was extracted successfully. A number field would not
  fix those causes. Shared optional measure-only routing, conservative explicit
  cell-address reconstruction and declared-context routing are being tested.

## DECIDED WITHOUT REVIEW

Do not add “The number you see”: none of the twelve not-measurable records was
caused by its absence, and the one numeric matrix failure had already extracted
149 exactly. Restore the genuinely lost subject/cell paths instead. Rejected
adding a field because it would leave the evidenced defects intact.

Keep truthful `USER_SUPPLIED_FORM` authority instead of relabelling it `STATED`
to pass a text-derived acceptance contract. The expected contract and its
provenance remain fixed; any acceptance mismatch is reported separately from
outcome correctness. Field-presence alignment may be fixed where it loses no
evidence, but missing boundaries cannot be formatted into a pass.

## Pending report points

Fresh dev scores, full regression, fixture three-repeat table, billing/chat,
scenario matrix, offline capture/replay and the recorded demo remain pending.
No Round Thirteen live correctness, stability, billing or replay pass is claimed.

## Fresh dev and parallel accounting checkpoint

Fresh scores are in round-thirteen-dev-results.md. Original46 attempts remain unchanged. Unique named-matrix addressing and intrinsic saved-context reproduction now share the existing selected-target path; unknown visual qualifiers remain refused. Affected fresh follow-up is pending.

Workspace admission counts active owners atomically and bounds them by the manifest, preserving one active operation per owner. Provider429 retries receive distinct reservations, sidecars and events, obeying the original owner deadline and call bounds. Tapev6 records these controls; v1 through v5 remain supported unchanged. Concurrent spend rows allocate private ledger identities atomically. Initial full2903 failed vocabulary and identity ratchets; pricing moved into the adapter and unrecorded identity was removed without relaxing either ratchet. Recording tests on dirty source correctly refused; committed-source validation follows.
