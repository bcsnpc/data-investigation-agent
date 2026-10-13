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
