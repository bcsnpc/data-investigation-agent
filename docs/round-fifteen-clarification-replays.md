# Round Fifteen exact clarification replays

Final, 2026-10-12 05:46 UTC: **127 MATCHED + 1 MISMATCH + 0 pending = 128 operations**. All identities are unique, and every original tape SHA-256 still agrees with its sealed inventory. This is replay conservation, not investigation accuracy, readiness certification or an all-green gate.

The operations comprise 71 form comments, 19 ticket replies and 38 agent resumes. Two matches were already completed by root; this helper completed 125 matches and retained one mismatch. No estate/provider calls were made. Successful summaries report zero network requests; replay socket guards forbid network access, and the helper forbids connecting or attaching the live pot and dollar ledgers. No engine-drift option, recorded-identity override, source edit, receipt rewrite or expectation change was used.

## The preserved mismatch

`c30646ee-b47b-4c88-aeef-beb6552b5de8`, clarification 030, `agent_resume`, returned **TapeError: TAPE_REQUEST_BYTES_DIFFER** under the matching source fingerprint `b9868654a96b89e0d254ea813ff7889c6f57afbec86886e4a57b1065b63eae6b`. Its failed clone and result remain, compressed with identical logical SHA-256. It was not retried and was never counted as a pass.

Read-only code reconstruction identifies the exception-chain fidelity problem at the next recorded progress event (CONFIGURATION ordinal 264):

| Field | Recorded event | Reconstructed replay transport |
|---|---|---|
| event.error_type | APITimeoutError | APITimeoutError |
| event.cause_types | [ReadTimeout, ReadTimeout] | [ReadTimeout] |

The provider-failure event retains only `ReadTimeout`, not its underlying cause chain. Live HTTP transport supplied two nested timeout causes; replay creates one HTTPX timeout, and the SDK wraps it. The failed clone's last persisted agent-progress ordinal is 24; the next sealed progress ordinal is 25. The derived progress identity also depends on this event content. **The rejected attempted request bytes were not saved. This specific-field explanation is code reconstruction, not a saved byte-diff or a second replay.** The original mismatch remains the finding; no matching rule was relaxed and no engine fix was made.

The private helper's failed report did not emit its success-only `network_requests` or `recorded_engine_identity_used` fields. The coordinator initially labelled that missing report data `Offline boundary failed` and exited 1; this was a bookkeeping validation error, not evidence of a network connection. The failed report still states zero estate/model calls and no live-ledger attachment; socket denial was active. The corrected bookkeeping preserves MISMATCH without inventing those absent counters, while MATCHED continues to require its full zero-counter and no-override proof.

Phase one preserved the mismatch and stopped its peer: 73 matches, one mismatch and twelve untouched operations. A separately frozen, disjoint second plan ran those twelve exactly once: twelve actual matches, native exit 0. It excluded 030. The final map therefore contains 127 matches and one mismatch, with nothing abandoned or silently replaced.

## Source and controls

Six historical operations replayed against their recorded Git revisions, 515bb1c and 09ad88b. Nineteen unchanged Git-blob files required their recorded working-copy line endings; logical source contents did not change. Their actual source fingerprint matched `3326f52096e52c07be711ed07a27ae99e3d324f17107f0bffe9145c04be11667`. The other 122 operations match `b9868654a96b89e0d254ea813ff7889c6f57afbec86886e4a57b1065b63eae6b`. The current working source remains unchanged.

The first serial replay pass yielded to live continuations. After live work drained, root approved at most two independent offline coordinators: distinct frozen tape lists, distinct outputs, no child writes to the shared map, and one aggregation writer verifying duplicate/conflict coverage and original SHA-256. Measured startup headroom was 17,832,046,592 bytes, exceeding 16 GiB; each child additionally required more than 14 GiB free. The existing 10 GiB floor was retained. DECIDED WITHOUT REVIEW records the authorized scheduling choice and rejected serial-duration alternative. Nine private coordinator tests passed, separately from the unchanged production suite; they cover disjointness, admission limits, source/offline boundaries, duplicate and SHA refusal, single-writer ownership and preservation of incomplete failed reports.

Cold controls 10 through 15 used disjoint slices of the existing inventory: 84:96, 96:108, 108:120, 120:132, 132:144 and 144:156. All 72 original catalogs were FINAL, journal-free, nonactive and outside the shared ledgers; all six controls returned native exit 0 and preserved catalog/tape logical SHA-256. Receipts and dated ledger notes are retained. Cold 16 was unused. All 126 clones produced by this helper were compressed after closing, with SHA-256 agreement, including the mismatch. No file was deleted. Final free space was 17,201,254,400 bytes.

