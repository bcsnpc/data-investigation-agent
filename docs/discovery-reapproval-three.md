# Discovery re-approval and unchanged-engine trials

Tracking: #193. Authorized by the user on 2026-09-26 local time; execution
receipts use 2026-09-27 UTC. This is known-domain regression, not frozen acceptance.

## What the gate protects

`adaptive_candidates.catalog` compares `model.discovery.policy_hash` with
`digest(config)` before admitting a dynamic/process investigation. That digest
covers the entire **validated, normalized config object**, including resolved
paths. It is not a hash of raw JSON file bytes. Whitespace alone is immaterial.
`Discovery` uses the same digest when collecting and projecting model contexts.
The collector profile must match it; published models and their new immutable
contexts receive that digest. Explicit model denies remain effective.

This gate is a conservative configuration-approval boundary. It prevents an
investigation from treating discovery approved under one connection/identity/
transport configuration as approval for another. It does not inspect a semantic
diff or decide which changes are harmless. It also does not prove query access,
reader identity, quantity equivalence, or conclusion correctness: those checks
remain separate.

The old approval was
`1f1616d4f4d80915ddabc2dabea0638fc881961f9f14c30b90d2c6cdbdb477a0`.
The current validated config is
`19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6`.
`fabric.sql_reader` enables a distinct execution transport; `fabric.xmla_client`
configures failure refinement through another interface. The former is material
to execution, so dismissing this as a harmless stale-file hash would be wrong.
The old approval genuinely predates the current declared transports. This does
not establish that the estate metadata itself changed or that the old metadata
was factually incorrect.

The authorized remedy uses the existing discovery collect/publish path. It does
not rewrite the old policy record, narrow the hash, revert either config section,
or call the adapter around the gate.

## Execution controls

Engine fingerprint:
`a9e32c8192401ba23c353a9c5955312142b8e70725bd832861ce69060a373830`.
The clean worktree at `D:/dia-surface-inventory` has the same engine bytes as
`main` at `24a23be`; its additional parent commit `799f768` preserves the previous
three preview refusals. Older uncommitted changes in the original working tree
are not used. No engine or configuration edits are part of this work.

The new batch preserves the previous G ticket, GPT-5.4 medium profile, 8,000
output allowance, 120-second provider timeout, 48,000 per-call input ceiling,
384,000 cumulative investigation input, six-read limit, 65-second pacing,
recording, synthesis and explicit `--environment unknown-domain-v4`.
Exactly three new attempts are authorized. Previous failures remain unchanged.

## Re-approval result

Discovery completed at 2026-09-27T03:54:31.262720+00:00, with **88 collector
operations: 87 metadata API calls and one Azure SQL catalog batch**. All 47
coverage surfaces were `COMPLETE`. Polling and definition requests are included
in the 87 API operations. The SQL catalog batch contains catalog queries; it is
not counted as one application-data query.

- Discovery scan: `3db5fbeb-9162-465b-8bf6-e7877a7444af`.
- Raw inventory scan: `b028a5e7-51f2-4413-892d-c562dac67ba5`.
- Target catalog model: `5b3eff46-631c-47b8-8211-049b5aa906ee`.
- Target context: `1570dd54-5f55-4440-a7a0-9d2f74f1ef80`, revision **3**.
- Approval hash: `19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6`.

Both the projected model approval and its new context pin that hash. The old
context remains stored. Five discovered model contexts were refreshed. The
operation log and before/after contexts are retained locally; the content-free
[discovery receipt](runs/discovery-reapproval.json) records identifiers and counts.
Discovery uses its existing bounded collector (160 operations / 600 seconds),
separately from adaptive investigation reservations. Neither budget was increased.

## Exactly three investigation attempts

| Trial | Intake | Investigation data reads | Other reads | Verified / within-layer comparisons | Investigation planner calls | Synthesis | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | HELD, one model call | 0 | 0 | 0 / 0 | 0 | Not reached, 0 calls | No session or outcome |
| R2 | PROPOSED, one model call | 1 Power BI DAX + 1 Fabric SQL | 1 OneLake commit-metadata tool invocation | 1 / 0 | 0 | BLOCKED before provider, 0 calls; not validated | Deterministic `CONSISTENT_TO_BOUNDARY`; incomplete delivery |
| R3 | HELD, one model call | 0 | 0 | 0 / 0 | 0 | Not reached, 0 calls | No session or outcome |

Wall times were 8.512, 67.664 and 8.150 seconds. Keys are
`G-reapproved-R1-20260927`, `G-reapproved-R2-20260927` and
`G-reapproved-R3-20260927`. R2 session is
`54509912-5e30-4850-afd7-ed26b5bc56aa`. All raw outputs and three intake tapes are
preserved. The [machine report](runs/discovery-reapproval-three.json) retains the
per-trial metrics, receipt IDs, surfaces and limits. The ledger has one original
row for each attempt; its `PENDING_TRUTH_REVIEW` and generic failed-intake labels
remain unchanged. The analysis below supplies the more precise qualification.

### R1 and R3: invalid intake proposal, not a discovery refusal

