# Metadata-Driven Data Investigator — Product Architecture & Engineering Plan

**Status:** Proposed architecture plan for review. No application implementation is authorized by this document.  
**Updated:** 2026-09-14  
**Purpose:** Evolve the current bounded investigator into a first-class, metadata-driven, evidence-led enterprise investigation product without discarding the verified application, Azure SQL, Fabric, Power BI, metadata, lineage, provenance, ticket, evidence, and routing foundation already built.

---

# 1. Product Thesis

The product should answer a familiar enterprise question:

> **“Why does this report look wrong?”**

A business user should not need to understand DAX, Fabric notebooks, Gold/Silver/Bronze tables, Azure SQL, refresh pipelines, or technical lineage.

The product should provide two connected experiences:

## Admin / Data Team Experience

A data team onboards a semantic model once.

The platform:

1. connects to the semantic model and its upstream systems,
2. performs a deep metadata and report scan,
3. builds semantic and technical context,
4. discovers lineage,
5. determines which investigation capabilities are available,
6. lets the owning team add business definitions, owners, tolerances, refresh expectations and known exceptions,
7. marks reports/metrics as investigation-ready,
8. continuously detects model/report/source changes.

## Business / Support Experience

A user submits a ticket:

```text
Report: Executive Sales
Metric: Refund Rate
Issue: Refund Rate looks unusually high for USD orders this week.
Observed: 15.2%
Expected: ~10%
Screenshot: optional
```

The investigator then:

```text
resolve report / metric / visual / context
        ↓
load the onboarded semantic + technical context
        ↓
inspect lineage and available investigation capabilities
        ↓
execute live, read-only queries against Power BI / Fabric / Azure SQL
        ↓
interpret results
        ↓
generate and test hypotheses
        ↓
collect deterministic evidence
        ↓
identify expected behavior / first broken boundary / root cause / evidence gap
        ↓
calculate impact and affected assets
        ↓
prepare reviewed notification / defect ticket
        ↓
human triage
```

The product boundary remains:

```text
Investigation
Evidence
Classification
Impact
Notification
Bug creation
Human triage
```

Out of scope for this phase:

```text
Fix Agent
automatic code changes
automatic PR creation
QA Agent
Release Agent
production remediation
automatic business-rule changes
```

---

# 2. What Must Change From the Current Bounded Investigator

Preserve:

- coherent synthetic business system,
- application audit behavior,
- Azure SQL,
- Fabric Bronze/Silver/Gold,
- Power BI semantic model and reports,
- metadata collection,
- lineage/provenance evidence,
- current bounded-v1 investigator,
- ticket/review/evidence workflows,
- defect lab,
- routing controls,
- regression tests.

Replace this assumption:

```text
known metric
→ fixed Python branch
→ known tables
→ fixed layer order
→ scenario verifier
```

with:

```text
ticket
→ onboarded model context
→ metadata-resolved metric/report/filter context
→ relevant lineage subgraph
→ capability discovery
→ persisted InvestigationState
→ planner selects safe investigation tool
→ live system query
→ structured evidence
→ hypothesis update
→ next tool or conclusion
```

The engine must **predefine capabilities, not investigation paths**.

---

# 3. First-Class Product Surfaces

## 3.1 Admin Console — Model Onboarding & Investigation Readiness

Recommended sections:

```text
Models
Connections
Onboarding
Business Context
Investigation Readiness
Scan History
Changes
Ownership
Policies
```

A model is not automatically assumed to be fully investigable simply because it can be queried.

## 3.2 Investigation Workspace — Ticket to Evidence

Recommended user workflow:

```text
New Ticket
↓
Investigation Timeline
↓
Result
├── Business Summary
├── Evidence
├── Lineage
├── Impact
└── Activity
```

Business and technical views must reference the **same investigation ID, scope, evidence and outcome**.

Do not maintain separate business and technical investigation engines.

---

# 4. Semantic Model Onboarding

