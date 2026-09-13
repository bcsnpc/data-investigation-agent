# Data Investigator — Ticket Experience, Defect Lab, and POC Scope Extension

**Status:** Approved scope extension  
**Updated:** 2026-09-13  
**Applies to:** Existing Data Investigator POC / Portfolio project  
**Scope boundary:** Stop at **root-cause identification + evidence + classification + team notification + bug creation**. Autonomous fixing, QA agents, release agents, and production remediation are out of scope for this phase.

---

# 1. Product Direction

The product should behave like an **enterprise data investigation system**, not a general-purpose chatbot.

The main user experience begins with a **ticket submission**.

A business user, analyst, report consumer, support engineer, or data team member notices something wrong and submits an issue.

The user should not need to know which table is wrong, which Fabric notebook owns the metric, which pipeline loaded the data, or whether the problem came from the application, Azure SQL, Bronze, Silver, Gold, semantic model, refresh, or report.

Core product promise:

> A user reports what looks wrong. The system traces the metric or business object across the full technical lineage, determines whether the behavior is expected or defective, identifies the first broken boundary, proves the cause with evidence, quantifies impact, and routes the result to the responsible team.

---

# 2. Current POC Environment

```text
Order Operations Web App
        ↓
Azure SQL
        ↓
Fabric Bronze
        ↓
Fabric Silver
        ↓
Fabric Gold
        ↓
Power BI Semantic Model
        ↓
Power BI Reports
```

The baseline is verified and reconciled.

**Rule:** Preserve a known-good baseline. Intentional defects must be injectable and resettable.

---

# 3. Scope Boundary

Implement:

```text
Ticket
   ↓
Investigation
   ↓
Root cause
   ↓
Evidence
   ↓
Classification
   ↓
Impact
   ↓
Notify responsible team
   ↓
Create bug / incident / review item
```

Do **not** implement:

```text
Fix Agent
QA Agent
Release Agent
automatic code changes
automatic PR creation
automatic production deployment
automatic production data repair
```

After a defect is created, the product stops at a conceptual human triage gate:

```text
Bug created
   ↓
Human review / triage
   ├── Approve future agent fix
   ├── Assign engineer
   ├── Park in backlog
   ├── Send for business review
   └── Close / reject
```

---

# 4. Primary User Experience — Ticket-Based Investigation

Do not make chat the main interface.

Primary flow:

```text
Submit Ticket
    ↓
Investigating
    ↓
Root Cause / Expected Behavior / Escalation
    ↓
Evidence + Impact
    ↓
Notification / Bug creation when appropriate
```

---

# 5. Ticket Submission Form

Create a **New Data Issue** / **New Investigation** page.

Required:

```text
Title
Report
Issue Description
```

Optional:

```text
Report Page
Visual
Metric
Observed Value
Expected Value
Date / Period
Priority
Screenshot(s)
Additional Notes
```

Example:

```text
Title:
September revenue mismatch

Report:
Executive Finance

Page:
Revenue Overview

Metric:
Net Revenue

Description:
September Net Revenue looks approximately $500K lower
than the source application.

Observed:
$10.21M

Expected:
~$10.73M

Period:
September 2026
```

The user must not have to select technical tables or lineage paths.

---

# 6. Screenshot Support

Screenshots are **supporting context**, not source of truth.

For the POC:

- store screenshot with ticket,
- show it in investigation workspace,
- optionally use vision to extract report name, metric, period, filters, and displayed value,
- validate any extracted context against metadata and actual query results.

---

# 7. Investigation Workspace

Recommended tabs:

```text
Overview
Investigation
Evidence
Lineage
Impact
Activity
```

Example investigation timeline:

```text
✓ Ticket interpreted
✓ Report resolved: Executive Finance
✓ Metric resolved: Net Revenue
✓ Technical lineage loaded
✓ Power BI value reproduced
✓ Gold value checked
✓ Silver value checked
⚠ First divergence found: Silver → Gold
✓ Transformation inspected
✓ Hypothesis generated
✓ Hypothesis verified
✓ Downstream impact calculated
✓ Root cause classified
✓ Engineering bug created
✓ Team notification sent
```

