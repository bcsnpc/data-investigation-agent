# Round Nine mechanism-only supersessions

Recorded 2026-10-06 America/Chicago; provider timestamps are 2026-10-07 UTC.
Human decision: revise the eight rejected inferred-column mechanisms, at most
one retry per rejection, zero estate reads, preserve all structured fields and
original tapes. Exact acceptance-change reason:
`synthesis rules tightened per human review, #420`.

Eight accepted sentences required nine metered provider calls. A, D, G, H, I,
source-consistent and source-latency passed first call; E's first response
contained two `may` markers and its sole retry passed. No second rejection.
Actual usage: 49,717 input tokens, 5,387 output tokens, 55,104 total. Output
reservation was 72,000; cumulative model calls 88 -> 97, output reservations
314,000 -> 386,000. Estate physical/diagnostic reads: zero. No settings, pot,
ordinary allowance, reader scope, counter reset or refund. Estate pot remains
0/200 with 40 reserved; last usage snapshot ordinary rolling119/1500.

The E retry-feedback formatter initially raised TypeError after validation and
before sending the retry. That failed batch, E response, tape and ledger row
remain intact. The continuation skipped already accepted A/D and sent only E's
unused retry, then the remaining five cases. A regression prevents a second
rejection from being resumed as a third call. No accepted case was re-run.

## Immutable acceptance amendment

[Supersessions](../acceptance/model_steps/synthesis-revisions-420.json) retain
source tape/event hashes and original sentences marked superseded alongside
new responses and new provider-event hashes. The original
`synthesis-recorded.json`, its human-review paragraphs, grades, all original
investigation tapes and expected structured results are unchanged.

The provider emits only the new text. The application copies every other field
from the original response. Shared validation compares canonical UTF-8 bytes of
the entire response with only that text removed; future fields are included.
The gate also matches the original sealed full response, new tape seal, source
bootstrap link and actual provider body. A different tape never inherits a
sentence on the strength of the family name. Tests reject changed quantities,
citations, outcomes, future fields, wrong source events, absent private proof
and cross-column substitution.

The model-step gate now passes: effective synthesis14/14 versus preserved
original6/14 under the corrected checker. This is a mechanism supersession
score, not a clean first-attempt rate: one of nine new responses was rejected.
Original human grades remain 4/10 all flags, not grades of the new sentences.
The acceptance replay still executes the original pinned producers byte-exactly;
its current mechanism invariant separately grades the authorised superseding
sentence. Original rendered outputs remain historical, unchanged. This does
not claim a new current-engine investigation or new human readability approval.

## Additional archived findings

The archived column contains different tapes. Its current-rule audit rejects
seven different final paragraphs: A (hedge), B (non-role layer word), D
(non-role layer word), E (both), I (hedge), source-consistent (non-role layer
word), source-unreachable (non-role layer word). They were not included in the
eight-call-case authorisation, so no further provider call was made. A separate
human decision is requested for seven archived replacements, at most14 model
calls, under identical limits. The full thirty-case replay is in progress;
archived A/B/D/E already fail the tightened invariant. PR420 stays draft.
No threshold, checker, expected answer or baseline was relaxed to make it green.

## Private evidence delivery under section 8

The existing encrypted evidence-delivery authorisation is used for a new
immutable bundle: nine new tapes (including failed E and its retry), and both
batch result files including the operator failure. Eleven exact member hashes
are pinned in
[the delivery manifest](../acceptance/known_domain/private-mechanism-bundle.json).
All files, decoded events and provider bodies passed the credential scanner;
no estate credential is inside. Original private bundles are unchanged.
Only the existing recipient public key was used locally; the decryption key
remains solely in unchanged Actions secret `KNOWN_DOMAIN_REPLAY_KEY`.
No identity, reader audience or scope changed.

Release tag: `mechanism-revisions-420-e3d03e97a371015fadfdb99c9cab3c86022cfbb25f6c8e81e9cdcf4fbd5e2b29`.
Ciphertext SHA-256: `e3d03e97a371015fadfdb99c9cab3c86022cfbb25f6c8e81e9cdcf4fbd5e2b29`.
Only encrypted `mechanism-tapes.sealed` was published. Hosted download verifies
ciphertext before decryption, then every member hash, and removes temporary
private inputs. No raw tape or payload was committed or published.
Initial release creation returned HTTP422 for an abbreviated target SHA; no
release existed. Retrying with the full same commit ID succeeded without
changing tag, content or scope. No existing tag was overwritten.