Every semantic model should go through an explicit onboarding lifecycle.

```text
REGISTERED
    ↓
CONNECTED
    ↓
SCANNING
    ↓
DISCOVERED
    ↓
SEMANTICALLY_ANALYZED
    ↓
BUSINESS_CONTEXT_REVIEW
    ↓
CAPABILITY_EVALUATED
    ↓
INVESTIGATION_READY
    ↓
ENABLED
```

Partial states are valid:

```text
PARTIAL
NEEDS_CONTEXT
UNSUPPORTED
STALE_SCAN
```

---

# 5. Onboarding Step 1 — Register and Connect

An admin selects or registers:

```text
Workspace
Semantic Model
Reports
Upstream Fabric assets
Source connections
```

The platform records:

```text
organization / environment
workspace ID
semantic model ID
report IDs
connection identities
scan policy
owner/team
```

All runtime access should remain read-only for the investigator.

---

# 6. Onboarding Step 2 — Deep Technical and Semantic Scan

The deep scan should collect as much deterministic context as the platform exposes.

## Semantic Model

Collect:

```text
tables
columns
data types
relationships
relationship direction
active/inactive relationships
measures
DAX definitions
measure dependencies
hierarchies
calculation metadata where supported
source bindings
model mode / Direct Lake / relevant execution metadata
```

## Reports

Collect:

```text
reports
pages
visuals
visual-to-model bindings
measures used by visuals
columns used by visuals
report filters
page filters
visual filters
slicers
drillthrough context
supported interactions/context where available
```

## Fabric

Collect:

```text
lakehouses
warehouses
tables
columns
notebooks
pipelines
SQL definitions
notebook definitions
refresh/run metadata
source/target relationships
native lineage
deployment/version information where available
```

## Azure SQL / Operational Source

Collect:

```text
schemas
tables
columns
views
stored definitions where applicable
keys
business identifiers
timestamps / watermarks
source metadata
application audit/event structures
```

The result is a versioned technical snapshot of the investigation environment.

---

# 7. Onboarding Step 3 — Build the Semantic Graph

Do not treat a Power BI measure as merely a string containing DAX.

Build a semantic dependency graph.

Example:

```text
Adjusted Margin %
│
├── Revenue
├── COGS
└── Returns Adjustment
```

Example:

```text
Refund Rate
│
├── Refunded Orders
└── Delivered Orders
```

Record:

```text
measure
dependencies
referenced tables/columns
relationships involved
known filter modifiers
semantic operation classes
report/visual usage
```

This graph supports recursive investigation.

---

# 8. Onboarding Step 4 — LLM Semantic Enrichment

After deterministic metadata has been collected, an LLM may perform an enrichment pass.

Its job is to organize and interpret existing context, not invent technical truth.

Possible outputs:

```text
metric description candidates
metric synonyms
likely business grain
measure category
ratio / additive / semi-additive / time-shift classification
important child measures
potential investigation dimensions
human-readable explanation
```

Every enriched field must have provenance:

```text
DISCOVERED
DERIVED_DETERMINISTICALLY
LLM_INFERRED
TEAM_CONFIRMED
```

LLM inference must never silently become authoritative business metadata.

---

# 9. Onboarding Step 5 — Team-Supplied Business Context

The owning team should be able to provide or approve:

```text
Business definition
Metric synonyms
Authoritative source
Business grain
Expected date basis
Important dimensions
Refresh SLA
Acceptable tolerance
Metric owner
Report owner
Technical owner
Known exceptions
Known exclusions
Fiscal/calendar rules
Links to documentation
```

Example:

```text
Metric:
Net Cash

Definition:
Captured payments minus successful refunds.

Authoritative source:
Orders payment/refund transactions.

Refresh expectation:
30 minutes.

Tolerance:
$0 for closed periods.

Known exception:
Pending refunds are excluded.

Owner:
Finance Analytics.
```

This context becomes available to investigations without being re-entered for every ticket.

---

