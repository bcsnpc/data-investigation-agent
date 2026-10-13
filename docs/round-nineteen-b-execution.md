# Round Nineteen-B execution record

Owner approval dated 2026-10-13 (America/Chicago), from `round-nineteen-b-complete-the-graph.md`. Branch starts at 3fdbf7d; no prior result or evidence is rewritten.

## Authority under CLAUDE.md section 8

One additional secretless `dia-scanner`, following the existing cross-tenant federated pattern, with Contributor only on the approved test workspaces and model Write for dependency metadata. Separate scanner-only gateway must pass red-team tests before its first live call. Investigator access remains read-only; no scanner credential may enter investigation execution. Read-only admin metadata setting scoped to scanner-only security group. One `dia-sample-estate` workspace and official Microsoft sample on existing capacity. No new paid resource. Existing platform cost must remain below USD20/month.

Fresh round pot1500, reserve95, rolling3000 and investigation12 unchanged. Model new spend at most USD15 with existing protected USD10. Counters preserved. Merges authorized only in PartE, in order423/424/425/newPR, merge commits, full tests and CI; tagv0.19b after verifiedmain. Prior freeze invalid when code changes.

## Execution boundaries

Part0 runs first, with background archive alongside later parts. Live captures pause below11GiB free. Original archives may only be removed from verified manifests; prior tool refusal is honored by an owner-run `.local/cleanup-all-verified.ps1`, not a workaround. Archive bulk transfers require current cost admission; old13.74 baseline is stale after the schedule allocation.

## DECIDED WITHOUT REVIEW

- Interpret "no agents" as no product agent/intake changes: the same prompt explicitly requires parallel engineering helpers in isolated worktrees.
- Preserve the previous round's failed verification inputs; correct the new batch's prewarm cross-reference rather than weakening the guard.

## Opening

Opened 2026-10-13T16:26:06.421688+00:00; free disk11432660992bytes (10.647GiB). Live-capture admission blocked below11GiB; offline engineering and approved platform controls continue.

Budget opened 2026-10-13T16:26:13.900646+00:00: shared USD108.046558; ceiling USD133.046558, including protectedUSD10 and newUSD15. Fresh physical pot1500/reserve95. Rolling3000 and all daily limits unchanged; counters not reset. No existing RESERVED monetary reservation. Previous scheduled scanner retains its old round pin and must not silently adopt the new pot.

## Owner archive verification amendment, 2026-10-13

New archive uploads use Cool tier, locally computed hashes, upload Content-MD5 validation and a properties comparison; no verification download. Matching objects are then moved to Archive. The USD20 ceiling applies to steady monthly running cost. The owner separately approved up to USD2 total one-off archive transactions this round. Current runtime/test inputs remain excluded. Previous full-readback receipts are preserved as historical proofs, not retroactively relabelled. For block uploads, each block must use service-validated transactional MD5; stored whole-object MD5 alone is a client-supplied property and is not represented as Azure recomputing SHA256.

Scanner setup before first use: the home application, federated credential and home service principal were created. Fabric-tenant service-principal creation returned HTTP400 NoBackingApplicationObject. Receipt and original failure retained under `.local/round-nineteen-b/scanner-identity-controls.json`; no scanner token or estate call yet. The existing same-pattern investigator had the same propagation response. One bounded retry is permitted only after independently confirming the unchanged backing app, without changing identity/scope or creating a second app. This resolves propagation rather than bypassing a permission refusal. Initial local script encoding failure made zero network calls and is preserved separately.


## Scanner setup applied, 2026-10-13 (§8)

Approved by Chaitu in the Round Nineteen-B prompt. The unchanged backing application was independently checked; one bounded retry created its Fabric service principal. No password or certificate was created. The federated credential trusts the existing platform managed identity, with the application in its home tenant and service principal in Fabric. This follows the existing cross-tenant federation pattern.

- app_id: `86a9d95a-466c-443e-9eb9-91f870ffe15a`
- app_object_id: `706915c6-0dc6-472f-beca-caf29547a030`
- home_sp_id: `77d6ee28-5b37-46b4-9d10-8985c01bc318`
- fabric_sp_id: `dbb49594-6c70-4989-a6c8-c4f237c4a021`
- group_id: `94dbb72c-f1f2-4b4f-9e21-2e1e5ca73096`
- name: `dia-scanner`
- credential: `federated id-dia-worker; no secret or certificate`

Exact workspace grant on each of fixture `149f8d99-1c66-4a0a-9624-759be002bb60` and billing `7d67bb36-04f6-4182-95aa-da5d515248fa`:

```http
POST https://api.fabric.microsoft.com/v1/workspaces/{workspace}/roleAssignments
{"principal": {"id": "dbb49594-6c70-4989-a6c8-c4f237c4a021", "type": "ServicePrincipal"}, "role": "Contributor"}
```

Independent listings: scanner absent before, one Contributor assignment after, on each workspace. The rebuilt workspace was not granted. No direct model grant was applied; inherited workspace rights will be tested rather than presumed to prove INFO access. Investigator roles are unchanged.

Tenant settings `AllowServicePrincipalsUseReadAdminAPIs`, `AdminApisIncludeDetailedMetadata`, and `AdminApisIncludeExpressions` each retained their existing groups and appended only scanner group `94dbb72c-f1f2-4b4f-9e21-2e1e5ca73096` (`dia-scanner-metadata-only`). All three read back enabled with that group. Group contains only the scanner. The exact requests, before/after listings, initial 400 and later success are retained locally in `scanner-identity-controls.json`; no secret is in that receipt.

Integrated focused check: 52 tests and 106 subtests passed, including denied write paths and scanner credentials unavailable to investigation jobs. A subsequent dependency wiring/CI change is under verification before first scanner live use. This is application gateway enforcement, not a claim of an OS/network security boundary.

Cleanup correction: 37 files referenced by current tests/runtime were removed before exclusions were complete. Calling the script ready was an implementation error. All 37 were restored from retained local archives, with exact original SHA256 and size checks (1,071,241,247 bytes), without network retrieval. The new script protects them; original deletion logs remain. Disk afterward: 12,551,286,784 bytes free.

## Platform graph table grant, 2026-10-13 (?8)

The first scanner batch retained 31 physical requests and all 12 owner refreshes unavailable: five publication attempts failed with `InsufficientPrivilege`; seven kinds remained unsupported. Admin metadata scan succeeded. The batch is not a coverage success.

The existing Round Eighteen owner approval grants the worker rights to the tool database only. The new graph tables had omitted those grants. Applied via the existing owner connection, only to the five platform tables below; no estate reader permission changed.

```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE dia_state.estate_graph_nodes, dia_state.estate_graph_edges TO "id-dia-worker";
GRANT SELECT, INSERT, UPDATE ON TABLE dia_state.estate_graph_owner_versions, dia_state.estate_graph_history TO "id-dia-worker";
GRANT SELECT, INSERT ON TABLE dia_state.estate_graph_changes TO "id-dia-worker";
```

Before: all four permissions false on all five tables. Independent after: nodes/edges SELECT, INSERT, UPDATE, DELETE; owner_versions/history SELECT, INSERT, UPDATE; changes SELECT, INSERT. All other listed permissions remain false. Exact receipt: `.local/round-nineteen-b/platform-graph-grant.json`, at 2026-10-13T17:01:29.884766+00:00.


## 2026-10-13 continuation checkpoint

Billing retry refreshed both formerly colliding owners after the gap-identity repair. Both billing Warehouse schema owners were subsequently refreshed through the existing investigator SQL scope (21 physical requests); no scanner SQL credential was used. Fixture batches continue. RESCANNED is not itself proof that INFO calls succeeded or that a complete path is verified.

The first sample-publication preparation failed on its first read-only workspace list: HTTP200 bytes were not decoded before JSON parsing, ending in KeyError `value`. One physical control request, zero mutations. Original script and receipt retained. A separately hashed v2 publisher uses bounded decoded reads and explicit response-shape refusals; seven offline tests pass. Its new attempt created the approved workspace and roles, then received HTTP202 for the unchanged official sample import. Completion is pending; it is not yet an onboarded estate.

The final cloud verification attempt was admitted after an offline 18-binding,40/40-probe check, full manifest/spec budget equality, and an independent current-model match. Candidate e77890a70a7b6661456d3098aa9594ad79040f98f1453a451e360297f1238a0a; execution job-dia-worker-siyf9k6. No third live attempt is authorized.

Archive selection caught six additional capture parents referenced by current acceptance manifests before the first network upload. The original100-file plan and zero-network interruption remain; corrected76-file batch excludes24 files. Nothing from either batch is yet declared cleanup-ready.

## Owner additional cloud attempt approval, 2026-10-13 (section 8)

Chaitu approved one additional attempt, conditional on a matching job/run runtime of at least 1,800 seconds, exclusive shared-budget writer access with bounded lock waits, and passing offline admission. This supersedes only the earlier no-third-attempt stopping decision; both failed attempts remain unchanged. All other caps, identities and scopes stay unchanged. No retry follows a failure of this additional attempt.

