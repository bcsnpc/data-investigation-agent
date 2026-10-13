# Opt-in slim recording

Default recording is unchanged. To publish **new exact tapes** through the
platform Blob adapter, set `DIA_SLIM_RECORDING_CONFIG` to a private configuration
file containing only public platform coordinates:

```json
{
  "version": "slim-recording-v1",
  "account_url": "https://<platform-account>.blob.core.windows.net",
  "identity": {
    "mode": "managed_identity",
    "client_id": "<worker-client-uuid>",
    "tenant_id": "<tenant-uuid>",
    "principal_id": "<worker-principal-uuid>"
  },
  "snapshot_channel": "worker-snapshots",
  "tape_channel": "worker-tapes",
  "tape_class": "EXACT"
}
```

The schema is closed, the account must be an HTTPS Azure Blob endpoint, and
identity IDs must be canonical UUIDs. No secret, CLI fallback or implicit storage
account is accepted. The platform gateway must separately allow the exact Blob
URLs/methods for these channels. The explicit MI token's audience, tenant and
principal binding are checked. This is an operator storage switch, not a second
estate schema or an agent-selectable tool. The selected configuration is pinned
in memory when the new capture directory is created and recorded with its
published pointer; changing the environment mid-run cannot redirect that tape.

For a newly completed recording, `run_recording`:

1. Seals the original tape and retains its original event bytes.
2. Takes private final SQLite snapshots of the written catalog and inventory;
   shared accounting is materialized into the private snapshot as before.
3. Publishes initial/final snapshots and unchanged event/tape files to the
   existing content-addressed `snapshots` store. The `tapes` store receives the
   immutable envelope containing those references and the final-state references.
4. Downloads/restores every original and final reference, verifies hashes and
   the source tape seal, then verifies the published envelope itself.
5. Writes a durable `slim-recording.json` pointer, then retires only the four
   newly owned private SQLite copies. Each individual file is checked for the
   exact directory, ordinary single-link file status, expected size and hash.
   Every retirement is appended to `slim-retirements.jsonl`.

The running store, shared catalog and shared ledgers are never deletion targets.
Historical recordings are not marked as newly owned merely by enabling the
switch. Publication/verification failure preserves the private databases and
does not claim successful retirement. Incomplete uploads may exist remotely;
they do not authorize deletion. Interrupted publication requires operator
inspection rather than an overwrite retry. Native `tape.json`, event files and
the small local bundle/pointer remain for provenance; full duplicate databases
do not remain after successful publication. SQLite remains job-local execution
and replay scratch, not the permanent snapshot storage format.

`acceptance/unknown_domain/process_replay.replay` accepts the retained tape path
or its `slim-recording.json`. It materializes the referenced starting state in
temporary scratch, verifies the unchanged original seal, then invokes the same
engine replay path. Hydration requires platform artifact access; the engine
replay itself blocks estate/model networking. Offline CI can supply the same
CAS API backed by pre-fetched `LocalObjects`. The recorder's receipt deliberately
says `engine_replay: NOT_RUN`: publication proves restoration, not behavior.

The focused end-to-end test runs the existing process engine's intake, preview,
create, run and synthesis with synthetic provider/transport responses. After
private snapshot retirement, replay from the CAS reconstructs all five
operations, session result, classification and both outputs byte-exactly. It
also checks the existing engine-drift refusal. This proves the wiring on
synthetic evidence, not that a live cloud recording has completed.

**Privacy-projected slim recording is unsupported and fails before an exact
backup.** It must be implemented through the atomic projected installation
capture adapter; raw legacy snapshots are never relabelled projected. This
switch does not change any existing exact or projected tape contract.
