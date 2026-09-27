# Engine fingerprint covers adapters and transports

Updated 2026-09-27.

## The defect

`runtime.fingerprint()` hashed only `scripts/investigator/*.py` plus a fixed list
of scripts. It missed two groups of files:
- **Adapters:** everything in `scripts/investigator/adapters/`, including
  `microsoft_process.py`.
- **Newer transports:** `fabric_sql_auth.py`, `fabric_sql_surface.py`,
  `read_xmla_failure.py`, `read_onelake_commit.py` and their PowerShell scripts.

An adapter-only or transport-only change therefore left the engine tag
unchanged. A freeze would have certified a run as unchanged while the behaviour
that produced it had changed. This was found in #250: the adapter bug fix there
did not move the tag.

## The fix

- **Coverage:** `fingerprint()` now hashes every `.py` file under
  `scripts/investigator/`, recursively (adapters included, `__pycache__`
  excluded). It also hashes every transport listed in `FINGERPRINT_TRANSPORTS`,
  which adds the newer transports and scripts named above.
- **Portable paths:** paths are hashed in POSIX form, so the tag no longer
  depends on the operating system's path separator.
- **Tests:** they fail if the adapters are not covered, if an adapter-only or
  transport-only change leaves the tag unchanged, or if a listed transport is
  missing.

## Invalidated fingerprints

**Every existing fingerprint is invalidated.** The covered file set and the path
form both changed, so no tag computed before this change is comparable with one
computed after it, even on identical code. This covers:
- **The ledger:** all 30 distinct `unfrozen-*` engine tags recorded in
  `docs/runs/ledger.jsonl`. The most recent are `unfrozen-a909b4d9785e`, `unfrozen-789b25653c0c`, `unfrozen-0769954a7c49`, `unfrozen-a841e4860b0a`, `unfrozen-e3b2724a5c50`, `unfrozen-53545e76a35e`. Their ledger rows are
  unchanged; they describe the old algorithm.
- **Stored hashes:** every `engine_hash` stored in session state and in planner
  recordings. Replay of any existing recording now fails closed with
  `ENGINE_VERSION_MISMATCH` unless drift is explicitly allowed.
- **No freeze:** none is currently claimed, so none is revoked.

## New fingerprint

On `main` at `bb5be32`, with this change, the fingerprint is
`a9e32c8192401ba23c353a9c5955312142b8e70725bd832861ce69060a373830`, tag
**`unfrozen-a9e32c819240`**. The same code under the old algorithm gave
`unfrozen-d4e6977a453b`.
