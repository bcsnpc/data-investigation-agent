# Round Six ? gate and transformation reader

Dated 2026-10-05T02:12:49.230427-05:00 (America/Chicago). Unattended instructions from the human's
round-six-transformation-reader.md apply. No estate credential/reader scope
changed in section1. Original run/tape/database bytes preserved.

## Section1 report — encrypted evidence delivery

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

**#376 merged; the actual main merge commit passed hosted15/15.**
Merge commit: `f4378dfeac79b74a3d2a5616b3a852336ae64df5`.
PR check: [37277755751](https://github.com/bcsnpc/data-investigation-agent/actions/runs/37277755751).
Actual main-commit check: [37278367358](https://github.com/bcsnpc/data-investigation-agent/actions/runs/37278367358),
completed 2026-10-05T07:38:52Z. All six ordinary PR checks also passed.
The following column is parsed from that main-commit hosted log, not a local run.

| Ticket | Hosted main column | Walk outcome | Reproduction |
| --- | --- | --- | --- |
| family-A | PASSED | TRANSFORMATION_LOGIC | — |
| family-B | PASSED | NO_KNOWN_PATTERN | — |
| family-C | PASSED | INSUFFICIENT_EVIDENCE | — |
| family-D | PASSED | NO_COMPARABLE_PATH | — |
| family-E | PASSED | TRANSFORMATION_LOGIC | — |
| family-F | PASSED | CONSISTENT_TO_BOUNDARY | — |
| family-G | PASSED | TRANSFORMATION_LOGIC | — |
| family-H | PASSED | NO_KNOWN_PATTERN | — |
| family-I | PASSED | TRANSFORMATION_LOGIC | — |
| reproduction-16 | PASSED | NO_COMPARABLE_PATH | REPRODUCED 16 |
| reproduction-empty | PASSED | NO_COMPARABLE_PATH | REPRODUCED EMPTY |
| source-consistent | PASSED | CONSISTENT_TO_SOURCE | — |
| source-gap | PASSED | INGESTION_GAP | — |
| source-latency | PASSED | LOAD_LATENCY | — |
| source-unreachable | PASSED | CONSISTENT_TO_BOUNDARY | — |

Every case recorded zero network calls and zero physical requests. These are
pinned historical producer replays, not current-engine requalification.


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

The next hosted attempt37277589967 stopped before replay because a delivery
test compared the loader's resolved long Windows temp path to its unresolved
8.3 alias. The test now compares resolved paths on both sides; path-escape
rejection and original source preservation remain tested. That failure remains
in the ledger and Actions log. Subsequent PR and actual-main checks passed.

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

2026-10-05 America/Chicago. **Blocked under section0's authorization rule.**
The specified reader fetch through the item-definition API requires write
permission, which this round explicitly forbids. Microsoft Learn states:

> The caller must have read and write permissions for the notebook.

See [Notebook Get Definition](https://learn.microsoft.com/en-us/rest/api/fabric/notebook/items/get-notebook-definition).
[Generic Item Get Definition](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-item-definition)
has the same item permission requirement, and
[Data Pipeline Get Definition](https://learn.microsoft.com/en-us/rest/api/fabric/datapipeline/items/get-data-pipeline-definition)
also requires read and write. Choosing the generic endpoint does not remove it.
The delegated ReadWrite scope and the item's own permission are distinct checks;
a read grant does not meet the documented item requirement.

This is a **documented route constraint**, not an observed reader HTTP403.
No reader definition probe, permission listing, grant, new audience, identity
change or credential was attempted. The pre-approved read-only grant was not
applied because it would not satisfy this route. No publisher definition was
relabeled as reader evidence. Under the prompt's stop-that-section rule the
reader implementation and dependent live section were stopped. No new
ProposedBinding schema, verifier, model fallback, approval gate or ledger is
claimed; the existing design remains design only. No synthetic test results
are invented for an unimplemented capability.

The starting-state audit also found two independent discrepancies with the
prompt: `estate_manifest.py` currently offers `inference.enabled` and
`inference.code_resources`, but no per-boundary `may_infer_from_code` or code
locations; both committed fixture and Databricks manifests have inference
disabled with empty code resources. The fixture has only the application-to-
landing configured lineage binding; its original notebook chain is currently
derived from retained definitions in `adapters/declared_chain.py`. A future
implementation must extend the closed contract explicitly and distinguish
that legacy retained-definition path from reader-fetched, verified inference.
Nothing was silently inserted into either manifest.

Verifier design issue retained: agreement between a *transformed* source
expression and its target can qualify that binding only for the tested
quantity/context/precision. It must not replace the investigation's independent
input-versus-output comparison, which locates the transformation difference.
Aggregate agreement alone cannot establish equal memberships, intended grain
or aligned snapshots. No verification rule has been implemented tonight.

Section2 windows: pot **0/400 before,0/400 after**,60 reserved; rolling allowance
**1500 unchanged**,386 last observed at section1. Zero estate/provider requests.

## Live reader report

**Not run**, because reader-fetched notebook definitions are a precondition
of the lineage-stripped experiment. No alternative identity or cached publisher
definition was substituted. No binding verdict, inferred-lineage ticket, source
control run, fixture mutation or new tape exists for this section. The second
acceptance column is **NOT RUN**, not15/15. The first column remains historical
pinned-producer replay and must not be described as current-engine inference
acceptance. Pot0/400 before/after; no restoration was needed.

## Section4 independent documentation

Recorded the documented definition-read authorization constraint separately
from tested platform findings. Existing SQL endpoint audit lag of at least
6m20.259836s and the serverless Free Limit AutoPause constraint remain recorded
with their original receipts in CLAUDE.md. The prompt's "workspace monitoring
never enabled" is contradicted by the preserved human confirmation that
Workspace settings Monitoring was ON and the native Monitoring artifact/database
listing. Empty monitoring queries do not prove monitoring was disabled. That
history was preserved; no contrary assertion or new monitoring probe was made.
Optional allow-list shrink and ticket-history implementation were not attempted.

## Final report

The section1 main-commit hosted column above passed all fifteen cases.
Sections2–3 stopped at the documented permission constraint; no permission was
expanded. No new engine acceptance, freeze or unfamiliar-domain claim. Original
evidence and failed hosted attempts remain unchanged. Prior freezes remain invalid.

## DECIDED WITHOUT REVIEW — blocked reader

- Applied section0's stop-that-section rule to the definition-read requirement.
  Granting write was explicitly forbidden. Building a disconnected reader and
  substituting publisher-retained definitions to obtain the live result was
  rejected because it would not meet the required evidence identity.
- Did not spend exploratory reader requests before the required offline
  implementation/testing stage or pretend the published permission requirement
  was an observed refusal. No unauthorized grant was attempted.
- Preserved the documented monitoring ON finding instead of copying the
  prompt's contradictory "never enabled" statement into known limits.

Final windows, 2026-10-05 America/Chicago: RoundSix **0/400**,60 reserved,
ordinary-work stop340; rolling **386/1500**,1114 available. No allowance,
manifest configuration, counter, fixture, grant or estate identity changed.
