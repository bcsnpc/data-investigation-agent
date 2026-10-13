# Round Eighteen hard-coding audit

Audit date: 2026-10-13 UTC (owner local date 2026-10-12). Offline only; no estate,
model, identity or accounting changes. This audit separates the installed
investigation product from reference-estate builders and historical experiments.

## Findings and disposition

| Finding | Location and disposition |
|---|---|
| Prompt teaches a real fixture report, page, measure and expected number: `Round Ten Visual Variety`, `Global card`, `Handled Quantity`, `8765` | Removed from `scripts/investigator/intake_extraction.py`. The interpretation rule now states how setup identifies the primary referent without carrying any estate example or expected answer. Original ticket bytes/goldens/tapes remain unchanged in acceptance evidence. |
| Native workspace, model, table, server and identity values | Already live in the validated `estate-manifest-v1` configuration or collected metadata. The runtime audit found no reference-estate GUID/server/table/name literal in installed engine/adapters/CLI/UI after the prompt fix. |
| Historical fixture manifest mixes portable declarations with local absolute paths, fixture-state arithmetic and observed collation receipts | New `estates/fixture.json` uses the existing contract, repository-relative storage paths, declared layers/identity references, and no copied historical verification or authored result. `infra/estates/fixture.json` remains unchanged for existing tests/tapes. |
| Billing installation configuration existed only in local round artifacts | Added `estates/billing.json`, derived from the retained Round Sixteen collection manifest. Its one declared semantic layer and explicit unresolved-binding limitations are retained, not expanded into inferred paths. Paths are relative and receipt/fixture-state fields are omitted. |
| Audit producer requires `run_id`, `pipeline_name`, counts and timestamp fields | These are the engine's existing load-accounting interchange contract (`load_accounting.COLUMNS`), not guessed billing/fixture table names. The audit *object* is declared by configuration and types are checked against discovery. A client audit source must expose this contract; arbitrary audit-column mappings remain unsupported. |
| `reason_code` matched the old fixture-column regex | It is also a generic engine error/evidence contract key. Not an estate assumption; retained. The old platform literal debt ratchet remains unchanged, alongside the new estate-specific zero-debt test. |
| `8765` in the historical evidence HTTP server | TCP port default, not expected data. The scanner exempts only the explicit `add_argument('--port', type=int, default=...)` form from expected-number checks. No filename-wide exception. |
| Azure/Fabric/Power BI names, service URLs and native schema keys | Platform protocol vocabulary belongs to adapter code. Retained; the new test allows it while rejecting specific estate identities even inside adapters. Existing above-adapter platform-debt checks still apply. |

## Historical and fixture tooling — explicit portability boundary

These files are **not** called by the installed investigation entrypoints. Their
estate-specific behavior is retained as fixture construction or historical
evidence, rather than misrepresented as a portable client runtime:

| Tooling | Estate-specific content |
|---|---|
| `build_powerbi_model.py`, `build_powerbi_reports.py`, `infra/powerbi/` | OrderOps deterministic IDs, report and measure definitions. Authored fixture data. |
| `fixture/apply.py`, `infra/fixture/` | Seed table substitution, source-table selection and report/pipeline construction. Explicit fixture deployment tools. |
| `cross_layer_investigation.py`, `investigation_query_worker.py` | Old fixed order path, `app.orders`, Order Count/Net Cash, fixed layer names. Historical experiment, not an installed manifest investigation route. Not generalized in this round. |
| `deploy_snapshot_publication.py` | Old OrderOps snapshot notebook naming and publication tool. Not an investigation reader. |
| `validate_metadata_inventory.py` | Validates the authored OrderOps model against fixture definition. Test/fixture validation tooling. |
| `audit_lineage_tape.py`, `revise_conversational_oracle.py` | Historical audit/oracle tooling with named fixture examples; not imported by the runtime. No oracle or expectation changed. |
| `business_demo.py`, `apps/business-demo/`, `apps/order-portal/` and early lab scripts | Authored order-domain demo/application and its Net Cash rules, not the current investigator workspace. Kept as fixture/demo artifacts. |
| `.local/round-*` scripts and sealed acceptance inputs | Historical execution/evaluation recipes and evidence. Not imported, rewritten or copied into runtime; preserving these is required for replay. |

No claim is made that every historical script has become estate-neutral. A
future import of that tooling into an installed CLI is included in the new
transitive scan and will fail if it introduces known estate values.

## Enforcement and verification

`scripts/test_estate_neutrality.py` scans the entire investigator package,
including adapters, public investigation/metadata/readiness CLIs and their local
imports, plus the current workspace/admin/evidence UI (358 files at the initial
audit). It rejects reference-estate GUIDs drawn from the example configurations,
distinctive names, table/server/identity labels, authored expected totals,
fixture-family selectors and known absolute working-folder forms. Ordinary
business nouns and protocol words are allowed. This catches known literals;
it is not a proof that an arbitrary new hard-coded string is estate-independent.

The four initial tests pass: runtime scan, positive/negative scanner controls,
both example manifests accepted by the existing closed loader/projector, and
the primary-referent prompt retaining its target-preservation rule. No network
or secret reads occur in these tests. A configuration typo still fails load;
there is no second schema or hidden default estate.

The prompt change invalidates a current-source prompt/replay freeze; archived
tapes and expectations are untouched. Model quality and current live readiness
are not claimed by these offline tests.
