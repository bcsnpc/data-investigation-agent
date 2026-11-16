# Cached query schemas: development correction

The stable prefix added generic query tools when absent, but retained the initial layer enum when a query tool already existed. A later lineage expansion could therefore leave the wire schema narrower than the current local validator. Both existing and initially absent query tools now use a string layer field in the cached wire contract. Current admitted identifiers remain in changing context; the investigator refreshes and validates its local enum before dispatch. Unknown layers still fail before any query executes.

This is a code-level defect and regression fix, not an established explanation of a benchmark outcome. The saved Astra quantity-v1 capture inspection found `strict: false` and no wire/current enum difference in the extracted requests. It does **not** prove the proposed strict-schema failure. The adjacent JSON is retained as a negative diagnostic, despite its historical filename. No earlier result, score, tape or expectation is changed.

Tests cover stable prefix bytes after expansion, compatibility with a newly admitted layer, unchanged caller schemas, and rejection of an unknown layer by the real investigator dispatch before estate execution. The correction applies to the next development image; the already-started three-column benchmark remains pinned to its original image and is reported separately.

Additional observational timing records capture admission journal UTC, worker start, investigation start, first model dispatch and answer completion. Missing timestamps in old captures remain unavailable, with no backfill.

Authoritative budget read on 2026-11-01: physical 2,543/9,000 (investigation 2,300/6,405; scan 225/2,500; restoration 18/95). Anthropic charged/committed USD34.413328/150; OpenAI USD37.277113/180; combined USD71.690441. No pending model exposure at this observation. No ceiling or reservation was reset.
