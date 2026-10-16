# Product setup and client onboarding (owner design, 2026-10-12)

The tool is a **product**, not a script tied to our test estates.
Nothing about a specific estate (workspace names, report names,
measures, table names, fixture families) may be hard-coded. Every
estate is described by configuration, and everything else is
discovered.

## 1. Prerequisites (published as a client checklist)

- **Azure:** a subscription to deploy into (the client's own, by
  default, so their data never leaves their tenant), and an Azure
  OpenAI model deployment, or a supported alternative.
- **Identities:** separate service principals or managed identities,
  each with least privilege:
  - **scanner:** metadata only (Power BI or Fabric admin read-only
    metadata APIs, report and model definitions);
  - **investigator:** read-only query access (SQL `db_datareader`, a
    read endpoint on the semantic models);
  - **impersonation reader** (optional): recreates a user's view
    under RLS. Opt-in, and limited to specific models.
- **Fabric / Power BI tenant settings,** listed exactly: service
  principals may use read-only admin APIs; detailed metadata and DAX
  expressions in admin APIs; XMLA or `executeQueries` read access;
  workspace monitoring, if runtime lineage is wanted.
- **Sources:** connection details for each source system (Azure SQL,
  warehouses and so on), using read-only logins.
- **Network:** outbound access from the deployment to Fabric, Power BI
  and the sources.

The guide lists each permission, why it's needed and what breaks
without it. The tool's **preflight check** tests every one and
reports pass, fail or missing, with the fix, before onboarding
starts.

## 2. Configure

One estate configuration, through an admin page or a config file:

- tenant, workspaces in scope (or "all I can see"), source
  connections;
- identities, taken from Key Vault and never stored in plain text;
- budgets: model spend, query limits and diagnostic caps;
- guardrail settings (read-only is always on and can't be disabled);
- the business glossary, optionally imported;
- user sign-in (Entra ID), and how users map to RLS roles.

Deployment is **one command**, using an infrastructure template
(Bicep or Terraform): database, storage, Key Vault, containers and
web front end.

## 3. Onboard: the first full scan

1. **Preflight:** check the prerequisites.
2. **Full lineage scan:** every report, page, visual, slicer and
   filter (including hidden ones); measures, relationships, RLS and
   Power Query steps; lakehouse, warehouse, views, procedures,
   notebooks, pipelines and Copy mappings; sources; refresh
   schedules and run history. The result is the estate graph, with
   every link marked declared, inferred, verified or unknown.
3. **Coverage report** for the client admin:
   - what was mapped;
   - what couldn't be read, and why;
   - what to grant or fix to improve coverage.
4. **Verify the most-used metrics** up front (the top N by report
   usage). Everything else is verified on demand when a ticket
   touches it.
5. **Go live:** open intake to users.

## 4. Stay current: event-driven updates

The graph must track changes at every level without a full rescan
each time:

| Change | How it's detected | What the tool does |
|---|---|---|
| Report, dataset, model, notebook or pipeline created, changed or deleted | Fabric workspace item events and the Power BI activity log where available; otherwise an incremental scan of modified workspaces on a schedule | Rescan only the changed items. Update the graph. Mark affected verified links as stale. Remove deleted objects, keeping their history. |
| New or changed tables, views, procedures or columns in the warehouse or SQL | Schema fingerprint polling (object modify dates and column lists) | Re-read the changed objects; flag broken links |
| Data loads, refreshes and pipeline runs | Refresh history, job and run history, Delta table history | Update the freshness information (used for stale-data tickets). No structural rescan. |
| Definition fingerprint unchanged | Nothing to do | Skip |

Every change is logged. A link affected by a change is re-verified
the next time a ticket needs it.

## 5. Deploy to users

- Intake: a web form (report name required; one or more pages; one or
  more screenshots; a description), an API for clients who build their
  own form or chat bot, and later Teams.
- Users sign in with Entra ID. Answers respect each user's RLS. The
  developer evidence pack goes to the data team.
- Admin console: estate health, coverage, change log, budgets, and
  ticket statistics.

## 6. Engineering rules that follow from this

- **No estate-specific values in code.** Audit the codebase and move
  every fixture- or billing-specific name, ID and assumption into
  configuration or test data.
- The fixture and billing become **two example estate
  configurations**, used for tests, exactly as a client would set
  theirs up.
- The setup guide, the prerequisite checklist and the preflight are
  product deliverables. They are tested by onboarding an estate from
  scratch using only the guide.
