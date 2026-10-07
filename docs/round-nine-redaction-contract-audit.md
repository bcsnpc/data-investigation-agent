# Redaction capture and replay contract audit

Recorded 2026-10-06 America/Chicago. Synthetic material only; zero provider or
estate requests. Existing evidence was not changed. This records unfinished
work, not a delivered redaction control.

The requested guarantee covers every output and every tape, rather than just
rendered explanations. Current capture precedes those explanations:

| Boundary | Existing behavior | Consequence for a declared sensitive key |
| --- | --- | --- |
| `Tape.__init__` / BOOTSTRAP | Serializes full configuration and state | A ticket or context payload can retain the value before any read |
| BOUNDED_REQUEST and WORKER_SEND | Retains the original diagnostic request | A key can appear inside the predicate, not only in a result column |
| BOUNDED_RESPONSE and WORKER_READ | Retains the original response | Hashing a later receipt leaves the raw value in the tape |
| PROVIDER_REQUEST / RESPONSE | Nested JSON and base64 HTTP bodies are retained | Final-output masking does not cover model payloads or responses |
| FINAL | Retains results and outputs | Every earlier leak remains even if FINAL is masked |

A temporary synthetic tape with `person_name=ROUND_NINE_SYNTHETIC_PERSON`
retained that value in BOOTSTRAP, BOUNDED_REQUEST, BOUNDED_RESPONSE and FINAL.
Replacing the request's value with a hash under the current replay contract
refused with exactly `TAPE_REQUEST_BYTES_DIFFER`. The temporary tape was removed;
the audit result and ledger entry are retained. No actual person data was used.

The relevant code is [process_tape.py](../scripts/investigator/process_tape.py)
(`Tape.event`, `take`, `bounded_call`) and
[provider_tape_contract.py](../scripts/investigator/provider_tape_contract.py)
(canonical provider-body comparison, including its nested body encoding).
Secret detection does not constitute column-value redaction. Base64 is encoding,
not concealment. Encryption is not the requested substitution either.

Implementing an output-only replacement or rewriting sealed historical tapes
would fail the requirement. A correct implementation needs a distinct capture
contract for installations that declare sensitive columns:

1. Exact column identities, typed hashing and explicit policy provenance. No
   basename guessing, inferred sensitive-column list, new secret or grant.
2. A typed projection before durable capture, with sensitive query/selection
   values covered as well as returned grouping keys. Parsing failures refuse
   capture rather than leaking an opaque body.
3. Consistent opaque identities across receipts, addresses and outputs. Preserve
   null/zero/empty distinctions, equality, grouping cardinality and attestation;
   do not change a predicate or replace an aggregate with a plausible value.
4. Original-request content hashes and clearly labelled projected response
   bodies. A projected replay must never claim it replayed the original raw
   response bytes. Original versions remain immutable and supported.
5. Coverage of bootstrap, workers, bounded routes, nested provider bodies,
   failures, final outputs, sidecars and pinned context artifacts; a raw tape
   plus a masked export is insufficient.

The remaining contract decision is whether redacted installations may use a
new explicitly labelled privacy-projected replay format, or must fail closed
as non-replayable where projection changes a sealed input identity. Both choices
must keep the original raw-body contract for existing tapes. Until that choice
is resolved and the full path is tested, the manifest does not advertise this
control and the fixture continues to declare no redacted columns.

## Dated contract decision and codec checkpoint, 2026-10-07

The human approved a separate privacy-projected class: projection at capture,
no raw durable or transient files, an estate-keyed secret-store key, exact replay
after projection under the same key, one class per estate declared in the
manifest, and a tape-class field in grading. Existing unredacted gate tapes stay
exact. Changing the sensitive-column list requires re-recording; old tapes cannot
be re-projected. This supersedes the pending decision above, not the earlier audit.

The new codec uses HMAC-SHA256 with an estate domain and typed string values.
Its descriptor carries policy, policy hash and a keyed key-binding assertion,
never the key or an unkeyed hash of a sensitive value. A keyed seal prevents a
modified capture from passing as an authentic projected tape. It decodes nested
JSON and base64 JSON before projection. Null, zero and unrelated empty strings
remain distinct. Unsupported sensitive numeric types and opaque non-JSON bodies
refuse; no numeral guessing or string-column basename guessing occurs.

The separate capture packet invokes projection at each event and keeps its
projected events in memory until sealing; no raw journal or scratch file is
written. A final pass also removes values that later typed evidence identifies
from earlier prose. Sealed outputs are returned projected. A synthetic person
column records and replays under the same in-memory test secret; the raw name
appears in no file, decoded event, nested provider body or returned output.
Eighteen focused tests pass. Recording declarations do not enter the model
payload: directory entries2/2, SQL entries1/1 and payload characters7563/7563.

This is **codec groundwork, not a delivered installation privacy guarantee**.
The existing recorder also backs up catalog/inventory databases, and runtime
stores and planner sidecars persist independently. Those paths do not yet use
this typed boundary. Projected installations therefore refuse before execution,
legacy capture or raw artifact backup. An unlabelled value cannot be safely
identified as belonging to a sensitive column; native result aliases need exact
resolved-column provenance. This remaining wiring must cover those producers,
all sidecars, pinned artifacts and output persistence before this control is
advertised as usable. Memory-only unfinished packets also need an explicit
interruption record without leaking unidentified values; no failure-preservation
guarantee is claimed for a process killed before sealing.

Fixture and example manifests now explicitly declare EXACT. Their hashes change,
so existing current approvals must not be reused for new live work. No approval
was rewritten, secret created/read, identity changed, model called or estate
request made. Old exact v1-v4 tapes and recorded manifests remain unchanged.
Legacy manifest omission is supported only as the existing exact class.

Dated regression correction: the committed2326fb8 full suite ran2226 tests
and returned6errors, all context-pin refusal tests. The new guard accessed
configuration before the existing pin invariant rejected a mismatched handle.
The invariant now runs first; privacy refusal still precedes raw backup or
capture.5 context-pin tests and18 privacy tests pass after that correction.
Unresolved tabular headers, duplicate identities and unaccounted row fields
also refuse before capture; none are silently skipped. The original failed
log is retained. Corrected64ca314 passed2227 tests in742.483s. The Windows
secret-store resolver is adapter-owned; the neutral projector accepts a secret
store callback. Its PowerShell transport is included in the engine fingerprint,
so a transport-only change cannot preserve an old freeze identity. Final path/
fingerprint coverage has focused verification; it does not make installation
capture complete.