The existing job was read, changed from replicaTimeout600 to1800 and temporarily switched from its six-hour Schedule to Manual (parallelism1/completion1), then independently read back. No paid resource was added. The original schedule will be restored after the isolated window. Before/after: `.local/round-nineteen-b/job-before-owner-runtime-approval.json`, `job-isolation-update.json`, `job-after-isolation-update.json`.

Platform-only PostgreSQL contention proof passed using an isolated namespace and advisory key, leaving the production lease untouched. Foreign writer refused in0.345s; a held lock raised SQLSTATE55P03 (canceling statement due to lock timeout) after5.387s; same-owner access, recovery and exception release passed. Receipt SHA256cc4070aa950aaf58ec24e8d6b875875a03ccb0038a65e9f09e8f4e016ee4cc4a. This is not evidence that production workers drained; fresh production observations are required at admission.


Frozen source78b17f8: full unittest discovery ran4,451tests in1,804.662seconds, OK,46skipped. Subsequent integrated changes receive separate focused/full validation. No original capture or expectation changed.

## Additional isolated attempt admitted, 2026-10-13

Frozen source `ff0347dba28ff8080db687648f53c93cfbe50dbc` passed the full pytest suite: 4,455 passed, 46 skipped, 1,552 subtests passed in 796.41 seconds. All PR checks passed; the separately published image passed its eight offline shards. Its immutable digest is `sha256:1a62ec92012d419b0b040cf6aef99bfaf2dda17835c61e8e5e687f19ecd126b6`.

Preparation03 completed without estate or model calls. Its publication candidate pins the current revision6 model, rather than restoring an earlier image of shared state. The reviewed candidate hash is `528d97d11b0e983e43f4c2e45a0d92b32129019c4a77f9240adc1716b79e273c`.

The additional attempt started at 18:46:51 UTC as `job-dia-worker-rhp9wxh`. Fresh control-plane observations showed all56 earlier executions terminal, the sole job Manual with1800-second timeout, no other Container Apps and no other PostgreSQL sessions or advisory holders. The admission check passed before the one start request. A2100-second exclusive writer lease covers the1800-second run envelope;1200seconds are available for work and600 for finalization. Foreign cooperative writers refuse before waiting; database lock waits are bounded. Old images/raw administrative writers remain operationally drained. This is not a database ACL claim. Archive uploads touch Blob/local files only.

The live result is pending; admission is not successful verification, exact replay or a demo finding. A failure of this additional attempt will not be retried. Original attempts and charges remain unchanged.

## Additional attempt closed, 2026-10-13

Job `job-dia-worker-rhp9wxh` ran18:46:51-19:01:54 UTC, within1800seconds. Azure reports its wrapper Succeeded; the retained stage result is FAILED, `ValueError: VERIFICATION_NOT_COMPLETED`. The capture wrapper completed, but the actual verifier progress is REFUSED: six bounded binding witnesses agreed, and the seventh independent source read failed. No verification profile or READY route was published; family A was not admitted. No further attempt follows.

The complete353,827,279-byte ZIP is retained locally and remotely, SHA256 `e1c1a35d395bd72bfbb884e360c84b0ce3cae5e0cc567678dde6a799c6ceb065`. Verification tape SHA256 `e47da8adbde93ac29737d2498d2466f3052020cfc2c1ae191b1853527bf864a7`. Exact offline replay and the lower read receipt are being audited separately. Counts:36physical,16verification reads against40,0investigation diagnostics against12,0model calls,0pending reservations.

At19:00:50 a read-only platform check found no other PostgreSQL sessions or advisory holders. Cleanup released the exact lease. Schedule restoration PATCH returned success with an empty body; the control receipt parser raised JSONDecodeError. That control failure remains recorded. An independent GET at19:05:04 confirmed the original Schedule/cron/retry/template restored with timeout1800 retained; no repeated PATCH was sent and no usage counter changed.

Sample repair frozen source6c94c1b full pytest:4,461passed,46skipped,1,552subtests,615.75seconds. The tested image starts the separate sample structural rescan at19:05:41 as `job-dia-worker-iw8hnx5`; this is not a cloud-demo retry.

## Bronze follow-up owner approval, 2026-10-13

The owner conditionally approved one further full attempt after a maximum-ten-request Bronze-only check. Exact identity/endpoint and before-permission evidence are in [the diagnosis](round-nineteen-b-bronze-diagnosis.md). Current Viewer scope already covers the unchanged Bronze endpoint; no grant or identity switch was justified or performed. The first probe launcher failed before imports and zero SQL reads; corrected launcher pending. The sample rescan completed with359nodes/396edges,204UNKNOWN boundaries and no verified source path.