## Verification and remaining work

29 focused tests pass, including original-grade provenance and hostile
supersession cases. Earlier test fixtures lacked a balanced provider request
(two errors), then aliased an original response (one assertion failure); these
were fixture defects and were corrected without weakening the validator.
Full regression and current thirty-case gate remain pending at this checkpoint.
General translation/runtime wiring, privacy capture contract, complete rebuild,
browser verification, discovery approval and the bounded estate verification
remain pending. Prior freezes remain invalid. No live estate run here.

Dated hosted follow-up: model-step-regression passed on d8ae849. Generator CI
failed because the two-column test double did not accept the new explicit
mechanism-root argument. The double now asserts it is forwarded for all30
cases;31 focused tests pass. The operator uses the consumer-owned claim bound
rather than a duplicated1000 literal. Failed CI runs37566469628/37566474060
remain visible. Current hosted full replay and stable regression are pending.
Published ciphertext was independently downloaded and its SHA-256 verified;
no local decryption or new secret was used.

Dated full-source proof: all eight new provider requests contain the exact
original sealed evidence spine, previous mechanism and approved reason. This
is now asserted by the hosted amendment checker as well as the local proof;
a different evidence context refuses even if the response text is valid.
31 focused tests pass. No new provider or estate request.

Local d8ae849 full discovery ran2208 tests in459.805s with8 errors: seven
tracing tests lacked opentelemetry in the invoked base interpreter, and one
used the already-corrected replay double. No failure was discarded. The stable
527abcd rerun uses the previously installed, pinned otlp-deps directory; no
package or system environment was changed. Latest527abcd generator, portal,
PowerShell and model-score hosted checks pass. Full current replay still
rejects seven archived paragraphs; no15x2 pass or draft promotion is claimed.

Dated stable regression result:527abcd passed2208 tests in447.851s with the
pinned tracing dependency directory. The stricter source-context proof on
67b6d61 passed31 focused tests and all8 actual sealed-source comparisons.
The earlier8-error run remains intact. Current15x2 remains unearned because
seven distinct archived paragraphs fail the tightened rules. No additional
model call while the bounded archived-revision decision is pending.

## Archived authorisation and execution ? 2026-10-07 America/Chicago

The human authorised the seven independently sealed archived paragraphs after
the preceding full replay scored archived8/15 and inferred15/15. A, B, D, E, I,
source-consistent and source-unreachable are now accepted after eight metered
model calls. A first emitted `may` and `could`; that response was rejected and
its sole retry passed. The other six passed first call. No second rejection.
Every new request uses its own exact archived evidence spine. Zero estate reads.

Actual tokens:41,601 input +4,524 output =46,125. Reservations:64,000 output.
Cumulative calls97 ->105, output reservations386,000 ->450,000; no refund or
reset. Across both authorised batches:17 calls,91,318 input +9,911 output
=101,229 tokens. Investigation cap12 and all estate allowances unchanged.
The rolling window naturally aged to7/1500 at the final usage snapshot; this
is not a counter reset. Round Nine estate pot remains0/200,40 reserved.

The archived extracts and supersession index are separate from the inferred
ones. Selection uses source tape hash, never a family or column name. Duplicate
source claims across indexes refuse. All seven complete response structures
are canonically byte-identical except `technical_output.text`. The original
paragraphs are retained as superseded in the index and unchanged in their tapes.
Original human grades are not transferred to these new sentences.

Section8 evidence delivery uses a new immutable encrypted bundle with19
exact members: the previous11 proof files unchanged plus seven new tapes and
the archived batch results. The prior release and its manifest remain retained.
Ciphertext SHA-256:`e46a5ce9c27389f1b8b8fb74251f498ecd6c4f72a8d18a547a23adc09776daaf`.
Release tag:`mechanism-revisions-420-e46a5ce9c27389f1b8b8fb74251f498ecd6c4f72a8d18a547a23adc09776daaf`.
Existing Actions secret `KNOWN_DOMAIN_REPLAY_KEY` unchanged; local encryption
uses only its public recipient key. All19 files, decoded events and provider
bodies scanned clean. No estate credential, reader scope or identity changed.

Eight source-selector/revision tests pass. The full regression and current
30-case replay are running. No15x2 or draft-promotion claim yet.
