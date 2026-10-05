# Canonical provider replay: fifteen of fifteen

2026-10-05 UTC. Implementation PR #402 merged as
`dbcf18370fca61eab03a8eec756283edeee98c66` with six green CI checks.
All fifteen selected sealed tapes passed one complete offline re-grade.
Zero estate reads, physical requests or provider/model calls were initiated.
The fifteen individual grading rows are appended to the ledger; every earlier
failed/blocked row and original tape/source file remains unchanged.

## Final column

| Case | Final grade | Source run | Recorded outcome / reproduction |
| --- | --- | --- | --- |
| family-A | PASSED | `746c765a-26e3-4979-a694-3f06eda15275` | TRANSFORMATION_LOGIC |
| family-B | PASSED | `8be79ae0-febb-4913-ad5c-95a0347edbfc` | NO_KNOWN_PATTERN |
| family-C | PASSED | `23ff3deb-12c4-4458-8ef0-757215d606b7` | INSUFFICIENT_EVIDENCE |
| family-D | PASSED | `7c23cadc-e788-483e-8fbf-0a14b46182d5` | NO_COMPARABLE_PATH |
| family-E | PASSED | `9b5ce960-114a-4801-a947-e6ba08819bab` | TRANSFORMATION_LOGIC |
| family-F | PASSED | `ae3436f4-3f72-4b7d-9e60-823a69ad83b0` | CONSISTENT_TO_BOUNDARY |
| family-G | PASSED | `c3be2f05-4af5-4813-85da-2bc7206cd0df` | TRANSFORMATION_LOGIC |
| family-H | PASSED | `d93995a9-0e2d-47eb-805b-c4018c4e3b39` | NO_KNOWN_PATTERN |
| family-I | PASSED | `e726e66c-17d1-4171-a6d3-ccb978aa800c` | TRANSFORMATION_LOGIC |
| reproduction-16 | PASSED | `6308d027-2ed3-4cf7-b87a-ee9aff105bfa` | REPRODUCED 16 |
| reproduction-empty | PASSED | `6575058a-4f86-422a-92ff-2f3def6687c4` | REPRODUCED EMPTY |
| source-consistent | PASSED | `a96e0ca5-0266-439d-a72f-c83a99b505b1` | CONSISTENT_TO_SOURCE |
| source-gap | PASSED | `809d67b9-82c6-43d3-ad64-c25a749a7c86` | INGESTION_GAP |
| source-latency | PASSED | `ea69d8e7-0ebf-4e3a-8d87-356cfb922235` | LOAD_LATENCY |
| source-unreachable | PASSED | `90fe815a-d244-439d-b1e1-5bf901f78587` | CONSISTENT_TO_BOUNDARY |

Numeric reproduction passed from its original sealed tape against report-15sep,
reproducing 16. Its prior request mismatch was object-key ordering inside the
provider's structured input; canonical comparison removes only that representation
difference. The conditional live re-record was therefore not executed. EMPTY
passed against its preserved report-14sep context. Source consistency uses the
previously recorded `a96e0ca5-0266-439d-a72f-c83a99b505b1` run, not a replacement
this round; every quantity is 7,661 and requested record 900099 is absent at
each checked layer. Original source failures remain historical failed evidence.

This is a fifteen-case known-domain recorded-producer regression column. Producer
revisions are pinned by native tape fields or separate hash-bound historical
bindings. Replay executes the archived engine with the reviewed transport-matching
consumer and refuses network calls. It does not test upstream platform decoding,
requalify every case on the latest engine, or establish unfamiliar-domain acceptance.
Prior freezes remain invalid.

## Matching and tests

Provider requests and responses compare compact sorted JSON bytes, including
the declared input, response-body and function-argument JSON carriers. Values,
ordinary prose whitespace and array order remain content; a one-field change
fails. Invalid JSON, duplicate keys and non-finite numbers refuse. Physical
requests remain byte-exact. Original sealed events are not rewritten.
Eight provider-contract tests, five budget-contract tests, ten planner tests
and twenty-six tape tests passed locally. Provider and budget contract tests
are now explicitly included in CI. An older planner assertion that key-order
changes must fail was replaced with canonical equality plus content refusal.
No planner context content or directory coverage changed.

## Both windows

Round Five pot: **263/400** before and after this round; 137 remain, including
the unchanged restoration reserve. Rolling 24-hour ordinary requests:
**396/1,500** at the closing control-plane read; 1104 available.
Per-run diagnostic ceiling remains 12. No credit, refund, counter reset or
policy change. GitHub/CI control operations are not estate diagnostic reads.

## Delivery gate entry

Local prerequisite: **15/15 PASS**, summary SHA-256
`574b3894ddf892016b67f8d573ee7a5996ff5be3117db4b775622f46019bc83d`. #376 is rebased onto the canonical
consumer but **not merged**. Its hosted `known-domain-acceptance` check currently
fails because no private replay inputs are available on the runner. The repository
has neither a configured self-hosted runner nor replay secret. A local result is
not substituted for that seventh check.

A 61-file private delivery bundle was prepared locally (245,953,790 compressed
bytes), containing fifteen unmodified source files/tapes, their pinned bootstrap
databases and a separate path-relocation map. Publishing an authenticated-encrypted
release asset and placing the key in an Actions secret awaits the human decision
requested this round. No raw evidence, credential or private bundle is committed
or uploaded. After approval, hosted replay must genuinely pass before #376 merges;
missing inputs will continue to fail. No gate deployment is claimed here.
