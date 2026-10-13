# Round Nineteen B: published sample onboarding

## Initial customer-guide trial, 2026-10-13

No code was changed before this trial. The unchanged official Microsoft AdventureWorks Sales PBIX (SHA-256 `2fd4c768661362889f04ff28a2bf8c69f650a23fa82b01b5a09e50d661d8b670`) is published as workspace `220708c4-6b51-4be7-ba1a-fb91bbd09e0f`, semantic model `10431c90-79c8-4508-8c17-48ec6d08e638`, report `c1c5c1d2-8f46-403a-b057-29d06b204d32`. It is an imported workbook sample; no Azure SQL source was invented.

The exact guide snapshot has SHA-256 `af3f66b81f3b4ea75dd8b55c03b3d76d299fcab701fb38f803720f4f22d17af7`. The actual-ID manifest has SHA-256 `1c8a06f2af8e0c76db16d45b6d5f7eda82458b71d44c6b51cbfd0e455f1f9a1a`; both are retained under the helper's `.local/round-nineteen-b/sample-onboarding/`. Offline preflight returned **NOT_READY**, `FAIL manifest: Manifest validation failed: ValueError`. Calling the same installed adapter revealed the exact error: `manifest.adapters.options: expected sql and fabric only`. No estate, model, or platform request was made for this initial trial.

This is a generic adapter onboarding defect: the neutral manifest permits a semantic-only estate, but its Microsoft adapter demands an unrelated SQL connection and binds every non-application layer's credential to a SQL reader. The guide also omits the initial graph-catalog bootstrap and describes implemented cloud/federated features as future work. These failures are recorded before fixes; publication is not readiness.

## Section 8: approved sample scopes

Owner: Chaitu; explicit Round Nineteen B sample-estate approval, recorded 2026-10-13. Execution used the existing isolated owner profile. No new identity, credential, capacity or paid resource was created. The new workspace is assigned to existing capacity `ec15bc07-8e88-436e-8dbe-485b9a7f4533`. The original owner remains Admin.

| Identity | Object/group ID | Scope granted | Purpose |
|---|---|---|---|
| Existing investigator application | `439ceb25-d200-4f02-95cf-4b1318faca62` | Viewer on this workspace only | Read-only investigation |
| Existing scanner application | `dbb49594-6c70-4989-a6c8-c4f237c4a021` | Contributor on this workspace only | Guarded metadata definitions and INFO discovery; never an investigation identity |
| Existing investigator group | `79c75be9-d8c3-4824-91c2-fc945041a8c3` | ReadExplore on this semantic model only | Build/read for the existing investigator |

The scanner's effective model `ReadWriteExplore` is platform scope required for INFO metadata, not a write tool permission. Its code-owned gateway still rejects refresh, definition writes, sharing, arbitrary DAX and all SQL. The investigator app appears as `Read` individually; the separate group carries `ReadExplore`. These permission listings establish grants, not a successful reader query.

### Exact retained grant requests and before/after listings

Journal `owner-publication.jsonl` in `sample-publication-02`, SHA-256 `5037472722068c3b91e79184e12b59bf446f085a5157526396cc6cb81b6e08bd`.

Journal `owner-publication.jsonl` in `sample-publication-03`, SHA-256 `c426e8b3ec259979c4739ca10f4093b9e8bbebafbd9ed6b90f52c539f8adb0b0`.

```json
{
  "at": "2026-10-13T17:52:47.615419+00:00",
  "method": "GET",
  "url": "https://api.powerbi.com/v1.0/myorg/groups/220708c4-6b51-4be7-ba1a-fb91bbd09e0f/datasets/10431c90-79c8-4508-8c17-48ec6d08e638/users",
  "body": null,
  "http_status": 200,
  "response": {
    "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/220708c4-6b51-4be7-ba1a-fb91bbd09e0f/$metadata#Collection(Microsoft.PowerBI.ServiceContracts.Api.Access.DatasetUser)",
    "value": [
      {
        "datasetUserAccessRight": "ReadWriteReshareExplore",
        "identifier": "admin@skynwhy.com",
        "principalType": "User"
      },
      {
        "datasetUserAccessRight": "Read",
        "identifier": "439ceb25-d200-4f02-95cf-4b1318faca62",
        "principalType": "App"
      },
      {
        "datasetUserAccessRight": "ReadWriteExplore",
        "identifier": "dbb49594-6c70-4989-a6c8-c4f237c4a021",
        "principalType": "App"
      }
    ]
  }
}
```

```json
{
  "at": "2026-10-13T17:52:51.364003+00:00",
  "method": "POST",
  "url": "https://api.powerbi.com/v1.0/myorg/groups/220708c4-6b51-4be7-ba1a-fb91bbd09e0f/datasets/10431c90-79c8-4508-8c17-48ec6d08e638/users",
  "body": {
    "datasetUserAccessRight": "ReadExplore",
    "identifier": "79c75be9-d8c3-4824-91c2-fc945041a8c3",
    "principalType": "Group"
  },
  "http_status": 200,
  "response": null
}
```

```json
{
  "at": "2026-10-13T17:52:55.489466+00:00",
  "method": "GET",
  "url": "https://api.powerbi.com/v1.0/myorg/groups/220708c4-6b51-4be7-ba1a-fb91bbd09e0f/datasets/10431c90-79c8-4508-8c17-48ec6d08e638/users",
  "body": null,
  "http_status": 200,
  "response": {
    "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/220708c4-6b51-4be7-ba1a-fb91bbd09e0f/$metadata#Collection(Microsoft.PowerBI.ServiceContracts.Api.Access.DatasetUser)",
    "value": [
      {
        "datasetUserAccessRight": "ReadWriteReshareExplore",
        "identifier": "admin@skynwhy.com",
        "principalType": "User"
      },
      {
        "datasetUserAccessRight": "Read",
        "identifier": "439ceb25-d200-4f02-95cf-4b1318faca62",
        "principalType": "App"
      },
      {
        "datasetUserAccessRight": "ReadWriteExplore",
        "identifier": "dbb49594-6c70-4989-a6c8-c4f237c4a021",
        "principalType": "App"
      },
      {
        "datasetUserAccessRight": "ReadExplore",
        "identifier": "79c75be9-d8c3-4824-91c2-fc945041a8c3",
        "principalType": "Group"
      }
    ]
  }
}
```

Publication accounting: 15 actual HTTP sends; 16 charged controls including one interrupted reservation conservatively retained. The failed first response and interrupted second continuation remain recorded. The final continuation made five sends and did not recreate, reimport, or regrant workspace roles.
