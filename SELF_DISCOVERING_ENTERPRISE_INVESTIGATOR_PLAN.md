# Codex Mission: Pivot `data-investigation-agent` into a Self-Discovering Enterprise Data Investigator

Repository:

`bcsnpc/data-investigation-agent`

You are working inside an existing, substantial engineering project. Do **not** restart the project, rewrite the system from scratch, or discard working foundations.

The architectural direction has changed.

The project is no longer primarily:

> a metadata-driven investigator for manually onboarded semantic models.

The new target is:

> **A self-discovering enterprise data investigator that continuously discovers the connected data estate, understands new models/reports/tables/measures as they appear, and uses an LLM plus safe read-only tools to investigate unfamiliar data questions and discrepancies without investigator-specific code changes.**

This is an FDE-style enterprise system, not a generic SaaS product.

The goal is to deeply integrate with one enterprise environment and make the investigator behave more like a strong senior data engineer who can enter an unfamiliar data estate, discover its structure, ask the right questions, run the right diagnostics, interpret results and either explain the issue, isolate the likely/verified cause, or clearly state what context is missing.

---

# 1. First: inspect the actual repository

Before changing code:

1. inspect the current branch and latest `main`,
2. inspect all open PRs,
3. inspect the current architecture and delivery documentation,
4. inspect the current v2/catalog/adaptive-investigation implementation,
5. inspect current metadata collectors and lineage code,
6. inspect the current model-admin/onboarding implementation,
7. inspect current Power BI/Fabric/Azure SQL execution tools,
8. inspect the current adaptive planner/runtime,
9. inspect current business-question and screenshot intake,
10. inspect current tests and current documented limitations.

At minimum review:

* `README.md`
* `PROJECT_STATE_AND_NEXT_STEPS.md`
* `METADATA_DRIVEN_INVESTIGATOR_FIRST_CLASS_PRODUCT_PLAN.md`
* `docs/architecture/README.md`
* `docs/architecture/onboarding-and-model-context.md`
* `docs/architecture/current-assessment-and-migration.md`
* `docs/architecture/contracts-and-tools.md`
* `docs/architecture/planner-and-safety.md`
* `docs/architecture/phases-and-acceptance.md`
* `docs/current-delivery-status.md`
* `docs/progress.md`
* `docs/model-onboarding.md`
* `docs/catalog-scans-and-semantics.md`
* current milestone docs
* `scripts/metadata_inventory.py`
* `scripts/metadata_connectors.py`
* `scripts/lineage_graph.py`
* `scripts/investigator/onboarding.py`
* `scripts/investigator/semantic_graph.py`
* current adaptive planner/runtime modules
* current Power BI native diagnostic modules
* current SQL/source diagnostic modules
* current record/freshness/dependency diagnostic modules

Do not trust old documentation where code proves otherwise.

Before implementation, write a short current-state assessment identifying:

```text
KEEP
SIMPLIFY
REFACTOR
REMOVE FROM PRIMARY PATH
NEW REQUIRED CAPABILITY
```

---

# 2. Preserve the strong parts already built

Do not throw away the engineering foundation.

Preserve and reuse where appropriate:

* Azure SQL source/application system
* Fabric Bronze/Silver/Gold
* Power BI semantic models/reports
* metadata inventory
* report-definition collection
* semantic dependency discovery
* lineage graph
* immutable/versioned context where useful
* read-only investigation identities
* native Power BI DAX execution
* SQL/Fabric read-only execution
* typed filters/scopes
* adaptive LLM planner
* persisted observations/hypotheses
* tool receipts
* record-level evidence
* freshness evidence
* screenshot intake
* natural-language ticket intake
* business/technical shared investigation state
* query budgets
* cancellation
* replay/idempotency
* reviewed external actions
* bounded-v1 regression path

The pivot is primarily about **how context is discovered and how generally the investigator behaves**, not removing all safety or engineering discipline.

---

# 3. New product thesis

The system should behave as follows.

An enterprise operator connects the allowed environment once:

```text
Power BI / Fabric tenant or approved workspaces
Azure SQL / application databases
approved credentials / read-only identities
security policy
optional documentation sources
```

After that, the system continuously discovers what exists.

