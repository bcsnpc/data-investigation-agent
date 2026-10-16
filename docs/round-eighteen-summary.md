# Round Eighteen ? cloud foundation

2026-10-13 UTC. Draft **#424** is based on draft **#423**; neither is merged. Infrastructure is deployed, but the live cloud demo and complete cloud onboarding are **not earned**. Previous freezes are invalid.

## Platform and safety

| Created resource | Configuration |
|---|---|
| `rg-dia-platform` | Platform resource group |
| `pg-dia-d5dd7d65` | PostgreSQL B1ms, 32 GB, no HA, Entra-only; database `investigator` |
| `diaplatformd5dd7d65` | Standard LRS; private snapshots, tapes, captures, screenshots and archive containers |
| `kv-dia-d5dd7d65`, `id-dia-worker` | RBAC Key Vault and scoped worker managed identity |
| `cae-dia-platform`, `job-dia-worker` | Consumption Container Apps environment/manual job; no always-running API |

PostgreSQL/compute are in South Central US after the approved East US restriction fallback; other resources remain East US. No ACR, Log Analytics workspace or estate capacity was created. Parameterized Bicep and code-only GHCR publication are committed. The estimate is **$13.74/month**, conditional on confirmed PostgreSQL free entitlement through 2027-10-12 and bounded use. Without that entitlement, PostgreSQL alone is about **$19.308/month**. The estimate is not a billing hard stop. [Cost assumptions](cloud-cost-estimate.md).

Worker MI passed PostgreSQL/Blob/vault health checks. The approved existing reader cache authenticated for Power BI and SQL with the same tenant/object/audiences. The reader remains an Entra user; no new estate scope was granted. The existing Azure owner received Secrets Officer on this vault only after the recorded RBAC denial. Existing workstation caches remain. Application-source authentication is unavailable in cloud; Contributor code-reader credentials never serve quantities.

The integrated gateway/literal/MI/Linux gate passed **43 tests / 47 subtests**; the executed image passed eight network-disabled cloud CI shards. The gateway denies unlisted access, but is an application boundary, not an OS firewall. The literal audit covered **358 installed files**, removed one fixture-specific prompt example and separated historical fixture builders from product code. No intake redesign or acceptance expectation changed.

## State, recordings and disk

PostgreSQL production wiring covers smart tickets, catalog/readiness and transactional budgets. Migration preserved **10,022 usage rows**, including historical statuses, plus **1,043 tickets, 291 contexts and nine models**. Graph tables are empty. **Claim-first state, runtime/investigation tables and screenshots still use per-job SQLite**, retained in captures. Generic shared case-file storage exists but has no production writer. Projected cloud persistence/slim recording refuse explicitly.

The pilot plus eight selected tapes occupy **48,595,256 bytes** in shared content-addressed storage. The eight tapes' **1,958,359,736 original bytes** added **23,394,768 bytes**. All 32 restored files and eight local pinned-engine replays matched. Broader conversion remains unfinished. Verified cleanup removed 45 pilot files (**96,485,376 allocated bytes**) and 32 later files (**1,958,359,736 logical bytes**). Failures remain recorded. Logical bytes are not claimed as allocated savings.

D: free space was **13,558,284,288 bytes** at opening and **14,078,382,080** after cleanup; closing free space is **12,648,144,896 bytes** (12.65 GB). Net free space fell by 910,139,392 bytes after new retained artifacts and working files; no net disk gain is claimed. The **10 GB floor** remains enforced. This is selected archival, not completion of the roughly 218 GB recording backlog.

The [content audit](round-eighteen-recording-content-audit.md) covered 1,146 loose tapes, 1,596 inventories and 1,959/1,961 catalog schemas. All 9,652 decoded arrays above 249 rows were accounting. However, 141 tapes have uninspected protocol events, two catalog reads refused and archive payloads are incompletely inspected. Universal no-bulk certification is **not earned**. A separate intentional legacy source export contains **1,410,699 rows**, with a byte-identical duplicate; both remain untouched and excluded from recording publication. Automatic screenshot expiry is not implemented.

## Cloud smoke and failures

Eight historical tapes ran in parallel cloud jobs: initial **7/8**, about **68 seconds** from first start to last finish, versus local **8/8 in 198.253 seconds**. Correcting Windows-path handling gave the remaining shard **1/1 in 55 seconds**. All eight have passing cloud receipts, but no single all-green parallel timing cohort or speedup is claimed. Offline replay children made zero network/estate/model calls; platform artifact controls are separate.

| Fresh cloud verification | Reader result | Physical requests | Exact replay / demo |
|---|---|---:|---|
| `job-dia-worker-974nsjk` | 18/18 witnesses; 40/40 probes | 89 | FAILED: shared/legacy budget clock sequence differed; demo NOT_RUN |
| `job-dia-worker-ybvd8u6` | 18/18 witnesses; 40/40 probes | 89 | FAILED: live-only `require_read_only` field changed worker request bytes; demo NOT_RUN |

Both tapes remain immutable. No readiness certificate or **7,661 ? 8,765** cloud finding was earned. Connection attestation remains partial and **SNAPSHOT_UNVERIFIED** applies. Recording fixes now select the actual shared-budget algorithm, initialize replay controllers without live state, construct SQL payloads identically in live/replay, and preserve first errors through cleanup. The last fix requires fresh pinned verification; it does not make the old tape pass. Native capture pointers now export with explicit incomplete-capture dispositions; neither executed image is changed retroactively.

Full executed engine `e646f7e`: **4,057 passed, 46 skipped, 1,416 subtests**, 464.88 seconds. Subsequent payload/error fix: **23 focused tests passed**; pointer export: **19 passed**. Final integrated source `db3bed8`: **4,073 passed, 46 skipped, 1,416 subtests**, 449.65 seconds. All eight cloud CI shards passed and the corrected image was published (workflow 38352575331). Prior failed invocations remain in the ledger.

## Setup and closing limits

Retained-control preflight is fixture **8 PASS / 0 FAIL / 24 MISSING**, billing **8 / 0 / 13**: both **NOT_READY** as whole estates. Billing's example covers its semantic model, not the full chain. The guide exercise corrected paths, region parameters, credential-reference consistency and receipt imports. Clean-client onboarding through teardown is not proven. [Part D](round-eighteen-part-d.md) and [owner actions](owner-actions.md) distinguish operator work from future permission decisions.

At **05:48:18 UTC**, all **178 new physical requests were SETTLED**. New model calls/spend: **0 / $0**; shared charge **$107.957725**. Pot **3,017/4,000**, rolling **376/3,000**, restoration **95 untouched**, diagnostic cap **12 unchanged**. The $10 round allowance and protected $10 margin remain intact. One status read lost its connection; a second stalled and was stopped; a direct repeatable-read SELECT report supplied the closing figures without mutations. No third verification or demo was admitted.

Remaining: earn exact cloud verification/demo; complete shared claim/case persistence; broader archive/content audit; projected cloud storage; enforced retention; complete client preflight/onboarding; source-app cloud authentication. No general availability claim is made.