Both responses chose `ticket_shape=MISMATCH_COMPLAINT` together with
`comparison_mode=NONE`. The unchanged validator requires `VERTICAL` or
`HORIZONTAL` for a mismatch complaint. Offline validation against the unchanged
catalog reproduced **`Comparison mode conflicts with ticket shape`** for both.
Their stored error is the broader `INVALID_OR_STALE_PROPOSAL`; the catalog hashes
still match, so the reproduced failure is the invalid pairing, not a stale
catalog. No scope was repaired or resubmitted.

Neither attempt reached preview or executed any probe. There are no execution
surfaces, attestations, compared/skipped boundaries, claimed limits or findings
to grade for those two attempts.

### R2: genuine comparison, with incomplete surface attestation retained

The routine compared the selected semantic quantity in model
`3484a2bc-98c5-4cef-be5c-a6215484075e` against its declared source table
`movement_values` in database `warehouse_gold_e1b8e1`. The binding provenance is
`DECLARED_BY_DEFINITION`. The sealed data receipts are distinct and their
adapter-normalized quantities agree. This is an **adjacent, genuinely
cross-surface comparison**, not two aggregates inside the semantic model.

| Probe | Execution surface | Surface's own report | Engine attestation |
| --- | --- | --- | --- |
| Presentation baseline | `POWER_BI_DAX`; workspace `149f8d99-1c66-4a0a-9624-759be002bb60`; model `3484a2bc-98c5-4cef-be5c-a6215484075e` | Identity `investigator-reader@skynwhy.com` | `MATCHED` for identity; engine, connection and object unattested |
| Declared source aggregate | `FABRIC_SQL`; configured `*.datawarehouse.fabric.microsoft.com` endpoint; database `warehouse_gold_e1b8e1` | Identity `investigator-reader@skynwhy.com` and database `warehouse_gold_e1b8e1` | `MATCHED` for identity and object; engine and connection unattested |
| Ingestion metadata | OneLake Delta commit metadata for the same Gold table, through the existing metadata transport | Commit metadata only | No surface self-report/attestation recorded; not used as either quantity in the comparison |

Exact endpoint and receipt IDs are in the machine report. The OneLake helper
uses the existing metadata account, identified as the administrator in prior
receipts; this run's metadata observation does not independently attest that
identity. It is not a reader-data receipt. Its single metered tool invocation
performs a log listing and a commit-file read; three tool reservations do not
mean three HTTP requests.

Boundaries checked: **semantic table Activity -> declared Gold table
movement_values**. Verified comparisons: **1**. Within-layer checks: **0**.
No non-adjacent comparison occurred. The path did not execute Gold-to-Silver,
Silver-to-Bronze or application-source comparisons: no faithful lower quantity
for those boundaries was supplied in this run. They remain unchecked, not equal.
The engine records `CAPABILITY_UNAVAILABLE` at Gold rather than individual
skipped-boundary records for those uncompiled layers; this reporting limitation
is preserved.

The explicit skipped procedure step was presentation freshness: unavailable to
the isolated execution reader, without elevation. Since the compared values
were equal, the divergence branch was not entered. **No transformation-definition
judgment call occurred.** This trial does not test whether that model judgment
works when a genuine difference is observed.

The deterministic claim was `CONSISTENT_TO_BOUNDARY`, limited to Gold. Its limits
name the five unattested fields: DAX engine/connection/object and SQL
engine/connection. Both deterministic business and technical outputs carry those
unattested fields and the skipped freshness check. No verified defect, intended
business correctness, shared-generation continuity, or upstream agreement was
established.

### R2: synthesis failed before its model call

The saved synthesis status is `BLOCKED`, with `Conflict`, zero calls and no
validated assessment. A read-only offline build of the saved evidence reproduced
**`Process execution surface differs`**. In `synthesis_digest._process_evidence`,
the surface validator accepts exactly `engine`, `connection`, `object`. The
current query probes also carry `identity`, so their four-field surfaces fail
that check. This is the first reproduced blocker, not a claim that it is the only
remaining synthesis problem. No field was stripped and no engine fix was made.

The investigation state itself is `COMPLETED`; that does **not** mean the separate
synthesis/delivery stage completed. The closed outcome is a deterministic partial
result. There remains **no end-to-end completion in this batch**.

## Accounting and preservation

The batch added three intake calls, three cloud-tool reservations, 127,437 input
characters reserved and 4,500 output tokens reserved. Investigation planner calls
and synthesis provider calls were zero. Daily reservations rose from 3 to 6
planner-kind calls and from 4 to 7 cloud-tool calls. Existing usage was not reset
or refunded. Metadata-discovery operations are recorded separately above.
Measured reference model cost across the three intake calls was about $0.03984;
this is a reference-rate calculation, not an Azure billing statement.

Engine, configuration, profile, ticket and usage-policy hashes were checked
before each run; the engine and config remained unchanged afterward. No fourth
trial, repair retry, deadline extension, permission change, freeze or new domain
was attempted. The required two generator tests passed; engine tests were not
rerun because no engine bytes changed. All three intake tapes passed byte/hash verification; both R2 data receipts
passed seal verification. All 112 local link targets checked resolve. The ledger
preserves every prior line and appends exactly three investigation rows;
`git diff --check` passed. No scripts, acceptance code or infrastructure differ
from the main engine used for this batch.
