# Native currency filter diagnostic

`scripts/native_filter_parity.py` compares Order Count and Net Cash using
FactOrder.currency (the native order-details slicer field) versus
FactOrderLine.currency (the existing acquisition adapter). Both calculations
use the same explicit order ID in one fixed DAX request. There is no arbitrary
query input, refresh, SQL connection, or automatic retry.

Run with the Fabric-authenticated Python environment and explicit `--tenant`,
`--workspace`, `--model`, `--currency`, `--order-id`, and `--output` arguments.
The output path must not exist. Output retains query, raw response, scope,
capture time and a content hash; authentication failures retain only the error
class. Credentials and tokens are never saved.

Results are OBSERVED_MATCH, OBSERVED_MISMATCH, or NO_MATCHING_ORDERS. Matching
values for one order do not prove general filter equivalence. This diagnostic
does not reproduce saved report filters, browser selections, relationships in
all contexts, or user-specific RLS. It does not establish a common source
snapshot or a technical root cause. Production slicer approval holds remain.

Next acceptance work: expand representative scopes, verify native definitions
against the deployed model, and establish comparable source versions before
allowing production report conclusions.
