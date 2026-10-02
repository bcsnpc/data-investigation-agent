# Whole-chain investigation — report only

2026-09-27 UTC. Code inspected at merged #262, `542ab0b`. No engine,
configuration, policy, permission or output changes; no new investigation run.
This is Part 2's report-and-stop checkpoint. Part 3 remains queued.

## Finding

The neutral engine **already descends on equality**. The Microsoft adapter gives
it only presentation and Gold as executable layers. The loop exhausts that path;
it does not deliberately return success at its first equal comparison.

Gold's two Silver inputs are already resolved metadata declarations, but are not
executable layers. Silver-to-Bronze is explicit in the deployed notebook, but the
static collector cannot expand its loop. **There is no declared Azure SQL read in
this notebook: Bronze is created from embedded literal rows.** Native relations
also expose no Silver/Bronze-to-Azure-SQL datasource binding. This confirms the
#224 missing-edge finding for this fixture; it does not prove every source path
in the estate is absent. Matching table names or matching rows would not establish
an ingestion connection.

The [first completion](first-completed-investigation.md) checked one of the four
intended boundaries. The fourth is a target, not a deployed binding demonstrated
by this fixture. Extending the resolver alone cannot legitimately reach it.

## Evidence and acquisition limits

- Retained context: `3db5fbeb-9162-465b-8bf6-e7877a7444af`. Offline execution of
  the existing resolver returned exactly two executable layers and two resolved
  upstream declarations. See [resolver receipt](runs/whole-chain-resolver.json).
- Fresh native upstream/downstream relations for Silver, Bronze and the notebook:
  six HTTP 200 responses, no continuation fields returned. The API's visible
  item relationships are not an authoritative inventory of every external source.
- Fresh notebook definition: initial read-only `getDefinition` returned 202;
  its operation-result GET returned 200. Python content is byte-for-byte equal
  to retained content: SHA-256
  `3a980c4bd1920343202174c26b357be6233c6db267409d226d6a95fca4694273`.
  No notebook execution was requested. Embedded fixture rows remain local and
  are not copied into this report or investigator configuration.
- Two isolated-reader SQL self-reports and two zero-row object-permission
  queries succeeded for Silver and Bronze. Azure SQL's one zero-row probe failed
  at connection with SQL error **40613**. No retry; no source permission or
  data-availability conclusion can be drawn from that attempt.
- Nineteen cloud reservations total: twelve relations requests (six initial
  responses were incorrectly projected by the local audit script, then six
  corrected requests), two definition requests, two SQL self-reports, two
  Fabric SQL zero-row reads and one failed Azure SQL probe. Initial observations
  and their charges are preserved, not treated as empty relations evidence or
  refunded. This was a local audit response-extraction error, not an engine edit.
- Daily cloud usage went **16 → 35 of 60**; planner calls remained 18; input
  characters 657,620 and output-token reservations 46,500 were unchanged. No
  model call, quantity comparison, synthesis or new discovery context occurred.
  [All audit receipts and before/after usage](runs/whole-chain-platform-audit.json).

## 1. What the path resolver resolves today

In [`MicrosoftProcessAdapter.resolve_path`](../scripts/investigator/adapters/microsoft_process.py),
the semantic partition identifies its SQL endpoint and entity. Native endpoint
relations confirm the lakehouse scope. Scoped declaration resolution binds
`Activity` to Gold `movement_values`. A supported plain `SUM(column)` then adds
the lower `declared_source` layer, using physical source-column metadata.

The resolver separately selects `DERIVED_FROM` edges whose source is that Gold
asset, resolves each target inside its declared parent, and attaches:

| Declaration | Existing result | Evidence |
| --- | --- | --- |
| Gold `movement_values` → Silver `stock_movements_e1b8e1` | RESOLVED | Notebook read line 26, join line 28, write line 29 |
| Gold `movement_values` → Silver `product_rates_e1b8e1` | RESOLVED | Notebook read line 27, join line 28, write line 29 |

