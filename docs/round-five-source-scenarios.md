# Round Five independently authored source scenarios

These are fixture tickets, not real user observations or unfamiliar-domain
acceptance. The seeded notebook's 360 literal rows sum to 7,661: warehouse
groups 2,629 + 2,948 + 2,084. Record 900099 is absent. Arithmetic was computed
from those literals, independently of compiled engine queries. No expected
answer was obtained by transcribing an engine read.

| Scenario | Independent state | Actual result | Diagnostic / physical |
| --- | --- | --- | --- |
| Consistent | Source and landing 7,661; expected record absent | CONSISTENT_TO_BOUNDARY: application quantity failed SQL 40613, though membership succeeded | 6 / 13 |
| Latency | Append record 900001, 17 units after the retained successful load; source 7,678, landing 7,661 | LOAD_LATENCY, qualified by missing matching snapshots and endpoint synchronization | 10 / 23 |
| Gap | Append record 900002, 11 units; copy 361 rows, then the authorized fixture step removes that row from landing; source 7,672, landing 7,661 | INGESTION_GAP, qualified by matching-snapshot and synchronization limits | 10 / 23 |
| Unreachable | Restored 7,661; application declared unreachable, record 900099 absent in seed | CONSISTENT_TO_BOUNDARY through landing; application not read | 7 / 14 |

The latency producer read the Warehouse audit's retained successful load ending
2026-10-04T16:48:22.2386045Z, own counts 360 read / 360 written, and independently
read a later application change at 2026-10-04 21:48:44.4619782. The gap producer
read its successful load ending 2026-10-04T23:01:36.9831858Z, own counts 361/361,
and the earlier application change at 2026-10-04 23:00:24.7184471. These are the
load's own accounting, not a recount or estimated delivery counts. The delivery
probe observed one missing source row, zero differing versions in each case.
Counters do not prove row-level delivery or exclude SQL endpoint lag.

For unreachable, the retained successful load ended
2026-10-04T23:19:23.5350123Z with own 360/360 counts. That timestamp was authored
into the acceptance input from the reader's activity output before consulting
the investigation answer. No LOAD_LATENCY or INGESTION_GAP was claimed without
an application read. All source probes, attestation omissions, boundary grades,
snapshot qualifications and both narratives are preserved in the
[transcripts](round-five-output-transcripts.md).

The first gap setup never reached intake: the controller mistook successful
NOTEBOOK_COMPLETED for failure because it expected JOB_COMPLETED. The state was
restored before another fixture setup. The restoration accepted before a local
interruption was polled, not resubmitted. Both controller failures, the first
source-read verification failure and subsequent explicit verification remain in
the ledger. Each investigation ticket itself ran once; no failed investigation
was replaced. No provider, permission, diagnostic cap or fixture expectation was
tuned during a run.

Honesty check: none of the arithmetic guaranteed success. Intake could select a
different scope; reads could fail or lag; attestation could refuse a boundary;
the audit could be incomplete; synthesis or strict replay could fail. The
consistent ticket actually stopped short of its expected source conclusion on
SQL 40613. The gap/latency labels reproduced offline but the original acceptance
checker misidentified their deterministic spine as model prose. These are
separate facts, not a fifteen-ticket acceptance pass.

Final independent reader values after cleanup: application, landing and isolated
model 7,661; original model 8,765. Reachability and approval were restored with
the original configuration digest. Historical receipts were not edited. Prior
freezes remain invalid; this evidence is known-domain only.
