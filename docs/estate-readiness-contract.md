# Prospective estate readiness

The offline command is `python scripts/estate_readiness.py --manifest <estate.json> --approval <approval.json> [--index <readiness-index.json>]`. It reads local retained evidence only. Exit 0 means READY; exit 2 means BLOCKED. Missing evidence is a named block, not inferred completion. It does not block diagnostic execution, authorize a read, or change an archived replay result.

The `estate-readiness-v1` index contains `pins` and `stages`. Pins are the canonical manifest hash, retained context identity and hash, whole configuration hash, and current engine hash. The six stage names are `discovery`, `discovery_approval`, `transformations`, `bindings`, `reader_verification`, and `publication`. Each stage reference contains the original local path and SHA-256 of its bridge receipt.

A bridge receipt contains the same pins and original facts, plus `sources`. Each source names `path`, `sha256`, `field`, and an RFC-6901 JSON `pointer`. Every checked field must equal that selection in its original hash-pinned artifact. Missing fields, changed bytes, duplicate entries and invented summary facts refuse. Bridges cannot replace missing authoritative evidence with prose or a READY label.

Stage facts are:

- Discovery: `scan` with COMPLETE status, nonempty complete coverage, and all manifest layer/resource asset identities.
- Approval: the original `approval` and original `manifest`; context/configuration/engine pins and the exact approved manifest-file hash must match.
- Transformations: `discovered_declarations`, `inventory`, `boundary_inventory`, and `extraction_status`. Every discovered declaration has exactly one READ, DIRECT or UNSUPPORTED disposition. READ carries retained content and reader identity; DIRECT requires an explicit DIRECT_REFERENCE operation. UNSUPPORTED blocks. Every configured boundary names its declaration evidence. A missing exhaustive extractor receipt is a block, including when existing code retained only recognized forms.
- Bindings: schema-validated `proposals`, covering exactly the manifest boundaries. An empty executable binding inventory cannot certify a semantic-only installation as fully onboarded.
- Reader verification: original `verifications` and `model_contexts`. The consumer recomputes every verdict from both original quantity-bound observations and checks native evidence IDs and VALUE_QUERY binding. A producer's VERIFIED label is insufficient.
- Publication: original `replay` and `publication`. Replay must be COMPLETED and matched, its exact original receipt hash and capture hash must match the PROFILE_APPEND_ACCEPTED receipt, and publication pins must still match.

SNAPSHOT_UNVERIFIED remains allowed: readiness establishes completion of onboarding at its recorded scope, not proof of query-bound snapshot currency or general equivalence. Missing query-bound snapshot identities are still limitations on every dependent claim.

For new acceptance scores, `grade(..., prospective=True, readiness={manifest, pins, index, base})` recomputes these checks before grading. An unready estate yields `NOT_SCORED`, reason `estate-not-fully-onboarded`, and `passed: null`. Passing a fabricated READY report cannot admit scoring. The legacy `grade` default is reserved for archived replay under its original contract; no sealed tape, oracle or expectation is revised.