Both are labelled `DECLARED_BY_DEFINITION`, with retained definition identities,
source/destination URIs and derivation proofs. This is static definition lineage,
not proof of a particular run's inputs or business intent. They are **parallel
inputs to a join**, not sequential layers to compare blindly in list order.

The resolver does not recurse, append either declaration to `layers`, assign
lower input quantities, or select the notebook as a deeper boundary's definition.
The only current `definition_asset_id` is the semantic `model.bim`. Neither
executable layer carries a `transformation_asset_id` for a load job. Its
`external_source_declaration` says `CAPABILITY_NOT_IMPLEMENTED`; that constant is
not an absence finding.

## 2. Missing hops and Silver-to-Azure-SQL provenance

The deployed notebook `7ccafe59-0460-4c8a-a691-bfdfa75a2b25` declares stable
workspace/lakehouse paths for Bronze, Silver and Gold. Its source sequence is:

1. Line 19: `json.loads` of literal table data and column descriptions.
2. Lines 21–24: create a DataFrame from those rows and write each Bronze table.
3. Line 25: read each Bronze table, apply all-column `dropDuplicates()`, write Silver.
4. Lines 26–29: read Silver movements and rates, left-join on `product_id`, add
   `movement_value = units * unit_cost`, write Gold `movement_values`.

[`StaticNotebook`](../scripts/lineage_notebook.py) handles finite literal loops,
but does not resolve this `json.loads` call into a static collection. The catalog
contains **no Silver or Bronze outgoing DERIVED_FROM edges**, and records
`Unresolved loop containing write` at line 21. This is a collector limitation for
Silver-to-Bronze, even though a human can read the declared paths. A future bounded,
nonexecuting literal decoder and scoped expansion could produce deterministically
derived edges with exact definition/line/hash provenance. It must retain unknown
or ambiguous cases rather than infer edges from table names.

The six fresh native relation responses show:

| Item | Upstream | Downstream |
| --- | --- | --- |
| Silver lakehouse | No relation edges | Its SQL endpoint → lakehouse `CascadeDelete` |
| Bronze lakehouse | No relation edges | Its SQL endpoint → lakehouse `CascadeDelete` |
| Valuation notebook | Notebook → Gold lakehouse `Datasource` | No relation edges |

Microsoft describes `Datasource` as a soft item dependency; it is not a table or
column mapping, a copy-job declaration, or proof of a SQL read. A collected edge
would carry native-discovery provenance; transforming it into a table-level flow
would require more evidence. The observed Gold relation also matches the
notebook's declared default lakehouse; it does not supply the missing source.
See the official [upstream](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-upstream-relations%28beta%29)
and [downstream relation definitions](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-downstream-relations%28beta%29).

**Silver-to-Azure-SQL cannot be derived from this notebook.** Its declared input
is Bronze. Bronze itself reads literal fixture data, not JDBC, an Azure SQL
connector, or an explicit application endpoint. An actual notebook/JDBC/copy
declaration naming server, database, schema and object could support a scoped,
definition-derived binding. None is present here. Publisher-side knowledge that
the tables share generated content is not runtime lineage and was not used to
create a binding. An LLM guess would remain inferred and insufficient.

## 3. Faithful quantities and layer shape

The current implementation compiles only the semantic-to-Gold lower read. These
are feasibility findings, **not newly compiled or executed comparisons**:

