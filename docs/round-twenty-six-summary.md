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