It should discover, where permissions/API coverage allow:

```text
Workspaces
Semantic models
Reports
Pages
Visuals
Measures
DAX
Tables
Columns
Relationships
Slicers
Filters
Drillthrough
Fabric lakehouses
Fabric warehouses
Fabric tables
Notebooks
Pipelines
SQL databases
SQL schemas
SQL tables
SQL views
keys
watermarks
application audit/event structures
lineage
ownership/context metadata
```

A human should **not** have to manually register every semantic model or every report for the normal product path.

Manual registration may remain as:

```text
fallback
override
restricted-environment mode
test fixture mode
```

but not as the principal architecture.

---

# 4. Replace manual onboarding with continuous discovery

The current model onboarding concept should evolve into:

> **Enterprise Connection + Continuous Discovery + Context Enrichment**

The preferred lifecycle is:

```text
ENTERPRISE CONNECTED
        ↓
DISCOVERY SCAN
        ↓
ASSETS DISCOVERED
        ↓
CONTEXT GRAPH BUILT
        ↓
SEMANTIC ENRICHMENT
        ↓
CAPABILITIES EVALUATED
        ↓
AVAILABLE FOR INVESTIGATION
        ↓
CONTINUOUS CHANGE DETECTION
```

Avoid requiring:

```text
Admin manually enters model ID
Admin manually enters report IDs
Admin manually enables every newly created report
```

for ordinary operation.

If a user publishes a new report connected to an already visible model, the next discovery scan should find it.

If a user publishes a new semantic model inside an allowed workspace, the next discovery scan should find it.

If new tables/columns/measures/relationships are added, the next scan should find them.

If new Fabric tables/notebooks/pipelines are introduced, they should be discovered.

If new SQL tables/views appear inside an allowed database, they should be discovered.

---

# 5. Introduce an Enterprise Context Graph

The central reusable structure should become an automatically maintained context graph.

Conceptually:

```text
EnterpriseEnvironment
│
├── Power BI / Fabric
│   ├── Workspace
│   │   ├── SemanticModel
│   │   │   ├── SemanticTable
│   │   │   ├── Column
│   │   │   ├── Measure
│   │   │   ├── Relationship
│   │   │   └── Calculation metadata
│   │   │
│   │   ├── Report
│   │   │   ├── Page
│   │   │   ├── Visual
│   │   │   ├── Filters
│   │   │   ├── Slicers
│   │   │   └── Drillthrough
│   │   │
│   │   ├── Lakehouse
│   │   ├── Warehouse
│   │   ├── Notebook
│   │   └── Pipeline
│
└── Azure SQL / Application
    ├── Database
    ├── Schema
    ├── Table
    ├── View
    ├── Key
    ├── Watermark
    └── Audit/Event structure
```

Edges may represent:

```text
report USES model
visual USES measure
measure DEPENDS_ON measure
measure REFERENCES column
semantic table SOURCED_FROM Gold table
Gold DERIVED_FROM Silver
Silver DERIVED_FROM Bronze
Bronze INGESTED_FROM source
notebook READS
notebook WRITES
pipeline EXECUTES
asset OWNED_BY
report IMPACTED_BY
```

Every edge should retain provenance.

Do not infer strong semantic equivalence merely because names resemble each other.

---

# 6. Make change detection a first-class capability

This is critical.

The engine should be expected to encounter an environment that changes after the investigator code is frozen.

Examples:

```text
new SQL table
new Fabric table
new semantic table
new measure
changed DAX
new relationship
changed relationship
new report
new visual
new slicer
new pipeline
changed notebook
deleted asset
renamed asset
```

A scan should produce a versioned diff such as:

```text
ADDED
CHANGED
REMOVED
UNKNOWN_DUE_TO_PARTIAL_SCAN
```

Then recompute only relevant context where safe.

Do not treat permission failure as deletion.

Do not require investigator-code changes merely because a supported new asset appeared.

---

# 7. Use the LLM more extensively

The LLM should be a central investigation reasoner, not just a ticket parser.

However:

> LLM reasoning selects and interprets tests.
> Deterministic systems provide factual observations.

The LLM should be used for:

## 7.1 Ticket understanding

Interpret:

