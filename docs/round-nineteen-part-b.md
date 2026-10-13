# Part B — column dependencies and their limits

2026-10-13. The retained graph's second version is published in PostgreSQL. No estate read or model call was needed for this extraction. Earlier graph versions and raw definition hashes remain readable.

| Estate | Nodes | Edges | DECLARED | UNKNOWN |
|---|---:|---:|---:|---:|
| Fixture | 1,163 | 1,696 | 1,568 | 128 |
| Billing | 388 | 759 | 725 | 34 |

The existing notebook transformation reader now supplies column dependencies to the graph. It added 180 declared column edges and 264 schema nodes explicitly labelled `CODE_DECLARED_NOT_OBSERVED`. Pipeline Script SQL contributes 154 declared column edges. Column names are resolved through declared schemas and connections; an omitted schema is not silently replaced with `dbo`. Branches, procedure execution, set operations and unsupported dynamic operations remain named gaps.

These are statements about retained definitions. A Script that declares or authors a procedure is not evidence that the procedure is deployed or that the pipeline executed it. The interpreter and verification boundary must retain that distinction; quantity equality cannot supply missing deployment evidence.

The requested engine dependency route remains unavailable at the approved reader scope. Microsoft documents that [INFO.CALCDEPENDENCY requires semantic-model write permission](https://learn.microsoft.com/en-us/dax/info-calcdependency-function-dax). The graph preserves the missing DAX dependency as UNKNOWN. Parsing an expression or asking a model to guess it would not satisfy the requested engine-produced evidence.

Fresh definition collection is a separate permission boundary: [Fabric Report Get Definition documents Read and Write permission](https://learn.microsoft.com/en-us/rest/api/fabric/report/items/get-report-definition). Retained publication definitions are usable with their original provenance and observation time; they do not establish that the dedicated Viewer can refresh them. A read refusal must preserve the prior graph and mark current availability, without substituting the publisher identity.

The next bounded interpreter batch uses four exact retained code spans, at most one model call each, with shared dollar and token controls. Its edges can only be INFERRED. The inputs include fixture-authoring code explicitly labelled as not executed or asserted to be deployed. Any proposed edge must cite a validated span; no code is executed by the interpreter. Batch results will be appended below.

The offline v2 publication receipt is `.local/round-nineteen/graph-v2-receipt.json`; both estates passed node/edge conservation and readback of the original version. No new definition Blob was required. This version does not establish any VERIFIED end-to-end path.

## Change-detection deployment preparation

The existing job is 0.5 vCPU and 1 GiB. A six-hour schedule with a 600-second hard timeout bounds 120 monthly executions to 36,000 vCPU-seconds and 72,000 GiB-seconds. Microsoft's [monthly subscription grant](https://learn.microsoft.com/en-us/azure/container-apps/billing) is 180,000 vCPU-seconds and 360,000 GiB-seconds; the remaining grant is shared and is not assumed unused. No new paid resource is proposed.

The CLI unexpectedly refused `containerapp job show`, reporting Microsoft.App unregistered. An independent provider read reported `Registering`, and a direct read of the existing job succeeded. No provider registration or resource setting was changed in response to that CLI message. The exact control response is retained locally as `job-before-schedule-rest.json`.

## Part B boundary, 08:18 UTC

Version three explicitly qualifies all 154 billing Script column edges as authored logic with deployment not established. Counts are unchanged; version two remains in history. The asset catalog seed compares every current graph partition hash before atomically saving its manifest: fixture 825 assets across 61 retained ownership groups, billing 268 across 12. Only 40 and 9 groups respectively produce graph partitions. Original per-asset collection times are retained.

The first cloud interpreter batch stopped on task zero before the provider call: `PermissionError` while creating the capture directory under read-only `/app`. One planner reservation was conservatively settled UNCERTAIN; there was no dollar reservation, model response or model charge. Three tasks were not run. Result CAS SHA-256: `289ab6bbc51f5526f1a3555efead41c686515ce3ff1e7a79954d0b3a0949e13e`. This failure is preserved. The corrected recorder accepts an explicit writable directory; a regression exercises the non-writable default without patching its root. 51 recorder/privacy tests and 16 subtests passed. No retry of the failed task is claimed.

The tested image at `89b2fb75b19524405d9744325b8383bae8884595` passed all eight cloud CI shards. Integrated graph tests passed 55/55 before live admission. The recorder correction requires its own tested image before the remaining tasks. No VERIFIED path or model lineage proposal was produced by this batch.

## Part D interpreter result, 2026-10-13

Execution `job-dia-worker-x9fz5t9` used the tested `ef31595` image (all eight hosted shards green). It attempted only two of the three previously unattempted inputs: the first returned seven exact-span-validated INFERRED proposals; the second failed `GRAPH_INTERPRETER_SPAN_DIFFERS`. The batch stopped and the final input was not attempted. Both complete request/response captures are retained in private hash-addressed Blob storage, alongside the failed result. No retries, estate reads or graph mutations were performed. Result SHA-256: `eb43be7af0b67102dc4eeae0871e3ed13f204a7963cee5053be2e3418ba0d3e1`. Shared-ledger model charge: USD0.088833.

The seven proposals remain reviewable evidence, not published graph truth. Exact span validity does not prove semantic correctness or deployment; these fixture-authoring procedure declarations explicitly do not establish deployment. End-to-end procedure verification remains unavailable. The earlier pre-provider failure and its conservatively charged planner reservation remain unchanged.