The separate billing metadata replay remains blocked by its recorded-source mismatch; these clarification matches do not repair it or authorize publishing a profile. The [owner portal trial](round-fifteen-owner-demo-trial.md) has its separate six matched operations and is not included in this 128-operation clarification count.

Private audit: `.local/round-fifteen/clarification-replay-final-audit.json`; map SHA-256 `c3bbc22c55bd33654f1484f76b8838274f38f542cc050f02ba32a8f6a7b81598`. The private map retains full source, tape hashes, operation/result paths, errors and compression proof. No accuracy expectations or tester replies were used to rewrite evidence.

## Full operation map

| Clarification | Tape | Operation | Source | Exact replay | Sealed tape SHA-256 |
|---|---|---|---|---|---|
| 036 | `47e394b2-e04d-434e-8f52-f427989ba7da` | ticket_reply | `b9868654` | MATCHED | `8dd299fac9058b9da9bf98bb245ad09ff6ead6ba743c3d6dafc8e04886956d9f` |
| 036 | `f76de64c-611a-4cab-b13d-7bf7dc0cb3f3` | form_comment | `b9868654` | MATCHED | `3aeb6b2cfb2c91c31206b2636497d051104c17d58f9c248136e0b93c5ca58665` |
| 036 | `deabbcc1-95a1-46d4-b250-2848aea67d45` | ticket_reply | `3326f520` | MATCHED | `a07b8acbec453ce56eed666c188c8f6277ed61a562d848a443125695452b9341` |
| 036 | `e00ae144-4b13-471c-a5c1-c4297d9c493b` | form_comment | `3326f520` | MATCHED | `cb915de36d72c171cb6be7918f4d1b130c2cf93261a51f8f63f555e86f5a1306` |
| 035 | `09cf25c5-abda-4406-9ebe-e0db8edcd103` | ticket_reply | `3326f520` | MATCHED | `d13d9a77e04a71397b053a8ca1b3a763f5301489dee9bc761906ea6be71721eb` |
| 035 | `fe8fca5b-86f8-4d0b-a65f-167da1488192` | form_comment | `3326f520` | MATCHED | `b97493cf58147fe67eab65e0882bd1fdef400a2c6b79a9868fa0b63edaa7c95d` |
| 034 | `44001a3b-81fb-409f-ac5f-4dcde0b1089b` | ticket_reply | `3326f520` | MATCHED | `adbebf6ce7c9215fbe2eb6740c54161aa3bb1fbcef1b89eef045b4df7a935df7` |
| 034 | `f61e9cc1-604b-46b3-a6fb-ff2c19ac43dd` | form_comment | `3326f520` | MATCHED | `118c9a71307ad309510b05b9b23d98d58c3db949f0ef488193845d9cf5f7c6b2` |
| clarification-039 | `1ec5c664-ece5-4a23-b274-87fa8dc4c247` | form_comment | `b9868654` | MATCHED | `c8ab0463b62033be7e39d7ab987260d6704d5816c4de662163afcc8c7eef62a6` |
| clarification-037 | `47772b25-c809-42c5-a6d9-49a3ad8d7650` | form_comment | `b9868654` | MATCHED | `1db7e5002b255bad1aaa0f59add333461f9ac8d59bcc7e076ce91eafbdec46c2` |
| clarification-044 | `7f3efe16-f052-4839-8cee-c48306e20c45` | form_comment | `b9868654` | MATCHED | `52915df57cf2925b38eb666be2826a3fd120dcc6ebef415aa9735915b348f0d3` |
| clarification-042 | `18a36db7-191c-49cc-882a-66a50435a31b` | form_comment | `b9868654` | MATCHED | `b90ed77059fc3972189ce27bfced52d38674382fa1eb76aec31717743c7024c1` |
| clarification-041 | `c63ce189-cccb-4862-a2d3-944266ba39b8` | form_comment | `b9868654` | MATCHED | `88c31ed9478ecab6f27e7b548f4112411bcabd3a9f5411ef47d489d1f0925ac3` |
| clarification-040 | `0c45fa92-bfe7-4ceb-813b-c55e3daed65e` | ticket_reply | `b9868654` | MATCHED | `a651e3451f3ec9c58ebcc2c1c0c1c10d6c3459129a76ca1bcc9308a982e76182` |
| clarification-040 | `c0d200a0-7e24-42e4-be39-05ebe86b85fd` | form_comment | `b9868654` | MATCHED | `ce4ab7edf281499975a1db3a8abe7070001b0f4636914edb064dc52673dacdf2` |
| clarification-054 | `92f527a8-da33-443a-87c1-94f743f44335` | form_comment | `b9868654` | MATCHED | `8a7e3d3148489bb05539f3a55228db24e92b7566d1209034cc1119d1af6bba02` |
| clarification-052 | `e9608a5c-7c85-45b1-a6b5-64ac95fa98e1` | form_comment | `b9868654` | MATCHED | `82e64b37b821bb27b350c57c4ce65cead5fdce706bb409e6866327de5137b20b` |
| clarification-050 | `072189cd-9633-4029-82cd-f74fb28e7c50` | form_comment | `b9868654` | MATCHED | `de409d9448f7b91e06cf59429de2d905bf3fb48486c16d2a1c1b48568f116f28` |
| clarification-049 | `f9b69268-1588-4d2c-99b1-9383d9eadcf8` | form_comment | `b9868654` | MATCHED | `780e927896ffb52bd99c5eb544d0c1f4b56d5c8c1838534541b303fe5010e802` |
| clarification-047 | `e2aacaad-343f-45ac-b3c3-edb30824550c` | form_comment | `b9868654` | MATCHED | `1a86145a7d3dd429ca22e1937e0b552f6d7bd22bdeee98c71ab4440373926be0` |
| clarification-046 | `7b385b3b-91ee-4f5f-a4d2-621dc19dace4` | form_comment | `b9868654` | MATCHED | `3c1467a7e7ac2d27f7bc86d2feccb45f26323d199a1982121375ced5ff5dd94f` |
| clarification-056 | `dfd84509-215d-4f81-bab5-c0f85a692a5b` | form_comment | `b9868654` | MATCHED | `2a336c39eaaf409cb16cd11bff1c6961828039a07a42a0b58186725899d33d80` |
| clarification-055 | `3565043b-4b1a-4c5b-9ec9-ccffd6c2eb21` | form_comment | `b9868654` | MATCHED | `3e31cdee4e8c65f801796384be052d443475cf324de2eb6c4b0c35fde0262e03` |
| clarification-037 | `11d227b3-3897-430e-a8d6-6cad8b3fa231` | form_comment | `b9868654` | MATCHED | `37b9d68a0cb95d4794154926e2bd9e438b0fdecea75255a7fdd6f5f25da142f3` |
| clarification-057 | `f3db7a9b-c021-423f-bd42-a01782506e4d` | form_comment | `b9868654` | MATCHED | `94eeff0ba8c67b51ac1869ce13c0beb1bc49bb64a01566807a0f41599745731c` |
| clarification-039 | `f1dbfa42-5ccc-44e3-b6bd-2850c686f8fb` | ticket_reply | `b9868654` | MATCHED | `02ad066b56d4eb19ef43132f1d91b3537c2e583f8b3013e40f2a516ede6e3973` |
| clarification-039 | `7878eb7f-0403-469e-9ca6-905ac61a7a24` | form_comment | `b9868654` | MATCHED | `3c45209a2172c3bd7d41b7db09db7f3928dc59ba7eb35f5a36b09c4379857670` |
| clarification-037 | `b0b8cdc0-e987-4a1e-a6c8-395e45e460e9` | ticket_reply | `b9868654` | MATCHED | `fb2616e3d1e6a0c796a6ea53ac8727b3b6a272190adf0ade9eedecceff83f3ad` |
| clarification-041 | `ed821034-077e-4468-b9c3-18d4bcc4f418` | ticket_reply | `b9868654` | MATCHED | `4c28975b53678731a795acceead371688b3243b7b7a39d74cc6535599a738a78` |
| clarification-041 | `c70cd6ec-9a28-4352-ad6c-b0d1fff371f2` | form_comment | `b9868654` | MATCHED | `668fe93785ffb8374b4d6e27e89e6f2167fa1ad4c23896ceb709c36aeecbba7a` |
| clarification-055 | `1ebb3cf2-d5ca-4053-a310-ac21beb2be74` | ticket_reply | `b9868654` | MATCHED | `ce08cd77ddd6463a98ebc7a6fad10f61a2a1fc0ea1cefb596285782ced82f6e6` |
| clarification-055 | `44407e31-76b9-48c6-9c12-d0f92e18372b` | form_comment | `b9868654` | MATCHED | `6999d97299f568faa6769fd29cef2f43b0df90cdb07633f7578f33d2a79fe02a` |
| clarification-054 | `c6da5e13-9a34-47bb-859d-b3f5789d5744` | ticket_reply | `b9868654` | MATCHED | `40a68493790614169de0e376b27a14c2489d37e78460591532ed0f75e4e0924a` |
| clarification-054 | `f2906847-c7e7-430f-aee2-9b5274904c0e` | form_comment | `b9868654` | MATCHED | `fc046678bd10116be366bfddbff59f452e2d053129887def129456cdde044efc` |
| clarification-052 | `654cc1cc-e1c1-406e-8b2b-8774694ceef2` | ticket_reply | `b9868654` | MATCHED | `7095ddace218609f6215ee324f61549f67abdc76b971bf61c7f5c2ab14626265` |
| clarification-052 | `3a13549f-5ab0-48d3-bd99-6f50ef83e604` | form_comment | `b9868654` | MATCHED | `dd39b038215702eb8e04db466c1d3dd5ba1c462ad81e2de3b9e811d4bc12d719` |
| clarification-050 | `a4ef8393-fa18-4c29-b923-5c1f3014178c` | ticket_reply | `b9868654` | MATCHED | `7c512d9dd483f0136b101ba0e627e42439618e4cbecfdd38417d5a0c229a5eaa` |
| clarification-050 | `31c3af85-39b0-428a-8b1b-0822916cc0b3` | form_comment | `b9868654` | MATCHED | `2d850616d5d1a124cdaa3b5458719945e3df801e36e74c9d4d8533ad36fbc1e0` |
| clarification-049 | `90cd7877-a80d-4f49-8a07-89878b0318bf` | ticket_reply | `b9868654` | MATCHED | `b0b9e85c3fc89779caebebe0f224d19655750258e7bcd8c90376e6901daf2f27` |
| clarification-049 | `51df482e-a28e-448b-bc9b-543a86ebc542` | form_comment | `b9868654` | MATCHED | `ff1bfd2246e3bcad2857d0f47832f44856b90a8fa01fa0e9705f7ee7a1ad84da` |
| clarification-047 | `82fe57d0-1930-46d1-a4f1-d7e9c11078c3` | ticket_reply | `b9868654` | MATCHED | `329d21e3fe943c6d6f27385a28d569392d8b721a3785a882b7a69a3d17e4cf67` |
| clarification-047 | `5bc1cf3d-70c5-4649-94c3-0347444092d9` | form_comment | `b9868654` | MATCHED | `b3bee4971613ab4de9f23b94e2863dcb0bc7a96a8290cca5e68e35a83e684bfb` |
| clarification-046 | `3ec0f620-a5b4-4853-983a-a73292d7d161` | ticket_reply | `b9868654` | MATCHED | `4a59544c5f1a07e6eb71ec110078b7d96dff999f28a7b731ba84a9d0eeb415bb` |
| clarification-046 | `e51cc38b-5a38-451a-96cd-8c726b3bf410` | form_comment | `b9868654` | MATCHED | `6e0090a9f513e9ab39e55f4fc1ac5a43bc7fb9f26c824f29228932db31ba05bb` |
| clarification-044 | `45574776-7ba0-4292-b5b9-23a8f43c5389` | ticket_reply | `b9868654` | MATCHED | `c5a0ee5d1cb8768b0e1ced9f4e624a3ea4954c6d576509f9dd3441c3a297f2af` |
| clarification-044 | `b4d4568f-04f9-46a9-ab31-be08964f3587` | form_comment | `b9868654` | MATCHED | `9d3469da99075ec645159c3b15300085e273aeed11d173b2043dab75007f59ca` |
| clarification-042 | `93488402-3722-4c0f-a46a-5fad5e432040` | ticket_reply | `b9868654` | MATCHED | `d9b3b5553a4a91af42dc2581bad963040d2ea497e21d383cd48992048c397a4b` |
| clarification-042 | `8a286221-ed51-46ff-aa45-c81ecff663f8` | form_comment | `b9868654` | MATCHED | `1cb0cdf31421a0336c458cb8e6777ef0634af55f0e55a66c4dda7135d656ed80` |
| clarification-057 | `a32a03a4-0591-4af9-9d06-1f3a3666b115` | ticket_reply | `b9868654` | MATCHED | `f085bb1923f587741d64b24af79f80765b7d6b68edabc006b4be498e3e1b6572` |
| clarification-057 | `46c1e01d-d9c8-4e0d-9798-9d535cddcfad` | form_comment | `b9868654` | MATCHED | `69088d4758224cfa2cf42179acf9c690baf1f14c7f5d828003cfb943e1e7a625` |
| clarification-056 | `354d8de6-37fe-4790-9c69-3f835ed446b6` | ticket_reply | `b9868654` | MATCHED | `574dd8e93fb8a8a0d0f2ee198ec05189ad7222df670c8aeccacf673c53458271` |
| clarification-056 | `70c778cf-367f-4fbb-90ef-31fe4a99284d` | form_comment | `b9868654` | MATCHED | `0e0b1d1720add713f16ca4a9d54e7b9e1433a227c9fc29ba3102d06e439491f5` |
| clarification-021 | `67580ebe-cd9d-435c-9e52-45c6ed5bc701` | agent_resume | `b9868654` | MATCHED | `b0504500674ba92143eb320a1116eb9a46a345539cd1ada87b46040f99efbe7f` |
| clarification-021 | `8ed68364-39f1-46d6-bf6c-c03937017384` | form_comment | `b9868654` | MATCHED | `76d592d910781e3852c1e59e8c5e558c2f77d0e807b0d70d4d03bc732ce8a060` |
| clarification-020 | `39a7f4eb-7028-47e2-a338-2544992fd128` | agent_resume | `b9868654` | MATCHED | `0029e2da2a59fc46a6d8befffe85bc8cbedb31df1876137fb416bc678f6f0468` |
| clarification-020 | `d5826c20-49a6-42ca-a159-d5ed3be20454` | form_comment | `b9868654` | MATCHED | `7ccea1477fa870344ce841a6a843144f559fcfcf507b49fc3073245e43790afe` |
| clarification-019 | `4036c0db-cc2d-41c1-9afd-4bf97f3d674e` | agent_resume | `b9868654` | MATCHED | `99467abed828e9dca9ba3b6d6bcf81a888eaffe9b738540e7b250770781bf827` |
| clarification-019 | `372e48dc-fda0-483c-b1c0-fe7b1a76418e` | form_comment | `b9868654` | MATCHED | `bdfcb6ee233c41729c7cc6d106cfb31cafe8f461445486efe4ed1741765169f4` |
| clarification-018 | `9a4d42be-15fb-4e90-9a42-8bc669dbb653` | agent_resume | `b9868654` | MATCHED | `c3b717b3c03b92e9747dfc89059a7566f7903afe9db62e94cf58e58cc7d13d95` |
| clarification-018 | `8f1ccfee-261d-4308-988e-de4d89d8a202` | form_comment | `b9868654` | MATCHED | `52e28ecd4842e961122fb496f0afb05f0e069016009e570ff3155c17545f78ca` |
| clarification-017 | `e304835f-f847-4ca9-b8ad-fb4b659c5d27` | agent_resume | `b9868654` | MATCHED | `946141d8421b81df44a0d42c8646081e06169f3f9b5c2e839259f74b9e5cefbf` |
| clarification-017 | `2fc1f9ab-94ef-4a9c-8079-91fbf481132a` | form_comment | `b9868654` | MATCHED | `c48efdb8730ddd9389b827c7a73a7e735b73db28099afebe5e608804a9d6771f` |
| clarification-016 | `6c4197b8-780c-4a41-a2c7-805f57b383fc` | agent_resume | `b9868654` | MATCHED | `8b9ee138a01d487879b19e764c0a14a4bc55adaf023cec14ce4e8f004dd98a07` |
| clarification-016 | `8478be1f-7fa5-416f-9012-d3e6c54bff48` | form_comment | `b9868654` | MATCHED | `b2c9419c2963da24d520723f4e00663f23ef5c5f77289cc4d3d3df9bfc90ac23` |
| clarification-015 | `43fae53f-8351-4bb6-8a6c-1ba3acb0b293` | agent_resume | `b9868654` | MATCHED | `23dcebeab4c58a92ef1d897f9116414d3fa2402b340b6094921efd36fa757d0c` |
| clarification-015 | `f1fc7d47-9333-4488-ac56-b067f4592a11` | form_comment | `b9868654` | MATCHED | `6f1354c4e863dbf799678c1b82110eb8248e6a77c034b2dc15677e1f4580ee56` |
| clarification-014 | `1f374104-eba4-46e9-bf38-340277accec6` | agent_resume | `b9868654` | MATCHED | `bca2a3d8bfa8e11414644877869cd0cbd8ca94effdf22d6dc7ef0cf9801ef8fe` |
| clarification-014 | `695fe420-d210-4288-b11d-b014eb99dd9c` | form_comment | `b9868654` | MATCHED | `a0c8f07d7fa83930174a7e608930462a5b33a05d4a12a379958263aac7a17045` |
| clarification-013 | `eec41836-128b-4b8c-a038-c6da3961c21b` | agent_resume | `b9868654` | MATCHED | `b06974b35bf12a5bee2201eb93a0f2d75ec1b2fbf2288597e4b3ad0b011f5656` |
| clarification-013 | `01bbf909-5786-4a9e-a2ef-d33457f7f52e` | form_comment | `b9868654` | MATCHED | `1376f4919af010f0bbc73e94f66ec33dfe084007f5d2116be6b30283d1553f2a` |
| clarification-012 | `f114130a-dd72-4d05-b6e3-fb37a9c8660e` | agent_resume | `b9868654` | MATCHED | `dc495d687ad73530d3be05979f52730d0a832fd5a1b8843b81cff9abf3e61f13` |
| clarification-012 | `47c78841-eb73-4c36-8f74-25e53cebb1a9` | form_comment | `b9868654` | MATCHED | `09e30c939d95c01c77285f4ed9527e2ce8ea21c9bce018cbf1ab496e3aeeb47b` |
| clarification-011 | `6ebb752a-f096-475a-8c2f-330a43722a2c` | agent_resume | `b9868654` | MATCHED | `bc27288c32840a5ab893d81c6363983bb456d8ef24cf45de560b582159ebaf93` |
| clarification-011 | `cdb525db-502a-4e38-8e69-6ad07cdd31e8` | form_comment | `b9868654` | MATCHED | `6ba05c0c897d621869fb5cd89436220e526137a044896fa7db830497212163c8` |
| clarification-010 | `28308cb9-19f1-4833-89a3-55d1a2b26d70` | agent_resume | `b9868654` | MATCHED | `6cc88012f54b5d6418e2e38de0dca902aa2eacb9ad88235a777f37018c13467a` |
| clarification-010 | `295a0320-a5f3-4671-bdf4-8a8e29ba235f` | form_comment | `b9868654` | MATCHED | `c8743a4005ea49ba694855cdf487c66463cf229f0253b15fe384a5d17388c42d` |
| clarification-009 | `3e80a0bf-ad68-4a51-b479-0ec6eca2df74` | agent_resume | `b9868654` | MATCHED | `d9342c7e81e28d9cb58d27dde2cc96dd7ffb2ca92356ea2d06f416ce983d4e14` |
| clarification-009 | `4401de01-5d86-4b00-af2b-92b3ff6388ab` | form_comment | `b9868654` | MATCHED | `a1a5bb566b5b218bdf404c1a49f106ad26f369deee854c7de29268c78ec4ed68` |
| clarification-008 | `8b5444ef-0ce6-4001-93ce-739478600b74` | agent_resume | `b9868654` | MATCHED | `5790987438f26d43cce715508c3b82c8ce19072e538c6de181ade4fa5ca09bad` |
| clarification-008 | `ead41850-4242-446b-918e-9d0d02a47c4b` | form_comment | `b9868654` | MATCHED | `28f6a775b5aed8e0c4cf78ed2e55ef035714282e421d511d501630ba1058b91c` |
| clarification-007 | `deea9f8c-2876-43ab-87e7-97403b4260ad` | agent_resume | `b9868654` | MATCHED | `a60ac7098d4d48ab4b2edfde9f6c058ead94c405b6f16b6d804421a28a71dd09` |
| clarification-007 | `bfddc2ba-02c6-4123-8133-146230ec707d` | form_comment | `b9868654` | MATCHED | `8d176df02de4a4efadc0f4ac29f4e8a3b1141ddec482b86edf14943f79cca33d` |
| clarification-006 | `160ba1b0-5d5b-4d0e-b788-f52916cf6e39` | agent_resume | `b9868654` | MATCHED | `bdfbc2b9e1a8d5bd60df0ef48b8936fc9d401b4c3bb3e5e1dab76e2a65554da9` |
| clarification-006 | `c6e1bb5a-7c1d-4ee2-9487-e02e97be53f6` | form_comment | `b9868654` | MATCHED | `64af04454119457d358f220ba61c991b70e49bf2e7f38ba1058ef0ca69e0ff54` |
| clarification-005 | `378bdc6f-2004-46af-9a7f-d1ce68d97b2f` | agent_resume | `b9868654` | MATCHED | `bc5f46fa4fed07a516c654804c7ea3b9f39da85f3dbafd8369e1d60b304279a4` |
| clarification-005 | `dc2da441-b767-4449-9355-3c919d5c31f7` | form_comment | `b9868654` | MATCHED | `4d67c92a2e7edfaf493604eea114a33e1b8b4efe8e0ce8ec120ce038896ebbd5` |
| clarification-004 | `853c3c06-37bf-4659-8d2a-cfb01d9fd54f` | agent_resume | `b9868654` | MATCHED | `c919ce893015df9d95bbe720f421450a63ad4eeac09efd1d238b6c8c645160f9` |
| clarification-004 | `80e5b426-79f5-4b6a-adb3-d2da69e15f84` | form_comment | `b9868654` | MATCHED | `42ecd9c4a5048585cc4488eb9fcb9f11f3a65df6a4e66b228bee8bdc0b560fd5` |
| clarification-003 | `6d0741c7-13d5-4806-a441-8fc6a99d8c1c` | agent_resume | `b9868654` | MATCHED | `62d52730556f4374e5be983046d2a1411b4d1f73c68476986ccbc3db44dcb4cc` |
| clarification-003 | `1a037591-bc42-4274-b8de-bc4023964640` | form_comment | `b9868654` | MATCHED | `2ed2437c3a4be4012535b76e020587cb9891b2d9dc35faf3c62f75f00b3f9030` |
| clarification-002 | `48723bb3-cd8f-4a5d-b9e8-cf678f1215e6` | agent_resume | `b9868654` | MATCHED | `1a91fe6f1600fbaf65064c293db1d4c8bb3a2e61c01af792bf0d57ebe911cc53` |
| clarification-002 | `fb9836a8-69fc-468d-aa4e-b8fa049cf851` | form_comment | `b9868654` | MATCHED | `2937f35797a41b16acc5fbe406d073f04de66dde4301e5c54c63a594dc1634bb` |
| clarification-001 | `c7f744e8-5d9c-4817-b569-76a19de81820` | agent_resume | `b9868654` | MATCHED | `8aefc14a55743b2aa0356bea871582ff9d24681eca4219cf3090c5acc80bd9c1` |
| clarification-001 | `5ba10c42-108b-483b-8e16-63577bbe5639` | form_comment | `b9868654` | MATCHED | `e831277dbbab963b976eab6634ea05978842823807a634ad42babdd83ad4fc0b` |
| clarification-029 | `92759005-556d-4564-91e4-1fc7b41f3b89` | agent_resume | `b9868654` | MATCHED | `8077ed3e6faf580e814cf972b7ac5037ce0c56f63816c398dd31a2f2ab601d29` |
| clarification-029 | `f0a40066-9aa0-46a6-b465-f4aa97900ec2` | form_comment | `b9868654` | MATCHED | `816534884850c84849184612feffd6af328874aa8ba79e35bcdec30635c262a0` |
| clarification-022 | `f785d1f0-f3a6-4811-9c49-afa68b0c8801` | agent_resume | `b9868654` | MATCHED | `467765725ecd433d38a2854acf63b339e089c4860da43cdb7c77d12b0687cf04` |
| clarification-022 | `69128992-de23-4566-b6cc-2c5332aeab19` | form_comment | `b9868654` | MATCHED | `36eab97344da310e6af6e7c63691df7e5e2a3b4a36fedf8539c9453dd136573f` |
| clarification-011 | `61b07cc1-3c68-4cb2-ba9f-bdf26727f0c4` | agent_resume | `b9868654` | MATCHED | `810e34b48e0bc4e295b2916e9032b2d0a0b03d2bf78b378e76223275761f8929` |
| clarification-011 | `4fb10011-63c1-460a-a53e-8526d3f8d00a` | form_comment | `b9868654` | MATCHED | `0c17b0b6201a5f6a218cb6460d6b7d53912dd31b6cd0f2f51e7491003bc587cc` |
| clarification-010 | `5edb695b-6cbc-48ba-a38a-142df8ed2b44` | agent_resume | `b9868654` | MATCHED | `eb8f76be1ba3fcd3aa7995f23e3b1ba32d5fbcd0b9bd4760202c450bc26b62e0` |
| clarification-010 | `d596c456-f399-46c4-b6f8-e23fa526cf57` | form_comment | `b9868654` | MATCHED | `f5bd78104bdb38f182ed13e32bd540546ae9682827d7f0a78e013fb7ce38bb10` |
| clarification-003 | `5e649338-18bd-49c8-9cbb-671df0b94e67` | agent_resume | `b9868654` | MATCHED | `ab6b38ca0161d2cc0e7812e69ba9c82428d9925fad5bbb802626cd48d10ef941` |
| clarification-003 | `85dd10b5-3f7a-44c9-91b6-e2433505d60d` | form_comment | `b9868654` | MATCHED | `0f814d1a2dd322a39a1850c72797a47f221ec2d636d5ed077a357844782795f9` |
| clarification-033 | `c6ce26fb-c0fc-4b59-8e7a-955776369845` | agent_resume | `b9868654` | MATCHED | `3b2eb2b9a9d381a2b1d57926d7299dbdbc77be80aecb51ec0697616780dfbe7c` |
| clarification-033 | `fb644178-a5c7-43f0-8fa0-134d33eaf40c` | form_comment | `b9868654` | MATCHED | `cc0e1a1bedd038f0a0365cb00644aca6bfb7ace90618c1d0e4809988903abda7` |
| clarification-032 | `5bf8cdef-37be-4cf4-b89e-7a1857ad7733` | agent_resume | `b9868654` | MATCHED | `5968fbd90e391eff413d23264ddc35a97a506e42b62c483f7ad3221912caba63` |
| clarification-032 | `dabf7c68-d200-47af-b958-cf3ed466e8bd` | form_comment | `b9868654` | MATCHED | `384011f0ee7497b57b60df46c22d3f535de754058d596f9cfff70ee9a9bf64b8` |
| clarification-031 | `3710c93f-af0a-49a9-bac4-3e9201e5d4e7` | agent_resume | `b9868654` | MATCHED | `a2ac9c6860b0c04da7f66f6cb50e2a9bcd6020a22a2ff92be46be7fb97accbef` |
| clarification-031 | `ce1d79b2-203c-4cff-8f29-032c101a52c1` | form_comment | `b9868654` | MATCHED | `9d85189abcb20bb167a08fb5af5fd784896614b550050ac46f1fdb84aa840100` |
| clarification-030 | `c30646ee-b47b-4c88-aeef-beb6552b5de8` | agent_resume | `b9868654` | MISMATCH | `9d5e1e720bbfb7f24b70d007f6f41f24930521981263a50479238e81b8b50064` |
| clarification-030 | `7f97b322-c570-4a70-b630-67072d2c4648` | form_comment | `b9868654` | MATCHED | `689bf0f85f29b2fb648a7930e67a5923cb27b8b160d7b7aa928c30a40fbcb264` |
| clarification-029 | `2d4eb5a6-7728-4e5a-a19e-45935da5fab9` | agent_resume | `b9868654` | MATCHED | `faf7ef81c6401317dcbed85c29ef151d04514000a0bf7def16766ac4dfdf8299` |
| clarification-029 | `5ed6acbd-00d8-4731-8c93-0f8fc53d8611` | form_comment | `b9868654` | MATCHED | `b8b35327635989fafd8afb05dc4abbca8cd90441b493f7dcbdf24ba394b1cca1` |
| clarification-028 | `d2d23f09-7b8c-41c6-9485-29a3802e3574` | agent_resume | `b9868654` | MATCHED | `880aa6ee53aebbeebaf7b0bb6d9abae2efefa28b9688561f05acc0983f4834dc` |
| clarification-028 | `917b72ad-9ffe-4180-8d77-864d98024a52` | form_comment | `b9868654` | MATCHED | `4d91faa8b4ef0ae9a9dc7590c29dca81890c3e3b316fb53f499a7e5a628fd643` |
| clarification-027 | `7a506bf8-f9bd-4794-85f4-3a6f5d7c3523` | agent_resume | `b9868654` | MATCHED | `53e97c75164ec9d9c361a5e0fe48fe0d79f449bd79e831a628b08d927188fe75` |
| clarification-027 | `07e826f9-5442-4523-8da7-cb27152101a9` | form_comment | `b9868654` | MATCHED | `aef07147082d7c517c2dad33b601601f97df6c426083523adc707f515f330bb7` |
| clarification-026 | `88f6721a-b73b-4ead-a5ff-6b73ccf410b7` | agent_resume | `b9868654` | MATCHED | `6dd1a2943ab6c3cdd7fd5c91d274477dc4f4440f725257e07c9cff8b1ed46695` |
| clarification-026 | `48426a6a-a113-4894-ab61-a943c094de9e` | form_comment | `b9868654` | MATCHED | `8d99f0eb0b2da558a6a94dd1ecc053f536de162bdef9d9e7cd30b5e27f6438f8` |
| clarification-025 | `86029a46-f49b-4c37-a91d-8964319c490c` | agent_resume | `b9868654` | MATCHED | `ad00bee27827bb44557efe1af809001f700d6394fb403b2eaf1dbfee56b928aa` |
| clarification-025 | `b17e7051-d89a-4cc0-9950-72a5b6072603` | form_comment | `b9868654` | MATCHED | `8e1bbf7b66490545e881a476498565f6ccb6458bccededbe73e07911ca5e1ff4` |
| clarification-024 | `f4192188-2e51-4ebc-9a9f-9849a3c4dbb5` | agent_resume | `b9868654` | MATCHED | `1bad3223285edab9e8b5f8b2949e831f8ef17014d98e719d6ffc9bfe14e3c9eb` |
| clarification-024 | `5dadd8b7-1652-472f-89e2-042c9d1dcde3` | form_comment | `b9868654` | MATCHED | `365428c9e22b6e5af414bba05c10e4d5db9476bfa66283340406a89b3ce9371e` |
| clarification-023 | `42137ead-cf6b-465f-9882-39e26f6e49d6` | agent_resume | `b9868654` | MATCHED | `96e2ca0ae5c90580fb3a285835f18b981e3ad1f907c74fae9d6f4f75da6cf6c6` |
| clarification-023 | `b3efb2d6-8348-412b-848c-cf8656f1c454` | form_comment | `b9868654` | MATCHED | `58597602f2074d20bfe83afe827742720a0cde2eb0986f61c79e596ec4273945` |
| clarification-022 | `85a98418-533f-4c69-820b-b70c8fa66076` | agent_resume | `b9868654` | MATCHED | `afa1d3692c19733942d4b45281a18510f0547f4f73a188aea1ab5bac81355cb6` |
| clarification-022 | `f3a4ba4b-3f3d-4c78-b3b1-f82aa282539c` | form_comment | `b9868654` | MATCHED | `8d61a5c29808beff73572198dbdf27413cafbaac610a93b216ee5adb3922a985` |