Show actions, observations, and evidence. Do not expose hidden chain-of-thought.

---

# 8. Full Technical Investigation Path

The investigator must be capable of tracing:

```text
Business App / App Events
        ↓
Azure SQL
        ↓
Fabric Bronze
        ↓
Fabric Silver
        ↓
Fabric Gold
        ↓
Power BI Semantic Model
        ↓
Report / Page / Visual / Metric
```

Not every incident needs every layer. Use lineage and evidence to focus the search.

---

# 9. Classification Model

The system must be able to conclude:

```text
EXPECTED_BEHAVIOR
TECHNICAL_DEFECT
SOURCE_OR_DATA_ISSUE
REFRESH_FRESHNESS
BUSINESS_REVIEW_REQUIRED
UNRESOLVED
```

## Expected Behavior

Use when all technical layers reconcile and approved business logic explains the result.

Example:

```text
September revenue is lower because completed order volume fell
and returns increased.
```

No bug is created.

## Technical Defect

Use when implementation violates known expected behavior and deterministic evidence identifies the first broken boundary.

Create a bug and notify the responsible team.

## Source / Data Issue

Use when application/source data itself is wrong and downstream systems faithfully propagate it.

This may still create an application-team bug.

## Refresh / Freshness

Use when one layer is behind its upstream source.

Example:

```text
Azure SQL current through 14:00
Bronze current through 14:00
Silver current through 12:00
Gold current through 12:00
Power BI current through 12:00
```

First stale boundary: `Bronze → Silver`.

## Business Review Required

Use when current implementation matches the approved rule but the user expects a different business definition.

Do not create an automatic technical bug.

## Unresolved

Use when evidence is incomplete or multiple hypotheses remain.

Return what was checked, what was ruled out, and what evidence is still missing.

---

# 10. Defect Lab Requirements

Each controlled scenario must be:

- named,
- deterministic,
- injectable,
- resettable,
- documented,
- testable,
- associated with expected ground truth.

Do not hard-code scenario answers into the investigator.

---

# 11. Scenario Family A — Application / API

## APP-001 — Wrong Status Mapping

User performs:

```text
REINSTATE ORDER
```

Application/API writes:

```text
CANCELLED
```

Expected evidence:

```text
App event          REINSTATED
Azure SQL          CANCELLED
Bronze             CANCELLED
Silver             CANCELLED
Gold               affected
Power BI           affected
```

Expected first broken boundary:

```text
Application → Azure SQL
```

## APP-002 — Duplicate Transaction

Simulate frontend retry / duplicate submission / missing idempotency.

Expected:

```text
One logical user action
Two persisted business transactions
```

## APP-003 — Missing Application Write

Simulate:

```text
App says operation succeeded
App audit event exists
Azure SQL business row missing
```

Expected first broken boundary:

```text
Application → Azure SQL
```

## APP-004 — Incorrect Application Calculation

Example:

```text
quantity = 10
unit price = 100
discount = 100

Expected = 900
Persisted = 1000
```

Downstream may all reconcile to the wrong source value.

Expected conclusion:

> Downstream data platform is healthy. Incorrect value originated in application logic/source persistence.

---

# 12. Scenario Family B — Azure SQL → Bronze

## ING-001 — Bronze Refresh Not Run

Expected:

```text
Azure SQL  current
Bronze     stale
Silver     stale
Gold       stale
Power BI   stale
```

First broken boundary:

```text
Azure SQL → Bronze
```

## ING-002 — Partial Ingestion

Example:

```text
US loaded
Canada loaded
Europe missing
```

Identify missing partition/region/batch.

## ING-003 — Incremental Watermark Error

Introduce a boundary bug around `updated_at`.

Source contains affected records, Bronze does not.

## ING-004 — Schema Change

Introduce a controlled source schema change that causes ingestion failure or omission.

---

# 13. Scenario Family C — Bronze → Silver

## SIL-001 — Silver Refresh Not Run

Expected:

```text
Source     current
Bronze     current
Silver     stale
Gold       stale
Power BI   stale
```

