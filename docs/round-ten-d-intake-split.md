# Round Ten D ? extraction and code resolution

Updated 2026-10-08 America/Chicago. PR #423 remains draft. Previous recorded runs and expectations are unchanged; prior freezes are invalidated by this engine change.

The [35-request audit](round-ten-d-character-audit.md) records each component. Actual request bodies averaged 59,207 characters; the dominant model metadata component averaged 29,560. Earlier whole-day totals must not be divided by this batch's calls: this batch reserved 77,748 characters per call, including the larger catalog payload.

The current producer uses `ticket-spans-v1`: ticket text, the consumer-owned question-kind enum, and a sorted compact list of measure/column/table names when present. It receives no visual inventory, catalog identity, value inventory or definition body. The name list is bounded at 4,000 serialized characters; the complete provider request is bounded at 20,000. The same provider-body builder supplies admission sizing and transmission; oversize is recorded before transmission. No catalog truncation or guessed fallback occurs.

The model supplies verbatim spans and semantic labels, not offsets or resolved IDs. Code computes offsets, resolves measures by exact name, declared alias, then normalization, and resolves typed selections against metadata. Report projection display names supply declared aliases, not inferred synonyms. Dates without faithfully typed endpoints refuse rather than disappear. Model-only named questions remain model-only. The proposed record carries the extraction and computed spans in its closed contract; validation re-resolves them against retained metadata and rejects changed targets, figures, scopes or identities.

Only PRIMARY spans contained in the primary question and outside all COMPARISON/CONTEXT spans constrain the visual. Explicit names and adapter-owned neutral forms constrain the retained directory; one candidate resolves with its basis, multiple list TARGET_AMBIGUOUS, zero TARGET_UNRESOLVED. An unavailable inventory value cannot choose a target. A selected value does not prove which visual displays it. A reported value cannot choose a visual by matching its result.

Historical wire-v2 decoding tests explicitly call the legacy decoder. Production never selects the old decoder from a response shape or falls back to the full inventory. Current protocol tests independently cover comparison exclusion (even if mislabelled PRIMARY), the sealed wrong-cell regression, unique/multiple/missing targets, mixed questions, closed fields and code offsets, aliases, tampering, the whole-request cap and real intake admission/settlement.

## Dry-run admission

Pending admission against the existing governor, not a new environment. The preserved daily input reservation is 7,997,743 / 8,000,000, leaving 2,257. The fresh 59 plus nine rebuilt records have not been evaluated under this producer. Preflight request sizes are preparation, not measured model usage or evidence of correct extraction. Section 3 is not passed; sections 4?6 have not executed. No credential, identity, permission, fixture, cap or counter changed.

DECIDED WITHOUT REVIEW: persist extraction provenance in the existing proposed-record contract and recompute it during validation, rather than passing a second unvalidated side channel. Use a single shared provider-body builder instead of maintaining an intake-only estimate. Preserve legacy decoder tests explicitly rather than allowing production protocol autodetection. Refuse unresolved typed/date scope rather than inventing values or dropping restrictions.
