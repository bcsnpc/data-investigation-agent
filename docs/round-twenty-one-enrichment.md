# Enrichment pass: implementation and deferred live proof

The enrichment job has its own provider adapter and a separate owner-provisioned
account, `enrichment:round-twenty-one`, MICRODOLLARS, ceiling25,000,000,
protected0. It cannot use the investigator's monthly account. The worker never
creates that account. Request reservations bound UTF-8 input bytes plus framing
and the configured maximum output; returned actual token usage settles them.
Unknown usage retains the full reservation. Rejected prose is still charged.
Repeated submission of a previously admitted batch is refused, preventing a
second external send behind an existing reservation.

Provider API details stay in `adapters/enrichment_anthropic.py`. It uses
`claude-sonnet-4-6` through Message Batches with JSON-schema outputs, capped at
50 requests and4,000 output tokens each. Official documents checked2026-10-22:

- [Create a Message Batch](https://platform.claude.com/docs/en/api/messages/batches/create): asynchronous create; results can take up to24hours, and output_config supports JSON-schema format.
- [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing): match custom_id, never result order; input/output batch discount50%.
- [Pricing](https://platform.claude.com/docs/en/about-claude/pricing): selected Sonnet4.6 batch rates USD1.50 input/7.50 output per million tokens. These are a pinned rate-card estimate, not an invoice. No caching, tools or regional premium is requested; unexpected usage categories remain uncertain.

The app's gateway uses a separate `enrichment` policy role with:

```json
{"enrichment_batches":{"provider":"anthropic","purpose":"ENRICHMENT_ONLY","model":"claude-sonnet-4-6"}}
```

It authorizes only the exact compiled create request and response-bound reads of
that submitted batch and its results. It does not permit ordinary Messages API,
other models, arbitrary batches, cancellation, deletion or estate mutations.
The investigator's provider selection is unchanged. The existing managed
identity retrieves one versioned Key Vault reference in memory. The key travels
only in the HTTPS header; request/response capture excludes all headers. A
provider echo of the key is refused before recording. There is no environment
key, CLI fallback or saved credential. Exact permitted Key Vault GET metadata
must be included in the operator's existing policy for that identity.

Every response follows a fixed schema: business meaning, synonyms, calculation
explanation, hidden logic and proposed links. The latter must target a supplied
neighbour and quote an exact character span of the pinned definition. Links
remain INFERRED even after a human prose correction. There is no graph promotion
or runtime-fact write path. Query validation remains separately necessary.

Enrichment records use existing SharedState document namespaces, no new tables
or migration. Cache identity includes estate, subject, definition hash and
neighbour hash. Definition changes enqueue durable PENDING work in the same
existing graph-change transaction. A job consumes only changed/uncached inputs;
the operator must wire queue processing to its approved scheduled path. No
automatic paid provider call runs merely because a graph transaction commits.

Human CSV import records reviewer/time and HUMAN_CONFIRMED provenance. It
validates all rows before applying any correction and never promotes links.
Human prose always wins over later model output. When its definition changes,
the retained human correction is visibly `stale_definition=true`; intake must
not consume it as current until reviewed. New model output remains available in
the definition-keyed cache. CSV export escapes spreadsheet formula prefixes.

## Entry points

```powershell
python scripts/enrich_estate.py plan --tasks <definition-pinned-tasks.json>
python scripts/enrich_estate.py stub --tasks <synthetic-tasks.json> --outputs <recorded-stub-outputs.json> --database <private-offline.sqlite> --batch-key <unique-key>
python scripts/enrich_estate.py submit --tasks <definition-pinned-tasks.json> --config <secret-reference-only-config.json> --batch-key <unique-key>
python scripts/enrich_estate.py resume --config <same-config.json> --batch-key <same-key>
python scripts/enrich_estate.py export --tasks <same-tasks.json> --csv <review.csv>
python scripts/enrich_estate.py import --csv <review.csv> --reviewer <owner-name>
```

Live config contains only `secret_reference` (existing vault URL/name/version and
managed identity declaration), `gateway_identity`, and `worker_identity`. Shared
state and gateway environment are the existing approved worker configuration.
Submission exits with SUBMITTED; resume does one status check, returns PROCESSING
when unfinished, and never busy-polls. Original provider rows, exact request
bodies and submission receipts survive independently of parsed cache records.

`tasks_from_graph` is an operator enrichment enumeration, not ticket verification:
it covers report/page/visual/measure/calculated-column nodes and explicitly
selected key-table IDs. It pins definitions and neighbours from the existing
graph. A CAS definition reference must be resolved through the operator-provided
resolver and its exact byte length/SHA-256 verified. A pointer is never serialized
as a substitute for the definition text. Missing definitions refuse explicitly. Inputs larger than the bounds refuse rather than being truncated.

The recorded stub is explicitly RECORDED_STUB and permitted only in private
SQLite offline state. It cannot populate live PostgreSQL or claim live provider
coverage/spend. Acceptance must keep stub and live results separate. Tests cover
actual provider record/replay with network/Key Vault disabled on replay, result
identity matching, exact spans, independent budget admission/settlement, human
priority, cached and changed definitions, and graph transaction queueing.

Projected live shared-state enrichment remains unavailable because the existing
PostgreSQL privacy-projection boundary is not implemented. It refuses before
submission/storage instead of silently capturing raw values. Planner sidecars
use the existing projection-aware recorder; this does not by itself make raw
SharedState writes privacy-safe.

No Anthropic key was retrieved or created by this implementation; no live batch
was submitted and no estate request was made. Per-estate counts, actual provider
cost and five live examples remain to be earned after the owner creates the
approved key and the operator provisions the separate account.

The resumed offline preparation resolves retained CAS bytes for fifteen selected
objects: five each from fixture, billing and dia-sample-estate. Every byte length
and SHA-256 is checked before building a task. The five kinds are report, page,
visual, measure and table. Private batch results and task inputs are under
`C:\dia-r21-facts-ledger\.local\round21-helper\enrichment-stub-examples`;
the public [summary](runs/round-twenty-one-enrichment-stub-examples.json) labels
every example RECORDED_STUB. This is a wiring demonstration with deliberately
minimal placeholder prose, not fifteen model-enriched meanings. It claims no
synonyms or hidden logic, proposes no links and promotes none. Actual provider
calls, estate reads and enrichment spend are zero. The simulation timestamp is
an injected test clock, not a live observation time. No shared PostgreSQL
enrichment projection was written.

Collector configurations use exact existing graph IDs. Fixture selects two
pipelines, its demo model and the Bronze landing table; billing selects its two
pipelines and model; sample selects its model. The fixture landing table and
audited producer use the declared Warehouse audit source, requiring matching
producer/run and OBSERVED_COPY_OUTPUT provenance. Configuration is not a
collected fact: this helper made no collector read. The
[preparation summary](runs/round-twenty-one-collector-preparation.json) records
configuration hashes and gaps. No per-load checksum key columns are invented:
without declared keys, the key-table list remains empty and row-count/checksum
coverage unavailable. SQL endpoint modify time never substitutes for load
history. Application SQL and the legacy lakehouse audit are not silently added
as routes. Partial selected coverage is not whole-estate coverage.

Preparation update: the owner-selected six checksum columns for fixture landing
are now configured from retained metadata SHA
`ec45d792a5e5f2d5c4bd2a04f33e4e5396583c1820af85c2f99f7722d124eaab`:
movement_id, warehouse_id, product_id, units, event_day, movement_type. Schema
and table names come from the same definition. The SQL database name is the
retained native self-report in `docs/runs/R3-final-baseline-reader-verification.json`,
not a transformation of a lakehouse catalog label. The next live read must
freshly attest the existing investigator principal. This adds one configured
fixture profile, not a collected profile or a uniqueness assertion. Billing and
sample still have no declared profile keys. The updated preparation summary
records this delta and the new private configuration hash.

Live audit2026-10-22: initial200responses rejected unsupportedlinkvocabulary; new-schema200responses rejected199quote/offsetmismatches and1invalidspan. Originals and their model charges remain. The new enrichment-source-references-v1 producer supplies numbered200-character source segments; the model selects contiguous segment IDs, and trusted code extracts their exact original Unicode substring. The original consumer offset/quote/target/kind validator remains mandatory, links remainINFERRED, and rawproviderrows remainunchanged. This protocol only applies when the stored request explicitly uses its reference schema; historical rejected offsets are never backfilled.30enrichmenttestsPASS including actual BatchClient-to-EnrichmentJob result application and repeated/Unicode source spans. New live success notyetclaimed.
