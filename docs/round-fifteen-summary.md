# Round Fifteen final report

Dated 2026-10-11 America/Chicago / 2026-10-12 UTC. The isolated owner portal completed original family A. Billing remains incompletely onboarded; all 51 clarification continuations ended HELD without reaching a technical investigation. PIPELINE is restored as the default. Draft #423 stays draft and is not merged. Current source fingerprint is `b9868654a96b89e0d254ea813ff7889c6f57afbec86886e4a57b1065b63eae6b`; prior freezes remain invalid.

## Billing onboarding

| Stage | Result | Evidence and limit |
|---|---|---|
| Discovery | PARTIAL; completeness blocked | Workspace, report/model definitions, seven source objects/42 columns, Bronze and pipeline definitions retained. Two Warehouse catalogs hit an implementation limitation. Connection lookup returned HTTP 403. `can_view_definition=0` blocks the collector's completeness check; it does not prove missing metadata or insufficient SELECT permission. |
| Approval | Approved partial scope this round | Original context `ee607dec-f43a-4946-9cab-5cd33d4d471c`, hash `756beb6149ae255aba4af6bf073d6f59f2a2180eee4c125a6bc8f4620a159834`. Re-adoptions changed mode policy without recollection or rebinding old tickets. |
| Transformation reading | Definitions retained; complete mapping proof missing | Existing code-reader retained seven Copy activities with explicit source projections and sinks, including a rowversion cast, but no explicit translator/mapping arrays. This is not proof of a faithful implicit column mapping. The diagnostic reader's own Copy definition request was refused. |
| Binding proposals to billingapp | BLOCKED | The declared `BillingServingSource` partition lacks a resolved stable binding; the complete source/warehouse/connection and mapping proof chain is absent. No names were guessed into bindings. |
| Live binding verification | Not admitted | No faithfully compiled complete proposal set exists. |
| Verified profile publication | Unpublished | No verified bindings. The metadata capture's full exact replay is separately blocked by recorded source fingerprint `d56658b7...` not being reconstructed from its recorded revision. No drift waiver. |

The diagnostic reader's POST to the Copy pipeline `getDefinition` returned HTTP 401:

```json
{"requestId":"a41a5f8d-7ee9-4562-8d8e-bead516f46cb","errorCode":"Unauthorized","message":"User is not authorized","isRetriable":false}
```

This establishes that request's refusal, not the exact additional grant needed. Code-reader evidence is identified separately from diagnostic-reader evidence. No identity or permission was changed. Onboarding used 34 physical requests: 27 metadata plus four authentication controls for collection, then one metadata plus two authentication controls for the reader probe. It used no investigation diagnostics or model calls. A scoped transport replay does not establish complete metadata replay. See [onboarding status](billing-onboarding-status.md).

## Fresh readiness command results

The six-stage command and prospective scoring gate are implemented and tested. They require hash-bound discovery, approval, transformations, binding proposals, reader verification and publication proofs. They refuse scoring when those proofs are missing; they do not erase historical investigation or archived acceptance results. Query-bound SNAPSHOT_UNVERIFIED remains independent and is not replaced by readiness.

Both commands ran against current source after the live cohort drained, with zero estate/model calls and native exit 2. Billing used the restored PIPELINE approval; the fixture used its original approved PARTIAL context. The fixture's missing/stale exhaustive index is not proof that every historical capability failed. Frozen wrapper wording is clarified in [the dated correction](round-fifteen-readiness-corrections.md).

### Billing: exact result object

```json
{
  "estate_reads": 0,
  "model_calls": 0,
  "pins": {
    "config_hash": "95d5340b0509c50ddf2a19308ee4bbdbf470ab92aa87e8b379552654e475e57a",
    "context_hash": "011cc23304f45c7f7250a69ce4d6e3ccdb12144d0ae678136e327240f4000206",
    "context_identity": "01c29e37-914a-4ec5-9a1c-23d3de0bfb71",
    "engine_hash": "b9868654a96b89e0d254ea813ff7889c6f57afbec86886e4a57b1065b63eae6b",
    "manifest_hash": "5c71237002607f11d7762485f258d0944a59ad5d89a5924bdc66f3f0fd92aecd"
  },
  "reason": "estate-not-fully-onboarded",
  "scoring": "NOT_SCORED",
  "stages": [
    {
      "reason": "DISCOVERY_NOT_COMPLETE",
      "stage": "discovery",
      "status": "BLOCKED"
    },
    {
      "stage": "discovery_approval",
      "status": "VERIFIED"
    },
    {
      "reason": "'transformations'",
      "stage": "transformations",
      "status": "BLOCKED"
    },
    {
      "reason": "'bindings'",
      "stage": "bindings",
      "status": "BLOCKED"
    },
    {
      "reason": "'reader_verification'",
      "stage": "reader_verification",
      "status": "BLOCKED"
    },
    {
      "reason": "'publication'",
      "stage": "publication",
      "status": "BLOCKED"
    }
  ],
  "status": "BLOCKED",
  "version": "estate-readiness-v1"
}
```