# 10. Investigation Capability Model

A semantic model being discoverable does **not** imply every measure can be fully investigated.

Capabilities should be explicit and versioned.

Potential capability flags:

```text
MODEL_QUERYABLE
REPORT_CONTEXT_AVAILABLE
VISUAL_CONTEXT_REPLAYABLE
MEASURE_DEFINITION_AVAILABLE
MEASURE_DEPENDENCIES_RESOLVED
LINEAGE_TRACEABLE
UPSTREAM_QUERYABLE
FRESHNESS_COMPARABLE
ROW_KEY_COMPARABLE
AGGREGATE_RECONCILABLE
RATIO_DECOMPOSABLE
TIME_CONTEXT_SUPPORTED
RELATIONSHIP_CONTEXT_SUPPORTED
SOURCE_PROVENANCE_VERIFIED
IMPACT_TRAVERSAL_AVAILABLE
```

Capability state:

```text
SUPPORTED
PARTIAL
UNSUPPORTED
UNKNOWN
TEMPORARILY_UNAVAILABLE
```

---

# 11. Investigation Readiness

The admin panel should display readiness for each onboarded model/report/metric.

Example:

```text
Executive Sales Model

Connection                    ✓
Semantic metadata             ✓
Measure definitions           ✓
Report bindings               ✓
Visual/filter context         ✓
Technical lineage             ✓
Power BI query execution      ✓
Gold query execution          ✓
Silver query execution        ✓
Bronze query execution        ✓
Azure SQL query execution     ✓
Business definitions          ✓
Owners                        ✓

Investigation status:
READY
```

Another measure may show:

```text
Complex Calculation Group Metric

Queryable                     ✓
Dependency graph              PARTIAL
Upstream reconciliation       UNSUPPORTED

Investigation status:
PARTIAL
```

The system must communicate these limits honestly.

---

# 12. Continuous Change Detection

Onboarding is not a one-time static import.

After initial onboarding:

```text
scheduled / triggered scan
        ↓
compare definitions and hashes
        ↓
identify changed assets
        ↓
rescan affected subgraph
        ↓
recompute semantic dependencies
        ↓
reevaluate capabilities
        ↓
request team review only when necessary
```

Example:

A developer adds:

```DAX
Refund Success Rate =
DIVIDE(
    [Successful Refunds],
    [Refund Attempts]
)
```

The next scan should:

```text
discover measure
↓
capture DAX
↓
resolve dependencies
↓
classify semantic operations
↓
connect lineage
↓
evaluate investigation capabilities
↓
mark READY / PARTIAL / NEEDS_CONTEXT
```

No metric-name-specific investigator Python should be required.

---

# 13. Semantic Execution Principle — Use the Real Model

This is a major architecture decision.

**Do not attempt to build a second Power BI/DAX calculation engine.**

For Power BI semantics, the deployed semantic model is the authoritative execution engine.

The investigator should be able to call safe read-only functions such as:

```text
execute_dax_query()
evaluate_measure()
evaluate_measure_by_dimension()
evaluate_dependency_measures()
get_measure_definition()
get_measure_dependencies()
get_model_relationships()
get_visual_context()
get_report_filters()
get_page_filters()
get_visual_filters()
```

The LLM can understand DAX and propose diagnostic tests, but the actual semantic values should come from the real model.

---

# 14. Typed Expression / Semantic IR — Revised Role

Keep a typed semantic/expression IR, but **do not use it to reproduce arbitrary DAX**.

Use it for:

```text
classifying semantic operations
representing dependencies
describing grain
representing filters/scope
defining safe comparison contracts
building upstream equivalent expressions where supported
validating tool requests
determining capability support
```

Example supported semantic operation classes:

```text
SUM
COUNT
DISTINCT_COUNT
RATIO
DERIVED_ARITHMETIC
FILTERED_MEASURE
MEASURE_DEPENDENCY
TIME_SHIFT
RELATIONSHIP_SWITCH
DIMENSIONAL_SLICE
```

