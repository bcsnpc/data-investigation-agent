# Round Ten D: dedicated current-intake CI provider

Dated 2026-10-08 UTC. Human decision under CLAUDE.md section8: Round Ten D section4 explicitly approves a dedicated Azure OpenAI key **or deployment**, a low quota, and endpoint/key repository Actions secrets; the latest instruction directs this setup after reporting the full68 dry run, with live work conditional on its pass. The completed dry gate failed and remains failed.

**Applied:** dedicated `investigator-intake-ci`, `gpt-5.4` version `2026-03-05`, GlobalStandard capacity10. Served control-plane rate limits:100requests/minute and10,000tokens/minute. Before: three deployments, no dedicated intake CI deployment. After: those same three byte-identical deployment records plus the new succeeded deployment. Existing quality deployment stays at100,000TPM/1,000RPM; neither its quota nor any other setting changed.

Exact create command (existing model-resource control profile):

```powershell
python -m azure.cli cognitiveservices account deployment create --subscription d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9 --resource-group rg-investigator-dev --name aoai-investigator-9696025 --deployment-name investigator-intake-ci --model-name gpt-5.4 --model-version 2026-03-05 --model-format OpenAI --sku-name GlobalStandard --sku-capacity 10 -o json
```

The complete before/create/after responses are preserved in `.local/round-ten-20261007/part-b/part-d-approved/ci-control`. `control.json` records the human authority, commands and exact states. Microsoft documents [quota allocation](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/quota) and [deployment automation](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/automate-quota-deployments); the actual rate limits above come from the served control response, not an inferred conversion.

Before Actions secret listing: `KNOWN_DOMAIN_REPLAY_KEY` only. After: that secret unchanged plus `INTAKE_MODEL_API_KEY` and `INTAKE_MODEL_ENDPOINT`. The commands were `gh secret set INTAKE_MODEL_API_KEY --repo bcsnpc/data-investigation-agent` and the equivalent endpoint command, with values supplied through stdin. The model account's existing key1 was fetched and held only in memory, passed directly to gh stdin and released. No raw credential was written to a project file, printed or placed in argv. No key rotated, no app created, no Entra role, reader scope or estate credential changed.

DECIDED WITHOUT REVIEW: choose the explicitly permitted dedicated-deployment route at capacity10, retaining the same model/version used by the dry run. Rejected rotating an existing key or changing the investigation deployment's quota. Azure account keys are account-scoped, **not deployment-scoped**; the deployment quota is throughput isolation for the configured CI route, not a credential authorization boundary. This limitation is explicit.

Current-prompt evaluation now lives in `.github/workflows/current-intake-evaluation.yml`: manual dispatch, nightly08:00UTC, and PRs changing intake code, prompts, supporting validators/catalog resolution or golden/profile files. It is removed from the ordinary all-PR Validation workflow. Endpoint and API key both come from Actions **secrets**. Concurrent evals queue rather than overlap. Manual/nightly activation requires this workflow on the default branch; #423 remains draft. PR execution is independent and may fail on the known quality findings.

The runner executes fresh provider responses and the current schema/validator, with no cached-response fallback or estate transport. Missing credentials, provider errors, incomplete batches and failing quality scores fail visibly. It retains scores and the plan as hosted artifacts, not provider bodies or secrets. Its own CI quality governor permits118planner reservations for59cases including one retry each; no investigation cap is raised and no estate counter is reset.

No CI quality pass is claimed by credential provisioning. The local68-case gate is FAILED (1/50fifty matches,0/9resolved on either estate). No live rehearsal, changed-outcome list or billing execution follows. Prior freezes remain invalid.

## Exact secret listings (names and timestamps only)

Before:

```text
KNOWN_DOMAIN_REPLAY_KEY	2026-10-05T07:08:58Z
```

After:

```text
INTAKE_MODEL_API_KEY	2026-10-08T19:36:09Z
INTAKE_MODEL_ENDPOINT	2026-10-08T19:36:09Z
KNOWN_DOMAIN_REPLAY_KEY	2026-10-05T07:08:58Z
```

Verification: both workflow files parse; manual/nightly/path-filtered PR triggers, secret references and dedicated profile checked. The real model-eval intake suite passed28tests in10.251seconds; it complements the2,402-test complete regression. No live provider probe was substituted for a quality score. Both verification results have appended ledger rows.
