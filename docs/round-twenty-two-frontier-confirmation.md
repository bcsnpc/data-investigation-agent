# Owner frontier steer: confirmation, 2026-10-23

The one requested family A validation completed on source `8611703879fce5d1bfde3f5c6ec42ff4e74d5805`, tested image `sha256:9ecb3fec02272639b1c6d8e27deea36babb057e8d08932e6110430465ddff935`. Azure execution `job-dia-worker-6u1avrg` succeeded. It reached **as designed**, backed by native **TRANSFORMATION_LOGIC**: the measured model/Gold value was 8,765 and Silver/Bronze was 7,661. Provider calls fell from **18 to 4**. The earlier unsuccessful result remains unchanged.

Successful exact calls are retained in the case file. Repeats return that result locally, log reuse, and tell the model "Already have this as evidence" with the original evidence IDs. A final regression also checks repeated raw-evidence retrieval: its full body remains in the evidence store and case file, but duplicate feedback contains only the reference, never the body again.

After a rejected verdict, code chooses the first unmeasured boundary, then an unchecked explanation hypothesis. Each continuation exposes only its selected tool. Three exploratory steps without measurement/proof progress transfer control to this frontier; a continuation without progress advances. Exhaustion returns not found with the furthest measured point. Existing evidence validation still decides whether a finding is supported.

Six frontier tests cover successful repeats, repeated raw retrieval, rejected verdict recovery, phase exhaustion, immutable saved results and older case-file readability. Together with the core investigator and cloud assembly tests, **64 tests pass**. The initial focused command used the wrong import root and a nonexistent module name; the corrected command supplies `scripts` on `sys.path` and all 64 pass. That invocation error is not an engine failure.

The live A run exercised the phase-limit continuation; it had no duplicate or blocked calls. Duplicate suppression and rejected-verdict recovery are covered by tests, not claimed as live observations in that run. Azure duration was **278 seconds**, so the full-investigation target below 120 seconds remains missed. This was an unscored harness validation, not a dev or held-out result. Full outputs and sealed receipt: [family A receipt](runs/round-twenty-two-frontier-family-a.json).

Subsequent pre-score admission/control source `9c770d322f2e34368d2a1c076c2bac0ad9fd6388` passed **5,168 tests**, 48 skipped, zero failures/errors, in 643.25 seconds. All eight hosted image shards and publication passed in workflow `40004822471`; tested image `sha256:50739b407a9a73017099ccca02ff0981cc7b88d4503213ea15e29c3f3d9e0b5e`. That full result predates the final short duplicate-feedback change; the 64 focused tests include it. No scored dev admission has occurred.

Engine changes invalidate the previous freeze. No new run or ledger row was created for these offline tests.
