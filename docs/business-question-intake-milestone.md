# Business question intake and reviewed investigation scope

PR #186 is merged. This grouped milestone is tracked by [#187](https://github.com/bcsnpc/data-investigation-agent/issues/187).

Users can now describe a report issue in the local v2 workspace before selecting technical fields. A separate LLM call uses the enabled onboarding catalog to suggest one model, metric and bounded set of filters, or ask a clarification. The suggested scope fills the existing form. The user reviews it and explicitly starts the existing governed investigation; intake itself never queries Power BI or SQL.

This advances Phase I alongside the still-open D/H proof prerequisites. It does not resolve exclusive publication, shared-generation or effective report/RLS proof, and it does not mark Phase H complete.

## What is implemented

- Catalog-only structured resolution with no metric whitelist or executable query output. Names of retained reports, measures, supported columns and current reviewed business definitions are data supplied to the resolver. Credentials, data rows and full DAX expressions are not supplied.
- Typed filter validation against the selected model, explicit bounded scope, verbatim question quotes for metric/filter provenance, unknown-ID rejection and clarification for ambiguity. Quotes establish where a suggestion came from; they do not certify its interpretation.
- Durable question records and a maximum four-turn clarification chain. Questions are bounded to 2,000 combined characters; intake catalogs to 12 models, 200 measures, 300 supported columns and 60,000 serialized characters. Oversized catalogs fail explicitly instead of silently hiding candidate matches.
- Request-key idempotency, pre-dispatch shared planner reservations, conservative usage settlement and no automatic provider retry. Azure token counts use the provider usage object; response IDs/provider bodies are not persisted.
- Saved status and the 20 most recent questions, including after restart. A reserved response can be explicitly held without refunding its allowance or reissuing it. A late provider result cannot replace that hold. Loopback HTTP requests use threads so a bounded intake call does not block history/status requests.
- Metadata/engine/config/expiry checks before adopting a suggestion, including a second catalog check during preview. Manual scope edits drop the AI-proposal association. Saved sessions retain original question and quote provenance alongside the same business/technical evidence.
- Local workspace UI, authenticated API, regression tests and complete browser verification in one change.

## User flow

1. Open the existing local workspace and enter a question, including the metric/report name and exact selections.
2. Select **Find metric and filters**. This uses the configured LLM allowance; it does not query business data.
3. Answer any clarification. A suggested scope is not a finding or an execution approval.
4. Inspect the populated metric, filters and optional breakdown, then select **Review scope**. Edit manually if needed; manual edits lose the AI-proposal provenance.
5. Select **Start investigation**. The existing adaptive runtime chooses admitted read-only checks and both views display saved results.
6. Reopen questions or investigations from history without re-querying. A paused/uncertain question is not automatically retried.

The existing `serve_investigator_workspace.py --live --usage-policy ... --azure-settings ...` configuration enables both intake and investigation. History-only hosts cannot make new intake calls. This remains a local single-operator workspace, not a hosted multiuser service.

## Validation and live observations

All 822 regression tests passed on the final implementation. Twenty-seven focused tests cover: proposal-to-runtime integration, clarification, typed filters, catalog bounds, malformed output, unknown IDs, missing quotations, shared allowance, Azure usage normalization, duplicate/concurrent requests, crashes, explicit holds and late responses, stale/disabled/expired contexts, tampering, manual edits and API authentication.

All 19 browser checks passed. The full browser workflow exercised a question, clarification, populated boolean filter, reviewed start, context-aware results, saved question history and manual provenance removal. Browser data/LLM responses were injected; these are UI integration checks, not native semantic truth. Artifacts: `.local/question-intake-browser-final.*`.

Separate live Azure LLM checks used a copy of the retained onboarding catalog: 25 measures, 87 supported columns and three report names. Net Cash/USD was proposed; an unspecified metric with ?last week? required clarification. An unknown-metric request returned no usable provider response and was held, not retried or treated as a successful clarification. All three intake checks made zero data queries. These preliminary checks preceded the final usage/adoption fixes; their limitations are retained rather than omitted.

The final frozen implementation completed the live business-to-native flow using the existing isolated Import fixture and dedicated reader:

- Question `572ddcae-96cd-4c70-a0dd-8e1df2fc195f` selected a newly named catalog measure and boolean filter through the real Azure LLM, with no expected values in the question or resolver input.
- Reviewed start created session `aedeffed-e794-432c-b14a-6fda5c8877e0`. The adaptive LLM chose parent, contextual child and contextual base reads. All three Power BI values were 2, retained with reader identity and calculation context.
- Four LLM calls total (one intake, three adaptive) and three native queries. The final result remained insufficient evidence for a verified cause.
- Replaying question submission, start and saved history used zero provider calls, with an unchanged outcome hash. Engine fingerprint stayed unchanged during this final run and replay.

Final live artifacts: `.local/question-intake-final-freeze.json`, `.local/question-intake-end-to-end.json`, `.local/question-intake-end-to-end.sqlite` and `.local/question-intake-replay.json`. The end-to-end fixture catalog comes from the operator manifest, not a newly scanned report. The separate catalog-only tests used retained onboarding metadata. Neither establishes native hidden-family acceptance.

No Azure SQL queries, SQL quota changes, fixture publication/refresh/permission changes or deployment occurred in this milestone. Seven LLM attempts were made across preliminary catalog checks and the final end-to-end flow; the earlier unusable provider response remains recorded. Generated evidence, question databases and credentials stay under untracked `.local/`.

## Remaining work

1. Enforce controlled publication/shared generation and verify effective report identity/context. Add supported causal verifiers and pass the complete eight-family Phase H suite; current diagnostics are not a general cause certificate.
2. Add screenshot/attachment interpretation and explicit report/page/visual context acquisition. This intake reads text only, does not open URLs, and does not infer hidden filters or relative-date boundaries.
3. Finish hosted onboarding, multiuser authorization, reviewed v2 handoff/triage and Azure v2 deployment. Existing Azure bounded-v1 deployment is unchanged.

The resolver can make an incorrect suggestion. Catalog/type checks and quoted provenance narrow its output, while human scope review remains mandatory. Report names assist model/metric selection; they do not bind a complete report execution context.
