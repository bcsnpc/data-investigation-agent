# Cross-System Data Investigation Agent — POC Engineering Specification

**Document type:** POC / Software Engineering Project Plan  
**Status:** Draft v1  
**Primary objective:** Prove that an investigation agent can trace a business discrepancy end-to-end across an application, operational database, Microsoft Fabric data platform, and Power BI — and identify the most likely root cause with evidence.

---

# 1. Executive Summary

This POC demonstrates an **environment-agnostic investigation engine** that can connect technical lineage across multiple systems and investigate a user-reported business discrepancy.

The first POC will use the following stack:

```text
Business Web App
      |
      v
Azure SQL Database
(application / transactional source)
      |
      v
Microsoft Fabric
  Bronze -> Silver -> Gold
      |
      v
Power BI Semantic Model
      |
      v
Power BI Report
```

The investigation agent sits across the stack:

```text
Ticket / User Question
        |
        v
Investigation Orchestrator
        |
        +---- Business App metadata/logs
        +---- Azure SQL
        +---- Fabric pipelines/notebooks/tables
        +---- Semantic model metadata
        +---- Power BI report metadata
        +---- Lineage Graph
        |
        v
Evidence + Root Cause + Impact Analysis + Recommended Fix
```

The POC is intentionally small, but it must be built as a **real software engineering project**:

- source controlled
- ticket driven
- modular
- testable
- reproducible
- observable
- documented
- deployable
- extensible

The goal is not to prove that an LLM can write SQL.

The goal is to prove that an investigation engine can:

1. understand a discrepancy,
2. determine which systems are relevant,
3. navigate technical lineage,
4. query evidence from multiple layers,
5. compare expected vs actual behavior,
6. rank root-cause hypotheses,
7. explain downstream impact,
8. produce a reproducible investigation report.

---

# 2. POC Product Vision

## 2.1 Problem

Modern analytics issues are rarely isolated to a single system.

A business user may report:

> "Order 10582 shows $1,250 in the application but $1,050 in the Power BI report."

The defect could originate from:

- the application UI,
- application business logic,
- Azure SQL source data,
- an ingestion pipeline,
- bronze transformations,
- silver business rules,
- gold aggregation logic,
- semantic model relationships,
- DAX measures,
- report filters,
- stale refreshes,
- row-level security,
- bad reference/master data.

Today, engineers manually jump across systems to investigate.

The POC will prove that an agent can automate a large part of that workflow.

---

# 3. POC Success Statement

The POC succeeds if a user can submit an investigation ticket such as:

> "Order ORD-10042 is $500 in the business application but only $400 in the Revenue Dashboard."

and the system can automatically:

1. identify the relevant metric/entity,
2. map the report value back to the Power BI model,
3. map the model to the Fabric Gold table,
4. trace Gold -> Silver -> Bronze -> Azure SQL,
5. inspect the application-side transaction,
6. detect where the values diverged,
7. identify the likely defect,
8. show evidence at every layer,
9. identify affected downstream artifacts,
10. return a concise root-cause report.

---

# 4. Non-Goals

The first POC will **not** attempt to:

- support every Azure/Fabric/Power BI API,
- automatically fix production issues,
- support dozens of source systems,
- provide enterprise identity federation,
- provide full data catalog functionality,
- replace Microsoft Purview,
- replace Databricks Unity Catalog,
- replace Power BI lineage view,
- replace Fabric Copilot,
- replace Genie,
- perform autonomous production writes,
- build a commercial multi-tenant SaaS platform.

The POC is about **investigation orchestration and cross-system reasoning**.

---

# 5. Core Differentiator

Microsoft Copilot, Databricks Genie, Power BI lineage, Fabric lineage, and catalog products are generally strongest **inside their own environments**.

The proposed engine operates across environments.

Example:

```text
Business application
       ↓
Azure SQL
       ↓
Fabric pipeline
       ↓
Bronze table
       ↓
Silver model
       ↓
Gold aggregate
       ↓
Power BI semantic model
       ↓
DAX measure
       ↓
Report visual
       ↓
Business ticket
```

The differentiator is not:

> "Ask questions about a table."

The differentiator is:

> "Investigate why a business result is wrong across the complete technical path."

---

# 6. POC Business Domain

Use a synthetic but realistic **Order Management / Sales Operations** business domain.

This domain is chosen because it naturally supports:

- transactional data,
- updates,
- status changes,
- discounts,
- refunds,
- customers,
- products,
- sales metrics,
- data quality defects,
- aggregation issues,
- Power BI reporting.

---

# 7. Business Web Application

A small web application will act as the operational business system.

## 7.1 Suggested application

**Order Operations Portal**

Functions:

- Create order
- Add order lines
- Update quantity
- Apply discount
- Change order status
- Cancel order
- Issue refund
- View customer
- View product
- View transaction history

## 7.2 Why build the application?

The application makes the demo much stronger.

Instead of saying:

> "Assume Azure SQL is an application source."

we demonstrate a real end-to-end system.

It also allows defects to originate at the application layer.

Example:

```text
Application UI displays: $500
Azure SQL stores:         $400
```

or:

```text
Application API writes incorrect discount logic.
```

This gives the investigation agent multiple possible failure domains.

---

# 8. Proposed Technology Stack

## Frontend

Recommended:

- Next.js
- TypeScript
- React
- Tailwind CSS

Alternative:

- React + Vite

## Backend

Recommended:

- Next.js API routes / Server Actions for POC

or

- Python FastAPI

Use FastAPI if the investigation engine is primarily Python.

## Operational Database

- Azure SQL Database

## Data Platform

- Microsoft Fabric

Layers:

- Bronze Lakehouse
- Silver Warehouse/Lakehouse
- Gold Warehouse/Lakehouse

