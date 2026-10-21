# Deterministic DirectLake bridge (offline)

The adapter connects an entity partition only when the retained model declares
one DirectLake partition, one named M expression with a literal `Sql.Database`
server and catalog ID, one same-workspace physical container, and one physical
schema/entity. Each data column then needs its own explicit `sourceColumn` and
unique collected physical column. Calculated columns are excluded. Missing or
conflicting declarations produce UNKNOWN boundaries, never same-name guesses.

Warehouse IDs bind directly to the exact retained Warehouse identity. The server
string remains the model's declaration, not live server attestation. Lakehouse
SQL endpoint IDs additionally require a native endpoint-to-Lakehouse response.
The endpoint and table/column provenance is retained on each static DECLARED
edge. It does not earn VERIFIED or VALUE_VERIFIED.

`retained_lakehouse_endpoint_assets` accepts original native receipt bytes and
an explicit observation time, preserving the request/response, receipt SHA-256,
JSON pointer and time in distinct evidence assets. It does not rewrite listing
metadata. The collector now retains the native Lakehouse response it already
reads for visible column discovery, so future contexts keep that relationship
without another request. Existing Power Query extraction remains unchanged.

The retained coverage-final01 graphs have **76 fixture starts** (64 VISUAL and
12 SLICER) and **7 billing starts**, not 66 fixture starts. Static parsing cannot
change their identities. The model definitions offer 21 entity tables / 92 data
columns in fixture and 9 / 32 in billing; these are potential declarations, not
resolved path counts. The imported model is excluded.

The full immutable owner payloads were subsequently restored and SHA-256 checked:
61 fixture owners and 12 billing owners. The offline audit rebuilds each graph
from those exact raw assets, first with the entity bridge disabled (the previous
behavior), then with the parser, then with the unchanged three-endpoint receipt.
It asserts every original start ID remains and no new start is introduced.

| Estate / stage | Table bindings | Column bindings | Starts reaching a terminal physical column | Complete verified source paths |
| --- | ---: | ---: | ---: | ---: |
| Fixture before | 0 | 0 | 0/76 | 0 |
| Fixture parser alone | 0 | 0 | 0/76 | 0 |
| Fixture plus retained endpoint receipt | 5 | 22 | 29/76 | 0 |
| Billing before | 0 | 0 | 0/7 | 0 |
| Billing parser alone | 9 | 32 | 3/7 | 0 |
| Billing plus retained endpoint receipt | 9 | 32 | 3/7 | 0 |

The other 16 fixture entity tables and 70 model columns do not get a binding:
the three-endpoint receipt covers the original lakehouses, not the other fixture
variants' containers. Shared SQL server and display labels cannot fill that gap.
No start reaches a declared system-of-record column, and static reachability is
not full source verification. The parser resolves all 9 billing table and 32
column declarations, but only three of seven visual starts reach physical columns:
remaining expression-dependency and route gaps remain visible.

The machine receipt is `docs/runs/round-twenty-directlake-offline.json`; it pins
the original graph bytes, catalog manifests, receipt and rebuilt graph hashes.
The full per-owner hashes and start-by-start coverage remain in the local
`part-d-directlake-audit/audit.json`. `scripts/audit_directlake_bridge.py`
reproduces the check from the immutable owner payloads without estate/model calls.
The endpoint native response contains no service timestamp; its audit time is
explicitly labelled observation of retained metadata, not a new live observation.

Regression checks: 75 passed across DirectLake, static extraction, collector and
partition tests. Cases include renamed/duplicate container labels, unknown or
duplicate expressions, multiple partitions, dynamic expressions, imports,
missing sourceColumn, calculated columns, missing endpoint proof, mismatched
servers and contradictory endpoint declarations. Zero estate/model calls.