First broken boundary:

```text
Bronze → Silver
```

## SIL-002 — Row-Dropping Filter

Bronze contains valid rows; Silver drops them.

## SIL-003 — Incorrect Deduplication

Silver keeps the wrong record/version.

## SIL-004 — Incorrect Join

Example: use an inner join where unmatched source rows should be preserved.

## SIL-005 — Incorrect Derived Column

Row counts may match while totals differ due to bad calculation.

---

# 14. Scenario Family D — Silver → Gold

## GOLD-001 — Wrong Status Filter

Canonical defect:

Incorrect:

```sql
WHERE order_status NOT IN ('CANCELLED', 'REINSTATED')
```

Expected:

```sql
WHERE order_status <> 'CANCELLED'
```

Expected:

```text
Silver correct
Gold understated
Power BI understated
```

## GOLD-002 — Gold Refresh Not Run

```text
Silver current
Gold stale
Power BI stale
```

Cause is refresh/orchestration, not business logic.

## GOLD-003 — Aggregation / Grain Bug

Introduce an incorrect join/grouping that duplicates or loses values.

## GOLD-004 — Wrong Business Rule Implementation

Example: implementation uses Order Date while approved definition says Invoice Date.

## GOLD-005 — Missing Partition

One date/region partition fails to reach Gold.

---

# 15. Scenario Family E — Power BI / Analytics

## PBI-001 — Semantic / Direct Lake Freshness Issue

Gold is current; Power BI presents stale values.

## PBI-002 — Incorrect DAX

Gold is correct; semantic metric is wrong.

Expected first break:

```text
Gold → Semantic Metric
```

## PBI-003 — Wrong Semantic Relationship

Example: date relationship uses wrong date field. Grand total may look correct while monthly context is wrong.

## PBI-004 — Report / Visual Filter Error

Semantic metric is correct but report/page/visual applies an unintended filter.

Expected first break:

```text
Semantic Model → Report Visual Context
```

---

# 16. Expected-Behavior Scenario

Add at least one scenario where there is **no technical defect**.

Example:

```text
Revenue decreased because:
- completed order volume fell,
- returns increased,
- all layers reconcile.
```

Expected result:

```text
Classification: EXPECTED_BEHAVIOR
Bug Created: No
```

This is mandatory. The investigator must not label every complaint as a defect.

---

# 17. Freshness as a First-Class Dimension

Track where available:

```text
latest_source_timestamp
latest_loaded_timestamp
last_refresh_start
last_refresh_end
expected_refresh_frequency
pipeline_run_status
row_count
high_watermark
```

The investigator must distinguish:

```text
stale data
```

from:

```text
incorrect transformation logic
```

---

# 18. Golden Scenario Definitions

Each scenario should have machine-readable ground truth used only by tests/evaluation.

Example:

```yaml
incident_id: GOLD-001
name: Reinstated orders excluded

defect_family: gold
defect_type: transformation_logic

expected_first_broken_boundary:
  upstream: silver.orders
  downstream: gold.fact_sales

expected_root_cause:
  reinstated_orders_excluded

expected_classification:
  TECHNICAL_DEFECT

expected_metric:
  Net Revenue

expected_owner:
  Data Platform

expected_evidence:
  - silver_total
  - gold_total
  - excluded_row_count
  - excluded_amount
  - transformation_filter
```

---

# 19. Evaluation Requirements

For each scenario evaluate:

```text
Correct report/metric
Correct lineage
Correct first broken boundary
Correct defect family
Correct root cause
Correct affected records
Correct financial/business impact
Correct downstream assets
Correct classification
Correct owner/team
```

Also evaluate:

```text
Did it avoid false bug creation?
Did it recognize expected behavior?
Did it distinguish stale data from bad transformation logic?
Did it remain unresolved rather than hallucinating when evidence was insufficient?
```

---

# 20. Deterministic Investigator Tools

Before AI orchestration, implement deterministic capabilities such as:

```text
get_report_metadata()
get_metric_definition()
get_upstream_lineage()
get_downstream_lineage()
query_semantic_metric()
query_gold_metric()
query_silver_metric()
query_bronze_metric()
query_source_metric()
compare_aggregates()
compare_row_counts()
compare_business_keys()
compare_timestamps()
find_first_divergence()
get_transform_definition()
get_refresh_history()
get_pipeline_run_history()
get_app_event()
get_order_audit()
calculate_impact()
find_affected_assets()
```

AI must call/use these tools rather than invent results.

---

# 21. First Divergence

Make **first broken boundary** a core concept.

Examples:

## Gold defect

```text
Azure SQL  ✓
Bronze     ✓
Silver     ✓
Gold       ✗
Power BI   ✗
```

Result:

```text
Silver → Gold
```

## Bronze stale

```text
Azure SQL  current
Bronze     stale
Silver     stale
Gold       stale
Power BI   stale
```

Result:

```text
Azure SQL → Bronze
```

## Power BI filter issue

```text
Azure SQL       ✓
Bronze          ✓
Silver          ✓
Gold            ✓
Semantic Model  ✓
Report Visual   ✗
```

Result:

```text
Semantic Model → Report Visual Context
```

Show this prominently in the UI.

---

# 22. AI Investigator Responsibilities

AI should handle:

- interpreting ticket text,
- extracting probable report/metric/date context,
- interpreting screenshot context,
- resolving ambiguous business language against discovered metadata,
- choosing the next deterministic tool,
- generating hypotheses,
- selecting verification tests,
- summarizing verified evidence,
- explaining root cause,
- drafting bug and notification content.

AI should **not** be the source of truth for:

- row counts,
- monetary totals,
- freshness timestamps,
- deterministic lineage,
- SQL results,
- refresh status,
- business impact.

---

# 23. Evidence Requirements

Every technical root-cause result should include evidence such as:

```text
Layer totals
Row counts
Key comparisons
Freshness timestamps
Transformation code
DAX expression
Report filter state
Pipeline run status
Application audit event
Sample affected business keys
```

Persist:

```text
type
source
asset
test/query
timestamp
result
related_hypothesis
```

---

# 24. Root-Cause UI

Example:

```text
ROOT CAUSE

Classification:
Technical Defect

First Broken Boundary:
Silver → Gold

Cause:
Gold transformation excludes REINSTATED orders.

Business Impact:
$517,842 understated revenue

Affected Records:
4,821 orders

Affected Assets:
- Executive Finance
- Regional Revenue
- Net Revenue
- Revenue Growth %

Confidence:
99%

Responsible Team:
Data Platform
```

Actions:

```text
View Evidence
View Lineage
View Impact
View Activity
View Created Bug
```

---

# 25. Expected-Behavior UI

Example:

```text
NO TECHNICAL DEFECT FOUND

Classification:
Expected Behavior

Explanation:
September Net Revenue is lower because completed-order volume
decreased and returns increased.

Technical Validation:
Azure SQL → Bronze → Silver → Gold → Power BI all reconcile.

Bug Created:
No
```

---

# 26. Bug Routing

For verified technical defects:

```text
Create engineering bug
Notify responsible team
Link bug to investigation
Attach evidence summary
```

For the POC use GitHub Issues, but design a generic:

```text
IssueTrackerProvider
```

Future providers:

```text
GitHub Issues
Azure DevOps Boards
Jira
ServiceNow
```

Do not hard-wire core investigation logic to GitHub.

---

# 27. Bug Content

Include:

```text
Title
Priority/severity
Investigation ID
Original ticket
Classification
First broken boundary
Root cause
Affected assets
Affected records
Business/financial impact
Evidence summary
Suggested technical direction
Links to lineage/evidence
```

---

# 28. Notifications

For verified technical defects notify the responsible team.

Use email for the POC, behind a generic:

```text
NotificationProvider
```

Future channels:

```text
Email
Teams
Slack
PagerDuty
ServiceNow
```

Example email:

```text
Subject:
Data Incident — Net Revenue understated by $517,842

Investigation INV-0042 identified a technical defect in the
Silver → Gold transformation.

4,821 REINSTATED orders are excluded.

Azure SQL, Bronze and Silver are correct.
Gold and downstream Power BI assets are affected.

Bug:
#123

Confidence:
99%
```