Full command, assessment time and pins: [billing receipt](round-fifteen-readiness-restored-billing.json).

### Original fixture: exact result object

```json
{
  "estate_reads": 0,
  "model_calls": 0,
  "pins": {
    "config_hash": "bc6ef21fdf3a2fef1cdcebdda0b48dee83c19c2bce9db567ac07a87689dbd172",
    "context_hash": "e3cce421b4b694b005d9643c40dd0c66035e7a35cf0b3af0495ae655ff3e9dd5",
    "context_identity": "a6b6b130-e955-432d-8433-f2f7203302a2",
    "engine_hash": "b9868654a96b89e0d254ea813ff7889c6f57afbec86886e4a57b1065b63eae6b",
    "manifest_hash": "5462332e8ad6e52334e0c733ec0eabc9d64bd8f51e9fc2ccccf3b2d628522e9f"
  },
  "reason": "estate-not-fully-onboarded",
  "scoring": "NOT_SCORED",
  "stages": [
    {
      "reason": "ONBOARDING_EVIDENCE_INDEX_MISSING_OR_STALE",
      "stage": "discovery",
      "status": "BLOCKED"
    },
    {
      "reason": "ONBOARDING_EVIDENCE_INDEX_MISSING_OR_STALE",
      "stage": "discovery_approval",
      "status": "BLOCKED"
    },
    {
      "reason": "ONBOARDING_EVIDENCE_INDEX_MISSING_OR_STALE",
      "stage": "transformations",
      "status": "BLOCKED"
    },
    {
      "reason": "ONBOARDING_EVIDENCE_INDEX_MISSING_OR_STALE",
      "stage": "bindings",
      "status": "BLOCKED"
    },
    {
      "reason": "ONBOARDING_EVIDENCE_INDEX_MISSING_OR_STALE",
      "stage": "reader_verification",
      "status": "BLOCKED"
    },
    {
      "reason": "ONBOARDING_EVIDENCE_INDEX_MISSING_OR_STALE",
      "stage": "publication",
      "status": "BLOCKED"
    }
  ],
  "status": "BLOCKED",
  "version": "estate-readiness-v1"
}
```

Full command, assessment time and pins: [fixture receipt](round-fifteen-readiness-restored-fixture.json).

## Clarification round

These are 51 retained runtime tickets drawn from nine independently authored ticket files, not 51 independent cases. The 18 owner-authored tickets remain separate and unrun. Six unplanned-rendering cases remain outside this continuation cohort. All outcomes are NOT_SCORED because billing is unready; no investigation accuracy is claimed.

| Mode | Runtime tickets | Final stopping reasons | Technical investigations | Physical estate requests | New harmful technical findings |
|---|---:|---|---:|---:|---:|
| PIPELINE | 18 | 9 catalog-change refusals; 9 unavailable offered choices | 0 | 0 | 0 |
| HYBRID | 33 | 32 cumulative step-cap holds; 1 provider timeout | 0 | 0 | 0 |
| Total | 51 | All retained actual ticket states HELD | 0 | 0 | 0 |

The first HYBRID continuation phase produced 27 step-cap holds, five new questions and one timeout. All five new questions received their second independent reply. There were 71 distinct author reply rounds and 85 question prompts in total; no runtime ticket received more than two author rounds. No replacement was run for the timeout. Human-wait exclusions are timestamp-bound; prior decisions, counters and the 900-second active-work limit were preserved.

The source catalog guard refused nine PIPELINE tickets before settlement because the original intake's catalog hash differed from the current catalog. This is distinct from SQL permissions or an ambiguous author reply. The operator's offer-label and retained-reply-consumption mistakes are preserved with dated corrections; the 037 correction added no third comment. No target was silently rebound.

All exact original questions, author replies, form facts, attempts, errors and outcomes are in [the final 51-ticket record](round-fifteen-clarification-final.md). The earlier [clarification checkpoints](billing-clarification-round.md) remain preserved. Coordinator CLOSED means an attempt completed, not that its ticket was closed or its question answered.

### Question legitimacy

| Mode | Avoidable | Legitimate | Necessity not established |
|---|---:|---:|---:|
| PIPELINE prompts | 39 | 8 | 0 |
| HYBRID prompts | 21 | 13 | 4 |
| Total prompts | 60 | 21 | 4 |

These are evidence-based reviewer judgments, separate from the unchanged author's raw 35 already-answered / 23 not-already-answered votes. The [85-row audit](round-fifteen-question-legitimacy.md) gives the input span/field, reasoning and separate presentation defects for every prompt. The four unestablished necessities concern an exact visual without complete candidate proof, report-wide plan navigation, a screenshot, and a single figure for a page-freshness question. Unknown necessity was not counted as legitimate. The 22 repeated PIPELINE prompts asked for literal facts already supplied in the first author reply; offer-mapping difficulty does not make that information absent.

