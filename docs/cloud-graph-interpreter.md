# Bounded retained-code interpreter batch

Run `python /app/scripts/cloud_graph_interpreter.py` in the committed cloud image. This is a model-only job: it has no estate reader, does not refresh definitions, and does not insert proposed edges into the graph. Its results require review. Every proposed edge remains `INFERRED`, `execution_established: false`, and `deployment_binding: NOT_ESTABLISHED`. The production binding verifier refuses these edges until a reader-observed deployment binding exists; equal quantity profiles cannot prove that authoring code ran.

`DIA_CLOUD_GRAPH_INTERPRETER` is public JSON with these fields:

```json
{
  "batch_id": "round19-interpreter-01",
  "environment": "existing-shared-usage-policy-name",
  "identity": {"mode": "managed_identity", "client_id": "UUID", "principal_id": "UUID", "tenant_id": "UUID"},
  "channel": "worker:artifacts",
  "input_url": "https://ACCOUNT.blob.core.windows.net/captures/round19/interpreter-01-input.json",
  "input_sha256": "64-lowercase-hex-digest-of-exact-input-file",
  "output_url": "https://ACCOUNT.blob.core.windows.net/captures/round19/interpreter-01-result.json",
  "model": {"mode": "key_vault", "endpoint": "https://RESOURCE.openai.azure.com", "deployment": "existing-deployment", "reference": "existing-validated-version-pinned-reference-object"}
}
```

Use the existing validated identity and model configuration objects verbatim, not the placeholders above. The existing `model_session` validates the reference and retrieves credentials only into memory. Provide the same PostgreSQL shared-state, dollar ceiling/margin, worker identity, gateway channels, receipt paths and `DIA_CLOUD_SLIM_RECORDING_JSON` environment as the existing cloud-stage worker. `cloud_stage_environment.install()` materializes only public validated configuration. Use a fresh worker ID and batch ID. The configured environment must already have its approved shared `usage_policy`; this runner neither creates nor raises it.

The gateway must explicitly allow GET of the exact input URL, PUT of the exact output URL, the existing versioned Key Vault GET/model endpoint and private CAS containers. Input/output transport accepts only the private `captures` container and refuses redirects. Result PUT is create-only. CAS publication uses the existing guarded Blob adapter, capture and streaming hash verification. Raw provider messages and proposals are private CAS artifacts, not stdout.

Input is one JSON array, at most 250,000 bytes, containing one to four task objects. Each requires `estate`, `owner`, `source_id`, `observed_at`, `code`, `definition_hash`, and `nodes`. The definition hash must equal SHA-256 of the exact UTF-8 code; code is bounded to 24,000 characters. Each of at most 128 nodes has exactly `id`, `kind`, `label`. Duplicate IDs are refused. Additional retained-source metadata is allowed. Preserve the exact parent-definition CAS reference and JSON pointer for snippets, and retain each snippet in definition CAS before attaching any resulting proposal.

The shared immutable batch admission prevents accidental job retries from re-calling the model. Each task has one attempt, with no repair or deduplication. The actual compiled provider body is bounded to 64,000 characters; its full character count and 8,000 output tokens are reserved through existing SharedUsage. The installed provider enforces the existing shared dollar guard. Actual usage settles the reservation; missing usage remains uncertain. Any model, validation, settlement, incomplete-capture or publication error stops remaining tasks. An unresolved settlement is recorded separately without masking the original failure.

`planner_recording` preserves exact provider request/response bytes and the compiled request sidecar. Private CAS receives every retained capture file plus the result document. The public result contains status, attempted/not-run counts and the verified result CAS reference only. Stdout does not include code or model prose. Original tapes and graph snapshots are unchanged. This is recorded model evidence, not a claim of full investigation process-tape replay.

The cloud caller explicitly passes `/work/graph-interpreter/planner-recordings` to the recorder's `directory` argument. It does not require the installed `/app` tree to be writable. Local callers that omit the argument retain their existing directory. Error records name the failed stage; local I/O failures include errno and its standard system message. Provider text remains withheld, avoiding credential or source-code disclosure through exception messages. The first live batch's inaccessible default-directory failure is preserved, not rerun by this fix.

Offline tests exercise shared reservations, exact capture restoration, once-only admission, one-attempt refusal, authentication stop and settlement-error retention. No cloud or model call is made by those tests.