## Analytics

- Power BI semantic model
- 2–3 Power BI reports

## Agent / Investigation Engine

Recommended:

- Python
- FastAPI
- Pydantic
- graph abstraction
- SQL connectors
- Microsoft APIs
- LLM provider abstraction

## Metadata / State

POC options:

- PostgreSQL
- SQLite for local development
- Azure SQL
- Fabric SQL endpoint

Recommended:

**PostgreSQL or Azure SQL**

Store:

- lineage nodes
- lineage edges
- investigation runs
- evidence
- tickets
- connector configuration
- agent execution history

---

# 9. High-Level Architecture

```text
+-----------------------------------------------------------+
|                     Investigation UI                      |
| Ticket | Investigation Run | Evidence | Lineage | Impact |
+-------------------------------+---------------------------+
                                |
                                v
+-----------------------------------------------------------+
|                Investigation Orchestrator                 |
|                                                           |
|  Intent Parser                                            |
|  Investigation Planner                                   |
|  Evidence Collector                                      |
|  Hypothesis Generator                                    |
|  Hypothesis Validator                                    |
|  Root Cause Ranker                                       |
|  Impact Analyzer                                         |
|  Report Generator                                        |
+-----------+---------------+---------------+---------------+
            |               |               |
            v               v               v
       Connector Layer   Lineage Engine   LLM Gateway
            |
   +--------+--------+----------+----------+---------+
   |                 |          |                    |
   v                 v          v                    v
Business App     Azure SQL    Fabric            Power BI
Logs/API         metadata     metadata          metadata
SQL data         schema       tables            model
                              pipelines         measures
                              notebooks         visuals
```

---

# 10. Core Engineering Principle

The LLM must **not be the system of record**.

The platform should be deterministic wherever possible.

Use LLMs for:

- interpreting tickets,
- entity mapping,
- planning,
- hypothesis generation,
- explanation,
- ambiguity resolution.

Use deterministic services for:

- SQL execution,
- metadata retrieval,
- lineage traversal,
- schema matching,
- API calls,
- comparison,
- validation,
- scoring,
- evidence storage.

---

# 11. Repository Structure

Recommended monorepo:

```text
data-investigator/
│
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── ARCHITECTURE.md
├── CHANGELOG.md
├── .env.example
├── .gitignore
├── docker-compose.yml
│
├── docs/
│   ├── product/
│   │   ├── vision.md
│   │   ├── poc-scope.md
│   │   └── user-stories.md
│   │
│   ├── architecture/
│   │   ├── system-context.md
│   │   ├── container-design.md
│   │   ├── investigation-engine.md
│   │   └── lineage-model.md
│   │
│   ├── adr/
│   │   ├── ADR-001-monorepo.md
│   │   ├── ADR-002-lineage-graph.md
│   │   └── ADR-003-llm-abstraction.md
│   │
│   ├── runbooks/
│   │   ├── local-development.md
│   │   ├── deployment.md
│   │   └── demo-runbook.md
│   │
│   └── test-scenarios/
│
├── apps/
│   ├── business-app/
│   │   ├── frontend/
│   │   └── backend/
│   │
│   └── investigator-ui/
│
├── services/
│   ├── investigation-api/
│   ├── investigation-engine/
│   ├── lineage-service/
│   └── metadata-service/
│
├── connectors/
│   ├── azure_sql/
│   ├── fabric/
│   ├── powerbi/
│   └── business_app/
│
├── shared/
│   ├── models/
│   ├── config/
│   ├── logging/
│   └── security/
│
├── data/
│   ├── synthetic/
│   ├── seeds/
│   └── defect-scenarios/
│
├── infra/
│   ├── terraform/
│   ├── azure/
│   └── scripts/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── end_to_end/
│   └── regression/
│
└── .github/
    └── workflows/
```

---

# 12. Synthetic Data Model

## Core entities

### Customer

```text
customer_id
customer_name
customer_segment
state
country
created_at
```

### Product

```text
product_id
product_name
category
subcategory
unit_price
active_flag
```

### Order

```text
order_id
customer_id
order_date
status
subtotal
discount_amount
tax_amount
total_amount
created_at
updated_at
```

### Order Line

```text
order_line_id
order_id
product_id
quantity
unit_price
discount_amount
line_total
```

### Payment

```text
payment_id
order_id
payment_type
amount
payment_status
payment_date
```

### Refund

```text
refund_id
order_id
refund_amount
refund_reason
refund_date
```

---

# 13. Synthetic Data Requirements

Generate enough data to feel realistic.

POC target:

```text
Customers       5,000
Products          500
Orders         50,000
Order Lines    150,000+
Payments        50,000+
Refunds          2,000+
```

Include:

- different dates,
- customer segments,
- product categories,
- discounts,
- cancelled orders,
- returned orders,
- refunds,
- partial refunds,
- duplicate events,
- late arriving records,
- null values,
- boundary values.

Use a deterministic random seed.

Example:

```python
SEED = 42
```

This ensures defects and expected results are reproducible.

---

# 14. Azure SQL — Application Source

Azure SQL represents the transactional application database.

Schemas:

```text
app.customers
app.products
app.orders
app.order_lines
app.payments
app.refunds
app.audit_log
```

The web application reads/writes primarily through this database.

---

# 15. Application Audit Log

Every business action should generate an audit event.

Example:

```json
{
  "event_id": "evt_10344",
  "entity_type": "order",
  "entity_id": "ORD-10042",
  "operation": "UPDATE",
  "field": "discount_amount",
  "old_value": 0,
  "new_value": 100,
  "user_id": "demo_user",
  "timestamp": "2026-09-12T13:20:04Z"
}
```

This becomes extremely useful for agent investigations.

