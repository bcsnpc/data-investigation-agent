# Billing report built; stop for owner tickets

Updated 2026-10-09 UTC. The human authorised moving to billing regardless of
the final intake score. That gate remains failed: dev24/40, held16/28,
7/3 illegitimate questions and1/9 consequential-field mismatches. The final
demo revision c8e370c passed2,728 regression tests, native exit0. No oracle,
golden, acceptance expectation or original tape changed in this continuation.

The [Subscription Billing report](https://app.powerbi.com/groups/7d67bb36-04f6-4182-95aa-da5d515248fa/reports/e995a2cf-7748-45f7-bde1-47510ddc509a)
is published in dia-billing. Independent DAX as investigator-reader returned:

| Measure | Value |
|---|---:|
| Invoiced Amount |950|
| Collected Amount |550|
| MRR All Plans |600|
| Churned Accounts |1|
| Usage Overage |600|

USERPRINCIPALNAME matched investigator-reader@skynwhy.com. Identity evidence
does not attest the other surface fields or a served version. These reads
remain SNAPSHOT_UNVERIFIED. No browser rendering or screenshot was observed.
No billing ticket, expected outcome or investigation has been authored/run.

## Published estate

| Item | Returned identity |
|---|---|
| Workspace |7d67bb36-04f6-4182-95aa-da5d515248fa|
| Existing capacity |ec15bc07-8e88-436e-8dbe-485b9a7f4533|
| Bronze lakehouse |1853cbbb-06d1-4ae9-b378-370007c574ba|
| Serving Warehouse |406dcb89-0526-4f48-bb77-397d52471c89|
| Audit Warehouse |9cd1829b-7e2e-4340-8f59-fdf996033198|
| Source connection |93fd5fbf-5835-4756-bc59-bbf07302f321|
| Copy pipeline |fc8438fd-2c18-4196-9191-33e26481e2e0|
| Successful transformation continuation |62eb1a7f-19c2-466f-85ec-cda6bc231fb9|
| Direct Lake model |c6c1091c-3bde-46ca-94fc-58f62d1e4188|
| Report |e995a2cf-7748-45f7-bde1-47510ddc509a|

Azure SQL billingapp was created on the existing server. Returned configuration
establishes useFreeLimit=true, freeLimitExhaustionBehavior=AutoPause,
GeneralPurpose serverless Gen5 2vCores, minimum0.5 and autoPauseDelay60. No paid
fallback was selected. Seven synthetic application tables contain26 seeded rows.
Application reachability defaults false; orderops_investigator acquired no
billing database/table grant.

Pipeline Copy replaces the previously planned Dataflow Gen2 ingestion. The
author-only defect seal is unchanged:
9886e5e43ea170bbc8164a007686832e0d116fbe337c9f9ac59e3eb35aab5919.
It is not in the model, report, runtime configuration or code-source inputs.

The existing SQL owner credential was loaded from its DPAPI file into memory
and sent to Fabric's managed source-connection secret store. This is an added
credential location for an existing publisher-managed connection, not a new
reader credential, identity, audience or SQL grant. No credential was written
to a repository file, receipt or temporary file. The isolated Azure
administrator profile was used only for workspace creation. Artifact work
used the existing Fabric publisher profile; both profiles resolve to the same
human principal, so they are not represented as different identities.

## Own load accounting and independent reader verification

Copy run e82f690b-6865-48b5-a38c-9a116cd9c132 completed. Its retained outputs:

| Activity | Rows read | Rows copied |
|---|---:|---:|
| Copy_accounts |4|4|
| Copy_plans |2|2|
| Copy_account_plan_history |5|5|
| Copy_invoices |4|4|
| Copy_payments |3|3|
| Copy_usage_events |4|4|
| Copy_subscriptions |4|4|

Investigator-reader independently read one Warehouse audit row for that exact
run: Succeeded,26 rows read,26 written, OBSERVED_COPY_OUTPUT,
start2026-10-09T21:51:03.1830083Z,
end2026-10-09T21:54:56.6775595. The counts match activity outputs, not a recount.
SELECT=1 and INSERT/UPDATE/DELETE=0 on the audit table. High watermark is
explicitly NULL/unavailable. Timing is pipeline trigger to audit insertion,
not evidence of when the application changed.

The retained service billing references report seven0.0666666667 DIU-hours
Copy entries and two0.0166666667 IR-hours Script entries. These are reported
meters, not a dollar invoice or an estimate of trial billing. The first
pipeline includes one-time CREATE TABLE bootstrap and must not be rerun
unchanged. A reusable load-only definition remains a follow-up.

Warehouse T-SQL procedures completed after a recorded SQL-visibility
continuation. Publisher construction checks returned Gold5 invoice rows,
amount950, and Silver4 rows,amount700. The model has role-playing invoice and
payment dates and an active account-history-to-billing many-to-many
relationship. Bronze was actually loaded through Copy; no literal-row staging
or notebook substitutes for it.

The served report retains actual TopN and RelativeDate predicates: a Top2
subquery ordered by Invoiced Amount, and dynamic seven-day bounds including
today. Publication retention is established; collection into a new billing
discovery context and faithful reproduction support are not. Native published
definitions and IDs are preserved under fixture-code/billing/published-20261009.

## Exact scope changes under the human decision

Round Ten sections3/4 explicitly approved matching fixture scopes in the new
isolated workspace. Existing publisher applied these exact role POST bodies:

```json
[
  {"principal":{"id":"8a582d2a-ecb4-4320-bf72-75a529a0d382","type":"User"},"role":"Viewer"},
  {"principal":{"id":"dc89155f-9a9a-4daa-9c20-7eff55818ccd","type":"ServicePrincipal"},"role":"Contributor"}
]
```

Before listing: publisher23de217f-6e14-49cf-9acd-47dcd83cb82f Admin only.
After: same publisher Admin; investigator-reader8a582d2a-ecb4-4320-bf72-75a529a0d382
Viewer; investigator-code-readerdc89155f-9a9a-4daa-9c20-7eff55818ccd Contributor.
No existing workspace changed. The code reader is not a quantity execution
identity.

Exact model permission POST:

```json
{"identifier":"investigator-reader@skynwhy.com","datasetUserAccessRight":"ReadExplore","principalType":"User"}
```

Returned model permission listings before/after:

```json
{
  "before": [
    {"datasetUserAccessRight":"ReadWriteReshareExplore","identifier":"admin@skynwhy.com","principalType":"User"},
    {"datasetUserAccessRight":"Read","identifier":"investigator-reader@skynwhy.com","principalType":"User"},
    {"datasetUserAccessRight":"ReadWriteExplore","identifier":"dc89155f-9a9a-4daa-9c20-7eff55818ccd","principalType":"App"}
  ],
  "after": [
    {"datasetUserAccessRight":"ReadWriteReshareExplore","identifier":"admin@skynwhy.com","principalType":"User"},
    {"datasetUserAccessRight":"ReadExplore","identifier":"investigator-reader@skynwhy.com","principalType":"User"},
    {"datasetUserAccessRight":"ReadWriteExplore","identifier":"dc89155f-9a9a-4daa-9c20-7eff55818ccd","principalType":"App"}
  ]
}
```

No app registration, credential rotation, new audience, orderops_investigator
grant or dia-reader role changed. Private sealed before/after bodies and grant
receipts remain in billing-reader-grants.json and billing-model-report-publication.json.

## Preserved failures and manual steps

- Initial foundation startup: ModuleNotFoundError, no module named fabric_cli;
  zero dispatches. Used the existing Fabric virtualenv. Original PREPARING
  receipt and traceback remain, with an appended terminal correction.
- Wrong workspace-name assertion: one read, no mutation, retained.
- First seed attempt: SQL156, incorrect syntax near identity. No mutation;
  fixed the authoring alias in a separately recorded attempt.
- Publisher SQL token: AuthenticationFailed, failed to get access token.
  Zero SQL dispatches, one admitted reservation retained. Used the previously
  tested Script-activity route without a new identity or audience.
- First transformation:2011, Invalid object name billing_bronze.dbo.plans.
  Copy_plans completed21:52:27.2326469Z; failed transformation ended21:57:04.9.
  Reader probe21:57:38.003756–21:57:44.783893Z found all seven SQL-visible
  tables. This brackets observed Copy-success/SQL-visibility delay; it is not
  an exact Delta-commit sync measurement. The existing accounts view/table
  were preserved during continuation.
- Continuation publication:409 ItemDisplayNameAlreadyInUse. Retained failure;
  subsequent distinct name, no source reload.

The audit verification originally reported3 requests from a shared global
counter delta while two transformation controls ran concurrently. An appended
correction records1 audit SQL dispatch; the other2 belong to transformation.
No original row was edited and no budget charge removed.

## Budget, remaining work and stop

Billing charged79 reservations:78 actual estate dispatches plus one retained
pre-dispatch authentication-failure reservation. Round Ten1,035→1,114/1,500;
restoration reserve95 unchanged,291 ordinary pot capacity left. Rolling22→101
/3,000. Zero investigation diagnostic reads and zero model/provider calls for
this build; construction and verification controls are separately labelled.

Model allowances were restored to600 calls/8M input characters after scoring.
Charges remain659/9,131,997; no new model call until the next UTC window.

Stop for the owner's billing tickets. A published report with served measures
does not establish a completed billing investigation or unfamiliar-domain
acceptance. Billing-specific estate.yaml, code-source Git registration,
recollection/current whole-config approval, collector predicate verification
and a reusable load-only pipeline remain before billing investigations.
No rehearsal approval may be reused. Browser click-through, true screenshot
crops and screenshot Phase B remain incomplete: no browser surface is
connected and today's model allowance is exhausted.

DECIDED WITHOUT REVIEW: withhold a runnable billing investigation manifest
until its own context/approval exists, rather than copying a rehearsal approval
or giving publisher credentials to diagnostic execution. Use the existing
publisher Script route for authorised Warehouse DDL. Keep bootstrap visibly
one-time instead of implying the first pipeline is reusable. Current freeze
invalidated; #423 remains draft.
