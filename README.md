# Self-Discovering Enterprise Data Investigator

An enterprise data investigator for Azure SQL, Microsoft Fabric and Power BI.
The target is to connect an approved environment once, discover its changing data
estate, and use an LLM with safe read-only tools to investigate unfamiliar business
questions. **Approved-workspace discovery now feeds ticket context; unfamiliar-domain
investigation is still under construction.**
This is an FDE integration with one enterprise environment.

## What works today

- Related 100,000-order application data, Azure SQL source, deployed order portal,
  Fabric Bronze/Silver/Gold processing and native Power BI model/reports.
- Environment-owned metadata scans, per-surface coverage, versioned changes and
  evidence-backed context graphs. Supported discovered models/reports enter the
  ticket catalog automatically; manual registration remains a compatibility override.
- A persisted adaptive loop: the LLM retrieves context, proposes governed SQL/DAX
  or selects typed diagnostics, sees actual observations and revises hypotheses.
  Parsed queries run through approved read-only identities and produce receipts.
- A local workspace with business questions, reviewed screenshot transcription,
  scope review, history, cancellation and shared business/technical evidence.
  Read-only identities, budgets and replay controls remain in place.
- The older bounded-v1 investigator and reviewed routing workflows remain available.

PR #192 is merged. Its count/sum diagnostic captures a native total and supporting
record groups together. Complete, empty and truncated live cases were checked;
this is arithmetic consistency, not general root-cause proof.

## How it works and what changes next

An operator approves a workspace/database profile once. Scans discover supported
models independently of reports and publish technical context without mandatory
business review. Explicit deny and the separate reader policy still govern access.
The complete target flow is:

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

**Discovery-to-ticket (Stages 2–3)** merged in PR #196. **Dynamic reasoning and
governed tools (Stages 4–5)** merged in PR #198. Two frozen engine attempts and an unfamiliar
warehouse domain are recorded. Reliability corrections now require a fresh freeze. The first nine-family trial recorded partial reads,
reasoning failures and provider rate-limit blocks; it has **not passed**.
[Challenge acceptance](docs/unknown-domain-challenge.md) remains in progress.
[Current delivery status](docs/current-delivery-status.md) owns
implementation and verification claims; [stages 1–9](docs/architecture/phases-and-acceptance.md)
define remaining work.

Discovery currently uses one approved workspace and SQL database/schema per profile.
Finite repeat scans support an external scheduler; no persistent scheduler is installed.
Denied/unsupported metadata is explicit. Warehouse catalogs require an approved
endpoint adapter. Search exposes context but does not grant query authority.

Generated queries support explicit grammar subsets; SQL views are not yet admitted.
Practical assessments are evidence-qualified LLM interpretations, not verified causes.
Frozen unknown-domain acceptance remains pending. The legacy manual
catalog retains its review gates. Runtime report filters/RLS and cross-system
comparability remain explicit limits. V2 is local and single-operator; enterprise
hosting/authentication is pending. The latest quality revision passed 910 local regression tests, eight subsequent
focused checks and ten browser checks. Labelled definition navigation, bounded
content inspection and repeated-context accounting are implemented. A separate
GPT-4.1 evaluation deployment is available; the baseline reached the shared daily
usage limit before data queries. A subsequent nine-call trial successfully found
transformation code but failed to recover from a missing-schema query rejection
before its context budget ended. No data query executed and no model-quality
improvement or supported diagnosis is claimed. Context efficiency and recovery
remain the immediate priority; the temporary daily allowance has been restored.
The subsequent [context/query recovery milestone](docs/context-query-recovery.md)
preserves structured metadata and names missing schemas or ambiguous column aliases.
Its first live trial executed one source query, but ended unresolved after repeated
query errors and a planner connection failure. A follow-up trial is in progress.
See [quality engineering and research](docs/investigation-quality-engineering.md).
These checks do not establish unfamiliar-domain acceptance or retest every
deployed application.

## Run and demo

- [Local v2 workspace setup](docs/investigation-workspace-milestone.md#local-runbook)
  and [reviewed screenshot intake](docs/screenshot-intake-milestone.md).
  Install `scripts/requirements-workspace.txt` in your development environment.
  Keep provider credentials and workspace token outside Git. Execution requires an eligible discovered or enabled legacy catalog and
  configured provider access. Discovered execution requires a separate reader.
- [Environment discovery runbook](docs/enterprise-discovery-milestone.md).
- [Dynamic investigation behavior and limits](docs/dynamic-investigation-milestone.md).
- [Model admin fallback](docs/model-onboarding.md) and
  [metadata scan worker](docs/catalog-scans-and-semantics.md).
- [Bounded-v1 presenter runbook](docs/demo-runbook.md): historical demonstrations,
  not proof of unfamiliar-domain self-discovery.
- [Order portal setup](docs/order-portal.md), [synthetic data/loading](docs/synthetic-data.md)
  and [runtime identities](docs/runtime-identities.md).

Development order portal: https://orderops-portal-9696025.azurewebsites.net

## Engineering and plan

[Controlling mission](SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md) |
[Architecture and audit](docs/architecture/README.md) |
[Current status](docs/current-delivery-status.md) |
[Progress history](docs/progress.md) |
[Handoff](PROJECT_STATE_AND_NEXT_STEPS.md) | [Contributing](CONTRIBUTING.md)

Keep SQL free-overage settings unchanged. Query/result limits do not guarantee zero
resource cost. Automatic production repairs, deployments and data mutations are
outside the investigation product boundary.