Broader semantics can be added once, benefiting every metric that uses them.

---

# 15. Complex Measure Investigation

Complex measures are a core product requirement, not an optional future enhancement.

The investigator should use **controlled decomposition**.

Example:

```DAX
Adjusted Margin % =
DIVIDE(
    [Revenue] - [COGS] - [Returns Adjustment],
    [Revenue]
)
```

Investigation strategy:

```text
evaluate Adjusted Margin %
        ↓
inspect dependency graph
        ↓
evaluate Revenue
evaluate COGS
evaluate Returns Adjustment
        ↓
identify which dependency diverges
        ↓
recurse into that dependency
```

This behaves like debugging a calculation graph.

---

# 16. Ratio / Non-Additive Measures

For:

```DAX
Refund Rate =
DIVIDE(
    [Refunded Orders],
    [Delivered Orders]
)
```

Do not compare or sum the final percentage blindly across layers.

Instead:

```text
evaluate Refund Rate in Power BI
↓
evaluate Refunded Orders
↓
evaluate Delivered Orders
↓
identify numerator/denominator discrepancy
↓
trace only the problematic dependency upstream
```

The investigation engine must understand the measure type before choosing comparisons.

---

# 17. Filter and Visual Context

A ticket about a report visual must reproduce the **actual report context**, not only the global measure.

Context may include:

```text
report filters
page filters
visual filters
slicers
date context
currency
region
product
customer
drillthrough context
relationship behavior
```

The investigator should be able to run the same measure:

```text
globally
under the ticket's exact context
by selected dimensions
with controlled diagnostic breakdowns
```

Example:

```text
Global             correct
USD                correct
USD + September    wrong
USD + Sep + APAC   wrong
USD + Sep + US     correct
```

This isolates the problem without relying on a predefined scenario.

---

# 18. Dimensional Diagnostic Slicing

When a value differs, the planner should be able to request a generic breakdown.

Potential dimensions should come from metadata/model relationships, not hardcoded names.

Example:

```text
Revenue mismatch
↓
break down by Region
↓
APAC explains entire difference
↓
break APAC by Order Status
↓
REINSTATED explains entire difference
```

This is a reusable investigation technique across many metrics.

---

# 19. Counterfactual / Replay Tests

The investigator should support safe read-only counterfactual tests where deterministic tools can prove a hypothesis.

Example:

```text
Reported Net Cash:
$10.212M

Suspected excluded rows:
$0.518M

Reconstructed value:
$10.730M

Expected/source value:
$10.730M
```

Exact reconciliation is strong causal evidence.

Counterfactual tests must remain read-only and bounded.

---

# 20. Investigation Tool Layer

The investigation engine should have a typed tool registry.

The toolset is predefined.

**The sequence of tool calls is not.**

Initial tool families:

## Semantic / Power BI

```text
get_report_context
get_visual_context
get_measure_definition
get_measure_dependencies
get_model_relationships
evaluate_measure
evaluate_measure_dependencies
evaluate_measure_by_dimension
execute_bounded_dax
```

## Fabric / SQL

```text
query_asset
execute_bounded_sql
compare_assets
compare_keys
compare_row_counts
compare_aggregates
compare_freshness
profile_difference
inspect_transform
inspect_pipeline_run
get_high_watermark
```

## Application / Source

```text
get_app_event
get_order_audit
query_source_record
compare_application_intent_to_persisted_state
```

## Lineage / Impact

```text
find_upstream_lineage
find_downstream_lineage
find_downstream_impact
get_asset_owner
```

## Evidence

```text
record_observation
record_evidence
verify_reconciliation
```

---

# 21. Query Execution Model

The system needs enough flexibility to investigate unfamiliar cases without falling back to hardcoded templates.

But the LLM must not receive unrestricted database execution.

Recommended approach:

```text
Planner proposes diagnostic intent
        ↓
Tool builds or accepts a bounded query plan
        ↓
Policy / parser validation
        ↓
Read-only execution
        ↓
Structured result
```

For SQL:

```text
SELECT-only
validated identifiers
approved connections
row limits
execution timeout
cost limits
no DDL/DML
no stored procedure execution unless explicitly approved
```

For DAX:

```text
read-only query execution
model-scoped
bounded result set
timeout
validated referenced assets where practical
```

The goal is:

> flexible investigation queries without unrestricted arbitrary execution.

---

# 22. InvestigationState

Persist structured investigation state.

Recommended fields:

```text
investigation_id
engine_version
ticket_id

model_context_version
metadata_scan_id
lineage_snapshot_id

resolved_report
resolved_page
resolved_visual
resolved_metric
resolved_scope

business_context
capabilities

relevant_assets
relevant_lineage

observations
evidence_refs

open_hypotheses
supported_hypotheses
rejected_hypotheses

tests_attempted
tests_completed
tests_failed

tested_assets
unresolved_questions

policy_budget
tool_budget
query_budget

classification
root_cause
impact
stopping_reason
```

Do not persist private LLM chain-of-thought.

Persist externally meaningful:

```text
hypothesis
test selected
observation
evidence
decision
```

---

# 23. Evidence-Led Planner Loop

The planner should operate like:

```text
load ticket + model context
        ↓
resolve investigation target
        ↓
load relevant semantic/lineage subgraph
        ↓
inspect capabilities
        ↓
generate supported hypotheses
        ↓
choose next bounded diagnostic test
        ↓
policy gate
        ↓
execute tool
        ↓
persist receipt + evidence
        ↓
update hypotheses
        ↓
choose next test / ask clarification / conclude
```

Different observations must produce different next actions.

It must not always execute:

```text
Power BI → Gold → Silver → Bronze → Azure SQL
```

in that exact order.

Sometimes the best first test may be:

```text
measure dependency decomposition
freshness
visual filter reproduction
dimensional slice
application audit
relationship inspection
```

---

# 24. Deterministic Verification

The LLM proposes and interprets.

The product verifies.

Root-cause verification may include:

```text
exact difference reconciliation
matching missing business keys
matching freshness boundary
reproducible report context
matching transformation condition
counterfactual replay
corrected diagnostic expression
application audit/persisted-state mismatch
```

A generated explanation cannot promote itself to a verified cause.

---

# 25. Classification

Supported terminal classifications:

```text
EXPECTED_BEHAVIOR
TECHNICAL_DEFECT
REFRESH_FRESHNESS
SOURCE_OR_APPLICATION_DEFECT
BUSINESS_REVIEW_REQUIRED
INSUFFICIENT_EVIDENCE
UNSUPPORTED_CAPABILITY
UNRESOLVED
```

These should be determined from evidence gates, not arbitrary confidence percentages.

---

# 26. Ticket Experience

The primary user interface remains ticket-based.

Recommended fields:

```text
Report
Issue description
Screenshot(s)
```

Optional:

```text
Page
Visual
Metric
Observed value
Expected value
Date / period
Priority
Additional context
```

Only reports/models enabled in the admin console should be selectable.

The user should not select:

```text
Gold table
Silver table
Notebook
Pipeline
SQL table
```

The product exists to resolve those technical assets itself.

---

# 27. Screenshot Role

Screenshot input is supporting context.

The product may extract:

```text
report title
visual title
metric
visible value
date
visible slicers
```

But screenshots remain untrusted until confirmed against the onboarded catalog and live system.

Screenshot-only diagnosis is not required for the first general engine milestone.

---

# 28. Investigation Result

Business result example:

```text
TECHNICAL DEFECT FOUND

Net Cash is understated by $99.

Cause:
One refund is deducted twice in the Gold transformation.

Affected orders:
1

Affected reports:
Executive Sales

Technical layers:
Azure SQL  ✓
Bronze     ✓
Silver     ✓
Gold       ✗
Power BI   ✗

Responsible team:
Data Platform
```

