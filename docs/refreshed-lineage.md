# Lineage after snapshot publication

Metadata scan `4f443959-2657-4ca3-911a-0627441fa25f` completed with zero unavailable capabilities. It captures 39 lakehouse tables, five notebooks, 25 measures and 45 report visuals. Historical scans and graphs are preserved.

The parser recognizes the reviewed `read_pinned_bronze` helper by its exact normalized AST fingerprint. It reads literal binding destinations without executing notebook code. Changed helpers, shadowed names and unresolved bindings produce gaps. This narrow supported contract must be reviewed again if the helper changes.

`collect_snapshot_lineage.py` rebuilds the registered Bronze binding, including source artifact and verification proof checks, and adds the ten exact SQL-to-snapshot-Bronze mappings to the scan's supplemental evidence. Links retain source snapshot/manifest references, Bronze verification/proof references and Delta identities/versions. These are historical verified publication dependencies, not proof of arbitrary current table contents. The supplemental file is a trusted collector artifact, not an untrusted API input.

```powershell
python scripts/metadata_inventory.py
python scripts/collect_lineage_evidence.py --scan <scan-id> --output .local/metadata/lineage-evidence-current.json
python scripts/collect_snapshot_lineage.py --evidence .local/metadata/lineage-evidence-current.json
python scripts/lineage_graph.py --evidence .local/metadata/lineage-evidence-current.json
python scripts/audit_lineage.py --run <lineage-run-id>
```

Build `18791918-710b-4dfc-9360-ae328d7ada00` contains 373 links. All 41 data-bound visuals have an upstream SQL path without a gap on that traversed path. Four visuals have no discovered binding and are listed separately. Finding a source path does not prove exhaustive runtime dependencies.

The graph remains PARTIAL: eight conditional-dataflow gaps and two unresolved write-loop gaps remain in the snapshot publisher/verifier notebooks. Publication evidence supplies the verified dependencies without erasing static-parser uncertainty. Deployed legacy notebooks are still inventoried; the graph represents captured definitions and explicit publication mappings, not a scheduler's chosen execution route. Exact engine snapshot comparability remains a separate limitation.

The older `validate_lineage.py` is a baseline-specific assertion (including exactly ten SQL copy mappings); use the new audit for this expanded graph. Seven audit/parser tests, twelve existing lineage tests and generator tests pass. Next work should use this explicit graph build and surface its evidence/limitations to investigation consumers rather than silently selecting an older complete build.
