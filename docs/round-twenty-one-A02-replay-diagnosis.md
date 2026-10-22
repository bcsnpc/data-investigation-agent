# A02 same-image replay input failure

Offline diagnosis, 2026-10-22. Original source: `89785fca577c1f0740a7eb9bebce7d9feb3bf2f6`. Original tapes and expectations are unchanged.

A02 capture 2 failed `TAPE_EVENT_DIFFERS:CLOCK:BOUNDED_REQUEST`; captures 1 and 3 matched. The first error was an omitted replay input, not a clock comparison policy problem. Capture 2 reaches the Bronze reader: `MicrosoftProcessAdapter.evaluate` calls `AdaptiveRuntime.read_endpoint`, then `retained_endpoints.read` reads the sealed `/inputs/endpoints.json` path. That file was absent from the replay ZIP. `FileNotFoundError` was followed by the stage-finalization clock, which encountered the next bounded catalog request at zero-based event index 363 (ordinal 364). Captures 1 and 3 did not reach that reader.

The required endpoint receipt is 3,109 bytes, SHA-256 `b2705269319477d4e7f52e0ce307d531135af28524218f4ff56decb7b380ccd3`. Identical bytes are retained in the original Part 0 A sealing input ZIPs 01 and 02 at `endpoints.json`, `prepared/endpoints.json`, and `capture/endpoints.json`. A repaired input ZIP must include the root `endpoints.json`, materialized at `/inputs/endpoints.json`. The replay options and original image stay unchanged. The failed replay stays failed; any subsequent replay with complete inputs is a separate result.

The sealed configuration has no other external `/inputs` file. Its `/work/one-attempt/inventory.sqlite` is the already-restored replay inventory. Notebook code-location paths are logical retained-source references, not a reason to add live files or make network reads.

The generic fix validates declared endpoint input presence and its sealed hash before any replay operation. First-error diagnostics now also observe direct `Tape.take` calls, including clocks and identities, while retaining their original exception context. No event is ignored, consumed early, reordered, normalized or rewritten. Missing or changed input still refuses. The focused endpoint, replay-materialization and worker-replay tests pass (22 tests).

A02 replay result,2026-10-22: original inputs2/3matched; capture2 failed because its ZIP omitted the pinned endpoint file. New immutable input ZIP adds only the identical3109-byte endpoint SHA b2705269319477d4e7f52e0ce307d531135af28524218f4ff56decb7b380ccd3. Same original image/source89785fc replay of capture2 nowMATCHED, zero network; original tape unchanged. Corrected complete-input coverage3/3 is distinct from original2/3. See docs/runs/round-twenty-one-A02-replay-input-repair.json.
