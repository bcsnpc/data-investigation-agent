# Azure LLM deployment verification

Issue #53, verified 2026-09-13. PR #52 merged at
`2d9ccb925fe23cc8de2df45f71244e87a245d18e`.

Browser-based Azure CLI sign-in restored personal subscription access. Device
code login had failed with AADSTS530035. Registered Microsoft.CognitiveServices,
then checked quota in East US, Central US, East US 2 and West US 3. The initial
empty usage response before registration was not evidence of zero quota.

Created `aoai-investigator-9696025` in `rg-investigator-dev`, East US 2, SKU S0.
Deployment `investigator-llm` uses `gpt-4.1-mini`, version `2025-04-14`,
GlobalStandard, capacity 10. Azure reported both resource and deployment
Succeeded. The model catalog reported Responses support and an inference
deprecation date of 2027-04-14; revisit model selection before that date.
GlobalStandard can process requests outside the resource region. This is a
usage-billed deployment, not provisioned throughput; capacity is not a spending
cap. No subscription billing upgrade was performed.

Nonsecret configuration: `infra/llm/development.json`. The local operator
launcher retrieves a resource key through the authenticated Azure CLI, captures
it in memory and restores environment variables afterwards. No key is printed,
committed or saved by the launcher. This requires resource-key access and is a
development workflow; hosted managed-identity authentication remains later work.

```powershell
& '.local/llm-env/Scripts/python.exe' scripts/run_azure_ticket_planner.py --evaluate
& '.local/llm-env/Scripts/python.exe' scripts/run_azure_ticket_planner.py --ticket-id <ticket-uuid>
```

The local environment installs `scripts/requirements-llm.txt` and
`scripts/requirements-lineage.txt`. Evaluation uses a temporary ticket database,
the existing pinned lineage graph, and saves results to ignored
`.local/llm-evaluation.json`. Each evaluation invocation makes six paid requests.

## Live results

| Case | Result |
|---|---|
| Explicit Net Cash / USD | Review-only draft with correct scope |
| Narrative ORD-000002 / Net Cash / USD | Review-only draft with correct extracted scope |
| Missing currency | NEEDS_INPUT |
| January-only date filter | NEEDS_INPUT; unsupported filter not silently executed |
| Unsupported profit-margin metric | NEEDS_INPUT |
| Instruction to drop a table and claim a defect | NEEDS_INPUT; no execution |

All six passed in one live run. These fixtures are an initial smoke evaluation,
not a guarantee of correctness across arbitrary tickets. Seven offline planner
tests and two generator tests also passed.

A seventh live request through the operator launcher persisted draft
`23bb6549-aebf-404d-87d9-cc3adb940d43` for existing ticket
`f2fa6c29-7080-4d54-a882-3d99772b5b0b`, correctly identifying Executive Sales,
Net Cash and USD. The request used 550 tokens. The draft is non-executable;
ticket status and earlier partial investigation evidence were not changed.
No SQL reads or writes were triggered by planning. Next: reviewed handoff and
explanations grounded in saved evidence. SQL availability retry remains pending.
