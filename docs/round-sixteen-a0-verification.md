# Round Sixteen A0 - bounded native verification

2026-10-12. The single authorised attempt `round-sixteen-rates-20261012T072116` completed at 07:30:15 UTC. Four actual native verifier results were VERIFIED: the three Silver product_rates columns against Bronze, and the current Gold product_id KEY profile. The old NUMERIC profile remains unchanged. This is bounded sample evidence, not a whole-table or whole-estate completeness claim.

The samples were derived independently from the retained notebook's literal seed metadata: product_id 1 through 8 for rates, movement_id 1 through 360 for the Gold join. Notebook SHA-256: `313e90c9e25e1e1e844aac5383bfb3c01c4bd11684faeaabf48c207c623cf0c1`. No query answer was used to choose a sample or expected result. The existing compiler and verifier generated and evaluated all eight value probes; two reader catalog queries established the target schemas.

The isolated approved model context was `4dee59fc-206d-433c-bb55-e4c6245a235a`; retained enterprise context `e3d3e50b-844a-4f1a-bbe3-d98508d83d72` remained PARTIAL. Source commit `2846c25`, engine fingerprint `aa6064c139dc0527450c66b8e3b1fb2da63dcdcd9b1cd0a2605576b8e4d1efb0`. Existing reader identity, fixture data, grants and investigation cap were unchanged. The run did not publish a profile or activate a new shared model.

Accounting: 10 verification probes out of 11 allowed; zero investigation diagnostics and zero model calls. The worker issued 27 SQL physical requests: ten verification queries, ten per-query identity checks and seven newly established permission guards. Three database guards and four object guards were established, with fourteen explicit reuse events. Authentication used a cached isolated-reader token: zero HTTP requests observed, but the existing conservative metering charged one authentication-control slot. Total ledger charge was therefore 28, below the approved 36 bound. The rolling window after the attempt was 695/3,000. The restoration reserve remained 95; the shared pot advanced by 28, from 2,712 to 2,740 of 4,000.

The operation captured the actual verification objects in its sealed FINAL. Exact offline replay completed MATCHED with zero estate reads and zero model calls, including all returned objects and accounting. Its replay receipt explicitly identifies the input capture SHA and recorded engine hash; no historical proof association was manufactured.

- Exact engine fingerprint: `aa6064c139dc0527450c66b8e3b1fb2da63dcdcd9b1cd0a2605576b8e4d1efb0`.
- Capture SHA-256: `712c9b041f1cce407988f590d655160f8b029ec6f88ca820147ef2a780512ed2`.
- Original result SHA-256: `aeef90d9cabd183964794ad1068fd6d41f3a1dba9bc43746ac4e7210050325c6`.
- Exact replay receipt SHA-256: `ca3b28819549513c860d49ac387d25c6a460b9d2819557d545b3a2e8d88bc5ff`.
- Private evidence directory: `.local/round-sixteen/rates/round-sixteen-rates-20261012T072116/`, including `run-locator.json`, `result.json`, `capture/tape.json` and `exact-replay-result.json`.

The collector baseline copies were audited in memory after releasing the source database handle. This avoided repeating A1's long shared-catalog read lock. No secrets were written into the capture. Query-bound snapshot identity is still unavailable on these surfaces: SNAPSHOT_UNVERIFIED remains, regardless of these bounded reader checks.


Model spend remained USD94.704272 of USD119.704272, with the existing USD10 protected margin. Completed replay and working copies were losslessly archived (1,635,897,482 bytes to 173,345,246 bytes; every member hash checked). Automatic tool policy rejected the guarded removal of those derived originals, so the archive and originals both remain; no reclaimed-space claim is made. Free disk was 11,363,401,728 bytes at 07:36:25 UTC. Original capture members and tapes were never removal targets.

Subsequent safe housekeeping used native NTFS compression on six closed derived SQLite copies, without deleting any file. All six commands returned zero and SHA-256 was identical before and after for every file. Free space became 12341776384 bytes. The ZIP also remains.


The first MATCHED replay receipt did not measure network attempts; the readiness gate correctly refused its missing network field. A separate guarded offline replay was therefore recorded. Its first attempt refused the archived engine fingerprint because Git archive had converted line endings; that failure remains intact. Restoring the exact recorded fingerprint bytes, including native line endings, allowed the second guarded replay to MATCH. Socket connect/connect_ex attempts were denied and counted throughout; the measured count was zero. Native live producers were separately forbidden by the sealed replay helper. No universal operating-system network claim is made. New guarded receipt SHA-256: `0440ad7ddc5c4f569c099e7c00157700ee3b7a982dc41b0db877b0fd32596499`; path `network-guarded-replay-2-result.json`. Original receipts and all sealed tapes remain unchanged.