---

# 16. Fabric Architecture

## Bronze

Purpose:

> Raw ingestion from Azure SQL with minimal transformation.

Example:

```text
bronze.customers
bronze.products
bronze.orders
bronze.order_lines
bronze.payments
bronze.refunds
```

Add technical columns:

```text
_ingestion_timestamp
_source_system
_batch_id
```

---

# 17. Silver Layer

Silver represents cleaned, conformed business entities.

Examples:

```text
silver.dim_customer
silver.dim_product
silver.fact_order
silver.fact_order_line
silver.fact_payment
silver.fact_refund
```

Business rules are applied here.

Examples:

- normalize order statuses
- remove invalid records
- calculate net order amount
- join product reference data
- standardize dates
- deduplicate events

---

# 18. Gold Layer

Gold contains reporting-ready models.

Examples:

```text
gold.sales_daily
gold.sales_by_product
gold.sales_by_customer
gold.order_summary
gold.refund_summary
```

Example metric:

```text
Net Revenue =
Order Amount
- Refund Amount
```

---

# 19. Power BI Scope

Build 2–3 reports.

## Report 1 — Executive Sales Dashboard

Visuals:

- Total Revenue
- Net Revenue
- Order Count
- Average Order Value
- Revenue Trend
- Revenue by Category
- Revenue by State

## Report 2 — Order Operations

Visuals:

- Order Detail
- Order Status
- Cancelled Orders
- Refund Amount
- Order Drillthrough

## Report 3 — Product Performance

Visuals:

- Product Revenue
- Units Sold
- Discount %
- Refund %
- Category Performance

---

# 20. Semantic Model

Core tables:

```text
DimDate
DimCustomer
DimProduct
FactOrder
FactOrderLine
FactRefund
```

Example measures:

```DAX
Revenue =
SUM(FactOrder[OrderAmount])

Refund Amount =
SUM(FactRefund[RefundAmount])

Net Revenue =
[Revenue] - [Refund Amount]

Order Count =
DISTINCTCOUNT(FactOrder[OrderID])
```

---

# 21. Technical Lineage Model

The POC must create its own normalized lineage graph.

Do not depend exclusively on one vendor's lineage view.

## Node examples

```text
application
api_endpoint
database
schema
table
column
pipeline
notebook
sql_query
fabric_table
semantic_model
semantic_table
semantic_column
measure
report
page
visual
metric
```

## Edge examples

```text
WRITES_TO
READS_FROM
INGESTS_FROM
TRANSFORMS_TO
DERIVED_FROM
USES_COLUMN
USES_MEASURE
FEEDS
DISPLAYED_IN
DEPENDS_ON
```

---

# 22. Example Lineage

```text
Business App
   |
   | WRITES_TO
   v
app.orders.total_amount
   |
   | INGESTS_FROM
   v
bronze.orders.total_amount
   |
   | TRANSFORMS_TO
   v
silver.fact_order.net_amount
   |
   | DERIVED_FROM
   v
gold.order_summary.net_revenue
   |
   | FEEDS
   v
FactOrder[NetRevenue]
   |
   | USED_BY
   v
[Net Revenue]
   |
   | DISPLAYED_IN
   v
Executive Sales Dashboard
   |
   v
Net Revenue Card
```

---

# 23. Lineage Storage Model

For the POC, a relational graph representation is sufficient.

## lineage_node

```text
node_id
node_type
system
name
qualified_name
metadata_json
created_at
updated_at
```

## lineage_edge

```text
edge_id
source_node_id
target_node_id
relationship_type
metadata_json
confidence
created_at
```

A dedicated graph database can be evaluated later.

---

# 24. Investigation Ticket Model

Example:

```json
{
  "ticket_id": "INC-1007",
  "title": "Order amount mismatch",
  "description": "ORD-10042 shows $500 in the application but $400 in Revenue Dashboard.",
  "reported_by": "demo_user",
  "priority": "P2",
  "status": "OPEN",
  "created_at": "2026-09-12T14:00:00Z"
}
```

---

# 25. Investigation Workflow

The system should implement the following workflow.

```text
1. Ticket submitted
       ↓
2. Parse business entities / metrics
       ↓
3. Identify relevant report / visual
       ↓
4. Resolve metric lineage
       ↓
5. Build investigation plan
       ↓
6. Query evidence from each layer
       ↓
7. Compare values
       ↓
8. Detect divergence point
       ↓
9. Generate hypotheses
       ↓
10. Validate hypotheses
       ↓
11. Rank root cause
       ↓
12. Determine downstream impact
       ↓
13. Generate investigation report
```

---

# 26. Agent Components

## 26.1 Ticket Interpreter

Input:

```text
ORD-10042 shows $500 in application but $400 in Revenue Dashboard.
```

Output:

```json
{
  "entity_type": "order",
  "entity_id": "ORD-10042",
  "metric": "revenue",
  "systems": [
    "business_app",
    "power_bi"
  ],
  "issue_type": "value_mismatch"
}
```

---

# 27. Investigation Planner

The planner generates explicit steps.

Example:

```json
{
  "steps": [
    "Get order value from application API",
    "Get source order row from Azure SQL",
    "Trace revenue metric lineage",
    "Query Bronze order row",
    "Query Silver fact row",
    "Query Gold aggregate row",
    "Query semantic model value",
    "Compare values",
    "Identify first divergence"
  ]
}
```

---

# 28. Evidence Collector

Evidence must be stored, not only summarized.

Example:

```json
{
  "source": "azure_sql",
  "query": "SELECT ...",
  "result": {
    "order_id": "ORD-10042",
    "total_amount": 500
  },
  "timestamp": "...",
  "status": "SUCCESS"
}
```

---

