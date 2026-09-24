# Microsoft-native capability review — documentation research only

Checked 2026-09-24 against official Microsoft documentation. No cloud endpoint, SQL query, permission change, capacity change, or implementation was performed for this draft. Every estate-specific outcome remains **NOT PROBED BY THIS RESEARCH**; documentation describes capabilities, not availability or completeness in our workspace.

## 1. Fabric item relations

**Documented:** upstream/downstream GET APIs are beta, explicitly not recommended for production. Item Read is required; delegated Item.Read.All suffices; users, service principals and managed identities are supported. Responses contain items, typed relations and referenced workspaces. Cross-workspace references are represented. This is item-level metadata, not column lineage or an executed-data provenance guarantee. Relation types include PushData, Datasource, Orchestration, Shortcut, WeakAssociation and lifecycle relationships; their directions/meaning must be retained rather than all converted into generic source edges. No separate API SKU is specified in these references. [Upstream API](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-upstream-relations(beta)), [downstream API](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-downstream-relations(beta)).

**Recommendation:** adopt experimentally behind a replaceable metadata adapter, retaining derived graph fallback and per-source coverage. Intersect referenced workspaces with approved scope; seeing an ID never approves access. This could replace part of item-level edge discovery, but cannot replace notebook/SQL transformation analysis. Probe model, report, notebook and lakehouse in both directions; normalize exact item IDs, compare edge sets with definitions, and preserve empty/denied/unsupported results distinctly. Do not infer complete absence from an empty beta response. Endpoint docs do not promise complete dynamic notebook lineage.

## 2. INFO.CALCDEPENDENCY

