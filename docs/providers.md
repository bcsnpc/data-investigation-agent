# AI providers — Round 26

Status: implementation in progress; no new provider has earned investigation support yet.

| Provider | Transport | Live access | Same-dev benchmark | Status |
|---|---|---|---|---|
| Anthropic | Existing Messages adapter; cache_control retained | Existing Key Vault reference | pending Round26 | prior live path, Round26 pending |
| OpenAI | Responses, client-side function calls; normalized usage | owner key pending | pending | offline-tested only |
| Azure OpenAI | Configured Azure Responses endpoint | not deployed or requested | not run | fake-endpoint tested only |

One content contract carries text, images, tool calls/results, schemas and call IDs. OpenAI input-token totals include cached reads/writes; Anthropic reports ordinary inputs separately. The normalized usage keeps those distinct so rates do not double-count input. Unknown usage stays charged. Switching vendors does not reset the $3 actual-use ticket threshold. Provider monthly accounts remain independent.

Official implementation references, retrieved 2026-11-01: [function calling](https://developers.openai.com/api/docs/guides/function-calling) and [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching). Cache capabilities depend on the selected model. Explicit caching is an opt-in configuration, not inferred merely from a model name. Model availability and prices will be pinned after the owner's model-list check; no assumed model is dispatched.

Cross-provider grading, all component routing, stable-prefix assertions and provider benchmarking remain pending. Existing unredacted tapes and sealed expectations remain unchanged.
