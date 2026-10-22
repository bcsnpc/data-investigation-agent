# Shared catalog read evidence (2026-10-21)

Replay03 exposes a capture gap, not a changed expectation. The sealed live intake
used two authoritative shared-catalog models, including billing; its private
SQLite backup instead contained six earlier fixture models and no billing model.
Replaying that backup generated a different declaration inventory. The first
mismatch was an extra identity request in `report_predicates._extract` where the
tape already expected the ticket's CONFIGURATION event. The live catalog hash
was `fb2130f71899e5d8b6c7ee806fb5004f1fa213dae35ef0336264d3afc3e019a5`;
the baseline-only offline catalog hash was
`0c35e7572b7bd2ec00578f0c0a4855514f5ab0a1214ec17fa2bd3367cfb1d18a`.

New shared-catalog recordings declare `shared_catalog_capture: READ_RESULTS_V1`
in their native bootstrap. Each existing get/list/context read records its exact
request and returned data through the existing bounded-call journal. A list
records its actual returned ordered set once; it does not preload every historical
context or introduce extra authority reads. Successful results and failures use
the existing protected bounded-call grammar. No network call is moved into a
shared-state transaction or budget lease.

Replay installs a read-only RecordedCatalog only for that explicit contract. Its
get/list/context calls consume sealed bounded results and never consult PostgreSQL
or substitute stale private model rows. Request drift and unknown contract versions
refuse. The private backup remains an immutable artifact and is not rewritten to
make it agree with the live catalog.

Old tapes without the declaration retain their old interpretation. Replay03 and
Replay04 are not backfilled or newly claimed to match. The two-model/fresh-recording
regression deliberately leaves six stale models in the private database, then
records and replays the exact two-model order plus get/context calls with authority
connection forbidden. Separate tests cover request drift, unknown versions and
unchanged old-tape behavior. No estate/model calls, permission or identity changes.

The related intake hard-stop regression now includes `SpendHold`, in addition to
gateway and usage holds. Intake retains only its safe error type and project
frames, settles its existing reservation, then propagates the model-spend stop.
It does not convert a missing monthly policy or exhausted monthly allowance into
a normal held answer, and does not retain the exception's private message.