Technical view provides:

```text
resolved scope
semantic dependency graph
lineage
tests executed
DAX/SQL tool receipts
comparison results
evidence
rejected hypotheses
verified causal evidence
impact analysis
```

Both views come from the same outcome revision.

---

# 29. Routing

Only verified outcomes become routing candidates.

```text
verified outcome
↓
owner resolution
↓
reviewed defect draft
↓
human authorization
↓
GitHub / Jira / ADO / ServiceNow adapter
↓
email / Teams / Slack adapter
↓
human triage
```

For the current project:

```text
GitHub Issues
Email
```

can remain the first implemented providers.

Do not let planner text directly trigger an external action.

---

# 30. Core Product Object Model

Recommended first-class entities:

```text
Organization
Environment
Connection
SemanticModel
Report
Page
Visual
Metric
MetricDependency
BusinessDefinition
Asset
LineageEdge
MetadataScan
Capability
Owner
Policy

Ticket
Investigation
InvestigationState
Hypothesis
Observation
ToolReceipt
Evidence
Outcome
Impact
RoutingDraft
DeliveryReceipt
```

This object model should guide the API and UI.

---

# 31. Revised Target Architecture

```text
                         ADMIN CONSOLE
                              │
                     Model Onboarding
                              │
                 ┌────────────┴────────────┐
                 │                         │
           Deep Technical Scan       Team Context
                 │                         │
                 └────────────┬────────────┘
                              ↓
                  Versioned Model Context
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
 Semantic Dependency     Technical Lineage     Business Context
       Graph                   Graph                 Catalog
        └─────────────────────┼─────────────────────┘
                              ↓
                    Capability Evaluation
                              ↓
                    Investigation Catalog
                              │
                        ENABLED MODELS
                              │
──────────────────────────────┼──────────────────────────────
                              │
                         USER TICKET
                              ↓
                       Ticket Resolver
                              ↓
                     Relevant Context Pack
                              ↓
                    InvestigationState
                              ↓
                  Evidence-Led Planner / LLM
                              ↓
                     Policy / Budget Gate
                              ↓
                       Tool Registry
             ┌────────────────┼────────────────┐
             ↓                ↓                ↓
          Power BI          Fabric          Azure SQL
          DAX API          SQL/API          SQL/API
             └────────────────┼────────────────┘
                              ↓
                         Live Evidence
                              ↓
                    Deterministic Verifier
                              ↓
                    Investigation Outcome
                   ┌──────────┴──────────┐
                   ↓                     ↓
              Business View        Technical View
                   └──────────┬──────────┘
                              ↓
                       Reviewed Routing
                              ↓
                         Human Triage
```

---

# 32. Revised Engineering Milestones

The original A–I sequence should be updated to make onboarding and semantic execution first-class.

## Phase A — Freeze Current Bounded POC

### Objective
Preserve the existing working system as `bounded-v1`.

### Work
- reconcile current demo PR chain,
- update stale status documentation,
- create a known baseline tag/commit,
- retain current demos,
- retain Order Count / Net Cash regressions,
- pin engine version on saved investigations.

### Acceptance
The bounded POC remains reproducible after the v2 refactor starts.

---

## Phase B — Product Model Onboarding Foundation

### Objective
Introduce the admin-facing concept of an onboarded investigation model.

### Work
Define/persist:

```text
SemanticModel
Report
Metric
ModelContextVersion
BusinessDefinition
Owner
Capability
MetadataScan
```

Create onboarding state machine.

Do not build a highly polished UI yet; basic admin UI/API is sufficient.

### Acceptance
A model can be registered, scanned, reviewed and enabled/disabled for investigation without hardcoding model IDs in the investigator.

---

## Phase C — Deep Semantic Catalog & Change Detection

### Objective
Turn collected metadata into a reusable investigation catalog.

