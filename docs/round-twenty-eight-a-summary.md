# Round 28A ? estate configuration and local replay API

Completed the owner's narrowed scope offline on `round-twenty-eight-templating`.
Separate draft PR: https://github.com/bcsnpc/data-investigation-agent/pull/436 .
No estate reads, model calls, new Azure resources, identity/permission changes or ledger changes.

`estate-config/1` now covers installation identity, connector references, six layer
roles, source of truth/reachability, identity and secret-name references, model and
limit declarations, and disabled optional sources. The existing validated native
installation remains the binding source; the loader projects it unchanged. Existing
shared gateway and budget policies remain authoritative. Both the practice config
and disabled hospital draft validate through `dia estate validate` without network
or secret resolution. Invalid references, missing layers and secret-value fields refuse.

The local API provides authenticated submit, status, result and health endpoints.
Requester and estate scope are checked; every request is durably audited. It is
replay-only, with exact saved-request matching and no native/model fallback. A real
saved billing delivery returned unchanged over HTTP, with all four calls audited.

| Check | Final result |
| --- | --- |
| Full repository suite | **6,219 passed, 53 skipped**, zero failures/errors |
| Image shards | **8/8 passed** |
| Focused config/API/literal/tape tests | **60 passed**, 22 subtests |
| Ordered saved replay | **123/123 classifications identical** to current R27 head |
| Frozen confirmation files | **248/248 byte-identical** |
| Saved delivery through local HTTP | **PASS**, delivery unchanged, 4 audited requests |

The replay still has 86 finished, 28 negative and 9 no-investigation cases. These are
preserved regression classifications, not a new quality score. All three recorded
R27 exceptions remain exactly as they were. Qualification source: `3c37d9c7227eda143751cbe8ed21c1856a7c6a7a`;
workflow [45875413156](https://github.com/bcsnpc/data-investigation-agent/actions/runs/45875413156).
The code image was published, **not deployed**. The final follow-up commit adds reports only.
An initial API UUID-source violation was fixed using the existing recordable identity
source; the validation rule was kept unchanged.

Known concrete estate literal hits in scoped engine/runtime: **0 before / 0 after**.
The historical audit remains 4,594 indexed line hits: 932 estate config, 83 identity/
secrets, 267 infrastructure and 3,312 test-only. Generic platform terms in that index
are not concrete estate literals. Runner/test-fixture cleanup and connector stubs
were explicitly excluded by the narrowed owner steer.

PR #435 remains open/draft at `d20bbd544862acc514d0a716adcc3ebd474f708b`, with its frozen
image and files unchanged. Neither PR was merged or tagged. On Dec 1, R27 restoration,
the last four tickets on its original image and its gate plan run **first**.

Owner actions: approve API ingress on Azure and provision a named API secret before
any future public deployment; confirm December Anthropic balance and grading funding
for R27. No API secret was created; tests used memory-only tokens.

Details: [configuration](estate-config.md), [API](api/README.md),
[qualification](round-twenty-eight-a-qualification.json),
[replay](round-twenty-eight-a-replay.json),
[immutability](round-twenty-eight-a-immutability.json),
[HTTP proof](round-twenty-eight-a-api-replay.json).

## Named-connection extension, 2026-11-26

PR #436 additionally supports multiple named SQL databases in one native bundle,
with per-layer references and independent reader/secret bindings. The practice
fixture remains one connection with its native manifest unchanged. HealthNet is a
disabled metadata-only draft, validated offline; no test material or live data was
read. Final qualified source `4d4fd7ed`: 6,228 tests passed / 53 skipped, all eight
image shards green, 123/123 saved classifications and 248 frozen hashes unchanged.
See [extension report and receipts](round-twenty-eight-connections.md). No deployment,
merge or tag.
