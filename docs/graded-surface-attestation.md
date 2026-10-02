# Graded, quantity-bound surface attestation

2026-10-02. User ruling: `attestation-standard.md`. Probe PR #301 merged as
`56a15450a95c65119cd2e228518d4ed4fc818b5b` after six successful checks.
This implements the ruling, not a new live investigation or acceptance pass.

## Contract

Coverage remains NONE/PARTIAL/FULL. Consistency is checked separately against
what the adapter intended to reach. FULL is recorded but no longer admits a
boundary by itself. Both original quantity observations must carry consistent
self-reports, a VALUE_QUERY binding and their own receipt identities. A separate
metadata receipt, however complete, cannot supply either side's difference.
Synthesis checks the quantity self-report against the sealed value receipt.

Each reported field also carries an adapter-owned self-report kind, with the
consumer-owned ENGINE_PRODUCT semantic type required for engine independence. The neutral
engine compares only the same field with the same kind on both sides; it does
not interpret native property names, product strings, IP addresses or hostnames.
Different kinds cannot establish a difference. Identity and version never
contribute. Equality contributes no difference and does not prove sameness of
surface or instance. Grade is recomputed from originals, never accepted from
an adapter's comparison marker or from a model's narrative.

| Grade | What establishes it | What the output may claim |
| --- | --- | --- |
| ENGINE_INDEPENDENT | Different engine products, comparable self-reports in both value queries | Engine-independent cross-surface computation |
| OBJECT_DISTINCT | Different objects, comparable self-reports in both value queries | A data-path boundary; engine-level independence not established, shared computation faults not excluded |
| WITHIN_LAYER_CHECK | No engine/object difference established; connection-only difference does not qualify | No independent lower boundary |
| SURFACE_DIFFERENCE_UNESTABLISHED | Missing query-bound evidence or incomparable self-report kinds | NOT_COMPARABLE, with the reason named |

The strongest qualifying difference wins. OBJECT_DISTINCT does not assert that
identical product names prove a single physical engine instance; it records the
weaker protection and does not claim engine-level independence. Both structured
outputs name every comparison's grade. The engine renders its wording into both
narratives, and model mechanism prose cannot independently assert independence.
Unattested fields remain explicit and validated. Snapshot rules, faithful quantity
scope, discovered bindings, reader checks and outcome taxonomy are unchanged.
SNAPSHOT_UNVERIFIED remains the default; a surface difference is not a snapshot.

## Adapter and compiler

Semantic quantity queries include identity plus ProviderName and Catalog from
INFO.PROPERTIES in the same EVALUATE result. Their kinds are ENGINE_PRODUCT and
MODEL_CATALOG_ID. Workspace connection identity remains unattested. The DAX
compiler admits only the exact bounded scalar property expressions used for those
two fields, while retaining discovered measure/column binding. General INFO-table
queries and other property values remain unsupported. The self-report expressions
remain in the compiled fingerprint; filter/scope distinctions are not erased.

Fabric SQL wraps the compiled quantity SELECT with inline identity, database
and engine-product columns in the same result. The engine product comes from the
version header, not from a client library or an intended route label. Object kind
is DATABASE_CATALOG_NAME, deliberately distinct from a semantic model catalog ID.
The report is cleared after guards and rebuilt from the value rows, so the earlier
guard query cannot be mistaken for value-query evidence. Added columns are checked
and removed from measured quantities. All existing read-only guards remain; there
are no added physical query requests for self-description.

The new combined statements have compiler/injected-transport regression coverage,
not live estate verification. Unknown/missing descriptors fail closed. No grants,
configuration, fixture, schedule, budget or discovery approval changed.

## Historical counterfactual, not a regrade

If future value queries capture the descriptors obtained in #301:

* DAX versus SQL Gold would grade ENGINE_INDEPENDENT: OLAP Server versus Microsoft
  Azure SQL Data Warehouse, both self-reported as engine products.
* SQL Gold versus SQL Silver would grade OBJECT_DISTINCT: the database objects
  differ, while the engine product contributes no difference. This is a real data
  boundary with weaker computation protection, never engine-level independence.

The differing DB_NAME values already in historical receipts do not retroactively
supply missing typed, query-bound evidence. c2658c88 and 3d2c5bf0 stay partially
attested as captured. The #300 corrections, original outputs, receipt bodies,
ledger lines and outcome labels are unchanged. Draft #297 stays open.

## Validation and delivery

Hostile-producer tests cover identity/version-only differences, IP versus hostname,
engine/object/connection grades, detached metadata, forged grade or attestation,
partial versus full coverage, missing output grades, and compiler refusal outside
the narrow self-description grammar. Narrative tests require grade-specific wording
and forbid model-written independence. Golden context retains 28 directory entries
and 11 SQL objects before and after rendering, with identical payload characters;
rendering does not mutate or truncate the payload. The synthesis digest adds a
small explicit grade record to each compared boundary, not a directory or an
additional planning context. Existing directory-coverage tests remain.

Engine/adapter/transport bytes changed: every prior freeze is invalidated for this
engine. No investigation runs, no model/cloud calls and no ledger row in this PR.
Next remains intake evidence resolution and target/figure wiring in one PR, then
the separately authorised runs; none were performed here.
