# Round Six ? gate and transformation reader

Dated 2026-10-05T02:12:49.230427-05:00 (America/Chicago). Unattended instructions from the human's
round-six-transformation-reader.md apply. No estate credential/reader scope
changed in section1. Original run/tape/database bytes preserved.

## Section1 report ? encrypted evidence delivery

The amended delivery condition permits tenant IDs and definition connection
strings; credentials remain forbidden. The original condition and finding remain
as-is below the dated amendment in docs/round-five-i-canonical-gate.md.

Credential scan: **60 files** (15 source runs,15 sealed tapes,30 pinned SQLite
databases), plus decoded non-clock tape events and decoded provider responses.
Counts: password=0; secret=0; token=0; sig=0; SharedAccessSignature=0;
BEGIN PRIVATE KEY=0; AccountKey=0; Azure/Fabric JWT-token shapes=0. Additional
JSON password/client-secret assignments and certificate-header scan:0.
This is a pattern-scan result, not a claim that arbitrary unseen encodings
cannot exist. No evidence was redacted or edited.

Bundle: the60 unchanged files and one separate path-relocation map, so sealed
source and bootstrap hashes survive hosted filesystem relocation.
Tape-set SHA-256: `1b6d344c8072d8a9e47e4957efeac7ffd6f9e4ed4f3afa500562e41562224174`.
Ciphertext SHA-256: `fb7ac3ef8812c43230641bf90ce77c0f40b79ba9e127b15a8b9f9da883d530f4`.
Compressed plaintext SHA-256: `9094bbb09f37fda1b40e7d5c1416cb7f21192b7c1561a4488adfe5d31e0aa42b`.
Encrypted asset bytes: 245953822.
Release tag: `known-domain-tapes-1b6d344c8072d8a9e47e4957efeac7ffd6f9e4ed4f3afa500562e41562224174`.
Release asset: `fixture-tapes.aesgcm`.
Actions secret: `KNOWN_DOMAIN_REPLAY_KEY`.

CLAUDE.md section8 human decision: immutable authenticated-encrypted GitHub
release delivery and the Actions secret were explicitly approved and then
amended to allow identifiers/definition strings. Before secret listing:`[]`.
After:`[{"name":"KNOWN_DOMAIN_REPLAY_KEY"}]`. The key was generated in memory,
passed to the approved secret through stdin, and never stored in a local file,
repo, release or report. Release API digest matches the committed ciphertext
hash. No estate credential or reader scope changed.

The hosted check verifies the downloaded ciphertext hash **before** decrypting
AES-256-GCM; a wrong hash or key refuses. It extracts only safe regular-file
members outside the checkout, replays all15 network-blocked, then removes the
decrypted inputs/results. No raw artifacts are committed or published. A new
bundle requires a new tape-set tag and a reasoned PR updating the hash; no
overwrite of an existing release asset was used. Four delivery tests pass,
including hash rejection before decryption, wrong-key rejection, safe extraction,
path-traversal refusal and separate path mapping without editing source files.

**Hosted15/15 and #376 merge are pending actual CI execution.** No local pass
is substituted for the hosted column. The final main merge-commit check will
be quoted here after it actually runs.

Dated hosted attempt, 2026-10-05: run37276485968 authenticated and decrypted
the immutable bundle successfully, then passed family C and blocked the other
14 at `TAPE_EVENT_DIFFERS:CLOCK:WORKER_SEND`. No estate requests occurred.
The archived native worker normalizes the configured executable with
`Path(v).name`: the recorded Windows path ends in `python.exe` under Windows,
but its entire backslash-separated path is the basename under Linux. The
sealed descriptor is `python`; Linux therefore differs before the worker send.
The archived replay's subsequent cleanup clock masks that earlier descriptor
difference. Original failed hosted column remains in the Actions log.
The hosted runner is now Windows, preserving archived producer path semantics;
no tape, expectation, event matching or encrypted asset was changed. The four
private-delivery tests still pass.

Section1 estate windows: pot **0/400 before,0/400 after**,60 reserved.
Rolling **386/1500** at the section closing read. GitHub release/secret/CI
controls are outside estate requests; no estate/model calls initiated.

## DECIDED WITHOUT REVIEW

- Added the gate on main pushes as well as PRs, so the human's requested hosted
  column can come from the actual merge commit. PR-only execution was rejected
  because its synthetic merge head is not the final main commit.
- Used a separate authenticated path map for the archived Windows paths. Editing
  the source JSON was rejected because it would invalidate the sealed historical
  source-hash associations.
- Kept ordinary prose/physical matching unchanged; private delivery does not
  weaken any refusal or create a replacement investigation.
- Run archived Windows producers on Windows. Rewriting their descriptors or
  accepting different physical requests was rejected because replay must retain
  the producer's original behavior and the sealed transport contract.

## Reader design/offline report

Pending. No reader capability, live binding or two-column acceptance claimed.

## Live reader report

Not started.

## Final report

Pending the remaining sections and stop rules. Prior freezes remain invalid.
