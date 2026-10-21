# Offline retry inputs from a published parent

`python scripts/prepare_runner_retry_inputs.py --help` builds a new input ZIP from an original input ZIP and the eight exact, restored `prepared` CAS dependencies. The source ZIP and dependency manifest are hash-pinned. The real readonly ModelStore read must equal the retained model record, including its events and context history. Its retained discovery source must still exist. The derived ZIP copies the prepared catalog and inventory byte for byte; only its request key and owner/provenance record otherwise change. Originals are never opened for writing. The builder makes no network or model calls.

The CLI requires a local restored dependency folder. An operator may restore it with existing `Files.restore` through `restore_dependencies`; the operator owns that separately admitted platform access. This command never falls back to a stale catalog or rewrites historical runs.

The first Part C attempt published model revision 85 but exhausted its verification deadline before any diagnostic or physical request. The next input must therefore use that exact published parent, not revision 83 from the first ZIP. The new approval and context are still constructed inside the current worker image through the ordinary publication path.

## Deadline finding and proposed correction (not implemented here)

The handler currently computes the native verification deadline before the capture constructor audits and snapshots the full SQLite databases and before pre-read dependencies are retained. Those controls consumed the 900-second native-read window on the first attempt, which recorded `VERIFICATION_DEADLINE` with zero physical/diagnostic/model requests. Retention after that failure remained subject to the 1,800-second Azure job limit.

Keep the overall 1,800-second envelope anchored at runner entry. Start the native verification window only after pre-read capture and dependencies are durable; allow at most 900 seconds and clamp it to the remaining envelope after explicit demo and finalization reserves. If insufficient time remains for a bounded query and settlement, record timing unavailability and admit no query. Record the start with a tape clock event and derive its deadline deterministically. Do not alter a sealed bootstrap deadline or reinterpret old tapes. Settlement of an existing reservation remains possible after the read-admission deadline. This separates a diagnostic window from controls without increasing any cap. Implementation requires a separate reviewed change; this helper only prepares inputs.