# 29. Divergence Detection

Example evidence:

```text
Application       500
Azure SQL         500
Bronze            500
Silver            400
Gold              400
Semantic Model    400
Power BI          400
```

The system should conclude:

```text
First divergence = Silver transformation.
```

This is stronger than asking an LLM to guess.

---

# 30. Hypothesis Engine

Example hypotheses:

```text
H1: Silver transformation incorrectly excludes order-line discount.
H2: Order status mapping caused partial exclusion.
H3: Duplicate removal removed a valid line.
H4: Fabric pipeline used stale source data.
```

---

# 31. Hypothesis Validation

Each hypothesis should have explicit tests.

Example:

```text
H1 test:
Compare Bronze line totals with Silver calculation.

Expected:
500

Actual:
400

Difference:
100

Check transformation code.

Finding:
CASE expression subtracts order discount twice.
```

---

# 32. Root Cause Report

Example:

```text
Root Cause
----------

The discrepancy originates in the Silver transformation
silver.fact_order.

Order ORD-10042 is stored correctly as $500 in:
- Business application
- Azure SQL
- Bronze

During Silver transformation, the $100 order-level discount
is applied twice.

Expected Silver value: $500
Actual Silver value:   $400

Gold and Power BI correctly reflect the incorrect Silver value.

Confidence: 97%
```

---

# 33. Impact Analysis

Once a defect node is found, traverse downstream lineage.

Example:

```text
silver.fact_order.net_amount
      |
      +-> gold.order_summary
      |
      +-> gold.sales_daily
      |
      +-> semantic model FactOrder
      |
      +-> Revenue measure
      |
      +-> Net Revenue measure
      |
      +-> Executive Dashboard
      |
      +-> Product Performance Report
```

The agent should report:

```text
Potentially impacted artifacts:
2 Gold tables
1 semantic model
3 measures
2 reports
7 visuals
```

---

# 34. POC Defect Scenarios

The POC must include deliberately injected defects.

At least **8 scenarios** should be created.

---

## Scenario 1 — Application UI Bug

Database:

```text
500
```

UI:

```text
550
```

Root cause:

Front-end formatting/calculation defect.

---

## Scenario 2 — Application API Bug

Application API writes incorrect discount.

Expected:

```text
500
```

Stored:

```text
450
```

Root cause:

Backend business logic.

---

## Scenario 3 — Source Data Bug

Incorrect product price entered into Azure SQL.

Root cause:

Operational data issue.

---

## Scenario 4 — Bronze Ingestion Failure

A record is missing from Bronze.

Root cause:

incremental watermark issue.

---

## Scenario 5 — Silver Transformation Bug

Discount deducted twice.

Root cause:

SQL / notebook transformation.

---

## Scenario 6 — Gold Aggregation Bug

Cancelled orders included in Revenue.

Root cause:

Gold aggregation filter.

---

## Scenario 7 — Semantic Model Bug

Incorrect relationship causes double counting.

Root cause:

Power BI model.

---

## Scenario 8 — DAX Measure Bug

Incorrect measure logic.

Example:

```DAX
Revenue =
SUM(FactOrder[GrossAmount])
```

instead of net revenue.

---

## Optional Scenario 9 — Refresh Delay

Application:

```text
latest
```

Power BI:

```text
old
```

Root cause:

dataset refresh has not completed.

---

## Optional Scenario 10 — Report Filter Bug

The model is correct but a visual-level filter changes the result.

---

# 35. POC UI

Build an investigator web interface.

Pages:

```text
/dashboard
/tickets
/tickets/{id}
/investigations/{id}
/lineage
/systems
```

---

# 36. Investigation Screen

Recommended layout:

```text
----------------------------------------------------
Ticket INC-1007
Order revenue mismatch
----------------------------------------------------

Status: Root Cause Found
Confidence: 97%

Summary
----------------------------------------------------
Mismatch originates in Silver transformation.

Evidence Timeline
----------------------------------------------------
Application        $500   ✓
Azure SQL          $500   ✓
Bronze             $500   ✓
Silver             $400   ✗
Gold               $400
Semantic Model     $400
Power BI           $400

Root Cause
----------------------------------------------------
Discount applied twice in silver.fact_order.

Affected Assets
----------------------------------------------------
gold.order_summary
Net Revenue measure
Executive Sales Dashboard

Investigation Steps
----------------------------------------------------
✓ Application checked
✓ Source checked
✓ Bronze checked
✓ Silver checked
✓ Gold checked
✓ Semantic model checked

Technical Evidence
----------------------------------------------------
[SQL]
[Pipeline]
[Transformation]
[DAX]
```

---

# 37. Lineage UI

Show a graph:

```text
App
 ↓
Azure SQL
 ↓
Bronze
 ↓
Silver
 ↓
Gold
 ↓
Semantic Model
 ↓
Measure
 ↓
Report
```

Highlight the failure node.

Example:

```text
App ✓
 ↓
Azure SQL ✓
 ↓
Bronze ✓
 ↓
Silver ✕  <-- ROOT CAUSE
 ↓
Gold
 ↓
Power BI
```

---

# 38. Ticket Demo Experience

For the POC, create a simple ticket UI.

Ticket fields:

```text
Title
Description
Affected report
Entity ID
Expected value
Actual value
Priority
Screenshot
```

A screenshot attachment can be supported later.

The initial POC can use text-only evidence.

---

# 39. Investigation Engine Interfaces

Define stable interfaces.

Example:

```python
class DataConnector:
    def execute_query(self, query):
        ...

    def get_schema(self):
        ...

    def get_metadata(self):
        ...
```

```python
class LineageProvider:
    def discover_nodes(self):
        ...

    def discover_edges(self):
        ...

    def get_upstream(self, node_id):
        ...

    def get_downstream(self, node_id):
        ...
```