```text
"This report looks wrong."
"Refund rate suddenly jumped."
"Why is revenue lower than yesterday?"
"Application shows 1917 orders but Power BI shows 1842."
"Why did Dallas stockout rate increase?"
```

Resolve likely:

```text
report
page
visual
metric
business entity
time period
filters
comparison intent
```

Ask clarification only when ambiguity materially affects investigation.

---

## 7.2 Context interpretation

Given discovered metadata, the LLM may interpret:

```text
DAX
SQL
notebook code
pipeline definitions
table/column names
relationships
visual definitions
business descriptions
documentation
```

It may propose:

```text
likely metric meaning
likely important dimensions
likely date role
possible source mappings
possible transformation boundaries
candidate hypotheses
```

But inferred context must carry provenance such as:

```text
LLM_INFERRED
```

and must not silently become authoritative.

---

## 7.3 Investigation planning

The LLM should decide:

> What should I test next?

based on:

```text
ticket
current observations
metric logic
semantic graph
report context
lineage
available tools
previous failed hypotheses
known business context
budgets
```

Do not predefine a mandatory:

```text
Power BI → Gold → Silver → Bronze → SQL
```

sequence.

Examples of valid first actions:

```text
reproduce semantic-model value
inspect dependency measures
break metric by dimension
inspect visual filters
inspect relationship behavior
check freshness
compare record keys
inspect source
inspect transformation logic
inspect application event
```

---

## 7.4 DAX reasoning

The LLM should reason about discovered DAX.

But Power BI remains the authoritative calculation engine.

For example:

```DAX
Refund Rate =
DIVIDE(
    [Refunded Orders],
    [Delivered Orders]
)
```

LLM can reason:

```text
ratio
numerator dependency
denominator dependency
non-additive final result
```

Then request actual evaluations from Power BI.

For:

```DAX
Adjusted Margin % =
DIVIDE(
    [Revenue] - [COGS] - [Returns Adjustment],
    [Revenue]
)
```

the investigator should recursively evaluate child measures and narrow the discrepancy.

For:

```DAX
CALCULATE(
    [Revenue],
    USERELATIONSHIP(...)
)
```

the LLM should recognize relationship-sensitive logic and use relationship/context tools.

Do **not** build a second DAX engine.

---

## 7.5 SQL / transformation interpretation

The LLM should be able to inspect SQL/notebook logic and say:

```text
this join may multiply rows
this filter excludes REINSTATED
this dedupe partitions by the wrong keys
this date predicate may drop late events
this incremental watermark could skip records
```

Then it should request deterministic tests.

It must not declare those as causes without supporting observations.

---

## 7.6 Evidence interpretation

Example:

```text
Power BI = 1428
Gold = 1428
Silver = 1428
Bronze = 1428
Azure SQL = 714
```

The LLM can infer:

```text
Downstream layers are internally consistent.
The divergence appears before/at ingestion.
Investigate duplication or ingestion semantics.
```

Then request:

```text
compare_keys
profile_duplicates
inspect ingestion transform
```

---

## 7.7 Unknown-business-context detection

This is equally important.

If the system sees:

```text
effective_date
adjustment_code
X17
```

and business meaning is unknown, it should be able to say:

```text
I can observe how this field behaves,
but I cannot establish its intended business meaning from available evidence.
```

Then request clarification or documentation.

Unknown should be a valid outcome.

---

# 8. Deterministic tool layer

Keep a generic tool registry.

Expand it where useful.

Possible tool families:

## Discovery

```text
discover_workspaces
discover_semantic_models
discover_reports
discover_model_objects
discover_fabric_assets
discover_sql_assets
discover_lineage
detect_context_changes
```

## Power BI / semantic model

```text
execute_dax
evaluate_measure
evaluate_measure_dependencies
evaluate_measure_by_dimension
evaluate_visual_context
get_measure_definition
get_measure_dependencies
get_relationships
get_report_context
get_visual_context
get_filters
get_slicers
```

## Fabric / SQL

```text
execute_bounded_sql
query_asset
profile_asset
compare_assets
compare_keys
compare_counts
compare_aggregates
compare_freshness
inspect_transform
inspect_notebook
inspect_pipeline_run
inspect_watermark
```

