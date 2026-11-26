# HealthNet engine DAX transport

Owner request and execution: 2026-11-26. PR #436 remains draft; no merge or tag.

## Path confirmed and changed

Before this change, ticket DAX used REST `executeQueries`. The AI investigation port is `scripts/investigator/adapters/investigative_native.py:NativeQueries.__call__`, which calls `scripts/run_native_diagnostic.py:execute`. That executor built the Power BI REST request regardless of the separate XMLA diagnostic configuration. The earlier successful HealthNet XMLA totals were smoke-helper reads, not proof of ticket transport.

The HealthNet native connection bundle now selects `fabric.dax_transport.mode = xmla`, with its exact workspace ID and the three previously verified model ID/native-name bindings. NativeQueries forwards that installed setting to the same executor. The legacy native worker path preserves it in its closed configuration projection and narrows model bindings to the requested model. No setting means the existing REST path. A configured XMLA failure never falls back to REST or an owner identity.

The new generic connector authorizes `XMLA_EVALUATE` through the gateway for the exact workspace/model IDs and validates the DAX before native execution. ADOMD uses the existing investigator token via AccessToken, no EffectiveUserName, Roles override or password. Connection-string values are escaped by DbConnectionStringBuilder. Reader principal, tenant and audience checks, query timeout, response-size/row bounds, exact decimal JSON and the existing native identity receipt remain enforced. No XMLA write/DDL API is exposed. Errors are reduced to a fixed safe message; uncertain subprocess completion remains a timeout.

## Actual engine-path proof

One read on HealthNet Operations (`85e662ed-c4e6-41fb-9e43-be0c5a6aeeae`):

```dax
EVALUATE ROW("ok", 1)
```

Result: `[ok] = 1`, PASS, 14.226 seconds. Entry point was the real NativeQueries port, using its default executor and the new gateway XMLA adapter, not a mocked query or the earlier smoke helper. The gateway policy admitted only XMLA_EVALUATE on the three configured HealthNet model IDs. This laptop supplied the already-approved investigator app token at the credential-provider seam; the engine still checked its principal, tenant and audience. It did not use the owner's token for DAX. Native reader: dia-investigator-round19, Fabric principal `439ceb25-d200-4f02-95cf-4b1318faca62`.

The proof used one settled INVESTIGATION request. Afterwards: physical 19,299/20,500; investigation 16,818/17,905; SCAN 2,430/2,500; restoration 51/95, unchanged. Zero ticket runs, AI calls, injections or new grants.

Runtime scope: proved on Windows PowerShell with ADOMD 19.117.0. The native adapter needs those configured dependencies. That initial checkpoint did not claim Linux-native execution. The subsequent Linux proof below supersedes that runtime limitation; no complete HealthNet ticket run or permanent deployment is claimed. HealthNet remains READY_SEALED_TEST with enabled=false, disabled connectors and installation=null. The semantic models and all existing permissions are unchanged by this transport task.

## Verification

Synthetic practice-fixture connector tests cover default REST versus configured XMLA, engine-port forwarding, worker projection, closed configuration, exact target scope, credential binding, gateway refusal of writes, response precision/identity, bounds and sanitized failures. No HealthNet-specific reasoning, prompts, rules or expectations changed. At the Windows checkpoint all 69 prompt-bearing files retained their authoring-freeze hashes. The Linux extension subsequently changes one of those files, build_cloud_image_context.py, solely to admit the two native client source files; its diff changes no prompt text. The other 68 file hashes remain identical. Compared with that earlier freeze, three additional existing files changed solely for this authorized connector selection (investigative_native.py, metadata_config.py, run_native_diagnostic.py); the prior three documented plumbing exceptions remain. New files are the generic XMLA adapter, native reader script and synthetic tests.

Qualification, the actual Azure proof and per-case replay comparison are recorded in `docs/healthnet-engine-dax-evidence.json`. The prior smoke receipts remain untouched. HealthNet tickets and encrypted expectations are byte-identical to approved seal commit 6e800e15; their contents were not read during this task.


## Linux extension requested by owner