```python
class InvestigationTool:
    def execute(self, context):
        ...
```

This makes the engine extensible.

---

# 40. Connector Architecture

Each connector should implement a common contract.

```text
Connector
│
├── authenticate()
├── health_check()
├── discover_metadata()
├── execute()
└── normalize_response()
```

POC connectors:

```text
AzureSqlConnector
FabricConnector
PowerBIConnector
BusinessAppConnector
```

---

# 41. LLM Abstraction

Never hardcode one LLM vendor deeply into the system.

Interface:

```python
class LLMProvider:
    def generate(self, messages, tools=None):
        ...
```

Possible implementations:

```text
OpenAIProvider
AzureOpenAIProvider
AnthropicProvider
```

The POC can initially implement one provider.

---

# 42. LLM Cost Controls

Design the POC with commercial economics in mind.

Use:

- deterministic lineage traversal,
- metadata caching,
- schema caching,
- result caching,
- prompt templates,
- compact context,
- structured outputs,
- smaller models for classification,
- larger models only for reasoning,
- token usage logging.

Do not send entire schemas repeatedly.

---

# 43. Cache Layers

Cache:

```text
database schema
Fabric metadata
Power BI metadata
lineage graph
report/model relationships
previous query results
```

Potential technologies:

- Redis
- in-memory cache for POC
- database table

---

# 44. Security

Even for a POC, security must be designed correctly.

Principles:

- no credentials in source code,
- environment variables / secret store,
- read-only investigation credentials,
- least privilege,
- parameterized SQL,
- API authentication,
- input validation,
- audit logging,
- query timeout,
- row/result limits.

---

# 45. Read-Only by Default

The investigation engine must initially have **zero write capability** to production-like systems.

Allowed:

```text
SELECT
metadata retrieval
lineage retrieval
log retrieval
```

Not allowed:

```text
UPDATE
DELETE
INSERT
DROP
ALTER
```

---

# 46. Query Guard

Implement a SQL safety layer.

Reject:

```text
DELETE
UPDATE
INSERT
DROP
TRUNCATE
ALTER
MERGE
EXEC
```

Allow controlled `SELECT`.

---

# 47. Observability

Every investigation should create structured logs.

Example:

```json
{
  "investigation_id": "INV-1007",
  "step": "query_silver",
  "system": "fabric",
  "duration_ms": 218,
  "status": "SUCCESS",
  "rows": 1
}
```

Track:

- execution time,
- connector latency,
- failed calls,
- LLM latency,
- LLM tokens,
- SQL queries,
- tool usage,
- hypothesis count,
- investigation outcome.

---

# 48. Investigation Run State

States:

```text
CREATED
PLANNING
COLLECTING_EVIDENCE
VALIDATING
ROOT_CAUSE_FOUND
INCONCLUSIVE
FAILED
COMPLETED
```

---

# 49. Testing Strategy

The project must have multiple test levels.

---

# 50. Unit Tests

Test:

- entity parsing
- lineage traversal
- graph functions
- comparison logic
- query guard
- root cause ranking
- config handling
- metric mapping

Target:

```text
80%+ coverage for core engine
```

---

# 51. Integration Tests

Test real interactions between:

```text
API + DB
Connector + Azure SQL
Connector + Fabric
Connector + Power BI
Engine + lineage database
```

---

# 52. Contract Tests

Each connector must satisfy the connector interface.

Example:

```text
authenticate
health_check
discover_metadata
execute
normalize
```

---

# 53. End-to-End Tests

Each injected defect becomes an E2E test.

Example:

```text
Given:
Silver discount bug exists.

When:
Ticket says ORD-10042 mismatch.

Then:
Root cause should identify Silver transformation.
```

---

# 54. Regression Suite

Every resolved defect scenario is permanently added to the regression suite.

This is important.

The system should improve without breaking previous investigation capability.

---

# 55. Golden Investigation Dataset

Maintain expected outputs.

Example:

```json
{
  "scenario": "silver_double_discount",
  "expected_root_system": "fabric",
  "expected_root_layer": "silver",
  "expected_object": "silver.fact_order",
  "expected_confidence_min": 0.8
}
```

---

# 56. CI/CD

Use GitHub Actions.

Pipeline:

```text
Pull Request
   ↓
Lint
   ↓
Type Check
   ↓
Unit Tests
   ↓
Security Checks
   ↓
Build
   ↓
Integration Tests
   ↓
Artifact Creation
```

Main branch:

```text
merge
 ↓
deploy dev
 ↓
smoke tests
```

---

# 57. Branching Strategy

Keep it simple.

```text
main
feature/*
bugfix/*
```

Every change through pull request.

No direct commits to `main`.

---

# 58. Pull Request Template

Each PR should include:

```text
What changed?

Why?

Related ticket

How tested?

Screenshots

Risks

Rollback plan
```

---

# 59. Ticket-Driven Development

Use GitHub Issues / Linear / Jira.

Recommended hierarchy:

```text
Epic
  └── Feature
        └── Story
              └── Task
```

Example:

```text
EPIC-01 Investigation Engine
  FEAT-01 Ticket Parsing
    STORY-01 Extract order identifiers
      TASK-01 Implement parser
      TASK-02 Add unit tests
```

---

# 60. Initial Epics

## EPIC-01 — Engineering Foundation

Includes:

- repo
- CI
- formatting
- linting
- environment config
- logging
- contribution standards

---

## EPIC-02 — Synthetic Business Application

Includes:

- UI
- API
- Azure SQL
- orders
- audit trail

---

## EPIC-03 — Synthetic Data Generator

Includes:

- customers
- products
- orders
- refunds
- deterministic generation
- defect injection

