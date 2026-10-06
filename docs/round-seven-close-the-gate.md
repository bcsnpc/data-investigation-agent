# Round Seven: close the two-column gate

Started 2026-10-05 America/Chicago (2026-10-06 UTC). This is known-domain
regression work, not a freeze or unfamiliar-domain acceptance claim. PR #410
remains draft until the requested evidence and hosted gate are earned.

## Budget and approvals

Round Six closed at **338/400 physical requests**, with its original records
unchanged. Round Seven has a separate **300-request pot, 60 reserved**, starting
at epoch `1791259533.388716`. Ordinary work stops before spending the reserve.
The rolling allowance remains 1,500; investigation diagnostics remain 12 per run.
Opening rolling usage was 374. Pre-warm connections and resume waits are controls,
not investigation diagnostic reads. Restoration is earmarked for six hours under
`round-seven-reserved-restoration-20261006`; no counters are reset or refunded.

The old manifest digest is
`908df87f1b066c11605b8381f3c7a5b3cdbd6482dde820f87c03bb3beed87f56`.
The separate Round Seven reachable manifest digest is
`d433f1b7b5ede9e8eb2d5343a7e960efbfedc23fbe64eff722daa95aff57da88`;
whole effective configuration digest
`8f692397ec49849388d2abbb445577bc207427101201d714786e9fa3015a067e`.
The unreachable manifest digest is
`e4ef23417aa3669794fb502891ba18b2b43445642e12db7e108ecfbc9307ad8a`;
whole effective configuration digest
`c5885fe61a9eed36bf14b814762f9d9122f96efc68e630e6003b1bb9851a55f4`.

The unreachable-policy approval is `e2789dad-ee71-4d41-b7ad-6b667c35cba7`,
hash `c6d6c82187a5f84badbc5cdb8bcb36aec42b8af8ffd091e34d280204b750070d`.
It explicitly reuses retained metadata; zero metadata requests were made and no
new data-currency claim follows. Existing bounded binding proofs were revalidated
under each new manifest hash, not re-measured. Both cases use the explicitly
approved retained application-model context `d48aa1d0-f692-44ed-969c-083c6d3df49f`,
hash `e284a33adec25f6aeb592adca76b88ed30f48e4596ef7dacd7f70cb99d0c05a0`.
All original manifests, tapes, outputs and ledger rows remain intact.

## DECIDED WITHOUT REVIEW

- “Run F once” is interpreted as the named archived **source-unreachable**
  case and its unchanged ticket, rather than original inventory family F.
  The latter cannot exercise the requested application reachability ceiling.
- A changed budget/reachability declaration receives a new whole-configuration
  approval using unchanged retained metadata, rather than silently narrowing
  the policy hash or recollecting metadata that this change does not affect.
- The existing bounded proofs are reused only after consumer revalidation.
  This is not a new live verification or proof of global equivalence.

## Preserved Round Six setup failure

`ModuleNotFoundError: fabric_cli` occurred in the operator's **fixture-control
pipeline-launch environment**, before any pipeline API request. It was not an
intake, recorder or investigation-runner failure. The first authored application
append was restored immediately; the failed control remains preserved. The fix
added the already installed `.local/fabric-cli-env/Lib/site-packages` to that
control script's import path before resuming the remaining setup. Round Seven
uses that existing path from the outset, without changing identities or engine
code.

## Once-only live results

| Case / session | Outcome | Pot before → after | Physical | Diagnostics / cap | Guards / reuse | Intake / investigation / synthesis |
| --- | --- | --- | --- | --- | --- | --- |
| source-unreachable / `8675f5c6-9dd9-44c2-86f8-65ce4cdc30eb` | CONSISTENT_TO_BOUNDARY | 0 → 16 | 16 | 7 / 12 | 7 / 2 | 1 / 0 / 1 |
| source-latency / `854270fd-5b11-402b-addc-efe1a689e053` | LOAD_LATENCY | 20 → 45 | 25 | 10 / 12 | 13 / 8 | 1 / 0 / 1 |

Both completed, synthesized, validated and matched their existing acceptance
contracts on their first attempt. Each sealed tape also replayed successfully
with sockets forbidden; replay adds zero estate reads. Complete original probe
attestations and boundary observations are retained in the public evidence
views, which are not substitutes for validator inputs:
[unreachable evidence](runs/round-seven-source-unreachable-evidence.json) and
[latency evidence](runs/round-seven-source-latency-evidence.json).
Verbatim outputs:
[unreachable business](runs/round-seven-source-unreachable-business_output.txt),
[unreachable technical](runs/round-seven-source-unreachable-technical_output.txt),
[latency business](runs/round-seven-source-latency-business_output.txt),
[latency technical](runs/round-seven-source-latency-technical_output.txt).

The unreachable run compared semantic 7,661 with landing 7,661, using different
quantity-bound engine reports. It checked record 900099 absent at those two
layers, did not read the application, and cited the successful load ending
2026-10-06T03:33:21.8711186Z with its own 360/360 counters. The configuration
ceiling is named as a limitation, not an ingestion or latency finding.

Reachability was restored with retained-policy approval
`063087a0-39e6-4630-874d-c957a17336d6`, hash
`79944d52b889ce5f013075d42fcfa700f0ec97a966b4e49b7c03abc8529162e2`,
pinning the reachable whole-config hash above. No data mutation occurred for
that case; the false/true approval pair is preserved separately.

For latency, independent authored arithmetic is **7,661 + 17 = 7,678**.
The exact isolated application append was movement 900001, warehouse 1,
product 1, 17 units, day 2026-10-04, type RECEIPT; the server assigned version
40001 and modified time 2026-10-06T04:10:18.8457497Z. The old seed was
360 rows / 7,661 units, becoming 361 / 7,678. The semantic and landing reads
remained 7,661; application read 7,678. The source changed after the recorded
successful 360/360 load, with no later load before the investigation. That
audit mechanism earned LOAD_LATENCY without a definition judge or planner.
Fixture arithmetic and expectations never entered runtime intake or probes.
It could have failed if intake selected another scope, a guarded surface was
unavailable, the source change did not appear to the reader, audit history did
not establish the ordering, or synthesis/replay failed. The independent
derivation did not guarantee these runtime preconditions.

## Restoration and both windows

Pre-warm used two physical control requests (first connect SQL40613, then
success after a five-second recorded wait). Baseline verification and append
used one control request each. Deleting only 900001 used one reserved request,
restoring the source to 360 / 7,661. Restoration pipeline
`37b546ca-863d-45ce-b63b-015d5cdccf61` completed and its own copy activity
reported 360 read / 360 copied. Four pipeline control requests were reserved.
Six subsequent reader probes used fourteen reserved physical requests and
verified **7,661 and record 900099 absent on semantic, landing and application**.
Their statements were copied from the sealed prior baseline compilation;
original requests/receipts were not modified. These are restoration controls,
zero investigation diagnostics, not replacement investigations.

Round Seven is **64/300**: 41 investigation physical requests and 23 controls;
19 of the 60 reserved restoration requests spent, 41 still earmarked.
Rolling ordinary usage was **417/1,500** at the restoration checkpoint (window
expiration explains changes from the earlier peak; no counters were reset).
Investigation diagnostics totaled 17; each run remained below 12.
Every comparison remains SNAPSHOT_UNVERIFIED; neither agreement nor these
bounded witnesses establishes currency or global equivalence.

The complete archived and inferred fifteen-case regrades are in progress.
The two-column hosted gate is not yet earned; #410 and the gate PR remain draft.
