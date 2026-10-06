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


## Live controls and honest stop

One statement was attempted on each accessible engine, using existing readers only. Spark was not attempted; no unauthorized identity was substituted. Raw requests, responses, budget decisions and failure events are preserved privately, with one ledger row per attempted control.

| Surface | case_fold | accent_fold | trim | kana | width | Collation/version | Physical |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Semantic model | true | false | false | true | true | No collation name reported; OLAP Server17.0.93.25 | 1 |
| Ops Warehouse | false | false | true | false | false | Latin1_General_100_BIN2_UTF8; EngineEdition11/version12.0.2000.8 | 4 |
| Application | unavailable | unavailable | unavailable | unavailable | unavailable | Query-stage failure; no result retained | 6 |
| Spark | unperformed | unperformed | unperformed | unperformed | unperformed | Documented execution-scope boundary above | 0 |

The Warehouse here is the approved isolated ops audit Warehouse `round_three_ops_audit_20261004`, not a Gold lakehouse endpoint renamed Warehouse. The semantic probe used model3484a2bc-98c5-4cef-be5c-a6215484075e. Both report investigator-reader@skynwhy.com in their statement. Successful controls retain query-bound identity, object, engine and engine version. Offline attestation recomputation checks the declared product name against DAX ProviderName or the Warehouse transport's same-statement product report; these are separate from the numeric EngineEdition field. Connection remains unattested. These controls are not boundary value/snapshot proofs.

Semantic session `round-six-f-semantic-20261006T003953`: pot119 ->120; rolling200 ->201. Warehouse session `round-six-f-warehouse-20261006T004309`: pot126 ->130; rolling207 ->211. Each consumed one metadata-verification slot of one, zero investigation diagnostics. Warehouse trim=true is the observed equality of a and a-space, not a claim that the storage engine physically removes spaces. Likewise, DAX literal equality does not attest import-time dictionary normalization.

Application session `round-six-f-application-20261006T004033`: pot120 ->126; rolling201 ->207. Its retained response was:

```json
{"error":"SQL_READ_FAILED","stage":"query","sql_error_number":null,"error_kind":"RuntimeException"}
```

The application transport executed the statement and then rejected the operator's `max_rows:1`: `Read-CatalogAggregate.ps1` requires at least2 for records. This exact request/consumer mismatch is established offline. The historical exception message is absent, so the named cause is an offline reproduction, not a recovered historical exception. No rows were retained and no booleans may be reconstructed from defaults. Two prewarm connection controls, a five-second resume wait and the guarded query are recorded separately; the six physical requests remain charged. No replacement statement was executed.

The local operator also raised `AttributeError: 'Tape' object has no attribute 'finalized'` while finalizing this failure. All retained control events and the original artifact remain unchanged; the application tape has no FINAL and is explicitly excluded from acceptance. The ledger separately records the recorder defect. Future unattempted Warehouse recording used the actual `finished` field; no historical tape was repaired or sealed retrospectively.

Two successful observations are memoized privately by exact engine/version/object/identity, with their original receipts. The observed semantic comparison declaration is now written to the fixture manifest; application and Spark declarations are not upgraded. The manifest change pins before hash `ac948762ba408de5fe6cf51ee38a2105807101361fbf086ee211a158a6f4b93b` and after hash `10aff65a4c9bac2a2c0dac18eea96cd3dc8a15b4636601f8c65520248aee5792`; whole-manifest approval hashing is unchanged and the obsolete approval is not rewritten. The other semantic model is not given this model's observation.

Full committed-engine regression:1999 tests in349.730s, unittest `OK`. The PowerShell wrapper returned1 with redirected ResourceWarnings; the retained test report has no failures. Golden planner coverage remains unchanged. No fixture data, permission, identity, secret, budget policy or acceptance expectation changed.

The eight non-verified bindings were **not re-read**: the four-engine observation/approval step is incomplete. The seven successful prior proofs were neither reread nor upgraded. No family, EMPTY, numeric16 or control scenario was attempted. The second column and hosted15x2 gate remain unearned, so #410 remains draft and unmerged. This is a recorded partial Round Six F result, not a general capability or unfamiliar-domain acceptance.

Final windows: pot130/400,60 reserved (ordinary stop340); rolling211/1500. Eleven physical requests, three metadata-verification attempts, zero investigation diagnostics, zero provider/planner calls. No credit, cap, refund or counter reset.
