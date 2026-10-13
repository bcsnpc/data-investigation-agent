# Native cloud form capture export

The cloud form worker now snapshots existing local capture IDs immediately before the normal form attempt. Its finally path writes `one-attempt/captures/index.json` and byte-identical `slim-recording.json` pointers for newly created captures. The existing stage package includes that directory. No SQLite file, token/cache, historical capture or sealed event is copied or rewritten.

Each new capture receives an explicit disposition: native pointer exported, missing tape, unsealed/invalid tape, sealed without publication pointer, or export invalid. A sealed tape without its pointer is not called published. Pointer bytes remain preserved even when their validation fails. No new captures is an explicit empty inventory, not a replay pass.

The exporter checks the tape envelope seal and event journal, plus the pointer's source seal and closed recording configuration. It deliberately does not claim full Tape validation: that requires the retired snapshots to be restored from CAS. CAS restoration and engine replay remain separate checks, labelled `NOT_RUN` in the exported index. The export performs no cloud reads and never reconstitutes a database.

An export failure is recorded separately and cannot mask a primary form/worker failure. After an otherwise successful attempt, an export failure propagates instead of being silently accepted.

This change is for subsequent images. The running e646 image and its evidence remain unchanged; its absent native exports may be recovered from immutable publication receipts, with that different provenance explicitly recorded.

Validation: 19 form/stage tests pass, including actual stage ZIP inclusion, exact pointer bytes, prior-capture exclusion, missing/unsealed/unpublished rows and primary-error retention. The additional slim-recording suite passed (24 tests before adding the stage ZIP integration test).
