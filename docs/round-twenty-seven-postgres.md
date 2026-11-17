# PostgreSQL diagnosis ? Round 27

Read-only Azure metrics for 2026-11-01 UTC: CPU credits 287.81?288, peak CPU 64.76%, maximum active connections 13, failed connections zero. No server log files were available in the queried inventory. These observations do not support exhausted credits or connection saturation during this window.

Root cause: **NOT ESTABLISHED**. Retained SQLSTATE 55P03 establishes lock timeout for those requests, but the holder was not captured. Healthy later reads cannot prove an idle network drop. Existing short transactions, connection timeouts/keepalives and safe idempotent retry remain; no tier, firewall, role or resource changed. The diagnostic made six read-only control-plane requests. Raw responses remain local; their hashes follow.

- cpu_credits_remaining: `8472ea2b0cddb7d27f58a102c02654a039d88c3508e100a9a0d9550f72fef7ce`
- cpu_percent: `e98e1c1a878b58750135ae47ee0a99490df2690ae8cbde37bbc4522ff59ef5cd`
- active_connections: `57baf5dde7f3af805156af0076148b55f72ca251940f96f993f22e2d742b6235`
- connections_failed: `9ed576f71daad2be1fb463fbd600e5b09058c13e31077be71987dde8224848a4`
