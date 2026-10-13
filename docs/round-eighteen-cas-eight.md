# Eight historical tapes: local CAS verification

2026-10-13 UTC. This is a bounded eight-tape result, not completion of the whole
historical archive migration. Originals and sealed events were unchanged.

The eight source IDs are `10fe967b-ac1b-4bdc-9ec8-87717aa4c4dd`,
`1a384606-630d-468e-b628-9e9b18c00431`, `1f9dad9a-057d-4158-8ba8-94e9ff6a8ce3`,
`27e7c3f6-0b57-4c70-b862-84edf3af0ebe`, `32e15ad1-bd79-468f-9e01-0af578aa2ea5`,
`35883d6f-5e51-48e3-99b8-5d0011d4c8ba`, `36ed5cb1-4a6b-4f79-bfcc-044696f0f0f3`,
and `55eadb6a-9d56-4a7c-ad5d-b5c92b7ddf22`.

| Check | Measured result |
|---|---:|
| Original SQLite/tape files | 32 |
| Original bytes | 1,958,359,736 |
| Files byte-identical after CAS restoration | 32/32 |
| Actual pinned-engine replay after CAS restoration | 8/8 matched |
| Shared CAS bytes before | 25,200,488 |
| Shared CAS bytes after | 48,595,256 |
| Incremental stored CAS bytes (references separate) | 23,394,768 |
| Serial conversion, restoration and actual replay wall time | 946.126 s |
| Estate requests / model calls | 0 / 0 |

The pinned engine is `0cc86cddd1aa65e33bb4dde48d720c56387a9e68`.
The independent original-tape laptop baseline was 8/8 matched in 198.253 seconds
with eight parallel workers. The CAS measurement is serial and includes conversion
and restoration, so those wall times are not a speed comparison. Each CAS bundle
has its own seal and result in the private `.local/round-eighteen/cas-eight/`;
`summary.json` records the combined values. The actual replay result is distinct
from the preceding byte-restoration proof. Temporary restored scratch was retired;
the helper did not delete any original or call a cloud endpoint.

The broad metadata inventory still contains 397,963,664,593 logical bytes across
21,841 files (184,051,580,886 NTFS allocated bytes). It includes active/protected,
privacy-quarantined and provenance-review-required material. A filename under an
old round is not proof it is safe to archive. Shared ledgers, current catalogs and
the owner demo remain protected. This result does not claim the remaining set was
converted, uploaded or deleted.
