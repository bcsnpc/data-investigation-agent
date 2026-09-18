# Self-Discovering Enterprise Data Investigator

An enterprise data investigator for Azure SQL, Microsoft Fabric and Power BI.
The target is to connect an approved environment once, discover its changing data
estate, and use an LLM with safe read-only tools to investigate unfamiliar business
questions. **Self-discovery is the new direction, not a completed capability.**
This is an FDE integration with one enterprise environment.

## What works today

- Related 100,000-order application data, Azure SQL source, deployed order portal,
  Fabric Bronze/Silver/Gold processing and native Power BI model/reports.
- Workspace metadata enumeration, definitions, semantic dependency analysis and
  evidence-backed lineage; a manually registered and enabled v2 model catalog.
- A persisted adaptive loop: the LLM selects admitted diagnostics, sees actual
  observations and revises hypotheses. Native measure/dependency/dimension reads,
  bounded SQL aggregates/watermarks and record comparisons produce receipts.
- A local workspace with business questions, reviewed screenshot transcription,
  scope review, history, cancellation and shared business/technical evidence.
  Read-only identities, budgets and replay controls remain in place.
- The older bounded-v1 investigator and reviewed routing workflows remain available.

PR #192 is merged. Its count/sum diagnostic captures a native total and supporting
record groups together. Complete, empty and truncated live cases were checked;
this is arithmetic consistency, not general root-cause proof.

## How it works and what changes next

Today, operators register models/reports and review/enable their catalog context.
The new architecture moves discovery ahead of that manual workflow:

```text
Approved connections -> recurring discovery -> versioned enterprise context graph
Business question / screenshot -> context resolution -> LLM hypotheses and tests
Policy + read-only tools -> real observations -> revised tests -> qualified outcome
Shared business/technical view -> human-reviewed handoff
```

Power BI remains the DAX engine. The LLM interprets context and chooses tests;
deterministic tools supply facts. New supported assets should require discovery,
not investigator-specific code changes.

## Current milestone and limitations

**Stage 1: architectural pivot.** Code audit, manual-onboarding dependency map,
discovery/graph design, governed query plan and frozen Unknown Domain Challenge.
[Current delivery status](docs/current-delivery-status.md) owns implementation and
verification claims; [stages 1-9](docs/architecture/phases-and-acceptance.md) define
remaining work.

Automatic environment-to-ticket discovery, generated SQL/DAX diagnostics, broader
causal outcomes and frozen unknown-domain acceptance are not yet delivered.
Planning still selects precompiled candidates. Business review and model enablement
still gate the legacy catalog. Runtime report filters/RLS, cross-system comparability
and unsupported syntax remain explicit limits. V2 is local and single-operator;
enterprise hosting/authentication is pending. Cloud deployment evidence is historical,
not a current availability check.

## Run and demo

- [Local v2 workspace setup](docs/investigation-workspace-milestone.md#local-runbook)
  and [reviewed screenshot intake](docs/screenshot-intake-milestone.md).
  Install `scripts/requirements-workspace.txt` in your development environment.
  Keep provider credentials and workspace token outside Git. Current execution
  still requires an enabled manual catalog and configured provider access.
- [Model admin fallback](docs/model-onboarding.md) and
  [metadata scan worker](docs/catalog-scans-and-semantics.md).
- [Bounded-v1 presenter runbook](docs/demo-runbook.md): historical demonstrations,
  not proof of unfamiliar-domain self-discovery.
- [Order portal setup](docs/order-portal.md), [synthetic data/loading](docs/synthetic-data.md)
  and [runtime identities](docs/runtime-identities.md).

Development order portal: https://orderops-portal-9696025.azurewebsites.net

## Engineering and plan

[Controlling mission](SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md) ?
[Architecture and audit](docs/architecture/README.md) ?
[Current status](docs/current-delivery-status.md) ?
[Progress history](docs/progress.md) ?
[Handoff](PROJECT_STATE_AND_NEXT_STEPS.md) ? [Contributing](CONTRIBUTING.md)

Keep SQL free-overage settings unchanged. Query/result limits do not guarantee zero
resource cost. Automatic production repairs, deployments and data mutations are
outside the investigation product boundary.
