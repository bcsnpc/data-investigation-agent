# Synthesis: fixed conclusion contract and cited narrative

2026-09-27 UTC. Known-domain regression. Tracking #193.

## Decision

The user's distinction is correct. A missing capability can prevent a supported
conclusion, or merely limit a conclusion already supported by checked evidence.
The previous run genuinely stopped at unavailable deeper capability and skipped
freshness. It was reasonable for the model to describe those limitations. The
wire contract was wrong to present a generic nullable missing_capability alongside
independent outcome and support fields, then enforce narrower meaning afterward.
This is a schema design defect, not a reason to erase the limitations or retry
until the model happens to omit them.

The persisted historical process field missing_capability retains its existing
meaning: a conclusion blocker on NO_KNOWN_PATTERN / NO_COMPARABLE_PATH. Historical
records are not rewritten. New synthesis context names it conclusion_blocker and
separately exposes capability_limitations (visibility boundary and skipped checks)
and mandatory_limits. Any outcome can carry limiting capabilities.

Synthesis had already been forbidden from changing the deterministic outcome.
The new provider schema consequently stops asking it to redeclare that conclusion
or its dependent support. It contains only cited business_output, technical_output
and limitations statements. Every object forbids additional properties; every
citation is selected from the displayed receipt-ID enum. The model cannot emit
an outcome plus an incompatible capability blocker, action, baseline or role.
There is no post-hoc deletion of a model-populated missing_capability field: that
field is absent from the wire entirely.

The complete original support and mandatory limits remain fixed. The runtime
validates the original assessment before live dispatch and again against original
observations after the response. Existing source/digest hash fencing and receipt
verification remain. The provider's narrative is separately retained as
LLM_INFERRED explanations and additional limitations alongside the original
business/technical facts, never substituted for those facts. The returned outcome
exposes these as synthesis_outputs. No validated model classification is invented:
the classification remains the deterministic investigation's classification.

This is preferable to enumerating dozens of redundant combinations: the
investigation has already established which combination occurred, and synthesis
has no authority to choose another. Local injected historical providers retain
the old testing interface; the production Azure provider only uses the new wire.

## Whole-response dependency audit

| Previous field/dependency | New ownership or representation |
| --- | --- |
| classification and recommended_action | Fixed original outcome/action pair; neither is model-emittable |
| procedure_step, visibility deepest_layer/stopped_by/receipts | Original process support; validated against original evidence |
| missing_capability vs outcome | Fixed conclusion_blocker, separate from capability_limitations and all-outcome narrative limitations |
| baseline status vs layer/reason/receipts; immediate divergent-boundary baseline | Complete original baseline; no independent response fields |
| capabilities_declared vs required outcome capabilities and skipped checks, especially DEFECT | Original canonical declaration and skip facts; not generated descriptions |
| evidence_by_role vs outcome-required roles and receipt tags | Complete original role mapping; original observations remain validation authority |
| equal/divergent comparison vs classification, distinct surfaces, binding provenance | Original verified comparison evidence; local guards unchanged |
| intent_dependency=ESTABLISHED vs cited intent; causal labels vs UNKNOWN | Original support status and evidence retained; synthesis cannot upgrade intent |
| measure_connection status vs contribution/baseline/mapping citations | Original support status and evidence retained; no independently generated establishment claim |
| mechanism_evidence_ids, intent_evidence_ids, measure_connection_evidence_ids vs outer evidence_ids | Original support and assembled citations remain together; model narrative has its own displayed-ID enums |
| narrative references vs available/complete observations | Per-response schema restricts every citation to displayed receipt IDs, requiring at least one when evidence exists |
| limits vs inferred bindings and unattested fields | All original mandatory limits remain, plus separately retained model limitations; no competition for the old six-item limit |
| business/technical outputs vs mandatory provenance, attestation and skipped checks | Original outputs and limits accompany both narratives without reconstruction |
| claim neutrality and factual/semantic truth | Prose meaning cannot be guaranteed by JSON Schema. Existing original-assessment guards remain; new prose is explicitly interpretation, not evidence certification |
| alternatives, prose lengths, missing/extra fields | Original alternatives remain; narrative prose is bounded with required closed objects. No control-field combination remains in the response |