## Application/source

```text
query_source_record
inspect_application_event
inspect_audit_history
compare_intent_to_persisted_state
```

## Lineage / impact

```text
find_upstream
find_downstream
find_impacted_reports
find_asset_owner
```

## Generic diagnostic tools

```text
find_duplicates
find_missing_keys
find_extra_keys
dimension_breakdown
distribution_compare
null_profile
schema_compare
time_window_compare
```

The exact list should follow the existing implementation where possible.

Do not create dozens of overlapping tools merely for architecture purity.

---

# 9. Allow flexible read-only query generation

The investigator must be able to investigate unfamiliar data.

If every SQL/DAX diagnostic must be pre-authored as a fixed template, the system will remain narrow.

Therefore support flexible but governed query execution.

## SQL

Allow generated read-only diagnostic SQL subject to validation:

```text
SELECT only
approved connection
approved schemas/assets
no DDL
no DML
no EXEC
bounded joins
row limits
timeout
query budget
result-size limits
parser/policy validation
```

Prefer structured builders where practical, but do not require a new Python tool implementation for every diagnostic question.

## DAX

Allow bounded read-only DAX queries against approved semantic models.

Use:

```text
validated model scope
timeouts
result limits
tool budget
read-only identity
```

The LLM can propose DAX diagnostics, but the platform executes them.

---

# 10. Simplify over-engineered proof requirements

Do not remove evidence discipline.

But stop letting formal proof infrastructure dominate development.

Keep what materially helps:

```text
read-only access
tool receipts
query/result provenance
context version
identity
replay protection
timeouts
budgets
NOT_COMPARABLE
unsupported/gap states
human review before external mutation
```

Avoid spending milestone after milestone attempting to formally certify every remote property before the investigator is useful.

The central product question is now:

> **Can the system investigate unfamiliar enterprise data correctly and transparently?**

Prioritize that.

A useful hierarchy:

```text
OBSERVED
STRONGLY_SUPPORTED
VERIFIED
INSUFFICIENT_EVIDENCE
```

where appropriate.

Do not turn every investigation into a formal proof theorem.

---

# 11. New primary acceptance strategy: unknown environment

This becomes the main milestone.

Freeze the general investigator engine.

Then introduce data assets that the investigator code has never seen.

Do not add metric names, table names, report names or scenario names to investigator Python.

---

# 12. Unknown Domain Challenge

Create at least one completely new analytics domain after engine freeze.

Preferably use a domain sufficiently different from OrderOps.

Example:

```text
Inventory / Warehouse Operations
```

Introduce after the investigator is frozen:

## Azure SQL

```text
inventory_transactions
warehouses
stock_movements
purchase_orders
inventory_adjustments
```

## Fabric

```text
Bronze inventory tables
Silver inventory facts/dimensions
Gold inventory reporting tables
```

## Semantic Model

New tables such as:

```text
FactInventory
FactStockMovement
DimWarehouse
DimProduct
DimDate
```

New measures such as:

```text
Stock On Hand
Stockout Count
Stockout Rate
Inventory Turnover
Average Days in Inventory
Backorder Rate
```

## Reports

```text
Inventory Health
Warehouse Performance
```

The investigator must discover them through environment scanning.

No manual report-ID registration in the primary test.

---

# 13. Unknown-domain investigations

Run multiple tickets.

## Scenario A — Simple discrepancy

Example:

> "Dallas stock on hand looks too low."

Expected behavior:

```text
resolve model/report/metric
execute semantic value
slice by warehouse/product/date
trace relevant data
identify divergence or expected behavior
```

---

## Scenario B — Ratio measure

Example:

> "Dallas stockout rate suddenly increased this week."

The investigator should discover the measure's numerator/denominator and inspect them independently.

No `Stockout Rate` branch.

---

## Scenario C — Complex derived measure

Example:

```DAX
Inventory Health Score =
...
```

with multiple child measures.

The investigator should recursively narrow which dependency explains the discrepancy.

---

## Scenario D — Visual/filter problem

Global measure correct.

Specific report visual wrong due to filter/slicer/page/relationship behavior.

The investigator should isolate report context.

---

## Scenario E — Pipeline/freshness problem

