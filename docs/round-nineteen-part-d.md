# Part D ? change detection and final cloud retry

2026-10-13. Incremental collection, content fingerprints, temporal history, stale-verification invalidation and bounded graph APIs are implemented. Scheduled runtime-query, refresh/run/Delta-history collectors remain explicit gaps, not freshness facts.

## Actual recorded-version test

The real retained report definitions from contexts `3ae7607b-5a5e-46c6-8e1b-195dbabc9cae` and `e920dda4-d5c8-4a95-b9e9-a600386ae3d5` were loaded offline with their original context hashes. Exactly one of sixteen parts changed. The graph returned the date filter September14, September15, then September14 on revert. Original content/provenance and unrelated model history were preserved. Receipt SHA256 `617025b92881d66aebebcf1a64ed5fd80fe3d3f7e68ad7c4e06651acd75d8d30`; full details in `round-nineteen-retained-definition-change.md`. This is not a live recollection or estate mutation.

The live mutation/revert test was not admitted: the dedicated reader cannot fetch the baseline report definition (HTTP404 EntityNotFound). The approved publisher was not substituted for this reader. No estate data, report or model changed during Part D.

## Final permitted cloud retry

The retry starts from the first failed attempt's retained catalog and the matching current PostgreSQL model, not an edited receipt. The fresh input ZIP SHA256 is `6b3a0817fdf6b72827a02b22c59d3a840fcc8aab3a7bf1214bb558260e437b36`; identity PUT/GET readback matched. Image `ef3159583b79858138c9c04ff57324f40ee9e21b` passed all eight hosted cloud shards; digest `sha256:d099784882da99836982b8397295dee645c512fcc5eddff922cf0418736af1cd`.

Preparation `job-dia-worker-ih0acng` completed with zero estate/model requests. It produced context `815a6dd1-5654-4e95-96f4-6a2708186232`, hash `6902ea48aeacf15490c035e0e3b193c5f3255ac0e762f629984292a5d5b31a68`, approval config `e13b215f2649fb0e46b2b383fd88ec69961bce551a5a00ded8ff9eef2d95a234`. Output ZIP SHA256 `801106e2c3675a90ea5b72fdc1a3df6dfb22329f04479e110c03429c871db7c8`; reviewed candidate SHA256 `588f9bf5b28ce5000988a8909eb15928d4f52aab75be370f749d598148f12926`.

Read-only admission review confirmed exact current model, budget-policy hash and no open reservation. Eighteen bindings/two catalog reads require40verification probes under the unchanged40cap. Investigation cap12 stays separate. Optional source prewarm is recorded as CONTROL with a240-second worker deadline and consumes physical allowance; it is not an investigation diagnostic. `job-dia-worker-62ij1pe` is the single permitted final verification/demo attempt. No further replacement is authorized in this round. Its terminal result will be appended.

## Scheduled scan deployment

Prepared exact PATCH to existing `job-dia-worker`: every six hours UTC (`0 */6 * * *`), .5vCPU/1GiB,600seconds,parallelism1,zero retries, exact image digest above. Only two missing public gateway identity variables are added from the successfully executed scan template. Existing managed identity, resource group and platform stay unchanged. Shared policy pins bound both estates to60+30physical requests per execution and the existing pot/reserve/rolling guards; the schedule does not renew the pot or silently adopt another round's policy.

Before apply, the script re-reads the unchanged existing job and requires the verification execution to be terminal. Exact PATCH SHA256 `c83072bd6cdffb74dacd0fd50d3f6cd2d5a2ddc0b24c42b6d9f37e6fc0bbda1d`. Configuration and provisioning readback are required; plan alone is not a deployment claim.

Retail source: South Central US active CPU USD0.000024/vCPU-second and memory USD0.000003/GiB-second, retained `container-apps-retail-prices.json`. At120executions/month the bound is36,000vCPU-seconds +72,000GiB-seconds =USD1.08 gross. This fits within20%of the documented subscription free compute grants, but existing consumption is not assumed zero. With prior conditional platform13.74 + full transfer allocation4.50 + controls0.50 + storage0.05 + compute1.08, the conservative allocation isUSD19.87/month, below20; no new paid resource. This is an estimate, not an invoice or promise of free operation.

## Terminal results, 08:47 UTC