---

## EPIC-04 — Fabric Data Platform

Includes:

- ingestion
- Bronze
- Silver
- Gold
- pipeline orchestration

---

## EPIC-05 — Power BI

Includes:

- semantic model
- measures
- reports
- drillthrough

---

## EPIC-06 — Metadata Connectors

Includes:

- Azure SQL
- Fabric
- Power BI
- business app

---

## EPIC-07 — Lineage Engine

Includes:

- node model
- edge model
- metadata normalization
- traversal

---

## EPIC-08 — Investigation Engine

Includes:

- ticket parser
- planner
- evidence engine
- hypothesis engine
- validator
- root cause scorer

---

## EPIC-09 — Investigation UI

Includes:

- tickets
- run status
- evidence
- root cause
- lineage
- impact

---

## EPIC-10 — Defect Lab

Includes:

- controlled bug injection
- scenario reset
- expected outcomes
- regression tests

---

# 61. Example First Sprint

## Sprint Goal

Build a working vertical slice:

```text
Web App
   ↓
Azure SQL
   ↓
Fabric Bronze
   ↓
Fabric Silver
   ↓
Fabric Gold
   ↓
Power BI
```

No AI yet.

Deliverable:

One order can be traced manually across every layer.

---

# 62. Sprint 1 Tickets

```text
ENG-001 Initialize monorepo
ENG-002 Configure linting and formatting
ENG-003 Configure GitHub Actions
APP-001 Create order portal
APP-002 Create Azure SQL schema
DATA-001 Build synthetic data generator
FAB-001 Build Bronze ingestion
FAB-002 Build Silver transformation
FAB-003 Build Gold transformation
PBI-001 Build semantic model
PBI-002 Build Sales Dashboard
DOC-001 Create architecture documentation
```

---

# 63. Sprint 2 Goal

Automate technical lineage.

Deliverable:

Given:

```text
Net Revenue
```

the engine can return:

```text
Power BI measure
 -> semantic column
 -> Gold
 -> Silver
 -> Bronze
 -> Azure SQL
```

---

# 64. Sprint 3 Goal

Build deterministic investigation logic.

No LLM dependency required for the core path.

Given:

```text
Order ID
```

compare its value across systems.

Return the first divergence.

---

# 65. Sprint 4 Goal

Add LLM reasoning.

Use LLM for:

- ticket interpretation,
- investigation planning,
- hypothesis generation,
- explanation.

The LLM operates on structured evidence gathered by the deterministic engine.

---

# 66. Sprint 5 Goal

Build polished demo UI and defect lab.

Add:

- ticket screen,
- investigation timeline,
- evidence,
- lineage visualization,
- impact view,
- seeded defect scenarios.

---

# 67. Definition of Done

A feature is not done merely because code works locally.

It must include:

- implementation,
- unit tests,
- documentation,
- logging,
- error handling,
- code review,
- passing CI,
- acceptance criteria validation.

---

# 68. Architecture Decision Records

Important architecture choices should be documented.

Example:

```text
ADR-001 Monorepo
ADR-002 Python investigation engine
ADR-003 Relational lineage graph for POC
ADR-004 Read-only system connectors
ADR-005 LLM provider abstraction
ADR-006 Synthetic defect framework
```

---

# 69. Error Handling

Connectors should return standardized failures.

Example:

```json
{
  "success": false,
  "error_type": "AUTHENTICATION_ERROR",
  "system": "fabric",
  "message": "...",
  "retryable": false
}
```

The agent should never invent missing evidence.

If a system cannot be queried, say so.

---

# 70. Confidence Model

Root cause confidence should be evidence-driven.

Example scoring inputs:

```text
First divergence found                 +40
Transformation code supports cause     +25
Reproduction successful                +20
Alternative hypotheses eliminated      +10
Lineage confidence                     +5
```

Example output:

```text
Confidence: 95%
```

Do not let the LLM arbitrarily choose confidence.

---

# 71. Investigation Explainability

Every conclusion must answer:

```text
What failed?

Where did it fail?

What evidence proves it?

Why is this considered root cause?

What downstream artifacts are affected?

What should be fixed?

How can the fix be verified?
```

---

# 72. Example Final Investigation Output

```text
Incident
-------
INC-1007 — Order revenue mismatch

Entity
------
ORD-10042

Reported
--------
Application: $500
Power BI:    $400

Finding
-------
The source transaction is correct.

Application          $500
Azure SQL            $500
Bronze               $500
Silver               $400
Gold                 $400
Semantic Model       $400
Power BI             $400

Root Cause
----------
silver.fact_order transformation applies the
order-level discount twice.

Technical Evidence
------------------
Transformation:
order_total - discount - discount

Expected:
500

Actual:
400

Impact
------
Affected downstream objects:
- gold.order_summary
- gold.sales_daily
- FactOrder
- Revenue measure
- Net Revenue measure
- Executive Sales Dashboard

Recommendation
--------------
Correct the Silver transformation and rerun the
affected batch.

Verification
------------
After reload:
ORD-10042 should equal $500 across all layers.

Confidence
----------
97%
```

---

# 73. Demo Script

The POC demo should tell a story.

## Step 1

Open the business application.

Show:

```text
ORD-10042 = $500
```

---

## Step 2

Open the Power BI report.

Show:

```text
ORD-10042 = $400
```

---

## Step 3

Create ticket.

```text
Order ORD-10042 shows $500 in the application,
but Revenue Dashboard shows $400.
```

Click:

```text
Investigate
```

---

## Step 4

Show investigation execution.

```text
✓ Identified order entity
✓ Identified Revenue metric
✓ Resolved Power BI lineage
✓ Checked semantic model
✓ Checked Gold
✓ Checked Silver
✓ Checked Bronze
✓ Checked Azure SQL
✓ Checked application
```

