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
