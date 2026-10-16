# Round Sixteen C: offline replay

The nine original captures are conserved: **six MATCHED, three MISMATCH**. All nine tape SHA-256 values still equal their initial capture records. No original tape, bootstrap database, expectation or source archive was rewritten. Diagnostic and corrected replays used isolated in-memory copies of the sealed catalogs; shared live budget stores were denied, network blocked, and no model or estate calls were made.

Two independent defects were found. The three submit captures emitted the same facts in caller dictionary order. Tape JSON canonicalization sorted request keys, so replay reordered their fact arrays and interpretation fact IDs. This is a true historical replay mismatch, not an altered fact value. The prospective shared submission fix iterates keys canonically; all 24 field permutations yield identical fact bytes, and a full submit/confirmation replay passes after canonical request decoding (34 intake/tape tests).

All three run captures first failed because the acceptance replayer omitted the direct claim execution outputs from its FINAL envelope, while the recorder retained them correctly. The acceptance-only correction conserves that prose pair, matching the recorder. Replaying those exact original captures under the exact archived engine with the corrected acceptance consumer genuinely MATCHED, with no engine drift. Four focused envelope tests pass. Initial failures remain recorded separately.

The corrected acceptance consumer SHA-256 is `e273f4b068721ec6efa07266381782d252e2caf1ee16d53e94bb8be159c8a893`. The archived engine fingerprint is `e86d572ff7808b0322b564570a389c33c44994ccabc31378062967594a37aa1a`.

| Tape | Operation | Final replay | Original tape SHA-256 |
|---|---|---|---|
| 9b974d4c-c695-4cce-bb43-fae09176b2b1 | claim_submit | MISMATCH | `d4e89692a6141bfbd1d99b1ae041e55bc0d9042d6b3a1dfcd917163234fab5cc` |
| 6176dd70-ea5f-46e1-b96e-8fbb072f8db3 | claim_run | MATCHED | `a49117f3b1126b892c417aa1725cd7bcd35dd276ab0aa4e3c65273851a69bbaf` |
| f9e6b0c2-31a5-4a0a-a24d-b5c87e44dc89 | claim_confirm | MATCHED | `737cbf56faabaf7804a6303362eb0b1c6a28b14ba9d64629342d7c3d568dd395` |
| 35ae28d3-2f1c-4f52-ad5e-d8f5166929ba | claim_run | MATCHED | `a14ca3c7326da1db92b84f0ea8dfe2bc78a9b92049a56b5798e5091029df8fd6` |
| 8fce3350-04ac-46a3-8e75-43288a4fe5de | claim_confirm | MATCHED | `e3080b8d55758790ab6cf7c518ff44377828a616366458479e4e22b0cae92c8e` |
| c479c21b-8a20-440c-bfbd-825167f4bc55 | claim_submit | MISMATCH | `a66f9a30c792ba06b66fbaafc537af6f2ebabe0849f159d103cfd58aa0fb93b4` |
| ac55da7b-742d-419a-9e8e-779e24983446 | claim_run | MATCHED | `677b2f979966e69d69959d42d544e658911f21f054de75eb197b7600f8f41a29` |
| 7aff2013-3a47-4416-a524-9ce17bacf52e | claim_submit | MISMATCH | `bd7e5404579610db434533c1105e23cbeec7a18e7d18ddd77e8cebead92c7b82` |
| 37f8f326-5e6a-4af2-a2e3-a59a8d12708e | claim_confirm | MATCHED | `bd1b634ffaaa8210a7dd8dade4cafd511bf54a455d751d7b1bee0673d52e4fac` |

The confirmations all matched. The original submit mismatches remain failures; no expectation or stored array was reordered to manufacture a pass. The complete private receipt map is `.local/round-sixteen/c-replay-final-map.json`, SHA-256 `94f9b7a3f23d573a540a96fc9faa6ffd142c6906ccc144d003ed71b13369bc20`. It records each result artifact and hash. This replay result is distinct from investigation accuracy and estate readiness.
