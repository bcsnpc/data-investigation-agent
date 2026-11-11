# AI providers â€” Round 26

Status: implementation in progress; no new provider has earned investigation support yet.

Azure budget integration is tested through the complete structured-step interface with a fake endpoint and a test-owner-funded offline account. Its installed allowance is zero: no Azure model spend or deployment is approved in this round. A client must explicitly configure its Azure model budget and provision its ledger account before dispatch; the worker never raises either. This does not debit OpenAI credit or alter either approved November allowance.

The independent guided writer now follows the same primary-target contract as intake: one report, measure or table, with a report required only for page/visual selection. Its visible catalog may contain table names and IDs, but not definitions, engine code or expectations. Measure/table-only wire outputs are validated against the actual intake schema. Eight independent-evaluation tests pass; no v5 wording or sealed expectation was changed by this correction.

| Provider | Transport | Live access | Same-dev benchmark | Status |
|---|---|---|---|---|
| Anthropic | Existing Messages adapter; cache_control retained | Existing Key Vault reference | pending Round26 | prior live path, Round26 pending |
| OpenAI | Responses, client-side function calls; normalized usage | key verified; model-list HTTP200, synthetic tool call passed | pending | offline-tested only |
| Azure OpenAI | Configured Azure Responses endpoint | not deployed or requested | not run | fake-endpoint tested only |

One content contract carries text, images, tool calls/results, schemas and call IDs. OpenAI input-token totals include cached reads/writes; Anthropic reports ordinary inputs separately. The normalized usage keeps those distinct so rates do not double-count input. Unknown usage stays charged. Switching vendors does not reset the $3 actual-use ticket threshold. Provider monthly accounts remain independent.