The owner subsequently required the actual Linux Azure worker image. The image now builds a .NET 8 console reader against Microsoft.AnalysisServices.AdomdClient 19.117.0 and includes the .NET runtime. The configured engine adapter selects this fixed native helper on Linux; Windows keeps its existing ADOMD/PowerShell implementation. Both receive the token through stdin, use AccessToken, return the same rows contract and pass the same gateway DAX authorization. This uses Microsoft's supported .NET client for HTTP cloud XMLA rather than REST executeQueries: https://learn.microsoft.com/en-us/analysis-services/client-libraries?view=sql-analysis-services-2025 . The client package and target runtime are pinned in infra/xmla-reader/Dia.XmlaReader.csproj.

Build qualification first caught the .NET Core AccessToken namespace difference; it was corrected without a live attempt. Image shards then correctly rejected missing native source files under the existing strict image-provenance check; the source files are now copied into the runtime image too, with no provenance-check relaxation. The native client also loads in an offline, no-network image self-test. Final Linux proof and qualification results are recorded below.

## payer_plan_history

The recorded metadata classifies app.payer_plan_history in hn_billing as an ordinary NON_TEMPORAL_TABLE, with no current-table temporal parent. The database reader role is present and its effective INSERT check was 0; a direct data read has not been demonstrated. Its direct count remains NOT_RUN: the owner's instruction permits history reads through current tables using FOR SYSTEM_TIME, and no such route exists for this ordinary table. It is not a proved SQL denial, nor a proved data read. No direct history query or guard relaxation was used. The unexplained INSERT=1 reports concern the other five active temporal history tables; this transport task does not resolve them.


## Final Linux Azure result

**PASS.** Manual execution `job-dia-worker-p3vbys2` ended **Succeeded**, 2026-11-26 22:10:44 to 22:11:30 UTC (46 seconds). Its actual image digest matches the qualified image `sha256:8018ca9a08c8fdb0527525514cdbe7e0b683723abbc0f326dd4b9c79b235a3e9`, source `b7b3b2c9a562242ef39f422fc974f82c326c73f2`.

Inside that Linux worker, the real engine path returned `[ok] = 1` for the single query above in 14.971 seconds. It used the existing managed identity's investigator federation without the Windows token-provider substitution. The transport was native ADOMD XMLA, not REST executeQueries. The existing limited-attestation warning remains a warning. No ticket, AI call, source query, model change, injection or permission change occurred.

The proof used the existing job's 0.5 vCPU / 1 GiB resources through an execution-only image/command/environment override. Fresh readback proves the scheduled job template, configuration and identity are unchanged. ARM execution listing returned BadGateway through both APIs before launch; that limitation is retained, with no claim of zero other in-flight executions. Job readback and the unique execution's status read worked. There was one accepted start and no POST retry.

[Qualification workflow 45901279787](https://github.com/bcsnpc/data-investigation-agent/actions/runs/45901279787): **6,239 passed, 54 skipped, zero failures/errors; all eight image shards passed**, then the immutable image was published. The native Linux ADOMD dependency test actually ran in the image (not skipped), loading client 19.117.0.0 on .NET 8.0.34. All 123 saved replay classifications/statuses/stops remain unchanged: 86 completed, 28 preserved failures, nine preserved no-investigation cases. No new estate or AI call occurred in replay.

Both proof reservations (one Windows, one Linux) are SETTLED, with zero open. After the Linux proof: physical 19,300/20,500; INVESTIGATION 16,819/17,905; SCAN 2,430/2,500; RESTORATION 51/95, unchanged. Monthly limits and all model budgets remain unchanged. The local hash manifest pins 24 receipt files; older 33 smoke receipt pins and approved sealed HealthNet test files remain unchanged. PR436 remains draft; no merge/tag.


## Owner clarification follow-up, 2026-11-26

The earlier NOT RUN status for ordinary `payer_plan_history` is superseded: its real Linux engine count is 14, with the unchanged permission guard admitted and Azure Succeeded. The no-direct-history rule still applies to the five system-versioned history objects. See [final readiness](healthnet-final-readiness.md) and its pinned receipts. No new permission or engine change.
