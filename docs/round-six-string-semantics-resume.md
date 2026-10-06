# Round Six E: string semantics and resume

Dated 2026-10-05, America/Chicago. Starting main is `177153f` (#409).
This is the offline checkpoint required before any live E request. No E cloud
request, investigation, permission change or fixture change has occurred.
Prior freezes are invalid; the inferred 15 x 2 acceptance gate is not earned.

## Owner declaration and retained code

The human explicitly declares BINARY string equality, with no case, trim or
accent folding, for the fixture's Spark/Delta landing, refined and serving
layers. This is an owner declaration; SQL endpoint collation is not substituted
for Spark semantics. The retained code confirms no normalization operation.

Both configured boundaries point to **one physical notebook**, not two:
`7ccafe59-0460-4c8a-a691-bfdfa75a2b25/notebook-content.py`, SHA-256
`313e90c9e25e1e1e844aac5383bfb3c01c4bd11684faeaabf48c207c623cf0c1`.
Its exact relevant lines are:

```python
# line 14: landing -> refined
spark.read.format('delta').load(paths['bronze']+table['name']).dropDuplicates().write.format('delta').mode('errorifexists').save(paths['silver']+table['name'])
# lines 15-18: refined -> serving
movements = spark.read.format('delta').load(paths['silver']+'stock_movements_e1b8e1')
rates = spark.read.format('delta').load(paths['silver']+'product_rates_e1b8e1')
valued = movements.join(rates, ['product_id'], 'left').withColumn('movement_value', F.col('units')*F.col('unit_cost'))
valued.write.format('delta').mode('errorifexists').save(paths['gold']+'movement_values')
```

Both retained model.bim definitions state `culture: en-US` and have no explicit
collation. The metadata declaration remains incomplete; neither is guessed
from the SQL endpoint. Microsoft's
[tabular string documentation](https://learn.microsoft.com/en-us/analysis-services/tabular-models/string-storage-and-collation-in-tabular-models?view=sql-analysis-services-2025)
describes inherited collation and a case-insensitive American-English default,
but does not name a complete model-specific collation.
[Power BI text documentation](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-data-types)
also documents trailing-space trimming. A complete declaration must distinguish
this behavior from binary Spark equality; unsupported rendering fails closed.

## Other seven unverified bindings: zero-read classification

The needed refinement `units` binding remains the resume gate for A/E/G/I.
Every other UNVERIFIED entry has the same declared-semantics prerequisite:

| Boundary | Column | Retained reason | Needed by | Declared equivalent | Classification |
| --- | --- | --- | --- | --- | --- |
| landing -> refined | movement_id | Whole-row string deduplication; COLLATION_UNDECLARED | None directly | No | Quantity-bearing discovery; numeric output still depends on full string keys |
| landing -> refined | warehouse_id | Same | None directly | No | Same |
| landing -> refined | product_id | Same | None directly | No | Same |
| landing -> refined | event_day | String distinct/content profile; COLLATION_UNDECLARED | None directly | No | Quantity-bearing STRING, not an inferred date |
| landing -> refined | movement_type | Same | None directly | No | Quantity-bearing STRING |
| refined -> serving | event_day | String distinct/content profile; COLLATION_UNDECLARED | None directly | No | Quantity-bearing STRING |
| refined -> serving | movement_type | Same | None directly | No | Quantity-bearing STRING |

There is no additional non-collation construct refusal, missing paragraph
declaration or N/A binding in these seven. The separate application copy is
not a declared equivalent for either original notebook boundary. Classification
uses #409's preserved matrix, without any new read.

## Offline implementation checkpoint

The layer contract accepts a closed four-field `string_semantics` declaration.
Unknown keys, missing fields and contradictory BINARY folding flags refuse.
Declarations remain separate from provenance in delivery records.

The Microsoft SQL renderer supports exact BINARY equality explicitly. It
encodes strings as UTF-16 bytes prefixed by their byte length for grouping,
deduplication and distinct counts, avoiding SQL's padded equality. Whole-row
deduplication preserves every key; it never chooses partial-key survivors.
The bounded content witness sums a SHA-256 prefix, with decimal accumulation;
it is an aggregate witness, not collision-free or global rowwise proof.
[HASHBYTES is documented for Fabric SQL endpoints](https://learn.microsoft.com/en-us/sql/t-sql/functions/hashbytes-transact-sql?view=sql-server-ver17).

Comparison receipts name source and target declarations and explicitly state
that both profiles use target semantics. Source transformations retain their
own deduplication semantics. Synthetic differing-semantics tests use an explicit
synthetic case-fold renderer; they do not claim Python case folding implements
a Microsoft linguistic collation. Unsupported native collations refuse.

Twenty binding/string tests, nineteen manifest tests, nine code-verification
tests and ten lineage tests pass. Full regression and live E verification have
not yet run. SNAPSHOT_UNVERIFIED remains query-bound; no standalone metadata or
memoization can upgrade it.

## One application metadata attempt, preserved

After the section 3 checkpoint, the authorized existing application reader
attempted this exact statement once:

```sql
SELECT CAST(DATABASEPROPERTYEX(DB_NAME(),'Collation') AS nvarchar(128)) AS collation,
       CURRENT_USER AS reader_identity, DB_NAME() AS database_name
```

Session `round-six-e-application-collation-20261006T001035`,
2026-10-06T00:10:35.191729Z to 00:11:22.658831Z (October 5 locally), returned:

```json
{"error":"SQL_READ_FAILED","stage":"connect","sql_error_number":40613,"error_kind":"SqlException"}
```

No SQL query or permission guard executed. One physical connection attempt is
charged SETTLED; no replacement, refund, counter reset or deadline extension.
Investigation diagnostics 0/12, metadata controls 1; pot 111 -> 112/400,
restoration reserve 60, ordinary stop 340; rolling 192 -> 193/1,500.
The actual database collation remains unknown. The sealed control tape hash is
`fc4d7f7d125ed4df8c3871facd07d17761de69e7cea08315fdf25420bd80de20`.
It records this control, not an investigation or a binding proof.

The owner-authorized Spark/Delta declarations and observed application collation were filled. Fixture digest
changed from `a347f2933fb51d1a9bb7b9fb8bf6cbc387095c5684c2b25f473d3e3e35c2fddb`
to `f0da74eac5b127d0fe4b8fea82fac4c2ec623417aa3fba0fb0090873b6389637`;
the Databricks landing example also declares BINARY. Whole-manifest approval
hashing is unchanged; no old approval is rewritten to this new hash. Do not run
with the obsolete approval. No fixture data, permission, identity, policy or
prior record was changed.

The complete semantic-default declaration, new approval,
memoized-proof runtime integration, eight-binding verification, resumed list and
inferred hosted gate remain pending. The seven original successful proofs remain
preserved, not reread or upgraded. No new VERIFICATION or investigation ledger row
was manufactured; the failed metadata control has its own ledger row.

## Subsequent controls, not replacement evidence

The original failed control above is unchanged. The existing authorized
serverless pre-warm then established a connection (no data statement), without a
resume wait. A new control performed the sole executed collation statement:

```json
{"collation":"SQL_Latin1_General_CP1_CI_AS","reader_identity":"orderops_investigator","database_name":"ordersops"}
```

Session `round-six-e-application-collation-warmed-20261006T001732` completed,
with read-only permission verification. Five physical requests: one connection
control, two permission guards, one identity check and one metadata statement.
Pot112 ->117/400; rolling193 ->198/1500. The tape SHA-256 is
`a9144093f7b5e9ac2baf711e8ea5b6dfc58c37c8a2d9a9387147fa8dbba9ebfe`.
The actual application declaration uses this observed collation, CI/AS flags,
and no explicit trimming; the SQL adapter refuses unsupported linguistic
rendering rather than treating that declaration as a binary equivalent.

The original model's existing least-privilege reader then attempted exactly
`EVALUATE INFO.MODEL()` in session
`round-six-e-model-semantics-20261006T001953`. The worker retained
`urllib.error.HTTPError: HTTP Error 400: Bad Request`. It did not retain the
service error body, so the cause remains unknown; do not label it a permission
refusal or a nonexistent function. One physical request, zero investigation
reads. Pot117 ->118/400; rolling198 ->199/1500. Tape SHA-256:
`c4ef6247af2c6aca0dffe11d53b99005f96ca51443a76769ae22d54521dc7ac0`.
No elevated identity, write or admin route was attempted.

DECIDED WITHOUT REVIEW: preserve the incomplete model declaration rather than
construct a complete four-field default from documentation that establishes only
part of it. The rejected alternative was to attach a guessed collation/flags to
the model; that could change string equivalence while appearing owner-declared.
The metadata failure has its own ledger row. The required declarations and new
whole-manifest approval are not complete, so the binding pass and family list
have not resumed. This is an incomplete Round Six E checkpoint, not acceptance.

All eight previously UNVERIFIED proposals compile both TARGET and SOURCE offline
under the exact BINARY renderer using retained target-native catalogs and the
existing explicit sample. Sixteen statements compiled, zero requests, zero
verdicts inferred from compilation. The seven successful original proofs were
not executed again. Golden context coverage with the declaration present:
2 directory entries,1 SQL object and7,540 payload characters before and after,
with byte-identical planner payloads.

The first full suite ran1992 tests and produced11 TAPE_UNCOMMITTED_ENGINE errors
because recording correctly requires committed engine bytes. It is preserved at
`.local/round-six-e-20261005/regression.log`. It is not reported as a pass. The
committed-engine repeat is pending; one further compiled-execution test now
checks preservation of case, trailing space, NUL and NULL in binary deduplication.
