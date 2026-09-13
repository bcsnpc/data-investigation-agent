# Gold publication from registered Silver versions

`deploy_gold_notebook.py` rebuilds the trusted Bronze binding, checks the registered Silver proof hash and receipt, and embeds that Silver publication into the existing Gold notebook. It does not discover inputs from `latest.json`. Every required Silver input is read at its recorded Delta version after checking table identity. Schema, keys, counts, Silver run and source/proof row markers must match. Missing retained versions fail; newer versions do not replace pinned inputs.

The existing six reporting tables and three dimensions are published together. Dimensions use the same order/line/refund frames as the reporting tables. Every output carries the Gold run, Silver run, source snapshot, source manifest hash and Silver proof hash. Each persisted output is checked in both directions and its Delta identity, version, schema and count are recorded. READY is written only after all nine outputs pass and no output version changed during the publication check. Writes remain atomic per table, not across all nine tables; this does not provide a distributed writer lock.

The old separate `prepare_reporting_dimensions.py` notebook is superseded for this snapshot path and should not be run to produce snapshot evidence. Its legacy `Files/reporting/latest.json` receipt is not updated by this publisher. The semantic refresh helper must be adapted to consume the new registered Gold receipt before framing this publication.

```powershell
python scripts/deploy_gold_notebook.py
# Run the existing Gold notebook and wait for completion, then:
python scripts/record_gold_publication.py --job-id <completed-job-id>
```

The recorder checks the completed job time window, exact Silver binding, all checks and the nine-table output mapping. Receipt/job evidence and its hash are persisted in SQLite `gold_snapshot_publications`. This is publisher reconciliation evidence, not an independent second Spark verification. Consumers must validate identities and retain/read the recorded versions; missing or vacuumed data is not reconstructed by this receipt.

Gold publication alone does not prove which versions a Direct Lake query used. Semantic refresh, model evidence and refreshed metadata lineage are still required. The previously acquired lineage graph describes older notebook definitions until recollected.

Four new evidence tests, six Gold business-rule tests, twelve lineage tests and two generator tests cover this implementation. Live results are recorded in the progress tracker.
