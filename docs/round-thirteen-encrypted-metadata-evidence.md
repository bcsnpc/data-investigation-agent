# Round Thirteen billing metadata encrypted evidence

Dated section 8 evidence-location record: 2026-10-10 America/Chicago / 2026-10-11 UTC. Chaitu's explicit human decision, "Approve encrypted identifier/route evidence", authorizes encrypted, hash-pinned fixture evidence at immutable release assets. Root reviewed this exact metadata-only roster and authorized publication.

Published eight DIA2 assets at [the immutable release](https://github.com/bcsnpc/data-investigation-agent/releases/tag/round13-billing-014940-74f6d44b-v1). Tag `round13-billing-014940-74f6d44b-v1` targets native producer `bf7c8b6d360abbc8af4e326619fc27eebf2bdbad`. Fresh release and Git-tag checks returned absence before creation. Creation returned native exit 0; after-listing contains exactly the eight approved names. All eight server-side SHA-256 digests and sizes match the approved ciphertext pins; every asset reports uploaded. No overwrite or replacement occurred.

Contents: billing014940's sealed native metadata tape/event sidecar, its original capture and V1 replay helpers, pinned before/after catalog databases, after-inventory database, and native collection receipt. Identifier and credential-free route evidence is retained. Full decoded-file/SQLite-cell and additive schema credential scans passed; no credentials are included. No plaintext archive was written to disk. Existing recipient decoded public-key SHA-256 `f58f954e9623fe0a0d0c6839acc944a9f7bf6b4fddcefb718031fc97e4e97d63` and existing Actions secret `KNOWN_DOMAIN_REPLAY_KEY` are used. The secret was not retrieved, changed or recreated. No estate credential, reader identity or reader scope changed.

| Asset | Ciphertext bytes | Ciphertext SHA-256 |
|---|---:|---|
| billing-014940-shard-01.dia2 | 21033809 | `75bdfe1982459a1ffcde0233c5c10c999a229361778ea5c6e497e95c7fbdb827` |
| billing-014940-shard-02.dia2 | 20979142 | `3b265d54d918a026012d2cbb9c4caa86352093dfacc35f6cfcb4f25810917878` |
| billing-014940-shard-03.dia2 | 24553 | `d83266694873f8c87d99dc3a6c0b6a76b9a481a240164c40ff690de957b1bd83` |
| billing-014940-shard-04.dia2 | 3319 | `498542d8754d1c41d303d81f2b4b4f84955e28cc69c8985800f45b507756d6b1` |
| billing-014940-shard-05.dia2 | 1717 | `67776dc4c0b8e56e280248e05f22111bdf8024d6340f3cc3feec9de6abe694b9` |
| billing-014940-shard-06.dia2 | 139779 | `67a60f573ed79058171c52dc821cf624ea68f1cb785893da5ec477e6b56ea8c0` |
| billing-014940-shard-07.dia2 | 139947 | `3c09233e570df58a18176957d35c8083d1c0af3f7593a855d2ee5235e783258f` |
| billing-014940-shard-08.dia2 | 36466 | `bac25db6fa4cbc1df11d9023b792f9bb7d4f4cbfc3d64b2b9638abe3f1007dd1` |

Total ciphertext: 42,358,732 bytes. Original sealed member bytes and hashes are unchanged.

The original V1 replay remains blocked at `TAPE_EVENT_DIFFERS:CLOCK:AUTH_STATE`. Separately pinned V2 reproduces exact archived Collector/Discovery, SQL compiler/worker protocol, recorded decoded JSON file-result, native context and 28 physical admissions (22 logical calls). Its claim excludes the unsealed private caller cap, four pre-tape authentication controls, and unretained native temporary-file bytes. This metadata publication does not establish any billing investigation result or a runnable whole-round replay.

Control receipt SHA-256: `4cf96acb7a08a8d7850db0167eba8a859006493e4da0efa6a6d75f20b30dc551`. Encryption receipt SHA-256: `e15857c82837265bcc9438d065eaa6eb4cc9b04b906ae908b07f77a821779f23`. Proposed asset manifest SHA-256: `fe767102174388da12ef6c6ee021d7d65df61e91de188a271fed6e2301ab79f5`. Cell-security receipt: `74f6d44be5bcf92d01211e00fb4acc27f4c9ec93ab9d6bab9f69f54d8d92c0fa`; schema-security receipt: `1cd67876d03bbade6697413ad62244d3d15f2db76b43d868155d14ddf5c1ca8c`.