---

# 29. Ownership

Persist ownership where possible:

```text
Application owner
Pipeline owner
Silver owner
Gold owner
Semantic model owner
Report owner
Business metric owner
```

Routing should depend on the **first broken boundary/root cause**, not just the ticket submitter.

---

# 30. Human Gate After Bug Creation

After bug creation:

```text
INVESTIGATION COMPLETE
↓
BUG CREATED
↓
AWAITING HUMAN TRIAGE
```

Conceptual decisions:

```text
Approve future agent fix
Assign engineer
Backlog
Business review
Close / reject
```

Agent remediation is outside current scope.

---

# 31. Application Evidence

Reuse the existing transactional audit wherever possible.

Useful fields:

```text
event_type
order_id
request_id
correlation_id
action
previous_state
new_state
app_version
timestamp
result
```

Goal: distinguish application intent/behavior from Azure SQL persisted state.

---

# 32. Portfolio Demo Flow

The strongest demo should be ticket-driven.

1. Show the Order Operations portal.
2. Show an incorrect Power BI result.
3. Submit a ticket with report, description, optional expected value and screenshot.
4. Start the investigation.
5. Show the live investigation timeline.
6. Show the first broken boundary.
7. Show root cause, evidence and impact.
8. Show lineage.
9. Show the automatically created GitHub issue.
10. Show the team notification.
11. Stop. No autonomous fixing.

---

# 33. Demo Scenario Picker

For demo/testing mode only, allow choosing controlled scenarios:

```text
Revenue mismatch — Gold transformation bug
Stale Bronze
Stale Silver
Stale Gold
Duplicate transaction
Wrong application status
Silver transformation row loss
Incorrect DAX/report filter
Expected business behavior
```

The normal enterprise experience still begins with a ticket.

---

# 34. Reset Capability

Every injected defect requires:

```text
inject_defect(scenario_id)
reset_defect(scenario_id)
validate_baseline()
```

After reset, all baseline validations should return READY.

---

# 35. Audit Trail

Persist:

```text
ticket
attachments
resolved context
selected metric
lineage snapshot
tests executed
observations
hypotheses
evidence
classification
root cause
impact
created bug
notifications
timestamps
status changes
```

---

# 36. Suggested Investigation Status Model

```text
NEW
QUEUED
INVESTIGATING
WAITING_FOR_EVIDENCE
ROOT_CAUSE_FOUND
EXPECTED_BEHAVIOR
TECHNICAL_DEFECT
BUSINESS_REVIEW_REQUIRED
UNRESOLVED
BUG_CREATED
NOTIFIED
COMPLETE
```

Keep transitions auditable.

---

# 37. Confidence

Do not use an arbitrary LLM percentage.

Confidence should be based on evidence strength.

High confidence example:

- exact cross-layer reconciliation,
- deterministic first divergence,
- transformation contains matching defect,
- affected records exactly explain monetary difference.

Low confidence example:

- inferred lineage,
- missing source evidence,
- multiple unresolved hypotheses.

---

# 38. Automatic Bug Creation Policy

Create a bug automatically only when:

```text
classification = TECHNICAL_DEFECT
AND
root cause is verified
AND
first broken boundary is known
AND
supporting evidence exists
AND
confidence >= configured threshold
```

Otherwise route to human review or leave unresolved.

---

# 39. Immediate Engineering Sequence From Current Baseline

## Phase 4A — Metadata Connectors

1. Azure SQL metadata connector
2. Fabric metadata/definition connector
3. Power BI semantic/report metadata connector
4. normalized asset model
5. metadata persistence

## Phase 4B — Lineage

1. native Fabric relationships
2. Azure SQL → Bronze mapping
3. SQL/notebook transformation parsing
4. Bronze → Silver lineage
5. Silver → Gold lineage
6. Gold → semantic model lineage
7. measure dependencies
8. report/page/visual dependency where accessible
9. upstream/downstream traversal
10. lineage UI

