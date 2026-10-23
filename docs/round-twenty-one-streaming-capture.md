# Round Twenty-One capture memory repair (offline implementation)

The retained Round Twenty outer execution has no exit code. Its historical
termination cause remains unestablished; this change does not label it OOM.
The implementation nevertheless had concrete memory amplification: Tape kept
all event bodies resident, then built full canonical JSON text and bytes twice
at FINAL. Native export additionally read complete tape and journal files.

Unified cloud runs now retain event bodies in their append-only journal and
keep only byte offsets resident. Final envelope hashing and atomic publication
stream canonical JSON. Tape format, canonical bytes, individual bodies, original
seals and pinned SQLite artifact hashes do not change. New tapes larger than
32 MiB replay through an index into the original file; native export, bundle
validation, trace summaries and artifact hashing no longer load full histories
or files into Python memory. The boundary-only replay validates one record at
a time. Only the requested native pointer and its exact dependencies are restored;
no other run's pointer is traversed. A sealed SQLite baseline is still restored
byte-for-byte: it is not silently trimmed or repinned to reduce its size.

The regression streams and seals more than 2 GiB of real canonical bytes through
the atomic publication writer into a counting SHA-256 sink. It measures traced
heap below 16 MiB without requiring a 2 GiB scratch file. Another test records,
seals and replays a real >50 MiB on-disk tape with traced recording heap below
20 MiB. Small exact JSON/seal parity, Unicode, truncated/trailing JSON refusal
and streaming trace-summary equivalence are covered separately.

These are offline proofs, not a claim that the historical Azure job succeeded.
Root integration must build one immutable image, run the new demo, confirm the
Azure execution Succeeded plus complete outer run-record seal, then replay that
new native capture on that identical image. Existing tapes remain untouched.
No dependency, image entrypoint, role, secret or budget configuration changes are
needed: `dia run` enables streaming automatically and restores its environment
on exit. Direct legacy recorders retain their existing in-memory event interface.

The daily smoke's Blob challenge previously attempted `captures` through the
CAS adapter, while its existing platform channel admitted only exact run-bound
outer records. `PLATFORM_CAS_NOT_ALLOWED` is a scope-routing finding, not a
reason to widen the grant. The unified smoke now stores the challenge as one
ordinary immutable outer record, GETs that exact record through the existing
runner channel, and verifies its retained SHA-256. Unknown or cross-run
references refuse. No CAS container declaration, role or identity is added.
