# Live self-report diagnosis ? report before fixes

2026-10-02 America/Chicago; inspected after the 2026-10-03 UTC R1?R3 batch.
Section 1 of the user's attestation-live-and-validator request only.

PR #314 merged as `6572ee0f4bb850935493726d06c84eb51d904cac` after all six
exact-head checks passed. This audit changes no runtime code. No new estate
request, model call, investigation, cap, policy, fixture or permission change;
no ledger row is needed for read-only inspection of existing receipts. Original
receipts, outputs, tapes and ledger entries remain unchanged. Prior freezes
remain invalid, with no additional engine-byte change here.

## Finding

**All nine dispatched statements contain all three self-report columns. The
surface answered identity and returned null engine/object values. Extraction
then discarded the partial report, including the answered identity and the
explicit nulls.** The empty-field case is established; a receipt-retention
loss accompanies it. This is not a missing compile path and not evidence that
this reader cannot access INFO.PROPERTIES through REST.

The raw provider response body was NOT retained in the flexible receipt. It
retains a canonical pre-extraction response hash and a query hash in
`execution_identity`. The quoted original request/result excerpts below are
from sealed receipts. To establish the otherwise discarded self-report values,
the audit reconstructs a response using the retained numeric row and candidate
identity/product/catalog values, explicit nulls, and omitted columns. Exactly
one candidate matches the original canonical response digest for each of the
nine receipts. Each executed-query hash also matches the stored dispatched
query, and every original receipt seal verifies.

These are **hash-verified canonical reconstructions**, not original raw response
files, new queries or rewritten receipts. The [audit evidence](runs/live-self-report-diagnosis.json)
retains every exact stored request/result, its seal, reconstructed response,
matching digest and pure extraction output. No historical attestation is upgraded.

The matching row shape in all nine responses is:

```json
{
  "[quantity]": 8765,
  "[surface_identity]": "investigator-reader@skynwhy.com",
  "[surface_engine]": null,
  "[surface_object]": null
}
```

Here 8,765 illustrates the six undeclared-context candidate reads. The existence
read instead has quantity 1; the final North-only baselines use `[m0]`: 3,359.
Identity is query-returned. Engine/object are null, not empty text or absent
columns. None establishes an independent surface or eligible binding.

## Exact emitted statements and sealed receipt excerpts

Every path uses TOPN around the same ADDCOLUMNS self-report form. The following
are the stored dispatched `request.query` statements, not freshly compiled
proposals. The three candidate reads in each R2/R3 run are byte-identical.

### Existence lookup ? R1

Receipt `f4164fc3-ab60-4401-8abd-a45369403688`:

```dax
EVALUATE TOPN(21,ADDCOLUMNS(ROW("quantity",COUNTROWS(FILTER(VALUES('Locations'[warehouse_name]),'Locations'[warehouse_name] == "North")),"surface_identity",USERPRINCIPALNAME()),"surface_engine",MAXX(FILTER(INFO.PROPERTIES(),[PropertyName]="ProviderName"),[Value]),"surface_object",MAXX(FILTER(INFO.PROPERTIES(),[PropertyName]="Catalog"),[Value])))
```

Stored result excerpt:

```json
{
  "rows": [
    {
      "[quantity]": {
        "type": "decimal",
        "value": "1"
      }
    }
  ],
  "columns": [
    "[quantity]"
  ],
  "surface_report": null,
  "surface_report_binding": "VALUE_QUERY"
}
```

Retained original `execution_identity` hashes:

```text
query_hash = dc7bf3e220715a4c49b5043affe7b36c22bdcc53b3ea5ab463820aca2bc07c3d
response_hash = 04856f803dd711d2690712f4a5a2e573655ab1eb5f19e65140c9ebb0a3406f47
```

### Undeclared-context candidate evaluation ? R2/R3

Receipt `d7c5ae17-94fb-4cbd-a043-3f417737dc54`:

```dax
EVALUATE TOPN(21,ADDCOLUMNS(ROW("quantity",'Activity'[Handled Quantity],"surface_identity",USERPRINCIPALNAME()),"surface_engine",MAXX(FILTER(INFO.PROPERTIES(),[PropertyName]="ProviderName"),[Value]),"surface_object",MAXX(FILTER(INFO.PROPERTIES(),[PropertyName]="Catalog"),[Value])))
```

Stored result excerpt:

```json
{
  "rows": [
    {
      "[quantity]": {
        "type": "decimal",
        "value": "8765"
      }
    }
  ],
  "columns": [
    "[quantity]"
  ],
  "surface_report": null,
  "surface_report_binding": "VALUE_QUERY"
}
```

Retained original `execution_identity` hashes:

```text
query_hash = 9daa28a5914f1bf33ddaf0f4b743189f654906638c9c1370843e588c24e55858
response_hash = 5592625efd81d4378b5ab0bd917a325a6466804823ec06530bed0c250a44fd0a
```

### North-only baseline ? R2/R3

Receipt `602e065a-ed55-439c-a38f-62a27b0d9f3f`:

```dax
EVALUATE TOPN(21,ADDCOLUMNS(ADDCOLUMNS(CALCULATETABLE(ROW("m0",'Activity'[Handled Quantity]),TREATAS({"North"},'Locations'[warehouse_name])),"surface_identity",USERPRINCIPALNAME()),"surface_engine",MAXX(FILTER(INFO.PROPERTIES(),[PropertyName]="ProviderName"),[Value]),"surface_object",MAXX(FILTER(INFO.PROPERTIES(),[PropertyName]="Catalog"),[Value])))
```

Stored result excerpt:

```json
{
  "rows": [
    {
      "[m0]": {
        "type": "decimal",
        "value": "3359"
      }
    }
  ],
  "columns": [
    "[m0]"
  ],
  "surface_report": null,
  "surface_report_binding": "VALUE_QUERY"
}
```

Retained original `execution_identity` hashes:

```text
query_hash = 709fb2e3b6b879f5ee14f53b1c7514de5658c4d2869c0d3ad50a3eb76e800ca5
response_hash = 8eed36fb44c9150b8d5fcaa8abfb9f568ad8afa2905a13baed711580b75f6d5b
```

The three candidate probes are the first (undeclared-context) partner only;
no full active page/visual/slicer restriction set was executed. The missing
self-report makes each candidate probe unavailable, so its restricted partner
is not admitted. The fourth read is the procedure's North-only baseline, not
the declared-context reproduction. The cell/reproduction path did not execute
a restricted probe whose returned value could be checked against BLANK.

## What came back ? UNATTESTED, information only

Each row below has the same returned self-report: identity
`investigator-reader@skynwhy.com`, engine null, object null. The stored report
is null after extraction. Values below are not eligible comparison evidence.

| Run / probe | Receipt | Read purpose | Raw numeric value |
| --- | --- | --- | ---: |
| R1 / 1 | `f4164fc3-ab60-4401-8abd-a45369403688` | North existence count | 1 |
| R2 / 1 | `d7c5ae17-94fb-4cbd-a043-3f417737dc54` | undeclared-context candidate 1 | 8765 |
| R2 / 2 | `37764631-4126-4c94-9a51-e97b75ee47ec` | undeclared-context candidate 2 | 8765 |
| R2 / 3 | `4e608d41-e4fc-4086-88a2-bd6944018c50` | undeclared-context candidate 3 | 8765 |
| R2 / 4 | `602e065a-ed55-439c-a38f-62a27b0d9f3f` | North-only baseline | 3359 |
| R3 / 1 | `941741bd-2648-4479-835f-401e86a7ee96` | undeclared-context candidate 1 | 8765 |
| R3 / 2 | `a458d8d9-e9c8-4163-83a4-d7da1b3f5e64` | undeclared-context candidate 2 | 8765 |
| R3 / 3 | `083412d1-0f99-4ff2-a2ea-62bfb1ed09e1` | undeclared-context candidate 3 | 8765 |
| R3 / 4 | `37bf51c0-743f-4777-9fb8-202052ad638f` | North-only baseline | 3359 |

