# Round Sixteen: billing onboarding permission controls

Executed 2026-10-12 UTC (2026-10-12 recorded round date). Owner Chaitu explicitly authorized Part A1 in `round-sixteen-claim-first-redesign.md`: User on the billing SQL connection and VIEW DEFINITION on billing tables. This is the human identity-scope decision required by CLAUDE.md ?8.

The existing definition collector `investigator-code-reader` was the principal whose retained connection lookup returned 403. Only that principal gained the connection User role. The existing `orderops_investigator` gained object-level VIEW DEFINITION on the seven billing tables. No identity was created or replaced; no credentials, workspace roles or diagnostic execution accounts changed. The two expressly approved access scopes changed as recorded below.

## Connection grant

Existing publisher `admin@skynwhy.com`, object `23de217f-6e14-49cf-9acd-47dcd83cb82f`, applied:

```http
POST https://api.fabric.microsoft.com/v1/connections/93fd5fbf-5835-4756-bc59-bbf07302f321/roleAssignments
{
  "principal": {
    "id": "dc89155f-9a9a-4daa-9c20-7eff55818ccd",
    "type": "ServicePrincipal"
  },
  "role": "User"
}
```

Before, HTTP 200:

```json
{
  "value": [
    {
      "id": "23de217f-6e14-49cf-9acd-47dcd83cb82f",
      "principal": {
        "id": "23de217f-6e14-49cf-9acd-47dcd83cb82f",
        "type": "User"
      },
      "role": "Owner"
    }
  ]
}
```

Grant HTTP 201. After, HTTP 200:

```json
{
  "value": [
    {
      "id": "23de217f-6e14-49cf-9acd-47dcd83cb82f",
      "principal": {
        "id": "23de217f-6e14-49cf-9acd-47dcd83cb82f",
        "type": "User"
      },
      "role": "Owner"
    },
    {
      "id": "dc89155f-9a9a-4daa-9c20-7eff55818ccd",
      "principal": {
        "id": "dc89155f-9a9a-4daa-9c20-7eff55818ccd",
        "type": "ServicePrincipal"
      },
      "role": "User"
    }
  ]
}
```

This role permits use of the stored connection; it is not a SELECT-only SQL permission. The connection was originally provisioned with the existing SQL-owner credential. The investigation path continues to use the isolated diagnostic readers, never that stored owner credential. No pipeline or data was changed by this grant.

