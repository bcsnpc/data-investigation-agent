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

An initial offline check using the earlier approved fixture context plus the
later six model-owner payloads produces no bridge without endpoint evidence.
Adding the exact retained three-endpoint receipt binds five original-container
tables; that older context lacks their collected physical column schemas, so
it binds zero columns. These limited-input numbers are not a rebuild of the
later coverage graph. Full unchanged-input graph counts require its raw retained
owner payloads; no physical evidence is reconstructed from graph labels.

Regression checks: 74 passed across DirectLake, static extraction, collector and
partition tests. Cases include renamed/duplicate container labels, unknown or
duplicate expressions, multiple partitions, dynamic expressions, imports,
missing sourceColumn, calculated columns, missing endpoint proof, mismatched
servers and contradictory endpoint declarations. Zero estate/model calls.