**R2's derived BLANK was not tested.** Its four returned quantities were
8,765, 8,765, 8,765, and 3,359. R3 returned the same sequence. None was a
completed restricted evaluation under RECEIPT + North + Component 1 + date.
Neither confirms nor refutes the independent fixture arithmetic.

## Comparison with the successful #300 metadata request

The preserved successful receipt is `rest-dax-engine-descriptors` from
2026-10-02T05:47:57.690884+00:00; HTTP200, RequestId
`b5dc4ee8-c625-4c5e-bc07-f98beeb35ac8`.

```dax
EVALUATE SELECTCOLUMNS(
    FILTER(INFO.PROPERTIES(), [PropertyName] = "Catalog" || [PropertyName] = "ProviderName"
        || [PropertyName] = "ProviderVersion" || [PropertyName] = "DBMSVersion"
        || [PropertyName] = "ServerName"),
    "PropertyName", [PropertyName], "Value", [Value])
```

Original returned rows (receipt excerpt):

```json
[
  {"[PropertyName]":"Catalog","[Value]":"3484a2bc-98c5-4cef-be5c-a6215484075e"},
  {"[PropertyName]":"ProviderName","[Value]":"OLAP Server"},
  {"[PropertyName]":"ProviderVersion","[Value]":"17.0.91.20"},
  {"[PropertyName]":"DBMSVersion","[Value]":"17.0.91.20"},
  {"[PropertyName]":"ServerName","[Value]":"host002_datasets-023"}
]
```

Both routes targeted:

```text
POST https://api.powerbi.com/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/datasets/3484a2bc-98c5-4cef-be5c-a6215484075e/executeQueries
identity: investigator-reader@skynwhy.com
serializerSettings.includeNulls: true
```

The preserved operator script and plan used the existing reader MSAL token,
Power BI audience, workspace and model, not a publisher or XMLA endpoint. The
nine worker receipts bind the same workspace/model/account and principal to
the dispatched query hash. Endpoint and account are the same; time and statement
shape differ. The successful query projects the property rowset's strings;
the current queries use `MAXX(FILTER(INFO.PROPERTIES(), ...), [Value])` to
scalarize them inside a quantity row, wrapped in ADDCOLUMNS and TOPN.

The receipts demonstrate null results for that scalar form. They do NOT
establish a permission refusal or general INFO.PROPERTIES unavailability, and
they do not identify exactly why this scalar composition yields null. No new
statement, alternate form or platform request was sent to make it populate.
The successful rowset's separate metadata result cannot be substituted into
these quantity receipts. See [original metadata evidence](surface-self-description-probes.md).

## Where retention loses the answered/empty fields

After establishing the response content from receipt hashes, code inspection
identifies the loss in `flexible_tools._split_surface_report`:

```python
answers.add(row.pop(present[0]))
...
report[field]=answer if isinstance(answer,str) and answer else None
return stripped,(report if all(report.values()) else None)
```

For every live row, the helper removes all three columns from the numeric row,
builds `{identity: reader, engine: None, object: None}`, then replaces that
entire mapping with None because not all values are truthy. `extract()` writes
only those stripped numeric rows and the None report; `run()` stores/seals
that normalized result. Pure local extraction of the hash-matched canonical
responses reproduces the exact stored rows/null report. This explains why the
original result cannot show which fields answered and which were empty.

The refused binding is correct: two required self-report values are unavailable.
The receipt loss is not correct: successful identity and explicit empty fields
must remain evidence even when attestation fails. These are distinct findings.

## Stop point

This is the requested section-1 report. No section-2 implementation, inventory
validator removal, business-output change, refusal recategorization, new run or
fixture work has started. The next work is the separate self-report invariant
PR, then the scoped-validator/output PR, after this report has been reviewed.
