# Round Six F: observed string semantics

Dated 2026-10-05, America/Chicago. Continues draft #410 after E; prior freezes remain invalid.

## Section 2 checkpoint (zero reads)

Semantics now carry DECLARED, DECLARED_DEFAULT or OBSERVED resolution. An observed record requires all five comparison results, the raw row, exact statement, receipt identity, and engine/version/object/identity from the same statement. Partial rows, mismatched self-reports and mutated resolved flags refuse. A declaration conflict refuses approval with both declarations named. The approval projection returns no partial manifest on conflict. Existing declarations remain readable; fixture and Databricks declarations now state DECLARED explicitly.

Memoization keys include exact engine, version, object and reader identity. A version or identity change misses the memo; replay rechecks any declaration. The controls use VerificationBudget independently of investigation diagnostics; physical guards remain governed and counted. Five literal results witness those comparisons, not arbitrary Unicode linguistic equivalence. Renderers still refuse an unsupported normalization; no guessed collation name follows from the probe.

The Houston/houston synthetic case verifies only when both sides apply the observed target case-fold rule and deduplicate explicitly; the naive two-row comparison falsifies, as does a real Houston/Dallas mismatch. These are synthetic execution tests, not evidence that a Microsoft linguistic renderer has shipped.

Six new offline tests passed, along with 15 existing binding tests, five binary renderer tests and 19 manifest tests. Golden directory coverage remains 2 entries, 1 SQL object and 7540 characters before/after, byte-identical. No F estate request occurred before this checkpoint. Pot119/400, reserve60, rolling200/1500 last observed, investigation diagnostic cap12 unchanged.

## Spark route boundary

The [SQL analytics endpoint](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-sql-analytics-endpoint) is a T-SQL surface on the Warehouse engine, not Spark. Its equality response cannot be recorded as an observation of Spark dropDuplicates semantics. The existing reader is Viewer/ReadExplore; the separate Contributor code identity is authorized only to fetch definitions, never execute diagnostic code.

[Microsoft's documented Livy route](https://learn.microsoft.com/en-us/fabric/data-engineering/get-started-api-livy) requires Contributor for the calling user and Lakehouse.Execute.All plus Code.AccessFabric.All/Code.AccessStorage.All scopes. No such grant or token-audience extension was authorized. This is a documented route constraint, not a tested HTTP403. No Spark session is started and no publisher or code-fetch identity is substituted. The accessible semantic, Warehouse and application controls can proceed independently; the Spark control section stops under CLAUDE.md section8.

## DECIDED WITHOUT REVIEW

Retain the fourth control as unperformed rather than relabel a T-SQL endpoint result Spark or execute with the publisher/code identity. Alternative rejected: apparent completion at the cost of false engine provenance or unauthorized execution scope.

## Pending

Live observations, declaration checks, eight-binding re-verification, runtime memo integration, resumed families and the inferred 15x2 hosted gate are not yet earned. The seven existing verified proofs remain untouched. No acceptance expectation is changed and no fixture arithmetic enters a runtime query.