A source/bronze/silver/gold/model freshness mismatch.

The system should diagnose freshness before assuming transformation logic.

---

## Scenario F — Transformation defect

Inject something such as:

```text
duplicate join
incorrect filter
wrong dedupe
wrong date predicate
incremental watermark issue
```

The LLM should inspect transformation logic and run tests.

---

## Scenario G — Source/application defect

All downstream layers reflect the source accurately, but application write/audit intent is wrong.

---

## Scenario H — Expected behavior

The business value legitimately changed.

The system should explain it without creating a technical defect.

---

## Scenario I — Insufficient business context

Introduce a new field/rule whose meaning cannot be inferred safely.

The correct outcome should explicitly request/identify missing business context.

---

# 14. New reports must be discovered automatically

This is a required acceptance criterion.

After engine freeze:

1. publish a new report in an allowed workspace,
2. point it to an existing or newly discovered semantic model,
3. do not manually add its report ID to the investigator,
4. run discovery,
5. verify the report appears as an available investigation target,
6. verify its pages/visuals/measures/filter metadata are captured where supported.

If API/platform constraints prevent automatic enumeration, document the precise platform limitation and implement the least-manual fallback.

Do not silently retain explicit report registration as though it were self-discovery.

---

# 15. New semantic models must be discovered automatically

Required test:

1. add a new semantic model in an allowed workspace,
2. do not modify investigator code,
3. do not explicitly register that model in the primary test,
4. run discovery,
5. verify model/tables/columns/relationships/measures are cataloged,
6. evaluate its capabilities,
7. allow tickets against supported reports/model assets.

Again, if platform APIs impose limitations, clearly document them.

---

# 16. New tables must be discovered automatically

Test all three levels:

```text
new Azure SQL table
new Fabric table
new semantic model table
```

The engine should:

```text
detect it
version it
connect lineage where evidence exists
mark unknown semantics where necessary
make it available to investigation tools when permitted
```

No table-name-specific Python.

---

# 17. Business context becomes optional enrichment, not onboarding gate

Teams may provide:

```text
metric definitions
owners
SLAs
tolerances
known exclusions
fiscal rules
business terminology
documentation
```

This should make investigations better.

But absence of manually entered business context should not prevent basic technical investigation when the data/model definitions are sufficient.

Use provenance:

```text
DISCOVERED
DETERMINISTICALLY_DERIVED
LLM_INFERRED
TEAM_CONFIRMED
```

Only use `TEAM_CONFIRMED` fields for decisions that require authoritative business meaning.

---

# 18. InvestigationState remains important

Continue persisting structured state such as:

```text
investigation_id
question
resolved targets
context version

observations
tool receipts
hypotheses
rejected hypotheses
supported hypotheses

tests attempted
tests completed
tested assets

unresolved questions
business-context gaps

classification
impact
stopping reason
```

Do not persist hidden chain-of-thought.

Persist only externally meaningful investigation reasoning:

```text
Hypothesis
Test
Observation
Interpretation
Next action
```

---

# 19. User experience

The main experience should become extremely simple.

## Business user

```text
Ask a data question / report a discrepancy
[optional report]
[optional screenshot]
[optional expected value]
```

Examples:

```text
Why is refund rate high this week?
This dashboard looks wrong.
Why are Dallas orders lower than yesterday?
Application and Power BI don't match.
Why did revenue drop?
```

The user should not need to select:

```text
Gold
Silver
Bronze
SQL table
notebook
pipeline
```

The investigator should resolve those.

---

# 20. Investigation timeline

Show understandable activity such as:

```text
Identified metric: Stockout Rate
Reproduced report value
Inspected measure dependencies
Compared numerator and denominator
Increase isolated to Dallas
Increase isolated to Category X
Traced Stockout Count upstream
Compared semantic model with Gold
Inspected Silver transformation
Found duplicated stock movement IDs
Reconstructed expected count
Calculated downstream impact
```

Do not expose private LLM chain-of-thought.

---

# 21. Outcomes

Use practical outcomes:

