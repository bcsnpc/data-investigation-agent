# AI providers â€” Round 26

Status: implementation in progress; no new provider has earned investigation support yet.

| Provider | Transport | Live access | Same-dev benchmark | Status |
|---|---|---|---|---|
| Anthropic | Existing Messages adapter; cache_control retained | Existing Key Vault reference | pending Round26 | prior live path, Round26 pending |
| OpenAI | Responses, client-side function calls; normalized usage | key verified; model-list HTTP200, synthetic tool call passed | pending | offline-tested only |
| Azure OpenAI | Configured Azure Responses endpoint | not deployed or requested | not run | fake-endpoint tested only |

One content contract carries text, images, tool calls/results, schemas and call IDs. OpenAI input-token totals include cached reads/writes; Anthropic reports ordinary inputs separately. The normalized usage keeps those distinct so rates do not double-count input. Unknown usage stays charged. Switching vendors does not reset the $3 actual-use ticket threshold. Provider monthly accounts remain independent.

Official implementation references, retrieved 2026-11-01: [function calling](https://developers.openai.com/api/docs/guides/function-calling) and [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching). Cache capabilities depend on the selected model. Explicit caching is an opt-in configuration, not inferred merely from a model name. Model availability and prices will be pinned after the owner's model-list check; no assumed model is dispatched.

Cross-provider grading, all component routing, stable-prefix assertions and provider benchmarking remain pending. Existing unredacted tapes and sealed expectations remain unchanged.


2026-11-01: `gpt-6-astra` is the strongest accessible model selected for the required OpenAI benchmark, per the [official model guide](https://developers.openai.com/api/docs/guides/latest-model). Standard rates pinned from the [model card](https://developers.openai.com/api/docs/models/gpt-6-astra): input10USD, output50USD, cached-input1USD and 30-minute cache-write12.5USD per million tokens. Larger-context premiums must be bounded before dispatch. Synthetic transport check0.001660USD; transport access is not investigation quality. Owner confirmed key storage; expiry is still a placeholder, so no exact expiry is asserted.
