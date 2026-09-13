# Investigation acquisition on reviewed snapshot lineage

The development estate explicitly selects lineage build `549f1a33-5b04-40c3-8b64-718d507e480c`. `--lineage-run` can override it for a deliberate historical investigation; without either reference, acquisition fails instead of selecting an implicit latest graph.

When a snapshot Bronze reference exists, its schema must equal `snapshot_<source UUID without hyphens>`. Asset resolution and the actual SQL query use that same schema for orders, payments and refunds. The reviewed graph must connect every planned boundary before any cloud query. Older estate files without snapshot configuration retain their original `app` path; missing/mismatched snapshot assets fail rather than falling back.

Python and PowerShell both restrict the schema identifier to `app` or the exact lowercase snapshot format. Values remain parameterized. The saved investigation includes asset IDs, the actual SQL text/schema, graph ID, per-boundary eligibility and expected publication references. Credentials and credential-file paths are not retained in investigation evidence.

```powershell
python scripts/cross_layer_investigation.py --currency USD --order-id ORD-000002
python scripts/cross_layer_investigation.py --currency USD
```

These are current endpoint observations: source SQL is live, and SQL analytics endpoints/DAX are not pinned Delta readers. Expected publication references therefore do not populate `source_snapshot`. Numerical matches are diagnostics; strict comparisons remain NOT_COMPARABLE without common snapshot evidence. Unresolved relevant lineage still blocks conclusions through the gap policy. No automatic defect routing or data mutation is introduced.

Four new tests cover schema/source identity, injection rejection before authentication, explicit graph selection, persisted paths and no implicit latest-build fallback. Existing cross-layer and generator tests pass. Live evidence is recorded in the tracker.

Live run `203157aa-0ccd-4bca-9188-1111191c8cc1` matched all five layers at 100,000 orders and USD 64,892,824.49 net cash. All eight boundaries have observed MATCH and supported lineage; strict status remains NOT_COMPARABLE. Earlier sample run `6fee7189-fa82-4bdd-a510-74c95cdd1573` retained a source SQL connection failure (40613) while the four downstream layers matched at one order/USD 1,529.64. The successful full-baseline retry is a separate retained observation, not a rewrite of the failed sample evidence.