**Documented:** Query restriction is supported and returns dependency records with object, referenced object, table, expressions and query fields. Microsoft explicitly requires semantic-model **Write** and disallows use while live connected in Power BI Desktop. It is a DAX-query function, not a calculation function. [Function reference](https://learn.microsoft.com/en-us/dax/info-calcdependency-function-dax).

**Premise correction:** this is calculation dependency metadata for a supplied query, not proof that every physical source column was scanned. It also does not capture current visual selections/RLS merely from a report ID, and does not provide the model-to-Gold physical binding by itself. The REST Execute Queries endpoint has a separate restriction against INFO functions, so an Execute Queries rejection may identify transport grammar support rather than conclusively test the model Write requirement. [Execute Queries restrictions](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries).

**Recommendation:** do not grant Write to investigator-reader. Retain parser/definition-derived semantic dependency traversal. Optional separately authorized metadata-collector export could supplement it, with provenance and freshness clearly isolated from reader execution. Reader probe should record transport and error category; permission denial is useful, but distinguish unavailable transport from authorization failure. XMLA connectivity/capacity availability is a separate prerequisite, not implied by Build.

## 3. SQL dependency views

**Documented:** sys.sql_expression_dependencies covers named dependencies in persisted SQL expressions; schema-bound column dependencies are available, non-schema-bound column dependencies may require sys.dm_sql_referenced_entities. Cross-database/server names may be present without resolved IDs. It requires database VIEW DEFINITION plus SELECT on the catalog view; ordinary SELECT on application tables does not imply these grants. It does not record external Spark/notebook transformation logic. [Catalog reference](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-sql-expression-dependencies-transact-sql?view=sql-server-ver17).

INFORMATION_SCHEMA.VIEW_COLUMN_USAGE returns columns referenced by view definitions, limited to objects visible to the caller. It is view usage, not general column-to-column transformation mapping. [View reference](https://learn.microsoft.com/en-us/sql/relational-databases/system-information-schema-views/view-column-usage-transact-sql?view=sql-server-ver17).

**Recommendation:** adopt as authoritative metadata where existing grants expose it, with no separate service required. Probe effective metadata permissions and visible view/module counts before interpreting zero rows. Six base fixture tables with transformation logic in a notebook can legitimately produce no useful view dependency rows. Never infer that notebook-fed tables have no dependencies from this absence. These views can reduce SQL-view parsing work, not the Fabric medallion middle.

## 4. Evidence primitives

### Delta history and time travel

Fabric supports read-only version/timestamp queries in Spark SQL/PySpark; DESCRIBE HISTORY identifies versions and timestamps. Both transaction log and data files must still exist. Time travel does not mutate current state. [Fabric time travel](https://learn.microsoft.com/en-us/fabric/data-engineering/delta-lake-time-travel). VACUUM commonly retains seven days by default; deleting old files can make old versions unreadable despite retained log metadata. [VACUUM and history limits](https://learn.microsoft.com/en-us/fabric/data-engineering/delta-lake-vacuum).

**Recommendation:** valuable optional evidence adapter. For E, commit time/operation documents last observed table mutation, not business-event freshness or SLA compliance. For F, compare bounded aggregates/keyed differences at two retained versions; this demonstrates a state change, not by itself the code or intended rule that caused it. Exact changed-row claims require stable keys and complete comparison, not a small sample. Spark compute is capacity-metered; OneLake data access and execution permissions must be verified independently of Power BI Read/Build. Never launch a notebook with publisher rights as reader fallback.

A potentially simpler read-only route exists now: Fabric Warehouse **and Lakehouse SQL analytics endpoint** document T-SQL `FOR TIMESTAMP AS OF`, distinct from Spark syntax. Viewer can query subject to security; Lakehouse historical availability depends on vacuum. [SQL time travel](https://learn.microsoft.com/en-ca/fabric/data-warehouse/time-travel). Do not apply Warehouse retention defaults to Lakehouses. Estate probe must check endpoint support and actual retained versions before proposing adoption.

### Query Insights

Documents 30-day SQL execution history, actual query text, aggregates, and up to 15-minute appearance lag; system queries excluded. Applies to Fabric Warehouse/SQL analytics endpoints, not Azure SQL or arbitrary notebook Spark activity. Prerequisites list Premium-capacity workspace and Contributor+, and complete query text is for Admin/Member/Contributor. [Query Insights](https://learn.microsoft.com/en-us/fabric/data-warehouse/query-insights).

**Recommendation:** optional existing privileged metadata feed only; not a reason to elevate the reader. Useful for query/performance evidence and candidate historical transformations, not proof of full lineage or intended business behavior. The referenced feature article is not labeled preview; a specific GA announcement date was not verified. Probe only an approved endpoint/identity; empty results may be retention/visibility/lag, not no activity.

### Refresh and item job histories

Power BI refresh-history GET accepts Dataset.Read.All scope but explicitly requires dataset **Write**, excludes OneDrive refresh and defaults to the last 60 available entries. Do not confuse OAuth read scope with model authorization. [Refresh API](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-history-in-group).

Fabric job-instance listing supports read scopes and service principals/managed identities, pagination, and usually up to 100 recently completed instances. [Job instances](https://learn.microsoft.com/en-us/rest/api/fabric/core/job-scheduler/list-item-job-instances).

**Recommendation:** favor bounded job-history retrieval where current item permissions permit; preserve an explicit gap for Power BI history denied to reader. A completed notebook or refresh does not prove that relevant source data reached all layers. These primitives improve freshness evidence without building a lineage backend, but require connector-specific capabilities and retained receipt timestamps.

## 5. Not recommended as core dependencies

### Purview

Fabric scan documentation says non-Power-BI lineage remains item-level; lakehouse table/file metadata does not imply sub-item lineage. Tenant setup can require read-only admin API tenant enablement and administrative consent/configuration. [Fabric scanning](https://learn.microsoft.com/en-us/purview/register-scan-fabric-tenant). External upstream and cross-workspace lineage for non-Power-BI items, plus notebook-to-pipeline lineage, remain documented gaps. [Fabric lineage limitations](https://learn.microsoft.com/en-us/purview/data-map-lineage-fabric). Power BI column lineage support is specifically limited to Azure SQL source scenarios, with further measure limitations. [Power BI lineage](https://learn.microsoft.com/en-us/purview/data-map-lineage-power-bi).

**Recommendation:** reject as required backend: it does not supply the missing column-level medallion transformations and adds deployment/administration requirements incompatible with the no-tenant-admin baseline. Optional customer-provided Purview metadata can remain a future enrichment source. **Pricing correction:** per-asset-per-day is a Unified Catalog governed-asset meter; Data Map also has capacity-unit/hour and processing meters. Do not describe all lineage storage as one per-asset/day charge or quote an unverified numeric price. [Official pricing](https://azure.microsoft.com/en-us/pricing/details/purview/).

### Fabric Data Agent

Current official concept docs say GA, paid F2+ or P1+ capacity, tenant AI settings, Read access; semantic-model Read can suffice without Build. Chat outputs are capped at 25 rows and 25 columns and may summarize. At most five configured sources and no selectable underlying model. [Concepts/limits](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent). Standard and preview runtimes exist; underlying model upgrades affect both. [Runtime](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-runtime).

**Recommendation:** reject as diagnostic executor. Conversational/summarized outputs are not our complete, sealed query receipts. However, 25x25 alone does not make all reconciliation impossible: small scalar aggregates can fit. The current primary pages reviewed did **not** establish the blanket no-cross-source-joins assertion, so record it as unverified rather than repeat it as fact. No need to rely on it for rejection. A future NL-to-DAX suggestion-only experiment would need a supported generation-without-execution API, independently compiled/validated and executed by our reader; such a standalone contract was **not verified** here. Do not assume invoking Data Agent yields generation only. Existing permission/capacity/tenant prerequisites remain, even for a fallback.

## Estate probe checklist for the parent task

1. Capture identity and approved scope, then bounded relation GETs with edge counts and exact-ID comparisons to existing graph.
2. Reader-only calculation dependency attempt: label Execute Queries INFO transport restriction separately from permission denial. No Write grant.
3. Reader SQL metadata query: capture effective VIEW DEFINITION and accessible view count, dependency/column-usage row counts and redacted identifiers. No new grants.
4. Existing lakehouse/warehouse connection: inspect whether history/time travel and queryinsights are exposed; do not invent a new trusted endpoint or silently use publisher execution.
5. Bounded GET job/refresh histories: retain denied/empty/unsupported outcomes, last observed completion/commit timestamps, and coverage limits.

Build-versus-adopt result: adopt existing native metadata/evidence behind capability interfaces where already authorized; keep local deterministic normalization/traversal and definition parsing for unsupported or permission-constrained gaps. No provider eliminates the entire report -> model -> Gold -> transformation -> source chain under the current read-only contract.