## Phase 5A — Deterministic Investigator

1. report/metric resolver
2. source/Bronze/Silver/Gold/PBI query tools
3. aggregate comparison
4. key comparison
5. freshness comparison
6. first-divergence detection
7. transformation retrieval
8. impact traversal
9. evidence persistence

## Phase 5B — Ticket Interface

1. ticket form
2. report selector
3. optional page/metric selector
4. screenshot upload
5. investigation detail page
6. timeline
7. evidence tab
8. lineage tab
9. impact tab

## Phase 6 — AI Investigator

1. interpret ticket
2. resolve context
3. use deterministic tools
4. generate hypotheses
5. verify hypotheses
6. classify result
7. explain findings
8. draft bug/notification content

## Phase 7 — Initial Defect Lab

Start with:

```text
APP-001 Wrong status mapping
APP-002 Duplicate transaction
ING-001 Bronze stale
SIL-001 Silver stale
SIL-002 Silver row loss
GOLD-001 Reinstated-order filter
GOLD-002 Gold stale
PBI-002 Incorrect DAX/filter
EXPECTED-001 Expected business behavior
```

## Phase 7B — Routing

1. generic IssueTrackerProvider
2. GitHub Issues adapter
3. generic NotificationProvider
4. email adapter
5. asset/team ownership mapping
6. human-triage state after bug creation

---

# 40. Acceptance Criteria

## Ticket Experience

- [ ] User can select report.
- [ ] User can describe the issue.
- [ ] User can optionally specify metric/value/date.
- [ ] User can attach screenshots.
- [ ] Ticket starts an investigation.

## Metadata / Lineage

- [ ] Report resolves to semantic assets.
- [ ] Semantic metric resolves to Gold.
- [ ] Gold resolves to Silver.
- [ ] Silver resolves to Bronze.
- [ ] Bronze resolves to Azure SQL.
- [ ] Application evidence can be correlated when required.
- [ ] Final POC does not rely on manually hard-coded end-to-end lineage.

## Investigation

- [ ] Reproduce reported value where possible.
- [ ] Compare relevant layers.
- [ ] Detect stale layers.
- [ ] Identify first divergence.
- [ ] Retrieve relevant transformation/metadata.
- [ ] Verify root cause with deterministic evidence.
- [ ] Calculate impact.
- [ ] Identify downstream affected assets.

## Classification

- [ ] Recognize expected behavior.
- [ ] Recognize technical defect.
- [ ] Distinguish freshness from logic defect.
- [ ] Do not turn business-rule ambiguity into an automatic bug.
- [ ] Leave insufficient-evidence cases unresolved.

## Routing

- [ ] Verified technical defect creates a bug.
- [ ] Bug contains evidence and impact.
- [ ] Responsible team receives notification.
- [ ] Bug links to investigation.
- [ ] Workflow stops at human triage.

## Defect Lab

- [ ] Defects exist across multiple layers.
- [ ] Defects are injectable.
- [ ] Defects are resettable.
- [ ] Ground truth is stored separately.
- [ ] Investigator is evaluated against ground truth.

---

# 41. Core Product Statement

> The Data Investigator accepts a business-facing issue ticket, resolves the affected report/metric, traces its technical lineage from Power BI back through Fabric to the transactional application/source, determines the first point where expected behavior diverges, verifies the root cause with deterministic evidence, distinguishes expected behavior from real technical defects, quantifies downstream impact, and automatically routes verified defects to the responsible engineering team with a complete evidence package.

---

# 42. Scope Lock

```text
YES:
Ticket submission
Screenshot support
Report/metric resolution
Automated lineage
Cross-layer investigation
Refresh/freshness diagnosis
Application-level diagnosis
Deterministic evidence
AI interpretation/orchestration
Expected-behavior classification
Technical-defect classification
Impact analysis
Email notification
Bug creation
Human triage boundary

NO:
Agent writes fix
Agent creates code PR
Agent performs QA
Agent approves release
Agent deploys to production
Agent modifies production business logic
```

Do not cross this boundary until the investigation POC is reliable across the defect suite.