### Work
- remove general-path metric whitelist,
- capture measure definitions/dependencies,
- capture relationships,
- capture report/page/visual/filter context,
- connect semantic assets to technical lineage,
- add definition hashes and delta scans,
- discover newly added measures automatically,
- store provenance for discovered/inferred/team-confirmed context.

### Acceptance
A newly added semantic measure appears in the catalog without investigator Python changes.

---

## Phase D — Semantic Execution & Typed Investigation Tools

### Objective
Expose the connected systems as safe, generic investigation capabilities.

### Work
Implement/refactor typed tools for:

```text
Power BI DAX execution
measure evaluation
dependency evaluation
dimensional slicing
report-context evaluation

Fabric/Azure SQL querying
asset comparison
freshness comparison
key comparison
transformation inspection
pipeline/run inspection

application audit inspection
lineage traversal
impact traversal
```

### Acceptance
Tools operate on resolved assets/scope, not metric names or fixed scenario paths.

---

## Phase E — Semantic Operation & Capability Evaluator

### Objective
Determine what kind of investigation is safe/possible for each metric.

### Work
Support initial operation classes:

```text
additive aggregation
distinct count
ratio
derived arithmetic
measure dependency
basic filtered measure
dimensional slice
supported relationship context
```

Use the actual semantic model for execution.

Use typed IR for decomposition/comparability, not arbitrary DAX reproduction.

### Acceptance
The system can state precisely whether a discovered metric is queryable, decomposable, upstream-reconcilable, partially supported, or unsupported.

---

## Phase F — Persisted InvestigationState & Capability Registry

### Objective
Make investigations restartable, auditable and dynamic.

### Work
Persist:

```text
scope
context version
capabilities
hypotheses
observations
tests
evidence
tool receipts
budgets
stopping reason
```

### Acceptance
An investigation can stop and resume without losing evidence or repeating completed work unnecessarily.

---

## Phase G — Evidence-Led Planner Loop

### Objective
Replace fixed investigation sequencing.

### Work
Planner:

```text
reads evidence
selects next diagnostic question
chooses eligible tool
executes through policy gate
updates hypotheses
continues / clarifies / stops
```

Add explicit budgets and stopping rules.

### Acceptance
Different evidence produces different next tool calls.

The planner demonstrates at least one rejected/revised hypothesis.

---

## Phase H — Complex / Unseen Metric Acceptance

### Objective
Prove generality beyond simple additive measures.

After engine code is frozen, introduce a new metric such as:

```DAX
Refund Rate =
DIVIDE(
    [Refunded Orders],
    [Delivered Orders]
)
```

Do not add metric-specific investigator code.

Test:

### Healthy
Agent confirms expected behavior with evidence.

### Controlled Defect
Agent decomposes the ratio, finds the problematic dependency, traces it upstream and verifies cause.

### Insufficient Evidence
Remove required provenance/context and confirm the agent returns a precise evidence gap rather than inventing an answer.

### Acceptance
PASS only if:

```text
no Refund Rate-specific Python branch
no scenario-name verifier in general path
measure discovered through metadata
real Power BI DAX execution used
dependency graph used
planner selects tests dynamically
evidence supports outcome
```

Existing Order Count / Net Cash become regressions.

---

## Phase I — Unified Ticket Product Experience

### Objective
Connect the business and technical experiences to the same general engine.

### Work
- report selector based on enabled onboarded models,
- ticket description,
- screenshot attachment,
- context resolution,
- live investigation timeline,
- business summary,
- technical evidence,
- lineage,
- impact,
- activity.

### Acceptance
One investigation ID powers both views.

---

## Phase J — Reviewed Routing

### Objective
Complete the approved product boundary.

### Work
- owner resolution,
- defect eligibility gates,
- reviewed bug draft,
- notification draft,
- GitHub/email provider integration,
- human triage state.

### Acceptance
Verified technical defect can create a reviewed bug and notification.

Expected behavior, ambiguity, unsupported capability or insufficient evidence must not create automatic defect spam.

