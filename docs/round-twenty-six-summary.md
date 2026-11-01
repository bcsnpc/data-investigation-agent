# Round 26 — front door and providers

Started 2026-11-01 from main `188077989737446237b4aa01b6e07101470eaaad`, after the v0.25 release.

## Provider setup and benchmark

_pending_

## Intake, investigation and PostgreSQL

_pending_

## Dev and independent held-out measurement

_pending_

## Budgets, restores and release validation

_pending_

## Owner actions and open items

Owner stored the existing OpenAI project key in the platform Key Vault. Model listing and bounded synthetic Responses/tool/cache calls passed. Credit expiry remains unknown: the owner reply used the placeholder <date>. No key was printed or committed. The live benchmark and release remain pending.

### In-progress provider usage checkpoint

There are 31 saved benchmark outcomes at this checkpoint; this is not a quality score. Actual investigator call means and cached-input ratios are: Opus USD0.106269 / 69.94%; Astra-only USD0.182081 / 64.47%; Sol first leg USD0.034744 / 58.99%; Astra fallback USD0.257695 / 44.31%. Different unresolved paths and differing call counts make these cost observations, not proof of relative quality. Exact counts, costs, capture seals and the original common image are in `round-twenty-six-benchmark-usage-checkpoint.json`. Screenshot and standalone-summary calls have not yet been measured in this checkpoint; no zero-cost claim is substituted.

The benchmark remains on its original image. The next development image includes a generic cached query-layer contract correction and observational UTC timing, tested separately. The saved strict-schema hypothesis was not established by the captured requests. All prior outcomes are preserved. Physical-budget planning and an owner decision request are recorded in `owner-actions.md`; no ceiling has changed.

## Intake diagnostic checkpoint (2026-11-01)

The first model-only R22 dev intake diagnostic admitted 21/40; the second admitted 28/40, with 12 questions, 86 model calls and USD10.653160. Both used unchanged dev text and retained catalog metadata, with zero estate reads. These are admission diagnostics, not scored investigation results. Original results and provider journals are retained. See round-twenty-six-intake-dry1.json and round-twenty-six-intake-dry2.json.

Current authoritative November AI charge: Anthropic USD30.526751/150; OpenAI USD15.111366/180; combined USD45.638117. No pending exposure in either provider account at this observation. Historical usage was not reset.

The configured enrichment/evaluation cloud entry now uses the common provider surface, persists dispatch intent and returns saved status without resubmitting interrupted calls. Legacy Anthropic batch receipts retain their old route. Focused checks: 63 Round26 tests, 3 cloud enrichment tests and 8 prior cache regressions passed; full suite and live qualification pending.


## Selected intake checkpoint

Observed first-leg intake results: Astra28/40, USD0.123874/call,18.37%cached; Terra21/40,USD0.010282/call,86.74%cached; Sol28/40,USD0.024139/call,88.04%cached. Engine versions differ, and eight operational routes make no model call; this is not a controlled investigation benchmark. Sol selected by readiness first, cost second. One Astra fallback pass on13 non-ready/low-confidence tickets gives29/40 atUSD7.733820 combined, zero estate reads. Later Terra19/40 remains recorded.

The three investigator columns are Sol with unresolved-only Astra escalation, Astra-only, and Opus. All share selected intake and Terra helpers. First Sol launch failed before model dispatch due to the obsolete Opus-only cache-spec restriction; partial capture and failure are retained, unscored. Corrected specification plus fake Azure key-header coverage passed90Round26 tests; corrected image publication pending at this checkpoint.

The offline80route check now includes native declared continuations:59PATH_OPENED,8native operational,10questions,3rejected saved proposals; zero estate/model reads. This does not establish value correctness or full layer coverage.


Partial cross-vendor primary grading checkpoint: first two application tickets each earned2/2 in Sol-to-Astra and Astra-only, graded by Claude Sonnet4.6 Batch, harmful0; initial three Opus tickets earned3/3 with Sol primary, harmful0. These are partial benchmark results and do not select the investigator default. Anthropic batch grading costUSD0.015069/call for the Sol-cascade sample andUSD0.015386/call for Astra-only; OpenAI Sol synchronous gradingUSD0.022148/call, cached-input0% on these one-call evaluations. Native usage and pricing class are recorded in round-twenty-six-initial-crossvendor-grading.json.

Intake cascade costs98generation calls(63Sol including failed-original costs,35Astra fallback),USD0.193346 per ticket versus historical Astra-onlyUSD0.266329. Fallback cached-input85.43%. Engine-revision differences remain disclosed.


November owner-approved request increase applied and read back 2026-11-01: total14,500 / investigation11,905, SCAN2,500 / restoration95 and model caps unchanged. At readback3,054total /2,808INV /228SCAN /18REST;77restorationremaining. Prior checkpoint saying no ceiling changed is historical. Receipt: round-twenty-six-request-increase.json. Corrected focused tests:103Round26 and17build-phase passed; the prior November9,000 assertion was updated for this explicit owner decision.

Independent partial primary grading now Sol-to-Astra3/11, Astra-only5/11, Opus10/11; harmful0 in these subsets. Subsets are incomplete and differ by one case, so no default-investigator choice is made. Two further five-case Claude batch submissions use batch pricing; five further Opus outputs are being graded by OpenAI.


Usage checkpoint updated2026-11-01T21:47Z:18selected saved outcomes per investigator column; answers are not grades. Actual mean investigator costs: SolUSD0.031679/call (60.51%cached), its Astra fallbackUSD0.239186/call(46.30%cached), Astra-onlyUSD0.184910/call(63.33%cached), OpusUSD0.098992/call(69.46%cached). Original environment-failure charges stay in the authoritative ledger and are excluded from these selected-outcome call means. See round-twenty-six-benchmark-usage-checkpoint.json.

Next-development build891a7ef1 failed one obsolete November9,000 policy assertion;438other focused checks passed,28skipped, publication refused. Assertion corrected for the explicit owner November14,500/INV11,905 approval, with a December9,000/INV6,405 assertion; four local policy tests passed. Replacement focused build source76197296 submitted; benchmark image remains unchanged. Native owner controls separately verified billing3ACTIVE/600 and temporal historyON with earliest retained start2026-10-23T22:43:47.9434148Z; these are authoring facts, not investigator evidence. New v5 wording remains un-authored.


Next-development image source76197296 published assha256:3c3cb713064b52b30cd0cc6753a4cd3edd4d79b3e42dee9f98c21f770bea8975. Hosted focused439PASS/28skip plus107Round26PASS, no full-release qualification. Current benchmark retains image1e0016e4. Eight superseded automatic CI runs were cancelled to free runner slots; latest checks and explicit image build preserved.

Serial benchmark continuation is active behind the static queue. It admits no fault mutation until all77non-deferred static outcomes exist, rechecks the retained uncertain quantity original before one prepared labelled replacement, then runs approved failure/history/latency/access/waiting controllers with guarded restores. Stale remains pending its native UI control. No new v5 tickets have been authored: the40-ticket20FORM/20TEXT writer plan is prepared only, with current-native-fact and ID checks required before calls/sealing.
