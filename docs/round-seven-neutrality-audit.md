# Round Seven platform-neutrality audit

2026-10-06 America/Chicago. Offline; zero estate reads. The existing CI ratchet measured **85 matches in18 modules before,83 in17 modules after**. Two unnecessary product names were removed from comments in dependency_context and evidence_synthesis. No executable configuration, provider admission, receipt, prompt or capability description changed. The frozen historical ceiling is unchanged; the active allowance was lowered.

**Zero was not reached.** Seventy-two remaining product matches are real legacy integration debt; eleven fixture-column-pattern matches are all the neutral `reason_code` field, not business-column branches. The scanner is unchanged and still catches that spelling. There are no account, GUID or fixture-value matches above adapters in this measurement. Removing spelling while leaving provider interpretation above the adapter is not neutrality.

## Remaining words, modules and reasons

| Module | Matches | Words | Required migration / reason retained |
| --- | --- | --- | --- |
| `adaptive_candidates.py` | 2 | `fabric` | Legacy native reader/workspace eligibility. Moving its configuration interpretation requires an adapter-owned eligibility interface; preserve the reader refusal. |
| `adaptive_runtime.py` | 26 | `azure`, `fabric`, `reason_code` | Legacy transport construction, optional metadata routes and live-provider usage governance. Migrate the transport factory and live-provider trait together; deleting the guards would weaken admission. |
| `connection_registry.py` | 4 | `fabric` | Legacy native URI to ownership/connection mapping. Its adapter must supply connection identities before the engine can stop parsing this scheme. |
| `discovery_collect.py` | 13 | `azure`, `fabric`, `onelake`, `powerbi` | Installed-platform discovery orchestration and catalog conversion. Move behind the connector registry while preserving legacy enumeration coverage and immutable IDs. |
| `dynamic_reasoning.py` | 3 | `power bi`, `reason_code` | One executor description in planner guidance; change it only with measured context/golden coverage. The other matches are the neutral reason_code field, not fixture columns. |
| `enterprise_discovery.py` | 9 | `fabric` | Legacy graph/model-catalog identities and approved workspace roots. Adapter-owned identity conversion must preserve historical approvals and deny scopes. |
| `evidence_synthesis.py` | 1 | `azure` | Live-provider metering guard. Replace with a provider-owned live-execution trait before removing the provider name; never make unmetered execution eligible. |
| `flexible_tools.py` | 5 | `fabric`, `reason_code` | Native reader and workspace admission/receipt checks. Move configuration decoding behind the registered adapter without removing the boundary; reason_code is neutral feedback. |
| `native_identity.py` | 2 | `fabric` | Configuration-specific workspace and reader scope guard. Keep neutral self-report validation separate from adapter-owned configured-reader decoding. |
| `onboarding.py` | 1 | `fabric` | Legacy catalog ownership root. Existing model IDs and history must survive an adapter-owned URI constructor migration. |
| `physical_binding.py` | 3 | `fabric` | Installed-platform physical URI/owner interpretation. The adapter must emit opaque ownership records; renaming the scheme would hide the interpretation. |
| `proof_preflight.py` | 8 | `fabric`, `powerbi` | Legacy installed-platform control-plane API preflight. Move the executable helper and its permission boundary into the adapter, preserving receipts and callers. |
| `query_dax.py` | 1 | `power bi` | Executor limitation text in advertised capabilities. An adapter-owned description must replace it with measured payload coverage; a cosmetic replacement is not capability discovery. |
| `query_sql.py` | 2 | `reason_code` | Both matches are the neutral reason_code feedback keyword. It is not a fixed business column here; renaming the contract would create false progress. |
| `record_readback.py` | 1 | `fabric` | Legacy native workspace refusal. Adapter-owned scope decoding must preserve the exact approved-reader boundary. |
| `semantic_graph.py` | 1 | `power bi` | Executor-specific evidence limitation text. Supply the description through the adapter rather than disguising which runtime interprets the language. |
| `source_diagnostics.py` | 1 | `fabric` | Legacy configured-workspace scope refusal. Keep it until adapter admission carries the same approved scope. |

## Validation and DECIDED WITHOUT REVIEW

Three existing ratchet tests and eleven planner projection/wire golden tests pass. The dense directory remains28 entries/11 SQL objects before and after; all projected and wire golden objects are byte-identical, and their expected files were not regenerated. This change adds no planner content. No output or acceptance answer is changed. The seven-check hosted gate must pass before merge.

Keep the explicit residual allowance rather than moving entire mixed engine modules under an adapter or renaming security configuration to make a text counter reach zero. Those alternatives would conceal live-provider metering and scope interpretation instead of removing it. The table is the next migration backlog, not a claim of completed neutrality. The optional post-gate scope is limited to honest debt reduction/audit in this PR; no engine behavior or estate capability is rebuilt. Engine-file comments change the fingerprint, so earlier freezes remain invalid.