---

# 33. Critical Acceptance Tests

The v2 product should not be considered successful merely because it produces better prose.

## Test 1 — New Additive Metric
Add a new supported additive measure after engine freeze. No investigator code changes.

## Test 2 — New Ratio Metric
Use `Refund Rate`. Agent must decompose dependencies.

## Test 3 — Complex Derived Metric

```DAX
Adjusted Margin % =
DIVIDE(
    [Revenue] - [COGS] - [Returns Adjustment],
    [Revenue]
)
```

Agent must recursively identify which child dependency explains the issue.

## Test 4 — Visual Context Issue
Metric is globally correct but wrong under a report/page/visual filter. Agent must reproduce context and isolate the filter problem.

## Test 5 — Freshness Issue
Agent must distinguish stale Bronze, stale Silver, stale Gold and stale semantic layer.

## Test 6 — Application-Origin Issue
All downstream data agrees with Azure SQL, but application audit/intent proves the source write is wrong.

## Test 7 — Expected Behavior
All layers reconcile and business data explains the change. No technical bug should be created.

## Test 8 — Unsupported / Insufficient Evidence
Agent must stop honestly when required capability/provenance is unavailable.

---

# 34. Safety and Product Guardrails

Keep:

```text
read-only investigation identities
query timeouts
row limits
cost budgets
validated identifiers
explicit capability eligibility
NOT_COMPARABLE
provenance requirements
unsupported-context holds
human review for external actions
```

Add:

```text
prompt-injection isolation for metadata/ticket/report text
tool-call schema validation
DAX/SQL query validation
planner iteration limits
per-investigation query budgets
sensitive-field handling
audit trail for every query/tool call
```

The LLM proposes.

The policy engine authorizes.

The tool executes.

The evidence store records.

---

# 35. Decisions Required Now

Approve these defaults:

1. **Keep `bounded-v1`; build `catalog-v2` incrementally.**
2. **Model onboarding is a first-class product feature, not an implementation detail.**
3. **Power BI remains the authoritative DAX execution engine.**
4. **Typed semantic IR supports decomposition/comparability; it does not replace DAX.**
5. **Investigation tools are generic; investigation paths are dynamic.**
6. **Every enabled model has versioned semantic, lineage, business and capability context.**
7. **Team-provided business context is stored separately from LLM inference.**
8. **New measures are discovered through delta scans and capability evaluation.**
9. **Evidence gates determine outcomes; LLM confidence wording does not.**
10. **One investigation powers both business and technical views.**
11. **Bug/notification creation remains human-reviewed and is the end of current product scope.**
12. **The unseen complex-measure experiment is the architectural acceptance gate.**

---

# 36. Decisions That Can Wait

Do not block v2 on:

```text
multi-tenant SaaS deployment
hosted graph database
vector database
multi-agent architecture
additional data platforms
full OCR/vision automation
calculation groups
arbitrary DAX support
many-to-many edge cases
all time-intelligence patterns
automatic repair
QA agents
release automation
```

Add these only after the core investigation architecture proves itself.

---

# 37. Product North Star

> A team onboards its semantic model and upstream data environment once. The platform continuously understands the model, reports, measures, relationships, filters, transformations, lineage, refresh behavior, ownership and business definitions. When a user reports that a report or metric looks wrong, the investigator retrieves the relevant context, executes safe live queries across Power BI, Fabric and source systems, decomposes complex calculations when necessary, selects its next diagnostic step from the evidence, verifies the cause deterministically, quantifies impact, and presents the same investigation to business and technical users at the appropriate level of detail.

The product should **not** require a new Python investigation branch every time a team adds a supported measure.

The core design rule is:

> **Predefine investigation capabilities. Do not predefine investigation paths.**

And the key product rule is:

> **Onboarding builds understanding. Tickets provide symptoms. Investigation tools gather live evidence. The planner decides what to test next. Deterministic verification decides what can be claimed.**
