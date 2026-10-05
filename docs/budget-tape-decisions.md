# Versioned budget decisions

BUDGET replay compares all structured decision, reservation and count fields,
including the reserved/actual maps stored as JSON text by SQLite. Formatting and
map key order do not participate. Different counts, omitted fields and different
decisions still refuse. Physical requests and provider bodies remain byte-exact.
The same budget consumer is installed for archived producer revisions; their
engine code and provider payload shaping are otherwise unchanged.

Accounting contract v2 is assigned retrospectively to #393 (`7abaabf`): physical
guard/control accounting and bounded serverless resume changed accounting.
This dated version history is an annotation, not a rewrite of any sealed tape.
The new recorder envelope is bounded-worker-tape-v3 and seals accounting_version 2.
Archived replay reports accounting version 1 before #393 and 2 at/after its
immutable commit; original v1/v2 envelopes are not changed and still replay.
Prior engine freezes invalidated. No estate reads or live investigation in this PR.

The numeric reproduction diagnostic found a PROVIDER_REQUEST byte mismatch at
ordinal 2557: cell_display_names map key order differs, although its structured
content is identical. Subsequent finally settlement masks it with BUDGET versus
PROVIDER_RESPONSE. Budget representation matching does not authorize relaxing
provider matching. This limitation remains recorded pending the fifteen-case grade.