Historical false duplicate-report premises (001/005), supplied report/page/visual facts (034), and already selected page/unique Collected Amount role (014/018) are named. Multi-card answers were kept as multi-card answers. A legitimate single-target requirement can still expose a mismatch with an overview question; it never authorizes choosing a card the author did not choose. No new intake repair or expectation change was made in this continuation phase. Round Fourteen's two harmful pure-agent fixture claims remain recorded separately; this round's zero is scoped to its new technical deliveries (there were none).

### Provider failure

030 ended `AGENT_ADMISSION_OR_PROVIDER_FAILED`: `APITimeoutError`, caused by `ReadTimeout` / `ReadTimeout`. The source SDK disables automatic retries; its explicit transport retry handles HTTP 429 separately. The timed-out attempt was preserved as an environment/provider failure, not a quality result, and its uncertain charge remains. No counter was refunded.

## Owner demo

One original-fixture A portal trial completed: `TRANSFORMATION_LOGIC / PARTLY_ANSWERED`. The checked input was 7,661 in L2 (REFINED); the output was 8,765 in L1 (SERVING), which matched L0 (SEMANTIC). The retained left join can multiply movement matches; the run did not prove actual duplicate matches or business correctness, read the application, or establish aligned served snapshots. Both outputs and all limits are retained verbatim in [the trial record](round-fifteen-owner-demo-trial.md).

The trial used four diagnostic slots, six SQL guards and three provider calls. Five separate startup/recovery controls make total demo physical usage 15, of which the investigation itself used 10. Procedure planner calls were one, distinct from three provider calls. Synthesis completed, a clearly labelled agent-operated comment was posted, and Agree closed the ticket. This is an operator trial, not independent owner acceptance or a general capability proof.

The isolated worktree, catalog and captures remain. Both guards use the same canonical live files:

- Dollar ledger: `D:\data_investigation_agent\.local\round-thirteen\model-spend.sqlite`.
- Physical/daily ledger: `D:\data_investigation_agent\.local\unknown-domain-v4\catalog.sqlite`.

Replay snapshots do not govern live admission. The [owner guide](owner-demo.md) has the actual single startup command and a tested read-only history command for after cutoff. Six screenshot images were surfaced in the conversation and the transcript retained; no local PNG/hash is claimed. Six demo operation tapes replay exactly. Its worktree remains on its recorded source `1f9914e9...`; later root fixes are not silently claimed to be installed there.

## Capture and replay

All 128 clarification operations are accounted for: **127 MATCHED, one MISMATCH, zero pending**. The set is 71 `form_comment`, 38 `agent_resume` and 19 `ticket_reply` operations. All 128 original tape hashes remain unchanged. The separate six demo operation tapes also matched. These are replay-fidelity results, not investigation accuracy scores. See [the full operation map](round-fifteen-clarification-replays.md).

The mismatch is clarification 030's `agent_resume` tape `c30646ee-b47b-4c88-aeef-beb6552b5de8`: `TAPE_REQUEST_BYTES_DIFFER`, while the recorded source fingerprint matched. Read-only code/event reconstruction identifies the likely difference in `CONFIGURATION` event 264, `event.cause_types`: the live `APITimeoutError` recorded two nested `ReadTimeout` causes; replay recreates only one. The rejected attempted bytes were not retained, so this is a reconstructed explanation, not a captured byte diff. The original failure, failed replay and clone are preserved; no source patch, tape edit, drift waiver or replacement replay was used.

The first parallel phase stopped both workers on that mismatch. A separate immutable disjoint plan then attempted only the remaining 12 independent operations, all of which actually matched. Nine private bookkeeping tests confirmed that a failed summary remains a mismatch without invented optional counters, while successful replay still requires zero estate/model/network requests and guarded connections. A missing success-only counter in the failed helper report is not evidence that a network request occurred. The independent captures were not abandoned merely because one replay failed.

Cold compression controls 10 through 15 covered 72 closed original catalogs, with native exit 0 and identical logical SHA-256 before/after. Cold control 16 was not used. Measured free space after all replay was 17,201,254,400 bytes. No live credit was consumed.

Original source, failed/partial evidence and tapes remain unchanged. Offline replay uses recorded-source fingerprints, denies network and shared-live-ledger connections including ATTACH, and creates separate replay clones. Closed captures/clones are compressed losslessly with logical SHA-256 checks. Further bounded disjoint compression was chosen instead of deleting evidence or lowering the disk floor; all controls have zero estate/model requests. DECIDED WITHOUT REVIEW: after the live cohort drained, two isolated offline workers were chosen instead of a much longer serial replay. Eight private coordinator tests checked disjoint coverage, duplicate refusal, single-writer aggregation, source and connection guards, and failure handling. Each child used a separate clone/result path and a stricter 14-GiB headroom guard; the estate floor stayed 10 GiB. Private coordinator changes do not alter engine source. Historical working-copy line-ending restoration and the separate metadata fingerprint blocker are disclosed rather than waived.

