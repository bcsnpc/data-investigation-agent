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

The dependency is pinned to PyNaCl 1.6.2, whose
[maintainer changelog](https://pypi.org/project/PyNaCl/#changelog) records the
updated libsodium security fix. Current engine code and live-run producer
revisions are untouched by this delivery change. Previous freezes remain invalid.