```text
EXPECTED_BEHAVIOR
LIKELY_TECHNICAL_DEFECT
VERIFIED_TECHNICAL_DEFECT
SOURCE_OR_APPLICATION_ISSUE
REFRESH_OR_FRESHNESS_ISSUE
BUSINESS_CONTEXT_REQUIRED
INSUFFICIENT_EVIDENCE
UNSUPPORTED
UNRESOLVED
```

Do not force certainty.

---

# 22. Routing remains human-reviewed

Do not expand into automatic repair.

Current product boundary remains:

```text
investigation
evidence
classification
impact
reviewed issue/notification draft
human triage
```

Do not add:

```text
automatic code repair
automatic PR
automatic deployment
automatic production data mutation
```

---

# 23. Do not over-focus on one vendor abstraction yet

The current proving environment is:

```text
Azure SQL
Microsoft Fabric
Power BI
```

Use those deeply.

Do not spend the next milestone building hypothetical Snowflake/Tableau/Databricks adapters.

However, maintain clean conceptual tool boundaries so the investigation engine is not written as:

```text
if metric == ...
if report == ...
if OrderOps ...
```

This is an FDE system for one enterprise environment with reusable investigation architecture.

---

# 24. README discipline — mandatory

**README must be updated at every meaningful stage.**

This is not optional.

The README is currently prone to historical statements becoming stale.

At the end of every implementation milestone:

1. review the entire `README.md`,
2. remove or rewrite stale current-state statements,
3. update:

   * current product definition,
   * what works today,
   * architecture summary,
   * current milestone,
   * known limitations,
   * how to run/demo,
   * link to current detailed status,
4. verify the README does not contradict:

   * `docs/current-delivery-status.md`,
   * architecture docs,
   * actual code,
5. move historical milestone detail to `docs/` rather than leaving obsolete status paragraphs in the README.

The README should answer within 60 seconds:

```text
What is this?
What can it do now?
How does it work?
What is the current milestone?
What remains?
How do I demo it?
```

Do this after **every stage**, not only at project completion.

---

# 25. Documentation discipline

At every milestone update:

```text
README.md
docs/current-delivery-status.md
docs/progress.md
relevant architecture document
relevant milestone document
PROJECT_STATE_AND_NEXT_STEPS.md if the handoff materially changes
```

Avoid duplicated contradictory status text.

Prefer one authoritative current-status source and links from other documents.

---

# 26. Engineering style

Continue treating this as real software engineering.

Use:

```text
issues
cohesive feature branches
cohesive milestone PRs
tests
acceptance criteria
architecture decisions
documented limitations
reproducible demos
```

Avoid:

```text
one tiny PR per trivial change
hundreds of infrastructure PRs without user-visible progress
metric-specific branches
scenario-specific hidden answers
documentation-only claims
tests that merely encode the expected answer
```

Favor larger coherent milestones.

---

# 27. Testing strategy should shift

Do not measure progress primarily by test count.

Regression tests remain important.

But the strongest tests are now **behavioral unknown-environment tests**.

Success should be demonstrated by:

```text
new assets introduced after engine freeze
investigator discovers them
LLM resolves unfamiliar context
LLM selects useful diagnostics
real Power BI/Fabric/SQL tools execute
evidence changes the investigation path
failed hypotheses are revised
correct outcome reached or uncertainty stated
no investigator-specific code added
```

---

# 28. Preserve adversarial tests

Also test:

```text
ambiguous table names
same measure name in multiple models
partial metadata scan
permission denial
deleted report
renamed column
changed relationship
unsupported DAX
runtime timeout
empty result
duplicate keys
large result truncation
malicious text in ticket
malicious text in metadata
malicious comments in SQL/notebook
```

Untrusted text must never become executable instructions.

---

# 29. Required architectural review

Before implementing the pivot, produce a written proposal covering:

## A. Current-state assessment

What exists now.

## B. Manual-onboarding dependencies

List exactly where model IDs/report IDs/manual enablement are assumed.

## C. Discovery architecture

How workspaces/models/reports/data assets will be automatically enumerated.

## D. Enterprise Context Graph

Schema, versioning, provenance and change handling.

## E. LLM responsibilities

Where the LLM becomes more capable.

## F. Deterministic tool responsibilities

What remains factual/tool-driven.

## G. Simplification opportunities

Identify proof/infrastructure complexity that can be retained but deprioritized.

