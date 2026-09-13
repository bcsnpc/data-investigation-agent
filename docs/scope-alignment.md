# Ticket and defect lab scope alignment

The approved [scope extension](../DATA_INVESTIGATOR_TICKET_AND_DEFECT_LAB_SCOPE.md) extends the [original plan](../cross_system_data_investigator_poc.md). This review records implementation implications; it does not mark the new capabilities complete.

## Product contract

- Start with a ticket: title, report and description; optional page, visual, metric, values, period and screenshots. Screenshots provide context that must be validated against metadata and queries.
- Persist the resolved context, lineage snapshot, executed checks, observations, evidence, impact and status transitions. Show these in the workspace without hidden chain-of-thought.
- Support all six classifications: `EXPECTED_BEHAVIOR`, `TECHNICAL_DEFECT`, `SOURCE_OR_DATA_ISSUE`, `REFRESH_FRESHNESS`, `BUSINESS_REVIEW_REQUIRED`, `UNRESOLVED`.
- Diagnose the first broken boundary using comparable business definitions, filters, grain, currency and data versions. Missing evidence must remain explicit; reconciliation alone does not prove that a business rule is correct.
- Separate workflow status, investigation classification, bug creation and notification delivery state so retries do not change the finding or create duplicate external actions.
- Automatic bug creation follows section 38: verified technical defect, known boundary, supporting evidence and a configured evidence-based confidence threshold. Source/data and freshness findings remain eligible for human review unless an approved policy explicitly covers them. Expected behavior creates no bug.
- Use generic issue tracker and notification providers, with GitHub Issues and email adapters. Configure real recipients and delivery credentials before enabling delivery. Stop at human triage; product-driven code changes, PRs, repair and deployments are outside scope. Repository engineering PRs remain the development workflow.

## Engineering order

1. **4A Metadata:** discover Azure SQL, Fabric and Power BI assets and definitions; persist stable identifiers, discovery time, source/version, supported capabilities, ownership and available refresh/run metadata. Unknown ownership or unavailable evidence must not be guessed.
2. **4B Lineage:** derive edges from native relationships, ingestion mappings, transformation definitions, semantic relationships/DAX and report bindings/filter context. Persist edge provenance and unresolved dependencies. Provide upstream/downstream traversal; do not hard-code the final end-to-end graph.
3. **5A Deterministic investigation:** resolve report/metric context, reproduce values, compare totals/keys/freshness, retrieve transformations, identify divergence and persist evidence and affected assets. Retain run/version context to distinguish different snapshots from faulty logic.
4. **5B Tickets:** implement submission, attachment storage and the investigation workspace over the deterministic contracts.
5. **6 AI:** interpret tickets and choose tools; verify hypotheses through deterministic results and explain supported conclusions.
6. **7 Defect lab:** implement named, resettable scenarios and separately stored evaluation truth. Build evaluation fixtures alongside deterministic tools; the investigator must never consume expected answers.
7. **7B Routing:** add idempotent issue creation and notification delivery, evidence links, owner mapping and the human-triage endpoint.

Recurring refresh orchestration remains open. Until a schedule is configured, freshness evaluation must report actual run/version evidence without inventing an expected refresh frequency.

## Scenario selection and baseline protection

- **Examples are illustrative:** use the scope document to identify defect families, not literal business features or mandatory scenario implementations. User clarification: derive scenarios from our existing data and supported workflows; reinstatement is not a prerequisite. Do not add business features just to reproduce an example.
- **Candidate scenarios:** omit valid partially returned orders from Gold; duplicate a refund through a faulty aggregation join; map a delivery action to the wrong persisted status in an isolated lab; leave Silver stale after a controlled upstream change; use an incorrect refund measure or unintended report filter. These are proposed injections, not claims of defects in the verified baseline. Include an expected-behavior case explained by valid returns and reconciled net sales.
- **Revenue:** current Gold uses funded captures and refunds, including fully refunded paid cancellations. Copying the illustrative `status <> 'CANCELLED'` rule would change verified gross/capture/refund measures. Define the scenario's metric contract explicitly and preserve the known-good baseline.
- **Application intent:** transactional database audit proves committed actions. A missing-write scenario also needs independently correlated application intent/result evidence; absence of a committed audit row is not proof of the original request.
- **Ingestion:** Bronze currently overwrites all ten tables. Prioritize stale-copy or omitted-row scenarios that fit this implementation. The illustrative incremental-watermark scenario does not require introducing incremental ingestion.
- **Identifiers:** scenario identifiers such as APP-001 and PBI-001 overlap existing engineering work-item names. Store them in a separate scenario namespace. Section 15 distinguishes incorrect DAX (PBI-002) from visual filters (PBI-004); preserve that distinction despite the combined shorthand in section 39.
- **Reset:** record pre-injection versions/configuration and affected assets; isolate test mutations, reset them, and rerun the existing baseline validations before declaring READY. Keep evaluation ground truth inaccessible to the investigator.

## Next implementation acceptance

Phase 4A should persist a discoverable inventory of the existing source, Fabric and analytics assets with definitions and acquisition provenance. It must record freshness and ownership where available, explicitly represent missing capabilities, and supply inputs for derived lineage. Ticket UI, AI orchestration and live defect injection are later milestones.
