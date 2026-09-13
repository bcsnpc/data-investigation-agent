# LLM ticket planning

Issue #51 adds an opt-in planning command alongside the deterministic worker.
It sends ticket text and a small catalog of report IDs, names and supported
measures to the configured Azure deployment. It does not send credentials,
business rows or full notebook definitions to the model.

The Responses API requests a strict JSON schema. Local validation independently
checks report membership, report/measure compatibility, filter formats, required
clarifications and preservation of explicit ticket fields. Every accepted plan
is `DRAFT_REQUIRES_REVIEW` or `NEEDS_INPUT`, with `executable: false`.
Model interpretation can still be wrong or miss a filter; schema validity is
not semantic correctness. Human review is required before submitting an explicit
ticket for the existing deterministic worker. No automatic handoff is implemented.

Each attempt gets a UUID and a row in `ticket_plans` inside ignored local
`workflow.sqlite`: ticket ID, pinned lineage, prompt version, input hash,
validated draft and provider response ID/model/token usage when successful.
Errors are stored by exception type only; raw provider errors and rejected text
are not persisted. Repeated invocations create separate attempts and may incur
separate provider charges. There are no automatic model retries. A process crash
before the record is saved can leave an unrecorded provider request.

## Local configuration

Requires an Azure OpenAI deployment supporting Responses and structured outputs.
Availability and quota must be checked in the user's subscription. Nothing has
been provisioned and no live model call has been verified in this change.

Install `scripts/requirements-llm.txt` in a local Python environment. Set process
environment variables `AZURE_OPENAI_ENDPOINT` (resource root HTTPS URL ending in
`.openai.azure.com`), `AZURE_OPENAI_DEPLOYMENT` and `AZURE_OPENAI_API_KEY`.
Keep the key out of chat, repository files and command history; use a hidden
prompt or a local secret provider. The current adapter supports this Azure public
cloud endpoint format only. It uses `/openai/v1/`, `store=False`, a 45-second
request timeout and a 1,500-token output cap. SDK HTTP logging must remain off.

```powershell
python scripts/ticket_planner.py --ticket-id <existing-ticket-uuid>
```

This leaves the ticket queue and classification unchanged. Query results,
lineage gates and snapshot comparability remain the deterministic backend's
responsibility. Planning is not yet available through the HTTP API or UI.

## Verification and next work

Offline tests cover unknown reports, unsupported metrics, explicit filter
conflicts, SQL/diagnosis field injection, missing scope, durable attempts,
sanitized failures and unchanged ticket status. These are contract tests, not
live model quality evaluations. Next: configure a deployment, run representative
ticket evaluations (including ambiguous scope and unsupported date filters),
then implement reviewed handoff and evidence-grounded explanation.

References: [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
and [Microsoft Azure endpoint configuration](https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/switching-endpoints).