## Accounting and windows

These amounts are rate-card estimates from receipts and reservations, not an Azure invoice:

| Accounting | USD |
|---|---:|
| Settled receipt-based estimate, all retained history | 89.216827 |
| Uncertain upper bounds, 13 calls | 5.487445 |
| Conservative shared ledger total | 94.704272 |
| Guard | 190.000000 |
| Protected margin | 10.000000 |
| New-admission stop threshold | 180.000000 |

The 13 uncertain calls are the 12 preserved earlier calls plus this round's one timeout. No uncertainty was quietly converted to an actual bill. Initial conservative total was $87.703910; this round added $6.765449 settled estimates plus the $0.234913 timeout bound. HYBRID continuations initiated 115 provider attempts (114 with successful receipt accounting), 4,862,424 input characters and $6.727005 known estimates. Demo provider usage added three calls, 26,927 characters and $0.038444. Total new project-provider attempts: 118. Independent tester/orchestration chat activity is not presented as Azure project-provider usage.

| Window / cap | Retained ending counters |
|---|---|
| Existing estate pot | 2,641 / 4,000 physical slots; this round used 49 physical requests |
| Restoration reserve | 95 untouched; 1,264 spendable slots remain below the pot after reserve |
| Ordinary rolling 24-hour window | 685 / 3,000 at the retained ending live window; 2,315 available |
| Per-investigation diagnostic cap | 12 unchanged; demo used 4, clarifications used 0 |
| UTC 2026-10-12 model-call counter | 115 / 2,000 |
| UTC model input-character counter | 4,862,424 / 80,000,000 |
| UTC model output counter | 230,991 charged / 20,000,000; 920,000 cumulative reservation history preserved separately |
| Agent bounds | 12 cumulative decisions, 900 active seconds, 150,000 request characters unchanged |
| Disk admission floor | 10 GiB preserved; replay uses stricter headroom checks |

The daily counters include conservative failure treatment and are not an assertion of exact provider token usage. Active governor reservations were zero at the ending live window; the cumulative reserved count is not an active lease. No counters were reset and no old unowned reservation was released. The read-only dollar snapshot at 04:22:54 UTC is SHA-256 `27b597d70600715763f9dfa308d294b79b4d17d6ddd9341cadec716497613f52`. A subsequent read-only delivery check confirmed all shared dollar rows and charges still matched that ending snapshot; its receipt SHA-256 is `28ac7d32a38e851577e66a144de32add38905248ea5434ed320b40f649b7e3e3`. Both coordinators drained before restoration. PIPELINE was restored at 04:21:22 UTC to context `01c29e37-914a-4ec5-9a1c-23d3de0bfb71`, context hash `011cc23304f45c7f7250a69ce4d6e3ccdb12144d0ae678136e327240f4000206`, config hash `95d5340b0509c50ddf2a19308ee4bbdbf470ab92aa87e8b379552654e475e57a`.

## Cutoff, limits and delivery

All 51 first replies and permitted second replies ran before the live cutoff; none was omitted because of the deadline. The actual cutoff control at 04:31:38 UTC refused new live admission with `ROUND_FIFTEEN_DEADLINE`, before any provider/estate request, with model-ledger counts unchanged. Its receipt SHA-256 is `401f85a98ef90858fc7b3d40a97c18a19d6b7a9af6fbbddb3cd449d572ae480f`. After 23:30 Central, only offline replay, compression, records and push work continued.

Unfinished work is blocked work, not silently successful: billing's full metadata/mapping/binding proof chain and profile publication, exact reconstruction of its metadata-capture source, and a current exhaustive readiness index for the fixture. No new estate identity, permission, persistent credential, deployment, data or schedule was changed. Some tool failures retain only an exception type (029 includes ValueError without a retained message); no cause is invented for them. Remaining intake causes require design work around whole-page/multi-card questions, target/measure resolution and continuation capacity; this round did not patch tickets or golden expectations.

Full source regression: 3,410 PASS, native exit 0, on the frozen source. Hosted offline checks and the deliberately skipped live intake evaluation are reported separately. A historical CI metadata replay does not certify this round's failed metadata replay. Delivery correction: checkpoint `15db812` was initially pushed to a same-named remote alias instead of #423's head. It was subsequently pushed to `feat/round-ten-fifty-tickets`, and local upstream was corrected. No history was overwritten or branch deleted. All records are pushed to draft #423; it is not merged.
