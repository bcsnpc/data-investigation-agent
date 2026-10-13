# Round Eighteen ? cloud foundation

Recorded2026-10-13 UTC. Draft **#424** is based on draft **#423**; neither merges. The foundation is deployed, with explicit gaps below. The previous freeze is invalid. The cloud verification/demo closing result is still pending in this checkpoint.

## Platform, cost and guardrails

Created `rg-dia-platform`, PostgreSQL `pg-dia-d5dd7d65` (B1ms,32GB,no HA,Entra-only), private Standard LRS Blob `diaplatformd5dd7d65`, RBAC Key Vault `kv-dia-d5dd7d65`, worker MI `id-dia-worker`, and consumption Container Apps environment/job `cae-dia-platform` / `job-dia-worker`. PostgreSQL and compute use South Central US after the approved East US restriction fallback; the other resources use East US. No always-running API, ACR, Log Analytics workspace or estate capacity was created. Parameterized Bicep and CI-published code-only GHCR images are committed.

The estimate is **$13.74/month**, conditional on the confirmed PostgreSQL free entitlement through2027-10-12 and bounded storage/compute use. Without that entitlement, regional PostgreSQL alone is about$19.308/month. This is an estimate, not an Azure spending lock; see [cost assumptions](cloud-cost-estimate.md).

The worker MI passed platform PostgreSQL/Blob/vault checks. The owner-approved existing investigator-reader delegated cache authenticated for Power BI and SQL with the same tenant/object/audiences. It remains an Entra user, not a newly created principal. Vault-only Secrets Officer was applied to the existing Azure owner after the recorded RBAC refusal; no estate reader gained scope. Application-source workstation authentication remains unreachable in cloud. The Contributor code reader never serves quantities.

The integrated gateway/literal/MI/Linux gate passed43 tests/47 subtests; all eight current cloud test shards passed with network disabled. The gateway is deny-by-default and an application boundary, not an OS firewall. The hard-coding audit covered358 installed files, removed one fixture-specific prompt example and separated historical fixture builders from product code. No intake redesign or acceptance change occurred.

## Storage and disk

Shared PostgreSQL now holds smart-ticket state, catalog/readiness and transactional budgets. Claim-first state, investigation/runtime tables and screenshots remain in per-job SQLite persisted in captures. Generic shared case-file repository support exists but is not wired into a production writer. Migration preserved10,022 usage rows, statuses and monetary counters, plus1,043 tickets,291 contexts and nine models. Graph tables remain empty. Private SQLite supports offline replay. Privacy-projected PostgreSQL and slim cloud recording explicitly refuse until supported; there is no silent exact fallback.

The pilot plus eight selected tapes use48,595,256 bytes of shared content-addressed storage. The eight tapes'1,958,359,736 original bytes added23,394,768 bytes;32 reconstructed files were byte-identical and all eight local pinned-engine replays matched. Most historical conversion remains unfinished. Verified archive cleanup removed45 pilot files (96,485,376 allocated bytes) and32 later files (1,958,359,736 logical bytes). Initial connection-reset and transport-counting errors remain recorded; the corrected transport counts physical dispatches. Logical bytes are not claimed as allocated savings.

D: free at the Part D opening was13,558,284,288 bytes; after cleanup14,078,382,080. Closing free space will be recorded after current artifacts are retained. The10GB floor remains enforced. No general deletion or full218GB archive claim is made.

The [content audit](round-eighteen-recording-content-audit.md) inspected1,146 loose tapes,1,596 inventory schemas and1,959/1,961 catalog schemas. All9,652 decoded row arrays exceeding249 were accounting. However141 tapes have uninspected protocol events, two catalog reads refused and archive payload inspection is incomplete: universal no-bulk certification is **not earned**. A separate intentional legacy export contains1,410,699 rows, with a byte-identical duplicate; both remain untouched and excluded from recording publication. Screenshot expiry is configured but not automatically enforced.

## Cloud execution and onboarding

Eight historical tapes ran as parallel cloud jobs: initial7/8 in about68seconds from first start to last finish, against local8/8 in198.253seconds. A Windows-path portability correction gave the remaining shard1/1 in55seconds. Thus all eight have passing cloud receipts, but no single all-green parallel cohort or speedup claim is made. Offline children made zero network/estate/model calls; platform artifact controls are separate.

The first live reader verification completed18/18 witnesses with40 probes and89 physical requests, then failed exact replay before readiness or demo admission. New captures now declare the shared-budget implementation and replay that algorithm privately; old failures/bytes are preserved. A fresh approval conserved825 retained assets and admits verification02 on immutable imagee646f7e. Its closing result is pending. Connection attestation remains partial and SNAPSHOT_UNVERIFIED remains throughout; reader verification alone is not the requested7,661-to-8,765 finding.

Retained-control preflight: fixture8 PASS/0 FAIL/24 MISSING; billing8 PASS/0 FAIL/13 MISSING. Both are NOT_READY as whole estates. Billing's example declares its semantic model, not the entire chain. The setup-guide exercise found and fixed paths, regional parameters, credential-reference consistency and receipt imports. Clean-client onboarding through teardown is not proven. [Part D](round-eighteen-part-d.md) and [owner actions](owner-actions.md) separate unfinished operator work from future authority decisions.

## Closing status

The last completed full regression on60c741a passed4,055 tests. A later frozen9634cef run had4,056 passes and one replay-bootstrap failure; its correction passes the specific test on e646f7e, whose full run is pending. Do not treat the older full pass as certification of every later commit.

Opening shared model spend$107.957725; new allowance$10, ceiling$127.957725 with protected$10 margin (admission stop$117.957725). After verification01, new spend$0; pot2,928/4,000, reserve95, rolling287/3,000. Closing verification02/demo counters remain pending. Investigation diagnostic12 and every other cap stay unchanged.

Remaining product gaps: integrating claim-first and case-file shared persistence; full archive conversion/content audit; projected cloud persistence; enforced screenshot/cloud-wide purge; complete client preflight/onboarding; source-app cloud authentication; and the live demo result until its gates pass. No general availability claim is made.
