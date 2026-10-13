# Recorded report versions: offline incremental change and revert

2026-10-13. This is an offline validation using two actual retained report
definitions, not a live controlled estate edit or a new collection. Estate
requests: **0**. Model calls: **0**.

The original read-only catalog at
`D:/data_investigation_agent/.local/unknown-domain-v4/catalog.sqlite` retains:

| State | Context | Sealed context hash |
|---|---|---|
| report-14sep | `3ae7607b-5a5e-46c6-8e1b-195dbabc9cae` | `d6f3841fc02368a066f2de2d2e8bb4c22579b02d3bce3a95e441996091d5784f` |
| report-15sep | `e920dda4-d5c8-4a95-b9e9-a600386ae3d5` | `baf3044545048d410b602ed8bec138e878d7d61da32490b364e42891db2beb2a` |

Both retain the same report
`fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995`
and 16 native definition parts. The historical scan rows are absent from this
catalog; the hash-checked context bodies retain the native part bytes. Original
observation times are October 1 and October 4 respectively, not today's date.

Exactly one native part differs:
`definition/pages/8b067ecb975e5af7a39b/visuals/a32b6a48db655ac8a4f2/visual.json`.
Its SHA-256 changes from
`41b2c66d525a988c083fc4368e6fb9f3cc4b4a68ecfd9390ead21d34da39e64a`
to `676e53f55b826174482f8dd88c53d10529e42cee817eca731e4ca3af648ad6cb`.

The generic `scripts/validate_retained_graph_versions.py` validates context
hashes, uses the existing collector expansion for page/visual children, and seeds
an isolated offline graph and CAS. The baseline model assets are retained across
the test. `IncrementalScanner` replaces only the report owner's asset payload;
`AssetCatalog` extracts over the merged retained catalog and updates affected
partitions atomically. `GraphAPI.filters_on` returns the real
`visual_event_day` predicate as **2026-09-14**, then **2026-09-15**, then
**2026-09-14** after replaying the original definition.

| Returned filter content (version timing excluded) | SHA-256 |
|---|---|
| Before | `08724140ea54f2e47a8aae780444106a009d8a1a6b839e00770125ea00de417c` |
| Changed | `fe71ddb6bd9f575a595828ba7ee930ea8a1811c420be5f28c4f1b29b1c7b7fd2` |
| Reverted | `08724140ea54f2e47a8aae780444106a009d8a1a6b839e00770125ea00de417c` |

**PASSED:** change is returned, revert restores identical filter content, and
the original as-of version retains its complete original content/provenance.
Closing a history interval adds its `valid_to` boundary; this is excluded from
the original-content equality check, not erased from history. The report has
three version records; the unrelated model's history stays unchanged. Every
fetch in this validation is the same explicit report owner.

Derived files only:
`D:/dia-r19-state/.local/round-nineteen/retained-definition-change-02/`.
`receipt.json` SHA-256:
`617025b92881d66aebebcf1a64ed5fd80fe3d3f7e68ad7c4e06651acd75d8d30`.
This contains scanner results and graph history; adjacent before/after/reverted
filter JSON files retain exact returned payloads. The derived SQLite and CAS are
local. Original contexts, approvals and tapes were neither edited nor replaced.

The first derived harness attempt (`retained-definition-change-01`) stopped on an
overstrict comparison that included the newly closed historical interval. It is
preserved. The corrected harness checks original body/provenance separately from
that expected temporal closure. These simulated scan times establish no claim
that a live scanner successfully refreshed these owners today.