| Boundary | Quantity feasibility | What remains necessary |
| --- | --- | --- |
| Semantic → Gold | Already demonstrated for unfiltered `Handled Quantity = SUM(Activity[units])` against Gold physical `units` | Existing guards require one whole-entity partition, no model roles, declared physical column and independent endpoint. Filters and more complex expressions still fail closed. |
| Gold → Silver | `units` originates in Silver movements, so a pre/post sum can test quantity preservation. Rates is a second join input, not another quantity-bearing rung. | Bind the movement column and relevant join input explicitly; inspect multiplicity and scope. The product-only join may repeat movement units. Do not call raw Silver sum an equivalent implementation of Gold's post-join total, or reconstruct the same join and treat agreement as proof that units were preserved. Use the real disagreement, if any, to ask whether the definition explains it. |
| Silver → Bronze | This fixture's Bronze has typed `units` (fresh zero-row SQL response: Int64), not only opaque payloads. Raw-unit sums can test the effect of all-column deduplication. | Resolve the loop and full row/grain mapping. Applying the declared dedupe can separately test implementation fidelity; summing raw Bronze tests preservation. These are different questions. Duplicate counts, null behavior and matching snapshot/scope matter. |
| Bronze → application | Similar columns are discoverable, but **no declared ingestion binding** exists here. | No faithful process comparison may be admitted on that basis. Record an unresolved path, not invented equivalence. Today's source probe also failed before table access. |

For monetary, nested or ratio measures, Bronze may lack Gold's derived columns
and rate-join grain. A derived quantity needs an explicit supported relational
expression with all required inputs, scope, cardinality and numeric semantics.
Rates alone cannot answer handled units. A nested/raw JSON Bronze representation
would need a declared extraction rule; missing fields or unsupported operators
must yield `NOT_COMPARABLE`. The available Int64 `units` in this fixture does not
make arbitrary Bronze shapes comparable. Never sum ratios or assume join keys
are unique without evidence.

## 4. Execution surfaces and reader access

| Layer | Execution surface | Evidence of reachability |
| --- | --- | --- |
| Semantic | Power BI DAX, model `3484a2bc-98c5-4cef-be5c-a6215484075e` | c2658c88 read succeeded; `investigator-reader@skynwhy.com` self-reported. Not repeated in this audit. |
| Gold | Fabric SQL endpoint, database `warehouse_gold_e1b8e1` | c2658c88 independent aggregate succeeded; identity and database attested. |
| Silver | Same configured Fabric SQL server, database `warehouse_silver_e1b8e1` | Fresh self-report and `SELECT TOP (0) [units] ... [dbo].[stock_movements_e1b8e1]` succeeded with read-only permissions verified. Identity and database self-reported. |
| Bronze | Same server, database `warehouse_bronze_e1b8e1` | Same fresh checks succeeded with read-only permissions verified. Identity and database self-reported. |
| Application | Azure SQL `sql-orderops-9696025.database.windows.net`, database `ordersops`, `app` schema | Configured dedicated reader; fresh single attempt failed at connect with 40613. No identity attestation or table reachability established by that attempt. |

The Silver/Bronze SQL endpoint identities are linked to their lakehouses by the
native `CascadeDelete` relations. Their database names came from discovered item
metadata. Both table probes returned **zero rows**, not quantity results. They
establish access to the named column, not permission for every dependency or the
correctness/completeness of the data. The metered operator probes used existing
reader transports; they do not claim catalog investigation admission or a newly
supported adapter path. No publisher identity read table data.

Fabric SQL endpoint triples differ by database, so Gold/Silver/Bronze reads can
cross distinct execution surfaces even on one server. Self-reports attest identity
and database, not connection or engine. The original semantic probe also lacked
object attestation. These limits remain explicit.

