# Billing onboarding — Round Fifteen

2026-10-11, America/Chicago. Billing is **not fully onboarded**. Diagnostic continuations are permitted, but prospective investigation results are `NOT_SCORED: estate-not-fully-onboarded`. No identity, permission or estate data changed.

| Stage | Status | Evidence and remaining work |
|---|---|---|
| Discovery | BLOCKED — partial discovery completed this round | Sealed collection `billing-native-collection-20261011T223356`: 27 metadata physical requests and four authentication controls. Workspace, seven Bronze tables, report/model definitions, three pipeline definitions and pipeline history were retained. Warehouse catalog coverage is `UNSUPPORTED`; source catalog completeness is `UNAVAILABLE`; connection lookup returned 403. |
| Discovery approval | DONE_THIS_ROUND — partial scope only | Retained enterprise context `ee607dec-f43a-4946-9cab-5cd33d4d471c`, hash `756beb6149ae255aba4af6bf073d6f59f2a2180eee4c125a6bc8f4620a159834`. Explicit mode-policy re-adoption records retain this source and its limits. Approval does not certify completeness or promote bindings. |
| Transformation reading | BLOCKED — definitions retrieved, mappings absent | Existing `investigator-code-reader` retrieved the application-load and two Warehouse-transformation definitions. Seven Copy activities contain source queries and sink declarations, but **no explicit translator/mapping arrays**. The installed Copy proof requires explicit column mappings; it must not infer them from matching names or silently ignore the source query. The diagnostic reader's separate probe was refused as quoted below. |
| Binding proposals to billingapp | BLOCKED | The declared source connection could not be read; complete source-definition visibility is absent, Warehouse objects are not discovered, and Direct Lake partition bindings remain unresolved in the retained graph. No complete executable chain is fabricated from asset names. |
| Live binding verification | BLOCKED / not admitted | There is no complete, faithfully compiled proposal set to verify. No verification diagnostic cap was raised and no quantity probes were spent on an assumed chain. |
| Profile publication | BLOCKED / not published | No verified binding set exists. The first metadata replay also refused an engine fingerprint mismatch with the recorded Git revision; the sealed tape is unchanged. Publication requires a matching replay, not merely a valid tape seal. |

The source metadata response contains seven visible objects and 42 columns, but its permission check is `[{"can_view_definition":0}]`. The collector therefore records `PermissionError: Complete schema visibility unavailable`. Visible objects do not establish that the schema inventory is complete. This is the actual retained response, not a SQL sign-in failure or a claim that SELECT is denied.

Private evidence: `.local/round-fifteen/billing/billing-native-collection-20261011T223356.json`, its sealed `-capture/` directory, and `onboarding-facts.json`. The capture has SHA-256 `c399b12c077bf578a9703458240629ca0eb9586d7338c34845e82000a15b72c0`. Existing runs and contexts are preserved. The inherited helper's Round Thirteen ledger label was corrected by a separate appended Round Fifteen note.

## Diagnostic-reader Copy definition test

Existing `investigator-reader@skynwhy.com`, with verified token audience `https://api.fabric.microsoft.com` and the configured tenant, made:

```text
POST https://api.fabric.microsoft.com/v1/workspaces/7d67bb36-04f6-4182-95aa-da5d515248fa/items/fc8438fd-2c18-4196-9191-33e26481e2e0/getDefinition
```

HTTP **401**, exact response:

```json
{"requestId":"a41a5f8d-7ee9-4562-8d8e-bead516f46cb","errorCode":"Unauthorized","message":"User is not authorized","isRetriable":false}
```

Receipt and byte-retaining metadata tape: `.local/round-fifteen/billing/round15-reader-copy-225749/`. One metadata request and two authentication controls, three physical requests total; zero investigation diagnostics or model calls. This establishes refusal for this reader and route. It does not identify an additional permission from the response alone, and no elevation or publisher fallback was attempted. The existing code-reader's successful retrieval is separate provenance; it does not make the diagnostic reader's probe successful.

The source queries also explicitly project columns and cast the source row version. Safely supporting an absent translator requires a separate generic proof of the declared projection and types, not a name-based substitution. No estate writes are authorized this round to add mappings.

## Readiness command

`python scripts/estate_readiness.py --manifest <estate.json> --approval <approval.json> [--index <readiness-index.json>]` checks hash-bound evidence for all six stages. Missing proofs return BLOCKED and exit 2. It does not prevent honest diagnostic continuations, and it never turns partial discovery into completeness. Actual fixture and billing outputs are recorded separately before the clarification report.

DECIDED WITHOUT REVIEW: stop onboarding at the evidenced access/declaration gaps, continue the authorized clarification round with explicit unready scoring. Rejected alternative: broaden identities, infer Copy mappings, or publish a profile without the required replay. Freeze invalidated; #423 remains draft.