The role request and required caller authority follow [Microsoft's Add Connection Role Assignment API](https://learn.microsoft.com/en-us/rest/api/fabric/core/connections/add-connection-role-assignment); the before/after calls follow [List Connection Role Assignments](https://learn.microsoft.com/en-us/rest/api/fabric/core/connections/list-connection-role-assignments). Actual HTTP results above establish this grant, not the documentation alone.

## SQL grant

Existing SQL owner `pocsqladmin`, using its existing DPAPI credential reference, executed in `billingapp` only:

```sql
SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF DB_NAME()<>N'billingapp' THROW 50000,'Wrong database',1;
GRANT VIEW DEFINITION ON OBJECT::[app].[accounts] TO [orderops_investigator];
GRANT VIEW DEFINITION ON OBJECT::[app].[plans] TO [orderops_investigator];
GRANT VIEW DEFINITION ON OBJECT::[app].[account_plan_history] TO [orderops_investigator];
GRANT VIEW DEFINITION ON OBJECT::[app].[invoices] TO [orderops_investigator];
GRANT VIEW DEFINITION ON OBJECT::[app].[payments] TO [orderops_investigator];
GRANT VIEW DEFINITION ON OBJECT::[app].[usage_events] TO [orderops_investigator];
GRANT VIEW DEFINITION ON OBJECT::[app].[subscriptions] TO [orderops_investigator];
COMMIT TRANSACTION;
```

Before: zero object-level explicit grants for `orderops_investigator`; its only database role was the already approved `db_datareader`. After:

```json
[
  [
    {
      "database_name": "billingapp",
      "identity": "pocsqladmin"
    }
  ],
  [
    {
      "state_desc": "GRANT",
      "permission_name": "VIEW DEFINITION",
      "schema_name": "app",
      "object_name": "account_plan_history"
    },
    {
      "state_desc": "GRANT",
      "permission_name": "VIEW DEFINITION",
      "schema_name": "app",
      "object_name": "accounts"
    },
    {
      "state_desc": "GRANT",
      "permission_name": "VIEW DEFINITION",
      "schema_name": "app",
      "object_name": "invoices"
    },
    {
      "state_desc": "GRANT",
      "permission_name": "VIEW DEFINITION",
      "schema_name": "app",
      "object_name": "payments"
    },
    {
      "state_desc": "GRANT",
      "permission_name": "VIEW DEFINITION",
      "schema_name": "app",
      "object_name": "plans"
    },
    {
      "state_desc": "GRANT",
      "permission_name": "VIEW DEFINITION",
      "schema_name": "app",
      "object_name": "subscriptions"
    },
    {
      "state_desc": "GRANT",
      "permission_name": "VIEW DEFINITION",
      "schema_name": "app",
      "object_name": "usage_events"
    }
  ],
  [
    {
      "role_name": "db_datareader"
    }
  ]
]
```

Signed-in reader verification:

```json
[
  {
    "can_insert": "0",
    "can_update": "0",
    "can_view_definition": "1",
    "object_name": "app.accounts"
  },
  {
    "can_insert": "0",
    "can_update": "0",
    "can_view_definition": "1",
    "object_name": "app.plans"
  },
  {
    "can_insert": "0",
    "can_update": "0",
    "can_view_definition": "1",
    "object_name": "app.account_plan_history"
  },
  {
    "can_insert": "0",
    "can_update": "0",
    "can_view_definition": "1",
    "object_name": "app.invoices"
  },
  {
    "can_insert": "0",
    "can_update": "0",
    "can_view_definition": "1",
    "object_name": "app.payments"
  },
  {
    "can_insert": "0",
    "can_update": "0",
    "can_view_definition": "1",
    "object_name": "app.usage_events"
  },
  {
    "can_insert": "0",
    "can_update": "0",
    "can_view_definition": "1",
    "object_name": "app.subscriptions"
  }
]
```

Object-level visibility does not imply schema-wide VIEW DEFINITION. The prior collector's schema-completeness check must not be silently relabelled satisfied by these object grants.

## Preserved failures and accounting

First SQL before-listing failed with `SqlException`, number 40613: `Database 'billingapp' on server 'sql-orderops-9696025.database.windows.net' is not currently available.  Please retry the connection later.  If the problem persists, contact customer support, and provide them the session tracing ID of '{E91D60C7-F991-4386-A1AA-473B88296F5C}'.` No SQL grant ran.

A separately metered serverless resume reached SQL, then failed with number 156, `Incorrect syntax near the keyword 'identity'.` This was the private operator check's unquoted alias. The corrected query uses `[identity]`; the failed attempt is preserved, and no grant ran in that attempt.

Ten physical controls total: one publisher authentication request; three connection before/grant/after requests; two failed SQL control attempts; four successful SQL before/grant/after/reader-verification requests. Zero investigation diagnostics and zero model calls. The shared estate ledger charged each physical request. No counter reset or refund.

| Immutable receipt | SHA-256 |
|---|---|
| `.local/round-sixteen/billing-grants.json` | `c0a928c3a492552596f186c79c2ed0313394ff605779cda5cd4dee711c552e85` |
| `.local/round-sixteen/billing-grants-resume.json` | `592264b9ab305b436860d4e929878b1aebdb15fcf360358564e35a953f4c9d1b` |
| `.local/round-sixteen/billing-grants-corrected.json` | `22b9bb5808c61355cdffdb19019691b513407053759db59fd4a68996de494f77` |

DECIDED WITHOUT REVIEW: interpret the authorized connection investigator as the existing principal that actually received the 403, not both metadata and diagnostic principals. Rejected granting both. Keep all automatic mappings UNVERIFIED until separate faithful compilation and verification succeed.


## A1 collection and inference limits

The next collection uses investigator-code-reader for Fabric definitions and connection metadata, orderops_investigator for the seven visible application objects, and investigator-reader for the discovered Fabric SQL catalogs. Its prepared manifest is hash-pinned to `44a753579fd07f4b580b22455940b7d877efe1e19c69ceb6935d5bd14662f676`. Authentication controls and each worker SQL guard/query are metered; the operational bounds are 70 metadata requests plus 10 authentication controls, inside the existing estate pot. The two-hour Part A cutoff remains 2026-10-12 07:50:24 UTC. No subsequent probe is admitted after it.

Matching declared Copy projection names to source and destination column metadata produces **INFERRED_FROM_CODE / UNVERIFIED** mappings. Native source casts remain explicit transformations, including the row-version-to-bigint cast. They are never replaced by an identity mapping or treated as proof of type or value equivalence. This generic adapter has no billing column literals or per-ticket branches. It refuses unknown expressions, conflicting names, incomplete destinations and predicates that change the source row set.

The table-scoped grant does not confer schema-wide VIEW DEFINITION. Returned source objects and Fabric catalog rows are retained as visible-object evidence only. Coverage still states that whole-schema completeness is unavailable; invisible objects are never asserted absent. Metadata collection alone does not make Copy/warehouse-script lineage executable, approve a model context, earn a verified binding or make billing ready. Publication still requires the normal verification and exact replay gates.


### Collection preparation failure retained

At 2026-10-12 06:15:44 UTC, `billing-native-collection-20261012T061544` stopped before capture or metadata collection with `JSONDecodeError: Expecting property name enclosed in double quotes: line 2 column 1 (char 2)`. Four code-reader authentication HTTP requests succeeded; a fifth conservative slot covered the SQL authentication wrapper. No metadata was read and no context was created. The private Azure CLI wrapper had not directed its formatted output into its in-memory output stream; it was corrected to pass `out_file` explicitly. The original receipt and ledger row remain unchanged. This was control plumbing, not a permission refusal or an investigation result.


### Shared-catalog capture lock finding

The initial exact-capture helper audited the shared catalog while holding a SQLite read transaction, then created its backup. On the 347,693,056-byte catalog, that audit held the read lock for several minutes and blocked three Part A smoke workspace initializations before ticket execution. Those initialization failures are control/environment failures, not ticket scores. The current collection was allowed to finish with its original helper unchanged.

For subsequent captures, the prepared helper first copies a consistent SQLite snapshot into memory, closes the source connection, audits the in-memory snapshot, and only writes the durable snapshot after the credential audit succeeds. Two offline tests pass: another connection can commit to the source during the audit while the retained copy stays consistent; rejected synthetic secret material leaves no output snapshot file. The failed first version of the tests exposed Windows test connection cleanup and was corrected by closing the test handles explicitly. The future helper is separate from the current sealed capture support; it does not alter earlier tapes or weaken the credential audit.