---

## Step 5

Show divergence.

```text
Application      500
Azure SQL        500
Bronze           500
Silver           400  <-- divergence
Gold             400
Power BI          400
```

---

## Step 6

Show root cause.

```text
Discount applied twice in Silver transformation.
```

---

## Step 7

Show lineage and impact.

Highlight:

```text
silver.fact_order
```

and all downstream affected assets.

This is the "wow" moment.

---

# 74. POC Acceptance Criteria

The POC is considered successful when:

### AC-01

A real synthetic business app writes transactions to Azure SQL.

### AC-02

Fabric ingests source data through Bronze, Silver, and Gold.

### AC-03

Power BI reports operate from Gold.

### AC-04

Technical lineage exists across all layers.

### AC-05

A ticket can trigger an investigation.

### AC-06

The engine can automatically compare values across layers.

### AC-07

The first divergence is detected correctly.

### AC-08

At least 5 defect scenarios are correctly diagnosed.

Target:

```text
8 scenarios
```

### AC-09

Downstream impact is identified.

### AC-10

Evidence is visible to the user.

### AC-11

The root-cause result is reproducible.

### AC-12

The repository has tests, CI, documentation, and structured tickets.

---

# 75. POC Quality Metrics

Track:

```text
Root Cause Accuracy
Investigation Completion Rate
Mean Investigation Time
Connector Failure Rate
False Root Cause Rate
LLM Token Usage
LLM Cost per Investigation
Lineage Coverage
Evidence Coverage
```

Target POC metrics:

```text
Root Cause Accuracy       >= 80%
Lineage Coverage          >= 90%
Evidence-backed findings  100%
```

---

# 76. Performance Targets

POC target:

```text
Ticket parsing          < 3 sec
Lineage resolution      < 3 sec
Individual data query   < 5 sec
Typical investigation   < 30 sec
```

These are design targets, not hard production SLAs.

---

# 77. Data Reset Strategy

Demo environments need reliable resets.

Create:

```text
scripts/reset_demo.py
```

Functions:

```text
reset source data
reload clean baseline
inject selected bug
trigger Fabric refresh
validate state
```

Example:

```bash
python reset_demo.py --scenario silver-double-discount
```

---

# 78. Defect Injection Framework

Represent scenarios declaratively.

Example:

```yaml
id: silver-double-discount
layer: silver
object: silver.fact_order
entity_id: ORD-10042

expected:
  value: 500

defect:
  type: transformation_logic

expected_root_cause:
  system: fabric
  layer: silver
```

This creates repeatable demos and automated tests.

---

# 79. Engineering Documentation

Minimum docs:

```text
README.md
ARCHITECTURE.md
CONTRIBUTING.md
SECURITY.md
LOCAL_DEVELOPMENT.md
DEPLOYMENT.md
DEMO_RUNBOOK.md
LINEAGE_MODEL.md
INVESTIGATION_ENGINE.md
```

---

# 80. README Structure

The main README should contain:

```text
Project overview
Architecture diagram
Features
Demo screenshots
Quick start
Technology stack
Repository structure
Local setup
Testing
Sample investigation
Roadmap
```

---

# 81. Screenshots for Portfolio

Capture:

1. Business application order screen
2. Power BI discrepancy
3. Ticket submission
4. Investigation running
5. Evidence timeline
6. Lineage graph
7. Root cause result
8. Impact analysis
9. GitHub issue board
10. CI pipeline

These prove this is a software-engineering project, not an isolated notebook.

---

# 82. Portfolio Presentation

The portfolio story should be:

> Built an end-to-end AI-assisted data investigation platform capable of tracing business discrepancies from a Power BI report back through semantic models, Microsoft Fabric transformations, Azure SQL, and the originating application.

Emphasize:

- distributed-system reasoning,
- metadata integration,
- lineage,
- investigation automation,
- agent orchestration,
- platform engineering,
- observability,
- testing,
- architecture,
- software engineering.

Do not market it merely as:

> "AI chatbot for Power BI."

---

# 83. Distribution Strategy — POC

Initially distribute as:

```text
GitHub repository
+
deployed demo web application
+
architecture documentation
+
demo video
+
sample defect scenarios
```

---

# 84. Future Distribution — Engine Model

Long term, separate the product into:

```text
Investigation Engine
        +
Connector SDK
        +
Configuration
        +
UI
```

A company should be able to configure:

```text
their source systems
their Fabric workspaces
their semantic models
their terminology
their investigation rules
their lineage sources
their ticket systems
```

without rewriting the core engine.

---

# 85. Configuration-Driven Design

Example:

```yaml
systems:

  application:
    type: custom_api

  source_database:
    type: azure_sql

  data_platform:
    type: microsoft_fabric

  analytics:
    type: power_bi
```

Later:

```yaml
data_platform:
  type: databricks
```

or:

```yaml
analytics:
  type: tableau
```

The investigation engine remains unchanged.

---

# 86. Future Connector SDK

Eventually expose:

```python
class ConnectorSDK:
    def discover_metadata(self):
        pass

    def query(self):
        pass

    def lineage(self):
        pass
```

Third parties can create connectors.

Examples:

```text
Snowflake
Databricks
BigQuery
Tableau
Looker
dbt
Salesforce
SAP
ServiceNow
PostgreSQL
Oracle
```

---

# 87. Future Ticket Integrations

Later:

```text
ServiceNow
Jira
Azure DevOps
Slack
Microsoft Teams
Email
```

Example future workflow:

```text
ServiceNow Incident
       ↓
Investigation Engine
       ↓
Root Cause
       ↓
Comment automatically added to incident
```

---

# 88. Future Agent Modes