## H. Unknown-domain test design

Exact frozen-engine experiment.

## I. Migration plan

How to evolve current catalog-v2 without breaking bounded-v1.

## J. README/documentation plan

How current documentation will remain accurate at every stage.

Do not start broad implementation until this review is coherent.

---

# 30. Proposed milestone sequence

Prefer something close to:

## Stage 1 — Architectural pivot

* update controlling architecture docs,
* rename product direction to Self-Discovering Enterprise Data Investigator,
* identify manual onboarding assumptions,
* establish discovery-first target,
* update README.

## Stage 2 — Enterprise discovery

* enumerate allowed workspaces/models/reports,
* discover SQL/Fabric assets,
* persist environment inventory,
* version scans,
* detect additions/changes/removals,
* update README.

## Stage 3 — Automatic context graph

* semantic/model/report/source graph,
* automatically ingest new reports/models/tables,
* lineage integration,
* capability evaluation,
* update README.

## Stage 4 — Expanded LLM reasoning

* richer semantic/DAX/SQL/context interpretation,
* generic hypothesis generation,
* flexible test selection,
* dynamic context retrieval,
* update README.

## Stage 5 — Flexible investigation tools

* safe bounded generic SQL/DAX diagnostics,
* dimensional/profile/key/freshness tools,
* transformation inspection,
* update README.

## Stage 6 — Freeze general engine

Tag/freeze investigator behavior.

No domain-specific additions after this point.

Update README.

## Stage 7 — Unknown Domain Challenge

Introduce new domain/data/models/reports after freeze.

Run all unknown-scenario tests.

Record successes, gaps and failures honestly.

Update README prominently with results.

## Stage 8 — UX consolidation

Make the self-discovering flow easy to demo from one business question.

Update README.

## Stage 9 — Reviewed handoff

Impact/ownership/routing and human triage.

Update README.

---

# 31. Primary architectural invariant

The final engine should satisfy:

> **New supported data assets should require metadata/context discovery, not investigator code changes.**

Examples:

```text
new measure        → no Python branch
new table          → no Python branch
new report         → no Python branch
new semantic model → no Python branch
new question       → no scenario branch
```

Configuration, credentials, access policies and human business context may change.

Investigator logic should not.

---

# 32. Key product philosophy

Use this as the guiding principle:

> **Discover first. Reason dynamically. Query real systems. Follow evidence. Admit uncertainty.**

And:

> **The system should behave less like a preprogrammed reconciliation workflow and more like a strong data engineer equipped with an automatically maintained map of the enterprise data estate and safe tools for testing hypotheses.**

---

# 33. Definition of success

The project succeeds when we can demonstrate:

1. connect an enterprise environment once,
2. automatically discover models/reports/tables/measures,
3. add an entirely new analytics domain after engine freeze,
4. do not modify investigator code,
5. ask unfamiliar business/data questions,
6. have the LLM understand the discovered context,
7. have it choose different tests depending on evidence,
8. query Power BI/Fabric/Azure SQL dynamically and safely,
9. revise failed hypotheses,
10. diagnose multiple different issue classes,
11. explain expected behavior when nothing is broken,
12. explicitly request missing business context when necessary,
13. preserve evidence and auditability,
14. present one coherent business/technical investigation,
15. keep external actions human-reviewed.

That is the new north star.

---

# 34. Immediate next action

Do **not** begin by adding more defect scenarios or more proof infrastructure.

First:

1. inspect the current repository,
2. reconcile any open PRs,
3. produce the architectural pivot assessment,
4. identify exactly what prevents automatic discovery of:

   * new semantic models,
   * new reports,
   * new semantic tables,
   * new Fabric tables,
   * new SQL tables,
5. propose the minimum coherent refactor that makes self-discovery the primary path,
6. identify where LLM reasoning can safely replace narrow hardcoded logic,
7. identify which current proof mechanisms can remain but stop blocking general investigation,
8. propose the Unknown Domain Challenge,
9. update the README to reflect the new direction immediately after the architecture pivot.

Then implement the plan in cohesive milestones.

Do not claim a capability merely because architecture exists.

Use live behavior and unknown-environment demonstrations as the primary proof.
