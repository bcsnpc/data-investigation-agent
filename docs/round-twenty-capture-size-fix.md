# Lossless outer capture encoding

The first demo after fixed-identity binding failed on the platform Blob PUT for
`00000490-tape-event.json`. Its run-specific URL and immutable headers were
valid; earlier objects succeeded. The gateway's 32 MiB body bound denied the
larger exact catalog response. The partial capture remains unchanged: 489
objects, no final seal, no delivered answer and no complete native replay.

The capture writer now compresses an oversized JSON record into an explicitly
labelled `gzip-base64-v1` envelope. It retains the original byte length and
SHA-256; the sealed record reference declares its encoding. A decoder bounds
decompression to the declared size (maximum128 MiB) and checks length and hash
before parsing. Encoded objects must still fit the existing32 MiB gateway
limit. Incompressible or larger records refuse explicitly before queueing; the
gateway has not been broadened. Ordinary records retain identical bytes, and
native tape bytes and historical captures are unchanged.

Secret validation runs on the original uncompressed bytes before encoding or
transport. Boundary replay decodes only records explicitly labelled in their
sealed references; ordinary user dictionaries cannot accidentally select a
decoder. Regression tests cross the real gateway size limit, replay the sealed
result, reject altered hash/length and unknown encoding, reject a synthetic
secret before publication, and preserve legacy record bytes.

Clean pre-fix regression:4,747 passed,47 skipped,1,622 subtests. Four new encoding
tests pass. An initial mixed focused run also retained seven expected
TAPE_UNCOMMITTED_ENGINE refusals while engine files were uncommitted; those are
not behavioral regressions or test passes. Clean-source focused/full validation
and a fresh immutable image are required before the next demo. This engine
change invalidates the prior freeze.

Dated clarification2026-10-21/UTC22: fixed03 losslessly captured a52,580,080-byte CONFIGURATION event (shared application state/history), encoded13,249,750bytes; original bytes/hash restored. This was not a catalog READ_RESULTS event. Whole-history overhead remains a Round21 path-scoped loading concern.