The response no longer has independent categorical fields with inter-field
validity dependencies. Remaining validation checks source facts, receipt integrity,
schema compliance and state fencing; a schema cannot prove natural-language truth.
The implementation follows the documented strict object/enum schema subset:
[OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

## Offline validation and context cost

All outcome contracts accept additional narrative limitations while retaining
original blocker rules. Mutation tests inject every old control field at the
root and inside narrative objects and require schema rejection. Unknown receipts
and missing citations are rejected. Invalid original blocker/consistency evidence
still fails. An actual runtime test exercises the production provider wrapper,
retains original support and exposes the separate outputs.

Saved known-domain run: offline assembly/validation passes with zero provider or
network calls. Digest characters: 6,298 -> 7,839. Evidence entries: 5 -> 5, identical
content. Synthesis directory entries: 0 -> 0; SQL-object directory entries: 0 -> 0
(the digest does not contain a directory). Investigation payload shaping is
unchanged; eleven golden projection tests pass. A regression asserts adding the
conclusion context cannot reduce evidence/scope/directory coverage. The existing
48,000-character input cap is unchanged. Old recorded tapes remain historical;
they are not claimed to match the changed wire or context.

## Single live run

Session `c2658c88-bbcc-44fc-b066-7d950c742f92`, engine commit
`486d50b`. Same G ticket, model, discovery context and policy; GPT-5.4 medium,
8,000 output tokens, 120-second synthesis deadline, 65-second pacing; read limit
6 and cumulative input limit 384,000. Recording enabled. No permission, quota,
config change, reset, retry, new freeze or new domain.

| Probe | Execution surface | Attestation | Result |
| --- | --- | --- | --- |
| Baseline | POWER_BI_DAX; workspace `149f8d99-1c66-4a0a-9624-759be002bb60`; model `3484a2bc-98c5-4cef-be5c-a6215484075e` | MATCHED reader identity; connection, engine and object not self-reported | Handled Quantity = 8,765 |
| Declared source | FABRIC_SQL; endpoint in machine report; database `warehouse_gold_e1b8e1`, `dbo.movement_values` | MATCHED reader identity and database/object; connection and engine not self-reported | SUM(units) = 8,765 |
| Ingestion metadata | OneLake Delta log for Gold movement_values, lakehouse `b0ab76f7-20c7-410e-90e4-2c4eb104059a` | Existing metadata identity/transport; no independent identity attestation in receipt | AVAILABLE WRITE commit metadata, 406 output rows; not a row-content verification |

Both data probes attest `investigator-reader@skynwhy.com`. DAX receipt:
`a44a4c48-87a2-4f21-abc6-2147573dd02e`; Fabric SQL receipt:
`25182d69-3f7c-47dc-9dbe-419c70a78852`.

One genuinely cross-surface equal comparison, semantic Activity -> Gold
movement_values, binding DECLARED_BY_DEFINITION; zero within-layer checks.
CROSS_SURFACE_VERIFIED describes the executed comparison, not full surface
attestation: five fields remain unattested. No non-adjacent jump, skipped
intermediate boundary or NOT_COMPARABLE receipt. No deeper source comparison:
capability unavailable at Gold. Application-source declaration inspection is
unimplemented, not proof of absent lineage. Freshness was skipped because the
isolated reader cannot access presentation refresh history. Equal values did not
trigger transformation-definition judgment.

Reads: one DAX, one Fabric SQL, one OneLake metadata invocation. The latter
performs two HTTP reads (listing and commit), giving four data/metadata requests
for three reserved cloud operations, excluding authentication. No Azure SQL
source read. Context observations: one local path lookup plus ingestion metadata.
Investigation planner calls: zero. Intake: one. Synthesis: one. Two tapes preserved.
Wall time 81.232 seconds.

**Synthesis completed and validated** its new narrative schema, the retained
original assessment, and source/digest integrity. Outcome remains the fixed
CONSISTENT_TO_BOUNDARY. This is one complete known-domain execution through
synthesis, not unfamiliar-domain acceptance, verified source correctness or proof
that the model's prose is semantically correct. No individual stock movement or
adjustment rows were investigated. The strict contract now validates machine
facts and narrative shape separately; it does not certify arbitrary prose.

## Verbatim business and technical explanations

The exact emitted explanations follow. The [complete returned output object](runs/synthesis-narrative-outputs.json)
retains their citation arrays, original business/technical facts, mandatory
attestation limits and additional limitations without abbreviation.

Business:

> The displayed measure total and the displayed warehouse total agree at the checked aggregate level: the Activity measure shows 8765, and the SQL sum of units in movement_values also shows 8765. That means the investigation found agreement between the reported Handled Quantity total and the summed source-table total that was actually checked. The available ingestion metadata also shows movement_values as an available written table with 406 output rows in its recorded write. This supports aggregate agreement across the checked boundary, but it does not show whether any individual stock movement or inventory adjustment entry is correct, complete, or aligned with the intended business rule. No displayed evidence inspects individual movement rows or related adjustment rows.

Technical:

> At the presentation surface, a bounded DAX query returned [Handled Quantity] = 8765. At the lower checked layer, a bounded SQL query returned SUM([units]) = 8765 from [dbo].[movement_values]. The comparison artifact reports these values as equal between the Activity surface and movement_values. Ingestion metadata for movement_values shows an available Delta commit for a WRITE operation with numOutputRows = 406. The displayed evidence therefore shows aggregate consistency from the Activity measure down to movement_values. It does not display row-level stock movement records, inventory adjustment tables, transformation definitions, or logic proving how adjustments should be included or excluded, so source correctness and business intent remain unverified by the shown evidence.

Verbatim additional limitations:

- The check stops at movement_values. The displayed evidence does not extend further upstream into source stock movement systems or related inventory adjustment sources because visibility ended at that boundary.
- Presentation refresh history was not available to the isolated execution reader, so freshness was not checked in the displayed investigation.
- The displayed evidence is aggregate-only for the checked source table. It does not show individual movement rows, individual adjustment rows, or row-level reconciliation that could evidence incorrect source entries.
- Context/path metadata is partial and omits directory, schema, and unstructured metadata, so lineage detail outside the displayed path is limited.
- Some surface identity fields are unattested in the displayed record for the checked surfaces, including missing reported connection/engine/object fields noted for Activity and missing reported connection/engine fields noted for movement_values.

The original technical facts include these executed queries, one resolved/executed
boundary, zero within-layer checks and no probe failures:

```dax
EVALUATE ROW("baseline", [Handled Quantity],"surface_identity",USERPRINCIPALNAME())
```

```sql
SELECT SUM([units]) AS [quantity] FROM [dbo].[movement_values]
```

The original business conclusion remains agreement through the fully qualified
Gold movement_values asset. Both output packages retain the five unattested fields
and the skipped freshness check. The new narrative does not replace these records.

## Preservation, usage and delivery

All 220 earlier ledger rows remain byte-identical; one row appended. Original
runs and provider tapes remain unchanged. Daily reservations before -> after:
planner 16 -> 18, cloud 13 -> 16, input characters 607,302 -> 657,620,
output tokens 37,000 -> 46,500. All 34 reservations settled. Measured provider
usage: 17,374 input and 1,437 output tokens (516 reasoning included). Reference
cost $0.064990; not Azure billing. No counters reset, refunds or limit increases.

PR #261 merged after six green checks as
`1b118feb0cd775e788c587adb56bb617f07cd1c9`. Eighty-nine focused tests passed.
Full regression: **1,208 tests passed** in 257.185 seconds, Python exit 0.
ResourceWarnings remain in the preserved log. All 299 local document targets
resolved; `git diff --check` passed. CI installs the schema-validation dependency
before synthesis tests and includes the new whole-contract suite.

[Full per-run evidence](runs/synthesis-narrative-live.json),
[offline/context measurements](runs/synthesis-narrative-offline.json).
Local artifacts: `.local/synthesis-narrative-contract-20260927/`.



## Dated correction: surface verification (2026-10-02, America/Chicago)

The historical claims above about verified cross-surface comparisons must not be
read as satisfying the full-coverage standard merged in #299 (`955b3fe`). The
[receipt audit](retrospective-surface-attestation.md) found identity-only DAX self-reports and
identity/database-only SQL self-reports, with engine/connection (and the DAX
model object) unattested. Earlier MATCHED/CROSS_SURFACE_VERIFIED labels admitted
partial coverage; #299 now calls that PARTIAL and refuses verified boundary
eligibility. Snapshot alignment remains unestablished separately.

Run c2658c88 remains the first completed end-to-end **execution**, with two
observed values of 8,765 on independently declared routes; it did not establish
a fully attested verified boundary. Run 3d2c5bf0 observed 8,765, 8,765 and 7,661,
and invoked a judge that identified a compatible join mechanism; neither its
DAX/SQL boundary nor its SQL/SQL boundary satisfies #299. These observations
and the qualified mechanism remain useful, but do not prove actual duplicate
matches, current snapshots, intended semantics or verified transformation
attribution. Other historical comparisons using the same partial self-report
contract are subject to the same qualification. Original prose, outputs,
receipt bodies, counts and outcome labels are preserved, not retrospectively
regraded. Ledger corrections are annotations, not replacement runs.