Potential modes:

```text
Data discrepancy investigation
Refresh failure investigation
Missing record investigation
Metric definition investigation
Pipeline failure investigation
Data quality investigation
Schema change impact analysis
Performance investigation
Release validation
```

---

# 89. Future Commercial Architecture

Eventually:

```text
Control Plane
    |
    +-- Tenant configuration
    +-- Auth
    +-- Billing
    +-- Connector registry
    +-- Agent policies
    +-- Observability

Customer Environment
    |
    +-- Secure connector runtime
    +-- Metadata scanner
    +-- Query executor
```

But none of this is required for POC.

---

# 90. POC Phase Plan

## Phase 0 — Engineering Foundation

Deliverables:

- repository
- issue templates
- PR templates
- CI
- local development
- logging
- config
- documentation skeleton

---

## Phase 1 — Business System

Deliverables:

- Order Operations web app
- Azure SQL schema
- synthetic dataset
- audit logging

---

## Phase 2 — Data Platform

Deliverables:

- Fabric Bronze
- Silver
- Gold
- orchestration
- validation queries

---

## Phase 3 — Analytics

Deliverables:

- semantic model
- DAX measures
- reports

---

## Phase 4 — Metadata and Lineage

Deliverables:

- metadata extraction
- normalized lineage graph
- lineage traversal API
- lineage UI

---

## Phase 5 — Deterministic Investigator

Deliverables:

- entity lookup
- cross-layer comparison
- first divergence detection
- evidence capture
- impact traversal

---

## Phase 6 — AI Investigator

Deliverables:

- natural-language ticket parsing
- investigation planner
- hypothesis generation
- explanation
- structured outputs

---

## Phase 7 — Defect Lab

Deliverables:

- 8–10 injected defects
- reset scripts
- golden results
- regression suite

---

## Phase 8 — Portfolio Polish

Deliverables:

- deployed app
- screenshots
- demo video
- architecture diagrams
- polished README
- technical article
- resume bullets

---

# 91. First Milestone

The first milestone should **not involve AI**.

Goal:

> Prove complete end-to-end data movement and traceability.

You should be able to manually answer:

```text
For ORD-10042:

What does the app show?
What is in Azure SQL?
What is in Bronze?
What is in Silver?
What is in Gold?
What does Power BI show?
```

Once this works, automate it.

---

# 92. Second Milestone

Goal:

> Given an entity and metric, automatically compare all layers.

Example API:

```http
POST /api/investigate/value-trace
```

Input:

```json
{
  "entity": "ORD-10042",
  "metric": "net_revenue"
}
```

Output:

```json
{
  "trace": [
    {"layer": "application", "value": 500},
    {"layer": "azure_sql", "value": 500},
    {"layer": "bronze", "value": 500},
    {"layer": "silver", "value": 400},
    {"layer": "gold", "value": 400},
    {"layer": "power_bi", "value": 400}
  ],
  "first_divergence": "silver"
}
```

This is the core technical proof.

---

# 93. Third Milestone

Goal:

> Allow natural-language tickets.

Input:

```text
Why is ORD-10042 $500 in the application but $400 in Power BI?
```

The system converts this into the deterministic investigation.

---

# 94. Fourth Milestone

Goal:

> Explain root cause and downstream impact automatically.

This completes the POC story.

---

# 95. Recommended Implementation Order

Do **not** start with the agent.

Implement in this order:

```text
1. Repo foundation
2. Business app
3. Azure SQL
4. Synthetic data
5. Fabric Bronze
6. Fabric Silver
7. Fabric Gold
8. Power BI
9. Manual lineage documentation
10. Metadata extraction
11. Lineage engine
12. Value trace API
13. Divergence detection
14. Defect injection
15. Investigation orchestration
16. LLM integration
17. Investigator UI
18. Automated regression
19. Deployment
20. Portfolio polish
```

---

# 96. Key POC Principle

The most important architectural rule is:

> **AI should reason over verified technical evidence, not replace technical evidence.**

This is what makes the project credible.

---

# 97. POC Final Deliverable

At completion, the repository should demonstrate:

```text
A real web application
        ↓
Real transactional database
        ↓
Real data engineering pipeline
        ↓
Real analytics model
        ↓
Real BI report
        ↓
Real injected defect
        ↓
Automated cross-system investigation
        ↓
Evidence-backed root cause
        ↓
Downstream impact analysis
```

---

# 98. Final Demo Statement

The project should be capable of making the following claim:

> A user can report a business discrepancy in natural language, and the investigation engine can trace the metric through Power BI, Microsoft Fabric, Azure SQL, and the source application, determine where the value first diverged, identify the likely root cause, show technical evidence, and calculate downstream impact.

That is the POC.

---

# 99. Immediate Next Step

Start with **Phase 0 + Phase 1 only**.

Create the following tickets first:

```text
ENG-001  Initialize repository
ENG-002  Define coding standards
ENG-003  Configure CI
ENG-004  Create architecture docs
APP-001  Scaffold business application
DB-001   Create Azure SQL schema
DATA-001 Build synthetic generator
DATA-002 Seed baseline dataset
APP-002  Implement order list
APP-003  Implement order details
APP-004  Implement order update
APP-005  Implement audit events
TEST-001 Add application tests
```

After those are complete, move to Fabric.

---

# 100. Guiding Philosophy

Build this project as though another engineer will join tomorrow.

They should be able to:

1. clone the repository,
2. understand the architecture,
3. run it locally,
4. pick up a ticket,
5. implement a change,
6. write tests,
7. submit a PR,
8. trace the change to a requirement,
9. deploy it safely.

If the project reaches that standard, it will look and behave like a genuine software-engineering product rather than a vibe-coded prototype.