The SQL analytics endpoint exposes supported Delta tables, not arbitrary lakehouse
files or every Spark type. SQL and Spark/OneLake permissions are distinct. Neither
endpoint access nor an administrator's metadata access proves a separate reader
can access raw files. See [Microsoft's endpoint and security description](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-sql-analytics-endpoint).

## 5. Shape of the change — proposal, not implementation

[`vertical`](../scripts/investigator/process_debugging.py) loops through
`layers[1:]`; after equal, independently attested observations it advances `upper`
and executes `continue`. Therefore **do not replace the equality branch**. Supply
and execute a truthful deeper path, with correct quantity and transformation
contracts:

1. Expand declared upstream dependencies within approved scopes, with cycle,
   depth and ambiguity limits. Preserve branching join inputs rather than flatten
   them into a fabricated linear chain. Retain definition IDs, exact evidence and
   job identity on the boundary they explain.
2. Extend bounded static declaration handling for Silver's literal-driven loop.
   Preserve the real Bronze origin as literal initialization. Do not manufacture
   an application binding to complete a desired diagram.
3. Compile boundary-specific quantities from discovered physical schemas and
   declared column/grain transformations. Preserve filters, casts, dedupe, joins,
   time scope and snapshot limits, or return `NOT_COMPARABLE`. Choose independent
   declared databases under the reader policy; re-admit every read.
4. On an actual divergence, supply both original probe receipts and the correct
   transformation definition to `judge_definition`. Gold→Silver needs the notebook
   join, Silver→Bronze needs the dedupe, not the semantic model definition carried
   by today's only lower layer. Equal values alone do not invoke this judgment.
5. Implement evidence-producing freshness, load and ingestion checks separately
   where available. Retained history or one commit is insufficient. Do not unlock
   classifications merely by announcing capabilities.

| Additional reach | Outcomes it could support, with required evidence | Current remaining obstacle |
| --- | --- | --- |
| Semantic/Gold disagreement | PRESENTATION_LOGIC if captured framing explains it; REFRESH_LATENCY if actual refresh/current-state evidence establishes lag | Freshness capability absent. Disagreement alone does not prove either; filters, security, snapshot and quantity errors remain alternatives. |
| Gold/Silver real comparison | TRANSFORMATION_LOGIC if definition judgment explains join/filter effects; LOAD_LATENCY with job and prior-state proof; DEFECT only after competing checks are actually completed | Declarations are not executable; deeper quantities/definition/job binding missing. Current job adapter never emits LATENT. |
| Silver/Bronze real comparison | TRANSFORMATION_LOGIC for supported dedupe/filter explanation; LOAD_LATENCY or qualified DEFECT with the corresponding evidence | Static loop unresolved, no lower compiler. Same history limitations. |
| Actual ingestion/source boundary | INGESTION_GAP with expected capture/delivery evidence; deeper consistency or business interpretation only within checked scope | No source binding in this fixture. Current ingestion reads the **first Gold declared_source** commit and only returns CURRENT/UNAVAILABLE, never GAP. |
| Any unsupported hop | NO_COMPARABLE_PATH if no boundary was established; otherwise limited CONSISTENT_TO_BOUNDARY, or NO_KNOWN_PATTERN on a divergence with missing competing checks | Preserve deepest verified reach and reasons; do not report all four checked. |

The current `job_history()` labels retained history CURRENT or UNAVAILABLE (or
NOT_APPLICABLE without a job ID); it never constructs LATENT/prior-state evidence.
`ingestion()` only tests commit availability. Thus a resolver-only change still
leaves LOAD_LATENCY and INGESTION_GAP unreachable with this adapter. Its final
CONSISTENT_TO_BOUNDARY is legitimate only as a bounded observation, not a diagnosis
of the full process or proof of correct application entries.

## Stop point

Validation for this documentation milestone: two required generator tests passed;
312 local document links resolved; both quoted explanations exactly matched the
original output JSON; the 19-reservation delta matched the retained usage records;
`git diff --check` passed. No runtime regression suite was rerun: engine code and
planner payloads are unchanged. The earlier 1,208-test result belongs to #262.

This report and the milestone are documentation/evidence only. No recursive path
walking, parser extension, quantity compiler, new outcome producer, output repair,
freeze, variant or live investigation was implemented/run. Next work requires
review of this shape. Part 3's business-output enforcement, mandatory derived
actions and five explicit technical attestation fields remain pending.


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