Official implementation references, retrieved 2026-11-01: [function calling](https://developers.openai.com/api/docs/guides/function-calling) and [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching). Cache capabilities depend on the selected model. Explicit caching is an opt-in configuration, not inferred merely from a model name. Model availability and prices will be pinned after the owner's model-list check; no assumed model is dispatched.

Cross-provider grading, all component routing, stable-prefix assertions and provider benchmarking remain pending. Existing unredacted tapes and sealed expectations remain unchanged.


2026-11-01: `gpt-6-astra` is the strongest accessible model selected for the required OpenAI benchmark, per the [official model guide](https://developers.openai.com/api/docs/guides/latest-model). Standard rates pinned from the [model card](https://developers.openai.com/api/docs/models/gpt-6-astra): input10USD, output50USD, cached-input1USD and 30-minute cache-write12.5USD per million tokens. Larger-context premiums must be bounded before dispatch. Synthetic transport check0.001660USD; transport access is not investigation quality. Owner confirmed key storage; expiry is still a placeholder, so no exact expiry is asserted.


## Owner step-cost steer, 2026-11-01

Use GPT-6.1 Terra for intake extraction, screenshot reading and standalone summaries; reserve Astra or Opus for investigation reasoning. Both benchmark columns use the same helper configuration. Primary grading remains cross-vendor, on a different configured model. Terra is accessible in the recorded project model list and supports image input and tool calling. Official rates: ordinary input USD1/M, cached input USD0.05/M, 30-minute writes USD1.25/M, output USD5/M: https://developers.openai.com/api/docs/models/gpt-6.1-terra . No secret or identity changed.

Observed before this steer: first intake diagnostic 75 Astra calls/USD4.407475, mean USD0.058766 per call, cached-input ratio33.63%; second86 calls/USD10.653160, mean USD0.123874, cached-input ratio18.37%. These are measured usage, not future estimates. The synthetic repeated-prefix check reached98.46% on its second call; it is not the workload ratio. Investigation, screenshot, summary and grading calls have not yet run in Round26, so their actual per-call cost is not established. Native per-call usage and actual cost will be grouped by step/model in the final report.

Intake now places deterministic retained catalog metadata before the cache breakpoint, with ticket tokens and ranked candidate references afterward. A regression asserts an identical prefix across different tickets and retries. Original capture bytes remain unchanged.


Owner refinement: measure Sol intake as well and pick readiness before cost. An optional one-pass configured intake fallback is recorded per ticket (model, status, confidence and resolving model). Unresolved investigator escalation retains the original evidence/queries, uses a fresh model-facing handoff instead of another model's opaque reasoning state, and divides the existing15-tool/900-second allowance rather than doubling it. Per-call normalized output now names INTAKE, INTAKE_FALLBACK, INVESTIGATOR, INVESTIGATOR_FALLBACK and the other AI steps. Full benchmark qualification remains pending.


## Superseding selection and live checkpoint

Owner's latest readiness-first rule selects Sol intake:28/40 atUSD0.024139/call and88.04%cachedinput, tied with historical Astra28/40 atUSD0.123874/call and18.37%cachedinput. Terra21/40 atUSD0.010282/call and86.74%cachedinput remains the cheap screenshot/standalone-summary model. Cohort engine revisions differ; this is observational selection, not an isolated quality comparison. Sol plus one Astra intake fallback measured29/40,totalUSD7.733820,zeroestate reads. See the [intake comparison](round-twenty-six-intake-comparison.md). This replaces the earlier Terra-first default while retaining the bounded fallback capability.

Three same-image investigator columns are now running: Sol with Astra only after unresolved status, Astra-only, and Opus5.5. The first corrected static ticket delivered answers in both OpenAI columns: Sol-to-Astra5calls/USD0.415137, Astra-only4calls/USD0.436823. These are ungraded observations, not earned support or correctness scores. Native per-step cache/cost and evidence remain saved; the earlier pre-dispatch cache-spec failure is retained separately.

Azure key authentication now has a fake HTTP test for the documented api-key header, distinct from OpenAI Bearer authentication. [Microsoft's Responses REST reference](https://learn.microsoft.com/en-us/rest/api/microsoft-foundry/azureopenai/responses?view=rest-microsoft-foundry-v1) documents this distinction. Azure has no live deployment in this round and remains fake-endpoint tested only.


Synthetic helper transport check (2026-11-01, not an estate score): Terra screenshot extraction USD0.000753/call; corrected structured summary USD0.000535/call. Original summary returned valid prose rather than its required tool record, retained atUSD0.000502; this was not a token-limit failure. The shared helper now explicitly requests the structured tool and permits one bounded retry only after a returned non-structured response; transport exceptions are not automatically resent. All three calls were below useful cache size and had0cachedinput. Receipt: round-twenty-six-helper-step-costs.json.


Official OpenAI documentation rechecked2026-11-01: [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol) lists USD2ordinary input/0.10cached input/2.50cache writes/10output per million tokens. The [prompt-caching guide](https://developers.openai.com/api/docs/guides/prompt-caching) specifies a1,024visible-token minimum, explicit breakpoints,30minute default writes and usage.input_tokens_details cached_tokens/cache_write_tokens. The implementation and recorded rate cards retain these distinctions. Tiny synthetic helper prompts below that minimum are not cache-hit tests; workload ratios use summed native cached-input / total-input counts. Documentation does not replace measured quality or project model availability.


## AWS Bedrock (Round26, Nova helper steps only)
`provider=bedrock` selects the boto3 Converse adapter. Model IDs, rate cards and us-east-1 live in deployment configuration. Three versioned KeyVault references are required under `secret_reference`: access_key_id, secret_access_key, region. Credentials are explicit in-memory SDK arguments; no profile/environment/instance credential fallback. The SDK makes one transport attempt; the outer bounded retry owns reservations and refuses billing/auth retries. Native tool-use IDs/results, stop reason and input/output/cache-read/cache-write counts normalize into the common provider contract and actual-usage ledger. Unknown usage stays charged. A non-resetting5USD Round26 account bounds all AWS steps. Invocation passes the same configured gateway before dispatch and at SDK before-send. Models/tools/region/URL must match its exact allowlist. Nova is refused for submit_finding/investigation in this round.
Claude IDs (including profile/ARN variants) are refused unless the owner explicitly sets BEDROCK_ALLOW_CLAUDE=true; it stays false. That future switch still requires an explicit rate/model/gateway policy and IAM scope. No Anthropic Bedrock access request or invocation is authorized now. Approved current invocation IAM resources cover Amazon Nova Micro/Lite/Pro only; no AWS Marketplace access.
[Converse](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) uses InvokeModel IAM permission; ConverseStream uses InvokeModelWithResponseStream. No fake Converse IAM actions are added. [Nova caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) uses system/messages cachePoint, minimum1K and maximum20K tokens, five-minute TTL; tools cachePoint is not supported. Cache hits are measured, never promised. Tiny one-call smoke has no expected cache hit. Pricing and live smoke pending native setup; no zero-cost/support claim. [AWS pricing](https://aws.amazon.com/bedrock/pricing/).


Bedrock live checkpoint2026-11-02: owner supplied existing dia-bedrock keys inKeyVault; agent skipped IAMsetup and created no key/role. STS verified the exactuser ARN; owner logout returned no session and no isolatedlogin cache exists. Nova Micro tool smoke PASS,1toolcall,433input/61output/cache0, actual normalized24microUSD (USD0.000024),0estate reads. Native AWSPriceListus-east-1 publication2026-10-30: Micro per1Minput0.035USD/output0.14/cache-read0.00875/cache-write0; Pro0.8/3.2/0.2/0. Non-default zero-write pricing is explicitly supported/tested. No live cache-hit claim on this tiny singlecall. Receipts:round-twenty-six-bedrock-smoke.json.

Owner-authorized Bedrock Haiku credit test (one wire dispatch, UTC2026-11-02): anthropic.claude-3-haiku-20240307-v1:0 returned HTTP404 ResourceNotFoundException after23.732s. Prompt Reply OK., maxTokens20. No alternate-model attempt; Claude guard restored. A preceding local helper failure never reached HTTP and is preserved separately. Token cost and credit coverage were not established; owner checks Billing -> Bills after24h. See round-twenty-six-haiku-credit-test.json.


## Round26 frozen-engine closing measurements

The completed earlier-image provider benchmark is unscored for held-out quality: Sol→Astra13/40 (harm1), Astra-only28/40 (harm0), Opus34/38 (harm0; two stale cases not admitted). On the common26static cases:5/26,19/26,23/26, all harm0. Opus is the provisional quality-first choice, not a fully qualified40-case default. Its current frozen-engine free-text calibration and v5 gates are reported separately; no earlier score is substituted for them.

Final saved-outcome benchmark accounting: Sol reasoning125calls, USD0.028479/call,61.27%cached; its Astra fallback63calls,USD0.223914/call,45.47%cached. Astra-only180calls,USD0.152410/call,65.00%cached. Opus162calls,USD0.091293/call,68.67%cached. Column total means including recorded helper steps:USD0.442175,0.685846,0.390287 per ticket respectively. Earlier timestamped18-outcome checkpoints are superseded by the full saved-outcome usage report. Environment-failure charges remain in the ledger but are excluded from these selected-outcome means.

Sol remains the intake choice by ready rate then cost (28/40 tied with Astra, cheaper); one Astra fallback raises observed readiness to29/40. Terra remains screenshot/summary helper. Tiny helper calls show zero cached input, not a cache-hit claim. Azure OpenAI is fake-endpoint tested only, not live-qualified. Nova remains helper/grader only with Claude-on-Bedrock guard false; the single approved Haiku404 does not prove credit coverage.


Round26 final calibration,2026-11-11: Final frozen e59 calibration did not qualify a default: reviewed2/10,harm2 (official2/10,strict2/10), despite earlier unequal-denominator Opus benchmark34/38. Common intake still uses Sol then Astra. In calibration22Opus calls averagedUSD0.112025 and66.32%cache;14Sol intake calls0.048898/71.77%;8Astra fallback0.290582/73.41%. Investigation AI total5.473769, grading/audits separate. No v5 and no further dev loop; no new production/default qualification is claimed.
