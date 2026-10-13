# Retry pre-warm refusal and offline admission correction

The optional final verification retry stopped with `ValueError: VERIFICATION_PREWARM_SOURCE_NOT_DECLARED`. Its retained result records zero physical requests, controls, verification probes and model calls, with no pending reservations. No graph verification was attached.

The operator selected the application's SQL asset because the estate manifest marks it serverless. None of the18 verification proposals uses that asset. Their sources resolve to four Lakehouse tables: movements and product rates in Bronze and Silver. Warming every serverless asset in a manifest is broader than warming the actual sources of a bounded verification. The runtime restriction was correct; the input planning was wrong.

The old planner checked the optional pre-warm declaration's shape, but not its membership in the resolved proposal sources. It could therefore report `admissible: true` for an unusable declaration. The corrected planner reports false with `prewarm_scope_validated: false` until a pre-warm spec has both configuration and resolved objects. `preflight` resolves only retained, hash-pinned endpoint metadata, checks the same source/serverless restriction as runtime, and has no transport or model seam. The cloud stage performs it before PostgreSQL candidate publication; verification repeats it before creating a capture or reserving usage. Runtime controls retain the same fail-closed scope check.

Run offline admission with:

```text
python scripts/cloud_binding_verifier.py --plan verification-spec.json --manifest estate.json --context context.json --endpoints endpoints.json
```

The CLI refuses a pre-warm spec without those retained inputs. A next-run operator must choose pre-warm assets from the intersection of resolved proposal-source assets and manifest layers explicitly marked serverless, not from the entire manifest. When that intersection is empty, omit the optional `prewarm` field rather than sending an empty or unrelated declaration. This is input construction for a new reviewed input; never edit an archived spec or receipt.

Offline inspection of the actual failed output reproduced the same refusal. A separate in-memory prospective spec omitting the unrelated pre-warm declaration passed retained-input admission:18 bindings, two target catalog reads,40 planned verification probes within the unchanged cap of40, and no pre-warm assets. That is a planning result only, not a successful verification. No new input was published and no retry was run. The original spec, captures, publication and failure remain unchanged. These code changes affect future engine pins; they do not repair the historical run.

Regression tests cover the unresolved-plan refusal, a manifest serverless asset unrelated to the proposal sources, valid source-scoped pre-warm, and omission when no serverless proposal source is reached.