Final retry `job-dia-worker-62ij1pe` ran08:34:15?08:42:43 UTC and returned **VERIFICATION_STOPPED** with `ValueError: VERIFICATION_PREWARM_SOURCE_NOT_DECLARED`. Zero physical/control/verification/diagnostic/model requests were made, and no reservation remains open. Result ZIP SHA256 `00ab7e48ee015de1ffe975e6d4c39694eee61c6d5256c63d89f53fe07a4b52e0`; tapeSHA256 `a6bc6e8c131f693000f7fe4cc7f00685fc6b72a55b60632ffa5cd0c4a0ceb67a`. The successful container status means it packaged its failure, not that verification passed. Exact verification replay/readiness/demo were not reached. No replacement attempt.

Cause: the operator selected the manifest's serverless application asset for prewarm, but none of the18 binding proposals uses that application source. Their four source locations are retained OneLake Bronze/Silver movement/rate tables. The guard correctly refused an out-of-batch source; no application connection was attempted. The offline admission plan checked prewarm shape but missed that cross-reference. This is an input/preflight defect, not a permission or Azure outage finding. Original input/spec/capture stay unchanged.

The existing job now reads back **Schedule**, cron `0 */6 * * *`, timeout600seconds, retry0, .5vCPU/1GiB, same managed identity; provisioning **Succeeded**. No new resource or role. Exact proposed template matches the returned template. Azure adds null inactive manual/event trigger fields; every declared configuration field matches exactly. The PATCH CLI returned exit0 with no JSON body, causing the operator decoder to raise; the PATCH was **not repeated**. An independent GET established applied state. Both the initial strict representation mismatch and the final semantic readback are retained. Final receipt `schedule-final-readback.json`; beforeSHA256 `d1bd23cb08526751f1070390a9bbd8ac69608124a7f9a4e4525a2c44a6964fe0`, afterSHA256 `1c87845f4dc2ecd18cef80da0dbacb4528a46a1f490eb4bd67ce053263590cf3`. First timed execution has not occurred; the equivalent two-estate manual scan is the live evidence.

At08:47:05UTC: round36/1500physical (6SETTLED,30UNCERTAIN retained provider failures), rolling312/3000, reserve95untouched. Two actual model calls costUSD0.088833; one additional pre-dispatch planner reservation remains conservatively UNCERTAIN but settled, with no model charge. Shared modelUSD108.046558, ceilingUSD132.957725, protectedUSD10. No open reservation. Archive controller exited afterfour bounded batches; all original receipts retained.

Offline correction after the terminal failure: retained-source preflight now runs before PostgreSQL candidate publication and before capture/usage reservation. A prewarm request cannot be admitted without its source scope being resolved, and unrelated manifest assets still refuse. The actual failed inputs reproduce the refusal offline; a separate in-memory prospective spec omitting the unrelated prewarm field plans 18 bindings/40 probes. No new input was published and no live retry was run. See `round-nineteen-prewarm-admission.md`. Engine changes require new pins for any future verification; the scheduled scanner remains on the separately tested ef31595 digest.

Final cloud-focused regression after the preflight correction: **85 passed, 4 skipped, 16 subtests passed**, 21.82 seconds with parallel workers. Earlier 20 targeted checks and 201 claim tests also passed. No new live verification or model call followed the correction.


Dated closing-CI correction, 2026-10-13: workflow 38372381714 on 30cb27e replayed inferred 15/15 but archived 7/15. Eight archived cases stopped before events because the current replay harness expected `metadata_config.validate_config`; their historical engine validates inline in `load_config`. Fix c4602de preserves that original validator and imported aliases, adapting only lexical path joining during replay. Ten portability regressions pass, including original validation refusing invalid configuration. No tape, expectation or historical engine bytes changed; zero estate/model calls. The full thirty-case hosted rerun is pending.


Final CI result, 2026-10-13 09:38 UTC: corrected source `c8e4bb1` passes archived **15/15** and inferred **15/15** in [workflow 38375299019](https://github.com/bcsnpc/data-investigation-agent/actions/runs/38375299019), with zero physical/network/model calls. All 25 checks pass; image publication is intentionally skipped. Original failure retained above; no tape or expectation changed. This confirms historical replay compatibility, not the unearned live demo or path-verification targets. This closing follow-up changes records only.
