# Diagnostic-only prompt caching

Owner approved 2026-10-27. Frozen held-out inference is unchanged. The diagnostic pins its first instructions, tool contracts and path context; subsequent updates remain after that prefix. Both tool and system breakpoints use the standard five-minute TTL. Native cache creation/read token counts and the prefix SHA256 are recorded per successful call. A post-run assertion fails on a later call with zero reads; a miss is reported, never fabricated or used to discard a finding.

[Anthropic prompt-caching documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) specifies a512-token minimum for Opus5.5. [Official pricing](https://platform.claude.com/docs/en/about-claude/pricing) lists USD per million tokens: base input4, output20, five-minute cache creation5, cache read0.20. The diagnostic uses these rates; one-hour caching is not enabled. Actual live hit ratio and cost comparison remain pending.

The provider?s [Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api) requires an admin or organization-scoped key. The existing workspace key returned401 for that reporting endpoint; the larger existing ledger total governs admission. No new key was requested.


Cached diagnostic preparation:26 unchanged static forms, zero submitted at preparation, immutable input archive SHA256 f9cc4f15823fa46013593de378e17bf9f2ee9083c78ea1ade15f7a3d54047252. [Image and source pin](runs/round-twenty-three-cached-diagnostic-image.json). The earlier uncached archive is retained and unused. Original frozen held-out image2f22b43d remains unchanged.
