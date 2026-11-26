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

Runtime scope: proved on Windows PowerShell with ADOMD 19.117.0. The native adapter needs those configured dependencies. No Linux-native XMLA execution, cloud deployment or complete HealthNet ticket run is claimed. HealthNet remains READY_SEALED_TEST with enabled=false, disabled connectors and installation=null. The semantic models and all existing permissions are unchanged by this transport task.

## Verification

Synthetic practice-fixture connector tests cover default REST versus configured XMLA, engine-port forwarding, worker projection, closed configuration, exact target scope, credential binding, gateway refusal of writes, response precision/identity, bounds and sanitized failures. No HealthNet-specific reasoning, prompts, rules or expectations changed. All 69 prompt-bearing files retain their authoring-freeze hashes. Compared with that earlier freeze, three additional existing files changed solely for this authorized connector selection (investigative_native.py, metadata_config.py, run_native_diagnostic.py); the prior three documented plumbing exceptions remain. New files are the generic XMLA adapter, native reader script and synthetic tests.

Qualification and per-case replay comparison are recorded in `docs/healthnet-engine-dax-evidence.json` when complete. The prior smoke receipts remain untouched. HealthNet tickets and encrypted expectations are byte-identical to approved seal commit 6e800e15; their contents were not read during this task.
