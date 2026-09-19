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

The current reliability work adds automatic structural hypotheses to discovered
model context, SQL/DAX capability descriptions from the validators, and autonomous
structural experiments during relevant tickets. Keys, grain, join behavior,
functional dependencies and freshness can be tested through the existing bounded
read-only tools. Metadata guesses remain distinct from measured evidence and
business intent. Scans do not launch background data profiling. See
[structural discovery](docs/structural-discovery.md). The frozen unfamiliar-domain
challenge remains the main acceptance gate; these additions do not replace it.
The latest known-domain transformation run reproduced the native value but timed
out before a supported conclusion, with overlapping tests and no SQL read.
Test-selection reliability remains the next priority.


**Discovery-to-ticket (Stages 2–3)** merged in PR #196. **Dynamic reasoning and
governed tools (Stages 4–5)** merged in PR #198. Three frozen engine attempts are recorded. The latest discovered its new model
and reports automatically, then exposed excessive planner-profile truncation.
The generic correction requires a fresh freeze and variant. The first nine-family trial recorded partial reads,
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
hosting/authentication is pending. The earlier context/query recovery revision passed
920 local regression tests and 10 dynamic browser checks. The structural-discovery
revision now passes 929 regression tests; its ten browser checks preceded the final
profile projection correction. Structured definitions, parent-qualified asset search, missing-schema
recovery, actionable query feedback and remaining-time context are implemented.

A GPT-5.4 known-domain trial completed a qualified join-multiplication diagnosis:
one Power BI read and two SQL reads reproduced 57,043 and linked it to the inspected
notebook logic. It preserved uncertainty about the intended rate-selection rule
and corrected total. Earlier trials remained unresolved; one successful case does
not establish model superiority or unfamiliar-domain generality. The default model
is unchanged. SQL firewall error 40615 was resolved by a user-approved single-IP
rule; free-limit AutoPause remains.
See [context/query recovery](docs/context-query-recovery.md) and
[quality engineering research](docs/investigation-quality-engineering.md).
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
