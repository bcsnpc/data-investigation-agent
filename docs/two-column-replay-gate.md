# Two-column replay delivery

Round Seven, 2026-10-05 America/Chicago. The archived fifteen-tape gate remains
unchanged and continues to use its original immutable AES-GCM release. A second
immutable bundle will carry the fifteen inferred-lineage runs, their pinned
databases and the exact manifests already sealed by those tapes. Expectations
are shared; every answer remains subject to the existing output gate. No hosted
two-column pass is claimed until both actually replay from the merge commit.

## DECIDED WITHOUT REVIEW

Reuse the existing `KNOWN_DOMAIN_REPLAY_KEY` without changing its value or creating
another secret. A domain-separated HKDF recipient key is derived only inside
Actions. Only its public encryption key is emitted. Local publication uses the
standard [PyNaCl sealed-box API](https://pynacl.readthedocs.io/en/latest/public/#nacl-public-sealedbox)
to encrypt to that public key; the ephemeral sender private key is discarded by
the library. The existing secret and derived recipient private key never leave
Actions. This avoids rotating away the only decryption key for the original
release, or introducing a new secret forbidden by the unattended rules.

The original `DIA1` decryption remains supported. New `DIA2` ciphertext authenticates
its format inside the sealed box. Its ciphertext hash is checked before decryption;
the pinned member inventory is checked before extraction. All paths must remain
inside the output directory. Wrong-key, ciphertext-hash, member-hash and legacy
format tests run before replay. Delivery hashes and the release tag will be
recorded after the immutable second bundle has been published. Only encrypted
evidence is published; no estate credential or reader scope changes.

The measured fifteen inferred tapes plus their databases exceed the original
three-billion-byte extraction ceiling (3,044,552,001 bytes before source-run
files and manifest pointers). The delivery-only extraction ceiling is four
billion bytes, with an exact pinned member inventory for the new bundle.
Original evidence is neither compacted nor rewritten to fit the old ceiling.
This bounds runner disk work, not estate requests; all investigation and
physical-request budgets remain unchanged.

The dependency is pinned to PyNaCl 1.6.2, whose
[maintainer changelog](https://pypi.org/project/PyNaCl/#changelog) records the
updated libsodium security fix. Current engine code and live-run producer
revisions are untouched by this delivery change. Previous freezes remain invalid.

## Immutable publication, 2026-10-05 America/Chicago

The inferred bundle contains 64 unchanged inputs: 15 source-run records, 15
sealed tapes, 30 pinned fixture databases, three sealed estate manifests and
one separate relocation map. All nine credential-pattern counts are zero,
including decoded provider bodies. This is a pattern-scan result, not a proof
about arbitrary encodings. Fixture rows, definitions and audit records are
retained; no estate credential is inside the scanned material. The previously
approved identifiers and definition connection strings are not credentials.

Tape-set SHA-256: `d918f8417c90ddde27cf300862c890c3e6a1b2cf2e89ad752b73ac97589c8d7e`.
Ciphertext SHA-256: `a22a2ead23d4ae2b40b899acc1191b66c2a67c5b1f795bdae302363b6bbc64c7`.
Compressed plaintext SHA-256: `073b4bef2a0eabf1d3a27d8e82fa923aa8f1c27aceb4fb0d2ca375183d289318`.
Release tag: `known-domain-inferred-tapes-d918f8417c90ddde27cf300862c890c3e6a1b2cf2e89ad752b73ac97589c8d7e`.
Asset: `inferred-tapes.sealed`, 324,526,458 bytes.
The exact 64-member inventory is committed in
`acceptance/known_domain/private-inferred-bundle.json`.

Section 8 delivery record: this applies the human's immutable encrypted-evidence
delivery approval using the existing `KNOWN_DOMAIN_REPLAY_KEY`. Before and after
secret listings show only that secret, last updated 2026-10-05T07:08:58Z; its
value was not changed, read locally or exported. Only a public encryption key
was exported by Actions run 37413002231, SHA-256
`f58f954e9623fe0a0d0c6839acc944a9f7bf6b4fddcefb718031fc97e4e97d63`.
No estate credential, identity or reader scope changed. No raw evidence was
published. A new bundle requires a new immutable tag and a reasoned hash change
in a PR; this release was not overwritten.

The first publication request failed with HTTP 422:
`Release.target_commitish is invalid`, because local merge commit 2f2051f had
not been pushed. No asset was published by that attempt. The same ciphertext
was then published against the already-pushed evidence commit 78218b2; the
release API's asset digest matches the pinned ciphertext hash. This is a
delivery-control failure, not a replacement investigation.

Both columns replay sealed producer revisions and grade with current output
contracts. This gate protects recorded answers and their evidence contracts;
it is not a replay of every historical request through today's planner. A changed
expected answer requires a new `acceptance_change_reason` in the same PR.
Each column conserves all fifteen cases and refuses missing inputs. The hosted
thirty-answer pass remains pending at this publication checkpoint.
