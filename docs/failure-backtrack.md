# Round24 automatic backtracks

Original R23 reports remain in git and docs/runs. Intermediate static-monitor grades/backtracks are preserved as JSON; final assessments below reuse them unchanged. Each table distinguishes the first causal wrong step from an earlier corrected query error. No new estate/model calls are used here.


## Round24 dev01 automatic backtrack

{'graded': 15, 'score': 13, 'harmful': 0, 'correctness': {'cause_match': 13, 'layer_match': 14, 'verdict_match': 13}, 'zero_groups': {'query': 1, 'reading results': 1}}

| Ticket | First wrong step | Reason and correct action |
|---|---|---|
| v2-failed-billing-transform-v1 | reading results | The expected answer requires identifying a specific failed native transform run with concrete details (name/run ID/start/end/error). The delivered answer stopped with TOOL_OR_TIME_LIMIT and concluded no cause could be established. The triage correctly identified the billing transformation layer, and queries did reach billing_ops/load_run_audit, but the single row returned showed a Succeeded run (run_id e82f690b, 2026-10-09), not a failed run. The agent never located or surfaced evidence of the expected failed job. Layer is matched (billing transformation pipeline identified and queried), but the cause is not matched because no failed run was found and reported. The verdict 'failed job' was not confirmed in the delivered answer. The handoff is scored 2: next_checks names a specific query hash to retry, stopping_point is clear, and the query history provides a rerunnable trail, making it a solid handoff despite the unresolved outcome. Interpret the saved result with its actual scope and native semantics. |
| v2-failed-billing-transform-v2 | query | Expected verdict: 'failed job' at layer 'billing transformation pipeline / DEV split', with the cause being the latest failed native transform run (name, run ID, start, end, error). The delivered answer is UNRESOLVED with stopping reason TOOL_OR_TIME_LIMIT. It never established the failed job as the cause; triage showed no run history (MODEL_REFRESH check returned OBSERVED_NEGATIVE with an empty runs list), and subsequent SQL probes of silver.invoices and bronze.invoices both failed with 'SQL object unavailable or view dependencies not validated'. The agent correctly identified the data matches between the DAX semantic model and the SQL warehouse (both showing 950, max_invoice_date 2026-10-01, 5 rows) but never found the failed pipeline run or its details. Verdict does not match (UNRESOLVED vs 'failed job'), layer does not match (no pipeline layer confirmed), cause does not match (no failed run identified). The honest unresolved answer is not harmful. Handoff quality is 2: the next_checks list is specific and rerunnable, the stopping point is clear (TOOL_OR_TIME_LIMIT), and the schema slice from gold.invoice_activity is preserved for the next investigator. Use the returned native error and schema to correct this read before concluding. |

### v2-failed-billing-transform-v1
The expected answer requires identifying a specific failed native transform run with concrete details (name/run ID/start/end/error). The delivered answer stopped with TOOL_OR_TIME_LIMIT and concluded no cause could be established. The triage correctly identified the billing transformation layer, and queries did reach billing_ops/load_run_audit, but the single row returned showed a Succeeded run (run_id e82f690b, 2026-10-09), not a failed run. The agent never located or surfaced evidence of the expected failed job. Layer is matched (billing transformation pipeline identified and queried), but the cause is not matched because no failed run was found and reported. The verdict 'failed job' was not confirmed in the delivered answer. The handoff is scored 2: next_checks names a specific query hash to retry, stopping_point is clear, and the query history provides a rerunnable trail, making it a solid handoff despite the unresolved outcome. Interpret the saved result with its actual scope and native semantics.

Intake:
```json
{
  "classified_issue_type": "DATA_LOOKS_OLD",
  "compared_with": {
    "kind": "NOTHING"
  },
  "description": "I noticed that the Billing Warehouse transformation pipeline shows a Failed status on its latest job-history run. Because of this, I'm concerned the Invoiced Amount figure on the Subscription Billing page may not be reflecting current data. Can you tell me what happened with that failed run and whether the numbers in this report are stale as a result? I'd like to understand the impact on the data before I share this report with the finance team.",
  "issue_type": "DATA_LOOKS_OLD",
  "measure_candidates": [
    {
      "id": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
      "name": "Invoiced Amount"
    }
  ],
  "page": "69271186d3ccfbba0cccf5a28033b28f779e8c46e00b6f45adad14d97507539e",
  "report": "44dc6baac12f79e0f4a1c4474c63bb2867262137212e4061f4ce0882c4a90257",
  "status": "READY",
  "version": "IntakeRequest/1",
  "visual": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b"
}
```

Target:
```json
{
  "layers": {
    "native:4aae8dbb1d373ebef783": {
      "dialect": "DAX",
      "label": "Subscription Billing"
    },
    "native:ac3ebe915b1cc00c45d7": {
      "dialect": "T-SQL",
      "label": "billing_bronze"
    },
    "native:bc3914e8dae9e68e7163": {
      "dialect": "T-SQL",
      "label": "billing_ops"
    },
    "native:db47aa505c8c14efec29": {
      "dialect": "T-SQL",
      "label": "billingapp"
    },
    "native:f87556d4485196602461": {
      "dialect": "T-SQL",
      "label": "billing_serving"
    }
  },
  "path": {
    "as_of": null,
    "declared_route_bridges": [
      {
        "column_bindings": [
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/invoice_id",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/invoice_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/account_id",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/account_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/plan_id",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/plan_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/invoice_date",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/invoice_date"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/status",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/status"
          }
        ],
        "confidence": "DECLARED",
        "definition_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/part/model.bim",
        "definition_hash": "7565c9db1f3083abd3e08cf3d16d74e0a8f93f5c6efd1119ef278dc5db152db1",
        "graph_nodes": [
          "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
          "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd"
        ],
        "literal_expression": "let database = Sql.Database(\"i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com\", \"406dcb89-0526-4f48-bb77-397d52471c89\") in database",
        "native_ownership": [],
        "partition_source": {
          "entityName": "invoice_activity",
          "expressionSource": "BillingServingSource",
          "schemaName": "gold",
          "type": "entity"
        },
        "physical_table": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
        "qualification": "Declared route only; value agreement and aligned snapshots are not implied.",
        "semantic_table": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing"
      }
    ],
    "edges": [
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "3a6ba8ce4d7efd8c326192d087b8dfb05c43ca5209cf86cf5fb79cdbd9e4534c",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "binding_kind": "DIRECTLAKE_ENTITY",
          "catalog_id": "406dcb89-0526-4f48-bb77-397d52471c89",
          "container_asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "container_binding": {
            "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "container_bindings": [
            {
              "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
              "observed_at": "2026-10-12T06:22:48.745954Z",
              "source": "STATIC_DEFINITION",
              "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
              "span": {
                "kind": "JSON_POINTER",
                "path": ""
              }
            }
          ],
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "entity": "invoice_activity",
          "expression_pointer": "/model/expressions/0",
          "expression_source": "BillingServingSource",
          "physical_definition": {
            "definition_hash": "b32a45a2bf55337bb1a7b5ad78602572341ad2b6ebb249dc7657a32d3fb9e876",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "schema": "gold",
          "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com"
        },
        "provenance": {
          "definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/part/model.bim",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/model/tables/5/partitions"
          }
        },
        "source": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "target": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "unknown": null,
        "valid_from": "2026-10-27T10:08:38.481811Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "5b1782b90d25ef08907c1313aa35b95c128b4ee89d888d8371860a27ea6d1804",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "completeness": "ROW_ONLY",
          "definition": {
            "bytes": 8289,
            "sha256": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c"
          },
          "model_definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "native_row_hash": "f46ed22f744430f4f9406a42a056fdac7f90072a2f613406dbf2866e92b476f0"
        },
        "provenance": {
          "definition_hash": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "ENGINE_DEPENDENCY",
          "source_id": "24dc7f097c6839881270308e2651f9937a44cdfcbaa0d58448f2364a4d6b8627",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/rows/21"
          }
        },
        "source": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "target": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "62f0613f9f6894eaf7b5e2c5047953bea360ce5bfb26ff07c9cc1e26a9b073ac",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a",
        "properties": {
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a"
        },
        "provenance": {
          "definition_hash": "c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db",
          "observed_at": "2026-10-13T17:34:44.997022Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a/part/definition%2Fpages%2Fc9b267726b645332927d%2Fvisuals%2F788498de9a325c7bb6a9%2Fvisual.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/queryState/Values/projections/0/field/Measure"
          }
        },
        "source": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "target": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "unknown": null,
        "valid_from": "2026-10-13T17:34:44.997022Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "6a48e802bd984e9779fdd00a33e71b6841ab618cd095b9bcbcfdf73b2a654aae",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "completeness": "ROW_ONLY",
          "definition": {
            "bytes": 8289,
            "sha256": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c"
          },
          "model_definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "native_row_hash": "ad0462db0652c3ca7c3eb37d57ab7ff55057e3edc0d3374449f3517a4d07d6e5"
        },
        "provenance": {
          "definition_hash": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "ENGINE_DEPENDENCY",
          "source_id": "24dc7f097c6839881270308e2651f9937a44cdfcbaa0d58448f2364a4d6b8627",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/rows/20"
          }
        },
        "source": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "target": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "d8908c0765aacbfb72890a1818efd03f1efd4d224259f81635ba81fa609075dc",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "binding_kind": "DIRECTLAKE_ENTITY",
          "catalog_id": "406dcb89-0526-4f48-bb77-397d52471c89",
          "container_asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "container_binding": {
            "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "container_bindings": [
            {
              "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
              "observed_at": "2026-10-12T06:22:48.745954Z",
              "source": "STATIC_DEFINITION",
              "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
              "span": {
                "kind": "JSON_POINTER",
                "path": ""
              }
            }
          ],
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "entity": "invoice_activity",
          "expression_pointer": "/model/expressions/0",
          "expression_source": "BillingServingSource",
          "physical_column_definition": {
            "definition_hash": "e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d",
            "observed_at": "2026-10-13T17:41:15.000678Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "physical_definition": {
            "definition_hash": "b32a45a2bf55337bb1a7b5ad78602572341ad2b6ebb249dc7657a32d3fb9e876",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "schema": "gold",
          "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com",
          "source_column": "amount"
        },
        "provenance": {
          "definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/part/model.bim",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/model/tables/5/columns/4/sourceColumn"
          }
        },
        "source": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "target": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "unknown": null,
        "valid_from": "2026-10-27T10:08:38.481811Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "6042ff3c9dfb5abdf8c92b18f134b7e2be824412f423aa110475bf6b076cb4ad",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e"
        },
        "provenance": {
          "definition_hash": "6a8b2cf63f4dd89c731612162da50b38507fbc9120d3b5d88507d8c0653ab6cf",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/9/text"
          }
        },
        "source": "cd24018f200d886024efd549c6a79f2cc38fd8665b0337f3d4b5c3d391788c22",
        "target": "5824559a10e087711ceb49661818923333c1c87efa9ed0a2c80433e8f7f8c654",
        "unknown": null,
        "valid_from": "2026-10-13T07:41:50.583455Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "68a96a39b4f2f455ef383009526418b8fff04c3eb8d00a148a01b989068b86a1",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e",
        "properties": {
          "basis": "EXACT_SCRIPT_DATABASE_AND_TABLE",
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e",
          "execution_established": false
        },
        "provenance": {
          "definition_hash": "6a8b2cf63f4dd89c731612162da50b38507fbc9120d3b5d88507d8c0653ab6cf",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/9/text"
          }
        },
        "source": "5824559a10e087711ceb49661818923333c1c87efa9ed0a2c80433e8f7f8c654",
        "target": "072efb563a80031fb6ed6773a44b89662672682c6b0a16ef8c309b8e477485fb",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "7aaa34af4c1bad7ccfc7ce3f765a2d4843fae4616ddeac1bd97374180f1cb8a9",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba",
        "properties": {
          "basis": "EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS",
          "connection_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/connection/93fd5fbf-5835-4756-bc59-bbf07302f321",
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0",
          "destination_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba/table/invoices",
          "native_destination": {
            "artifactId": "1853cbbb-06d1-4ae9-b378-370007c574ba",
            "workspaceId": "7d67bb36-04f6-4182-95aa-da5d515248fa"
          },
          "source_asset": "sql://sql-orderops-9696025.database.windows.net/billingapp/object/1941581955",
          "source_query": "SELECT [invoice_id],[account_id],[invoice_date],[amount],[status],CAST(source_row_version AS bigint) AS source_row_version,source_modified_at_utc FROM [app].[invoices]"
        },
        "provenance": {
          "definition_hash": "0389f86a2811c8e11ae84891984d39ea93e5a9fb631135b78d38b22c42b3574c",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/4"
          }
        },
        "source": "072efb563a80031fb6ed6773a44b89662672682c6b0a16ef8c309b8e477485fb",
        "target": "5fd69c1b5817645bf256c653c3a6fdfb060ba4f6cd3b35c7f56324a93e5e9ad4",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "7c9ceae9e132e23285f38c8c42b36b40efb0edd02bdc646b1d6d852abf5d992b",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9"
        },
        "provenance": {
          "definition_hash": "b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/7/text"
          }
        },
        "source": "cd24018f200d886024efd549c6a79f2cc38fd8665b0337f3d4b5c3d391788c22",
        "target": "18e99db0461c73d0ab6adfdd91203ddfa934583167f2a525f0f33f54cfa5b780",
        "unknown": null,
        "valid_from": "2026-10-13T07:41:50.583455Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "9d47086709abdedd0e7709cb370976f363b0befdb19e7af7ba7005b63d4c162b",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0",
        "properties": {
          "basis": "EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS",
          "connection_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/connection/93fd5fbf-5835-4756-bc59-bbf07302f321",
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0",
          "destination_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba/table/invoices",
          "native_destination": {
            "artifactId": "1853cbbb-06d1-4ae9-b378-370007c574ba",
            "workspaceId": "7d67bb36-04f6-4182-95aa-da5d515248fa"
          },
          "source_asset": "sql://sql-orderops-9696025.database.windows.net/billingapp/object/1941581955",
          "source_query": "SELECT [invoice_id],[account_id],[invoice_date],[amount],[status],CAST(source_row_version AS bigint) AS source_row_version,source_modified_at_utc FROM [app].[invoices]"
        },
        "provenance": {
          "definition_hash": "0389f86a2811c8e11ae84891984d39ea93e5a9fb631135b78d38b22c42b3574c",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/4"
          }
        },
        "source": "5fd69c1b5817645bf256c653c3a6fdfb060ba4f6cd3b35c7f56324a93e5e9ad4",
        "target": "564adac92668939502d6e329320c18788ae803227e5ba70fa31a65e501f9612e",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "acaa3c15195e3d45419cf863e36b0b0e599c85db8769685c4f4a86baa6590234",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9",
        "properties": {
          "basis": "EXACT_SCRIPT_DATABASE_AND_TABLE",
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9",
          "execution_established": false
        },
        "provenance": {
          "definition_hash": "b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/7/text"
          }
        },
        "source": "18e99db0461c73d0ab6adfdd91203ddfa934583167f2a525f0f33f54cfa5b780",
        "target": "072efb563a80031fb6ed6773a44b89662672682c6b0a16ef8c309b8e477485fb",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      }
    ],
    "estate": "billing",
    "nodes": [
      {
        "confidence": "DECLARED",
        "id": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "kind": "COLUMN",
        "label": "amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
          "definition": {
            "bytes": 249,
            "sha256": "e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "hidden": null,
          "native_kind": "WarehouseColumn"
        },
        "provenance": {
          "definition_hash": "e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d",
          "observed_at": "2026-10-13T17:41:15.000678Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:41:15.000678Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "kind": "COLUMN",
        "label": "amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount",
          "dataType": "int64",
          "definition": {
            "bytes": 88,
            "sha256": "b1f9170e2c11581cbb5f36f01e51d440deff9cc017c473c9a2e93af6501741f5",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/b1f9170e2c11581cbb5f36f01e51d440deff9cc017c473c9a2e93af6501741f5"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "hidden": null,
          "native_kind": "SemanticColumn",
          "sourceColumn": "amount"
        },
        "provenance": {
          "definition_hash": "b1f9170e2c11581cbb5f36f01e51d440deff9cc017c473c9a2e93af6501741f5",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "kind": "TABLE",
        "label": "Billing",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing",
          "definition": {
            "bytes": 1459,
            "sha256": "6b0f856158e5e4207753b23208cf3d6770986030db7b78d0e8f3434b54cc7177",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/6b0f856158e5e4207753b23208cf3d6770986030db7b78d0e8f3434b54cc7177"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "hidden": null,
          "native_kind": "SemanticTable"
        },
        "provenance": {
          "definition_hash": "6b0f856158e5e4207753b23208cf3d6770986030db7b78d0e8f3434b54cc7177",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "kind": "VISUAL",
        "label": "Invoiced Amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a/visual/definition%2Fpages%2Fc9b267726b645332927d%2Fvisuals%2F788498de9a325c7bb6a9%2Fvisual.json",
          "definition": {
            "bytes": 1360,
            "sha256": "c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a",
          "hidden": null,
          "native_kind": "ReportVisual"
        },
        "provenance": {
          "definition_hash": "c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db",
          "observed_at": "2026-10-13T17:34:44.997022Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a/part/definition%2Fpages%2Fc9b267726b645332927d%2Fvisuals%2F788498de9a325c7bb6a9%2Fvisual.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-24T08:27:13.767574Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "kind": "MEASURE",
        "label": "Invoiced Amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/measures/Invoiced%20Amount",
          "definition": {
            "bytes": 65,
            "sha256": "a26b55b6f4cb71659087dca20a9ec79fed75dc019546cf877c8da04323a8f13d",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/a26b55b6f4cb71659087dca20a9ec79fed75dc019546cf877c8da04323a8f13d"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "hidden": null,
          "native_kind": "Measure"
        },
        "provenance": {
          "definition_hash": "a26b55b6f4cb71659087dca20a9ec79fed75dc019546cf877c8da04323a8f13d",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/measures/Invoiced%20Amount",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "id": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "kind": "TABLE",
        "label": "gold.invoice_activity",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
          "definition_source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity"
        }
      },
      {
        "id": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
        "kind": "MODEL",
        "label": "Subscription Billing",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "definition_source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "072efb563a80031fb6ed6773a44b89662672682c6b0a16ef8c309b8e477485fb",
        "kind": "TABLE",
        "label": "invoices",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba/table/invoices",
          "definition": {
            "bytes": 2325,
            "sha256": "ab15c7afa25e113c01bfb1da86109ba2d05b7e565b1febe526d3bbe5c4fa9aa6",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/ab15c7afa25e113c01bfb1da86109ba2d05b7e565b1febe526d3bbe5c4fa9aa6"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba",
          "hidden": null,
          "native_kind": "LakehouseTable",
          "retained_metadata_hash_encoding": "SORTED_JSON_COMPACT_LEGACY"
        },
        "provenance": {
          "definition_hash": "ab15c7afa25e113c01bfb1da86109ba2d05b7e565b1febe526d3bbe5c4fa9aa6",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba/table/invoices",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-12T06:22:48.745954Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "18e99db0461c73d0ab6adfdd91203ddfa934583167f2a525f0f33f54cfa5b780",
        "kind": "QUERY_STEP",
        "label": "Declared SQL script",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9",
        "properties": {
          "definition": {
            "bytes": 7287,
            "sha256": "b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9",
          "execution_established": false,
          "expression": "CREATE VIEW [bronze].[invoices] AS SELECT [invoice_id],[account_id],[invoice_date],[amount],[status],source_row_version,source_modified_at_utc FROM [billing_bronze].[dbo].[invoices];",
          "language": "TSQL"
        },
        "provenance": {
          "definition_hash": "b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/7/text"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T07:41:50.583455Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "564adac92668939502d6e329320c18788ae803227e5ba70fa31a65e501f9612e",
        "kind": "TABLE",
        "label": "app.invoices",
        "owner": "sql://sql-orderops-9696025.database.windows.net/billingapp",
        "properties": {
          "asset_id": "sql://sql-orderops-9696025.database.windows.net/billingapp/object/1941581955",
          "definition": {
            "bytes": 1936,
            "sha256": "3a9f9060f6d5dd82a343bf33e2a8677046c0fecdac24025dc111a10fbbf8d3a7",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/3a9f9060f6d5dd82a343bf33e2a8677046c0fecdac24025dc111a10fbbf8d3a7"
          },
          "definition_source_owner": "sql://sql-orderops-9696025.database.windows.net/billingapp",
          "hidden": null,
          "native_kind": "SqlObject",
          "retained_metadata_hash_encoding": "SORTED_JSON_SPACED",
          "source_system_object": true
        },
        "provenance": {
          "definition_hash": "3a9f9060f6d5dd82a343bf33e2a8677046c0fecdac24025dc111a10fbbf8d3a7",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "sql://sql-orderops-9696025.database.windows.net/billingapp/object/1941581955",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "5824559a10e087711ceb49661818923333c1c87efa9ed0a2c80433e8f7f8c654",
        "kind": "QUERY_STEP",
        "label": "Declared SQL script",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e",
        "properties": {
          "definition": {
            "bytes": 7645,
            "sha256": "6a8b2cf63f4dd89c731612162da50b38507fbc9120d3b5d88507d8c0653ab6cf",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/6a8b2cf63f4dd89c731612162da50b38507fbc9120d3b5d88507d8c0653ab6cf"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e",
          "execution_established": false,
          "expression": "CREATE VIEW [bronze].[invoices] AS SELECT [invoice_id],[account_id],[invoice_date],[amount],[status],source_row_version,source_modified_at_utc FROM [billing_bronze].[dbo].[invoices];",
          "language": "TSQL"
        },
        "provenance": {
          "definition_hash": "6a8b2cf63f4dd89c731612162da50b38507fbc9120d3b5d88507d8c0653ab6cf",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/9/text"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T07:41:50.583455Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "5fd69c1b5817645bf256c653c3a6fdfb060ba4f6cd3b35c7f56324a93e5e9ad4",
        "kind": "COPY_ACTIVITY",
        "label": "Copy_invoices",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0",
        "properties": {
          "activity_type": "Copy",
          "definition": {
            "bytes": 21384,
            "sha256": "0389f86a2811c8e11ae84891984d39ea93e5a9fb631135b78d38b22c42b3574c",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/0389f86a2811c8e11ae84891984d39ea93e5a9fb631135b78d38b22c42b3574c"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0",
          "native_copy_binding": {
            "basis": "EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS",
            "connection_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/connection/93fd5fbf-5835-4756-bc59-bbf07302f321",
            "destination_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba/table/invoices",
            "native_destination": {
              "artifactId": "1853cbbb-06d1-4ae9-b378-370007c574ba",
              "workspaceId": "7d67bb36-04f6-4182-95aa-da5d515248fa"
            },
            "source_asset": "sql://sql-orderops-9696025.database.windows.net/billingapp/object/1941581955",
            "source_query": "SELECT [invoice_id],[account_id],[invoice_date],[amount],[status],CAST(source_row_version AS bigint) AS source_row_version,source_modified_at_utc FROM [app].[invoices]"
          }
        },
        "provenance": {
          "definition_hash": "0389f86a2811c8e11ae84891984d39ea93e5a9fb631135b78d38b22c42b3574c",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/4"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "cd24018f200d886024efd549c6a79f2cc38fd8665b0337f3d4b5c3d391788c22",
        "kind": "VIEW",
        "label": "bronze.invoices",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "definition": {
            "bytes": 7287,
            "sha256": "b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9",
          "execution_established": false,
          "schema_evidence": "CODE_DECLARED_NOT_OBSERVED",
          "script_database": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "script_name": "bronze.invoices"
        },
        "provenance": {
          "definition_hash": "b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/7/text"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T07:41:50.583455Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "56132b6a75761fcbacab05eb8d140b68e0c5ebbdc195e993a772d1f464db1463",
        "kind": "TABLE",
        "label": "dbo.load_run_audit",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/9cd1829b-7e2e-4340-8f59-fdf996033198",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/9cd1829b-7e2e-4340-8f59-fdf996033198/table/dbo.load_run_audit",
          "definition": {
            "bytes": 1402,
            "sha256": "e980b97b290eade70d549961586aa27e43aa5e199de1ec36021cf92a5533568c",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/e980b97b290eade70d549961586aa27e43aa5e199de1ec36021cf92a5533568c"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/9cd1829b-7e2e-4340-8f59-fdf996033198",
          "hidden": null,
          "native_kind": "WarehouseTable",
          "retained_metadata_hash_encoding": "SORTED_JSON_SPACED"
        },
        "provenance": {
          "definition_hash": "e980b97b290eade70d549961586aa27e43aa5e199de1ec36021cf92a5533568c",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/9cd1829b-7e2e-4340-8f59-fdf996033198/table/dbo.load_run_audit",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-12T06:22:48.745954Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      }
    ],
    "stops": [
      {
        "node": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "reason": "No retained upstream dependency is declared for this object."
      },
      {
        "node": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "reason": "No retained upstream dependency is declared for this object."
      }
    ],
    "truncated": false,
    "unavailable_owners": {
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89": {
        "at": "2026-10-28T06:03:11.630566Z",
        "failure": {
          "errno": null,
          "error_type": "RuntimeError",
          "line": 88,
          "message": "GRAPH_DEFINITION_KIND_UNAVAILABLE",
          "message_redacted": false,
          "module": "graph_change_collector.py"
        },
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "status": "UNAVAILABLE"
      },
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188": {
        "at": "2026-10-28T06:03:20.599000Z",
        "failure": {
          "errno": null,
          "error_type": "MetadataUnavailable",
          "http_status": 404,
          "line": 106,
          "message": "Metadata provider request unavailable",
          "message_redacted": false,
          "module": "metadata_auth.py",
          "provider_code": "EntityNotFound"
        },
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "status": "UNAVAILABLE"
      },
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a": {
        "at": "2026-10-28T06:03:23.952432Z",
        "failure": {
          "errno": null,
          "error_type": "MetadataUnavailable",
          "http_status": 404,
          "line": 106,
          "message": "Metadata provider request unavailable",
          "message_redacted": false,
          "module": "metadata_auth.py",
          "provider_code": "EntityNotFound"
        },
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "status": "UNAVAILABLE"
      }
    }
  }
}
```

Triage:
```json
{
  "facts": [
    {
      "cached": false,
      "check": "MODEL_REFRESH",
      "observed_at": "2026-10-28T06:21:43.643661Z",
      "source": "facts-ledger",
      "state": "OBSERVED_NEGATIVE",
      "value": [
        {
          "collected_at": "2026-10-28T06:21:43.643661Z",
          "freshness": "CURRENT",
          "id": "65fd28349e41df4f2669d89da23dd1de597e5fd5a2db9b05aa481c3c0eeefd78",
          "kind": "RUN_HISTORY",
          "observed_at": "2026-10-28T06:21:43.643661Z",
          "provenance": {
            "collector": "microsoft-runtime:8b8add39b1b3bbf05051200684642bc68ee0c9695580165440fd17fca6875167",
            "evidence_ids": [
              "sha256:5518e69e59a63ae9599830ab0ea2552a1c16ca90d74383d71cc10ca34d69ac77"
            ],
            "locator": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED_NEGATIVE",
          "subject": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
          "value": {
            "listing_complete": true,
            "runs": []
          }
        }
      ]
    },
    {
      "cached": false,
      "check": "REFRESH_SCHEDULE",
      "observed_at": "2026-10-28T06:21:43.643661Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T06:21:43.643661Z",
          "freshness": "CURRENT",
          "id": "bf606243fbce354e0c2b91ac6a1f0b6715f84ac09d309b0fab4a9b9e200e6036",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T06:21:43.643661Z",
          "provenance": {
            "collector": "microsoft-runtime:8b8add39b1b3bbf05051200684642bc68ee0c9695580165440fd17fca6875167",
            "evidence_ids": [
              "sha256:82b1cbfbfff465c33982765807dc9f50a201edeba662730817051b285b134874"
            ],
            "locator": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/7d67bb36-04f6-4182-95aa-da5d515248fa/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "19:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        }
      ]
    },
    {
      "check": "AUTOMATIC_UPDATES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:AUTOMATIC_UPDATES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "JOB_RUNS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:JOB_RUNS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "LAYER_FRESHNESS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:LAYER_FRESHNESS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SOURCE_CHANGES",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:SOURCE_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "NEXT_LOAD",
      "observed_at": "2026-10-28T06:21:43.643661Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T06:21:43.643661Z",
          "freshness": "CURRENT",
          "id": "bf606243fbce354e0c2b91ac6a1f0b6715f84ac09d309b0fab4a9b9e200e6036",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T06:21:43.643661Z",
          "provenance": {
            "collector": "microsoft-runtime:8b8add39b1b3bbf05051200684642bc68ee0c9695580165440fd17fca6875167",
            "evidence_ids": [
              "sha256:82b1cbfbfff465c33982765807dc9f50a201edeba662730817051b285b134874"
            ],
            "locator": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/7d67bb36-04f6-4182-95aa-da5d515248fa/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "19:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        }
      ]
    },
    {
      "check": "CONNECTION_MODE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:CONNECTION_MODE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SECURITY_PRESENCE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:SECURITY_PRESENCE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "DEFINITION_CHANGES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:DEFINITION_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    }
  ],
  "path": [
    "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
    "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
    "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
    "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
    "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
    "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
    "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1"
  ],
  "refresh_operations": 10,
  "what_triage_suggests": "Triage has unavailable checks (AUTOMATIC_UPDATES, JOB_RUNS, LAYER_FRESHNESS, SOURCE_CHANGES, CONNECTION_MODE, SECURITY_PRESENCE, DEFINITION_CHANGES); this does not establish that those mechanisms are absent."
}
```

Tool decisions:
```json
[
  {
    "arguments": {
      "layer": "native:4aae8dbb1d373ebef783",
      "purpose": "recreate",
      "query": "EVALUATE ROW(\"Invoiced Amount\", [Invoiced Amount], \"rows\", COUNTROWS(Billing), \"max_invoice_date\", MAX(Billing[invoice_date]))"
    },
    "tool": "run_dax",
    "tool_use_id": "toolu_018eEBfyL3GTXsNNDEg4GgNo",
    "turn": 1
  },
  {
    "arguments": {
      "layer": "native:f87556d4485196602461",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, COUNT(*) AS rows_observed, MAX([invoice_date]) AS max_invoice_date FROM [gold].[invoice_activity]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01DghjiwDKdwbvo9cpDNyvbn",
    "turn": 1
  },
  {
    "arguments": {
      "node": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
    },
    "tool": "get_refresh_history",
    "tool_use_id": "toolu_016hRdACPbEsfTxaKGb1hsoK",
    "turn": 1
  },
  {
    "arguments": {
      "node": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
      "operation": "PRODUCERS"
    },
    "tool": "get_lineage",
    "tool_use_id": "toolu_01SqqH9p3vzq51f4SaaEvXpc",
    "turn": 1
  },
  {
    "arguments": {
      "words": "billing warehouse transformation pipeline stored procedure invoice_activity bronze job history"
    },
    "tool": "list_candidates",
    "tool_use_id": "toolu_01Mduzd63BkcHFHs5CDUMN1p",
    "turn": 4
  },
  {
    "arguments": {
      "words": "invoices bronze invoice load procedure pipeline run"
    },
    "tool": "list_candidates",
    "tool_use_id": "toolu_01Lrddk4VDkJvQRVjJYprdBi",
    "turn": 7
  },
  {
    "arguments": {
      "layer": "native:f87556d4485196602461",
      "purpose": "lookup",
      "query": "SELECT TOP 20 s.name AS schema_name, o.name AS object_name, o.type_desc, o.modify_date FROM sys.objects o JOIN sys.schemas s ON s.schema_id = o.schema_id WHERE o.type IN ('P','V','U') ORDER BY o.modify_date DESC"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01Hkci1RMsEdJU7yArabYCdm",
    "turn": 7
  },
  {
    "arguments": {
      "node": "cd24018f200d886024efd549c6a79f2cc38fd8665b0337f3d4b5c3d391788c22",
      "operation": "PATH"
    },
    "tool": "get_lineage",
    "tool_use_id": "toolu_01CgPBESBJgjXFHS9goKxepZ",
    "turn": 10
  },
  {
    "arguments": {
      "node": "56132b6a75761fcbacab05eb8d140b68e0c5ebbdc195e993a772d1f464db1463",
      "operation": "PATH"
    },
    "tool": "get_lineage",
    "tool_use_id": "toolu_01FB8xpmQ3uaNjv487LZAbc8",
    "turn": 10
  },
  {
    "arguments": {
      "node": "cd24018f200d886024efd549c6a79f2cc38fd8665b0337f3d4b5c3d391788c22"
    },
    "tool": "get_definition",
    "tool_use_id": "toolu_01Vz45WgyRLocm4fuUdaCFJe",
    "turn": 10
  },
  {
    "arguments": {
      "node": "cd24018f200d886024efd549c6a79f2cc38fd8665b0337f3d4b5c3d391788c22"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_018KujiqTfEKrp8FjTE5g6kD",
    "turn": 13
  },
  {
    "arguments": {
      "layer": "native:bc3914e8dae9e68e7163",
      "purpose": "history",
      "query": "SELECT TOP 20 run_id, pipeline_name, status, rows_read, rows_written, accounting_state, start_time_utc, end_time_utc, high_watermark FROM dbo.load_run_audit ORDER BY start_time_utc DESC"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_014vMCvhLQ6Jth2Fsdh1AK9Y",
    "turn": 13
  },
  {
    "arguments": {
      "layer": "native:ac3ebe915b1cc00c45d7",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, COUNT(*) AS rows_observed, MAX([invoice_date]) AS max_invoice_date, MAX([source_modified_at_utc]) AS max_modified FROM [dbo].[invoices]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01WktJC5R8m6BoaYS4Rk8QyZ",
    "turn": 13
  },
  {
    "arguments": {
      "layer": "native:db47aa505c8c14efec29",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, COUNT(*) AS rows_observed, MAX([invoice_date]) AS max_invoice_date, MAX([source_modified_at_utc]) AS max_modified FROM [app].[invoices]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_011bTXNjfvHCARJQ1ZWMZuSW",
    "turn": 13
  },
  {
    "arguments": {
      "node": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_012dHrS6HbTUCagnbE3yv5Lk",
    "turn": 16
  }
]
```

Queries:
```json
[
  {
    "asset_ids": [
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing",
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/invoice_date",
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/measures/Invoiced%20Amount"
    ],
    "duration_seconds": 11.482870622000064,
    "executed_text": "EVALUATE TOPN(251,ROW(\"Invoiced Amount\",[Invoiced Amount],\"rows\",COUNTROWS(Billing),\"max_invoice_date\",MAX(Billing[invoice_date])))",
    "id": "query:af218d97b40a5fa42330fb33dab6ecb3feb73968404870ad81f458d338248199:1",
    "layer": "native:4aae8dbb1d373ebef783",
    "parameters": [],
    "purpose": "recreate",
    "result": {
      "rows": [
        {
          "[Invoiced Amount]": 950,
          "[max_invoice_date]": "2026-10-01T00:00:00",
          "[rows]": 5
        }
      ],
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "768c09ce7732d94e86a1cb7b15cfaca800790def6ed32f5e8a21996794489f75",
    "row_count": 1,
    "signature": "af218d97b40a5fa42330fb33dab6ecb3feb73968404870ad81f458d338248199",
    "status": "SUCCEEDED",
    "text": "EVALUATE ROW(\"Invoiced Amount\", [Invoiced Amount], \"rows\", COUNTROWS(Billing), \"max_invoice_date\", MAX(Billing[invoice_date]))",
    "time": "2026-10-28T06:21:57.633301+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity"
    ],
    "duration_seconds": 8.618429688999981,
    "executed_text": "SELECT TOP 251 SUM(CAST([invoice_activity].[amount] AS BIGINT)) AS [invoiced_amount], COUNT(*) AS [rows_observed], MAX([invoice_activity].[invoice_date]) AS [max_invoice_date] FROM [gold].[invoice_activity] AS [invoice_activity]",
    "id": "query:eb0a6a56597dd8f881f57a31589ffd5bcf8e91fb244fee5ffdb6a400bb2825f6:2",
    "layer": "native:f87556d4485196602461",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "invoiced_amount": "Int64",
        "max_invoice_date": "DateTime",
        "rows_observed": "Int64"
      },
      "execution_identity": {
        "database": "billing_serving",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "invoiced_amount": "950",
          "max_invoice_date": "2026-10-01",
          "rows_observed": "5"
        }
      ]
    },
    "result_digest": "9bd1e64a4f8477fb9245c7757b56cbe2b1f0b48b252d208dd3dea7392b4641d7",
    "row_count": 1,
    "signature": "eb0a6a56597dd8f881f57a31589ffd5bcf8e91fb244fee5ffdb6a400bb2825f6",
    "status": "SUCCEEDED",
    "text": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, COUNT(*) AS rows_observed, MAX([invoice_date]) AS max_invoice_date FROM [gold].[invoice_activity]",
    "time": "2026-10-28T06:22:09.369952+00:00",
    "truncated": false
  },
  {
    "duration_seconds": 0,
    "error": "SQL object unavailable or view dependencies not validated",
    "error_type": "QueryRejection",
    "failure_class": "wrong column or table",
    "id": "query:82ba092806fe06c9d423feb229d34b5969876832f61b5a818cb23b50eb49ea54:3",
    "layer": "native:f87556d4485196602461",
    "native_dispatched": false,
    "purpose": "lookup",
    "result_digest": null,
    "row_count": null,
    "schema_slice": [
      {
        "columns": [
          {
            "collation_name": null,
            "data_type": "int",
            "name": "invoice_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "account_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "plan_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "date",
            "name": "invoice_date",
            "observed_type": "date"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "amount",
            "observed_type": "int"
          },
          {
            "collation_name": "Latin1_General_100_BIN2_UTF8",
            "data_type": "varchar",
            "name": "status",
            "observed_type": "varchar"
          }
        ],
        "id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
        "name": "invoice_activity",
        "schema_name": "gold",
        "type_desc": "USER_TABLE"
      }
    ],
    "signature": "82ba092806fe06c9d423feb229d34b5969876832f61b5a818cb23b50eb49ea54",
    "status": "ERROR",
    "text": "SELECT TOP 20 s.name AS schema_name, o.name AS object_name, o.type_desc, o.modify_date FROM sys.objects o JOIN sys.schemas s ON s.schema_id = o.schema_id WHERE o.type IN ('P','V','U') ORDER BY o.modify_date DESC",
    "time": "2026-10-28T06:22:35.299499+00:00"
  },
  {
    "asset_ids": [
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/9cd1829b-7e2e-4340-8f59-fdf996033198/table/dbo.load_run_audit"
    ],
    "duration_seconds": 16.039217263999944,
    "executed_text": "SELECT TOP 20 [load_run_audit].[run_id] AS [run_id], [load_run_audit].[pipeline_name] AS [pipeline_name], [load_run_audit].[status] AS [status], [load_run_audit].[rows_read] AS [rows_read], [load_run_audit].[rows_written] AS [rows_written], [load_run_audit].[accounting_state] AS [accounting_state], [load_run_audit].[start_time_utc] AS [start_time_utc], [load_run_audit].[end_time_utc] AS [end_time_utc], [load_run_audit].[high_watermark] AS [high_watermark] FROM [dbo].[load_run_audit] AS [load_run_audit] ORDER BY [start_time_utc] DESC",
    "id": "query:89a3fff720af43d3727a83b3fd069c4e36dc0eff46e6cfd1cefc241f8c3e2173:4",
    "layer": "native:bc3914e8dae9e68e7163",
    "parameters": [],
    "purpose": "history",
    "result": {
      "column_types": {
        "accounting_state": "String",
        "end_time_utc": "String",
        "high_watermark": "String",
        "pipeline_name": "String",
        "rows_read": "Int64",
        "rows_written": "Int64",
        "run_id": "String",
        "start_time_utc": "String",
        "status": "String"
      },
      "execution_identity": {
        "database": "billing_ops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "accounting_state": "OBSERVED_COPY_OUTPUT",
          "end_time_utc": "2026-10-09T21:54:56.6775595",
          "high_watermark": null,
          "pipeline_name": "fc8438fd-2c18-4196-9191-33e26481e2e0",
          "rows_read": "26",
          "rows_written": "26",
          "run_id": "e82f690b-6865-48b5-a38c-9a116cd9c132",
          "start_time_utc": "2026-10-09T21:51:03.1830083Z",
          "status": "Succeeded"
        }
      ]
    },
    "result_digest": "3bc8ab902f07870146ce8ca1030281b9c1b0d1d7b31de7331702fd87eb951559",
    "row_count": 1,
    "signature": "89a3fff720af43d3727a83b3fd069c4e36dc0eff46e6cfd1cefc241f8c3e2173",
    "status": "SUCCEEDED",
    "text": "SELECT TOP 20 run_id, pipeline_name, status, rows_read, rows_written, accounting_state, start_time_utc, end_time_utc, high_watermark FROM dbo.load_run_audit ORDER BY start_time_utc DESC",
    "time": "2026-10-28T06:23:17.141150+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba/table/invoices"
    ],
    "duration_seconds": 12.495990182000014,
    "executed_text": "SELECT TOP 251 SUM(CAST([invoices].[amount] AS BIGINT)) AS [invoiced_amount], COUNT(*) AS [rows_observed], MAX([invoices].[invoice_date]) AS [max_invoice_date], MAX([invoices].[source_modified_at_utc]) AS [max_modified] FROM [dbo].[invoices] AS [invoices]",
    "id": "query:a0003b4ea20aa9bf2035a3a69a6e8866c2e49a503043f6d437206b4b34b9d3ca:5",
    "layer": "native:ac3ebe915b1cc00c45d7",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "invoiced_amount": "Int64",
        "max_invoice_date": "DateTime",
        "max_modified": "DateTime",
        "rows_observed": "Int64"
      },
      "execution_identity": {
        "database": "billing_bronze",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "invoiced_amount": "700",
          "max_invoice_date": "2026-10-01",
          "max_modified": "2026-10-09 21:42:24.128711",
          "rows_observed": "4"
        }
      ]
    },
    "result_digest": "cbe01cb0338cc410b7a3fd52e2435e0a392671fd2622b6877473de31231d01cf",
    "row_count": 1,
    "signature": "a0003b4ea20aa9bf2035a3a69a6e8866c2e49a503043f6d437206b4b34b9d3ca",
    "status": "SUCCEEDED",
    "text": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, COUNT(*) AS rows_observed, MAX([invoice_date]) AS max_invoice_date, MAX([source_modified_at_utc]) AS max_modified FROM [dbo].[invoices]",
    "time": "2026-10-28T06:23:33.562782+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/billingapp/object/1941581955"
    ],
    "duration_seconds": 3.1794493909999346,
    "executed_text": "SELECT TOP 251 SUM(CAST([invoices].[amount] AS BIGINT)) AS [invoiced_amount], COUNT(*) AS [rows_observed], MAX([invoices].[invoice_date]) AS [max_invoice_date], MAX([invoices].[source_modified_at_utc]) AS [max_modified] FROM [app].[invoices] AS [invoices]",
    "id": "query:0d13e699ed49e6f09872497c31b76b96a8436c203b5fd5dccb5d1ba78bed5002:6",
    "layer": "native:db47aa505c8c14efec29",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "invoiced_amount": "Int64",
        "max_invoice_date": "DateTime",
        "max_modified": "DateTime",
        "rows_observed": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T06:23:49.343472+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T06:23:46.643843+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "billingapp",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "invoiced_amount": "700",
          "max_invoice_date": "2026-10-01",
          "max_modified": "2026-10-09 21:42:24.128711",
          "rows_observed": "4"
        }
      ]
    },
    "result_digest": "2fed1e78ac4875f097bfcbacb4bcc533fa104e72116dc79d524daf3b39af62be",
    "row_count": 1,
    "signature": "0d13e699ed49e6f09872497c31b76b96a8436c203b5fd5dccb5d1ba78bed5002",
    "status": "SUCCEEDED",
    "text": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, COUNT(*) AS rows_observed, MAX([invoice_date]) AS max_invoice_date, MAX([source_modified_at_utc]) AS max_modified FROM [app].[invoices]",
    "time": "2026-10-28T06:23:46.436400+00:00",
    "truncated": false
  }
]
```

Final answer:
```json
"The checks did not establish a cause within this ticket’s limits."
```

Sealed expected:
```json
{
  "case_id": "v2-failed-billing-transform",
  "cause": "Latest failed native transform run with name/run ID/start/end/error; no invented successful completion.",
  "estate": "billing",
  "expectation_basis": "Practice source literals, declared definitions and reversible scenario plan; never an engine answer.",
  "fixture": "failed-billing",
  "id": "v2-failed-billing-transform-v1",
  "layer": "billing transformation pipeline",
  "split": "DEV",
  "variation": "detailed support question",
  "verdict": "failed job"
}
```

Saved checkpoint SHA-256: f5dda9f77f33795cf942922f2724e333b0e3c9761a4a41e38c710f5931cd280d. Only recorded tool choices are shown; no new queries or model calls.

### v2-failed-billing-transform-v2
Expected verdict: 'failed job' at layer 'billing transformation pipeline / DEV split', with the cause being the latest failed native transform run (name, run ID, start, end, error). The delivered answer is UNRESOLVED with stopping reason TOOL_OR_TIME_LIMIT. It never established the failed job as the cause; triage showed no run history (MODEL_REFRESH check returned OBSERVED_NEGATIVE with an empty runs list), and subsequent SQL probes of silver.invoices and bronze.invoices both failed with 'SQL object unavailable or view dependencies not validated'. The agent correctly identified the data matches between the DAX semantic model and the SQL warehouse (both showing 950, max_invoice_date 2026-10-01, 5 rows) but never found the failed pipeline run or its details. Verdict does not match (UNRESOLVED vs 'failed job'), layer does not match (no pipeline layer confirmed), cause does not match (no failed run identified). The honest unresolved answer is not harmful. Handoff quality is 2: the next_checks list is specific and rerunnable, the stopping point is clear (TOOL_OR_TIME_LIMIT), and the schema slice from gold.invoice_activity is preserved for the next investigator. Use the returned native error and schema to correct this read before concluding.

Intake:
```json
{
  "classified_issue_type": "DATA_LOOKS_OLD",
  "compared_with": {
    "kind": "NOTHING"
  },
  "description": "The Billing Warehouse transformation job shows Failed on the latest run. Is the Invoiced Amount on the Subscription Billing page out of date because of this?",
  "issue_type": "DATA_LOOKS_OLD",
  "measure_candidates": [
    {
      "id": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
      "name": "Invoiced Amount"
    }
  ],
  "page": "69271186d3ccfbba0cccf5a28033b28f779e8c46e00b6f45adad14d97507539e",
  "report": "44dc6baac12f79e0f4a1c4474c63bb2867262137212e4061f4ce0882c4a90257",
  "status": "READY",
  "version": "IntakeRequest/1",
  "visual": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b"
}
```

Target:
```json
{
  "layers": {
    "native:4aae8dbb1d373ebef783": {
      "dialect": "DAX",
      "label": "Subscription Billing"
    },
    "native:f87556d4485196602461": {
      "dialect": "T-SQL",
      "label": "billing_serving"
    }
  },
  "path": {
    "as_of": null,
    "declared_route_bridges": [
      {
        "column_bindings": [
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/invoice_id",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/invoice_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/account_id",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/account_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/plan_id",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/plan_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/invoice_date",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/invoice_date"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/status",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/status"
          }
        ],
        "confidence": "DECLARED",
        "definition_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/part/model.bim",
        "definition_hash": "7565c9db1f3083abd3e08cf3d16d74e0a8f93f5c6efd1119ef278dc5db152db1",
        "graph_nodes": [
          "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
          "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd"
        ],
        "literal_expression": "let database = Sql.Database(\"i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com\", \"406dcb89-0526-4f48-bb77-397d52471c89\") in database",
        "native_ownership": [],
        "partition_source": {
          "entityName": "invoice_activity",
          "expressionSource": "BillingServingSource",
          "schemaName": "gold",
          "type": "entity"
        },
        "physical_table": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
        "qualification": "Declared route only; value agreement and aligned snapshots are not implied.",
        "semantic_table": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing"
      }
    ],
    "edges": [
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "3a6ba8ce4d7efd8c326192d087b8dfb05c43ca5209cf86cf5fb79cdbd9e4534c",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "binding_kind": "DIRECTLAKE_ENTITY",
          "catalog_id": "406dcb89-0526-4f48-bb77-397d52471c89",
          "container_asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "container_binding": {
            "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "container_bindings": [
            {
              "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
              "observed_at": "2026-10-12T06:22:48.745954Z",
              "source": "STATIC_DEFINITION",
              "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
              "span": {
                "kind": "JSON_POINTER",
                "path": ""
              }
            }
          ],
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "entity": "invoice_activity",
          "expression_pointer": "/model/expressions/0",
          "expression_source": "BillingServingSource",
          "physical_definition": {
            "definition_hash": "b32a45a2bf55337bb1a7b5ad78602572341ad2b6ebb249dc7657a32d3fb9e876",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "schema": "gold",
          "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com"
        },
        "provenance": {
          "definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/part/model.bim",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/model/tables/5/partitions"
          }
        },
        "source": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "target": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "unknown": null,
        "valid_from": "2026-10-27T10:08:38.481811Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "5b1782b90d25ef08907c1313aa35b95c128b4ee89d888d8371860a27ea6d1804",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "completeness": "ROW_ONLY",
          "definition": {
            "bytes": 8289,
            "sha256": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c"
          },
          "model_definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "native_row_hash": "f46ed22f744430f4f9406a42a056fdac7f90072a2f613406dbf2866e92b476f0"
        },
        "provenance": {
          "definition_hash": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "ENGINE_DEPENDENCY",
          "source_id": "24dc7f097c6839881270308e2651f9937a44cdfcbaa0d58448f2364a4d6b8627",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/rows/21"
          }
        },
        "source": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "target": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "62f0613f9f6894eaf7b5e2c5047953bea360ce5bfb26ff07c9cc1e26a9b073ac",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a",
        "properties": {
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a"
        },
        "provenance": {
          "definition_hash": "c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db",
          "observed_at": "2026-10-13T17:34:44.997022Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a/part/definition%2Fpages%2Fc9b267726b645332927d%2Fvisuals%2F788498de9a325c7bb6a9%2Fvisual.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/queryState/Values/projections/0/field/Measure"
          }
        },
        "source": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "target": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "unknown": null,
        "valid_from": "2026-10-13T17:34:44.997022Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "6a48e802bd984e9779fdd00a33e71b6841ab618cd095b9bcbcfdf73b2a654aae",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "completeness": "ROW_ONLY",
          "definition": {
            "bytes": 8289,
            "sha256": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c"
          },
          "model_definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "native_row_hash": "ad0462db0652c3ca7c3eb37d57ab7ff55057e3edc0d3374449f3517a4d07d6e5"
        },
        "provenance": {
          "definition_hash": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "ENGINE_DEPENDENCY",
          "source_id": "24dc7f097c6839881270308e2651f9937a44cdfcbaa0d58448f2364a4d6b8627",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/rows/20"
          }
        },
        "source": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "target": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "d8908c0765aacbfb72890a1818efd03f1efd4d224259f81635ba81fa609075dc",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "binding_kind": "DIRECTLAKE_ENTITY",
          "catalog_id": "406dcb89-0526-4f48-bb77-397d52471c89",
          "container_asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "container_binding": {
            "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "container_bindings": [
            {
              "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
              "observed_at": "2026-10-12T06:22:48.745954Z",
              "source": "STATIC_DEFINITION",
              "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
              "span": {
                "kind": "JSON_POINTER",
                "path": ""
              }
            }
          ],
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "entity": "invoice_activity",
          "expression_pointer": "/model/expressions/0",
          "expression_source": "BillingServingSource",
          "physical_column_definition": {
            "definition_hash": "e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d",
            "observed_at": "2026-10-13T17:41:15.000678Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "physical_definition": {
            "definition_hash": "b32a45a2bf55337bb1a7b5ad78602572341ad2b6ebb249dc7657a32d3fb9e876",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "schema": "gold",
          "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com",
          "source_column": "amount"
        },
        "provenance": {
          "definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/part/model.bim",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/model/tables/5/columns/4/sourceColumn"
          }
        },
        "source": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "target": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "unknown": null,
        "valid_from": "2026-10-27T10:08:38.481811Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      }
    ],
    "estate": "billing",
    "nodes": [
      {
        "confidence": "DECLARED",
        "id": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "kind": "COLUMN",
        "label": "amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
          "definition": {
            "bytes": 249,
            "sha256": "e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "hidden": null,
          "native_kind": "WarehouseColumn"
        },
        "provenance": {
          "definition_hash": "e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d",
          "observed_at": "2026-10-13T17:41:15.000678Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:41:15.000678Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "kind": "COLUMN",
        "label": "amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount",
          "dataType": "int64",
          "definition": {
            "bytes": 88,
            "sha256": "b1f9170e2c11581cbb5f36f01e51d440deff9cc017c473c9a2e93af6501741f5",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/b1f9170e2c11581cbb5f36f01e51d440deff9cc017c473c9a2e93af6501741f5"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "hidden": null,
          "native_kind": "SemanticColumn",
          "sourceColumn": "amount"
        },
        "provenance": {
          "definition_hash": "b1f9170e2c11581cbb5f36f01e51d440deff9cc017c473c9a2e93af6501741f5",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "kind": "TABLE",
        "label": "Billing",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing",
          "definition": {
            "bytes": 1459,
            "sha256": "6b0f856158e5e4207753b23208cf3d6770986030db7b78d0e8f3434b54cc7177",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/6b0f856158e5e4207753b23208cf3d6770986030db7b78d0e8f3434b54cc7177"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "hidden": null,
          "native_kind": "SemanticTable"
        },
        "provenance": {
          "definition_hash": "6b0f856158e5e4207753b23208cf3d6770986030db7b78d0e8f3434b54cc7177",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "kind": "VISUAL",
        "label": "Invoiced Amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a/visual/definition%2Fpages%2Fc9b267726b645332927d%2Fvisuals%2F788498de9a325c7bb6a9%2Fvisual.json",
          "definition": {
            "bytes": 1360,
            "sha256": "c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a",
          "hidden": null,
          "native_kind": "ReportVisual"
        },
        "provenance": {
          "definition_hash": "c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db",
          "observed_at": "2026-10-13T17:34:44.997022Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a/part/definition%2Fpages%2Fc9b267726b645332927d%2Fvisuals%2F788498de9a325c7bb6a9%2Fvisual.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-24T08:27:13.767574Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "kind": "MEASURE",
        "label": "Invoiced Amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/measures/Invoiced%20Amount",
          "definition": {
            "bytes": 65,
            "sha256": "a26b55b6f4cb71659087dca20a9ec79fed75dc019546cf877c8da04323a8f13d",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/a26b55b6f4cb71659087dca20a9ec79fed75dc019546cf877c8da04323a8f13d"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "hidden": null,
          "native_kind": "Measure"
        },
        "provenance": {
          "definition_hash": "a26b55b6f4cb71659087dca20a9ec79fed75dc019546cf877c8da04323a8f13d",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/measures/Invoiced%20Amount",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "id": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "kind": "TABLE",
        "label": "gold.invoice_activity",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
          "definition_source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity"
        }
      },
      {
        "id": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
        "kind": "MODEL",
        "label": "Subscription Billing",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "definition_source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188"
        }
      }
    ],
    "stops": [
      {
        "node": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "reason": "No retained upstream dependency is declared for this object."
      },
      {
        "node": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "reason": "No retained upstream dependency is declared for this object."
      }
    ],
    "truncated": false,
    "unavailable_owners": {
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89": {
        "at": "2026-10-28T06:03:11.630566Z",
        "failure": {
          "errno": null,
          "error_type": "RuntimeError",
          "line": 88,
          "message": "GRAPH_DEFINITION_KIND_UNAVAILABLE",
          "message_redacted": false,
          "module": "graph_change_collector.py"
        },
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "status": "UNAVAILABLE"
      },
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188": {
        "at": "2026-10-28T06:03:20.599000Z",
        "failure": {
          "errno": null,
          "error_type": "MetadataUnavailable",
          "http_status": 404,
          "line": 106,
          "message": "Metadata provider request unavailable",
          "message_redacted": false,
          "module": "metadata_auth.py",
          "provider_code": "EntityNotFound"
        },
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "status": "UNAVAILABLE"
      },
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a": {
        "at": "2026-10-28T06:03:23.952432Z",
        "failure": {
          "errno": null,
          "error_type": "MetadataUnavailable",
          "http_status": 404,
          "line": 106,
          "message": "Metadata provider request unavailable",
          "message_redacted": false,
          "module": "metadata_auth.py",
          "provider_code": "EntityNotFound"
        },
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "status": "UNAVAILABLE"
      }
    }
  }
}
```

Triage:
```json
{
  "facts": [
    {
      "cached": true,
      "check": "MODEL_REFRESH",
      "observed_at": "2026-10-28T06:22:18.194285Z",
      "source": "facts-ledger",
      "state": "OBSERVED_NEGATIVE",
      "value": [
        {
          "collected_at": "2026-10-28T06:22:18.194285Z",
          "freshness": "CURRENT",
          "id": "f55f20bf6ff328d22705b4043ea996e110df3eda334d3be5ee99988b8814b942",
          "kind": "RUN_HISTORY",
          "observed_at": "2026-10-28T06:22:18.194285Z",
          "provenance": {
            "collector": "microsoft-runtime:8b8add39b1b3bbf05051200684642bc68ee0c9695580165440fd17fca6875167",
            "evidence_ids": [
              "sha256:5af1889bed514118e966f6e5667727c75b7e45bc338836793d373e3b2046235b"
            ],
            "locator": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED_NEGATIVE",
          "subject": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
          "value": {
            "listing_complete": true,
            "runs": []
          }
        }
      ]
    },
    {
      "cached": true,
      "check": "REFRESH_SCHEDULE",
      "observed_at": "2026-10-28T06:22:18.194285Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T06:22:18.194285Z",
          "freshness": "CURRENT",
          "id": "5364674dabc7d981b7989ddd96151fdd04d0a85f8d0207c61da08b0fc2e9374a",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T06:22:18.194285Z",
          "provenance": {
            "collector": "microsoft-runtime:8b8add39b1b3bbf05051200684642bc68ee0c9695580165440fd17fca6875167",
            "evidence_ids": [
              "sha256:a141b182fa6e710f7ad086c88e702f3d73a0a158301326e03f14360e093b4e52"
            ],
            "locator": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/7d67bb36-04f6-4182-95aa-da5d515248fa/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "19:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        }
      ]
    },
    {
      "check": "AUTOMATIC_UPDATES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:AUTOMATIC_UPDATES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "JOB_RUNS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:JOB_RUNS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "LAYER_FRESHNESS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:LAYER_FRESHNESS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SOURCE_CHANGES",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:SOURCE_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "NEXT_LOAD",
      "observed_at": "2026-10-28T06:25:06.836417Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T06:25:06.836417Z",
          "freshness": "CURRENT",
          "id": "acce0facb9594bc9f16cdb9bdedce6b90140dc7aea917b378a29e8076f930a25",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T06:25:06.836417Z",
          "provenance": {
            "collector": "microsoft-runtime:8b8add39b1b3bbf05051200684642bc68ee0c9695580165440fd17fca6875167",
            "evidence_ids": [
              "sha256:387d3b298ba159e8d6315019426f5dec299aeedefb66bef074d154a5f91220f1"
            ],
            "locator": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/7d67bb36-04f6-4182-95aa-da5d515248fa/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "19:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        }
      ]
    },
    {
      "check": "CONNECTION_MODE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:CONNECTION_MODE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SECURITY_PRESENCE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:SECURITY_PRESENCE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "DEFINITION_CHANGES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:DEFINITION_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    }
  ],
  "path": [
    "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
    "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
    "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
    "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
    "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
    "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
    "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1"
  ],
  "refresh_operations": 8,
  "what_triage_suggests": "Triage has unavailable checks (AUTOMATIC_UPDATES, JOB_RUNS, LAYER_FRESHNESS, SOURCE_CHANGES, CONNECTION_MODE, SECURITY_PRESENCE, DEFINITION_CHANGES); this does not establish that those mechanisms are absent."
}
```

Tool decisions:
```json
[
  {
    "arguments": {
      "id": "case-evidence:25e2e825633c60689792fb46cf09e8735a2a9174e412d06b69702a22bc9899f1"
    },
    "tool": "get_evidence",
    "tool_use_id": "toolu_011hFGqK6KopqPw1HA62zM1G",
    "turn": 1
  },
  {
    "arguments": {
      "layer": "native:4aae8dbb1d373ebef783",
      "purpose": "recreate",
      "query": "EVALUATE ROW(\"Invoiced Amount\", SUM(Billing[amount]), \"max_invoice_date\", MAX(Billing[invoice_date]), \"rows\", COUNTROWS(Billing))"
    },
    "tool": "run_dax",
    "tool_use_id": "toolu_01WUUC3Mm8fMCdMKgMx9Fcda",
    "turn": 1
  },
  {
    "arguments": {
      "layer": "native:f87556d4485196602461",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, MAX([invoice_date]) AS max_invoice_date, COUNT(*) AS rows_observed FROM [gold].[invoice_activity]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_012GsF1bG7dUmPzP3mMJ5WFf",
    "turn": 1
  },
  {
    "arguments": {
      "node": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
    },
    "tool": "get_refresh_history",
    "tool_use_id": "toolu_01G2qZC5XQTNkNCefVLsGj2V",
    "turn": 1
  },
  {
    "arguments": {
      "node": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
      "operation": "PRODUCERS"
    },
    "tool": "get_lineage",
    "tool_use_id": "toolu_01VjfmXNedFyNKt7L8jdFYFy",
    "turn": 1
  },
  {
    "arguments": {
      "words": "invoice_activity stored procedure transformation bronze invoices billing warehouse job",
      "workspace": "7d67bb36-04f6-4182-95aa-da5d515248fa"
    },
    "tool": "list_candidates",
    "tool_use_id": "toolu_01FdKGSAtzGjix2TueSE1vD7",
    "turn": 4
  },
  {
    "arguments": {
      "node": "2439472548ec60dbbc1c57e217175f6e5cc5eef8b3c3cfea6b10463407a0e04c",
      "operation": "NEIGHBOURS"
    },
    "tool": "get_lineage",
    "tool_use_id": "toolu_01A932pXfzq3Ec4Xn8UKdqfV",
    "turn": 7
  },
  {
    "arguments": {
      "node": "072efb563a80031fb6ed6773a44b89662672682c6b0a16ef8c309b8e477485fb",
      "operation": "NEIGHBOURS"
    },
    "tool": "get_lineage",
    "tool_use_id": "toolu_01Knyptoxjy9R1xPXVEgrDoc",
    "turn": 7
  },
  {
    "arguments": {
      "node": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_01R7wAJ7dkrskgs7B6ndNyET",
    "turn": 10
  },
  {
    "arguments": {
      "node": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_01FZsV1rsuY2fK7ocmAHYKNX",
    "turn": 10
  },
  {
    "arguments": {
      "node": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_01PLaiZVAub7YVhq1gH7YSQt",
    "turn": 10
  },
  {
    "arguments": {
      "layer": "native:f87556d4485196602461",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount FROM [silver].[invoices]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01YBtZopxiDgJGLtU9gKTAtb",
    "turn": 10
  },
  {
    "arguments": {
      "layer": "native:f87556d4485196602461",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount FROM [bronze].[invoices]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01GWT4XGmr3q4NBUmckJAWtH",
    "turn": 10
  },
  {
    "arguments": {
      "id": "case-evidence:af837c6c27d533e5843ccea850f69d4f191294d2b061380d7bff7844e196f40e"
    },
    "tool": "get_evidence",
    "tool_use_id": "toolu_01WiDJeXJfxwD3Nq15qjYrQS",
    "turn": 13
  },
  {
    "arguments": {
      "node": "5fd69c1b5817645bf256c653c3a6fdfb060ba4f6cd3b35c7f56324a93e5e9ad4"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_019spftoTGqaWUxFoMxmZXHt",
    "turn": 16
  }
]
```

Queries:
```json
[
  {
    "asset_ids": [
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing",
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount",
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/invoice_date"
    ],
    "duration_seconds": 6.573167568000031,
    "executed_text": "EVALUATE TOPN(251,ROW(\"Invoiced Amount\",SUM(Billing[amount]),\"max_invoice_date\",MAX(Billing[invoice_date]),\"rows\",COUNTROWS(Billing)))",
    "id": "query:c1a7cd18dfc92ed71deead3e5846f934c0ee4e00aa65abac09f8ab0ca1cba89d:1",
    "layer": "native:4aae8dbb1d373ebef783",
    "parameters": [],
    "purpose": "recreate",
    "result": {
      "rows": [
        {
          "[Invoiced Amount]": 950,
          "[max_invoice_date]": "2026-10-01T00:00:00",
          "[rows]": 5
        }
      ],
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "768c09ce7732d94e86a1cb7b15cfaca800790def6ed32f5e8a21996794489f75",
    "row_count": 1,
    "signature": "c1a7cd18dfc92ed71deead3e5846f934c0ee4e00aa65abac09f8ab0ca1cba89d",
    "status": "SUCCEEDED",
    "text": "EVALUATE ROW(\"Invoiced Amount\", SUM(Billing[amount]), \"max_invoice_date\", MAX(Billing[invoice_date]), \"rows\", COUNTROWS(Billing))",
    "time": "2026-10-28T06:25:21.693175+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity"
    ],
    "duration_seconds": 9.90300928900001,
    "executed_text": "SELECT TOP 251 SUM(CAST([invoice_activity].[amount] AS BIGINT)) AS [invoiced_amount], MAX([invoice_activity].[invoice_date]) AS [max_invoice_date], COUNT(*) AS [rows_observed] FROM [gold].[invoice_activity] AS [invoice_activity]",
    "id": "query:76aa9664ef825db16af5b28737f38d5cfa02fea5d8177a57e6ff3d35d9b63ec6:2",
    "layer": "native:f87556d4485196602461",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "invoiced_amount": "Int64",
        "max_invoice_date": "DateTime",
        "rows_observed": "Int64"
      },
      "execution_identity": {
        "database": "billing_serving",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "invoiced_amount": "950",
          "max_invoice_date": "2026-10-01",
          "rows_observed": "5"
        }
      ]
    },
    "result_digest": "9bd1e64a4f8477fb9245c7757b56cbe2b1f0b48b252d208dd3dea7392b4641d7",
    "row_count": 1,
    "signature": "76aa9664ef825db16af5b28737f38d5cfa02fea5d8177a57e6ff3d35d9b63ec6",
    "status": "SUCCEEDED",
    "text": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, MAX([invoice_date]) AS max_invoice_date, COUNT(*) AS rows_observed FROM [gold].[invoice_activity]",
    "time": "2026-10-28T06:25:28.457579+00:00",
    "truncated": false
  },
  {
    "duration_seconds": 0,
    "error": "SQL object unavailable or view dependencies not validated",
    "error_type": "QueryRejection",
    "failure_class": "wrong column or table",
    "id": "query:cb48f0c186d2b6715c604905c0df4c18f493ed77f119d4cb581f837cf594003b:3",
    "layer": "native:f87556d4485196602461",
    "native_dispatched": false,
    "purpose": "compare",
    "result_digest": null,
    "row_count": null,
    "schema_slice": [
      {
        "columns": [
          {
            "collation_name": null,
            "data_type": "int",
            "name": "invoice_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "account_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "plan_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "date",
            "name": "invoice_date",
            "observed_type": "date"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "amount",
            "observed_type": "int"
          },
          {
            "collation_name": "Latin1_General_100_BIN2_UTF8",
            "data_type": "varchar",
            "name": "status",
            "observed_type": "varchar"
          }
        ],
        "id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
        "name": "invoice_activity",
        "schema_name": "gold",
        "type_desc": "USER_TABLE"
      }
    ],
    "signature": "cb48f0c186d2b6715c604905c0df4c18f493ed77f119d4cb581f837cf594003b",
    "status": "ERROR",
    "text": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount FROM [silver].[invoices]",
    "time": "2026-10-28T06:26:05.831706+00:00"
  },
  {
    "duration_seconds": 0,
    "error": "SQL object unavailable or view dependencies not validated",
    "error_type": "QueryRejection",
    "failure_class": "wrong column or table",
    "id": "query:9f7efcc07564548ddfb194dc777e195d6a5a6828aa2f40d10019323a2eb5f8d7:4",
    "layer": "native:f87556d4485196602461",
    "native_dispatched": false,
    "purpose": "compare",
    "result_digest": null,
    "row_count": null,
    "schema_slice": [
      {
        "columns": [
          {
            "collation_name": null,
            "data_type": "int",
            "name": "invoice_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "account_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "plan_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "date",
            "name": "invoice_date",
            "observed_type": "date"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "amount",
            "observed_type": "int"
          },
          {
            "collation_name": "Latin1_General_100_BIN2_UTF8",
            "data_type": "varchar",
            "name": "status",
            "observed_type": "varchar"
          }
        ],
        "id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
        "name": "invoice_activity",
        "schema_name": "gold",
        "type_desc": "USER_TABLE"
      }
    ],
    "signature": "9f7efcc07564548ddfb194dc777e195d6a5a6828aa2f40d10019323a2eb5f8d7",
    "status": "ERROR",
    "text": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount FROM [bronze].[invoices]",
    "time": "2026-10-28T06:26:06.283089+00:00"
  }
]
```

Final answer:
```json
"The checks did not establish a cause within this ticket’s limits."
```

Sealed expected:
```json
{
  "case_id": "v2-failed-billing-transform",
  "cause": "Latest failed native transform run with name/run ID/start/end/error; no invented successful completion.",
  "estate": "billing",
  "expectation_basis": "Practice source literals, declared definitions and reversible scenario plan; never an engine answer.",
  "fixture": "failed-billing",
  "id": "v2-failed-billing-transform-v2",
  "layer": "billing transformation pipeline",
  "split": "DEV",
  "variation": "brief support question",
  "verdict": "failed job"
}
```

Saved checkpoint SHA-256: 356ac3ccb5d70be403e849ad6ba2e2858349cc1f1d0041eee2a562ea585672f6. Only recorded tool choices are shown; no new queries or model calls.


## Round24 finaldev second-grader zeros (separate audit) automatic backtrack

{'graded': 3, 'score': 0, 'harmful': 1, 'correctness': {'cause_match': 0, 'layer_match': 0, 'verdict_match': 0}, 'zero_groups': {'conclusion': 1, 'triage': 2}}

| Ticket | First wrong step | Reason and correct action |
|---|---|---|
| v2-failed-application-load-v1 | conclusion | Expected: verdict 'failed job' at the application load pipeline layer. The cause should be the latest native failed run, citing the job name, run ID, start, end and error. Delivered: verdict 'consistent to boundary'. It states as fact that the data looks old because the source has nothing newer, not because delivery is behind. That is a confident cause that contradicts the expected failed-job cause, so it is harmful. The answer does find the failed run: it names pipeline round_two_application_load_audited_20261003, a failure at 2026-10-28 05:59, and error 2011. But it calls this only an 'open issue' and says it did not leave the report behind. It also never cites the failed run's run ID or both its start and end times. So the layer was not identified as the split point and the cause is not named as required. This is a partial match, which scores zero. The answer is wrong at the conclusion step, not because evidence was missing. Handoff: the queries are literal and can be rerun, but the handoff object is empty. There is no stopping point or next check, such as pulling the failed run's details or the load audit row. Score 1. Restrict the cause to what the cited native evidence establishes. |
| v2-failed-billing-transform-v1 | triage | Expected: verdict 'failed job' in the billing transformation pipeline (split DEV). The cause should be the latest failed native transform run, with its name, run ID, start/end times and error, and no made-up successful completion. The delivered answer is UNRESOLVED (TOOL_OR_TIME_LIMIT). It gives no verdict, no layer or split point and no named cause, so all three dimensions score zero. Nothing matched, so partial is false. It is not harmful: it states honestly that no cause was established and does not claim a successful run. It never retrieved the failed transform run that the ticket asks about. Triage reported JOB_RUNS (along with LAYER_FRESHNESS and SOURCE_CHANGES) as UNAVAILABLE. The only job-history-like query (billing_ops dbo.load_run_audit) returned a single successful copy run from 2026-10-09, not the failed transform. Model refresh history was empty and the schedule was disabled. Gold (5 rows / 950) and bronze (4 rows / 700) disagree, but this was not followed up. Handoff quality is 1. The queries are recorded verbatim and can be rerun, and the stopping point is clear. However, the only next check is to review a failed sys.objects metadata query. It does not point to the obvious next step: getting job history for the Billing Warehouse transformation pipeline and its latest failed run (run ID, times, error), or explaining the gold/bronze gap. The first failing step is triage, because the job-run fact needed to answer the ticket was unavailable and was never gathered another way. Read and act on the current path run or freshness fact first. |
| v2-failed-billing-transform-v2 | triage | Expected: verdict 'failed job' in the billing transformation pipeline, with the cause being the latest failed native transform run (name, run ID, start/end time, error). The delivered answer is UNRESOLVED (TOOL_OR_TIME_LIMIT). It names no verdict, no layer or split point, and no cause, so all three score zero. The grading rule also says an unresolved budget stop is not a successful technical answer. The answer is not harmful: it honestly says no cause was established and doesn't invent a successful run or a wrong cause. Where it went wrong: the ticket explicitly says the transformation job shows Failed, but the JOB_RUNS triage fact was UNAVAILABLE (FRESH_PATH_FACT_NOT_AVAILABLE). The investigation then compared the semantic model with gold.invoice_activity (both 950 / 5 rows / max 2026-10-01) and tried to query silver.invoices and bronze.invoices, which don't exist. It never looked at the pipeline run history. Handoff quality is 1. The queries are recorded word for word and can be rerun, and the stopping point is clearly stated. However, the next checks only say to review the queries rejected for missing silver/bronze objects. They don't suggest the obvious next step: get the latest run status and error for the Billing Warehouse transformation job, even though the ticket points straight to it. Read and act on the current path run or freshness fact first. |

### v2-failed-application-load-v1
Expected: verdict 'failed job' at the application load pipeline layer. The cause should be the latest native failed run, citing the job name, run ID, start, end and error. Delivered: verdict 'consistent to boundary'. It states as fact that the data looks old because the source has nothing newer, not because delivery is behind. That is a confident cause that contradicts the expected failed-job cause, so it is harmful. The answer does find the failed run: it names pipeline round_two_application_load_audited_20261003, a failure at 2026-10-28 05:59, and error 2011. But it calls this only an 'open issue' and says it did not leave the report behind. It also never cites the failed run's run ID or both its start and end times. So the layer was not identified as the split point and the cause is not named as required. This is a partial match, which scores zero. The answer is wrong at the conclusion step, not because evidence was missing. Handoff: the queries are literal and can be rerun, but the handoff object is empty. There is no stopping point or next check, such as pulling the failed run's details or the load audit row. Score 1. Restrict the cause to what the cited native evidence establishes.

Intake:
```json
{
  "compared_with": {
    "kind": "NOTHING"
  },
  "details": {
    "record": "round_two_application_load_audited_20261003"
  },
  "issue_type": "DATA_LOOKS_OLD",
  "page": "e4d6e671103ca3746c4ca9435fc635e13ae0a08bf09ffa515580b7f1a50fd7f7",
  "report": "3ba93e33aa41f6b91b0ef623bfd66bf2d9ec9eefd5e583643e6462e0dbd5b2ed",
  "version": "IntakeRequest/1",
  "visual": "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce"
}
```

Target:
```json
{
  "layers": {
    "native:4caf47d120d4fd198ffe": {
      "dialect": "DAX",
      "label": "Application load fixture 20261003"
    },
    "native:9e3796a26d8d5c1a039e": {
      "dialect": "T-SQL",
      "label": "ordersops"
    },
    "native:e95b94fd338e7086320f": {
      "dialect": "T-SQL",
      "label": "round_two_bronze_20261003"
    }
  }
}
```

Triage:
```json
{
  "facts": [
    {
      "cached": false,
      "check": "MODEL_REFRESH",
      "observed_at": "2026-10-28T06:03:45.192045Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T06:03:45.192045Z",
          "freshness": "CURRENT",
          "id": "0813c24647c79e63d5d228598a98416c83cc589bdc2b2c4aaf2ef7c565c900ca",
          "kind": "RUN_HISTORY",
          "observed_at": "2026-10-28T06:03:45.192045Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:07c699f26ee9bacb86e202ea45602e142e0bc1f6beb9bbdace1cdbc2a47eaecc"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "listing_complete": true,
            "runs": [
              {
                "end": "2026-10-27T15:56:11.943000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967533",
                "start": "2026-10-27T15:55:47.577000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:55:31.980000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967527",
                "start": "2026-10-27T15:55:17.423000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T11:22:45.240000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762883014",
                "start": "2026-10-27T11:22:42.810000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T10:04:03.517000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762859376",
                "start": "2026-10-27T10:03:42.330000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:20.813000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762589234",
                "start": "2026-10-26T18:20:20.733000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:33.260000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762588999",
                "start": "2026-10-26T18:19:56.113000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:27:55.313000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "761468506",
                "start": "2026-10-24T01:26:52.530000Z",
                "status": "SUCCEEDED"
              }
            ]
          }
        },
        {
          "collected_at": "2026-10-28T06:03:45.192045Z",
          "freshness": "CURRENT",
          "id": "2e60c156929dff59ed5e0a433f6936e63a6829539d73c019ece8f5afcdfba133",
          "kind": "REFRESH_RUN",
          "observed_at": "2026-10-28T06:03:45.192045Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:07c699f26ee9bacb86e202ea45602e142e0bc1f6beb9bbdace1cdbc2a47eaecc"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "accounting": "UNAVAILABLE_FROM_JOB_INSTANCE_SCHEMA",
            "end": "2026-10-27T15:56:11.943000Z",
            "error": null,
            "recent_runs": [
              {
                "end": "2026-10-27T15:56:11.943000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967533",
                "start": "2026-10-27T15:55:47.577000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:55:31.980000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967527",
                "start": "2026-10-27T15:55:17.423000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T11:22:45.240000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762883014",
                "start": "2026-10-27T11:22:42.810000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T10:04:03.517000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762859376",
                "start": "2026-10-27T10:03:42.330000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:20.813000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762589234",
                "start": "2026-10-26T18:20:20.733000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:33.260000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762588999",
                "start": "2026-10-26T18:19:56.113000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:27:55.313000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "761468506",
                "start": "2026-10-24T01:26:52.530000Z",
                "status": "SUCCEEDED"
              }
            ],
            "rows_read": null,
            "rows_written": null,
            "run_id": "762967533",
            "start": "2026-10-27T15:55:47.577000Z",
            "status": "SUCCEEDED"
          }
        },
        {
          "collected_at": "2026-10-28T06:03:45.192045Z",
          "freshness": "CURRENT",
          "id": "dadf9b538d81d60964e2f068231f586b49d072d84813af505481ee2757452c6a",
          "kind": "REFRESH_STATE",
          "observed_at": "2026-10-28T06:03:45.192045Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:07c699f26ee9bacb86e202ea45602e142e0bc1f6beb9bbdace1cdbc2a47eaecc"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "last_end": "2026-10-27T15:56:11.943000Z",
            "run_id": "762967533",
            "state": "SUCCEEDED"
          }
        }
      ]
    },
    {
      "cached": false,
      "check": "REFRESH_SCHEDULE",
      "observed_at": "2026-10-28T06:03:19.550779Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T06:03:45.192045Z",
          "freshness": "CURRENT",
          "id": "ecc0189dfc2f70a4d9303abb650c168427a7879dba0c82565b8a81e8a378232a",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T06:03:45.192045Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:7a55ebca2f0b3182a80bc69a8733e03bbb751b8cd668ceb94146ecb79f1b6c3f"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "01:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        },
        {
          "collected_at": "2026-10-28T06:03:19.550779Z",
          "freshness": "CURRENT",
          "id": "09c5ba81c0e36d233305d72dd183917c9b258cc057e8485303d9f742a9713817",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T06:03:19.550779Z",
          "provenance": {
            "collector": "microsoft-runtime:50ed9389d7d5682c8f2f36c6c2f43a2a3731a84b0c91204d9e25890e096564dc",
            "evidence_ids": [
              "sha256:934e05110c283815011ccfbcc809d65c007737e7ac5bdb66c2e9fc19473941c7"
            ],
            "locator": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "value": {
            "native_schedules": {
              "value": []
            },
            "next_due": null,
            "reason": "Job schedule recurrence retained; unsupported recurrence types remain a named coverage gap."
          }
        }
      ]
    },
    {
      "check": "AUTOMATIC_UPDATES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:AUTOMATIC_UPDATES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "JOB_RUNS",
      "observed_at": "2026-10-28T06:03:39.305110Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T06:03:39.305110Z",
          "freshness": "CURRENT",
          "id": "5e9db6ba4c8fcf13e06129ac9cc22cc010a2e7d00c51409941d6f19615f59ae9",
          "kind": "JOB_RUN",
          "observed_at": "2026-10-28T06:03:39.305110Z",
          "provenance": {
            "collector": "microsoft-runtime:d90ae203d1e049b5d17b28ad8d56b3e9cbbe0ea8e79c91698aded7cf5e687f7e",
            "evidence_ids": [
              "sha256:bdc882ff58bd4d502e9fadfe8f1f318a3bdd24ea54678be0c3d5df7c260d4adb"
            ],
            "locator": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
          "value": {
            "accounting": "UNAVAILABLE_FROM_JOB_INSTANCE_SCHEMA",
            "end": "2026-10-27T15:54:02.6605794Z",
            "error": null,
            "recent_runs": [
              {
                "end": "2026-10-27T15:54:02.6605794Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "c0e2613f-b446-4d00-a2c5-7f44c4662ae2",
                "start": "2026-10-27T15:53:32.7157778Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:44:05.0886872Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "a33b8ae0-57b8-4794-9cab-f50ec12e03ca",
                "start": "2026-10-27T15:43:33.6916187Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:20:29.5709877Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "fa3d9c73-ff5a-410a-89c8-907afd3f623c",
                "start": "2026-10-27T15:19:55.229535Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:10:24.4533955Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "644ef25a-bad3-4e5e-87b0-3f27c9b4498c",
                "start": "2026-10-27T15:09:53.1889637Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T14:31:41.1898358Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "5caa5c35-5e58-4dc1-94f0-fb8a9ab6619a",
                "start": "2026-10-27T14:31:09.9560782Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:59:50.6670091Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "d3d519f4-55b9-48ef-bf68-ee9b3d6fd724",
                "start": "2026-10-27T09:59:21.4245453Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:49:04.8377033Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "f12d45ba-a321-4a76-9f38-cfd86501054b",
                "start": "2026-10-27T09:48:35.0709386Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:41:49.8935835Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "4eda71d5-c497-4d52-b447-232386f672b5",
                "start": "2026-10-27T09:41:18.3358933Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:28:21.9101852Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "175ebde3-2543-47e5-bde0-ec38474c3ccc",
                "start": "2026-10-27T09:27:52.0485311Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T08:36:56.310785Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "d847a503-2bd8-4297-a917-8789854bbbdf",
                "start": "2026-10-27T08:36:25.9174801Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T06:45:53.3924184Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "150cca85-8b3d-44e6-ad1a-2e5ac059e2df",
                "start": "2026-10-27T06:45:24.4810815Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T06:15:17.1734177Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "1db862a2-6df5-41a7-a71a-02ca24eab7da",
                "start": "2026-10-27T06:09:51.1598474Z",
                "status": "CANCELLED"
              },
              {
                "end": "2026-10-26T18:15:51.642450Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "2b43720a-f2bb-47bb-a456-9dac546a4eb4",
                "start": "2026-10-26T18:15:14.6320687Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T02:12:10.4565917Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "c2bf877a-9ff2-4852-aa6b-f0503b71b2f3",
                "start": "2026-10-24T02:11:38.9387923Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:40:16.5003956Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "4ea4687d-5e43-4933-8db5-860286d0f681",
                "start": "2026-10-24T01:39:46.1269955Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:38:34.0644025Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "98fae91b-2011-485b-855d-fa288e98a292",
                "start": "2026-10-24T01:38:03.7174285Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:30:31.4662186Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "6f06aae7-d60b-4d61-beeb-0fab21e4c5b2",
                "start": "2026-10-24T01:29:12.6228674Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T00:33:09.2916262Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "8d7d15cc-b985-4b12-85cb-495691a8d417",
                "start": "2026-10-24T00:31:48.7636953Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-06T04:14:36.7034118Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "d748fff0-b0d4-43de-89c7-8a929be24642",
                "start": "2026-10-06T04:14:04.0430647Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-06T03:33:24.3307242Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "ccc21d6a-41a7-4e20-839d-0b5d8cf8858c",
                "start": "2026-10-06T03:32:52.1454566Z",
                "status": "SUCCEEDED"
              }
            ],
            "rows_read": null,
            "rows_written": null,
            "run_id": "c0e2613f-b446-4d00-a2c5-7f44c4662ae2",
            "start": "2026-10-27T15:53:32.7157778Z",
            "status": "SUCCEEDED"
          }
        }
      ]
    },
    {
      "check": "LAYER_FRESHNESS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:LAYER_FRESHNESS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SOURCE_CHANGES",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:SOURCE_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "NEXT_LOAD",
      "observed_at": "2026-10-28T06:03:19.550779Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T06:03:45.192045Z",
          "freshness": "CURRENT",
          "id": "ecc0189dfc2f70a4d9303abb650c168427a7879dba0c82565b8a81e8a378232a",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T06:03:45.192045Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:7a55ebca2f0b3182a80bc69a8733e03bbb751b8cd668ceb94146ecb79f1b6c3f"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "01:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        },
        {
          "collected_at": "2026-10-28T06:03:19.550779Z",
          "freshness": "CURRENT",
          "id": "09c5ba81c0e36d233305d72dd183917c9b258cc057e8485303d9f742a9713817",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T06:03:19.550779Z",
          "provenance": {
            "collector": "microsoft-runtime:50ed9389d7d5682c8f2f36c6c2f43a2a3731a84b0c91204d9e25890e096564dc",
            "evidence_ids": [
              "sha256:934e05110c283815011ccfbcc809d65c007737e7ac5bdb66c2e9fc19473941c7"
            ],
            "locator": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "value": {
            "native_schedules": {
              "value": []
            },
            "next_due": null,
            "reason": "Job schedule recurrence retained; unsupported recurrence types remain a named coverage gap."
          }
        }
      ]
    },
    {
      "check": "CONNECTION_MODE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:CONNECTION_MODE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SECURITY_PRESENCE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:SECURITY_PRESENCE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "DEFINITION_CHANGES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:DEFINITION_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    }
  ],
  "path": [
    "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
    "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
    "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
    "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
    "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
    "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
    "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
    "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
    "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce",
    "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
    "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
    "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
    "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
    "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
    "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
    "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
    "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
    "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
    "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
  ],
  "refresh_operations": 10,
  "what_triage_suggests": "Triage has unavailable checks (AUTOMATIC_UPDATES, LAYER_FRESHNESS, SOURCE_CHANGES, CONNECTION_MODE, SECURITY_PRESENCE, DEFINITION_CHANGES); this does not establish that those mechanisms are absent."
}
```

Tool decisions:
```json
[
  {
    "arguments": {
      "layer": "native:4caf47d120d4fd198ffe",
      "purpose": "recreate",
      "query": "EVALUATE ROW(\"Movement Units\", [Movement Units])"
    },
    "tool": "run_dax"
  },
  {
    "arguments": {
      "layer": "native:e95b94fd338e7086320f",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([units] AS bigint)) AS movement_units FROM [dbo].[stock_movements_round_two_20261003]"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([units] AS bigint)) AS movement_units FROM [app].[stock_movements_round_two_20261003]"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "node": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
    },
    "tool": "get_job_runs"
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "compare",
      "query": "SELECT MAX([source_modified_at_utc]) AS max_modified FROM [app].[stock_movements_round_two_20261003]"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "layer": "native:e95b94fd338e7086320f",
      "purpose": "compare",
      "query": "SELECT MAX([source_modified_at_utc]) AS max_modified FROM [dbo].[stock_movements_round_two_20261003]"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "compare",
      "query": "SELECT COUNT(*) AS rows_observed FROM [app].[stock_movements_round_two_20261003]"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "layer": "native:e95b94fd338e7086320f",
      "purpose": "compare",
      "query": "SELECT COUNT(*) AS rows_observed FROM [dbo].[stock_movements_round_two_20261003]"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "cause": "The Movement Units card (SUM of Movements[units]) recreates at 7661. The landing lakehouse table dbo.stock_movements_round_two_20261003 also reads 7661, and so does the application source table app.stock_movements_round_two_20261003. Both tables currently hold 360 rows, and in both the newest source_modified_at_utc is 2026-10-03 22:51:16.882024. So the data looks old because the source itself has nothing newer, not because delivery is behind the source. One open issue: the latest run of the load pipeline round_two_application_load_audited_20261003 failed at 2026-10-28 05:59 (error 2011, a controlled failure before the original activities). Its last successful run ended 2026-10-27 15:54, and the declared load audit has no row for the listed run. The current reads show no source change since then, so that failure has not left the report behind the source. The last model refresh succeeded on 2026-10-27 15:56. Matching totals are point-in-time reads; they don't prove the layers were captured at the same moment, and no retained source history was read.",
      "checked": [
        "native:4caf47d120d4fd198ffe",
        "native:e95b94fd338e7086320f",
        "native:9e3796a26d8d5c1a039e",
        "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
      ],
      "evidence_ids": [
        "case-evidence:07e8e3947ce864aeb8f9c405ef346dd0978894bbb974d0bf1ebd8c63678ceae3",
        "case-evidence:5efedfd682e4ad42704af4ce66423891c5a0c4d5ef216e7a254f1c8cd43d3fc6",
        "case-evidence:15668322d54828d48bbccb31bfb05ffb91252a8f5fb0e8cd815bab28a4e44981",
        "case-evidence:a49840af63840cbd21540e29db374c323db0bad2460b108c6b67be2d9ab68fcf",
        "case-evidence:653bc2881c31961771799162d4ebc0ed127ccccb1a2cc7a89dfd0c17efb0d19a",
        "case-evidence:3889f9ab659033051ef02b1732f48504bba0543d3f3ee3ffe38eac3de9ed4d63",
        "case-evidence:673c248d4714401ecca64113d17265111b7354aabd54c18a5aee3515ee4e3fbf",
        "case-evidence:aee8abc1ac370cd435720e4dd0f21aba9c704505561f7e592ca8ed1fd4e6a652"
      ],
      "numbers": [
        7661,
        7661,
        7661,
        360,
        360
      ],
      "verdict": "consistent to boundary"
    },
    "tool": "submit_finding"
  },
  {
    "arguments": {
      "cause": "The Movement Units card (SUM of Movements[units]) recreates at 7661. The landing lakehouse table dbo.stock_movements_round_two_20261003 also reads 7661, and so does the application source table app.stock_movements_round_two_20261003. Both tables currently hold 360 rows, and in both the newest source_modified_at_utc is 2026-10-03 22:51:16.882024. So the data looks old because the source itself has nothing newer, not because delivery is behind the source. One open issue: the latest run of the load pipeline round_two_application_load_audited_20261003 failed at 2026-10-28 05:59 (error 2011, a controlled failure before the original activities). Its last successful run ended 2026-10-27 15:54, and the declared load audit has no row for the listed run. The current reads show no source change since then, so that failure has not left the report behind the source. The last model refresh succeeded on 2026-10-27 15:56. Matching totals are point-in-time reads; they don't prove the layers were captured at the same moment, and no retained source history was read.",
      "checked": [
        "native:4caf47d120d4fd198ffe",
        "native:e95b94fd338e7086320f",
        "native:9e3796a26d8d5c1a039e"
      ],
      "evidence_ids": [
        "case-evidence:07e8e3947ce864aeb8f9c405ef346dd0978894bbb974d0bf1ebd8c63678ceae3",
        "case-evidence:5efedfd682e4ad42704af4ce66423891c5a0c4d5ef216e7a254f1c8cd43d3fc6",
        "case-evidence:15668322d54828d48bbccb31bfb05ffb91252a8f5fb0e8cd815bab28a4e44981",
        "case-evidence:a49840af63840cbd21540e29db374c323db0bad2460b108c6b67be2d9ab68fcf",
        "case-evidence:653bc2881c31961771799162d4ebc0ed127ccccb1a2cc7a89dfd0c17efb0d19a",
        "case-evidence:3889f9ab659033051ef02b1732f48504bba0543d3f3ee3ffe38eac3de9ed4d63",
        "case-evidence:673c248d4714401ecca64113d17265111b7354aabd54c18a5aee3515ee4e3fbf",
        "case-evidence:aee8abc1ac370cd435720e4dd0f21aba9c704505561f7e592ca8ed1fd4e6a652"
      ],
      "numbers": [
        7661,
        7661,
        7661,
        360,
        360
      ],
      "verdict": "consistent to boundary"
    },
    "tool": "submit_finding"
  }
]
```

Queries:
```json
[
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units"
    ],
    "duration_seconds": 3.6742456540000603,
    "executed_text": "EVALUATE TOPN(251,ROW(\"Movement Units\",[Movement Units]))",
    "id": "query:de0184c1e969349b6aea9859af3b75efc52516142cf617a938c73d90fe287b5a:1",
    "layer": "native:4caf47d120d4fd198ffe",
    "parameters": [],
    "purpose": "recreate",
    "result": {
      "rows": [
        {
          "[Movement Units]": 7661
        }
      ],
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "9ab717fe0b9eb233c96216461080cb3157e1cb290731cc4ed00cdc172576d5ba",
    "row_count": 1,
    "signature": "de0184c1e969349b6aea9859af3b75efc52516142cf617a938c73d90fe287b5a",
    "status": "SUCCEEDED",
    "text": "EVALUATE ROW(\"Movement Units\", [Movement Units])",
    "time": "2026-10-28T06:04:00.738740+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003"
    ],
    "duration_seconds": 12.074448176000033,
    "executed_text": "SELECT TOP 251 SUM(CAST([stock_movements_round_two_20261003].[units] AS BIGINT)) AS [movement_units] FROM [dbo].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003]",
    "id": "query:61e1ef357414429a0e11fb88194c9cf369c4bc070613fd8ede458bebb5888e45:2",
    "layer": "native:e95b94fd338e7086320f",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "movement_units": "Int64"
      },
      "execution_identity": {
        "database": "round_two_bronze_20261003",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "movement_units": "7661"
        }
      ]
    },
    "result_digest": "55899439a64256b0e5a0201a7acf008e51e8c3c6fb5627d7375a336e3f1d11ef",
    "row_count": 1,
    "signature": "61e1ef357414429a0e11fb88194c9cf369c4bc070613fd8ede458bebb5888e45",
    "status": "SUCCEEDED",
    "text": "SELECT SUM(CAST([units] AS bigint)) AS movement_units FROM [dbo].[stock_movements_round_two_20261003]",
    "time": "2026-10-28T06:04:04.703723+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 3.5433835260000706,
    "executed_text": "SELECT TOP 251 SUM(CAST([stock_movements_round_two_20261003].[units] AS BIGINT)) AS [movement_units] FROM [app].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003]",
    "id": "query:d9e2677e79949c2bed58a60daefa15a72df5da9f6689088295dc4b508dc6d6b5:3",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "movement_units": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T06:04:20.263953+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T06:04:17.198105+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "movement_units": "7661"
        }
      ]
    },
    "result_digest": "a3105e1a64489a88c1620d9af3c8f481e16840595d1361de311d0fadfc70cb4a",
    "row_count": 1,
    "signature": "d9e2677e79949c2bed58a60daefa15a72df5da9f6689088295dc4b508dc6d6b5",
    "status": "SUCCEEDED",
    "text": "SELECT SUM(CAST([units] AS bigint)) AS movement_units FROM [app].[stock_movements_round_two_20261003]",
    "time": "2026-10-28T06:04:16.994411+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 3.2043418189998647,
    "executed_text": "SELECT TOP 251 MAX([stock_movements_round_two_20261003].[source_modified_at_utc]) AS [max_modified] FROM [app].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003]",
    "id": "query:df9353b165605c359e4e6b89287b56b208beea4921073ec5d5c81ef32ccf3270:4",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "max_modified": "DateTime"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T06:04:46.361872+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T06:04:43.643703+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "max_modified": "2026-10-03 22:51:16.882024"
        }
      ]
    },
    "result_digest": "c6dedc0b7762c167b09b4a72478e4101418278eb7d435ba3aff5362f28c4cee9",
    "row_count": 1,
    "signature": "df9353b165605c359e4e6b89287b56b208beea4921073ec5d5c81ef32ccf3270",
    "status": "SUCCEEDED",
    "text": "SELECT MAX([source_modified_at_utc]) AS max_modified FROM [app].[stock_movements_round_two_20261003]",
    "time": "2026-10-28T06:04:43.434252+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003"
    ],
    "duration_seconds": 5.41629114400007,
    "executed_text": "SELECT TOP 251 MAX([stock_movements_round_two_20261003].[source_modified_at_utc]) AS [max_modified] FROM [dbo].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003]",
    "id": "query:618831286451eb222c8af2d110b4f699fb861a8e554f9602acdfa5b2978733f4:5",
    "layer": "native:e95b94fd338e7086320f",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "max_modified": "DateTime"
      },
      "execution_identity": {
        "database": "round_two_bronze_20261003",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "max_modified": "2026-10-03 22:51:16.882024"
        }
      ]
    },
    "result_digest": "2a11c14d49835a52daf9374880a3f4b012239d4b56af61ef13bcc31041836dec",
    "row_count": 1,
    "signature": "618831286451eb222c8af2d110b4f699fb861a8e554f9602acdfa5b2978733f4",
    "status": "SUCCEEDED",
    "text": "SELECT MAX([source_modified_at_utc]) AS max_modified FROM [dbo].[stock_movements_round_two_20261003]",
    "time": "2026-10-28T06:04:46.911386+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 3.107711436999807,
    "executed_text": "SELECT TOP 251 COUNT(*) AS [rows_observed] FROM [app].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003]",
    "id": "query:f3b8eb568b1cca202cf30a94b647e2d024067cd61212a5379ac0509c52b1bfd6:6",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "rows_observed": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T06:04:55.430829+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T06:04:52.805384+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "rows_observed": "360"
        }
      ]
    },
    "result_digest": "5a85d4649806d838bedd21451b5d85ce8ba20bd4853712317590e00b7d24a9ca",
    "row_count": 1,
    "signature": "f3b8eb568b1cca202cf30a94b647e2d024067cd61212a5379ac0509c52b1bfd6",
    "status": "SUCCEEDED",
    "text": "SELECT COUNT(*) AS rows_observed FROM [app].[stock_movements_round_two_20261003]",
    "time": "2026-10-28T06:04:52.600846+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003"
    ],
    "duration_seconds": 5.8232743159999245,
    "executed_text": "SELECT TOP 251 COUNT(*) AS [rows_observed] FROM [dbo].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003]",
    "id": "query:88d07cdf280559c8d65a84ae80699186f7b5eb3a786b3a9bc16c6dec6272482b:7",
    "layer": "native:e95b94fd338e7086320f",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "rows_observed": "Int64"
      },
      "execution_identity": {
        "database": "round_two_bronze_20261003",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "rows_observed": "360"
        }
      ]
    },
    "result_digest": "2825c1b7aa0dbdbdc15b9729d4bb7c75ff65ea140537d3ac2354cd63cf9b44af",
    "row_count": 1,
    "signature": "88d07cdf280559c8d65a84ae80699186f7b5eb3a786b3a9bc16c6dec6272482b",
    "status": "SUCCEEDED",
    "text": "SELECT COUNT(*) AS rows_observed FROM [dbo].[stock_movements_round_two_20261003]",
    "time": "2026-10-28T06:04:55.980410+00:00",
    "truncated": false
  }
]
```

Final answer:
```json
"consistent to boundary. The Movement Units card (SUM of Movements[units]) recreates at 7661. The landing lakehouse table dbo.stock_movements_round_two_20261003 also reads 7661, and so does the application source table app.stock_movements_round_two_20261003. Both tables currently hold 360 rows, and in both the newest source_modified_at_utc is 2026-10-03 22:51:16.882024. So the data looks old because the source itself has nothing newer, not because delivery is behind the source. One open issue: the latest run of the load pipeline round_two_application_load_audited_20261003 failed at 2026-10-28 05:59 (error 2011, a controlled failure before the original activities). Its last successful run ended 2026-10-27 15:54, and the declared load audit has no row for the listed run. The current reads show no source change since then, so that failure has not left the report behind the source. The last model refresh succeeded on 2026-10-27 15:56. Matching totals are point-in-time reads; they don't prove the layers were captured at the same moment, and no retained source history was read.\nNumbers: 7661, 7661, 7661, 360, 360.\nChecked: Application load fixture 20261003, round_two_bronze_20261003, ordersops.\nNative comparisons are observational snapshots; aligned query-bound versions are not established.\nCatalog bookkeeping unavailable: collector containment (recovered from literal native address), current inventory availability, inventory content hashes (metadata digests are derived and labelled), inventory provenance, per-asset collector timestamps. This does not block investigation; successful queries establish present readability only.\nattestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
```

Sealed expected:
```json
{
  "case_id": "v2-failed-application-load",
  "cause": "Latest native failed run, job name/run ID/start/end/error must be cited.",
  "estate": "fixture",
  "expectation_basis": "Practice source literals, declared definitions and reversible scenario plan; never an engine answer.",
  "fixture": "failed-fixture",
  "id": "v2-failed-application-load-v1",
  "layer": "application load pipeline",
  "split": "DEV",
  "variation": "detailed support question",
  "verdict": "failed job"
}
```

### v2-failed-billing-transform-v1
Expected: verdict 'failed job' in the billing transformation pipeline (split DEV). The cause should be the latest failed native transform run, with its name, run ID, start/end times and error, and no made-up successful completion. The delivered answer is UNRESOLVED (TOOL_OR_TIME_LIMIT). It gives no verdict, no layer or split point and no named cause, so all three dimensions score zero. Nothing matched, so partial is false. It is not harmful: it states honestly that no cause was established and does not claim a successful run. It never retrieved the failed transform run that the ticket asks about. Triage reported JOB_RUNS (along with LAYER_FRESHNESS and SOURCE_CHANGES) as UNAVAILABLE. The only job-history-like query (billing_ops dbo.load_run_audit) returned a single successful copy run from 2026-10-09, not the failed transform. Model refresh history was empty and the schedule was disabled. Gold (5 rows / 950) and bronze (4 rows / 700) disagree, but this was not followed up. Handoff quality is 1. The queries are recorded verbatim and can be rerun, and the stopping point is clear. However, the only next check is to review a failed sys.objects metadata query. It does not point to the obvious next step: getting job history for the Billing Warehouse transformation pipeline and its latest failed run (run ID, times, error), or explaining the gold/bronze gap. The first failing step is triage, because the job-run fact needed to answer the ticket was unavailable and was never gathered another way. Read and act on the current path run or freshness fact first.

Intake:
```json
{
  "classified_issue_type": "DATA_LOOKS_OLD",
  "compared_with": {
    "kind": "NOTHING"
  },
  "description": "I noticed that the Billing Warehouse transformation pipeline shows a Failed status on its latest job-history run. Because of this, I'm concerned the Invoiced Amount figure on the Subscription Billing page may not be reflecting current data. Can you tell me what happened with that failed run and whether the numbers in this report are stale as a result? I'd like to understand the impact on the data before I share this report with the finance team.",
  "issue_type": "DATA_LOOKS_OLD",
  "measure_candidates": [
    {
      "id": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
      "name": "Invoiced Amount"
    }
  ],
  "page": "69271186d3ccfbba0cccf5a28033b28f779e8c46e00b6f45adad14d97507539e",
  "report": "44dc6baac12f79e0f4a1c4474c63bb2867262137212e4061f4ce0882c4a90257",
  "status": "READY",
  "version": "IntakeRequest/1",
  "visual": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b"
}
```

Target:
```json
{
  "layers": {
    "native:4aae8dbb1d373ebef783": {
      "dialect": "DAX",
      "label": "Subscription Billing"
    },
    "native:ac3ebe915b1cc00c45d7": {
      "dialect": "T-SQL",
      "label": "billing_bronze"
    },
    "native:bc3914e8dae9e68e7163": {
      "dialect": "T-SQL",
      "label": "billing_ops"
    },
    "native:db47aa505c8c14efec29": {
      "dialect": "T-SQL",
      "label": "billingapp"
    },
    "native:f87556d4485196602461": {
      "dialect": "T-SQL",
      "label": "billing_serving"
    }
  },
  "path": {
    "as_of": null,
    "declared_route_bridges": [
      {
        "column_bindings": [
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/invoice_id",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/invoice_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/account_id",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/account_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/plan_id",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/plan_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/invoice_date",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/invoice_date"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/status",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/status"
          }
        ],
        "confidence": "DECLARED",
        "definition_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/part/model.bim",
        "definition_hash": "7565c9db1f3083abd3e08cf3d16d74e0a8f93f5c6efd1119ef278dc5db152db1",
        "graph_nodes": [
          "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
          "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd"
        ],
        "literal_expression": "let database = Sql.Database(\"i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com\", \"406dcb89-0526-4f48-bb77-397d52471c89\") in database",
        "native_ownership": [],
        "partition_source": {
          "entityName": "invoice_activity",
          "expressionSource": "BillingServingSource",
          "schemaName": "gold",
          "type": "entity"
        },
        "physical_table": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
        "qualification": "Declared route only; value agreement and aligned snapshots are not implied.",
        "semantic_table": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing"
      }
    ],
    "edges": [
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "3a6ba8ce4d7efd8c326192d087b8dfb05c43ca5209cf86cf5fb79cdbd9e4534c",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "binding_kind": "DIRECTLAKE_ENTITY",
          "catalog_id": "406dcb89-0526-4f48-bb77-397d52471c89",
          "container_asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "container_binding": {
            "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "container_bindings": [
            {
              "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
              "observed_at": "2026-10-12T06:22:48.745954Z",
              "source": "STATIC_DEFINITION",
              "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
              "span": {
                "kind": "JSON_POINTER",
                "path": ""
              }
            }
          ],
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "entity": "invoice_activity",
          "expression_pointer": "/model/expressions/0",
          "expression_source": "BillingServingSource",
          "physical_definition": {
            "definition_hash": "b32a45a2bf55337bb1a7b5ad78602572341ad2b6ebb249dc7657a32d3fb9e876",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "schema": "gold",
          "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com"
        },
        "provenance": {
          "definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/part/model.bim",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/model/tables/5/partitions"
          }
        },
        "source": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "target": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "unknown": null,
        "valid_from": "2026-10-27T10:08:38.481811Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "5b1782b90d25ef08907c1313aa35b95c128b4ee89d888d8371860a27ea6d1804",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "completeness": "ROW_ONLY",
          "definition": {
            "bytes": 8289,
            "sha256": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c"
          },
          "model_definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "native_row_hash": "f46ed22f744430f4f9406a42a056fdac7f90072a2f613406dbf2866e92b476f0"
        },
        "provenance": {
          "definition_hash": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "ENGINE_DEPENDENCY",
          "source_id": "24dc7f097c6839881270308e2651f9937a44cdfcbaa0d58448f2364a4d6b8627",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/rows/21"
          }
        },
        "source": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "target": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "62f0613f9f6894eaf7b5e2c5047953bea360ce5bfb26ff07c9cc1e26a9b073ac",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a",
        "properties": {
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a"
        },
        "provenance": {
          "definition_hash": "c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db",
          "observed_at": "2026-10-13T17:34:44.997022Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a/part/definition%2Fpages%2Fc9b267726b645332927d%2Fvisuals%2F788498de9a325c7bb6a9%2Fvisual.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/queryState/Values/projections/0/field/Measure"
          }
        },
        "source": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "target": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "unknown": null,
        "valid_from": "2026-10-13T17:34:44.997022Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "6a48e802bd984e9779fdd00a33e71b6841ab618cd095b9bcbcfdf73b2a654aae",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "completeness": "ROW_ONLY",
          "definition": {
            "bytes": 8289,
            "sha256": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c"
          },
          "model_definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "native_row_hash": "ad0462db0652c3ca7c3eb37d57ab7ff55057e3edc0d3374449f3517a4d07d6e5"
        },
        "provenance": {
          "definition_hash": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "ENGINE_DEPENDENCY",
          "source_id": "24dc7f097c6839881270308e2651f9937a44cdfcbaa0d58448f2364a4d6b8627",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/rows/20"
          }
        },
        "source": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "target": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "d8908c0765aacbfb72890a1818efd03f1efd4d224259f81635ba81fa609075dc",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "binding_kind": "DIRECTLAKE_ENTITY",
          "catalog_id": "406dcb89-0526-4f48-bb77-397d52471c89",
          "container_asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "container_binding": {
            "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "container_bindings": [
            {
              "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
              "observed_at": "2026-10-12T06:22:48.745954Z",
              "source": "STATIC_DEFINITION",
              "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
              "span": {
                "kind": "JSON_POINTER",
                "path": ""
              }
            }
          ],
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "entity": "invoice_activity",
          "expression_pointer": "/model/expressions/0",
          "expression_source": "BillingServingSource",
          "physical_column_definition": {
            "definition_hash": "e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d",
            "observed_at": "2026-10-13T17:41:15.000678Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "physical_definition": {
            "definition_hash": "b32a45a2bf55337bb1a7b5ad78602572341ad2b6ebb249dc7657a32d3fb9e876",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "schema": "gold",
          "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com",
          "source_column": "amount"
        },
        "provenance": {
          "definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/part/model.bim",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/model/tables/5/columns/4/sourceColumn"
          }
        },
        "source": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "target": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "unknown": null,
        "valid_from": "2026-10-27T10:08:38.481811Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "6042ff3c9dfb5abdf8c92b18f134b7e2be824412f423aa110475bf6b076cb4ad",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e"
        },
        "provenance": {
          "definition_hash": "6a8b2cf63f4dd89c731612162da50b38507fbc9120d3b5d88507d8c0653ab6cf",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/9/text"
          }
        },
        "source": "cd24018f200d886024efd549c6a79f2cc38fd8665b0337f3d4b5c3d391788c22",
        "target": "5824559a10e087711ceb49661818923333c1c87efa9ed0a2c80433e8f7f8c654",
        "unknown": null,
        "valid_from": "2026-10-13T07:41:50.583455Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "68a96a39b4f2f455ef383009526418b8fff04c3eb8d00a148a01b989068b86a1",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e",
        "properties": {
          "basis": "EXACT_SCRIPT_DATABASE_AND_TABLE",
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e",
          "execution_established": false
        },
        "provenance": {
          "definition_hash": "6a8b2cf63f4dd89c731612162da50b38507fbc9120d3b5d88507d8c0653ab6cf",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/9/text"
          }
        },
        "source": "5824559a10e087711ceb49661818923333c1c87efa9ed0a2c80433e8f7f8c654",
        "target": "072efb563a80031fb6ed6773a44b89662672682c6b0a16ef8c309b8e477485fb",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "7aaa34af4c1bad7ccfc7ce3f765a2d4843fae4616ddeac1bd97374180f1cb8a9",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba",
        "properties": {
          "basis": "EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS",
          "connection_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/connection/93fd5fbf-5835-4756-bc59-bbf07302f321",
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0",
          "destination_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba/table/invoices",
          "native_destination": {
            "artifactId": "1853cbbb-06d1-4ae9-b378-370007c574ba",
            "workspaceId": "7d67bb36-04f6-4182-95aa-da5d515248fa"
          },
          "source_asset": "sql://sql-orderops-9696025.database.windows.net/billingapp/object/1941581955",
          "source_query": "SELECT [invoice_id],[account_id],[invoice_date],[amount],[status],CAST(source_row_version AS bigint) AS source_row_version,source_modified_at_utc FROM [app].[invoices]"
        },
        "provenance": {
          "definition_hash": "0389f86a2811c8e11ae84891984d39ea93e5a9fb631135b78d38b22c42b3574c",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/4"
          }
        },
        "source": "072efb563a80031fb6ed6773a44b89662672682c6b0a16ef8c309b8e477485fb",
        "target": "5fd69c1b5817645bf256c653c3a6fdfb060ba4f6cd3b35c7f56324a93e5e9ad4",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "7c9ceae9e132e23285f38c8c42b36b40efb0edd02bdc646b1d6d852abf5d992b",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9"
        },
        "provenance": {
          "definition_hash": "b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/7/text"
          }
        },
        "source": "cd24018f200d886024efd549c6a79f2cc38fd8665b0337f3d4b5c3d391788c22",
        "target": "18e99db0461c73d0ab6adfdd91203ddfa934583167f2a525f0f33f54cfa5b780",
        "unknown": null,
        "valid_from": "2026-10-13T07:41:50.583455Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "9d47086709abdedd0e7709cb370976f363b0befdb19e7af7ba7005b63d4c162b",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0",
        "properties": {
          "basis": "EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS",
          "connection_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/connection/93fd5fbf-5835-4756-bc59-bbf07302f321",
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0",
          "destination_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba/table/invoices",
          "native_destination": {
            "artifactId": "1853cbbb-06d1-4ae9-b378-370007c574ba",
            "workspaceId": "7d67bb36-04f6-4182-95aa-da5d515248fa"
          },
          "source_asset": "sql://sql-orderops-9696025.database.windows.net/billingapp/object/1941581955",
          "source_query": "SELECT [invoice_id],[account_id],[invoice_date],[amount],[status],CAST(source_row_version AS bigint) AS source_row_version,source_modified_at_utc FROM [app].[invoices]"
        },
        "provenance": {
          "definition_hash": "0389f86a2811c8e11ae84891984d39ea93e5a9fb631135b78d38b22c42b3574c",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/4"
          }
        },
        "source": "5fd69c1b5817645bf256c653c3a6fdfb060ba4f6cd3b35c7f56324a93e5e9ad4",
        "target": "564adac92668939502d6e329320c18788ae803227e5ba70fa31a65e501f9612e",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "acaa3c15195e3d45419cf863e36b0b0e599c85db8769685c4f4a86baa6590234",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9",
        "properties": {
          "basis": "EXACT_SCRIPT_DATABASE_AND_TABLE",
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9",
          "execution_established": false
        },
        "provenance": {
          "definition_hash": "b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/7/text"
          }
        },
        "source": "18e99db0461c73d0ab6adfdd91203ddfa934583167f2a525f0f33f54cfa5b780",
        "target": "072efb563a80031fb6ed6773a44b89662672682c6b0a16ef8c309b8e477485fb",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      }
    ],
    "estate": "billing",
    "nodes": [
      {
        "confidence": "DECLARED",
        "id": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "kind": "COLUMN",
        "label": "amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
          "definition": {
            "bytes": 249,
            "sha256": "e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "hidden": null,
          "native_kind": "WarehouseColumn"
        },
        "provenance": {
          "definition_hash": "e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d",
          "observed_at": "2026-10-13T17:41:15.000678Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:41:15.000678Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "kind": "COLUMN",
        "label": "amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount",
          "dataType": "int64",
          "definition": {
            "bytes": 88,
            "sha256": "b1f9170e2c11581cbb5f36f01e51d440deff9cc017c473c9a2e93af6501741f5",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/b1f9170e2c11581cbb5f36f01e51d440deff9cc017c473c9a2e93af6501741f5"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "hidden": null,
          "native_kind": "SemanticColumn",
          "sourceColumn": "amount"
        },
        "provenance": {
          "definition_hash": "b1f9170e2c11581cbb5f36f01e51d440deff9cc017c473c9a2e93af6501741f5",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "kind": "TABLE",
        "label": "Billing",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing",
          "definition": {
            "bytes": 1459,
            "sha256": "6b0f856158e5e4207753b23208cf3d6770986030db7b78d0e8f3434b54cc7177",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/6b0f856158e5e4207753b23208cf3d6770986030db7b78d0e8f3434b54cc7177"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "hidden": null,
          "native_kind": "SemanticTable"
        },
        "provenance": {
          "definition_hash": "6b0f856158e5e4207753b23208cf3d6770986030db7b78d0e8f3434b54cc7177",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "kind": "VISUAL",
        "label": "Invoiced Amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a/visual/definition%2Fpages%2Fc9b267726b645332927d%2Fvisuals%2F788498de9a325c7bb6a9%2Fvisual.json",
          "definition": {
            "bytes": 1360,
            "sha256": "c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a",
          "hidden": null,
          "native_kind": "ReportVisual"
        },
        "provenance": {
          "definition_hash": "c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db",
          "observed_at": "2026-10-13T17:34:44.997022Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a/part/definition%2Fpages%2Fc9b267726b645332927d%2Fvisuals%2F788498de9a325c7bb6a9%2Fvisual.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-24T08:27:13.767574Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "kind": "MEASURE",
        "label": "Invoiced Amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/measures/Invoiced%20Amount",
          "definition": {
            "bytes": 65,
            "sha256": "a26b55b6f4cb71659087dca20a9ec79fed75dc019546cf877c8da04323a8f13d",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/a26b55b6f4cb71659087dca20a9ec79fed75dc019546cf877c8da04323a8f13d"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "hidden": null,
          "native_kind": "Measure"
        },
        "provenance": {
          "definition_hash": "a26b55b6f4cb71659087dca20a9ec79fed75dc019546cf877c8da04323a8f13d",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/measures/Invoiced%20Amount",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "id": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "kind": "TABLE",
        "label": "gold.invoice_activity",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
          "definition_source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity"
        }
      },
      {
        "id": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
        "kind": "MODEL",
        "label": "Subscription Billing",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "definition_source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "072efb563a80031fb6ed6773a44b89662672682c6b0a16ef8c309b8e477485fb",
        "kind": "TABLE",
        "label": "invoices",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba/table/invoices",
          "definition": {
            "bytes": 2325,
            "sha256": "ab15c7afa25e113c01bfb1da86109ba2d05b7e565b1febe526d3bbe5c4fa9aa6",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/ab15c7afa25e113c01bfb1da86109ba2d05b7e565b1febe526d3bbe5c4fa9aa6"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba",
          "hidden": null,
          "native_kind": "LakehouseTable",
          "retained_metadata_hash_encoding": "SORTED_JSON_COMPACT_LEGACY"
        },
        "provenance": {
          "definition_hash": "ab15c7afa25e113c01bfb1da86109ba2d05b7e565b1febe526d3bbe5c4fa9aa6",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba/table/invoices",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-12T06:22:48.745954Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "18e99db0461c73d0ab6adfdd91203ddfa934583167f2a525f0f33f54cfa5b780",
        "kind": "QUERY_STEP",
        "label": "Declared SQL script",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9",
        "properties": {
          "definition": {
            "bytes": 7287,
            "sha256": "b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9",
          "execution_established": false,
          "expression": "CREATE VIEW [bronze].[invoices] AS SELECT [invoice_id],[account_id],[invoice_date],[amount],[status],source_row_version,source_modified_at_utc FROM [billing_bronze].[dbo].[invoices];",
          "language": "TSQL"
        },
        "provenance": {
          "definition_hash": "b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/7/text"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T07:41:50.583455Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "564adac92668939502d6e329320c18788ae803227e5ba70fa31a65e501f9612e",
        "kind": "TABLE",
        "label": "app.invoices",
        "owner": "sql://sql-orderops-9696025.database.windows.net/billingapp",
        "properties": {
          "asset_id": "sql://sql-orderops-9696025.database.windows.net/billingapp/object/1941581955",
          "definition": {
            "bytes": 1936,
            "sha256": "3a9f9060f6d5dd82a343bf33e2a8677046c0fecdac24025dc111a10fbbf8d3a7",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/3a9f9060f6d5dd82a343bf33e2a8677046c0fecdac24025dc111a10fbbf8d3a7"
          },
          "definition_source_owner": "sql://sql-orderops-9696025.database.windows.net/billingapp",
          "hidden": null,
          "native_kind": "SqlObject",
          "retained_metadata_hash_encoding": "SORTED_JSON_SPACED",
          "source_system_object": true
        },
        "provenance": {
          "definition_hash": "3a9f9060f6d5dd82a343bf33e2a8677046c0fecdac24025dc111a10fbbf8d3a7",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "sql://sql-orderops-9696025.database.windows.net/billingapp/object/1941581955",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "5824559a10e087711ceb49661818923333c1c87efa9ed0a2c80433e8f7f8c654",
        "kind": "QUERY_STEP",
        "label": "Declared SQL script",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e",
        "properties": {
          "definition": {
            "bytes": 7645,
            "sha256": "6a8b2cf63f4dd89c731612162da50b38507fbc9120d3b5d88507d8c0653ab6cf",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/6a8b2cf63f4dd89c731612162da50b38507fbc9120d3b5d88507d8c0653ab6cf"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e",
          "execution_established": false,
          "expression": "CREATE VIEW [bronze].[invoices] AS SELECT [invoice_id],[account_id],[invoice_date],[amount],[status],source_row_version,source_modified_at_utc FROM [billing_bronze].[dbo].[invoices];",
          "language": "TSQL"
        },
        "provenance": {
          "definition_hash": "6a8b2cf63f4dd89c731612162da50b38507fbc9120d3b5d88507d8c0653ab6cf",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/9/text"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T07:41:50.583455Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "5fd69c1b5817645bf256c653c3a6fdfb060ba4f6cd3b35c7f56324a93e5e9ad4",
        "kind": "COPY_ACTIVITY",
        "label": "Copy_invoices",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0",
        "properties": {
          "activity_type": "Copy",
          "definition": {
            "bytes": 21384,
            "sha256": "0389f86a2811c8e11ae84891984d39ea93e5a9fb631135b78d38b22c42b3574c",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/0389f86a2811c8e11ae84891984d39ea93e5a9fb631135b78d38b22c42b3574c"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0",
          "native_copy_binding": {
            "basis": "EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS",
            "connection_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/connection/93fd5fbf-5835-4756-bc59-bbf07302f321",
            "destination_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba/table/invoices",
            "native_destination": {
              "artifactId": "1853cbbb-06d1-4ae9-b378-370007c574ba",
              "workspaceId": "7d67bb36-04f6-4182-95aa-da5d515248fa"
            },
            "source_asset": "sql://sql-orderops-9696025.database.windows.net/billingapp/object/1941581955",
            "source_query": "SELECT [invoice_id],[account_id],[invoice_date],[amount],[status],CAST(source_row_version AS bigint) AS source_row_version,source_modified_at_utc FROM [app].[invoices]"
          }
        },
        "provenance": {
          "definition_hash": "0389f86a2811c8e11ae84891984d39ea93e5a9fb631135b78d38b22c42b3574c",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/4"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "cd24018f200d886024efd549c6a79f2cc38fd8665b0337f3d4b5c3d391788c22",
        "kind": "VIEW",
        "label": "bronze.invoices",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "definition": {
            "bytes": 7287,
            "sha256": "b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9",
          "execution_established": false,
          "schema_evidence": "CODE_DECLARED_NOT_OBSERVED",
          "script_database": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "script_name": "bronze.invoices"
        },
        "provenance": {
          "definition_hash": "b6cf6663945807581f86d5ce8432c465c4265cdf5db9fa438945d43f9ea65e09",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0/typeProperties/scripts/7/text"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T07:41:50.583455Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "56132b6a75761fcbacab05eb8d140b68e0c5ebbdc195e993a772d1f464db1463",
        "kind": "TABLE",
        "label": "dbo.load_run_audit",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/9cd1829b-7e2e-4340-8f59-fdf996033198",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/9cd1829b-7e2e-4340-8f59-fdf996033198/table/dbo.load_run_audit",
          "definition": {
            "bytes": 1402,
            "sha256": "e980b97b290eade70d549961586aa27e43aa5e199de1ec36021cf92a5533568c",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/e980b97b290eade70d549961586aa27e43aa5e199de1ec36021cf92a5533568c"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/9cd1829b-7e2e-4340-8f59-fdf996033198",
          "hidden": null,
          "native_kind": "WarehouseTable",
          "retained_metadata_hash_encoding": "SORTED_JSON_SPACED"
        },
        "provenance": {
          "definition_hash": "e980b97b290eade70d549961586aa27e43aa5e199de1ec36021cf92a5533568c",
          "observed_at": "2026-10-12T06:22:48.745954Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/9cd1829b-7e2e-4340-8f59-fdf996033198/table/dbo.load_run_audit",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-12T06:22:48.745954Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      }
    ],
    "stops": [
      {
        "node": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "reason": "No retained upstream dependency is declared for this object."
      },
      {
        "node": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "reason": "No retained upstream dependency is declared for this object."
      }
    ],
    "truncated": false,
    "unavailable_owners": {
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89": {
        "at": "2026-10-28T06:03:11.630566Z",
        "failure": {
          "errno": null,
          "error_type": "RuntimeError",
          "line": 88,
          "message": "GRAPH_DEFINITION_KIND_UNAVAILABLE",
          "message_redacted": false,
          "module": "graph_change_collector.py"
        },
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "status": "UNAVAILABLE"
      },
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188": {
        "at": "2026-10-28T06:03:20.599000Z",
        "failure": {
          "errno": null,
          "error_type": "MetadataUnavailable",
          "http_status": 404,
          "line": 106,
          "message": "Metadata provider request unavailable",
          "message_redacted": false,
          "module": "metadata_auth.py",
          "provider_code": "EntityNotFound"
        },
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "status": "UNAVAILABLE"
      },
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a": {
        "at": "2026-10-28T06:03:23.952432Z",
        "failure": {
          "errno": null,
          "error_type": "MetadataUnavailable",
          "http_status": 404,
          "line": 106,
          "message": "Metadata provider request unavailable",
          "message_redacted": false,
          "module": "metadata_auth.py",
          "provider_code": "EntityNotFound"
        },
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "status": "UNAVAILABLE"
      }
    }
  }
}
```

Triage:
```json
{
  "facts": [
    {
      "cached": false,
      "check": "MODEL_REFRESH",
      "observed_at": "2026-10-28T06:21:43.643661Z",
      "source": "facts-ledger",
      "state": "OBSERVED_NEGATIVE",
      "value": [
        {
          "collected_at": "2026-10-28T06:21:43.643661Z",
          "freshness": "CURRENT",
          "id": "65fd28349e41df4f2669d89da23dd1de597e5fd5a2db9b05aa481c3c0eeefd78",
          "kind": "RUN_HISTORY",
          "observed_at": "2026-10-28T06:21:43.643661Z",
          "provenance": {
            "collector": "microsoft-runtime:8b8add39b1b3bbf05051200684642bc68ee0c9695580165440fd17fca6875167",
            "evidence_ids": [
              "sha256:5518e69e59a63ae9599830ab0ea2552a1c16ca90d74383d71cc10ca34d69ac77"
            ],
            "locator": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED_NEGATIVE",
          "subject": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
          "value": {
            "listing_complete": true,
            "runs": []
          }
        }
      ]
    },
    {
      "cached": false,
      "check": "REFRESH_SCHEDULE",
      "observed_at": "2026-10-28T06:21:43.643661Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T06:21:43.643661Z",
          "freshness": "CURRENT",
          "id": "bf606243fbce354e0c2b91ac6a1f0b6715f84ac09d309b0fab4a9b9e200e6036",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T06:21:43.643661Z",
          "provenance": {
            "collector": "microsoft-runtime:8b8add39b1b3bbf05051200684642bc68ee0c9695580165440fd17fca6875167",
            "evidence_ids": [
              "sha256:82b1cbfbfff465c33982765807dc9f50a201edeba662730817051b285b134874"
            ],
            "locator": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/7d67bb36-04f6-4182-95aa-da5d515248fa/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "19:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        }
      ]
    },
    {
      "check": "AUTOMATIC_UPDATES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:AUTOMATIC_UPDATES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "JOB_RUNS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:JOB_RUNS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "LAYER_FRESHNESS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:LAYER_FRESHNESS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SOURCE_CHANGES",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:SOURCE_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "NEXT_LOAD",
      "observed_at": "2026-10-28T06:21:43.643661Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T06:21:43.643661Z",
          "freshness": "CURRENT",
          "id": "bf606243fbce354e0c2b91ac6a1f0b6715f84ac09d309b0fab4a9b9e200e6036",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T06:21:43.643661Z",
          "provenance": {
            "collector": "microsoft-runtime:8b8add39b1b3bbf05051200684642bc68ee0c9695580165440fd17fca6875167",
            "evidence_ids": [
              "sha256:82b1cbfbfff465c33982765807dc9f50a201edeba662730817051b285b134874"
            ],
            "locator": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/7d67bb36-04f6-4182-95aa-da5d515248fa/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "19:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        }
      ]
    },
    {
      "check": "CONNECTION_MODE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:CONNECTION_MODE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SECURITY_PRESENCE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:SECURITY_PRESENCE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "DEFINITION_CHANGES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:DEFINITION_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    }
  ],
  "path": [
    "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
    "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
    "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
    "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
    "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
    "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
    "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1"
  ],
  "refresh_operations": 10,
  "what_triage_suggests": "Triage has unavailable checks (AUTOMATIC_UPDATES, JOB_RUNS, LAYER_FRESHNESS, SOURCE_CHANGES, CONNECTION_MODE, SECURITY_PRESENCE, DEFINITION_CHANGES); this does not establish that those mechanisms are absent."
}
```

Tool decisions:
```json
[
  {
    "arguments": {
      "layer": "native:4aae8dbb1d373ebef783",
      "purpose": "recreate",
      "query": "EVALUATE ROW(\"Invoiced Amount\", [Invoiced Amount], \"rows\", COUNTROWS(Billing), \"max_invoice_date\", MAX(Billing[invoice_date]))"
    },
    "tool": "run_dax",
    "tool_use_id": "toolu_018eEBfyL3GTXsNNDEg4GgNo",
    "turn": 1
  },
  {
    "arguments": {
      "layer": "native:f87556d4485196602461",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, COUNT(*) AS rows_observed, MAX([invoice_date]) AS max_invoice_date FROM [gold].[invoice_activity]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01DghjiwDKdwbvo9cpDNyvbn",
    "turn": 1
  },
  {
    "arguments": {
      "node": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
    },
    "tool": "get_refresh_history",
    "tool_use_id": "toolu_016hRdACPbEsfTxaKGb1hsoK",
    "turn": 1
  },
  {
    "arguments": {
      "node": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
      "operation": "PRODUCERS"
    },
    "tool": "get_lineage",
    "tool_use_id": "toolu_01SqqH9p3vzq51f4SaaEvXpc",
    "turn": 1
  },
  {
    "arguments": {
      "words": "billing warehouse transformation pipeline stored procedure invoice_activity bronze job history"
    },
    "tool": "list_candidates",
    "tool_use_id": "toolu_01Mduzd63BkcHFHs5CDUMN1p",
    "turn": 4
  },
  {
    "arguments": {
      "words": "invoices bronze invoice load procedure pipeline run"
    },
    "tool": "list_candidates",
    "tool_use_id": "toolu_01Lrddk4VDkJvQRVjJYprdBi",
    "turn": 7
  },
  {
    "arguments": {
      "layer": "native:f87556d4485196602461",
      "purpose": "lookup",
      "query": "SELECT TOP 20 s.name AS schema_name, o.name AS object_name, o.type_desc, o.modify_date FROM sys.objects o JOIN sys.schemas s ON s.schema_id = o.schema_id WHERE o.type IN ('P','V','U') ORDER BY o.modify_date DESC"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01Hkci1RMsEdJU7yArabYCdm",
    "turn": 7
  },
  {
    "arguments": {
      "node": "cd24018f200d886024efd549c6a79f2cc38fd8665b0337f3d4b5c3d391788c22",
      "operation": "PATH"
    },
    "tool": "get_lineage",
    "tool_use_id": "toolu_01CgPBESBJgjXFHS9goKxepZ",
    "turn": 10
  },
  {
    "arguments": {
      "node": "56132b6a75761fcbacab05eb8d140b68e0c5ebbdc195e993a772d1f464db1463",
      "operation": "PATH"
    },
    "tool": "get_lineage",
    "tool_use_id": "toolu_01FB8xpmQ3uaNjv487LZAbc8",
    "turn": 10
  },
  {
    "arguments": {
      "node": "cd24018f200d886024efd549c6a79f2cc38fd8665b0337f3d4b5c3d391788c22"
    },
    "tool": "get_definition",
    "tool_use_id": "toolu_01Vz45WgyRLocm4fuUdaCFJe",
    "turn": 10
  },
  {
    "arguments": {
      "node": "cd24018f200d886024efd549c6a79f2cc38fd8665b0337f3d4b5c3d391788c22"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_018KujiqTfEKrp8FjTE5g6kD",
    "turn": 13
  },
  {
    "arguments": {
      "layer": "native:bc3914e8dae9e68e7163",
      "purpose": "history",
      "query": "SELECT TOP 20 run_id, pipeline_name, status, rows_read, rows_written, accounting_state, start_time_utc, end_time_utc, high_watermark FROM dbo.load_run_audit ORDER BY start_time_utc DESC"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_014vMCvhLQ6Jth2Fsdh1AK9Y",
    "turn": 13
  },
  {
    "arguments": {
      "layer": "native:ac3ebe915b1cc00c45d7",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, COUNT(*) AS rows_observed, MAX([invoice_date]) AS max_invoice_date, MAX([source_modified_at_utc]) AS max_modified FROM [dbo].[invoices]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01WktJC5R8m6BoaYS4Rk8QyZ",
    "turn": 13
  },
  {
    "arguments": {
      "layer": "native:db47aa505c8c14efec29",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, COUNT(*) AS rows_observed, MAX([invoice_date]) AS max_invoice_date, MAX([source_modified_at_utc]) AS max_modified FROM [app].[invoices]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_011bTXNjfvHCARJQ1ZWMZuSW",
    "turn": 13
  },
  {
    "arguments": {
      "node": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_012dHrS6HbTUCagnbE3yv5Lk",
    "turn": 16
  }
]
```

Queries:
```json
[
  {
    "asset_ids": [
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing",
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/invoice_date",
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/measures/Invoiced%20Amount"
    ],
    "duration_seconds": 11.482870622000064,
    "executed_text": "EVALUATE TOPN(251,ROW(\"Invoiced Amount\",[Invoiced Amount],\"rows\",COUNTROWS(Billing),\"max_invoice_date\",MAX(Billing[invoice_date])))",
    "id": "query:af218d97b40a5fa42330fb33dab6ecb3feb73968404870ad81f458d338248199:1",
    "layer": "native:4aae8dbb1d373ebef783",
    "parameters": [],
    "purpose": "recreate",
    "result": {
      "rows": [
        {
          "[Invoiced Amount]": 950,
          "[max_invoice_date]": "2026-10-01T00:00:00",
          "[rows]": 5
        }
      ],
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "768c09ce7732d94e86a1cb7b15cfaca800790def6ed32f5e8a21996794489f75",
    "row_count": 1,
    "signature": "af218d97b40a5fa42330fb33dab6ecb3feb73968404870ad81f458d338248199",
    "status": "SUCCEEDED",
    "text": "EVALUATE ROW(\"Invoiced Amount\", [Invoiced Amount], \"rows\", COUNTROWS(Billing), \"max_invoice_date\", MAX(Billing[invoice_date]))",
    "time": "2026-10-28T06:21:57.633301+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity"
    ],
    "duration_seconds": 8.618429688999981,
    "executed_text": "SELECT TOP 251 SUM(CAST([invoice_activity].[amount] AS BIGINT)) AS [invoiced_amount], COUNT(*) AS [rows_observed], MAX([invoice_activity].[invoice_date]) AS [max_invoice_date] FROM [gold].[invoice_activity] AS [invoice_activity]",
    "id": "query:eb0a6a56597dd8f881f57a31589ffd5bcf8e91fb244fee5ffdb6a400bb2825f6:2",
    "layer": "native:f87556d4485196602461",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "invoiced_amount": "Int64",
        "max_invoice_date": "DateTime",
        "rows_observed": "Int64"
      },
      "execution_identity": {
        "database": "billing_serving",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "invoiced_amount": "950",
          "max_invoice_date": "2026-10-01",
          "rows_observed": "5"
        }
      ]
    },
    "result_digest": "9bd1e64a4f8477fb9245c7757b56cbe2b1f0b48b252d208dd3dea7392b4641d7",
    "row_count": 1,
    "signature": "eb0a6a56597dd8f881f57a31589ffd5bcf8e91fb244fee5ffdb6a400bb2825f6",
    "status": "SUCCEEDED",
    "text": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, COUNT(*) AS rows_observed, MAX([invoice_date]) AS max_invoice_date FROM [gold].[invoice_activity]",
    "time": "2026-10-28T06:22:09.369952+00:00",
    "truncated": false
  },
  {
    "duration_seconds": 0,
    "error": "SQL object unavailable or view dependencies not validated",
    "error_type": "QueryRejection",
    "failure_class": "wrong column or table",
    "id": "query:82ba092806fe06c9d423feb229d34b5969876832f61b5a818cb23b50eb49ea54:3",
    "layer": "native:f87556d4485196602461",
    "native_dispatched": false,
    "purpose": "lookup",
    "result_digest": null,
    "row_count": null,
    "schema_slice": [
      {
        "columns": [
          {
            "collation_name": null,
            "data_type": "int",
            "name": "invoice_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "account_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "plan_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "date",
            "name": "invoice_date",
            "observed_type": "date"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "amount",
            "observed_type": "int"
          },
          {
            "collation_name": "Latin1_General_100_BIN2_UTF8",
            "data_type": "varchar",
            "name": "status",
            "observed_type": "varchar"
          }
        ],
        "id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
        "name": "invoice_activity",
        "schema_name": "gold",
        "type_desc": "USER_TABLE"
      }
    ],
    "signature": "82ba092806fe06c9d423feb229d34b5969876832f61b5a818cb23b50eb49ea54",
    "status": "ERROR",
    "text": "SELECT TOP 20 s.name AS schema_name, o.name AS object_name, o.type_desc, o.modify_date FROM sys.objects o JOIN sys.schemas s ON s.schema_id = o.schema_id WHERE o.type IN ('P','V','U') ORDER BY o.modify_date DESC",
    "time": "2026-10-28T06:22:35.299499+00:00"
  },
  {
    "asset_ids": [
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/9cd1829b-7e2e-4340-8f59-fdf996033198/table/dbo.load_run_audit"
    ],
    "duration_seconds": 16.039217263999944,
    "executed_text": "SELECT TOP 20 [load_run_audit].[run_id] AS [run_id], [load_run_audit].[pipeline_name] AS [pipeline_name], [load_run_audit].[status] AS [status], [load_run_audit].[rows_read] AS [rows_read], [load_run_audit].[rows_written] AS [rows_written], [load_run_audit].[accounting_state] AS [accounting_state], [load_run_audit].[start_time_utc] AS [start_time_utc], [load_run_audit].[end_time_utc] AS [end_time_utc], [load_run_audit].[high_watermark] AS [high_watermark] FROM [dbo].[load_run_audit] AS [load_run_audit] ORDER BY [start_time_utc] DESC",
    "id": "query:89a3fff720af43d3727a83b3fd069c4e36dc0eff46e6cfd1cefc241f8c3e2173:4",
    "layer": "native:bc3914e8dae9e68e7163",
    "parameters": [],
    "purpose": "history",
    "result": {
      "column_types": {
        "accounting_state": "String",
        "end_time_utc": "String",
        "high_watermark": "String",
        "pipeline_name": "String",
        "rows_read": "Int64",
        "rows_written": "Int64",
        "run_id": "String",
        "start_time_utc": "String",
        "status": "String"
      },
      "execution_identity": {
        "database": "billing_ops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "accounting_state": "OBSERVED_COPY_OUTPUT",
          "end_time_utc": "2026-10-09T21:54:56.6775595",
          "high_watermark": null,
          "pipeline_name": "fc8438fd-2c18-4196-9191-33e26481e2e0",
          "rows_read": "26",
          "rows_written": "26",
          "run_id": "e82f690b-6865-48b5-a38c-9a116cd9c132",
          "start_time_utc": "2026-10-09T21:51:03.1830083Z",
          "status": "Succeeded"
        }
      ]
    },
    "result_digest": "3bc8ab902f07870146ce8ca1030281b9c1b0d1d7b31de7331702fd87eb951559",
    "row_count": 1,
    "signature": "89a3fff720af43d3727a83b3fd069c4e36dc0eff46e6cfd1cefc241f8c3e2173",
    "status": "SUCCEEDED",
    "text": "SELECT TOP 20 run_id, pipeline_name, status, rows_read, rows_written, accounting_state, start_time_utc, end_time_utc, high_watermark FROM dbo.load_run_audit ORDER BY start_time_utc DESC",
    "time": "2026-10-28T06:23:17.141150+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/1853cbbb-06d1-4ae9-b378-370007c574ba/table/invoices"
    ],
    "duration_seconds": 12.495990182000014,
    "executed_text": "SELECT TOP 251 SUM(CAST([invoices].[amount] AS BIGINT)) AS [invoiced_amount], COUNT(*) AS [rows_observed], MAX([invoices].[invoice_date]) AS [max_invoice_date], MAX([invoices].[source_modified_at_utc]) AS [max_modified] FROM [dbo].[invoices] AS [invoices]",
    "id": "query:a0003b4ea20aa9bf2035a3a69a6e8866c2e49a503043f6d437206b4b34b9d3ca:5",
    "layer": "native:ac3ebe915b1cc00c45d7",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "invoiced_amount": "Int64",
        "max_invoice_date": "DateTime",
        "max_modified": "DateTime",
        "rows_observed": "Int64"
      },
      "execution_identity": {
        "database": "billing_bronze",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "invoiced_amount": "700",
          "max_invoice_date": "2026-10-01",
          "max_modified": "2026-10-09 21:42:24.128711",
          "rows_observed": "4"
        }
      ]
    },
    "result_digest": "cbe01cb0338cc410b7a3fd52e2435e0a392671fd2622b6877473de31231d01cf",
    "row_count": 1,
    "signature": "a0003b4ea20aa9bf2035a3a69a6e8866c2e49a503043f6d437206b4b34b9d3ca",
    "status": "SUCCEEDED",
    "text": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, COUNT(*) AS rows_observed, MAX([invoice_date]) AS max_invoice_date, MAX([source_modified_at_utc]) AS max_modified FROM [dbo].[invoices]",
    "time": "2026-10-28T06:23:33.562782+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/billingapp/object/1941581955"
    ],
    "duration_seconds": 3.1794493909999346,
    "executed_text": "SELECT TOP 251 SUM(CAST([invoices].[amount] AS BIGINT)) AS [invoiced_amount], COUNT(*) AS [rows_observed], MAX([invoices].[invoice_date]) AS [max_invoice_date], MAX([invoices].[source_modified_at_utc]) AS [max_modified] FROM [app].[invoices] AS [invoices]",
    "id": "query:0d13e699ed49e6f09872497c31b76b96a8436c203b5fd5dccb5d1ba78bed5002:6",
    "layer": "native:db47aa505c8c14efec29",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "invoiced_amount": "Int64",
        "max_invoice_date": "DateTime",
        "max_modified": "DateTime",
        "rows_observed": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T06:23:49.343472+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T06:23:46.643843+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "billingapp",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "invoiced_amount": "700",
          "max_invoice_date": "2026-10-01",
          "max_modified": "2026-10-09 21:42:24.128711",
          "rows_observed": "4"
        }
      ]
    },
    "result_digest": "2fed1e78ac4875f097bfcbacb4bcc533fa104e72116dc79d524daf3b39af62be",
    "row_count": 1,
    "signature": "0d13e699ed49e6f09872497c31b76b96a8436c203b5fd5dccb5d1ba78bed5002",
    "status": "SUCCEEDED",
    "text": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, COUNT(*) AS rows_observed, MAX([invoice_date]) AS max_invoice_date, MAX([source_modified_at_utc]) AS max_modified FROM [app].[invoices]",
    "time": "2026-10-28T06:23:46.436400+00:00",
    "truncated": false
  }
]
```

Final answer:
```json
"The checks did not establish a cause within this ticket’s limits."
```

Sealed expected:
```json
{
  "case_id": "v2-failed-billing-transform",
  "cause": "Latest failed native transform run with name/run ID/start/end/error; no invented successful completion.",
  "estate": "billing",
  "expectation_basis": "Practice source literals, declared definitions and reversible scenario plan; never an engine answer.",
  "fixture": "failed-billing",
  "id": "v2-failed-billing-transform-v1",
  "layer": "billing transformation pipeline",
  "split": "DEV",
  "variation": "detailed support question",
  "verdict": "failed job"
}
```

Saved checkpoint SHA-256: f5dda9f77f33795cf942922f2724e333b0e3c9761a4a41e38c710f5931cd280d. Only recorded tool choices are shown; no new queries or model calls.

### v2-failed-billing-transform-v2
Expected: verdict 'failed job' in the billing transformation pipeline, with the cause being the latest failed native transform run (name, run ID, start/end time, error). The delivered answer is UNRESOLVED (TOOL_OR_TIME_LIMIT). It names no verdict, no layer or split point, and no cause, so all three score zero. The grading rule also says an unresolved budget stop is not a successful technical answer. The answer is not harmful: it honestly says no cause was established and doesn't invent a successful run or a wrong cause. Where it went wrong: the ticket explicitly says the transformation job shows Failed, but the JOB_RUNS triage fact was UNAVAILABLE (FRESH_PATH_FACT_NOT_AVAILABLE). The investigation then compared the semantic model with gold.invoice_activity (both 950 / 5 rows / max 2026-10-01) and tried to query silver.invoices and bronze.invoices, which don't exist. It never looked at the pipeline run history. Handoff quality is 1. The queries are recorded word for word and can be rerun, and the stopping point is clearly stated. However, the next checks only say to review the queries rejected for missing silver/bronze objects. They don't suggest the obvious next step: get the latest run status and error for the Billing Warehouse transformation job, even though the ticket points straight to it. Read and act on the current path run or freshness fact first.

Intake:
```json
{
  "classified_issue_type": "DATA_LOOKS_OLD",
  "compared_with": {
    "kind": "NOTHING"
  },
  "description": "The Billing Warehouse transformation job shows Failed on the latest run. Is the Invoiced Amount on the Subscription Billing page out of date because of this?",
  "issue_type": "DATA_LOOKS_OLD",
  "measure_candidates": [
    {
      "id": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
      "name": "Invoiced Amount"
    }
  ],
  "page": "69271186d3ccfbba0cccf5a28033b28f779e8c46e00b6f45adad14d97507539e",
  "report": "44dc6baac12f79e0f4a1c4474c63bb2867262137212e4061f4ce0882c4a90257",
  "status": "READY",
  "version": "IntakeRequest/1",
  "visual": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b"
}
```

Target:
```json
{
  "layers": {
    "native:4aae8dbb1d373ebef783": {
      "dialect": "DAX",
      "label": "Subscription Billing"
    },
    "native:f87556d4485196602461": {
      "dialect": "T-SQL",
      "label": "billing_serving"
    }
  },
  "path": {
    "as_of": null,
    "declared_route_bridges": [
      {
        "column_bindings": [
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/invoice_id",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/invoice_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/account_id",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/account_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/plan_id",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/plan_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/invoice_date",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/invoice_date"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/status",
            "semantic_column": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/status"
          }
        ],
        "confidence": "DECLARED",
        "definition_asset": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/part/model.bim",
        "definition_hash": "7565c9db1f3083abd3e08cf3d16d74e0a8f93f5c6efd1119ef278dc5db152db1",
        "graph_nodes": [
          "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
          "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd"
        ],
        "literal_expression": "let database = Sql.Database(\"i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com\", \"406dcb89-0526-4f48-bb77-397d52471c89\") in database",
        "native_ownership": [],
        "partition_source": {
          "entityName": "invoice_activity",
          "expressionSource": "BillingServingSource",
          "schemaName": "gold",
          "type": "entity"
        },
        "physical_table": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
        "qualification": "Declared route only; value agreement and aligned snapshots are not implied.",
        "semantic_table": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing"
      }
    ],
    "edges": [
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "3a6ba8ce4d7efd8c326192d087b8dfb05c43ca5209cf86cf5fb79cdbd9e4534c",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "binding_kind": "DIRECTLAKE_ENTITY",
          "catalog_id": "406dcb89-0526-4f48-bb77-397d52471c89",
          "container_asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "container_binding": {
            "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "container_bindings": [
            {
              "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
              "observed_at": "2026-10-12T06:22:48.745954Z",
              "source": "STATIC_DEFINITION",
              "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
              "span": {
                "kind": "JSON_POINTER",
                "path": ""
              }
            }
          ],
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "entity": "invoice_activity",
          "expression_pointer": "/model/expressions/0",
          "expression_source": "BillingServingSource",
          "physical_definition": {
            "definition_hash": "b32a45a2bf55337bb1a7b5ad78602572341ad2b6ebb249dc7657a32d3fb9e876",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "schema": "gold",
          "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com"
        },
        "provenance": {
          "definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/part/model.bim",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/model/tables/5/partitions"
          }
        },
        "source": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "target": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "unknown": null,
        "valid_from": "2026-10-27T10:08:38.481811Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "5b1782b90d25ef08907c1313aa35b95c128b4ee89d888d8371860a27ea6d1804",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "completeness": "ROW_ONLY",
          "definition": {
            "bytes": 8289,
            "sha256": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c"
          },
          "model_definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "native_row_hash": "f46ed22f744430f4f9406a42a056fdac7f90072a2f613406dbf2866e92b476f0"
        },
        "provenance": {
          "definition_hash": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "ENGINE_DEPENDENCY",
          "source_id": "24dc7f097c6839881270308e2651f9937a44cdfcbaa0d58448f2364a4d6b8627",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/rows/21"
          }
        },
        "source": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "target": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "62f0613f9f6894eaf7b5e2c5047953bea360ce5bfb26ff07c9cc1e26a9b073ac",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a",
        "properties": {
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a"
        },
        "provenance": {
          "definition_hash": "c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db",
          "observed_at": "2026-10-13T17:34:44.997022Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a/part/definition%2Fpages%2Fc9b267726b645332927d%2Fvisuals%2F788498de9a325c7bb6a9%2Fvisual.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/queryState/Values/projections/0/field/Measure"
          }
        },
        "source": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "target": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "unknown": null,
        "valid_from": "2026-10-13T17:34:44.997022Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "6a48e802bd984e9779fdd00a33e71b6841ab618cd095b9bcbcfdf73b2a654aae",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "completeness": "ROW_ONLY",
          "definition": {
            "bytes": 8289,
            "sha256": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c"
          },
          "model_definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "native_row_hash": "ad0462db0652c3ca7c3eb37d57ab7ff55057e3edc0d3374449f3517a4d07d6e5"
        },
        "provenance": {
          "definition_hash": "fb3cd6f0527e4a3b6621e12a0a081d9d43b26f9af8b78693b9cb841b5edd1d8c",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "ENGINE_DEPENDENCY",
          "source_id": "24dc7f097c6839881270308e2651f9937a44cdfcbaa0d58448f2364a4d6b8627",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/rows/20"
          }
        },
        "source": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "target": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "d8908c0765aacbfb72890a1818efd03f1efd4d224259f81635ba81fa609075dc",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "binding_kind": "DIRECTLAKE_ENTITY",
          "catalog_id": "406dcb89-0526-4f48-bb77-397d52471c89",
          "container_asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "container_binding": {
            "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "container_bindings": [
            {
              "definition_hash": "3e654caa0eaa113e180f9997155d8a102b13a78bc4e15ddaccebc4e82564bdc1",
              "observed_at": "2026-10-12T06:22:48.745954Z",
              "source": "STATIC_DEFINITION",
              "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
              "span": {
                "kind": "JSON_POINTER",
                "path": ""
              }
            }
          ],
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "entity": "invoice_activity",
          "expression_pointer": "/model/expressions/0",
          "expression_source": "BillingServingSource",
          "physical_column_definition": {
            "definition_hash": "e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d",
            "observed_at": "2026-10-13T17:41:15.000678Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "physical_definition": {
            "definition_hash": "b32a45a2bf55337bb1a7b5ad78602572341ad2b6ebb249dc7657a32d3fb9e876",
            "observed_at": "2026-10-12T06:22:48.745954Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "schema": "gold",
          "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com",
          "source_column": "amount"
        },
        "provenance": {
          "definition_hash": "73f6ea95a163d1b9ceb5e9d7eec29653c05c83d0e19f879daeac7b9b5a4823b1",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/part/model.bim",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/model/tables/5/columns/4/sourceColumn"
          }
        },
        "source": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "target": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "unknown": null,
        "valid_from": "2026-10-27T10:08:38.481811Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      }
    ],
    "estate": "billing",
    "nodes": [
      {
        "confidence": "DECLARED",
        "id": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "kind": "COLUMN",
        "label": "amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
          "definition": {
            "bytes": 249,
            "sha256": "e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
          "hidden": null,
          "native_kind": "WarehouseColumn"
        },
        "provenance": {
          "definition_hash": "e1906c3b8a1609c4564d8aac4481e9fbfe04c6b65ec9220c1b37169bd9ed8f9d",
          "observed_at": "2026-10-13T17:41:15.000678Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity/column/amount",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:41:15.000678Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "kind": "COLUMN",
        "label": "amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount",
          "dataType": "int64",
          "definition": {
            "bytes": 88,
            "sha256": "b1f9170e2c11581cbb5f36f01e51d440deff9cc017c473c9a2e93af6501741f5",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/b1f9170e2c11581cbb5f36f01e51d440deff9cc017c473c9a2e93af6501741f5"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "hidden": null,
          "native_kind": "SemanticColumn",
          "sourceColumn": "amount"
        },
        "provenance": {
          "definition_hash": "b1f9170e2c11581cbb5f36f01e51d440deff9cc017c473c9a2e93af6501741f5",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "kind": "TABLE",
        "label": "Billing",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing",
          "definition": {
            "bytes": 1459,
            "sha256": "6b0f856158e5e4207753b23208cf3d6770986030db7b78d0e8f3434b54cc7177",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/6b0f856158e5e4207753b23208cf3d6770986030db7b78d0e8f3434b54cc7177"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "hidden": null,
          "native_kind": "SemanticTable"
        },
        "provenance": {
          "definition_hash": "6b0f856158e5e4207753b23208cf3d6770986030db7b78d0e8f3434b54cc7177",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "kind": "VISUAL",
        "label": "Invoiced Amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a/visual/definition%2Fpages%2Fc9b267726b645332927d%2Fvisuals%2F788498de9a325c7bb6a9%2Fvisual.json",
          "definition": {
            "bytes": 1360,
            "sha256": "c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a",
          "hidden": null,
          "native_kind": "ReportVisual"
        },
        "provenance": {
          "definition_hash": "c7a45e237c6350ece678a65742b3a13db4ea3e874521898574f52d08de4e70db",
          "observed_at": "2026-10-13T17:34:44.997022Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a/part/definition%2Fpages%2Fc9b267726b645332927d%2Fvisuals%2F788498de9a325c7bb6a9%2Fvisual.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-24T08:27:13.767574Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "kind": "MEASURE",
        "label": "Invoiced Amount",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/measures/Invoiced%20Amount",
          "definition": {
            "bytes": 65,
            "sha256": "a26b55b6f4cb71659087dca20a9ec79fed75dc019546cf877c8da04323a8f13d",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/a26b55b6f4cb71659087dca20a9ec79fed75dc019546cf877c8da04323a8f13d"
          },
          "definition_source_owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "hidden": null,
          "native_kind": "Measure"
        },
        "provenance": {
          "definition_hash": "a26b55b6f4cb71659087dca20a9ec79fed75dc019546cf877c8da04323a8f13d",
          "observed_at": "2026-10-13T17:33:39.523856Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/measures/Invoiced%20Amount",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:33:39.523856Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "id": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "kind": "TABLE",
        "label": "gold.invoice_activity",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
          "definition_source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity"
        }
      },
      {
        "id": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
        "kind": "MODEL",
        "label": "Subscription Billing",
        "owner": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
        "properties": {
          "asset_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188",
          "definition_source_id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188"
        }
      }
    ],
    "stops": [
      {
        "node": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
        "reason": "No retained upstream dependency is declared for this object."
      },
      {
        "node": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
        "reason": "No retained upstream dependency is declared for this object."
      }
    ],
    "truncated": false,
    "unavailable_owners": {
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89": {
        "at": "2026-10-28T06:03:11.630566Z",
        "failure": {
          "errno": null,
          "error_type": "RuntimeError",
          "line": 88,
          "message": "GRAPH_DEFINITION_KIND_UNAVAILABLE",
          "message_redacted": false,
          "module": "graph_change_collector.py"
        },
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "status": "UNAVAILABLE"
      },
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188": {
        "at": "2026-10-28T06:03:20.599000Z",
        "failure": {
          "errno": null,
          "error_type": "MetadataUnavailable",
          "http_status": 404,
          "line": 106,
          "message": "Metadata provider request unavailable",
          "message_redacted": false,
          "module": "metadata_auth.py",
          "provider_code": "EntityNotFound"
        },
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "status": "UNAVAILABLE"
      },
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/e995a2cf-7748-45f7-bde1-47510ddc509a": {
        "at": "2026-10-28T06:03:23.952432Z",
        "failure": {
          "errno": null,
          "error_type": "MetadataUnavailable",
          "http_status": 404,
          "line": 106,
          "message": "Metadata provider request unavailable",
          "message_redacted": false,
          "module": "metadata_auth.py",
          "provider_code": "EntityNotFound"
        },
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "status": "UNAVAILABLE"
      }
    }
  }
}
```

Triage:
```json
{
  "facts": [
    {
      "cached": true,
      "check": "MODEL_REFRESH",
      "observed_at": "2026-10-28T06:22:18.194285Z",
      "source": "facts-ledger",
      "state": "OBSERVED_NEGATIVE",
      "value": [
        {
          "collected_at": "2026-10-28T06:22:18.194285Z",
          "freshness": "CURRENT",
          "id": "f55f20bf6ff328d22705b4043ea996e110df3eda334d3be5ee99988b8814b942",
          "kind": "RUN_HISTORY",
          "observed_at": "2026-10-28T06:22:18.194285Z",
          "provenance": {
            "collector": "microsoft-runtime:8b8add39b1b3bbf05051200684642bc68ee0c9695580165440fd17fca6875167",
            "evidence_ids": [
              "sha256:5af1889bed514118e966f6e5667727c75b7e45bc338836793d373e3b2046235b"
            ],
            "locator": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED_NEGATIVE",
          "subject": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
          "value": {
            "listing_complete": true,
            "runs": []
          }
        }
      ]
    },
    {
      "cached": true,
      "check": "REFRESH_SCHEDULE",
      "observed_at": "2026-10-28T06:22:18.194285Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T06:22:18.194285Z",
          "freshness": "CURRENT",
          "id": "5364674dabc7d981b7989ddd96151fdd04d0a85f8d0207c61da08b0fc2e9374a",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T06:22:18.194285Z",
          "provenance": {
            "collector": "microsoft-runtime:8b8add39b1b3bbf05051200684642bc68ee0c9695580165440fd17fca6875167",
            "evidence_ids": [
              "sha256:a141b182fa6e710f7ad086c88e702f3d73a0a158301326e03f14360e093b4e52"
            ],
            "locator": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/7d67bb36-04f6-4182-95aa-da5d515248fa/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "19:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        }
      ]
    },
    {
      "check": "AUTOMATIC_UPDATES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:AUTOMATIC_UPDATES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "JOB_RUNS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:JOB_RUNS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "LAYER_FRESHNESS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:LAYER_FRESHNESS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SOURCE_CHANGES",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:SOURCE_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "NEXT_LOAD",
      "observed_at": "2026-10-28T06:25:06.836417Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T06:25:06.836417Z",
          "freshness": "CURRENT",
          "id": "acce0facb9594bc9f16cdb9bdedce6b90140dc7aea917b378a29e8076f930a25",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T06:25:06.836417Z",
          "provenance": {
            "collector": "microsoft-runtime:8b8add39b1b3bbf05051200684642bc68ee0c9695580165440fd17fca6875167",
            "evidence_ids": [
              "sha256:387d3b298ba159e8d6315019426f5dec299aeedefb66bef074d154a5f91220f1"
            ],
            "locator": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/7d67bb36-04f6-4182-95aa-da5d515248fa/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "19:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        }
      ]
    },
    {
      "check": "CONNECTION_MODE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:CONNECTION_MODE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SECURITY_PRESENCE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:SECURITY_PRESENCE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "DEFINITION_CHANGES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:DEFINITION_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    }
  ],
  "path": [
    "191cfb575489c32fd0d75d43d1edbaa3929cd88cd07d8823c2360d32d42237bd",
    "43a0c02d3d2889262b20a0d477b2bc41fa5985831578b1ece2f691c1da18fa5b",
    "65cb9c1f1a3864da8e2e4f0a23f759fe3edf25c3ea2b033b3b4ea6016f6469f7",
    "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8",
    "a4e07b71d13d1ba73eca555ceafa3544425363d1f6f19e0f69ff9722987e4d4b",
    "d2134e5898e279c2662565bf22d60de79ec7b5516ae09128fade437079f4b6fe",
    "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1"
  ],
  "refresh_operations": 8,
  "what_triage_suggests": "Triage has unavailable checks (AUTOMATIC_UPDATES, JOB_RUNS, LAYER_FRESHNESS, SOURCE_CHANGES, CONNECTION_MODE, SECURITY_PRESENCE, DEFINITION_CHANGES); this does not establish that those mechanisms are absent."
}
```

Tool decisions:
```json
[
  {
    "arguments": {
      "id": "case-evidence:25e2e825633c60689792fb46cf09e8735a2a9174e412d06b69702a22bc9899f1"
    },
    "tool": "get_evidence",
    "tool_use_id": "toolu_011hFGqK6KopqPw1HA62zM1G",
    "turn": 1
  },
  {
    "arguments": {
      "layer": "native:4aae8dbb1d373ebef783",
      "purpose": "recreate",
      "query": "EVALUATE ROW(\"Invoiced Amount\", SUM(Billing[amount]), \"max_invoice_date\", MAX(Billing[invoice_date]), \"rows\", COUNTROWS(Billing))"
    },
    "tool": "run_dax",
    "tool_use_id": "toolu_01WUUC3Mm8fMCdMKgMx9Fcda",
    "turn": 1
  },
  {
    "arguments": {
      "layer": "native:f87556d4485196602461",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, MAX([invoice_date]) AS max_invoice_date, COUNT(*) AS rows_observed FROM [gold].[invoice_activity]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_012GsF1bG7dUmPzP3mMJ5WFf",
    "turn": 1
  },
  {
    "arguments": {
      "node": "85ebcba2928d8f8528fb24a35f5eef13ba764e4ad8f00d738c85558dc2a53bd8"
    },
    "tool": "get_refresh_history",
    "tool_use_id": "toolu_01G2qZC5XQTNkNCefVLsGj2V",
    "turn": 1
  },
  {
    "arguments": {
      "node": "d9f7093f1620cf2715c3b6b0d43f5e569975ad02e75519892fd133ea007142c1",
      "operation": "PRODUCERS"
    },
    "tool": "get_lineage",
    "tool_use_id": "toolu_01VjfmXNedFyNKt7L8jdFYFy",
    "turn": 1
  },
  {
    "arguments": {
      "words": "invoice_activity stored procedure transformation bronze invoices billing warehouse job",
      "workspace": "7d67bb36-04f6-4182-95aa-da5d515248fa"
    },
    "tool": "list_candidates",
    "tool_use_id": "toolu_01FdKGSAtzGjix2TueSE1vD7",
    "turn": 4
  },
  {
    "arguments": {
      "node": "2439472548ec60dbbc1c57e217175f6e5cc5eef8b3c3cfea6b10463407a0e04c",
      "operation": "NEIGHBOURS"
    },
    "tool": "get_lineage",
    "tool_use_id": "toolu_01A932pXfzq3Ec4Xn8UKdqfV",
    "turn": 7
  },
  {
    "arguments": {
      "node": "072efb563a80031fb6ed6773a44b89662672682c6b0a16ef8c309b8e477485fb",
      "operation": "NEIGHBOURS"
    },
    "tool": "get_lineage",
    "tool_use_id": "toolu_01Knyptoxjy9R1xPXVEgrDoc",
    "turn": 7
  },
  {
    "arguments": {
      "node": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/76c60248-b830-433b-9880-90593da28e7e"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_01R7wAJ7dkrskgs7B6ndNyET",
    "turn": 10
  },
  {
    "arguments": {
      "node": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/62eb1a7f-19c2-466f-85ec-cda6bc231fb9"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_01FZsV1rsuY2fK7ocmAHYKNX",
    "turn": 10
  },
  {
    "arguments": {
      "node": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/fc8438fd-2c18-4196-9191-33e26481e2e0"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_01PLaiZVAub7YVhq1gH7YSQt",
    "turn": 10
  },
  {
    "arguments": {
      "layer": "native:f87556d4485196602461",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount FROM [silver].[invoices]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01YBtZopxiDgJGLtU9gKTAtb",
    "turn": 10
  },
  {
    "arguments": {
      "layer": "native:f87556d4485196602461",
      "purpose": "compare",
      "query": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount FROM [bronze].[invoices]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01GWT4XGmr3q4NBUmckJAWtH",
    "turn": 10
  },
  {
    "arguments": {
      "id": "case-evidence:af837c6c27d533e5843ccea850f69d4f191294d2b061380d7bff7844e196f40e"
    },
    "tool": "get_evidence",
    "tool_use_id": "toolu_01WiDJeXJfxwD3Nq15qjYrQS",
    "turn": 13
  },
  {
    "arguments": {
      "node": "5fd69c1b5817645bf256c653c3a6fdfb060ba4f6cd3b35c7f56324a93e5e9ad4"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_019spftoTGqaWUxFoMxmZXHt",
    "turn": 16
  }
]
```

Queries:
```json
[
  {
    "asset_ids": [
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing",
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/amount",
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/c6c1091c-3bde-46ca-94fc-58f62d1e4188/table/Billing/columns/invoice_date"
    ],
    "duration_seconds": 6.573167568000031,
    "executed_text": "EVALUATE TOPN(251,ROW(\"Invoiced Amount\",SUM(Billing[amount]),\"max_invoice_date\",MAX(Billing[invoice_date]),\"rows\",COUNTROWS(Billing)))",
    "id": "query:c1a7cd18dfc92ed71deead3e5846f934c0ee4e00aa65abac09f8ab0ca1cba89d:1",
    "layer": "native:4aae8dbb1d373ebef783",
    "parameters": [],
    "purpose": "recreate",
    "result": {
      "rows": [
        {
          "[Invoiced Amount]": 950,
          "[max_invoice_date]": "2026-10-01T00:00:00",
          "[rows]": 5
        }
      ],
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "768c09ce7732d94e86a1cb7b15cfaca800790def6ed32f5e8a21996794489f75",
    "row_count": 1,
    "signature": "c1a7cd18dfc92ed71deead3e5846f934c0ee4e00aa65abac09f8ab0ca1cba89d",
    "status": "SUCCEEDED",
    "text": "EVALUATE ROW(\"Invoiced Amount\", SUM(Billing[amount]), \"max_invoice_date\", MAX(Billing[invoice_date]), \"rows\", COUNTROWS(Billing))",
    "time": "2026-10-28T06:25:21.693175+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity"
    ],
    "duration_seconds": 9.90300928900001,
    "executed_text": "SELECT TOP 251 SUM(CAST([invoice_activity].[amount] AS BIGINT)) AS [invoiced_amount], MAX([invoice_activity].[invoice_date]) AS [max_invoice_date], COUNT(*) AS [rows_observed] FROM [gold].[invoice_activity] AS [invoice_activity]",
    "id": "query:76aa9664ef825db16af5b28737f38d5cfa02fea5d8177a57e6ff3d35d9b63ec6:2",
    "layer": "native:f87556d4485196602461",
    "parameters": [],
    "purpose": "compare",
    "result": {
      "column_types": {
        "invoiced_amount": "Int64",
        "max_invoice_date": "DateTime",
        "rows_observed": "Int64"
      },
      "execution_identity": {
        "database": "billing_serving",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-g25wo7pwasbedfnk3jovcusi7i.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "invoiced_amount": "950",
          "max_invoice_date": "2026-10-01",
          "rows_observed": "5"
        }
      ]
    },
    "result_digest": "9bd1e64a4f8477fb9245c7757b56cbe2b1f0b48b252d208dd3dea7392b4641d7",
    "row_count": 1,
    "signature": "76aa9664ef825db16af5b28737f38d5cfa02fea5d8177a57e6ff3d35d9b63ec6",
    "status": "SUCCEEDED",
    "text": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount, MAX([invoice_date]) AS max_invoice_date, COUNT(*) AS rows_observed FROM [gold].[invoice_activity]",
    "time": "2026-10-28T06:25:28.457579+00:00",
    "truncated": false
  },
  {
    "duration_seconds": 0,
    "error": "SQL object unavailable or view dependencies not validated",
    "error_type": "QueryRejection",
    "failure_class": "wrong column or table",
    "id": "query:cb48f0c186d2b6715c604905c0df4c18f493ed77f119d4cb581f837cf594003b:3",
    "layer": "native:f87556d4485196602461",
    "native_dispatched": false,
    "purpose": "compare",
    "result_digest": null,
    "row_count": null,
    "schema_slice": [
      {
        "columns": [
          {
            "collation_name": null,
            "data_type": "int",
            "name": "invoice_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "account_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "plan_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "date",
            "name": "invoice_date",
            "observed_type": "date"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "amount",
            "observed_type": "int"
          },
          {
            "collation_name": "Latin1_General_100_BIN2_UTF8",
            "data_type": "varchar",
            "name": "status",
            "observed_type": "varchar"
          }
        ],
        "id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
        "name": "invoice_activity",
        "schema_name": "gold",
        "type_desc": "USER_TABLE"
      }
    ],
    "signature": "cb48f0c186d2b6715c604905c0df4c18f493ed77f119d4cb581f837cf594003b",
    "status": "ERROR",
    "text": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount FROM [silver].[invoices]",
    "time": "2026-10-28T06:26:05.831706+00:00"
  },
  {
    "duration_seconds": 0,
    "error": "SQL object unavailable or view dependencies not validated",
    "error_type": "QueryRejection",
    "failure_class": "wrong column or table",
    "id": "query:9f7efcc07564548ddfb194dc777e195d6a5a6828aa2f40d10019323a2eb5f8d7:4",
    "layer": "native:f87556d4485196602461",
    "native_dispatched": false,
    "purpose": "compare",
    "result_digest": null,
    "row_count": null,
    "schema_slice": [
      {
        "columns": [
          {
            "collation_name": null,
            "data_type": "int",
            "name": "invoice_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "account_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "plan_id",
            "observed_type": "int"
          },
          {
            "collation_name": null,
            "data_type": "date",
            "name": "invoice_date",
            "observed_type": "date"
          },
          {
            "collation_name": null,
            "data_type": "int",
            "name": "amount",
            "observed_type": "int"
          },
          {
            "collation_name": "Latin1_General_100_BIN2_UTF8",
            "data_type": "varchar",
            "name": "status",
            "observed_type": "varchar"
          }
        ],
        "id": "fabric://7d67bb36-04f6-4182-95aa-da5d515248fa/406dcb89-0526-4f48-bb77-397d52471c89/table/gold.invoice_activity",
        "name": "invoice_activity",
        "schema_name": "gold",
        "type_desc": "USER_TABLE"
      }
    ],
    "signature": "9f7efcc07564548ddfb194dc777e195d6a5a6828aa2f40d10019323a2eb5f8d7",
    "status": "ERROR",
    "text": "SELECT SUM(CAST([amount] AS bigint)) AS invoiced_amount FROM [bronze].[invoices]",
    "time": "2026-10-28T06:26:06.283089+00:00"
  }
]
```

Final answer:
```json
"The checks did not establish a cause within this ticket’s limits."
```

Sealed expected:
```json
{
  "case_id": "v2-failed-billing-transform",
  "cause": "Latest failed native transform run with name/run ID/start/end/error; no invented successful completion.",
  "estate": "billing",
  "expectation_basis": "Practice source literals, declared definitions and reversible scenario plan; never an engine answer.",
  "fixture": "failed-billing",
  "id": "v2-failed-billing-transform-v2",
  "layer": "billing transformation pipeline",
  "split": "DEV",
  "variation": "brief support question",
  "verdict": "failed job"
}
```

Saved checkpoint SHA-256: 356ac3ccb5d70be403e849ad6ba2e2858349cc1f1d0041eee2a562ea585672f6. Only recorded tool choices are shown; no new queries or model calls.


## Round24 held01 automatic backtrack

{'graded': 20, 'score': 18, 'harmful': 0, 'correctness': {'cause_match': 18, 'layer_match': 19, 'verdict_match': 18}, 'zero_groups': {'conclusion': 2}}

| Ticket | First wrong step | Reason and correct action |
|---|---|---|
| v3-before-temporal-retention | conclusion | Verdict mismatch: the expected answer is 'not found' (the historical quantity cannot be established because the requested time precedes retained temporal evidence). The delivered answer says 'definition explained' and concludes the report always shows current rows with no as-of logic — which is correct as far as it goes — but then goes further and treats the NULL from FOR SYSTEM_TIME AS OF as confirmation that no value existed at that time, rather than correctly concluding that the history boundary means the value is not found/not establishable. The delivered answer does note 'The retained history therefore gives no value for movement 1 at that time' and 'Limitation: why there is no version at that time was not established', which edges toward the correct finding, but the overall framing and verdict is 'definition explained' rather than 'not found'. Layer mismatch: the expected layer is 'source history boundary' (the temporal retention boundary in the source system), but the delivered answer frames the layer as the measure definition/Direct Lake architecture. The delivered answer does touch on source temporal history (FOR SYSTEM_TIME AS OF returning NULL, FOR SYSTEM_TIME ALL showing only one version), which is relevant evidence, but the named cause is 'definition explained' (no date logic in measure) rather than 'Requested time precedes retained temporal evidence'. The cause mismatch follows: expected cause is that the requested time precedes retained temporal evidence; delivered cause is that the measure has no as-of logic and always shows current rows. The answer is not harmful — it honestly reports uncertainty about why no history exists. Handoff quality is good: queries are rerunnable, the stopping point is clear, and sensible next checks (history period columns, Lakehouse time travel) are named. Restrict the cause to what the cited native evidence establishes. |
| v3-record-absent-everywhere | conclusion | Verdict mismatch: the sealed expected answer is 'as designed' (the record is intentionally absent at source and every layer), but the delivered answer gives 'not found' with a tone implying the record might have existed and been removed, and explicitly states 'The source system doesn't have it now' with a hedge about whether it existed earlier. The sealed expectation treats the absence as a designed fixture condition, not an unexplained missing record. Layer match: both identify the source application as where the absence is confirmed. Cause: the sealed cause is 'Record900099 is absent at source and every compared reachable layer; BLANK is not zero' — the delivered answer confirms absence at all layers but does not state 'as designed' or that BLANK is not zero; it instead frames this as an unexplained gap and hedges about possible earlier existence, which is a substantively different cause characterisation. Handoff quality is 0 because the answer is resolved (ANSWERED status, no handoff left), so there is no handoff to grade. Restrict the cause to what the cited native evidence establishes. |

### v3-before-temporal-retention
Verdict mismatch: the expected answer is 'not found' (the historical quantity cannot be established because the requested time precedes retained temporal evidence). The delivered answer says 'definition explained' and concludes the report always shows current rows with no as-of logic — which is correct as far as it goes — but then goes further and treats the NULL from FOR SYSTEM_TIME AS OF as confirmation that no value existed at that time, rather than correctly concluding that the history boundary means the value is not found/not establishable. The delivered answer does note 'The retained history therefore gives no value for movement 1 at that time' and 'Limitation: why there is no version at that time was not established', which edges toward the correct finding, but the overall framing and verdict is 'definition explained' rather than 'not found'. Layer mismatch: the expected layer is 'source history boundary' (the temporal retention boundary in the source system), but the delivered answer frames the layer as the measure definition/Direct Lake architecture. The delivered answer does touch on source temporal history (FOR SYSTEM_TIME AS OF returning NULL, FOR SYSTEM_TIME ALL showing only one version), which is relevant evidence, but the named cause is 'definition explained' (no date logic in measure) rather than 'Requested time precedes retained temporal evidence'. The cause mismatch follows: expected cause is that the requested time precedes retained temporal evidence; delivered cause is that the measure has no as-of logic and always shows current rows. The answer is not harmful — it honestly reports uncertainty about why no history exists. Handoff quality is good: queries are rerunnable, the stopping point is clear, and sensible next checks (history period columns, Lakehouse time travel) are named. Restrict the cause to what the cited native evidence establishes.

Intake:
```json
{
  "compared_with": {
    "kind": "NOTHING"
  },
  "description": "In the Movement Units visual, application movement1 currently shows 16 units. I need to know how many units this movement had as of 2026-10-20 at 12:00 UTC. I didn't save an export from that time, so I have nothing to compare against. Can you tell me what the value was at that point, and how the report works out a past value like this?",
  "details": {
    "approximate_date": "2026-10-20T12:00:00Z",
    "record": "movement1"
  },
  "issue_type": "HOW_IS_THIS_CALCULATED",
  "measure_candidates": [
    {
      "id": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
      "name": "Movement Units"
    }
  ],
  "page": "e4d6e671103ca3746c4ca9435fc635e13ae0a08bf09ffa515580b7f1a50fd7f7",
  "report": "3ba93e33aa41f6b91b0ef623bfd66bf2d9ec9eefd5e583643e6462e0dbd5b2ed",
  "reported_figure": {
    "precision": "EXACT",
    "state": "NUMBER",
    "value": "16"
  },
  "status": "READY",
  "version": "IntakeRequest/1",
  "visual": "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce"
}
```

Target:
```json
{
  "layers": {
    "native:4caf47d120d4fd198ffe": {
      "dialect": "DAX",
      "label": "Application load fixture 20261003"
    },
    "native:9e3796a26d8d5c1a039e": {
      "dialect": "T-SQL",
      "label": "ordersops"
    },
    "native:e95b94fd338e7086320f": {
      "dialect": "T-SQL",
      "label": "round_two_bronze_20261003"
    }
  },
  "path": {
    "as_of": null,
    "declared_route_bridges": [
      {
        "column_bindings": [
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/movement_id",
            "semantic_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/movement_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/warehouse_id",
            "semantic_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/warehouse_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/product_id",
            "semantic_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/product_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/units",
            "semantic_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/units"
          }
        ],
        "confidence": "DECLARED",
        "definition_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/part/model.bim",
        "definition_hash": "a87545a3e875d2260873432f55b447cbbe4d461928395aa15254ff574d34c5f6",
        "graph_nodes": [
          "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
          "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c"
        ],
        "literal_expression": "let database = Sql.Database(\"i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com\", \"fbbccea4-d943-4f58-b91f-e6cbcb912620\") in database",
        "native_ownership": [
          {
            "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/native-relation/5847348b3fe731e359d488a7c71321000b58db7362e3d339eda7af1eb0e37c92",
            "inventory_digest_qualification": "Retained inventory digests matched; this is not a current query-bound attestation.",
            "metadata": {
              "container_asset_hash": "d4fe38b53f7492e7e0634b5a277a155d2399772c5dd352b9f1371a48172ba817",
              "container_asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
              "context_hash": "42e974374d54fb08f1b1e3cc761ab80543200ed796a78917082f3bb2e6f8d0f6",
              "context_version": "4cae0d14-fd5d-4ff1-89ce-adf346790084",
              "endpoint_asset_hash": "dacb9d4b7db91da731f9c761c50043780a5dd2d501a41a33c559e8c7d20dc6e4",
              "endpoint_asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/fbbccea4-d943-4f58-b91f-e6cbcb912620",
              "observed_at": "2026-10-21T21:33:21.054850Z",
              "relation": {
                "evidence": [
                  {
                    "scope": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
                    "source_api": "fabric_item_relations_beta"
                  }
                ],
                "provenance": "DISCOVERED",
                "relation": "NATIVE_CASCADEDELETE",
                "source": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/fbbccea4-d943-4f58-b91f-e6cbcb912620",
                "target": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3"
              },
              "relation_pointer": "/graph/edges/843"
            }
          }
        ],
        "partition_source": {
          "entityName": "stock_movements_round_two_20261003",
          "expressionSource": "ApplicationLoadSource",
          "schemaName": "dbo",
          "type": "entity"
        },
        "physical_table": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
        "qualification": "Declared route only; value agreement and aligned snapshots are not implied.",
        "semantic_table": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements"
      },
      {
        "basis": "ESTATE_MANIFEST_BINDING",
        "binding": {
          "from_layer": "application",
          "provenance": "DECLARED_BY_DEFINITION",
          "to_layer": "landing"
        },
        "confidence": "DECLARED",
        "delivery_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
        "graph_nodes": [
          "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a"
        ],
        "producers": [
          {
            "audit": {
              "resource": "load-audit",
              "status": "PRESENT"
            },
            "audit_resource": {
              "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/bea673e0-a206-461e-9b2f-1b3b827e80de/table/dbo.load_run_audit",
              "id": "load-audit",
              "reach": {
                "adapter": "estate-reader",
                "address": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/bea673e0-a206-461e-9b2f-1b3b827e80de/table/dbo.load_run_audit",
                "reader": "investigator-reader"
              }
            },
            "delivery_asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
            "from_layer": "application",
            "history_resource": "load-history",
            "id": "application-load",
            "producer_asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c",
            "to_layer": "landing"
          }
        ],
        "qualification": "Declared mapping only; compare native values and retained load evidence to establish a cause.",
        "source_asset": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
      }
    ],
    "edges": [
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "06c8ec3ee7932e03fa0cee970e877a9f1ead91ab1a4024627716196f880d993b",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "17d8b434f56b320cba6bfc4ea56049014c39e0a7de73b71151e3c6d5bf7efabf",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "1e0a1aeaad2107704ac9c0da4f0b98a7649a1ac176baccd5e152e17c542d8c65",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "1eb4e7a69c34396385d68cd4b33f6b0007a5d7a9467a1a903fb6dfa02bfc6b99",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "20487352dbe71aaa186e04cd2a0b49c5fd2b9cb4fbff126fd0cfbec2b7b4edf1",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "binding_kind": "DIRECTLAKE_ENTITY",
          "catalog_id": "fbbccea4-d943-4f58-b91f-e6cbcb912620",
          "container_asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
          "container_binding": {
            "definition_hash": "23669eefffb853c2ca9014ee305dc7269cb2fa5a63160a33f5a2a1dc82cd665f",
            "observed_at": "2026-10-28T03:35:17.564451Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/native-relation/5847348b3fe731e359d488a7c71321000b58db7362e3d339eda7af1eb0e37c92",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "container_bindings": [
            {
              "definition_hash": "23669eefffb853c2ca9014ee305dc7269cb2fa5a63160a33f5a2a1dc82cd665f",
              "observed_at": "2026-10-28T03:35:17.564451Z",
              "source": "STATIC_DEFINITION",
              "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/native-relation/5847348b3fe731e359d488a7c71321000b58db7362e3d339eda7af1eb0e37c92",
              "span": {
                "kind": "JSON_POINTER",
                "path": ""
              }
            }
          ],
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
          "entity": "stock_movements_round_two_20261003",
          "expression_pointer": "/model/expressions/0",
          "expression_source": "ApplicationLoadSource",
          "physical_column_definition": {
            "definition_hash": "52c4a51badb36efea3e9a0ae19c764e87af8d48b152040b4e23ec7279e1f28e4",
            "observed_at": "2026-10-11T16:27:31.868191Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/units",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "physical_definition": {
            "definition_hash": "ec45d792a5e5f2d5c4bd2a04f33e4e5396583c1820af85c2f99f7722d124eaab",
            "observed_at": "2026-10-11T16:27:31.868191Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "schema": "dbo",
          "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com",
          "source_column": "units"
        },
        "provenance": {
          "definition_hash": "18be79d2ba4c304d1bba31d0823850f93bf964b2ff9feb002abe66a52463f43c",
          "observed_at": "2026-10-28T03:35:17.564451Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/part/model.bim",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/model/tables/0/columns/3/sourceColumn"
          }
        },
        "source": "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
        "target": "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "30577e94eeede86f93ae7f5c6d5c239e886ef3ca6899b04c13e4c44b33994c87",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "3070875cfdd22ac7316d00981f391fe2f98a8905cab84684200e5629ee85f028",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "33fcdac3222c9bb64858c980d34b1d898a3f22f194274e0c15a02c71b5ef90b8",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS",
          "connection_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/connection/3f5891f3-092b-4c26-b838-1d024e989501",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "destination_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
          "native_destination": {
            "artifactId": "33618b8d-46eb-4fe7-b80b-122c331260a3",
            "workspaceId": "149f8d99-1c66-4a0a-9624-759be002bb60"
          },
          "source_asset": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945",
          "source_query": null
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "4c0ff82c658eead5142c04a645bb4def66f5475cc1a73ba2f43153f6b08887be",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "57151bc18eeb30ee23d6da4e325cfd193ca0ed9bcf396a93fde0a7ced7adfb7c",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "666c5579851a32a3b5a9f56bc7018d2b92ae01305bf7c4e0d6f3f198604b10cb",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "669400314dab93454b3c1af392293ee7f557a499a1a8c432ed3c99dfa31b0df0",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "6792c3f8c484ae44c108b4e528d0fee217da3e35fbfb0966ab729c0fdee2d6f4",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "6e8fd211e6242e2ab549b7c841781ec6c41779696ad5e41f4eded9f85203ac98",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "binding_kind": "DIRECTLAKE_ENTITY",
          "catalog_id": "fbbccea4-d943-4f58-b91f-e6cbcb912620",
          "container_asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
          "container_binding": {
            "definition_hash": "23669eefffb853c2ca9014ee305dc7269cb2fa5a63160a33f5a2a1dc82cd665f",
            "observed_at": "2026-10-28T03:35:17.564451Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/native-relation/5847348b3fe731e359d488a7c71321000b58db7362e3d339eda7af1eb0e37c92",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "container_bindings": [
            {
              "definition_hash": "23669eefffb853c2ca9014ee305dc7269cb2fa5a63160a33f5a2a1dc82cd665f",
              "observed_at": "2026-10-28T03:35:17.564451Z",
              "source": "STATIC_DEFINITION",
              "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/native-relation/5847348b3fe731e359d488a7c71321000b58db7362e3d339eda7af1eb0e37c92",
              "span": {
                "kind": "JSON_POINTER",
                "path": ""
              }
            }
          ],
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
          "entity": "stock_movements_round_two_20261003",
          "expression_pointer": "/model/expressions/0",
          "expression_source": "ApplicationLoadSource",
          "physical_definition": {
            "definition_hash": "ec45d792a5e5f2d5c4bd2a04f33e4e5396583c1820af85c2f99f7722d124eaab",
            "observed_at": "2026-10-11T16:27:31.868191Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "schema": "dbo",
          "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com"
        },
        "provenance": {
          "definition_hash": "18be79d2ba4c304d1bba31d0823850f93bf964b2ff9feb002abe66a52463f43c",
          "observed_at": "2026-10-28T03:35:17.564451Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/part/model.bim",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/model/tables/0/partitions"
          }
        },
        "source": "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
        "target": "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "75f76c47eb9b8c836e06dee841dcf4664448e803c0c31b7dd674b71bb01124c4",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef"
        },
        "provenance": {
          "definition_hash": "01316df16f1ed86a54c0d457aaa55897df288ddc1f0ddf1bd79642bad475b997",
          "observed_at": "2026-10-27T04:06:22.268955Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/queryState/Values/projections/0/field/Measure"
          }
        },
        "source": "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce",
        "target": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "unknown": null,
        "valid_from": "2026-10-27T05:07:37.477893Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "7890d5105e809712fb07172a11aba9dbc04cc52b62155242cbec941b8ee9691b",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "7a22811d7d0ff9dbfc8559326230903f5071ee75b2d8a0cbc72433da2576f31a",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "7f56d35b6bd08b5d9a99614402b448388cce5494525f4283358e8085803c8246",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "completeness": "ROW_ONLY",
          "definition": {
            "bytes": 561,
            "sha256": "0899aeb41756ce76b582aed568a9d970d85295c35729f7c368dc454aabc939f9",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/0899aeb41756ce76b582aed568a9d970d85295c35729f7c368dc454aabc939f9"
          },
          "model_definition_hash": "18be79d2ba4c304d1bba31d0823850f93bf964b2ff9feb002abe66a52463f43c",
          "native_row_hash": "1ae9d5c404cc7749f33fa87a36ce702bef793fc0f3c5af3f018eaffde6acecbf"
        },
        "provenance": {
          "definition_hash": "0899aeb41756ce76b582aed568a9d970d85295c35729f7c368dc454aabc939f9",
          "observed_at": "2026-10-13T17:11:21.310792Z",
          "source": "ENGINE_DEPENDENCY",
          "source_id": "d06d2b3daefe976c10cbcbf1f2e3e207c8256f81621d3e73ceedf036b04cc58a",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/rows/1"
          }
        },
        "source": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "target": "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
        "unknown": null,
        "valid_from": "2026-10-13T17:11:21.310792Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "8612d5915b69806d03ff4a870b21803697afb820297940c7a4739b651bdf073f",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
        "properties": {
          "basis": "EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS",
          "connection_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/connection/3f5891f3-092b-4c26-b838-1d024e989501",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "destination_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
          "native_destination": {
            "artifactId": "33618b8d-46eb-4fe7-b80b-122c331260a3",
            "workspaceId": "149f8d99-1c66-4a0a-9624-759be002bb60"
          },
          "source_asset": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945",
          "source_query": null
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
        "target": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "97f1475120b8e2f1af28620b77651bc1afa195532d92b63e29dce5142293cbd6",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "b1326b7138cadf5b67e4fb8e437fd9b5c1860e4e061d56eb35a25b5a85ad7f83",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "cbde8d939597b988cb7186578be98c95bab4275a11c9212027c5e6075df8df69",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "db4094fac448b7bc3463118d25c4523d3131409d5fbc9f4cc688cad8906edc7a",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "completeness": "ROW_ONLY",
          "definition": {
            "bytes": 561,
            "sha256": "0899aeb41756ce76b582aed568a9d970d85295c35729f7c368dc454aabc939f9",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/0899aeb41756ce76b582aed568a9d970d85295c35729f7c368dc454aabc939f9"
          },
          "model_definition_hash": "18be79d2ba4c304d1bba31d0823850f93bf964b2ff9feb002abe66a52463f43c",
          "native_row_hash": "019f5aa703e133bee59f21b8ec1db58e30de10b5199e0200b54b815b47584415"
        },
        "provenance": {
          "definition_hash": "0899aeb41756ce76b582aed568a9d970d85295c35729f7c368dc454aabc939f9",
          "observed_at": "2026-10-13T17:11:21.310792Z",
          "source": "ENGINE_DEPENDENCY",
          "source_id": "d06d2b3daefe976c10cbcbf1f2e3e207c8256f81621d3e73ceedf036b04cc58a",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/rows/0"
          }
        },
        "source": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "target": "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
        "unknown": null,
        "valid_from": "2026-10-13T17:11:21.310792Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "275b6a0f2d4511949028c3fe5a581b5c1b746fbab9f49a1ba8b76eb757d1a4e8",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "NATIVE_COPY_ACTIVITY_OWNERSHIP",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
        "target": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "c120038524885218e7bc72b6f2a60622a60146a0285607c6d495b26b90ede2cb",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c",
        "properties": {
          "basis": "NATIVE_INVOKE_COPY_JOB_UUID",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c"
        },
        "provenance": {
          "definition_hash": "2ad010f0f8c75662d1fab7ebc89e2ef801da946287e2b62becbee58038477fdc",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
        "target": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      }
    ],
    "estate": "fixture",
    "nodes": [
      {
        "confidence": "DECLARED",
        "id": "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "movement_type"
            },
            "source": {
              "name": "movement_type"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "event_day"
            },
            "source": {
              "name": "event_day"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
        "kind": "COLUMN",
        "label": "units",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/units",
          "definition": {
            "bytes": 217,
            "sha256": "52c4a51badb36efea3e9a0ae19c764e87af8d48b152040b4e23ec7279e1f28e4",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/52c4a51badb36efea3e9a0ae19c764e87af8d48b152040b4e23ec7279e1f28e4"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
          "hidden": null,
          "native_kind": "LakehouseColumn",
          "retained_metadata_hash_encoding": "SORTED_JSON_SPACED"
        },
        "provenance": {
          "definition_hash": "52c4a51badb36efea3e9a0ae19c764e87af8d48b152040b4e23ec7279e1f28e4",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/units",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-11T16:27:31.868191Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "source_modified_at_utc"
            },
            "source": {
              "name": "source_modified_at_utc"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
        "kind": "TABLE",
        "label": "Movements",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements",
          "definition": {
            "bytes": 714,
            "sha256": "0bcb2b34b6dc2d54895df1997446c507fc5ee161d94de631776d395219242b0a",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/0bcb2b34b6dc2d54895df1997446c507fc5ee161d94de631776d395219242b0a"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
          "hidden": null,
          "native_kind": "SemanticTable"
        },
        "provenance": {
          "definition_hash": "0bcb2b34b6dc2d54895df1997446c507fc5ee161d94de631776d395219242b0a",
          "observed_at": "2026-10-13T17:11:21.310792Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:11:21.310792Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
        "kind": "COLUMN",
        "label": "units",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/units",
          "dataType": "int64",
          "definition": {
            "bytes": 86,
            "sha256": "7cd3462864ca0771eb694e8d79584f93c5af27e2f4f2e9d773adc3b085a86e2f",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/7cd3462864ca0771eb694e8d79584f93c5af27e2f4f2e9d773adc3b085a86e2f"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
          "hidden": null,
          "native_kind": "SemanticColumn",
          "sourceColumn": "units"
        },
        "provenance": {
          "definition_hash": "7cd3462864ca0771eb694e8d79584f93c5af27e2f4f2e9d773adc3b085a86e2f",
          "observed_at": "2026-10-13T17:11:21.310792Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/units",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:11:21.310792Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "kind": "MEASURE",
        "label": "Movement Units",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units",
          "definition": {
            "bytes": 67,
            "sha256": "9bac4b87495b487a3fade3ae0eda2eac30dd456247b18b7be78404985255a599",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/9bac4b87495b487a3fade3ae0eda2eac30dd456247b18b7be78404985255a599"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
          "hidden": null,
          "native_kind": "Measure"
        },
        "provenance": {
          "definition_hash": "9bac4b87495b487a3fade3ae0eda2eac30dd456247b18b7be78404985255a599",
          "observed_at": "2026-10-13T17:11:21.310792Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:11:21.310792Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce",
        "kind": "VISUAL",
        "label": "Movement Units",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef/visual/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
          "definition": {
            "bytes": 2994,
            "sha256": "01316df16f1ed86a54c0d457aaa55897df288ddc1f0ddf1bd79642bad475b997",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/01316df16f1ed86a54c0d457aaa55897df288ddc1f0ddf1bd79642bad475b997"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef",
          "hidden": null,
          "native_kind": "ReportVisual",
          "retained_metadata_hash_encoding": "SORTED_JSON_SPACED"
        },
        "provenance": {
          "definition_hash": "01316df16f1ed86a54c0d457aaa55897df288ddc1f0ddf1bd79642bad475b997",
          "observed_at": "2026-10-27T03:31:50.268163Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-27T03:31:50.268163Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "units"
            },
            "source": {
              "name": "units"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "id": "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
        "kind": "TABLE",
        "label": "dbo.stock_movements_round_two_20261003",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
          "definition_source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "source_row_version"
            },
            "source": {
              "name": "source_row_version"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "kind": "COPY_ACTIVITY",
        "label": "e8fc7b29-f267-4696-8ab2-4fdd4f78b5b9",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "activity_type": "Copy",
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "native_copy_binding": {
            "basis": "EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS",
            "connection_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/connection/3f5891f3-092b-4c26-b838-1d024e989501",
            "destination_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
            "native_destination": {
              "artifactId": "33618b8d-46eb-4fe7-b80b-122c331260a3",
              "workspaceId": "149f8d99-1c66-4a0a-9624-759be002bb60"
            },
            "source_asset": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945",
            "source_query": null
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "kind": "TABLE",
        "label": "app.stock_movements_round_two_20261003",
        "owner": "sql://sql-orderops-9696025.database.windows.net/ordersops",
        "properties": {
          "asset_id": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945",
          "definition": {
            "bytes": 2353,
            "sha256": "3edcd22eef92476a95134e8c91850521d94c3f3456df841fd22c64785462dbf8",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/3edcd22eef92476a95134e8c91850521d94c3f3456df841fd22c64785462dbf8"
          },
          "definition_source_owner": "sql://sql-orderops-9696025.database.windows.net/ordersops",
          "hidden": null,
          "native_kind": "SqlObject",
          "retained_metadata_hash_encoding": "SORTED_JSON_SPACED",
          "source_system_object": true
        },
        "provenance": {
          "definition_hash": "3edcd22eef92476a95134e8c91850521d94c3f3456df841fd22c64785462dbf8",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "product_id"
            },
            "source": {
              "name": "product_id"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "warehouse_id"
            },
            "source": {
              "name": "warehouse_id"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "movement_id"
            },
            "source": {
              "name": "movement_id"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "id": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
        "kind": "MODEL",
        "label": "Application load fixture 20261003",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
          "definition_source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
        "kind": "PIPELINE",
        "label": "round_two_application_load_audited_20261003",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c",
          "definition": {
            "bytes": 311,
            "sha256": "41fdb793abce933f29b74bfc1f7ce0aef4b9f1f558a61985d02049908edfc528",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/41fdb793abce933f29b74bfc1f7ce0aef4b9f1f558a61985d02049908edfc528"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c",
          "hidden": null,
          "native_kind": "DataPipeline"
        },
        "provenance": {
          "definition_hash": "41fdb793abce933f29b74bfc1f7ce0aef4b9f1f558a61985d02049908edfc528",
          "observed_at": "2026-10-13T17:50:04.516006Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:50:04.516006Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
        "kind": "PIPELINE",
        "label": "investigation_round_two_history_probe_20261003",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "definition": {
            "bytes": 322,
            "sha256": "2eb93cba09c1422b79507a518e2edcda3c4b6762d0550bef154954aa3d845d1e",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/2eb93cba09c1422b79507a518e2edcda3c4b6762d0550bef154954aa3d845d1e"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "hidden": null,
          "native_kind": "CopyJob"
        },
        "provenance": {
          "definition_hash": "2eb93cba09c1422b79507a518e2edcda3c4b6762d0550bef154954aa3d845d1e",
          "observed_at": "2026-10-13T17:20:33.292207Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:20:33.292207Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      }
    ],
    "stops": [
      {
        "node": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
        "reason": "No retained upstream dependency is declared for this object."
      },
      {
        "node": "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "reason": "No retained upstream dependency is declared for this object."
      },
      {
        "node": "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      }
    ],
    "truncated": false,
    "unavailable_owners": {
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6": {
        "at": "2026-10-28T06:01:26.092883Z",
        "failure": {
          "errno": null,
          "error_type": "MetadataUnavailable",
          "http_status": 404,
          "line": 106,
          "message": "Metadata provider request unavailable",
          "message_redacted": false,
          "module": "metadata_auth.py",
          "provider_code": "EntityNotFound"
        },
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "status": "UNAVAILABLE"
      },
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3": {
        "at": "2026-10-28T06:01:44.119965Z",
        "failure": {
          "errno": null,
          "error_type": "RuntimeError",
          "line": 88,
          "message": "GRAPH_DEFINITION_KIND_UNAVAILABLE",
          "message_redacted": false,
          "module": "graph_change_collector.py"
        },
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "status": "UNAVAILABLE"
      },
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782": {
        "at": "2026-10-28T06:02:00.311881Z",
        "failure": {
          "errno": null,
          "error_type": "MetadataUnavailable",
          "http_status": 401,
          "line": 106,
          "message": "Metadata provider request unavailable",
          "message_redacted": false,
          "module": "metadata_auth.py",
          "provider_code": "Unauthorized"
        },
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "status": "UNAVAILABLE"
      }
    }
  }
}
```

Triage:
```json
{
  "facts": [
    {
      "cached": false,
      "check": "MODEL_REFRESH",
      "observed_at": "2026-10-28T09:21:02.513855Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "5705f36190d3483830231b959e5412579efcf1e35fb2b373e4006ba362543371",
          "kind": "RUN_HISTORY",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:941551651b73e1287910ceaaf55f414ce9bf15fc410f4ce01657ff9fedbc8b84"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "listing_complete": true,
            "runs": [
              {
                "end": "2026-10-28T08:22:28.950000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "763241357",
                "start": "2026-10-28T08:22:02.380000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:56:11.943000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967533",
                "start": "2026-10-27T15:55:47.577000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:55:31.980000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967527",
                "start": "2026-10-27T15:55:17.423000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T11:22:45.240000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762883014",
                "start": "2026-10-27T11:22:42.810000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T10:04:03.517000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762859376",
                "start": "2026-10-27T10:03:42.330000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:20.813000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762589234",
                "start": "2026-10-26T18:20:20.733000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:33.260000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762588999",
                "start": "2026-10-26T18:19:56.113000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:27:55.313000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "761468506",
                "start": "2026-10-24T01:26:52.530000Z",
                "status": "SUCCEEDED"
              }
            ]
          }
        },
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "e6464f408d0786907f4ef96bd464c98a130a37a8800ef7bcc9f1cb9e1136c283",
          "kind": "REFRESH_RUN",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:941551651b73e1287910ceaaf55f414ce9bf15fc410f4ce01657ff9fedbc8b84"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "accounting": "UNAVAILABLE_FROM_JOB_INSTANCE_SCHEMA",
            "end": "2026-10-28T08:22:28.950000Z",
            "error": null,
            "recent_runs": [
              {
                "end": "2026-10-28T08:22:28.950000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "763241357",
                "start": "2026-10-28T08:22:02.380000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:56:11.943000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967533",
                "start": "2026-10-27T15:55:47.577000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:55:31.980000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967527",
                "start": "2026-10-27T15:55:17.423000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T11:22:45.240000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762883014",
                "start": "2026-10-27T11:22:42.810000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T10:04:03.517000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762859376",
                "start": "2026-10-27T10:03:42.330000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:20.813000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762589234",
                "start": "2026-10-26T18:20:20.733000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:33.260000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762588999",
                "start": "2026-10-26T18:19:56.113000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:27:55.313000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "761468506",
                "start": "2026-10-24T01:26:52.530000Z",
                "status": "SUCCEEDED"
              }
            ],
            "rows_read": null,
            "rows_written": null,
            "run_id": "763241357",
            "start": "2026-10-28T08:22:02.380000Z",
            "status": "SUCCEEDED"
          }
        },
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "fb02eea7d345e54fc8b55e7d68657db46a2896e4d730066b9431ee3a6ced92c3",
          "kind": "REFRESH_STATE",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:941551651b73e1287910ceaaf55f414ce9bf15fc410f4ce01657ff9fedbc8b84"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "last_end": "2026-10-28T08:22:28.950000Z",
            "run_id": "763241357",
            "state": "SUCCEEDED"
          }
        }
      ]
    },
    {
      "cached": false,
      "check": "REFRESH_SCHEDULE",
      "observed_at": "2026-10-28T09:20:33.717357Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "ca2ef01b13bd58ca8683c3609430f6d28193e0aff841cef381e1d7998c76e425",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:7f616a0bcd8016f94253e610fd057e1f8c034a2a4f2308173fa82cd0bb89d964"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "01:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        },
        {
          "collected_at": "2026-10-28T09:20:33.717357Z",
          "freshness": "CURRENT",
          "id": "2f9368a12c6260f1a88dc55126aa98ccbed0f5a328d86de68e9c9601e0a327ef",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:20:33.717357Z",
          "provenance": {
            "collector": "microsoft-runtime:50ed9389d7d5682c8f2f36c6c2f43a2a3731a84b0c91204d9e25890e096564dc",
            "evidence_ids": [
              "sha256:963d00f6f461a122327da82562cac5406ca9717ea982ad75895d6ce4e06d2232"
            ],
            "locator": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "value": {
            "native_schedules": {
              "value": []
            },
            "next_due": null,
            "reason": "Job schedule recurrence retained; unsupported recurrence types remain a named coverage gap."
          }
        }
      ]
    },
    {
      "check": "AUTOMATIC_UPDATES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:AUTOMATIC_UPDATES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "JOB_RUNS",
      "observed_at": "2026-10-28T09:20:56.943747Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:20:56.943747Z",
          "freshness": "CURRENT",
          "id": "fc32dc308581077f2d114aa0f240969c734c7736f3c23fa4ac5b5e25ecad94d1",
          "kind": "JOB_RUN",
          "observed_at": "2026-10-28T09:20:56.943747Z",
          "provenance": {
            "collector": "microsoft-runtime:d90ae203d1e049b5d17b28ad8d56b3e9cbbe0ea8e79c91698aded7cf5e687f7e",
            "evidence_ids": [
              "sha256:288cad8544be3ad251f37dd5321a1255394de641730d6a33bb3f3d82ad402672"
            ],
            "locator": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
          "value": {
            "accounting": "UNAVAILABLE_FROM_JOB_INSTANCE_SCHEMA",
            "end": "2026-10-28T08:16:41.2629279Z",
            "error": null,
            "recent_runs": [
              {
                "end": "2026-10-28T08:16:41.2629279Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "7237d82d-a728-4286-8891-6f548097cdcd",
                "start": "2026-10-28T08:16:11.3116784Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T08:03:50.0016825Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "353770e7-8eb4-47bc-8709-0a667ddb04ad",
                "start": "2026-10-28T08:03:00.469989Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T07:58:25.018859Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "7de99675-2ef8-4bd1-8292-c512f5121dbb",
                "start": "2026-10-28T07:57:40.5054246Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:58:07.0533205Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "15dfbcf2-6985-41e8-8ada-d1973f3ec8a0",
                "start": "2026-10-28T06:57:34.3969215Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:16:46.3062373Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "56e7ecc6-efb1-4d67-b6f8-0645b5de2d21",
                "start": "2026-10-28T06:14:52.7382767Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:54:02.6605794Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "c0e2613f-b446-4d00-a2c5-7f44c4662ae2",
                "start": "2026-10-27T15:53:32.7157778Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:44:05.0886872Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "a33b8ae0-57b8-4794-9cab-f50ec12e03ca",
                "start": "2026-10-27T15:43:33.6916187Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:20:29.5709877Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "fa3d9c73-ff5a-410a-89c8-907afd3f623c",
                "start": "2026-10-27T15:19:55.229535Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:10:24.4533955Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "644ef25a-bad3-4e5e-87b0-3f27c9b4498c",
                "start": "2026-10-27T15:09:53.1889637Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T14:31:41.1898358Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "5caa5c35-5e58-4dc1-94f0-fb8a9ab6619a",
                "start": "2026-10-27T14:31:09.9560782Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:59:50.6670091Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "d3d519f4-55b9-48ef-bf68-ee9b3d6fd724",
                "start": "2026-10-27T09:59:21.4245453Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:49:04.8377033Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "f12d45ba-a321-4a76-9f38-cfd86501054b",
                "start": "2026-10-27T09:48:35.0709386Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:41:49.8935835Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "4eda71d5-c497-4d52-b447-232386f672b5",
                "start": "2026-10-27T09:41:18.3358933Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:28:21.9101852Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "175ebde3-2543-47e5-bde0-ec38474c3ccc",
                "start": "2026-10-27T09:27:52.0485311Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T08:36:56.310785Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "d847a503-2bd8-4297-a917-8789854bbbdf",
                "start": "2026-10-27T08:36:25.9174801Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T06:45:53.3924184Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "150cca85-8b3d-44e6-ad1a-2e5ac059e2df",
                "start": "2026-10-27T06:45:24.4810815Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T06:15:17.1734177Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "1db862a2-6df5-41a7-a71a-02ca24eab7da",
                "start": "2026-10-27T06:09:51.1598474Z",
                "status": "CANCELLED"
              },
              {
                "end": "2026-10-26T18:15:51.642450Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "2b43720a-f2bb-47bb-a456-9dac546a4eb4",
                "start": "2026-10-26T18:15:14.6320687Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T02:12:10.4565917Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "c2bf877a-9ff2-4852-aa6b-f0503b71b2f3",
                "start": "2026-10-24T02:11:38.9387923Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:40:16.5003956Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "4ea4687d-5e43-4933-8db5-860286d0f681",
                "start": "2026-10-24T01:39:46.1269955Z",
                "status": "SUCCEEDED"
              }
            ],
            "rows_read": null,
            "rows_written": null,
            "run_id": "7237d82d-a728-4286-8891-6f548097cdcd",
            "start": "2026-10-28T08:16:11.3116784Z",
            "status": "SUCCEEDED"
          }
        }
      ]
    },
    {
      "check": "LAYER_FRESHNESS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:LAYER_FRESHNESS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SOURCE_CHANGES",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:SOURCE_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "NEXT_LOAD",
      "observed_at": "2026-10-28T09:20:33.717357Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "ca2ef01b13bd58ca8683c3609430f6d28193e0aff841cef381e1d7998c76e425",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:7f616a0bcd8016f94253e610fd057e1f8c034a2a4f2308173fa82cd0bb89d964"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "01:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        },
        {
          "collected_at": "2026-10-28T09:20:33.717357Z",
          "freshness": "CURRENT",
          "id": "2f9368a12c6260f1a88dc55126aa98ccbed0f5a328d86de68e9c9601e0a327ef",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:20:33.717357Z",
          "provenance": {
            "collector": "microsoft-runtime:50ed9389d7d5682c8f2f36c6c2f43a2a3731a84b0c91204d9e25890e096564dc",
            "evidence_ids": [
              "sha256:963d00f6f461a122327da82562cac5406ca9717ea982ad75895d6ce4e06d2232"
            ],
            "locator": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "value": {
            "native_schedules": {
              "value": []
            },
            "next_due": null,
            "reason": "Job schedule recurrence retained; unsupported recurrence types remain a named coverage gap."
          }
        }
      ]
    },
    {
      "check": "CONNECTION_MODE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:CONNECTION_MODE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SECURITY_PRESENCE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:SECURITY_PRESENCE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "DEFINITION_CHANGES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:DEFINITION_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    }
  ],
  "path": [
    "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
    "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
    "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
    "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
    "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
    "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
    "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
    "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
    "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce",
    "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
    "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
    "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
    "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
    "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
    "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
    "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
    "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
    "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
    "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
  ],
  "refresh_operations": 10,
  "what_triage_suggests": "Triage has unavailable checks (AUTOMATIC_UPDATES, LAYER_FRESHNESS, SOURCE_CHANGES, CONNECTION_MODE, SECURITY_PRESENCE, DEFINITION_CHANGES); this does not establish that those mechanisms are absent."
}
```

Tool decisions:
```json
[
  {
    "arguments": {
      "layer": "native:4caf47d120d4fd198ffe",
      "purpose": "recreate",
      "query": "EVALUATE ROW(\"Movement Units movement_id 1\", CALCULATE([Movement Units], 'Movements'[movement_id] = 1), \"Movement Units total\", [Movement Units])"
    },
    "tool": "run_dax",
    "tool_use_id": "toolu_01FUQGARmxPXBs25GyqWckF9",
    "turn": 1
  },
  {
    "arguments": {
      "layer": "native:4caf47d120d4fd198ffe",
      "purpose": "lookup",
      "query": "EVALUATE TOPN(20, SUMMARIZECOLUMNS('Movements'[movement_id], \"u\", [Movement Units]), 'Movements'[movement_id], ASC)"
    },
    "tool": "run_dax",
    "tool_use_id": "toolu_01UvYoApesmzcXsRuEdisQDC",
    "turn": 1
  },
  {
    "arguments": {
      "node": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
    },
    "tool": "get_job_runs",
    "tool_use_id": "toolu_01FdgLuL8p1yDDiHq6rsTcjo",
    "turn": 1
  },
  {
    "arguments": {
      "layer": "native:e95b94fd338e7086320f",
      "purpose": "compare",
      "query": "SELECT movement_id, units, event_day, movement_type, source_modified_at_utc FROM [dbo].[stock_movements_round_two_20261003] WHERE movement_id = 1"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01WR3hPy9N1ue87gQt4EoAjp",
    "turn": 4
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "compare",
      "query": "SELECT movement_id, units, event_day, movement_type, source_modified_at_utc FROM [app].[stock_movements_round_two_20261003] WHERE movement_id = 1"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01C8dZ3ZL1iBbMjSGUcTZY7D",
    "turn": 4
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "history",
      "query": "SELECT SUM(units) AS units_as_of FROM [app].[stock_movements_round_two_20261003] FOR SYSTEM_TIME AS OF '2026-10-20T12:00:00' WHERE movement_id = 1"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_015Ts7mZ22GT7UQiWtCkdXVP",
    "turn": 4
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "history",
      "query": "SELECT t.name, t.temporal_type_desc, h.name AS history_table, c1.name AS period_start, c2.name AS period_end FROM sys.tables t LEFT JOIN sys.tables h ON h.object_id = t.history_table_id LEFT JOIN sys.periods p ON p.object_id = t.object_id LEFT JOIN sys.columns c1 ON c1.object_id = t.object_id AND c1.column_id = p.start_column_id LEFT JOIN sys.columns c2 ON c2.object_id = t.object_id AND c2.column_id = p.end_column_id WHERE t.name = 'stock_movements_round_two_20261003'"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01247YRzBC7PWhcXJMzhTvpC",
    "turn": 7
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "history",
      "query": "SELECT movement_id, units, movement_type, source_modified_at_utc FROM [app].[stock_movements_round_two_20261003] FOR SYSTEM_TIME ALL WHERE movement_id = 1 ORDER BY source_modified_at_utc"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01LzzAoVW5kJVhQMh2dsUiTb",
    "turn": 10
  },
  {
    "arguments": {
      "cause": "Movement Units is SUM('Movements'[units]) with no date or as-of logic. The Movements table reads the Lakehouse table dbo.stock_movements_round_two_20261003 directly (Direct Lake), and the copy job investigation_round_two_history_probe_20261003 overwrites that table from app.stock_movements_round_two_20261003 on each run. So the visual always shows current rows and never works out a past value. Current value for movement_id 1 is 16 in the model, the Lakehouse table and the source table (one row in each, units 16). A native read of the source table's system-versioned history for 2026-10-20 12:00 UTC succeeded but returned NULL (no row), and FOR SYSTEM_TIME ALL keeps only one version of movement 1 (units 16). The retained history therefore gives no value for movement 1 at that time. The cause of that gap was not established: the catalog query for the history setup and period columns was rejected. Lakehouse table time travel was not checked. The source_modified_at_utc column (2026-10-03 22:51:16) is an application column, not the history validity period. The two failed pipeline runs (2026-10-27 14:25 and 2026-10-28 05:59 UTC) were followed by successful runs; the latest load succeeded 2026-10-28 08:15-08:17 UTC (360 rows read and written) and the model refresh succeeded at 08:22 UTC.",
      "checked": [
        "native:4caf47d120d4fd198ffe",
        "native:e95b94fd338e7086320f",
        "native:9e3796a26d8d5c1a039e",
        "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
        "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
      ],
      "evidence_ids": [
        "case-evidence:6b5f100ca5bcde9abaf0b529b75358497aa2c826fc2adeac290469e3e220eeff",
        "case-evidence:4be86fdbdace11bb982a66623faa79025b7a34be37411fc8ddf1acda5c5c312c",
        "case-evidence:5e162e5e5ec0185bde541361cfff86a3e09cc7ed92dc607657b1f972e88d740b",
        "case-evidence:89790e38ee60f4f7405dc686e2009340a5103f944327734cace28bb346b9dbc0",
        "case-evidence:2eb29e37a265bf1b892944f183d9a02c40abea589c6f6a4111cfaea92ca8e57d",
        "case-evidence:f9749e9281ac69ae7ea4a4850a2ecd16b3de1bb730c05b858eb52f7c0c09d549",
        "case-evidence:dcb5212e02f2d228f19a603fc3520f90998df57594750d4861e579614a620421",
        "case-evidence:28b30c849239ebe5dd232ce3522f29f589a644a46ec18dd3b52f169f4c3c54fe",
        "a87545a3e875d2260873432f55b447cbbe4d461928395aa15254ff574d34c5f6",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json"
      ],
      "numbers": [
        "16",
        "1",
        "7661",
        null
      ],
      "verdict": "definition explained"
    },
    "tool": "submit_finding",
    "tool_use_id": "toolu_016MHV2pcXP4YZHCE58W1mQw",
    "turn": 13
  },
  {
    "arguments": {
      "cause": "Movement Units is SUM('Movements'[units]) with no date or as-of logic. The Movements table reads the Lakehouse table dbo.stock_movements_round_two_20261003 directly (Direct Lake), and the copy job investigation_round_two_history_probe_20261003 overwrites that table from app.stock_movements_round_two_20261003 on each run. So the visual always shows current rows and never works out a past value. Current value for movement_id 1 is 16 in the model, the Lakehouse table and the source table (one row in each, units 16). A native read of the source table's system-versioned history for 2026-10-20 12:00 UTC succeeded but returned NULL (no row), and FOR SYSTEM_TIME ALL keeps only one version of movement 1 (units 16). The retained history therefore gives no value for movement 1 at that time. The cause of that gap was not established: the catalog query for the history setup and period columns was rejected. Lakehouse table time travel was not checked. The source_modified_at_utc column (2026-10-03 22:51:16) is an application column, not the history validity period. The two failed pipeline runs (2026-10-27 14:25 and 2026-10-28 05:59 UTC) were followed by successful runs; the latest load succeeded 2026-10-28 08:15-08:17 UTC (360 rows read and written) and the model refresh succeeded at 08:22 UTC.",
      "checked": [
        "native:4caf47d120d4fd198ffe",
        "native:e95b94fd338e7086320f",
        "native:9e3796a26d8d5c1a039e"
      ],
      "evidence_ids": [
        "case-evidence:6b5f100ca5bcde9abaf0b529b75358497aa2c826fc2adeac290469e3e220eeff",
        "case-evidence:4be86fdbdace11bb982a66623faa79025b7a34be37411fc8ddf1acda5c5c312c",
        "case-evidence:5e162e5e5ec0185bde541361cfff86a3e09cc7ed92dc607657b1f972e88d740b",
        "case-evidence:89790e38ee60f4f7405dc686e2009340a5103f944327734cace28bb346b9dbc0",
        "case-evidence:2eb29e37a265bf1b892944f183d9a02c40abea589c6f6a4111cfaea92ca8e57d",
        "case-evidence:f9749e9281ac69ae7ea4a4850a2ecd16b3de1bb730c05b858eb52f7c0c09d549",
        "case-evidence:dcb5212e02f2d228f19a603fc3520f90998df57594750d4861e579614a620421",
        "case-evidence:28b30c849239ebe5dd232ce3522f29f589a644a46ec18dd3b52f169f4c3c54fe",
        "a87545a3e875d2260873432f55b447cbbe4d461928395aa15254ff574d34c5f6",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json"
      ],
      "numbers": [
        "16",
        "1",
        "7661",
        null
      ],
      "verdict": "definition explained"
    },
    "tool": "submit_finding",
    "tool_use_id": "toolu_01VCndY7AuhN84Rq4gFzVKqL",
    "turn": 16
  },
  {
    "arguments": {
      "cause": "Movement Units is SUM('Movements'[units]) with no date or as-of logic. The Movements table reads the Lakehouse table dbo.stock_movements_round_two_20261003 directly (Direct Lake), and the copy job investigation_round_two_history_probe_20261003 overwrites that table from app.stock_movements_round_two_20261003 on each run. So the visual always shows current rows and never works out a past value. Current value for movement_id 1 is 16 in the model, the Lakehouse table and the source table (one row in each, units 16). A native read of the source table's system-versioned history for 2026-10-20 12:00 UTC succeeded but returned NULL (no row), and FOR SYSTEM_TIME ALL keeps only one version of movement 1 (units 16). The retained history therefore gives no value for movement 1 at that time. The cause of that gap was not established: the catalog query for the history setup and period columns was rejected. Lakehouse table time travel was not checked. The source_modified_at_utc column (2026-10-03 22:51:16) is an application column, not the history validity period. The two failed pipeline runs (2026-10-27 14:25 and 2026-10-28 05:59 UTC) were followed by successful runs; the latest load succeeded 2026-10-28 08:15-08:17 UTC (360 rows read and written) and the model refresh succeeded at 08:22 UTC.",
      "checked": [
        "native:4caf47d120d4fd198ffe",
        "native:e95b94fd338e7086320f",
        "native:9e3796a26d8d5c1a039e"
      ],
      "evidence_ids": [
        "case-evidence:6b5f100ca5bcde9abaf0b529b75358497aa2c826fc2adeac290469e3e220eeff",
        "case-evidence:4be86fdbdace11bb982a66623faa79025b7a34be37411fc8ddf1acda5c5c312c",
        "case-evidence:5e162e5e5ec0185bde541361cfff86a3e09cc7ed92dc607657b1f972e88d740b",
        "case-evidence:89790e38ee60f4f7405dc686e2009340a5103f944327734cace28bb346b9dbc0",
        "case-evidence:2eb29e37a265bf1b892944f183d9a02c40abea589c6f6a4111cfaea92ca8e57d",
        "case-evidence:f9749e9281ac69ae7ea4a4850a2ecd16b3de1bb730c05b858eb52f7c0c09d549",
        "case-evidence:dcb5212e02f2d228f19a603fc3520f90998df57594750d4861e579614a620421",
        "case-evidence:28b30c849239ebe5dd232ce3522f29f589a644a46ec18dd3b52f169f4c3c54fe"
      ],
      "numbers": [
        "16",
        "1",
        "7661",
        null
      ],
      "verdict": "definition explained"
    },
    "tool": "submit_finding",
    "tool_use_id": "toolu_018zoFjVGbsNJPgMW6tq4CmS",
    "turn": 19
  },
  {
    "arguments": {
      "cause": "Movement Units is SUM('Movements'[units]) with no date or as-of logic. The Movements table reads the Lakehouse table dbo.stock_movements_round_two_20261003 directly (Direct Lake), and the copy job investigation_round_two_history_probe_20261003 overwrites that table from app.stock_movements_round_two_20261003 on each run. So the visual always shows current rows and never works out a past value. Current value for movement_id 1 is 16 in the model, the Lakehouse table and the source table (one row in each, units 16). A native read of the source table's system-versioned history for 2026-10-20 12:00 UTC succeeded but returned NULL (no row), and FOR SYSTEM_TIME ALL keeps only one version of movement 1 (units 16). The retained history therefore gives no value for movement 1 at that time. Limitation: why there is no version at that time was not established, because the history period columns and setup were not read. Lakehouse table time travel was not checked. The source_modified_at_utc column (2026-10-03 22:51:16) is an application column, not the history validity period. The two failed pipeline runs (2026-10-27 14:25 and 2026-10-28 05:59 UTC) were followed by successful runs; the latest load succeeded 2026-10-28 08:15-08:17 UTC (360 rows read and written) and the model refresh succeeded at 08:22 UTC.",
      "checked": [
        "native:4caf47d120d4fd198ffe",
        "native:e95b94fd338e7086320f",
        "native:9e3796a26d8d5c1a039e"
      ],
      "evidence_ids": [
        "case-evidence:6b5f100ca5bcde9abaf0b529b75358497aa2c826fc2adeac290469e3e220eeff",
        "case-evidence:4be86fdbdace11bb982a66623faa79025b7a34be37411fc8ddf1acda5c5c312c",
        "case-evidence:5e162e5e5ec0185bde541361cfff86a3e09cc7ed92dc607657b1f972e88d740b",
        "case-evidence:89790e38ee60f4f7405dc686e2009340a5103f944327734cace28bb346b9dbc0",
        "case-evidence:2eb29e37a265bf1b892944f183d9a02c40abea589c6f6a4111cfaea92ca8e57d",
        "case-evidence:f9749e9281ac69ae7ea4a4850a2ecd16b3de1bb730c05b858eb52f7c0c09d549",
        "case-evidence:28b30c849239ebe5dd232ce3522f29f589a644a46ec18dd3b52f169f4c3c54fe"
      ],
      "numbers": [
        "16",
        "1",
        "7661",
        null
      ],
      "verdict": "definition explained"
    },
    "tool": "submit_finding",
    "tool_use_id": "toolu_011yfabT5UN2XYG1epNr4jFq",
    "turn": 22
  }
]
```

Queries:
```json
[
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/movement_id",
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units"
    ],
    "duration_seconds": 5.377762413000028,
    "executed_text": "EVALUATE TOPN(251,ROW(\"Movement Units movement_id 1\",CALCULATE([Movement Units],'Movements'[movement_id] = 1),\"Movement Units total\",[Movement Units]))",
    "id": "query:7d5d66b2383c3b57c500e287e888d8e30a8c7b7ebf434257498e66fa3bae72a4:1",
    "layer": "native:4caf47d120d4fd198ffe",
    "parameters": [],
    "purpose": "recreate",
    "result": {
      "rows": [
        {
          "[Movement Units movement_id 1]": 16,
          "[Movement Units total]": 7661
        }
      ],
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "d066e492923d4a1918cbb2f26debce16da26f12e95085c5df2c8175369d69a3e",
    "row_count": 1,
    "signature": "7d5d66b2383c3b57c500e287e888d8e30a8c7b7ebf434257498e66fa3bae72a4",
    "status": "SUCCEEDED",
    "text": "EVALUATE ROW(\"Movement Units movement_id 1\", CALCULATE([Movement Units], 'Movements'[movement_id] = 1), \"Movement Units total\", [Movement Units])",
    "time": "2026-10-28T09:21:20.487962+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/movement_id",
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units"
    ],
    "duration_seconds": 2.2019843939999646,
    "executed_text": "EVALUATE TOPN(251,TOPN(20,SUMMARIZECOLUMNS('Movements'[movement_id],\"u\",[Movement Units]),'Movements'[movement_id],ASC))",
    "id": "query:2e56d3c4c35b45855ce4442a3af5eef2331e8e32366085729470af160f3f54e4:2",
    "layer": "native:4caf47d120d4fd198ffe",
    "parameters": [],
    "purpose": "lookup",
    "result": {
      "rows_sample": [
        {
          "Movements[movement_id]": 20,
          "[u]": 18
        },
        {
          "Movements[movement_id]": 19,
          "[u]": 38
        },
        {
          "Movements[movement_id]": 15,
          "[u]": 38
        }
      ],
      "sample_note": "First3 native rows only; full sealed result retained, native total row_count unchanged.",
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "b32c92dd8dba21372d50280f2e170f8510ffd27a74633884c24c033e4afbfb1b",
    "row_count": 20,
    "signature": "2e56d3c4c35b45855ce4442a3af5eef2331e8e32366085729470af160f3f54e4",
    "status": "SUCCEEDED",
    "text": "EVALUATE TOPN(20, SUMMARIZECOLUMNS('Movements'[movement_id], \"u\", [Movement Units]), 'Movements'[movement_id], ASC)",
    "time": "2026-10-28T09:21:26.135242+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003"
    ],
    "duration_seconds": 7.09807860799998,
    "executed_text": "SELECT TOP 251 [stock_movements_round_two_20261003].[movement_id] AS [movement_id], [stock_movements_round_two_20261003].[units] AS [units], [stock_movements_round_two_20261003].[event_day] AS [event_day], [stock_movements_round_two_20261003].[movement_type] AS [movement_type], [stock_movements_round_two_20261003].[source_modified_at_utc] AS [source_modified_at_utc] FROM [dbo].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003] WHERE [stock_movements_round_two_20261003].[movement_id] = CAST(@p0 AS BIGINT)",
    "id": "query:06842e4fe4943a264785aadb346291518df94fba4b8056eaac92a1f6d45688f2:3",
    "layer": "native:e95b94fd338e7086320f",
    "parameters": [
      {
        "name": "@p0",
        "value": "1"
      }
    ],
    "purpose": "compare",
    "result": {
      "column_types": {
        "event_day": "String",
        "movement_id": "Int64",
        "movement_type": "String",
        "source_modified_at_utc": "DateTime",
        "units": "Int64"
      },
      "execution_identity": {
        "database": "round_two_bronze_20261003",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "event_day": "2026-09-11",
          "movement_id": "1",
          "movement_type": "RECEIPT",
          "source_modified_at_utc": "2026-10-03 22:51:16.882024",
          "units": "16"
        }
      ]
    },
    "result_digest": "cdca116cede14d43c35255771b2e99566721b50767e03fffef8b81bf9f951dc6",
    "row_count": 1,
    "signature": "06842e4fe4943a264785aadb346291518df94fba4b8056eaac92a1f6d45688f2",
    "status": "SUCCEEDED",
    "text": "SELECT movement_id, units, event_day, movement_type, source_modified_at_utc FROM [dbo].[stock_movements_round_two_20261003] WHERE movement_id = 1",
    "time": "2026-10-28T09:21:52.125543+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 10.460565817000031,
    "executed_text": "SELECT TOP 251 [stock_movements_round_two_20261003].[movement_id] AS [movement_id], [stock_movements_round_two_20261003].[units] AS [units], [stock_movements_round_two_20261003].[event_day] AS [event_day], [stock_movements_round_two_20261003].[movement_type] AS [movement_type], [stock_movements_round_two_20261003].[source_modified_at_utc] AS [source_modified_at_utc] FROM [app].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003] WHERE [stock_movements_round_two_20261003].[movement_id] = CAST(@p0 AS BIGINT)",
    "id": "query:8ad338eec2406be7278bbd6c2edeb034dec53ece34c5e166819a65d28feb8b67:4",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [
      {
        "name": "@p0",
        "value": "1"
      }
    ],
    "purpose": "compare",
    "result": {
      "column_types": {
        "event_day": "String",
        "movement_id": "Int64",
        "movement_type": "String",
        "source_modified_at_utc": "DateTime",
        "units": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T09:22:09.678261+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T09:21:59.831265+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "event_day": "2026-09-11",
          "movement_id": "1",
          "movement_type": "RECEIPT",
          "source_modified_at_utc": "2026-10-03 22:51:16.882024",
          "units": "16"
        }
      ]
    },
    "result_digest": "088e9ce2a54773b7f16e9cf600f2f12e33787718bf3b864f49996fb76b831932",
    "row_count": 1,
    "signature": "8ad338eec2406be7278bbd6c2edeb034dec53ece34c5e166819a65d28feb8b67",
    "status": "SUCCEEDED",
    "text": "SELECT movement_id, units, event_day, movement_type, source_modified_at_utc FROM [app].[stock_movements_round_two_20261003] WHERE movement_id = 1",
    "time": "2026-10-28T09:21:59.492079+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 3.625160254999969,
    "executed_text": "SELECT TOP 251 SUM([stock_movements_round_two_20261003].[units]) AS [units_as_of] FROM [app].[stock_movements_round_two_20261003] FOR SYSTEM_TIME AS OF @p1 AS [stock_movements_round_two_20261003] WHERE [stock_movements_round_two_20261003].[movement_id] = CAST(@p0 AS BIGINT)",
    "id": "query:a1b1a36b24f2264026b32bb10bdb4674ba0374f7da00c511b033ff1a8e370d09:5",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [
      {
        "name": "@p0",
        "value": "1"
      },
      {
        "name": "@p1",
        "value": "2026-10-20T12:00:00"
      }
    ],
    "purpose": "history",
    "result": {
      "column_types": {
        "units_as_of": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T09:22:13.623447+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T09:22:10.897699+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "units_as_of": null
        }
      ]
    },
    "result_digest": "4a62dc6f74be865ae67cc3bcfa2d32ec274eec1181ac506fe0b31ec0020c032e",
    "row_count": 1,
    "signature": "a1b1a36b24f2264026b32bb10bdb4674ba0374f7da00c511b033ff1a8e370d09",
    "status": "SUCCEEDED",
    "text": "SELECT SUM(units) AS units_as_of FROM [app].[stock_movements_round_two_20261003] FOR SYSTEM_TIME AS OF '2026-10-20T12:00:00' WHERE movement_id = 1",
    "time": "2026-10-28T09:22:10.274459+00:00",
    "truncated": false
  },
  {
    "duration_seconds": 0,
    "error": "SQL object unavailable or view dependencies not validated",
    "error_type": "QueryRejection",
    "failure_class": "wrong column or table",
    "id": "query:76155af6b656b23fe3625213402cc0bdd23fcd9ba397705de06c1bcf3593a2a6:6",
    "layer": "native:9e3796a26d8d5c1a039e",
    "native_dispatched": false,
    "purpose": "history",
    "result_digest": null,
    "row_count": null,
    "schema_slice": [
      {
        "columns": [
          {
            "column_id": 2,
            "computed_definition": null,
            "data_type": "int",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 4,
            "name": "warehouse_id",
            "object_id": 1938105945,
            "precision": 10,
            "scale": 0
          },
          {
            "column_id": 8,
            "computed_definition": null,
            "data_type": "timestamp",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 8,
            "name": "source_row_version",
            "object_id": 1938105945,
            "precision": 0,
            "scale": 0
          },
          {
            "column_id": 5,
            "computed_definition": null,
            "data_type": "nvarchar",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 200,
            "name": "event_day",
            "object_id": 1938105945,
            "precision": 0,
            "scale": 0
          },
          {
            "column_id": 6,
            "computed_definition": null,
            "data_type": "nvarchar",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 200,
            "name": "movement_type",
            "object_id": 1938105945,
            "precision": 0,
            "scale": 0
          },
          {
            "column_id": 3,
            "computed_definition": null,
            "data_type": "int",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 4,
            "name": "product_id",
            "object_id": 1938105945,
            "precision": 10,
            "scale": 0
          },
          {
            "column_id": 4,
            "computed_definition": null,
            "data_type": "int",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 4,
            "name": "units",
            "object_id": 1938105945,
            "precision": 10,
            "scale": 0
          },
          {
            "column_id": 7,
            "computed_definition": null,
            "data_type": "datetime2",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": true,
            "max_length": 8,
            "name": "source_modified_at_utc",
            "object_id": 1938105945,
            "precision": 27,
            "scale": 7
          },
          {
            "column_id": 1,
            "computed_definition": null,
            "data_type": "int",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 4,
            "name": "movement_id",
            "object_id": 1938105945,
            "precision": 10,
            "scale": 0
          }
        ],
        "id": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945",
        "name": "stock_movements_round_two_20261003",
        "schema_name": "app",
        "type_desc": "USER_TABLE"
      }
    ],
    "signature": "76155af6b656b23fe3625213402cc0bdd23fcd9ba397705de06c1bcf3593a2a6",
    "status": "ERROR",
    "text": "SELECT t.name, t.temporal_type_desc, h.name AS history_table, c1.name AS period_start, c2.name AS period_end FROM sys.tables t LEFT JOIN sys.tables h ON h.object_id = t.history_table_id LEFT JOIN sys.periods p ON p.object_id = t.object_id LEFT JOIN sys.columns c1 ON c1.object_id = t.object_id AND c1.column_id = p.start_column_id LEFT JOIN sys.columns c2 ON c2.object_id = t.object_id AND c2.column_id = p.end_column_id WHERE t.name = 'stock_movements_round_two_20261003'",
    "time": "2026-10-28T09:22:22.685606+00:00"
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 3.3088554130000034,
    "executed_text": "SELECT TOP 251 [stock_movements_round_two_20261003].[movement_id] AS [movement_id], [stock_movements_round_two_20261003].[units] AS [units], [stock_movements_round_two_20261003].[movement_type] AS [movement_type], [stock_movements_round_two_20261003].[source_modified_at_utc] AS [source_modified_at_utc] FROM [app].[stock_movements_round_two_20261003] FOR SYSTEM_TIME ALL AS [stock_movements_round_two_20261003] WHERE [stock_movements_round_two_20261003].[movement_id] = CAST(@p0 AS BIGINT) ORDER BY [source_modified_at_utc]",
    "id": "query:ce1023d8cdc14bdd197a306908d7266239f1e470c54616c06e6e12905756c6c1:7",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [
      {
        "name": "@p0",
        "value": "1"
      }
    ],
    "purpose": "history",
    "result": {
      "column_types": {
        "movement_id": "Int64",
        "movement_type": "String",
        "source_modified_at_utc": "DateTime",
        "units": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T09:22:31.437508+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T09:22:28.733495+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "movement_id": "1",
          "movement_type": "RECEIPT",
          "source_modified_at_utc": "2026-10-03 22:51:16.882024",
          "units": "16"
        }
      ]
    },
    "result_digest": "d6d0c1aaf97239e7032c7a90e4b2bcea300270394c83d87f75d5d17bd4247960",
    "row_count": 1,
    "signature": "ce1023d8cdc14bdd197a306908d7266239f1e470c54616c06e6e12905756c6c1",
    "status": "SUCCEEDED",
    "text": "SELECT movement_id, units, movement_type, source_modified_at_utc FROM [app].[stock_movements_round_two_20261003] FOR SYSTEM_TIME ALL WHERE movement_id = 1 ORDER BY source_modified_at_utc",
    "time": "2026-10-28T09:22:28.394479+00:00",
    "truncated": false
  }
]
```

Final answer:
```json
"definition explained. Movement Units is SUM('Movements'[units]) with no date or as-of logic. The Movements table reads the Lakehouse table dbo.stock_movements_round_two_20261003 directly (Direct Lake), and the copy job investigation_round_two_history_probe_20261003 overwrites that table from app.stock_movements_round_two_20261003 on each run. So the visual always shows current rows and never works out a past value. Current value for movement_id 1 is 16 in the model, the Lakehouse table and the source table (one row in each, units 16). A native read of the source table's system-versioned history for 2026-10-20 12:00 UTC succeeded but returned NULL (no row), and FOR SYSTEM_TIME ALL keeps only one version of movement 1 (units 16). The retained history therefore gives no value for movement 1 at that time. Limitation: why there is no version at that time was not established, because the history period columns and setup were not read. Lakehouse table time travel was not checked. The source_modified_at_utc column (2026-10-03 22:51:16) is an application column, not the history validity period. The two failed pipeline runs (2026-10-27 14:25 and 2026-10-28 05:59 UTC) were followed by successful runs; the latest load succeeded 2026-10-28 08:15-08:17 UTC (360 rows read and written) and the model refresh succeeded at 08:22 UTC.\nNumbers: 16, 1, 7661, BLANK.\nChecked: Application load fixture 20261003, round_two_bronze_20261003, ordersops.\nNative comparisons are observational snapshots; aligned query-bound versions are not established.\nCatalog bookkeeping unavailable: collector containment (recovered from literal native address), current inventory availability, inventory content hashes (metadata digests are derived and labelled), inventory provenance, per-asset collector timestamps. This does not block investigation; successful queries establish present readability only.\nattestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
```

Sealed expected:
```json
{
  "basis": "Native scenario observations verified before sealing; same fact-based class contract as sealed v2 dev template v2-before-temporal-retention-v1. No DIA output used to author wording or expectations.",
  "case_id": "v3-before-temporal-retention",
  "cause": "Requested time precedes retained temporal evidence; historical quantity cannot be established.",
  "estate": "fixture",
  "expectation_basis": "Practice source literals, declared definitions and reversible scenario plan; never an engine answer.",
  "fixture": "baseline",
  "id": "v3-before-temporal-retention",
  "layer": "source history boundary",
  "split": "HELD_OUT_V3",
  "variation": "independent new held-out v3",
  "verdict": "not found"
}
```

Saved checkpoint SHA-256: 07babf104ef5ff2f345527207cb4fb563db5a48b7c1df6973dbecc9ba537095f. Only recorded tool choices are shown; no new queries or model calls.

### v3-record-absent-everywhere
Verdict mismatch: the sealed expected answer is 'as designed' (the record is intentionally absent at source and every layer), but the delivered answer gives 'not found' with a tone implying the record might have existed and been removed, and explicitly states 'The source system doesn't have it now' with a hedge about whether it existed earlier. The sealed expectation treats the absence as a designed fixture condition, not an unexplained missing record. Layer match: both identify the source application as where the absence is confirmed. Cause: the sealed cause is 'Record900099 is absent at source and every compared reachable layer; BLANK is not zero' — the delivered answer confirms absence at all layers but does not state 'as designed' or that BLANK is not zero; it instead frames this as an unexplained gap and hedges about possible earlier existence, which is a substantively different cause characterisation. Handoff quality is 0 because the answer is resolved (ANSWERED status, no handoff left), so there is no handoff to grade. Restrict the cause to what the cited native evidence establishes.

Intake:
```json
{
  "compared_with": {
    "kind": "SOURCE_SYSTEM",
    "source": "d41e1c7af0bee9e569e9e4085c645331f3eb19ad9e7651dea93c571007beaaa1"
  },
  "description": "I'm looking for movement900099 from around 2026-09-12. I expected to see it, but it doesn't appear in the Movement Units visual on the Application Movements page. I also checked the application export, and it isn't there either. I'm not reporting an amount for this movement. I just can't find the record anywhere.",
  "details": {
    "approximate_date": "2026-09-12",
    "record": "movement900099"
  },
  "issue_type": "RECORD_MISSING",
  "measure_candidates": [
    {
      "id": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
      "name": "Movement Units"
    }
  ],
  "page": "e4d6e671103ca3746c4ca9435fc635e13ae0a08bf09ffa515580b7f1a50fd7f7",
  "report": "3ba93e33aa41f6b91b0ef623bfd66bf2d9ec9eefd5e583643e6462e0dbd5b2ed",
  "status": "READY",
  "version": "IntakeRequest/1",
  "visual": "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce"
}
```

Target:
```json
{
  "layers": {
    "native:4caf47d120d4fd198ffe": {
      "dialect": "DAX",
      "label": "Application load fixture 20261003"
    },
    "native:9e3796a26d8d5c1a039e": {
      "dialect": "T-SQL",
      "label": "ordersops"
    },
    "native:e95b94fd338e7086320f": {
      "dialect": "T-SQL",
      "label": "round_two_bronze_20261003"
    }
  },
  "path": {
    "as_of": null,
    "declared_route_bridges": [
      {
        "column_bindings": [
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/movement_id",
            "semantic_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/movement_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/warehouse_id",
            "semantic_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/warehouse_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/product_id",
            "semantic_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/product_id"
          },
          {
            "basis": "EXACT_PARTITION_SOURCE_COLUMN",
            "physical_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/units",
            "semantic_column": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/units"
          }
        ],
        "confidence": "DECLARED",
        "definition_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/part/model.bim",
        "definition_hash": "a87545a3e875d2260873432f55b447cbbe4d461928395aa15254ff574d34c5f6",
        "graph_nodes": [
          "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
          "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c"
        ],
        "literal_expression": "let database = Sql.Database(\"i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com\", \"fbbccea4-d943-4f58-b91f-e6cbcb912620\") in database",
        "native_ownership": [
          {
            "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/native-relation/5847348b3fe731e359d488a7c71321000b58db7362e3d339eda7af1eb0e37c92",
            "inventory_digest_qualification": "Retained inventory digests matched; this is not a current query-bound attestation.",
            "metadata": {
              "container_asset_hash": "d4fe38b53f7492e7e0634b5a277a155d2399772c5dd352b9f1371a48172ba817",
              "container_asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
              "context_hash": "42e974374d54fb08f1b1e3cc761ab80543200ed796a78917082f3bb2e6f8d0f6",
              "context_version": "4cae0d14-fd5d-4ff1-89ce-adf346790084",
              "endpoint_asset_hash": "dacb9d4b7db91da731f9c761c50043780a5dd2d501a41a33c559e8c7d20dc6e4",
              "endpoint_asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/fbbccea4-d943-4f58-b91f-e6cbcb912620",
              "observed_at": "2026-10-21T21:33:21.054850Z",
              "relation": {
                "evidence": [
                  {
                    "scope": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
                    "source_api": "fabric_item_relations_beta"
                  }
                ],
                "provenance": "DISCOVERED",
                "relation": "NATIVE_CASCADEDELETE",
                "source": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/fbbccea4-d943-4f58-b91f-e6cbcb912620",
                "target": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3"
              },
              "relation_pointer": "/graph/edges/843"
            }
          }
        ],
        "partition_source": {
          "entityName": "stock_movements_round_two_20261003",
          "expressionSource": "ApplicationLoadSource",
          "schemaName": "dbo",
          "type": "entity"
        },
        "physical_table": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
        "qualification": "Declared route only; value agreement and aligned snapshots are not implied.",
        "semantic_table": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements"
      },
      {
        "basis": "ESTATE_MANIFEST_BINDING",
        "binding": {
          "from_layer": "application",
          "provenance": "DECLARED_BY_DEFINITION",
          "to_layer": "landing"
        },
        "confidence": "DECLARED",
        "delivery_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
        "graph_nodes": [
          "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a"
        ],
        "producers": [
          {
            "audit": {
              "resource": "load-audit",
              "status": "PRESENT"
            },
            "audit_resource": {
              "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/bea673e0-a206-461e-9b2f-1b3b827e80de/table/dbo.load_run_audit",
              "id": "load-audit",
              "reach": {
                "adapter": "estate-reader",
                "address": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/bea673e0-a206-461e-9b2f-1b3b827e80de/table/dbo.load_run_audit",
                "reader": "investigator-reader"
              }
            },
            "delivery_asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
            "from_layer": "application",
            "history_resource": "load-history",
            "id": "application-load",
            "producer_asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c",
            "to_layer": "landing"
          }
        ],
        "qualification": "Declared mapping only; compare native values and retained load evidence to establish a cause.",
        "source_asset": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
      }
    ],
    "edges": [
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "06c8ec3ee7932e03fa0cee970e877a9f1ead91ab1a4024627716196f880d993b",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "17d8b434f56b320cba6bfc4ea56049014c39e0a7de73b71151e3c6d5bf7efabf",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "1e0a1aeaad2107704ac9c0da4f0b98a7649a1ac176baccd5e152e17c542d8c65",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "1eb4e7a69c34396385d68cd4b33f6b0007a5d7a9467a1a903fb6dfa02bfc6b99",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "20487352dbe71aaa186e04cd2a0b49c5fd2b9cb4fbff126fd0cfbec2b7b4edf1",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "binding_kind": "DIRECTLAKE_ENTITY",
          "catalog_id": "fbbccea4-d943-4f58-b91f-e6cbcb912620",
          "container_asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
          "container_binding": {
            "definition_hash": "23669eefffb853c2ca9014ee305dc7269cb2fa5a63160a33f5a2a1dc82cd665f",
            "observed_at": "2026-10-28T03:35:17.564451Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/native-relation/5847348b3fe731e359d488a7c71321000b58db7362e3d339eda7af1eb0e37c92",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "container_bindings": [
            {
              "definition_hash": "23669eefffb853c2ca9014ee305dc7269cb2fa5a63160a33f5a2a1dc82cd665f",
              "observed_at": "2026-10-28T03:35:17.564451Z",
              "source": "STATIC_DEFINITION",
              "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/native-relation/5847348b3fe731e359d488a7c71321000b58db7362e3d339eda7af1eb0e37c92",
              "span": {
                "kind": "JSON_POINTER",
                "path": ""
              }
            }
          ],
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
          "entity": "stock_movements_round_two_20261003",
          "expression_pointer": "/model/expressions/0",
          "expression_source": "ApplicationLoadSource",
          "physical_column_definition": {
            "definition_hash": "52c4a51badb36efea3e9a0ae19c764e87af8d48b152040b4e23ec7279e1f28e4",
            "observed_at": "2026-10-11T16:27:31.868191Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/units",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "physical_definition": {
            "definition_hash": "ec45d792a5e5f2d5c4bd2a04f33e4e5396583c1820af85c2f99f7722d124eaab",
            "observed_at": "2026-10-11T16:27:31.868191Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "schema": "dbo",
          "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com",
          "source_column": "units"
        },
        "provenance": {
          "definition_hash": "18be79d2ba4c304d1bba31d0823850f93bf964b2ff9feb002abe66a52463f43c",
          "observed_at": "2026-10-28T03:35:17.564451Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/part/model.bim",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/model/tables/0/columns/3/sourceColumn"
          }
        },
        "source": "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
        "target": "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "30577e94eeede86f93ae7f5c6d5c239e886ef3ca6899b04c13e4c44b33994c87",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "3070875cfdd22ac7316d00981f391fe2f98a8905cab84684200e5629ee85f028",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "33fcdac3222c9bb64858c980d34b1d898a3f22f194274e0c15a02c71b5ef90b8",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS",
          "connection_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/connection/3f5891f3-092b-4c26-b838-1d024e989501",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "destination_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
          "native_destination": {
            "artifactId": "33618b8d-46eb-4fe7-b80b-122c331260a3",
            "workspaceId": "149f8d99-1c66-4a0a-9624-759be002bb60"
          },
          "source_asset": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945",
          "source_query": null
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "4c0ff82c658eead5142c04a645bb4def66f5475cc1a73ba2f43153f6b08887be",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "57151bc18eeb30ee23d6da4e325cfd193ca0ed9bcf396a93fde0a7ced7adfb7c",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "666c5579851a32a3b5a9f56bc7018d2b92ae01305bf7c4e0d6f3f198604b10cb",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "669400314dab93454b3c1af392293ee7f557a499a1a8c432ed3c99dfa31b0df0",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "6792c3f8c484ae44c108b4e528d0fee217da3e35fbfb0966ab729c0fdee2d6f4",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "6e8fd211e6242e2ab549b7c841781ec6c41779696ad5e41f4eded9f85203ac98",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "binding_kind": "DIRECTLAKE_ENTITY",
          "catalog_id": "fbbccea4-d943-4f58-b91f-e6cbcb912620",
          "container_asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
          "container_binding": {
            "definition_hash": "23669eefffb853c2ca9014ee305dc7269cb2fa5a63160a33f5a2a1dc82cd665f",
            "observed_at": "2026-10-28T03:35:17.564451Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/native-relation/5847348b3fe731e359d488a7c71321000b58db7362e3d339eda7af1eb0e37c92",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "container_bindings": [
            {
              "definition_hash": "23669eefffb853c2ca9014ee305dc7269cb2fa5a63160a33f5a2a1dc82cd665f",
              "observed_at": "2026-10-28T03:35:17.564451Z",
              "source": "STATIC_DEFINITION",
              "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/native-relation/5847348b3fe731e359d488a7c71321000b58db7362e3d339eda7af1eb0e37c92",
              "span": {
                "kind": "JSON_POINTER",
                "path": ""
              }
            }
          ],
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
          "entity": "stock_movements_round_two_20261003",
          "expression_pointer": "/model/expressions/0",
          "expression_source": "ApplicationLoadSource",
          "physical_definition": {
            "definition_hash": "ec45d792a5e5f2d5c4bd2a04f33e4e5396583c1820af85c2f99f7722d124eaab",
            "observed_at": "2026-10-11T16:27:31.868191Z",
            "source": "STATIC_DEFINITION",
            "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
            "span": {
              "kind": "JSON_POINTER",
              "path": ""
            }
          },
          "schema": "dbo",
          "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com"
        },
        "provenance": {
          "definition_hash": "18be79d2ba4c304d1bba31d0823850f93bf964b2ff9feb002abe66a52463f43c",
          "observed_at": "2026-10-28T03:35:17.564451Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/part/model.bim",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/model/tables/0/partitions"
          }
        },
        "source": "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
        "target": "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "75f76c47eb9b8c836e06dee841dcf4664448e803c0c31b7dd674b71bb01124c4",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef"
        },
        "provenance": {
          "definition_hash": "01316df16f1ed86a54c0d457aaa55897df288ddc1f0ddf1bd79642bad475b997",
          "observed_at": "2026-10-27T04:06:22.268955Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/queryState/Values/projections/0/field/Measure"
          }
        },
        "source": "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce",
        "target": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "unknown": null,
        "valid_from": "2026-10-27T05:07:37.477893Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "7890d5105e809712fb07172a11aba9dbc04cc52b62155242cbec941b8ee9691b",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "7a22811d7d0ff9dbfc8559326230903f5071ee75b2d8a0cbc72433da2576f31a",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "7f56d35b6bd08b5d9a99614402b448388cce5494525f4283358e8085803c8246",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "completeness": "ROW_ONLY",
          "definition": {
            "bytes": 561,
            "sha256": "0899aeb41756ce76b582aed568a9d970d85295c35729f7c368dc454aabc939f9",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/0899aeb41756ce76b582aed568a9d970d85295c35729f7c368dc454aabc939f9"
          },
          "model_definition_hash": "18be79d2ba4c304d1bba31d0823850f93bf964b2ff9feb002abe66a52463f43c",
          "native_row_hash": "1ae9d5c404cc7749f33fa87a36ce702bef793fc0f3c5af3f018eaffde6acecbf"
        },
        "provenance": {
          "definition_hash": "0899aeb41756ce76b582aed568a9d970d85295c35729f7c368dc454aabc939f9",
          "observed_at": "2026-10-13T17:11:21.310792Z",
          "source": "ENGINE_DEPENDENCY",
          "source_id": "d06d2b3daefe976c10cbcbf1f2e3e207c8256f81621d3e73ceedf036b04cc58a",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/rows/1"
          }
        },
        "source": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "target": "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
        "unknown": null,
        "valid_from": "2026-10-13T17:11:21.310792Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "8612d5915b69806d03ff4a870b21803697afb820297940c7a4739b651bdf073f",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
        "properties": {
          "basis": "EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS",
          "connection_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/connection/3f5891f3-092b-4c26-b838-1d024e989501",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "destination_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
          "native_destination": {
            "artifactId": "33618b8d-46eb-4fe7-b80b-122c331260a3",
            "workspaceId": "149f8d99-1c66-4a0a-9624-759be002bb60"
          },
          "source_asset": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945",
          "source_query": null
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
        "target": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "97f1475120b8e2f1af28620b77651bc1afa195532d92b63e29dce5142293cbd6",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "b1326b7138cadf5b67e4fb8e437fd9b5c1860e4e061d56eb35a25b5a85ad7f83",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "COPY_MAPPING_WITH_EXACT_NATIVE_SOURCE",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
        "target": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "cbde8d939597b988cb7186578be98c95bab4275a11c9212027c5e6075df8df69",
        "kind": "DERIVED_IN_STEP",
        "label": "DERIVED_IN_STEP",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "target": "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "db4094fac448b7bc3463118d25c4523d3131409d5fbc9f4cc688cad8906edc7a",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "completeness": "ROW_ONLY",
          "definition": {
            "bytes": 561,
            "sha256": "0899aeb41756ce76b582aed568a9d970d85295c35729f7c368dc454aabc939f9",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/0899aeb41756ce76b582aed568a9d970d85295c35729f7c368dc454aabc939f9"
          },
          "model_definition_hash": "18be79d2ba4c304d1bba31d0823850f93bf964b2ff9feb002abe66a52463f43c",
          "native_row_hash": "019f5aa703e133bee59f21b8ec1db58e30de10b5199e0200b54b815b47584415"
        },
        "provenance": {
          "definition_hash": "0899aeb41756ce76b582aed568a9d970d85295c35729f7c368dc454aabc939f9",
          "observed_at": "2026-10-13T17:11:21.310792Z",
          "source": "ENGINE_DEPENDENCY",
          "source_id": "d06d2b3daefe976c10cbcbf1f2e3e207c8256f81621d3e73ceedf036b04cc58a",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/rows/0"
          }
        },
        "source": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "target": "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
        "unknown": null,
        "valid_from": "2026-10-13T17:11:21.310792Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "275b6a0f2d4511949028c3fe5a581b5c1b746fbab9f49a1ba8b76eb757d1a4e8",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "basis": "NATIVE_COPY_ACTIVITY_OWNERSHIP",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782"
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
        "target": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "base_confidence": "DECLARED",
        "confidence": "DECLARED",
        "id": "c120038524885218e7bc72b6f2a60622a60146a0285607c6d495b26b90ede2cb",
        "kind": "COMPUTED_FROM",
        "label": "COMPUTED_FROM",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c",
        "properties": {
          "basis": "NATIVE_INVOKE_COPY_JOB_UUID",
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c"
        },
        "provenance": {
          "definition_hash": "2ad010f0f8c75662d1fab7ebc89e2ef801da946287e2b62becbee58038477fdc",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c/part/pipeline-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "source": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
        "target": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      }
    ],
    "estate": "fixture",
    "nodes": [
      {
        "confidence": "DECLARED",
        "id": "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "movement_type"
            },
            "source": {
              "name": "movement_type"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "event_day"
            },
            "source": {
              "name": "event_day"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
        "kind": "COLUMN",
        "label": "units",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/units",
          "definition": {
            "bytes": 217,
            "sha256": "52c4a51badb36efea3e9a0ae19c764e87af8d48b152040b4e23ec7279e1f28e4",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/52c4a51badb36efea3e9a0ae19c764e87af8d48b152040b4e23ec7279e1f28e4"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
          "hidden": null,
          "native_kind": "LakehouseColumn",
          "retained_metadata_hash_encoding": "SORTED_JSON_SPACED"
        },
        "provenance": {
          "definition_hash": "52c4a51badb36efea3e9a0ae19c764e87af8d48b152040b4e23ec7279e1f28e4",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003/column/units",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-11T16:27:31.868191Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "source_modified_at_utc"
            },
            "source": {
              "name": "source_modified_at_utc"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
        "kind": "TABLE",
        "label": "Movements",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements",
          "definition": {
            "bytes": 714,
            "sha256": "0bcb2b34b6dc2d54895df1997446c507fc5ee161d94de631776d395219242b0a",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/0bcb2b34b6dc2d54895df1997446c507fc5ee161d94de631776d395219242b0a"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
          "hidden": null,
          "native_kind": "SemanticTable"
        },
        "provenance": {
          "definition_hash": "0bcb2b34b6dc2d54895df1997446c507fc5ee161d94de631776d395219242b0a",
          "observed_at": "2026-10-13T17:11:21.310792Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:11:21.310792Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
        "kind": "COLUMN",
        "label": "units",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/units",
          "dataType": "int64",
          "definition": {
            "bytes": 86,
            "sha256": "7cd3462864ca0771eb694e8d79584f93c5af27e2f4f2e9d773adc3b085a86e2f",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/7cd3462864ca0771eb694e8d79584f93c5af27e2f4f2e9d773adc3b085a86e2f"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
          "hidden": null,
          "native_kind": "SemanticColumn",
          "sourceColumn": "units"
        },
        "provenance": {
          "definition_hash": "7cd3462864ca0771eb694e8d79584f93c5af27e2f4f2e9d773adc3b085a86e2f",
          "observed_at": "2026-10-13T17:11:21.310792Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/units",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:11:21.310792Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "kind": "MEASURE",
        "label": "Movement Units",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units",
          "definition": {
            "bytes": 67,
            "sha256": "9bac4b87495b487a3fade3ae0eda2eac30dd456247b18b7be78404985255a599",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/9bac4b87495b487a3fade3ae0eda2eac30dd456247b18b7be78404985255a599"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
          "hidden": null,
          "native_kind": "Measure"
        },
        "provenance": {
          "definition_hash": "9bac4b87495b487a3fade3ae0eda2eac30dd456247b18b7be78404985255a599",
          "observed_at": "2026-10-13T17:11:21.310792Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:11:21.310792Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce",
        "kind": "VISUAL",
        "label": "Movement Units",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef/visual/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
          "definition": {
            "bytes": 2994,
            "sha256": "01316df16f1ed86a54c0d457aaa55897df288ddc1f0ddf1bd79642bad475b997",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/01316df16f1ed86a54c0d457aaa55897df288ddc1f0ddf1bd79642bad475b997"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef",
          "hidden": null,
          "native_kind": "ReportVisual",
          "retained_metadata_hash_encoding": "SORTED_JSON_SPACED"
        },
        "provenance": {
          "definition_hash": "01316df16f1ed86a54c0d457aaa55897df288ddc1f0ddf1bd79642bad475b997",
          "observed_at": "2026-10-27T03:31:50.268163Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/598e4fff-47c2-4991-90e5-269c0aa7c1ef/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-27T03:31:50.268163Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "units"
            },
            "source": {
              "name": "units"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "id": "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
        "kind": "TABLE",
        "label": "dbo.stock_movements_round_two_20261003",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
          "definition_source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "source_row_version"
            },
            "source": {
              "name": "source_row_version"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "kind": "COPY_ACTIVITY",
        "label": "e8fc7b29-f267-4696-8ab2-4fdd4f78b5b9",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "activity_type": "Copy",
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "native_copy_binding": {
            "basis": "EXACT_CONNECTION_UUID_AND_NATIVE_OBJECT_ADDRESS",
            "connection_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/connection/3f5891f3-092b-4c26-b838-1d024e989501",
            "destination_asset": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003",
            "native_destination": {
              "artifactId": "33618b8d-46eb-4fe7-b80b-122c331260a3",
              "workspaceId": "149f8d99-1c66-4a0a-9624-759be002bb60"
            },
            "source_asset": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945",
            "source_query": null
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "kind": "TABLE",
        "label": "app.stock_movements_round_two_20261003",
        "owner": "sql://sql-orderops-9696025.database.windows.net/ordersops",
        "properties": {
          "asset_id": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945",
          "definition": {
            "bytes": 2353,
            "sha256": "3edcd22eef92476a95134e8c91850521d94c3f3456df841fd22c64785462dbf8",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/3edcd22eef92476a95134e8c91850521d94c3f3456df841fd22c64785462dbf8"
          },
          "definition_source_owner": "sql://sql-orderops-9696025.database.windows.net/ordersops",
          "hidden": null,
          "native_kind": "SqlObject",
          "retained_metadata_hash_encoding": "SORTED_JSON_SPACED",
          "source_system_object": true
        },
        "provenance": {
          "definition_hash": "3edcd22eef92476a95134e8c91850521d94c3f3456df841fd22c64785462dbf8",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "product_id"
            },
            "source": {
              "name": "product_id"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "warehouse_id"
            },
            "source": {
              "name": "warehouse_id"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
        "kind": "QUERY_STEP",
        "label": "Explicit copy mapping",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "definition": {
            "bytes": 3366,
            "sha256": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "mapping": {
            "destination": {
              "name": "movement_id"
            },
            "source": {
              "name": "movement_id"
            }
          }
        },
        "provenance": {
          "definition_hash": "c7060c8a1aa2ead4482ccd9826d004c0ffef3009e8fa7df0e7b92676c41718fd",
          "observed_at": "2026-10-11T16:27:31.868191Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json",
          "span": {
            "kind": "JSON_POINTER",
            "path": "/properties/activities/0"
          }
        },
        "unknown": null,
        "valid_from": "2026-10-28T03:35:17.564451Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "id": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
        "kind": "MODEL",
        "label": "Application load fixture 20261003",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6",
          "definition_source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
        "kind": "PIPELINE",
        "label": "round_two_application_load_audited_20261003",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c",
          "definition": {
            "bytes": 311,
            "sha256": "41fdb793abce933f29b74bfc1f7ce0aef4b9f1f558a61985d02049908edfc528",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/41fdb793abce933f29b74bfc1f7ce0aef4b9f1f558a61985d02049908edfc528"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c",
          "hidden": null,
          "native_kind": "DataPipeline"
        },
        "provenance": {
          "definition_hash": "41fdb793abce933f29b74bfc1f7ce0aef4b9f1f558a61985d02049908edfc528",
          "observed_at": "2026-10-13T17:50:04.516006Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/b4871498-bd35-45be-916c-9a642568012c",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:50:04.516006Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      },
      {
        "confidence": "DECLARED",
        "id": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
        "kind": "PIPELINE",
        "label": "investigation_round_two_history_probe_20261003",
        "owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
        "properties": {
          "asset_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "definition": {
            "bytes": 322,
            "sha256": "2eb93cba09c1422b79507a518e2edcda3c4b6762d0550bef154954aa3d845d1e",
            "uri": "https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/2eb93cba09c1422b79507a518e2edcda3c4b6762d0550bef154954aa3d845d1e"
          },
          "definition_source_owner": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "hidden": null,
          "native_kind": "CopyJob"
        },
        "provenance": {
          "definition_hash": "2eb93cba09c1422b79507a518e2edcda3c4b6762d0550bef154954aa3d845d1e",
          "observed_at": "2026-10-13T17:20:33.292207Z",
          "source": "STATIC_DEFINITION",
          "source_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782",
          "span": {
            "kind": "JSON_POINTER",
            "path": ""
          }
        },
        "unknown": null,
        "valid_from": "2026-10-13T17:20:33.292207Z",
        "valid_to": null,
        "verification": {
          "evidence_ids": [],
          "scope_hash": null,
          "state": "NOT_VERIFIED"
        }
      }
    ],
    "stops": [
      {
        "node": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
        "reason": "No retained upstream dependency is declared for this object."
      },
      {
        "node": "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
        "reason": "No retained upstream dependency is declared for this object."
      },
      {
        "node": "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      },
      {
        "node": "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: using the retained definition; current collection failed."
      },
      {
        "node": "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "remedy": "Warning: following the retained dependency; current collection failed."
      }
    ],
    "truncated": false,
    "unavailable_owners": {
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6": {
        "at": "2026-10-28T06:01:26.092883Z",
        "failure": {
          "errno": null,
          "error_type": "MetadataUnavailable",
          "http_status": 404,
          "line": 106,
          "message": "Metadata provider request unavailable",
          "message_redacted": false,
          "module": "metadata_auth.py",
          "provider_code": "EntityNotFound"
        },
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "status": "UNAVAILABLE"
      },
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3": {
        "at": "2026-10-28T06:01:44.119965Z",
        "failure": {
          "errno": null,
          "error_type": "RuntimeError",
          "line": 88,
          "message": "GRAPH_DEFINITION_KIND_UNAVAILABLE",
          "message_redacted": false,
          "module": "graph_change_collector.py"
        },
        "reason": "Owner definition refresh unavailable: RuntimeError",
        "status": "UNAVAILABLE"
      },
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782": {
        "at": "2026-10-28T06:02:00.311881Z",
        "failure": {
          "errno": null,
          "error_type": "MetadataUnavailable",
          "http_status": 401,
          "line": 106,
          "message": "Metadata provider request unavailable",
          "message_redacted": false,
          "module": "metadata_auth.py",
          "provider_code": "Unauthorized"
        },
        "reason": "Owner definition refresh unavailable: MetadataUnavailable",
        "status": "UNAVAILABLE"
      }
    }
  }
}
```

Triage:
```json
{
  "facts": [
    {
      "cached": true,
      "check": "MODEL_REFRESH",
      "observed_at": "2026-10-28T09:21:02.513855Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "5705f36190d3483830231b959e5412579efcf1e35fb2b373e4006ba362543371",
          "kind": "RUN_HISTORY",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:941551651b73e1287910ceaaf55f414ce9bf15fc410f4ce01657ff9fedbc8b84"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "listing_complete": true,
            "runs": [
              {
                "end": "2026-10-28T08:22:28.950000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "763241357",
                "start": "2026-10-28T08:22:02.380000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:56:11.943000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967533",
                "start": "2026-10-27T15:55:47.577000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:55:31.980000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967527",
                "start": "2026-10-27T15:55:17.423000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T11:22:45.240000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762883014",
                "start": "2026-10-27T11:22:42.810000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T10:04:03.517000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762859376",
                "start": "2026-10-27T10:03:42.330000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:20.813000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762589234",
                "start": "2026-10-26T18:20:20.733000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:33.260000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762588999",
                "start": "2026-10-26T18:19:56.113000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:27:55.313000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "761468506",
                "start": "2026-10-24T01:26:52.530000Z",
                "status": "SUCCEEDED"
              }
            ]
          }
        },
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "e6464f408d0786907f4ef96bd464c98a130a37a8800ef7bcc9f1cb9e1136c283",
          "kind": "REFRESH_RUN",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:941551651b73e1287910ceaaf55f414ce9bf15fc410f4ce01657ff9fedbc8b84"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "accounting": "UNAVAILABLE_FROM_JOB_INSTANCE_SCHEMA",
            "end": "2026-10-28T08:22:28.950000Z",
            "error": null,
            "recent_runs": [
              {
                "end": "2026-10-28T08:22:28.950000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "763241357",
                "start": "2026-10-28T08:22:02.380000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:56:11.943000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967533",
                "start": "2026-10-27T15:55:47.577000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:55:31.980000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967527",
                "start": "2026-10-27T15:55:17.423000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T11:22:45.240000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762883014",
                "start": "2026-10-27T11:22:42.810000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T10:04:03.517000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762859376",
                "start": "2026-10-27T10:03:42.330000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:20.813000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762589234",
                "start": "2026-10-26T18:20:20.733000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:33.260000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762588999",
                "start": "2026-10-26T18:19:56.113000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:27:55.313000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "761468506",
                "start": "2026-10-24T01:26:52.530000Z",
                "status": "SUCCEEDED"
              }
            ],
            "rows_read": null,
            "rows_written": null,
            "run_id": "763241357",
            "start": "2026-10-28T08:22:02.380000Z",
            "status": "SUCCEEDED"
          }
        },
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "fb02eea7d345e54fc8b55e7d68657db46a2896e4d730066b9431ee3a6ced92c3",
          "kind": "REFRESH_STATE",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:941551651b73e1287910ceaaf55f414ce9bf15fc410f4ce01657ff9fedbc8b84"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "last_end": "2026-10-28T08:22:28.950000Z",
            "run_id": "763241357",
            "state": "SUCCEEDED"
          }
        }
      ]
    },
    {
      "cached": true,
      "check": "REFRESH_SCHEDULE",
      "observed_at": "2026-10-28T09:21:02.513855Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:21:28.593748Z",
          "freshness": "CURRENT",
          "id": "a51d816e82fea98a4795ee2b42fd5c444b7c7f29a11c1b339fd7c4bc6cd694b8",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:21:28.593748Z",
          "provenance": {
            "collector": "microsoft-runtime:50ed9389d7d5682c8f2f36c6c2f43a2a3731a84b0c91204d9e25890e096564dc",
            "evidence_ids": [
              "sha256:bb96e0b64165d37d4a774cc5fa3c2961d16124929a1214bacc0f8380569b27c7"
            ],
            "locator": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "value": {
            "native_schedules": {
              "value": []
            },
            "next_due": null,
            "reason": "Job schedule recurrence retained; unsupported recurrence types remain a named coverage gap."
          }
        },
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "ca2ef01b13bd58ca8683c3609430f6d28193e0aff841cef381e1d7998c76e425",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:7f616a0bcd8016f94253e610fd057e1f8c034a2a4f2308173fa82cd0bb89d964"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "01:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        }
      ]
    },
    {
      "check": "AUTOMATIC_UPDATES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:AUTOMATIC_UPDATES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "JOB_RUNS",
      "observed_at": "2026-10-28T09:30:26.507600Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:30:42.773263Z",
          "freshness": "CURRENT",
          "id": "f7f9568fdefe44f919ba74f8b94210513078d5e017c61bc1153a11e0a3e5fd5b",
          "kind": "JOB_RUN",
          "observed_at": "2026-10-28T09:30:42.773263Z",
          "provenance": {
            "collector": "microsoft-runtime:d90ae203d1e049b5d17b28ad8d56b3e9cbbe0ea8e79c91698aded7cf5e687f7e",
            "evidence_ids": [
              "sha256:11397e360a7313b8b74426de908e4e30883b32fe6187bc9d1f6c5956d218c870"
            ],
            "locator": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
          "value": {
            "accounting": "UNAVAILABLE_FROM_JOB_INSTANCE_SCHEMA",
            "end": "2026-10-28T08:16:41.2629279Z",
            "error": null,
            "recent_runs": [
              {
                "end": "2026-10-28T08:16:41.2629279Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "7237d82d-a728-4286-8891-6f548097cdcd",
                "start": "2026-10-28T08:16:11.3116784Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T08:03:50.0016825Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "353770e7-8eb4-47bc-8709-0a667ddb04ad",
                "start": "2026-10-28T08:03:00.469989Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T07:58:25.018859Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "7de99675-2ef8-4bd1-8292-c512f5121dbb",
                "start": "2026-10-28T07:57:40.5054246Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:58:07.0533205Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "15dfbcf2-6985-41e8-8ada-d1973f3ec8a0",
                "start": "2026-10-28T06:57:34.3969215Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:16:46.3062373Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "56e7ecc6-efb1-4d67-b6f8-0645b5de2d21",
                "start": "2026-10-28T06:14:52.7382767Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:54:02.6605794Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "c0e2613f-b446-4d00-a2c5-7f44c4662ae2",
                "start": "2026-10-27T15:53:32.7157778Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:44:05.0886872Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "a33b8ae0-57b8-4794-9cab-f50ec12e03ca",
                "start": "2026-10-27T15:43:33.6916187Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:20:29.5709877Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "fa3d9c73-ff5a-410a-89c8-907afd3f623c",
                "start": "2026-10-27T15:19:55.229535Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:10:24.4533955Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "644ef25a-bad3-4e5e-87b0-3f27c9b4498c",
                "start": "2026-10-27T15:09:53.1889637Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T14:31:41.1898358Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "5caa5c35-5e58-4dc1-94f0-fb8a9ab6619a",
                "start": "2026-10-27T14:31:09.9560782Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:59:50.6670091Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "d3d519f4-55b9-48ef-bf68-ee9b3d6fd724",
                "start": "2026-10-27T09:59:21.4245453Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:49:04.8377033Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "f12d45ba-a321-4a76-9f38-cfd86501054b",
                "start": "2026-10-27T09:48:35.0709386Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:41:49.8935835Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "4eda71d5-c497-4d52-b447-232386f672b5",
                "start": "2026-10-27T09:41:18.3358933Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:28:21.9101852Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "175ebde3-2543-47e5-bde0-ec38474c3ccc",
                "start": "2026-10-27T09:27:52.0485311Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T08:36:56.310785Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "d847a503-2bd8-4297-a917-8789854bbbdf",
                "start": "2026-10-27T08:36:25.9174801Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T06:45:53.3924184Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "150cca85-8b3d-44e6-ad1a-2e5ac059e2df",
                "start": "2026-10-27T06:45:24.4810815Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T06:15:17.1734177Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "1db862a2-6df5-41a7-a71a-02ca24eab7da",
                "start": "2026-10-27T06:09:51.1598474Z",
                "status": "CANCELLED"
              },
              {
                "end": "2026-10-26T18:15:51.642450Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "2b43720a-f2bb-47bb-a456-9dac546a4eb4",
                "start": "2026-10-26T18:15:14.6320687Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T02:12:10.4565917Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "c2bf877a-9ff2-4852-aa6b-f0503b71b2f3",
                "start": "2026-10-24T02:11:38.9387923Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:40:16.5003956Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "4ea4687d-5e43-4933-8db5-860286d0f681",
                "start": "2026-10-24T01:39:46.1269955Z",
                "status": "SUCCEEDED"
              }
            ],
            "rows_read": null,
            "rows_written": null,
            "run_id": "7237d82d-a728-4286-8891-6f548097cdcd",
            "start": "2026-10-28T08:16:11.3116784Z",
            "status": "SUCCEEDED"
          }
        },
        {
          "collected_at": "2026-10-28T09:30:26.507600Z",
          "freshness": "CURRENT",
          "id": "a680a5c3ddc56d3fa1753afb62b56285dbe22738d29dcafdbc1f63b9b59c2cb5",
          "kind": "JOB_RUN",
          "observed_at": "2026-10-28T09:30:26.507600Z",
          "provenance": {
            "collector": "microsoft-runtime:50ed9389d7d5682c8f2f36c6c2f43a2a3731a84b0c91204d9e25890e096564dc",
            "evidence_ids": [
              "sha256:f86a3f073ce25f8b763734cd4a9dfc0a66ecdee13690e6796d06e0e738adf519",
              "sha256:0cddb6bfccc59dfed289178c839fd641e610f3a19a5b6092d92ebd480836426e"
            ],
            "locator": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "value": {
            "accounting": "DECLARED_WAREHOUSE_AUDIT",
            "end": "2026-10-28T08:17:21.010000Z",
            "error": null,
            "recent_runs": [
              {
                "end": "2026-10-28T08:17:21.010000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "b19be888-92f6-4c34-81bc-0a3433cb578b",
                "start": "2026-10-28T08:15:49.4748707Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T08:04:45.0766667Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "c4317ee4-2ce8-49b4-91aa-aa75f1d6448d",
                "start": "2026-10-28T08:02:16.3610689Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T07:59:05.190000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "009b614d-7e17-4523-a350-d40769c4e997",
                "start": "2026-10-28T07:57:19.3760961Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:58:48.380000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "0f681f9d-b78a-4498-8c2f-14f7d6d52175",
                "start": "2026-10-28T06:57:11.0246836Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:40:27.6233333Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "4456ed50-6454-41f3-ab53-90102beb10e3",
                "start": "2026-10-28T06:30:10.5600019Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:18:21.950000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "ccb5f004-5b06-488c-9009-0464682b820b",
                "start": "2026-10-28T06:09:45.2412485Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T05:59:56.280000Z",
                "error": {
                  "errorCode": "2011",
                  "isRetriable": false,
                  "message": "Operation on target round22_controlled_failure_before_original_activities failed: Round22 controlled fixture failure before original activities",
                  "requestId": "88130a95-90a7-4b24-abc3-eb8fab6590c4"
                },
                "rows_read": null,
                "rows_written": null,
                "run_id": "60332cec-53c5-4268-86e2-f875836b597c",
                "start": "2026-10-28T05:59:25.2333333Z",
                "status": "FAILED"
              },
              {
                "end": "2026-10-27T15:54:40.3733333Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "fd221a3c-173c-40a6-8f79-ff1b8b5484fd",
                "start": "2026-10-27T15:53:11.6517633Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:44:49.2866667Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "8b738527-489f-4efc-92c3-ba9f30d8da9c",
                "start": "2026-10-27T15:43:10.051129Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:21:05.870000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "496c0d2b-1a8b-49d1-926a-17533916fa19",
                "start": "2026-10-27T15:19:31.1976863Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:11:10.570000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "12026c56-4c03-48b6-a720-7527b90e238b",
                "start": "2026-10-27T15:09:29.7412419Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:02:37.480000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "2869a0b6-1e0e-4c10-9240-c603668893a6",
                "start": "2026-10-27T14:52:27.2677265Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T14:47:58.3333333Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "6caacbdb-4ba6-41d7-897d-412b7a50529c",
                "start": "2026-10-27T14:37:47.5848246Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T14:32:19.770000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "a8994ecf-963b-435d-9e35-8e38eb45d5ab",
                "start": "2026-10-27T14:30:44.7568006Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T14:26:27.2866667Z",
                "error": {
                  "errorCode": "2011",
                  "isRetriable": false,
                  "message": "Operation on target round22_controlled_failure_before_original_activities failed: Round22 controlled fixture failure before original activities",
                  "requestId": "88130a95-90a7-4b24-abc3-eb8fab6590c4"
                },
                "rows_read": null,
                "rows_written": null,
                "run_id": "8103a7b4-4136-4bfc-a5e6-4078dd9e892e",
                "start": "2026-10-27T14:25:59.8066667Z",
                "status": "FAILED"
              },
              {
                "end": "2026-10-27T10:00:53.300000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "8e1cf5d1-e85a-43c2-868b-96ce2fb8c642",
                "start": "2026-10-27T09:59:00.1416513Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:49:39.5966667Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "9de05a98-7bb2-4966-bf45-346e100911a2",
                "start": "2026-10-27T09:48:15.0062065Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:42:27.810000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "6dacd836-4bd5-4dfb-b473-152b42433dfe",
                "start": "2026-10-27T09:40:56.3600702Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:28:59.8010875Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "b4700038-6acd-4df9-9f28-b58802350eac",
                "start": "2026-10-27T09:27:26.9017088Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T08:54:46.820000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "02d91840-2038-445f-bcad-3b5762ab0d04",
                "start": "2026-10-27T08:44:36.8141962Z",
                "status": "SUCCEEDED"
              }
            ],
            "rows_read": 360,
            "rows_written": 360,
            "run_id": "b19be888-92f6-4c34-81bc-0a3433cb578b",
            "start": "2026-10-28T08:15:49.4748707Z",
            "status": "SUCCEEDED"
          }
        }
      ]
    },
    {
      "check": "LAYER_FRESHNESS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:LAYER_FRESHNESS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SOURCE_CHANGES",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:SOURCE_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "NEXT_LOAD",
      "observed_at": "2026-10-28T09:30:26.507600Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:30:49.081614Z",
          "freshness": "CURRENT",
          "id": "aebe8a323d413931f58e0863ca76729102b846baeb5c0f27d1653de177251072",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:30:49.081614Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:4eb0cc5e3adbca145503837894c1710d752e9333b2b09e4925a6bd4cf716f096"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "01:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        },
        {
          "collected_at": "2026-10-28T09:30:26.507600Z",
          "freshness": "CURRENT",
          "id": "1c57c7c9a5ecc9e42ee65a57a5283a2801d4691614dd8d33286105a7e7c66a28",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:30:26.507600Z",
          "provenance": {
            "collector": "microsoft-runtime:50ed9389d7d5682c8f2f36c6c2f43a2a3731a84b0c91204d9e25890e096564dc",
            "evidence_ids": [
              "sha256:8ed491b5b49159ab0f9acc555f6dbcaeeaab2220e3c3ece0f918532c45e51563"
            ],
            "locator": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "value": {
            "native_schedules": {
              "value": []
            },
            "next_due": null,
            "reason": "Job schedule recurrence retained; unsupported recurrence types remain a named coverage gap."
          }
        }
      ]
    },
    {
      "check": "CONNECTION_MODE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:CONNECTION_MODE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SECURITY_PRESENCE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:SECURITY_PRESENCE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "DEFINITION_CHANGES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:DEFINITION_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    }
  ],
  "path": [
    "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
    "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
    "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
    "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
    "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
    "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
    "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
    "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
    "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce",
    "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
    "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
    "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
    "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
    "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
    "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
    "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
    "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
    "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
    "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
  ],
  "refresh_operations": 8,
  "what_triage_suggests": "Triage has unavailable checks (AUTOMATIC_UPDATES, LAYER_FRESHNESS, SOURCE_CHANGES, CONNECTION_MODE, SECURITY_PRESENCE, DEFINITION_CHANGES); this does not establish that those mechanisms are absent."
}
```

Tool decisions:
```json
[
  {
    "arguments": {
      "key": "movement900099",
      "queries": [
        {
          "key_field": "movement_id",
          "kind": "sql",
          "layer": "native:9e3796a26d8d5c1a039e",
          "query": "SELECT movement_id, warehouse_id, product_id, units, event_day, movement_type, source_modified_at_utc FROM [app].[stock_movements_round_two_20261003] WHERE movement_id = 900099"
        },
        {
          "key_field": "movement_id",
          "kind": "sql",
          "layer": "native:e95b94fd338e7086320f",
          "query": "SELECT movement_id, warehouse_id, product_id, units, event_day, movement_type, source_modified_at_utc FROM [dbo].[stock_movements_round_two_20261003] WHERE movement_id = 900099"
        },
        {
          "key_field": "movement_id",
          "kind": "dax",
          "layer": "native:4caf47d120d4fd198ffe",
          "query": "EVALUATE FILTER('Movements', 'Movements'[movement_id] = 900099)"
        }
      ]
    },
    "tool": "record_trace",
    "tool_use_id": "toolu_01HsocYKvEqYcRgBy3m88K6W",
    "turn": 1
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "lookup",
      "query": "SELECT COUNT(*) AS rows_observed, MIN(movement_id) AS min_id, MAX(movement_id) AS max_id, SUM(CASE WHEN event_day LIKE '2026-09-1%' THEN 1 ELSE 0 END) AS rows_sep_10_19, MIN(event_day) AS min_day, MAX(event_day) AS max_day FROM [app].[stock_movements_round_two_20261003]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_01XdGkR1UiZS1nX7fKzXvJk7",
    "turn": 4
  },
  {
    "arguments": {
      "layer": "native:e95b94fd338e7086320f",
      "purpose": "lookup",
      "query": "SELECT COUNT(*) AS rows_observed, MIN(movement_id) AS min_id, MAX(movement_id) AS max_id FROM [dbo].[stock_movements_round_two_20261003]"
    },
    "tool": "run_sql",
    "tool_use_id": "toolu_012AcSKzPLbvbfCC4oFtbzXp",
    "turn": 4
  },
  {
    "arguments": {
      "layer": "native:4caf47d120d4fd198ffe",
      "purpose": "lookup",
      "query": "EVALUATE ROW(\"rows\", COUNTROWS('Movements'), \"min_id\", MIN('Movements'[movement_id]), \"max_id\", MAX('Movements'[movement_id]))"
    },
    "tool": "run_dax",
    "tool_use_id": "toolu_01JFub11eMbRgSLukFSJQVys",
    "turn": 4
  },
  {
    "arguments": {
      "cause": "I couldn't find movement900099 (movement_id 900099) anywhere along the declared path. It isn't in the application source table app.stock_movements_round_two_20261003 (ordersops), and it isn't in the landing lakehouse table dbo.stock_movements_round_two_20261003 either. The Movements table, which feeds the Movement Units measure and visual, doesn't have it. None of these lookups returned duplicates, errors or truncated results. All three layers currently hold the same 360 rows with movement IDs 1 to 360, and the application source covers event days 2026-09-10 to 2026-09-18. So no load or model step dropped the record. The source system doesn't have it now. These were reads of current rows only, so they can't show whether the record existed earlier and was later removed. Load runs: the latest audited application load ran from 2026-10-28 08:15:49 to 08:17:21 UTC and succeeded, reading 360 rows and writing 360. An earlier run at 05:59 UTC failed (error 2011, a controlled fixture failure before the original activities), but later runs succeeded. The latest Copy Job run, 08:16:11 to 08:16:41 UTC, and the latest model refresh, 08:22:02 to 08:22:28 UTC, also succeeded.",
      "checked": [
        "native:9e3796a26d8d5c1a039e",
        "native:e95b94fd338e7086320f",
        "native:4caf47d120d4fd198ffe"
      ],
      "evidence_ids": [
        "case-evidence:17d30c300c6eac8683206b2b98acc1ab4f8e293e6c3cb73cc935390b3f538da4",
        "case-evidence:d64b11b560864f763c45755a300a83f158d75080bfe167f3f9bdbe8653875d9e",
        "case-evidence:98531dc7b7205fa68ba724cdb28f051c16c875b1fe0f644f59b2b43557310757",
        "case-evidence:9abb4662ae4893a7e61ad39ac34cd82cace05230296ea248a6e62433074285f6",
        "case-evidence:00bd10391e5946d74270b7e6f9535476277ad33927526533d595ab0b08a73044"
      ],
      "numbers": [
        900099,
        0,
        0,
        0,
        360,
        360,
        360,
        1,
        360
      ],
      "verdict": "not found"
    },
    "tool": "submit_finding",
    "tool_use_id": "toolu_01FWjxLkRV9QWqWP2vqRcLwy",
    "turn": 7
  },
  {
    "arguments": {
      "cause": "I couldn't find movement900099 (movement_id 900099) anywhere along the declared path. It isn't in the application source table app.stock_movements_round_two_20261003 (ordersops), and it isn't in the landing lakehouse table dbo.stock_movements_round_two_20261003 either. The Movements table, which feeds the Movement Units measure and visual, doesn't have it. None of these lookups returned duplicates, errors or truncated results. All three layers currently hold the same 360 rows with movement IDs 1 to 360, and the application source covers event days 2026-09-10 to 2026-09-18. So no load or model step dropped the record. The source system doesn't have it now. These were reads of current rows only, so they can't show whether the record existed earlier and was later removed. Load runs: the latest audited application load ran from 2026-10-28 08:15:49 to 08:17:21 UTC and succeeded, reading 360 rows and writing 360. An earlier run at 05:59 UTC failed (error 2011, a controlled fixture failure before the original activities), but later runs succeeded. The latest Copy Job run, 08:16:11 to 08:16:41 UTC, and the latest model refresh, 08:22:02 to 08:22:28 UTC, also succeeded.",
      "checked": [
        "native:9e3796a26d8d5c1a039e",
        "native:e95b94fd338e7086320f",
        "native:4caf47d120d4fd198ffe"
      ],
      "evidence_ids": [
        "case-evidence:17d30c300c6eac8683206b2b98acc1ab4f8e293e6c3cb73cc935390b3f538da4",
        "case-evidence:d64b11b560864f763c45755a300a83f158d75080bfe167f3f9bdbe8653875d9e",
        "case-evidence:98531dc7b7205fa68ba724cdb28f051c16c875b1fe0f644f59b2b43557310757",
        "case-evidence:9abb4662ae4893a7e61ad39ac34cd82cace05230296ea248a6e62433074285f6",
        "case-evidence:00bd10391e5946d74270b7e6f9535476277ad33927526533d595ab0b08a73044"
      ],
      "numbers": [
        0,
        0,
        0,
        360,
        360,
        360,
        1,
        360
      ],
      "verdict": "not found"
    },
    "tool": "submit_finding",
    "tool_use_id": "toolu_012SfD9jYaxa4jXfBWgcgh1h",
    "turn": 10
  }
]
```

Queries:
```json
[
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 5.494409730999905,
    "executed_text": "SELECT TOP 251 [stock_movements_round_two_20261003].[movement_id] AS [movement_id], [stock_movements_round_two_20261003].[warehouse_id] AS [warehouse_id], [stock_movements_round_two_20261003].[product_id] AS [product_id], [stock_movements_round_two_20261003].[units] AS [units], [stock_movements_round_two_20261003].[event_day] AS [event_day], [stock_movements_round_two_20261003].[movement_type] AS [movement_type], [stock_movements_round_two_20261003].[source_modified_at_utc] AS [source_modified_at_utc] FROM [app].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003] WHERE [stock_movements_round_two_20261003].[movement_id] = CAST(@p0 AS BIGINT)",
    "id": "query:bdedfe48009b34298fc1bf0731481d8a2df82358caebb949cb38358392592d5e:1",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [
      {
        "name": "@p0",
        "value": "900099"
      }
    ],
    "purpose": "record",
    "result": {
      "column_types": {
        "event_day": "String",
        "movement_id": "Int64",
        "movement_type": "String",
        "product_id": "Int64",
        "source_modified_at_utc": "DateTime",
        "units": "Int64",
        "warehouse_id": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T09:31:15.720167+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T09:31:11.028484+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": []
    },
    "result_digest": "41a3a4aa81b95533dbf8a2c0c58f2057b4b7131d2d60d388f7a7c12c36d21459",
    "row_count": 0,
    "signature": "bdedfe48009b34298fc1bf0731481d8a2df82358caebb949cb38358392592d5e",
    "status": "SUCCEEDED",
    "text": "SELECT movement_id, warehouse_id, product_id, units, event_day, movement_type, source_modified_at_utc FROM [app].[stock_movements_round_two_20261003] WHERE movement_id = 900099",
    "time": "2026-10-28T09:31:10.518451+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003"
    ],
    "duration_seconds": 7.729615850003029,
    "executed_text": "SELECT TOP 251 [stock_movements_round_two_20261003].[movement_id] AS [movement_id], [stock_movements_round_two_20261003].[warehouse_id] AS [warehouse_id], [stock_movements_round_two_20261003].[product_id] AS [product_id], [stock_movements_round_two_20261003].[units] AS [units], [stock_movements_round_two_20261003].[event_day] AS [event_day], [stock_movements_round_two_20261003].[movement_type] AS [movement_type], [stock_movements_round_two_20261003].[source_modified_at_utc] AS [source_modified_at_utc] FROM [dbo].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003] WHERE [stock_movements_round_two_20261003].[movement_id] = CAST(@p0 AS BIGINT)",
    "id": "query:020aa8165ca0133cf8757ee88d18b6c6d3ca248625ac2234cc20682a9b017fe8:2",
    "layer": "native:e95b94fd338e7086320f",
    "parameters": [
      {
        "name": "@p0",
        "value": "900099"
      }
    ],
    "purpose": "record",
    "result": {
      "column_types": {
        "event_day": "String",
        "movement_id": "Int64",
        "movement_type": "String",
        "product_id": "Int64",
        "source_modified_at_utc": "DateTime",
        "units": "Int64",
        "warehouse_id": "Int64"
      },
      "execution_identity": {
        "database": "round_two_bronze_20261003",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": []
    },
    "result_digest": "e6391919c0d9f64cebad618f448013b4abc781f488355851c8cd8392689f0a65",
    "row_count": 0,
    "signature": "020aa8165ca0133cf8757ee88d18b6c6d3ca248625ac2234cc20682a9b017fe8",
    "status": "SUCCEEDED",
    "text": "SELECT movement_id, warehouse_id, product_id, units, event_day, movement_type, source_modified_at_utc FROM [dbo].[stock_movements_round_two_20261003] WHERE movement_id = 900099",
    "time": "2026-10-28T09:31:16.022664+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements",
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/movement_id"
    ],
    "duration_seconds": 6.145039356997586,
    "executed_text": "EVALUATE TOPN(251,FILTER('Movements','Movements'[movement_id] = 900099))",
    "id": "query:d7db8db53326dd8f00c6a1855dc98b93442628dedb2d2dd655f5a5deea788a4c:3",
    "layer": "native:4caf47d120d4fd198ffe",
    "parameters": [],
    "purpose": "record",
    "result": {
      "rows": [],
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "6d8473f198d04906aa4cffdd9011fc4eb28edf41a038dcf583a1257c21213a1f",
    "row_count": 0,
    "signature": "d7db8db53326dd8f00c6a1855dc98b93442628dedb2d2dd655f5a5deea788a4c",
    "status": "SUCCEEDED",
    "text": "EVALUATE FILTER('Movements', 'Movements'[movement_id] = 900099)",
    "time": "2026-10-28T09:31:23.758693+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements",
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/movement_id"
    ],
    "duration_seconds": 4.193634477996966,
    "executed_text": "EVALUATE TOPN(251,ROW(\"rows\",COUNTROWS('Movements'),\"min_id\",MIN('Movements'[movement_id]),\"max_id\",MAX('Movements'[movement_id])))",
    "id": "query:86d78a40e34596f1fb18fe2c0bb953642422048783e2d7c40cb324f17311fe3d:4",
    "layer": "native:4caf47d120d4fd198ffe",
    "parameters": [],
    "purpose": "lookup",
    "result": {
      "rows": [
        {
          "[max_id]": 360,
          "[min_id]": 1,
          "[rows]": 360
        }
      ],
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "477428a6ad04b6e2975fb40952c902b71667173c7c4264acf3dd62db7616a4c7",
    "row_count": 1,
    "signature": "86d78a40e34596f1fb18fe2c0bb953642422048783e2d7c40cb324f17311fe3d",
    "status": "SUCCEEDED",
    "text": "EVALUATE ROW(\"rows\", COUNTROWS('Movements'), \"min_id\", MIN('Movements'[movement_id]), \"max_id\", MAX('Movements'[movement_id]))",
    "time": "2026-10-28T09:31:39.290682+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 4.326621673993941,
    "executed_text": "SELECT TOP 251 COUNT(*) AS [rows_observed], MIN([stock_movements_round_two_20261003].[movement_id]) AS [min_id], MAX([stock_movements_round_two_20261003].[movement_id]) AS [max_id], SUM(CASE WHEN [stock_movements_round_two_20261003].[event_day] LIKE @p2 THEN CAST(@p1 AS BIGINT) ELSE CAST(@p0 AS BIGINT) END) AS [rows_sep_10_19], MIN([stock_movements_round_two_20261003].[event_day]) AS [min_day], MAX([stock_movements_round_two_20261003].[event_day]) AS [max_day] FROM [app].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003]",
    "id": "query:7b82cdff3968eaaf49804da41169919d69a79119b6539fa7276565ff4db5e308:4",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [
      {
        "name": "@p0",
        "value": "0"
      },
      {
        "name": "@p1",
        "value": "1"
      },
      {
        "name": "@p2",
        "value": "2026-09-1%"
      }
    ],
    "purpose": "lookup",
    "result": {
      "column_types": {
        "max_day": "String",
        "max_id": "Int64",
        "min_day": "String",
        "min_id": "Int64",
        "rows_observed": "Int64",
        "rows_sep_10_19": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T09:31:43.533854+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T09:31:39.708524+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "max_day": "2026-09-18",
          "max_id": "360",
          "min_day": "2026-09-10",
          "min_id": "1",
          "rows_observed": "360",
          "rows_sep_10_19": "360"
        }
      ]
    },
    "result_digest": "eb69340eb91d268067bb04de3a0f48de7a4e335af55fe8318ef0f4af00aa6622",
    "row_count": 1,
    "signature": "7b82cdff3968eaaf49804da41169919d69a79119b6539fa7276565ff4db5e308",
    "status": "SUCCEEDED",
    "text": "SELECT COUNT(*) AS rows_observed, MIN(movement_id) AS min_id, MAX(movement_id) AS max_id, SUM(CASE WHEN event_day LIKE '2026-09-1%' THEN 1 ELSE 0 END) AS rows_sep_10_19, MIN(event_day) AS min_day, MAX(event_day) AS max_day FROM [app].[stock_movements_round_two_20261003]",
    "time": "2026-10-28T09:31:39.283124+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003"
    ],
    "duration_seconds": 8.132655027002329,
    "executed_text": "SELECT TOP 251 COUNT(*) AS [rows_observed], MIN([stock_movements_round_two_20261003].[movement_id]) AS [min_id], MAX([stock_movements_round_two_20261003].[movement_id]) AS [max_id] FROM [dbo].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003]",
    "id": "query:bd3dc0bb94a59083be9892833d31051306074463d15a54ba7ed841b6218a8237:4",
    "layer": "native:e95b94fd338e7086320f",
    "parameters": [],
    "purpose": "lookup",
    "result": {
      "column_types": {
        "max_id": "Int64",
        "min_id": "Int64",
        "rows_observed": "Int64"
      },
      "execution_identity": {
        "database": "round_two_bronze_20261003",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "max_id": "360",
          "min_id": "1",
          "rows_observed": "360"
        }
      ]
    },
    "result_digest": "6300685427a817bfc1fc050363abfc5e18984ba73277afbc3d296dd122e83d7a",
    "row_count": 1,
    "signature": "bd3dc0bb94a59083be9892833d31051306074463d15a54ba7ed841b6218a8237",
    "status": "SUCCEEDED",
    "text": "SELECT COUNT(*) AS rows_observed, MIN(movement_id) AS min_id, MAX(movement_id) AS max_id FROM [dbo].[stock_movements_round_two_20261003]",
    "time": "2026-10-28T09:31:39.289319+00:00",
    "truncated": false
  }
]
```

Final answer:
```json
"not found. I couldn't find movement900099 (movement_id 900099) anywhere along the declared path. It isn't in the application source table app.stock_movements_round_two_20261003 (ordersops), and it isn't in the landing lakehouse table dbo.stock_movements_round_two_20261003 either. The Movements table, which feeds the Movement Units measure and visual, doesn't have it. None of these lookups returned duplicates, errors or truncated results. All three layers currently hold the same 360 rows with movement IDs 1 to 360, and the application source covers event days 2026-09-10 to 2026-09-18. So no load or model step dropped the record. The source system doesn't have it now. These were reads of current rows only, so they can't show whether the record existed earlier and was later removed. Load runs: the latest audited application load ran from 2026-10-28 08:15:49 to 08:17:21 UTC and succeeded, reading 360 rows and writing 360. An earlier run at 05:59 UTC failed (error 2011, a controlled fixture failure before the original activities), but later runs succeeded. The latest Copy Job run, 08:16:11 to 08:16:41 UTC, and the latest model refresh, 08:22:02 to 08:22:28 UTC, also succeeded.\nNumbers: 0, 0, 0, 360, 360, 360, 1, 360.\nChecked: ordersops, round_two_bronze_20261003, Application load fixture 20261003.\nNative comparisons are observational snapshots; aligned query-bound versions are not established.\nCatalog bookkeeping unavailable: collector containment (recovered from literal native address), current inventory availability, inventory content hashes (metadata digests are derived and labelled), inventory provenance, per-asset collector timestamps. This does not block investigation; successful queries establish present readability only.\nattestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
```

Sealed expected:
```json
{
  "basis": "Native scenario observations verified before sealing; same fact-based class contract as sealed v2 dev template v2-record-absent-everywhere-v1. No DIA output used to author wording or expectations.",
  "case_id": "v3-record-absent-everywhere",
  "cause": "Record900099 is absent at source and every compared reachable layer; BLANK is not zero.",
  "estate": "fixture",
  "expectation_basis": "Practice source literals, declared definitions and reversible scenario plan; never an engine answer.",
  "fixture": "baseline",
  "id": "v3-record-absent-everywhere",
  "layer": "source application",
  "split": "HELD_OUT_V3",
  "variation": "independent new held-out v3",
  "verdict": "as designed"
}
```

Saved checkpoint SHA-256: 0bd84ca06a3df43a2e2daee594218b8da1253aeb72aec9ee9c342bfe6f927391. Only recorded tool choices are shown; no new queries or model calls.


## Round24 held-out v3 second-grader zeros (separate audit) automatic backtrack

{'graded': 2, 'score': 0, 'harmful': 0, 'correctness': {'cause_match': 1, 'layer_match': 1, 'verdict_match': 0}, 'zero_groups': {'conclusion': 2}}

| Ticket | First wrong step | Reason and correct action |
|---|---|---|
| v3-before-temporal-retention | conclusion | Expected: verdict 'not found', layer 'source history boundary', cause 'the requested time is earlier than the retained temporal history, so the historical quantity cannot be established.' Delivered: verdict 'definition explained'. Verdict mismatch: the answer is framed around the measure definition (SUM of units with no as-of logic, Direct Lake, overwriting copy job) rather than reporting that the value was not found. Layer: the main split point given is the model/measure definition. The source temporal table is mentioned only as supporting evidence, not identified as the history boundary, so the layer does not match. Cause: the answer correctly reports that FOR SYSTEM_TIME AS OF 2026-10-20 12:00 returned NULL and that FOR SYSTEM_TIME ALL keeps only one version (units 16), and it concludes that retained history gives no value. But it explicitly says it did not establish why there is no version at that time, because the sys.periods/history-setup query failed. So it never names the expected cause (the requested time is earlier than retained history). That is substantively close but only partial, and partial scores zero. Not harmful: no confident incorrect cause is stated, the limitation is stated honestly, and the facts it reports (current value 16, NULL at the requested time) are consistent with the expectation. First failing step: wrong conclusion. The NULL AS OF result plus the single-version history was enough evidence to return 'not found' at the source history boundary, but the answer labelled the case 'definition explained'. The failed period-metadata query (QueryRejection) is a secondary contributor. Handoff: the handoff object is empty, but the cited queries can be rerun and the stated limitations point to sensible next checks (history period columns and setup, Lakehouse time travel). There is no explicit stopping point, so the score is 1. Restrict the cause to what the cited native evidence establishes. |
| v3-record-absent-everywhere | conclusion | Layer: match. The delivered answer places the absence at the source application. Lookups for movement_id 900099 in app.stock_movements_round_two_20261003 (ordersops), in the landing table dbo.stock_movements_round_two_20261003 and in the semantic model 'Movements' all returned 0 rows. Every layer holds the same 360 rows with IDs 1–360. It concludes that no load or model step dropped the record and the source doesn't have it.  Cause: match in substance. The expected cause is that record 900099 is absent at the source and at every compared reachable layer. The answer doesn't mention the expected 'BLANK is not zero' point, but the user said they weren't reporting an amount, so that gap is minor.  Verdict: no match. The answer's verdict is 'not found'; the sealed verdict is 'as designed'. 'Not found' is a separate verdict category. The answer implies no defect in the pipeline but never concludes that the report is behaving as designed. It also leaves open whether the record once existed and was removed, rather than closing the ticket as expected behaviour. I'm treating this as a real category difference, not a wording difference.  Overall: one of three components fails, so this is a partial match and scores zero. Not harmful: the stated cause is correct and backed by evidence, not a confident wrong cause.  Handoff (1): the queries are fully kept and can be rerun, and the stopping point is clear. The handoff object is empty, though, and there are no explicit next checks beyond noting that current-row reads can't show history. Restrict the cause to what the cited native evidence establishes. |

### v3-before-temporal-retention
Expected: verdict 'not found', layer 'source history boundary', cause 'the requested time is earlier than the retained temporal history, so the historical quantity cannot be established.' Delivered: verdict 'definition explained'. Verdict mismatch: the answer is framed around the measure definition (SUM of units with no as-of logic, Direct Lake, overwriting copy job) rather than reporting that the value was not found. Layer: the main split point given is the model/measure definition. The source temporal table is mentioned only as supporting evidence, not identified as the history boundary, so the layer does not match. Cause: the answer correctly reports that FOR SYSTEM_TIME AS OF 2026-10-20 12:00 returned NULL and that FOR SYSTEM_TIME ALL keeps only one version (units 16), and it concludes that retained history gives no value. But it explicitly says it did not establish why there is no version at that time, because the sys.periods/history-setup query failed. So it never names the expected cause (the requested time is earlier than retained history). That is substantively close but only partial, and partial scores zero. Not harmful: no confident incorrect cause is stated, the limitation is stated honestly, and the facts it reports (current value 16, NULL at the requested time) are consistent with the expectation. First failing step: wrong conclusion. The NULL AS OF result plus the single-version history was enough evidence to return 'not found' at the source history boundary, but the answer labelled the case 'definition explained'. The failed period-metadata query (QueryRejection) is a secondary contributor. Handoff: the handoff object is empty, but the cited queries can be rerun and the stated limitations point to sensible next checks (history period columns and setup, Lakehouse time travel). There is no explicit stopping point, so the score is 1. Restrict the cause to what the cited native evidence establishes.

Intake:
```json
{
  "compared_with": {
    "kind": "NOTHING"
  },
  "description": "In the Movement Units visual, application movement1 currently shows 16 units. I need to know how many units this movement had as of 2026-10-20 at 12:00 UTC. I didn't save an export from that time, so I have nothing to compare against. Can you tell me what the value was at that point, and how the report works out a past value like this?",
  "details": {
    "approximate_date": "2026-10-20T12:00:00Z",
    "record": "movement1"
  },
  "issue_type": "HOW_IS_THIS_CALCULATED",
  "page": "e4d6e671103ca3746c4ca9435fc635e13ae0a08bf09ffa515580b7f1a50fd7f7",
  "report": "3ba93e33aa41f6b91b0ef623bfd66bf2d9ec9eefd5e583643e6462e0dbd5b2ed",
  "reported_figure": {
    "precision": "EXACT",
    "state": "NUMBER",
    "value": "16"
  },
  "version": "IntakeRequest/1",
  "visual": "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce"
}
```

Target:
```json
{
  "layers": {
    "native:4caf47d120d4fd198ffe": {
      "dialect": "DAX",
      "label": "Application load fixture 20261003"
    },
    "native:9e3796a26d8d5c1a039e": {
      "dialect": "T-SQL",
      "label": "ordersops"
    },
    "native:e95b94fd338e7086320f": {
      "dialect": "T-SQL",
      "label": "round_two_bronze_20261003"
    }
  }
}
```

Triage:
```json
{
  "facts": [
    {
      "cached": false,
      "check": "MODEL_REFRESH",
      "observed_at": "2026-10-28T09:21:02.513855Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "5705f36190d3483830231b959e5412579efcf1e35fb2b373e4006ba362543371",
          "kind": "RUN_HISTORY",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:941551651b73e1287910ceaaf55f414ce9bf15fc410f4ce01657ff9fedbc8b84"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "listing_complete": true,
            "runs": [
              {
                "end": "2026-10-28T08:22:28.950000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "763241357",
                "start": "2026-10-28T08:22:02.380000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:56:11.943000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967533",
                "start": "2026-10-27T15:55:47.577000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:55:31.980000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967527",
                "start": "2026-10-27T15:55:17.423000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T11:22:45.240000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762883014",
                "start": "2026-10-27T11:22:42.810000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T10:04:03.517000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762859376",
                "start": "2026-10-27T10:03:42.330000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:20.813000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762589234",
                "start": "2026-10-26T18:20:20.733000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:33.260000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762588999",
                "start": "2026-10-26T18:19:56.113000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:27:55.313000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "761468506",
                "start": "2026-10-24T01:26:52.530000Z",
                "status": "SUCCEEDED"
              }
            ]
          }
        },
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "e6464f408d0786907f4ef96bd464c98a130a37a8800ef7bcc9f1cb9e1136c283",
          "kind": "REFRESH_RUN",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:941551651b73e1287910ceaaf55f414ce9bf15fc410f4ce01657ff9fedbc8b84"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "accounting": "UNAVAILABLE_FROM_JOB_INSTANCE_SCHEMA",
            "end": "2026-10-28T08:22:28.950000Z",
            "error": null,
            "recent_runs": [
              {
                "end": "2026-10-28T08:22:28.950000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "763241357",
                "start": "2026-10-28T08:22:02.380000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:56:11.943000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967533",
                "start": "2026-10-27T15:55:47.577000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:55:31.980000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967527",
                "start": "2026-10-27T15:55:17.423000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T11:22:45.240000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762883014",
                "start": "2026-10-27T11:22:42.810000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T10:04:03.517000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762859376",
                "start": "2026-10-27T10:03:42.330000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:20.813000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762589234",
                "start": "2026-10-26T18:20:20.733000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:33.260000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762588999",
                "start": "2026-10-26T18:19:56.113000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:27:55.313000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "761468506",
                "start": "2026-10-24T01:26:52.530000Z",
                "status": "SUCCEEDED"
              }
            ],
            "rows_read": null,
            "rows_written": null,
            "run_id": "763241357",
            "start": "2026-10-28T08:22:02.380000Z",
            "status": "SUCCEEDED"
          }
        },
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "fb02eea7d345e54fc8b55e7d68657db46a2896e4d730066b9431ee3a6ced92c3",
          "kind": "REFRESH_STATE",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:941551651b73e1287910ceaaf55f414ce9bf15fc410f4ce01657ff9fedbc8b84"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "last_end": "2026-10-28T08:22:28.950000Z",
            "run_id": "763241357",
            "state": "SUCCEEDED"
          }
        }
      ]
    },
    {
      "cached": false,
      "check": "REFRESH_SCHEDULE",
      "observed_at": "2026-10-28T09:20:33.717357Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "ca2ef01b13bd58ca8683c3609430f6d28193e0aff841cef381e1d7998c76e425",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:7f616a0bcd8016f94253e610fd057e1f8c034a2a4f2308173fa82cd0bb89d964"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "01:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        },
        {
          "collected_at": "2026-10-28T09:20:33.717357Z",
          "freshness": "CURRENT",
          "id": "2f9368a12c6260f1a88dc55126aa98ccbed0f5a328d86de68e9c9601e0a327ef",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:20:33.717357Z",
          "provenance": {
            "collector": "microsoft-runtime:50ed9389d7d5682c8f2f36c6c2f43a2a3731a84b0c91204d9e25890e096564dc",
            "evidence_ids": [
              "sha256:963d00f6f461a122327da82562cac5406ca9717ea982ad75895d6ce4e06d2232"
            ],
            "locator": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "value": {
            "native_schedules": {
              "value": []
            },
            "next_due": null,
            "reason": "Job schedule recurrence retained; unsupported recurrence types remain a named coverage gap."
          }
        }
      ]
    },
    {
      "check": "AUTOMATIC_UPDATES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:AUTOMATIC_UPDATES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "JOB_RUNS",
      "observed_at": "2026-10-28T09:20:56.943747Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:20:56.943747Z",
          "freshness": "CURRENT",
          "id": "fc32dc308581077f2d114aa0f240969c734c7736f3c23fa4ac5b5e25ecad94d1",
          "kind": "JOB_RUN",
          "observed_at": "2026-10-28T09:20:56.943747Z",
          "provenance": {
            "collector": "microsoft-runtime:d90ae203d1e049b5d17b28ad8d56b3e9cbbe0ea8e79c91698aded7cf5e687f7e",
            "evidence_ids": [
              "sha256:288cad8544be3ad251f37dd5321a1255394de641730d6a33bb3f3d82ad402672"
            ],
            "locator": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
          "value": {
            "accounting": "UNAVAILABLE_FROM_JOB_INSTANCE_SCHEMA",
            "end": "2026-10-28T08:16:41.2629279Z",
            "error": null,
            "recent_runs": [
              {
                "end": "2026-10-28T08:16:41.2629279Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "7237d82d-a728-4286-8891-6f548097cdcd",
                "start": "2026-10-28T08:16:11.3116784Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T08:03:50.0016825Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "353770e7-8eb4-47bc-8709-0a667ddb04ad",
                "start": "2026-10-28T08:03:00.469989Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T07:58:25.018859Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "7de99675-2ef8-4bd1-8292-c512f5121dbb",
                "start": "2026-10-28T07:57:40.5054246Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:58:07.0533205Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "15dfbcf2-6985-41e8-8ada-d1973f3ec8a0",
                "start": "2026-10-28T06:57:34.3969215Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:16:46.3062373Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "56e7ecc6-efb1-4d67-b6f8-0645b5de2d21",
                "start": "2026-10-28T06:14:52.7382767Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:54:02.6605794Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "c0e2613f-b446-4d00-a2c5-7f44c4662ae2",
                "start": "2026-10-27T15:53:32.7157778Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:44:05.0886872Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "a33b8ae0-57b8-4794-9cab-f50ec12e03ca",
                "start": "2026-10-27T15:43:33.6916187Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:20:29.5709877Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "fa3d9c73-ff5a-410a-89c8-907afd3f623c",
                "start": "2026-10-27T15:19:55.229535Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:10:24.4533955Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "644ef25a-bad3-4e5e-87b0-3f27c9b4498c",
                "start": "2026-10-27T15:09:53.1889637Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T14:31:41.1898358Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "5caa5c35-5e58-4dc1-94f0-fb8a9ab6619a",
                "start": "2026-10-27T14:31:09.9560782Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:59:50.6670091Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "d3d519f4-55b9-48ef-bf68-ee9b3d6fd724",
                "start": "2026-10-27T09:59:21.4245453Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:49:04.8377033Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "f12d45ba-a321-4a76-9f38-cfd86501054b",
                "start": "2026-10-27T09:48:35.0709386Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:41:49.8935835Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "4eda71d5-c497-4d52-b447-232386f672b5",
                "start": "2026-10-27T09:41:18.3358933Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:28:21.9101852Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "175ebde3-2543-47e5-bde0-ec38474c3ccc",
                "start": "2026-10-27T09:27:52.0485311Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T08:36:56.310785Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "d847a503-2bd8-4297-a917-8789854bbbdf",
                "start": "2026-10-27T08:36:25.9174801Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T06:45:53.3924184Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "150cca85-8b3d-44e6-ad1a-2e5ac059e2df",
                "start": "2026-10-27T06:45:24.4810815Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T06:15:17.1734177Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "1db862a2-6df5-41a7-a71a-02ca24eab7da",
                "start": "2026-10-27T06:09:51.1598474Z",
                "status": "CANCELLED"
              },
              {
                "end": "2026-10-26T18:15:51.642450Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "2b43720a-f2bb-47bb-a456-9dac546a4eb4",
                "start": "2026-10-26T18:15:14.6320687Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T02:12:10.4565917Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "c2bf877a-9ff2-4852-aa6b-f0503b71b2f3",
                "start": "2026-10-24T02:11:38.9387923Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:40:16.5003956Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "4ea4687d-5e43-4933-8db5-860286d0f681",
                "start": "2026-10-24T01:39:46.1269955Z",
                "status": "SUCCEEDED"
              }
            ],
            "rows_read": null,
            "rows_written": null,
            "run_id": "7237d82d-a728-4286-8891-6f548097cdcd",
            "start": "2026-10-28T08:16:11.3116784Z",
            "status": "SUCCEEDED"
          }
        }
      ]
    },
    {
      "check": "LAYER_FRESHNESS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:LAYER_FRESHNESS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SOURCE_CHANGES",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:SOURCE_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "NEXT_LOAD",
      "observed_at": "2026-10-28T09:20:33.717357Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "ca2ef01b13bd58ca8683c3609430f6d28193e0aff841cef381e1d7998c76e425",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:7f616a0bcd8016f94253e610fd057e1f8c034a2a4f2308173fa82cd0bb89d964"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "01:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        },
        {
          "collected_at": "2026-10-28T09:20:33.717357Z",
          "freshness": "CURRENT",
          "id": "2f9368a12c6260f1a88dc55126aa98ccbed0f5a328d86de68e9c9601e0a327ef",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:20:33.717357Z",
          "provenance": {
            "collector": "microsoft-runtime:50ed9389d7d5682c8f2f36c6c2f43a2a3731a84b0c91204d9e25890e096564dc",
            "evidence_ids": [
              "sha256:963d00f6f461a122327da82562cac5406ca9717ea982ad75895d6ce4e06d2232"
            ],
            "locator": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "value": {
            "native_schedules": {
              "value": []
            },
            "next_due": null,
            "reason": "Job schedule recurrence retained; unsupported recurrence types remain a named coverage gap."
          }
        }
      ]
    },
    {
      "check": "CONNECTION_MODE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:CONNECTION_MODE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SECURITY_PRESENCE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:SECURITY_PRESENCE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "DEFINITION_CHANGES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:DEFINITION_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    }
  ],
  "path": [
    "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
    "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
    "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
    "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
    "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
    "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
    "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
    "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
    "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce",
    "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
    "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
    "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
    "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
    "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
    "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
    "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
    "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
    "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
    "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
  ],
  "refresh_operations": 10,
  "what_triage_suggests": "Triage has unavailable checks (AUTOMATIC_UPDATES, LAYER_FRESHNESS, SOURCE_CHANGES, CONNECTION_MODE, SECURITY_PRESENCE, DEFINITION_CHANGES); this does not establish that those mechanisms are absent."
}
```

Tool decisions:
```json
[
  {
    "arguments": {
      "layer": "native:4caf47d120d4fd198ffe",
      "purpose": "recreate",
      "query": "EVALUATE ROW(\"Movement Units movement_id 1\", CALCULATE([Movement Units], 'Movements'[movement_id] = 1), \"Movement Units total\", [Movement Units])"
    },
    "tool": "run_dax"
  },
  {
    "arguments": {
      "layer": "native:4caf47d120d4fd198ffe",
      "purpose": "lookup",
      "query": "EVALUATE TOPN(20, SUMMARIZECOLUMNS('Movements'[movement_id], \"u\", [Movement Units]), 'Movements'[movement_id], ASC)"
    },
    "tool": "run_dax"
  },
  {
    "arguments": {
      "node": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
    },
    "tool": "get_job_runs"
  },
  {
    "arguments": {
      "layer": "native:e95b94fd338e7086320f",
      "purpose": "compare",
      "query": "SELECT movement_id, units, event_day, movement_type, source_modified_at_utc FROM [dbo].[stock_movements_round_two_20261003] WHERE movement_id = 1"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "compare",
      "query": "SELECT movement_id, units, event_day, movement_type, source_modified_at_utc FROM [app].[stock_movements_round_two_20261003] WHERE movement_id = 1"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "history",
      "query": "SELECT SUM(units) AS units_as_of FROM [app].[stock_movements_round_two_20261003] FOR SYSTEM_TIME AS OF '2026-10-20T12:00:00' WHERE movement_id = 1"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "history",
      "query": "SELECT t.name, t.temporal_type_desc, h.name AS history_table, c1.name AS period_start, c2.name AS period_end FROM sys.tables t LEFT JOIN sys.tables h ON h.object_id = t.history_table_id LEFT JOIN sys.periods p ON p.object_id = t.object_id LEFT JOIN sys.columns c1 ON c1.object_id = t.object_id AND c1.column_id = p.start_column_id LEFT JOIN sys.columns c2 ON c2.object_id = t.object_id AND c2.column_id = p.end_column_id WHERE t.name = 'stock_movements_round_two_20261003'"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "history",
      "query": "SELECT movement_id, units, movement_type, source_modified_at_utc FROM [app].[stock_movements_round_two_20261003] FOR SYSTEM_TIME ALL WHERE movement_id = 1 ORDER BY source_modified_at_utc"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "cause": "Movement Units is SUM('Movements'[units]) with no date or as-of logic. The Movements table reads the Lakehouse table dbo.stock_movements_round_two_20261003 directly (Direct Lake), and the copy job investigation_round_two_history_probe_20261003 overwrites that table from app.stock_movements_round_two_20261003 on each run. So the visual always shows current rows and never works out a past value. Current value for movement_id 1 is 16 in the model, the Lakehouse table and the source table (one row in each, units 16). A native read of the source table's system-versioned history for 2026-10-20 12:00 UTC succeeded but returned NULL (no row), and FOR SYSTEM_TIME ALL keeps only one version of movement 1 (units 16). The retained history therefore gives no value for movement 1 at that time. The cause of that gap was not established: the catalog query for the history setup and period columns was rejected. Lakehouse table time travel was not checked. The source_modified_at_utc column (2026-10-03 22:51:16) is an application column, not the history validity period. The two failed pipeline runs (2026-10-27 14:25 and 2026-10-28 05:59 UTC) were followed by successful runs; the latest load succeeded 2026-10-28 08:15-08:17 UTC (360 rows read and written) and the model refresh succeeded at 08:22 UTC.",
      "checked": [
        "native:4caf47d120d4fd198ffe",
        "native:e95b94fd338e7086320f",
        "native:9e3796a26d8d5c1a039e",
        "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
        "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
      ],
      "evidence_ids": [
        "case-evidence:6b5f100ca5bcde9abaf0b529b75358497aa2c826fc2adeac290469e3e220eeff",
        "case-evidence:4be86fdbdace11bb982a66623faa79025b7a34be37411fc8ddf1acda5c5c312c",
        "case-evidence:5e162e5e5ec0185bde541361cfff86a3e09cc7ed92dc607657b1f972e88d740b",
        "case-evidence:89790e38ee60f4f7405dc686e2009340a5103f944327734cace28bb346b9dbc0",
        "case-evidence:2eb29e37a265bf1b892944f183d9a02c40abea589c6f6a4111cfaea92ca8e57d",
        "case-evidence:f9749e9281ac69ae7ea4a4850a2ecd16b3de1bb730c05b858eb52f7c0c09d549",
        "case-evidence:dcb5212e02f2d228f19a603fc3520f90998df57594750d4861e579614a620421",
        "case-evidence:28b30c849239ebe5dd232ce3522f29f589a644a46ec18dd3b52f169f4c3c54fe",
        "a87545a3e875d2260873432f55b447cbbe4d461928395aa15254ff574d34c5f6",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json"
      ],
      "numbers": [
        "16",
        "1",
        "7661",
        null
      ],
      "verdict": "definition explained"
    },
    "tool": "submit_finding"
  },
  {
    "arguments": {
      "cause": "Movement Units is SUM('Movements'[units]) with no date or as-of logic. The Movements table reads the Lakehouse table dbo.stock_movements_round_two_20261003 directly (Direct Lake), and the copy job investigation_round_two_history_probe_20261003 overwrites that table from app.stock_movements_round_two_20261003 on each run. So the visual always shows current rows and never works out a past value. Current value for movement_id 1 is 16 in the model, the Lakehouse table and the source table (one row in each, units 16). A native read of the source table's system-versioned history for 2026-10-20 12:00 UTC succeeded but returned NULL (no row), and FOR SYSTEM_TIME ALL keeps only one version of movement 1 (units 16). The retained history therefore gives no value for movement 1 at that time. The cause of that gap was not established: the catalog query for the history setup and period columns was rejected. Lakehouse table time travel was not checked. The source_modified_at_utc column (2026-10-03 22:51:16) is an application column, not the history validity period. The two failed pipeline runs (2026-10-27 14:25 and 2026-10-28 05:59 UTC) were followed by successful runs; the latest load succeeded 2026-10-28 08:15-08:17 UTC (360 rows read and written) and the model refresh succeeded at 08:22 UTC.",
      "checked": [
        "native:4caf47d120d4fd198ffe",
        "native:e95b94fd338e7086320f",
        "native:9e3796a26d8d5c1a039e"
      ],
      "evidence_ids": [
        "case-evidence:6b5f100ca5bcde9abaf0b529b75358497aa2c826fc2adeac290469e3e220eeff",
        "case-evidence:4be86fdbdace11bb982a66623faa79025b7a34be37411fc8ddf1acda5c5c312c",
        "case-evidence:5e162e5e5ec0185bde541361cfff86a3e09cc7ed92dc607657b1f972e88d740b",
        "case-evidence:89790e38ee60f4f7405dc686e2009340a5103f944327734cace28bb346b9dbc0",
        "case-evidence:2eb29e37a265bf1b892944f183d9a02c40abea589c6f6a4111cfaea92ca8e57d",
        "case-evidence:f9749e9281ac69ae7ea4a4850a2ecd16b3de1bb730c05b858eb52f7c0c09d549",
        "case-evidence:dcb5212e02f2d228f19a603fc3520f90998df57594750d4861e579614a620421",
        "case-evidence:28b30c849239ebe5dd232ce3522f29f589a644a46ec18dd3b52f169f4c3c54fe",
        "a87545a3e875d2260873432f55b447cbbe4d461928395aa15254ff574d34c5f6",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/57e128c3-6ba0-4aaf-9464-81164ecdc782/part/copyjob-content.json"
      ],
      "numbers": [
        "16",
        "1",
        "7661",
        null
      ],
      "verdict": "definition explained"
    },
    "tool": "submit_finding"
  },
  {
    "arguments": {
      "cause": "Movement Units is SUM('Movements'[units]) with no date or as-of logic. The Movements table reads the Lakehouse table dbo.stock_movements_round_two_20261003 directly (Direct Lake), and the copy job investigation_round_two_history_probe_20261003 overwrites that table from app.stock_movements_round_two_20261003 on each run. So the visual always shows current rows and never works out a past value. Current value for movement_id 1 is 16 in the model, the Lakehouse table and the source table (one row in each, units 16). A native read of the source table's system-versioned history for 2026-10-20 12:00 UTC succeeded but returned NULL (no row), and FOR SYSTEM_TIME ALL keeps only one version of movement 1 (units 16). The retained history therefore gives no value for movement 1 at that time. The cause of that gap was not established: the catalog query for the history setup and period columns was rejected. Lakehouse table time travel was not checked. The source_modified_at_utc column (2026-10-03 22:51:16) is an application column, not the history validity period. The two failed pipeline runs (2026-10-27 14:25 and 2026-10-28 05:59 UTC) were followed by successful runs; the latest load succeeded 2026-10-28 08:15-08:17 UTC (360 rows read and written) and the model refresh succeeded at 08:22 UTC.",
      "checked": [
        "native:4caf47d120d4fd198ffe",
        "native:e95b94fd338e7086320f",
        "native:9e3796a26d8d5c1a039e"
      ],
      "evidence_ids": [
        "case-evidence:6b5f100ca5bcde9abaf0b529b75358497aa2c826fc2adeac290469e3e220eeff",
        "case-evidence:4be86fdbdace11bb982a66623faa79025b7a34be37411fc8ddf1acda5c5c312c",
        "case-evidence:5e162e5e5ec0185bde541361cfff86a3e09cc7ed92dc607657b1f972e88d740b",
        "case-evidence:89790e38ee60f4f7405dc686e2009340a5103f944327734cace28bb346b9dbc0",
        "case-evidence:2eb29e37a265bf1b892944f183d9a02c40abea589c6f6a4111cfaea92ca8e57d",
        "case-evidence:f9749e9281ac69ae7ea4a4850a2ecd16b3de1bb730c05b858eb52f7c0c09d549",
        "case-evidence:dcb5212e02f2d228f19a603fc3520f90998df57594750d4861e579614a620421",
        "case-evidence:28b30c849239ebe5dd232ce3522f29f589a644a46ec18dd3b52f169f4c3c54fe"
      ],
      "numbers": [
        "16",
        "1",
        "7661",
        null
      ],
      "verdict": "definition explained"
    },
    "tool": "submit_finding"
  },
  {
    "arguments": {
      "cause": "Movement Units is SUM('Movements'[units]) with no date or as-of logic. The Movements table reads the Lakehouse table dbo.stock_movements_round_two_20261003 directly (Direct Lake), and the copy job investigation_round_two_history_probe_20261003 overwrites that table from app.stock_movements_round_two_20261003 on each run. So the visual always shows current rows and never works out a past value. Current value for movement_id 1 is 16 in the model, the Lakehouse table and the source table (one row in each, units 16). A native read of the source table's system-versioned history for 2026-10-20 12:00 UTC succeeded but returned NULL (no row), and FOR SYSTEM_TIME ALL keeps only one version of movement 1 (units 16). The retained history therefore gives no value for movement 1 at that time. Limitation: why there is no version at that time was not established, because the history period columns and setup were not read. Lakehouse table time travel was not checked. The source_modified_at_utc column (2026-10-03 22:51:16) is an application column, not the history validity period. The two failed pipeline runs (2026-10-27 14:25 and 2026-10-28 05:59 UTC) were followed by successful runs; the latest load succeeded 2026-10-28 08:15-08:17 UTC (360 rows read and written) and the model refresh succeeded at 08:22 UTC.",
      "checked": [
        "native:4caf47d120d4fd198ffe",
        "native:e95b94fd338e7086320f",
        "native:9e3796a26d8d5c1a039e"
      ],
      "evidence_ids": [
        "case-evidence:6b5f100ca5bcde9abaf0b529b75358497aa2c826fc2adeac290469e3e220eeff",
        "case-evidence:4be86fdbdace11bb982a66623faa79025b7a34be37411fc8ddf1acda5c5c312c",
        "case-evidence:5e162e5e5ec0185bde541361cfff86a3e09cc7ed92dc607657b1f972e88d740b",
        "case-evidence:89790e38ee60f4f7405dc686e2009340a5103f944327734cace28bb346b9dbc0",
        "case-evidence:2eb29e37a265bf1b892944f183d9a02c40abea589c6f6a4111cfaea92ca8e57d",
        "case-evidence:f9749e9281ac69ae7ea4a4850a2ecd16b3de1bb730c05b858eb52f7c0c09d549",
        "case-evidence:28b30c849239ebe5dd232ce3522f29f589a644a46ec18dd3b52f169f4c3c54fe"
      ],
      "numbers": [
        "16",
        "1",
        "7661",
        null
      ],
      "verdict": "definition explained"
    },
    "tool": "submit_finding"
  }
]
```

Queries:
```json
[
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/movement_id",
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units"
    ],
    "duration_seconds": 5.377762413000028,
    "executed_text": "EVALUATE TOPN(251,ROW(\"Movement Units movement_id 1\",CALCULATE([Movement Units],'Movements'[movement_id] = 1),\"Movement Units total\",[Movement Units]))",
    "id": "query:7d5d66b2383c3b57c500e287e888d8e30a8c7b7ebf434257498e66fa3bae72a4:1",
    "layer": "native:4caf47d120d4fd198ffe",
    "parameters": [],
    "purpose": "recreate",
    "result": {
      "rows": [
        {
          "[Movement Units movement_id 1]": 16,
          "[Movement Units total]": 7661
        }
      ],
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "d066e492923d4a1918cbb2f26debce16da26f12e95085c5df2c8175369d69a3e",
    "row_count": 1,
    "signature": "7d5d66b2383c3b57c500e287e888d8e30a8c7b7ebf434257498e66fa3bae72a4",
    "status": "SUCCEEDED",
    "text": "EVALUATE ROW(\"Movement Units movement_id 1\", CALCULATE([Movement Units], 'Movements'[movement_id] = 1), \"Movement Units total\", [Movement Units])",
    "time": "2026-10-28T09:21:20.487962+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/movement_id",
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/measures/Movement%20Units"
    ],
    "duration_seconds": 2.2019843939999646,
    "executed_text": "EVALUATE TOPN(251,TOPN(20,SUMMARIZECOLUMNS('Movements'[movement_id],\"u\",[Movement Units]),'Movements'[movement_id],ASC))",
    "id": "query:2e56d3c4c35b45855ce4442a3af5eef2331e8e32366085729470af160f3f54e4:2",
    "layer": "native:4caf47d120d4fd198ffe",
    "parameters": [],
    "purpose": "lookup",
    "result": {
      "rows": [
        {
          "Movements[movement_id]": 20,
          "[u]": 18
        },
        {
          "Movements[movement_id]": 19,
          "[u]": 38
        },
        {
          "Movements[movement_id]": 15,
          "[u]": 38
        },
        {
          "Movements[movement_id]": 17,
          "[u]": 24
        },
        {
          "Movements[movement_id]": 18,
          "[u]": 21
        },
        {
          "Movements[movement_id]": 14,
          "[u]": 5
        },
        {
          "Movements[movement_id]": 7,
          "[u]": 20
        },
        {
          "Movements[movement_id]": 11,
          "[u]": 23
        },
        {
          "Movements[movement_id]": 12,
          "[u]": 19
        },
        {
          "Movements[movement_id]": 16,
          "[u]": 28
        },
        {
          "Movements[movement_id]": 13,
          "[u]": 20
        },
        {
          "Movements[movement_id]": 2,
          "[u]": 17
        },
        {
          "Movements[movement_id]": 3,
          "[u]": 39
        },
        {
          "Movements[movement_id]": 4,
          "[u]": 21
        },
        {
          "Movements[movement_id]": 6,
          "[u]": 36
        },
        {
          "Movements[movement_id]": 9,
          "[u]": 11
        },
        {
          "Movements[movement_id]": 8,
          "[u]": 19
        },
        {
          "Movements[movement_id]": 10,
          "[u]": 4
        },
        {
          "Movements[movement_id]": 1,
          "[u]": 16
        },
        {
          "Movements[movement_id]": 5,
          "[u]": 3
        }
      ],
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "b32c92dd8dba21372d50280f2e170f8510ffd27a74633884c24c033e4afbfb1b",
    "row_count": 20,
    "signature": "2e56d3c4c35b45855ce4442a3af5eef2331e8e32366085729470af160f3f54e4",
    "status": "SUCCEEDED",
    "text": "EVALUATE TOPN(20, SUMMARIZECOLUMNS('Movements'[movement_id], \"u\", [Movement Units]), 'Movements'[movement_id], ASC)",
    "time": "2026-10-28T09:21:26.135242+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003"
    ],
    "duration_seconds": 7.09807860799998,
    "executed_text": "SELECT TOP 251 [stock_movements_round_two_20261003].[movement_id] AS [movement_id], [stock_movements_round_two_20261003].[units] AS [units], [stock_movements_round_two_20261003].[event_day] AS [event_day], [stock_movements_round_two_20261003].[movement_type] AS [movement_type], [stock_movements_round_two_20261003].[source_modified_at_utc] AS [source_modified_at_utc] FROM [dbo].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003] WHERE [stock_movements_round_two_20261003].[movement_id] = CAST(@p0 AS BIGINT)",
    "id": "query:06842e4fe4943a264785aadb346291518df94fba4b8056eaac92a1f6d45688f2:3",
    "layer": "native:e95b94fd338e7086320f",
    "parameters": [
      {
        "name": "@p0",
        "value": "1"
      }
    ],
    "purpose": "compare",
    "result": {
      "column_types": {
        "event_day": "String",
        "movement_id": "Int64",
        "movement_type": "String",
        "source_modified_at_utc": "DateTime",
        "units": "Int64"
      },
      "execution_identity": {
        "database": "round_two_bronze_20261003",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "event_day": "2026-09-11",
          "movement_id": "1",
          "movement_type": "RECEIPT",
          "source_modified_at_utc": "2026-10-03 22:51:16.882024",
          "units": "16"
        }
      ]
    },
    "result_digest": "cdca116cede14d43c35255771b2e99566721b50767e03fffef8b81bf9f951dc6",
    "row_count": 1,
    "signature": "06842e4fe4943a264785aadb346291518df94fba4b8056eaac92a1f6d45688f2",
    "status": "SUCCEEDED",
    "text": "SELECT movement_id, units, event_day, movement_type, source_modified_at_utc FROM [dbo].[stock_movements_round_two_20261003] WHERE movement_id = 1",
    "time": "2026-10-28T09:21:52.125543+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 10.460565817000031,
    "executed_text": "SELECT TOP 251 [stock_movements_round_two_20261003].[movement_id] AS [movement_id], [stock_movements_round_two_20261003].[units] AS [units], [stock_movements_round_two_20261003].[event_day] AS [event_day], [stock_movements_round_two_20261003].[movement_type] AS [movement_type], [stock_movements_round_two_20261003].[source_modified_at_utc] AS [source_modified_at_utc] FROM [app].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003] WHERE [stock_movements_round_two_20261003].[movement_id] = CAST(@p0 AS BIGINT)",
    "id": "query:8ad338eec2406be7278bbd6c2edeb034dec53ece34c5e166819a65d28feb8b67:4",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [
      {
        "name": "@p0",
        "value": "1"
      }
    ],
    "purpose": "compare",
    "result": {
      "column_types": {
        "event_day": "String",
        "movement_id": "Int64",
        "movement_type": "String",
        "source_modified_at_utc": "DateTime",
        "units": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T09:22:09.678261+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T09:21:59.831265+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "event_day": "2026-09-11",
          "movement_id": "1",
          "movement_type": "RECEIPT",
          "source_modified_at_utc": "2026-10-03 22:51:16.882024",
          "units": "16"
        }
      ]
    },
    "result_digest": "088e9ce2a54773b7f16e9cf600f2f12e33787718bf3b864f49996fb76b831932",
    "row_count": 1,
    "signature": "8ad338eec2406be7278bbd6c2edeb034dec53ece34c5e166819a65d28feb8b67",
    "status": "SUCCEEDED",
    "text": "SELECT movement_id, units, event_day, movement_type, source_modified_at_utc FROM [app].[stock_movements_round_two_20261003] WHERE movement_id = 1",
    "time": "2026-10-28T09:21:59.492079+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 3.625160254999969,
    "executed_text": "SELECT TOP 251 SUM([stock_movements_round_two_20261003].[units]) AS [units_as_of] FROM [app].[stock_movements_round_two_20261003] FOR SYSTEM_TIME AS OF @p1 AS [stock_movements_round_two_20261003] WHERE [stock_movements_round_two_20261003].[movement_id] = CAST(@p0 AS BIGINT)",
    "id": "query:a1b1a36b24f2264026b32bb10bdb4674ba0374f7da00c511b033ff1a8e370d09:5",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [
      {
        "name": "@p0",
        "value": "1"
      },
      {
        "name": "@p1",
        "value": "2026-10-20T12:00:00"
      }
    ],
    "purpose": "history",
    "result": {
      "column_types": {
        "units_as_of": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T09:22:13.623447+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T09:22:10.897699+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "units_as_of": null
        }
      ]
    },
    "result_digest": "4a62dc6f74be865ae67cc3bcfa2d32ec274eec1181ac506fe0b31ec0020c032e",
    "row_count": 1,
    "signature": "a1b1a36b24f2264026b32bb10bdb4674ba0374f7da00c511b033ff1a8e370d09",
    "status": "SUCCEEDED",
    "text": "SELECT SUM(units) AS units_as_of FROM [app].[stock_movements_round_two_20261003] FOR SYSTEM_TIME AS OF '2026-10-20T12:00:00' WHERE movement_id = 1",
    "time": "2026-10-28T09:22:10.274459+00:00",
    "truncated": false
  },
  {
    "duration_seconds": 0,
    "error": "SQL object unavailable or view dependencies not validated",
    "error_type": "QueryRejection",
    "failure_class": "wrong column or table",
    "id": "query:76155af6b656b23fe3625213402cc0bdd23fcd9ba397705de06c1bcf3593a2a6:6",
    "layer": "native:9e3796a26d8d5c1a039e",
    "native_dispatched": false,
    "purpose": "history",
    "result_digest": null,
    "row_count": null,
    "schema_slice": [
      {
        "columns": [
          {
            "column_id": 2,
            "computed_definition": null,
            "data_type": "int",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 4,
            "name": "warehouse_id",
            "object_id": 1938105945,
            "precision": 10,
            "scale": 0
          },
          {
            "column_id": 8,
            "computed_definition": null,
            "data_type": "timestamp",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 8,
            "name": "source_row_version",
            "object_id": 1938105945,
            "precision": 0,
            "scale": 0
          },
          {
            "column_id": 5,
            "computed_definition": null,
            "data_type": "nvarchar",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 200,
            "name": "event_day",
            "object_id": 1938105945,
            "precision": 0,
            "scale": 0
          },
          {
            "column_id": 6,
            "computed_definition": null,
            "data_type": "nvarchar",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 200,
            "name": "movement_type",
            "object_id": 1938105945,
            "precision": 0,
            "scale": 0
          },
          {
            "column_id": 3,
            "computed_definition": null,
            "data_type": "int",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 4,
            "name": "product_id",
            "object_id": 1938105945,
            "precision": 10,
            "scale": 0
          },
          {
            "column_id": 4,
            "computed_definition": null,
            "data_type": "int",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 4,
            "name": "units",
            "object_id": 1938105945,
            "precision": 10,
            "scale": 0
          },
          {
            "column_id": 7,
            "computed_definition": null,
            "data_type": "datetime2",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": true,
            "max_length": 8,
            "name": "source_modified_at_utc",
            "object_id": 1938105945,
            "precision": 27,
            "scale": 7
          },
          {
            "column_id": 1,
            "computed_definition": null,
            "data_type": "int",
            "default_definition": null,
            "is_identity": false,
            "is_nullable": false,
            "max_length": 4,
            "name": "movement_id",
            "object_id": 1938105945,
            "precision": 10,
            "scale": 0
          }
        ],
        "id": "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945",
        "name": "stock_movements_round_two_20261003",
        "schema_name": "app",
        "type_desc": "USER_TABLE"
      }
    ],
    "signature": "76155af6b656b23fe3625213402cc0bdd23fcd9ba397705de06c1bcf3593a2a6",
    "status": "ERROR",
    "text": "SELECT t.name, t.temporal_type_desc, h.name AS history_table, c1.name AS period_start, c2.name AS period_end FROM sys.tables t LEFT JOIN sys.tables h ON h.object_id = t.history_table_id LEFT JOIN sys.periods p ON p.object_id = t.object_id LEFT JOIN sys.columns c1 ON c1.object_id = t.object_id AND c1.column_id = p.start_column_id LEFT JOIN sys.columns c2 ON c2.object_id = t.object_id AND c2.column_id = p.end_column_id WHERE t.name = 'stock_movements_round_two_20261003'",
    "time": "2026-10-28T09:22:22.685606+00:00"
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 3.3088554130000034,
    "executed_text": "SELECT TOP 251 [stock_movements_round_two_20261003].[movement_id] AS [movement_id], [stock_movements_round_two_20261003].[units] AS [units], [stock_movements_round_two_20261003].[movement_type] AS [movement_type], [stock_movements_round_two_20261003].[source_modified_at_utc] AS [source_modified_at_utc] FROM [app].[stock_movements_round_two_20261003] FOR SYSTEM_TIME ALL AS [stock_movements_round_two_20261003] WHERE [stock_movements_round_two_20261003].[movement_id] = CAST(@p0 AS BIGINT) ORDER BY [source_modified_at_utc]",
    "id": "query:ce1023d8cdc14bdd197a306908d7266239f1e470c54616c06e6e12905756c6c1:7",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [
      {
        "name": "@p0",
        "value": "1"
      }
    ],
    "purpose": "history",
    "result": {
      "column_types": {
        "movement_id": "Int64",
        "movement_type": "String",
        "source_modified_at_utc": "DateTime",
        "units": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T09:22:31.437508+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T09:22:28.733495+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "movement_id": "1",
          "movement_type": "RECEIPT",
          "source_modified_at_utc": "2026-10-03 22:51:16.882024",
          "units": "16"
        }
      ]
    },
    "result_digest": "d6d0c1aaf97239e7032c7a90e4b2bcea300270394c83d87f75d5d17bd4247960",
    "row_count": 1,
    "signature": "ce1023d8cdc14bdd197a306908d7266239f1e470c54616c06e6e12905756c6c1",
    "status": "SUCCEEDED",
    "text": "SELECT movement_id, units, movement_type, source_modified_at_utc FROM [app].[stock_movements_round_two_20261003] FOR SYSTEM_TIME ALL WHERE movement_id = 1 ORDER BY source_modified_at_utc",
    "time": "2026-10-28T09:22:28.394479+00:00",
    "truncated": false
  }
]
```

Final answer:
```json
"definition explained. Movement Units is SUM('Movements'[units]) with no date or as-of logic. The Movements table reads the Lakehouse table dbo.stock_movements_round_two_20261003 directly (Direct Lake), and the copy job investigation_round_two_history_probe_20261003 overwrites that table from app.stock_movements_round_two_20261003 on each run. So the visual always shows current rows and never works out a past value. Current value for movement_id 1 is 16 in the model, the Lakehouse table and the source table (one row in each, units 16). A native read of the source table's system-versioned history for 2026-10-20 12:00 UTC succeeded but returned NULL (no row), and FOR SYSTEM_TIME ALL keeps only one version of movement 1 (units 16). The retained history therefore gives no value for movement 1 at that time. Limitation: why there is no version at that time was not established, because the history period columns and setup were not read. Lakehouse table time travel was not checked. The source_modified_at_utc column (2026-10-03 22:51:16) is an application column, not the history validity period. The two failed pipeline runs (2026-10-27 14:25 and 2026-10-28 05:59 UTC) were followed by successful runs; the latest load succeeded 2026-10-28 08:15-08:17 UTC (360 rows read and written) and the model refresh succeeded at 08:22 UTC.\nNumbers: 16, 1, 7661, BLANK.\nChecked: Application load fixture 20261003, round_two_bronze_20261003, ordersops.\nNative comparisons are observational snapshots; aligned query-bound versions are not established.\nCatalog bookkeeping unavailable: collector containment (recovered from literal native address), current inventory availability, inventory content hashes (metadata digests are derived and labelled), inventory provenance, per-asset collector timestamps. This does not block investigation; successful queries establish present readability only.\nattestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
```

Sealed expected:
```json
{
  "basis": "Native scenario observations verified before sealing; same fact-based class contract as sealed v2 dev template v2-before-temporal-retention-v1. No DIA output used to author wording or expectations.",
  "case_id": "v3-before-temporal-retention",
  "cause": "Requested time precedes retained temporal evidence; historical quantity cannot be established.",
  "estate": "fixture",
  "expectation_basis": "Practice source literals, declared definitions and reversible scenario plan; never an engine answer.",
  "fixture": "baseline",
  "id": "v3-before-temporal-retention",
  "layer": "source history boundary",
  "split": "HELD_OUT_V3",
  "variation": "independent new held-out v3",
  "verdict": "not found"
}
```

### v3-record-absent-everywhere
Layer: match. The delivered answer places the absence at the source application. Lookups for movement_id 900099 in app.stock_movements_round_two_20261003 (ordersops), in the landing table dbo.stock_movements_round_two_20261003 and in the semantic model 'Movements' all returned 0 rows. Every layer holds the same 360 rows with IDs 1–360. It concludes that no load or model step dropped the record and the source doesn't have it.

Cause: match in substance. The expected cause is that record 900099 is absent at the source and at every compared reachable layer. The answer doesn't mention the expected 'BLANK is not zero' point, but the user said they weren't reporting an amount, so that gap is minor.

Verdict: no match. The answer's verdict is 'not found'; the sealed verdict is 'as designed'. 'Not found' is a separate verdict category. The answer implies no defect in the pipeline but never concludes that the report is behaving as designed. It also leaves open whether the record once existed and was removed, rather than closing the ticket as expected behaviour. I'm treating this as a real category difference, not a wording difference.

Overall: one of three components fails, so this is a partial match and scores zero. Not harmful: the stated cause is correct and backed by evidence, not a confident wrong cause.

Handoff (1): the queries are fully kept and can be rerun, and the stopping point is clear. The handoff object is empty, though, and there are no explicit next checks beyond noting that current-row reads can't show history. Restrict the cause to what the cited native evidence establishes.

Intake:
```json
{
  "compared_with": {
    "kind": "SOURCE_SYSTEM",
    "source": "d41e1c7af0bee9e569e9e4085c645331f3eb19ad9e7651dea93c571007beaaa1"
  },
  "description": "I'm looking for movement900099 from around 2026-09-12. I expected to see it, but it doesn't appear in the Movement Units visual on the Application Movements page. I also checked the application export, and it isn't there either. I'm not reporting an amount for this movement. I just can't find the record anywhere.",
  "details": {
    "approximate_date": "2026-09-12",
    "record": "movement900099"
  },
  "issue_type": "RECORD_MISSING",
  "page": "e4d6e671103ca3746c4ca9435fc635e13ae0a08bf09ffa515580b7f1a50fd7f7",
  "report": "3ba93e33aa41f6b91b0ef623bfd66bf2d9ec9eefd5e583643e6462e0dbd5b2ed",
  "version": "IntakeRequest/1",
  "visual": "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce"
}
```

Target:
```json
{
  "layers": {
    "native:4caf47d120d4fd198ffe": {
      "dialect": "DAX",
      "label": "Application load fixture 20261003"
    },
    "native:9e3796a26d8d5c1a039e": {
      "dialect": "T-SQL",
      "label": "ordersops"
    },
    "native:e95b94fd338e7086320f": {
      "dialect": "T-SQL",
      "label": "round_two_bronze_20261003"
    }
  }
}
```

Triage:
```json
{
  "facts": [
    {
      "cached": true,
      "check": "MODEL_REFRESH",
      "observed_at": "2026-10-28T09:21:02.513855Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "5705f36190d3483830231b959e5412579efcf1e35fb2b373e4006ba362543371",
          "kind": "RUN_HISTORY",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:941551651b73e1287910ceaaf55f414ce9bf15fc410f4ce01657ff9fedbc8b84"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "listing_complete": true,
            "runs": [
              {
                "end": "2026-10-28T08:22:28.950000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "763241357",
                "start": "2026-10-28T08:22:02.380000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:56:11.943000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967533",
                "start": "2026-10-27T15:55:47.577000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:55:31.980000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967527",
                "start": "2026-10-27T15:55:17.423000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T11:22:45.240000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762883014",
                "start": "2026-10-27T11:22:42.810000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T10:04:03.517000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762859376",
                "start": "2026-10-27T10:03:42.330000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:20.813000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762589234",
                "start": "2026-10-26T18:20:20.733000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:33.260000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762588999",
                "start": "2026-10-26T18:19:56.113000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:27:55.313000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "761468506",
                "start": "2026-10-24T01:26:52.530000Z",
                "status": "SUCCEEDED"
              }
            ]
          }
        },
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "e6464f408d0786907f4ef96bd464c98a130a37a8800ef7bcc9f1cb9e1136c283",
          "kind": "REFRESH_RUN",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:941551651b73e1287910ceaaf55f414ce9bf15fc410f4ce01657ff9fedbc8b84"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "accounting": "UNAVAILABLE_FROM_JOB_INSTANCE_SCHEMA",
            "end": "2026-10-28T08:22:28.950000Z",
            "error": null,
            "recent_runs": [
              {
                "end": "2026-10-28T08:22:28.950000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "763241357",
                "start": "2026-10-28T08:22:02.380000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:56:11.943000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967533",
                "start": "2026-10-27T15:55:47.577000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:55:31.980000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762967527",
                "start": "2026-10-27T15:55:17.423000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T11:22:45.240000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762883014",
                "start": "2026-10-27T11:22:42.810000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T10:04:03.517000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762859376",
                "start": "2026-10-27T10:03:42.330000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:20.813000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762589234",
                "start": "2026-10-26T18:20:20.733000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-26T18:20:33.260000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "762588999",
                "start": "2026-10-26T18:19:56.113000Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:27:55.313000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "761468506",
                "start": "2026-10-24T01:26:52.530000Z",
                "status": "SUCCEEDED"
              }
            ],
            "rows_read": null,
            "rows_written": null,
            "run_id": "763241357",
            "start": "2026-10-28T08:22:02.380000Z",
            "status": "SUCCEEDED"
          }
        },
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "fb02eea7d345e54fc8b55e7d68657db46a2896e4d730066b9431ee3a6ced92c3",
          "kind": "REFRESH_STATE",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:941551651b73e1287910ceaaf55f414ce9bf15fc410f4ce01657ff9fedbc8b84"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "last_end": "2026-10-28T08:22:28.950000Z",
            "run_id": "763241357",
            "state": "SUCCEEDED"
          }
        }
      ]
    },
    {
      "cached": true,
      "check": "REFRESH_SCHEDULE",
      "observed_at": "2026-10-28T09:21:02.513855Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:21:28.593748Z",
          "freshness": "CURRENT",
          "id": "a51d816e82fea98a4795ee2b42fd5c444b7c7f29a11c1b339fd7c4bc6cd694b8",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:21:28.593748Z",
          "provenance": {
            "collector": "microsoft-runtime:50ed9389d7d5682c8f2f36c6c2f43a2a3731a84b0c91204d9e25890e096564dc",
            "evidence_ids": [
              "sha256:bb96e0b64165d37d4a774cc5fa3c2961d16124929a1214bacc0f8380569b27c7"
            ],
            "locator": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "value": {
            "native_schedules": {
              "value": []
            },
            "next_due": null,
            "reason": "Job schedule recurrence retained; unsupported recurrence types remain a named coverage gap."
          }
        },
        {
          "collected_at": "2026-10-28T09:21:02.513855Z",
          "freshness": "CURRENT",
          "id": "ca2ef01b13bd58ca8683c3609430f6d28193e0aff841cef381e1d7998c76e425",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:21:02.513855Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:7f616a0bcd8016f94253e610fd057e1f8c034a2a4f2308173fa82cd0bb89d964"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "01:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        }
      ]
    },
    {
      "check": "AUTOMATIC_UPDATES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:AUTOMATIC_UPDATES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "JOB_RUNS",
      "observed_at": "2026-10-28T09:30:26.507600Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:30:42.773263Z",
          "freshness": "CURRENT",
          "id": "f7f9568fdefe44f919ba74f8b94210513078d5e017c61bc1153a11e0a3e5fd5b",
          "kind": "JOB_RUN",
          "observed_at": "2026-10-28T09:30:42.773263Z",
          "provenance": {
            "collector": "microsoft-runtime:d90ae203d1e049b5d17b28ad8d56b3e9cbbe0ea8e79c91698aded7cf5e687f7e",
            "evidence_ids": [
              "sha256:11397e360a7313b8b74426de908e4e30883b32fe6187bc9d1f6c5956d218c870"
            ],
            "locator": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
          "value": {
            "accounting": "UNAVAILABLE_FROM_JOB_INSTANCE_SCHEMA",
            "end": "2026-10-28T08:16:41.2629279Z",
            "error": null,
            "recent_runs": [
              {
                "end": "2026-10-28T08:16:41.2629279Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "7237d82d-a728-4286-8891-6f548097cdcd",
                "start": "2026-10-28T08:16:11.3116784Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T08:03:50.0016825Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "353770e7-8eb4-47bc-8709-0a667ddb04ad",
                "start": "2026-10-28T08:03:00.469989Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T07:58:25.018859Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "7de99675-2ef8-4bd1-8292-c512f5121dbb",
                "start": "2026-10-28T07:57:40.5054246Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:58:07.0533205Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "15dfbcf2-6985-41e8-8ada-d1973f3ec8a0",
                "start": "2026-10-28T06:57:34.3969215Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:16:46.3062373Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "56e7ecc6-efb1-4d67-b6f8-0645b5de2d21",
                "start": "2026-10-28T06:14:52.7382767Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:54:02.6605794Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "c0e2613f-b446-4d00-a2c5-7f44c4662ae2",
                "start": "2026-10-27T15:53:32.7157778Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:44:05.0886872Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "a33b8ae0-57b8-4794-9cab-f50ec12e03ca",
                "start": "2026-10-27T15:43:33.6916187Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:20:29.5709877Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "fa3d9c73-ff5a-410a-89c8-907afd3f623c",
                "start": "2026-10-27T15:19:55.229535Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:10:24.4533955Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "644ef25a-bad3-4e5e-87b0-3f27c9b4498c",
                "start": "2026-10-27T15:09:53.1889637Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T14:31:41.1898358Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "5caa5c35-5e58-4dc1-94f0-fb8a9ab6619a",
                "start": "2026-10-27T14:31:09.9560782Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:59:50.6670091Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "d3d519f4-55b9-48ef-bf68-ee9b3d6fd724",
                "start": "2026-10-27T09:59:21.4245453Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:49:04.8377033Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "f12d45ba-a321-4a76-9f38-cfd86501054b",
                "start": "2026-10-27T09:48:35.0709386Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:41:49.8935835Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "4eda71d5-c497-4d52-b447-232386f672b5",
                "start": "2026-10-27T09:41:18.3358933Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:28:21.9101852Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "175ebde3-2543-47e5-bde0-ec38474c3ccc",
                "start": "2026-10-27T09:27:52.0485311Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T08:36:56.310785Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "d847a503-2bd8-4297-a917-8789854bbbdf",
                "start": "2026-10-27T08:36:25.9174801Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T06:45:53.3924184Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "150cca85-8b3d-44e6-ad1a-2e5ac059e2df",
                "start": "2026-10-27T06:45:24.4810815Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T06:15:17.1734177Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "1db862a2-6df5-41a7-a71a-02ca24eab7da",
                "start": "2026-10-27T06:09:51.1598474Z",
                "status": "CANCELLED"
              },
              {
                "end": "2026-10-26T18:15:51.642450Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "2b43720a-f2bb-47bb-a456-9dac546a4eb4",
                "start": "2026-10-26T18:15:14.6320687Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T02:12:10.4565917Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "c2bf877a-9ff2-4852-aa6b-f0503b71b2f3",
                "start": "2026-10-24T02:11:38.9387923Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-24T01:40:16.5003956Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "4ea4687d-5e43-4933-8db5-860286d0f681",
                "start": "2026-10-24T01:39:46.1269955Z",
                "status": "SUCCEEDED"
              }
            ],
            "rows_read": null,
            "rows_written": null,
            "run_id": "7237d82d-a728-4286-8891-6f548097cdcd",
            "start": "2026-10-28T08:16:11.3116784Z",
            "status": "SUCCEEDED"
          }
        },
        {
          "collected_at": "2026-10-28T09:30:26.507600Z",
          "freshness": "CURRENT",
          "id": "a680a5c3ddc56d3fa1753afb62b56285dbe22738d29dcafdbc1f63b9b59c2cb5",
          "kind": "JOB_RUN",
          "observed_at": "2026-10-28T09:30:26.507600Z",
          "provenance": {
            "collector": "microsoft-runtime:50ed9389d7d5682c8f2f36c6c2f43a2a3731a84b0c91204d9e25890e096564dc",
            "evidence_ids": [
              "sha256:f86a3f073ce25f8b763734cd4a9dfc0a66ecdee13690e6796d06e0e738adf519",
              "sha256:0cddb6bfccc59dfed289178c839fd641e610f3a19a5b6092d92ebd480836426e"
            ],
            "locator": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "value": {
            "accounting": "DECLARED_WAREHOUSE_AUDIT",
            "end": "2026-10-28T08:17:21.010000Z",
            "error": null,
            "recent_runs": [
              {
                "end": "2026-10-28T08:17:21.010000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "b19be888-92f6-4c34-81bc-0a3433cb578b",
                "start": "2026-10-28T08:15:49.4748707Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T08:04:45.0766667Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "c4317ee4-2ce8-49b4-91aa-aa75f1d6448d",
                "start": "2026-10-28T08:02:16.3610689Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T07:59:05.190000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "009b614d-7e17-4523-a350-d40769c4e997",
                "start": "2026-10-28T07:57:19.3760961Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:58:48.380000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "0f681f9d-b78a-4498-8c2f-14f7d6d52175",
                "start": "2026-10-28T06:57:11.0246836Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:40:27.6233333Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "4456ed50-6454-41f3-ab53-90102beb10e3",
                "start": "2026-10-28T06:30:10.5600019Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T06:18:21.950000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "ccb5f004-5b06-488c-9009-0464682b820b",
                "start": "2026-10-28T06:09:45.2412485Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-28T05:59:56.280000Z",
                "error": {
                  "errorCode": "2011",
                  "isRetriable": false,
                  "message": "Operation on target round22_controlled_failure_before_original_activities failed: Round22 controlled fixture failure before original activities",
                  "requestId": "88130a95-90a7-4b24-abc3-eb8fab6590c4"
                },
                "rows_read": null,
                "rows_written": null,
                "run_id": "60332cec-53c5-4268-86e2-f875836b597c",
                "start": "2026-10-28T05:59:25.2333333Z",
                "status": "FAILED"
              },
              {
                "end": "2026-10-27T15:54:40.3733333Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "fd221a3c-173c-40a6-8f79-ff1b8b5484fd",
                "start": "2026-10-27T15:53:11.6517633Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:44:49.2866667Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "8b738527-489f-4efc-92c3-ba9f30d8da9c",
                "start": "2026-10-27T15:43:10.051129Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:21:05.870000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "496c0d2b-1a8b-49d1-926a-17533916fa19",
                "start": "2026-10-27T15:19:31.1976863Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:11:10.570000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "12026c56-4c03-48b6-a720-7527b90e238b",
                "start": "2026-10-27T15:09:29.7412419Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T15:02:37.480000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "2869a0b6-1e0e-4c10-9240-c603668893a6",
                "start": "2026-10-27T14:52:27.2677265Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T14:47:58.3333333Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "6caacbdb-4ba6-41d7-897d-412b7a50529c",
                "start": "2026-10-27T14:37:47.5848246Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T14:32:19.770000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "a8994ecf-963b-435d-9e35-8e38eb45d5ab",
                "start": "2026-10-27T14:30:44.7568006Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T14:26:27.2866667Z",
                "error": {
                  "errorCode": "2011",
                  "isRetriable": false,
                  "message": "Operation on target round22_controlled_failure_before_original_activities failed: Round22 controlled fixture failure before original activities",
                  "requestId": "88130a95-90a7-4b24-abc3-eb8fab6590c4"
                },
                "rows_read": null,
                "rows_written": null,
                "run_id": "8103a7b4-4136-4bfc-a5e6-4078dd9e892e",
                "start": "2026-10-27T14:25:59.8066667Z",
                "status": "FAILED"
              },
              {
                "end": "2026-10-27T10:00:53.300000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "8e1cf5d1-e85a-43c2-868b-96ce2fb8c642",
                "start": "2026-10-27T09:59:00.1416513Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:49:39.5966667Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "9de05a98-7bb2-4966-bf45-346e100911a2",
                "start": "2026-10-27T09:48:15.0062065Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:42:27.810000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "6dacd836-4bd5-4dfb-b473-152b42433dfe",
                "start": "2026-10-27T09:40:56.3600702Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T09:28:59.8010875Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "b4700038-6acd-4df9-9f28-b58802350eac",
                "start": "2026-10-27T09:27:26.9017088Z",
                "status": "SUCCEEDED"
              },
              {
                "end": "2026-10-27T08:54:46.820000Z",
                "error": null,
                "rows_read": null,
                "rows_written": null,
                "run_id": "02d91840-2038-445f-bcad-3b5762ab0d04",
                "start": "2026-10-27T08:44:36.8141962Z",
                "status": "SUCCEEDED"
              }
            ],
            "rows_read": 360,
            "rows_written": 360,
            "run_id": "b19be888-92f6-4c34-81bc-0a3433cb578b",
            "start": "2026-10-28T08:15:49.4748707Z",
            "status": "SUCCEEDED"
          }
        }
      ]
    },
    {
      "check": "LAYER_FRESHNESS",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:LAYER_FRESHNESS",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SOURCE_CHANGES",
      "detail": "FRESH_PATH_FACT_NOT_AVAILABLE:SOURCE_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "cached": false,
      "check": "NEXT_LOAD",
      "observed_at": "2026-10-28T09:30:26.507600Z",
      "source": "facts-ledger",
      "state": "OBSERVED",
      "value": [
        {
          "collected_at": "2026-10-28T09:30:49.081614Z",
          "freshness": "CURRENT",
          "id": "aebe8a323d413931f58e0863ca76729102b846baeb5c0f27d1653de177251072",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:30:49.081614Z",
          "provenance": {
            "collector": "microsoft-runtime:760ed377e2f865e9fedbfa20799364e7e4367d4fc476d2be3066b7d19e89191e",
            "evidence_ids": [
              "sha256:4eb0cc5e3adbca145503837894c1710d752e9333b2b09e4925a6bd4cf716f096"
            ],
            "locator": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5",
          "value": {
            "enabled": false,
            "native_schedule": {
              "@odata.context": "https://wabi-india-central-a-primary-redirect.analysis.windows.net/v1.0/myorg/groups/149f8d99-1c66-4a0a-9624-759be002bb60/$metadata#Microsoft.PowerBI.ServiceContracts.Api.V1.RefreshSchedule",
              "days": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
              ],
              "enabled": false,
              "localTimeZoneId": "UTC",
              "notifyOption": "MailOnFailure",
              "times": [
                "01:00"
              ]
            },
            "next_due": null,
            "previous_due": null
          }
        },
        {
          "collected_at": "2026-10-28T09:30:26.507600Z",
          "freshness": "CURRENT",
          "id": "1c57c7c9a5ecc9e42ee65a57a5283a2801d4691614dd8d33286105a7e7c66a28",
          "kind": "SCHEDULE",
          "observed_at": "2026-10-28T09:30:26.507600Z",
          "provenance": {
            "collector": "microsoft-runtime:50ed9389d7d5682c8f2f36c6c2f43a2a3731a84b0c91204d9e25890e096564dc",
            "evidence_ids": [
              "sha256:8ed491b5b49159ab0f9acc555f6dbcaeeaab2220e3c3ece0f918532c45e51563"
            ],
            "locator": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba"
          },
          "reason": null,
          "source": "RUNTIME_OBSERVATION",
          "state": "OBSERVED",
          "subject": "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
          "value": {
            "native_schedules": {
              "value": []
            },
            "next_due": null,
            "reason": "Job schedule recurrence retained; unsupported recurrence types remain a named coverage gap."
          }
        }
      ]
    },
    {
      "check": "CONNECTION_MODE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:CONNECTION_MODE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "SECURITY_PRESENCE",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:SECURITY_PRESENCE",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    },
    {
      "check": "DEFINITION_CHANGES",
      "detail": "CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:DEFINITION_CHANGES",
      "observed_at": null,
      "previous": null,
      "reason": "ValueError",
      "source": null,
      "state": "UNAVAILABLE"
    }
  ],
  "path": [
    "04338ce830d63e3ab63d30a827b752e9163a7a50c36a3a8e2b6127b0480e5a34",
    "114f64a965934e8f034687583f17f05e5c8bfddf3d771753eecddd0020920222",
    "2780f358d5d1d2020da83986f3c092484c455eae1568e6f3517d35bf445a6c9c",
    "3334860e93f6632b17abd31fc175afe2ba07e7918ba0fda5cc6d5bcab485d210",
    "3bf74ae1043c1b528ef21a56ec14c7db29b4b94146434091a4149048762356ba",
    "47e39c36abbe4f68aacfcbc1f468c7090869b3d983942f8aeeade9e2b19d16ff",
    "497b809aab319a091c08598988a6c8202715e5629e01a5d8b6be448d45edd062",
    "4bc2a3e5f557b5591acd4ef788526cf6b3daac89f9d641094861d2f219033083",
    "5534dcab52ea12e3a590fc6ad8d7e5fa79ca8611cc06be894a80b65f6fe792ce",
    "569a3aaab8bae720214d342c6dfbaf14ccaaa08ce8faf3fb5da731023b3dd457",
    "5cc53633c459f46f51ae8362fdb549d859ecfe8e6f8dc9676764a9dde91241b4",
    "6630d959e13cb9cf8dea911895e20b36663b68717d40b5ed511376caa31912c6",
    "6e29c19610d2451365f4424018e56a87b8702eb485f499cad6349e1810ac5f54",
    "7334e052ba13d44cd117f9d5027516b2b1d52a38ee2983984ab2da06d54a2d1c",
    "77dca8a7a87c321d590c91d9b5dce32583bfa7913a30d3f22103016bb630985a",
    "7c4042009085cafc8ca9e5985af173de9af07bd6f919c9bb16d195e45b177dc2",
    "98be0634236a82a68e454d0e412716413cb967afd7244820b176c58d5da08707",
    "aa287d7cf4522d7100e8b12742bf7a826862d71bc1a8b43f22ab12d49a0d0a0d",
    "e90cca5c02d187ae130fcb29bd7769aa732b2e23c08cd18c311d93afbd1dd4f5"
  ],
  "refresh_operations": 8,
  "what_triage_suggests": "Triage has unavailable checks (AUTOMATIC_UPDATES, LAYER_FRESHNESS, SOURCE_CHANGES, CONNECTION_MODE, SECURITY_PRESENCE, DEFINITION_CHANGES); this does not establish that those mechanisms are absent."
}
```

Tool decisions:
```json
[
  {
    "arguments": {
      "key": "movement900099",
      "queries": [
        {
          "key_field": "movement_id",
          "kind": "sql",
          "layer": "native:9e3796a26d8d5c1a039e",
          "query": "SELECT movement_id, warehouse_id, product_id, units, event_day, movement_type, source_modified_at_utc FROM [app].[stock_movements_round_two_20261003] WHERE movement_id = 900099"
        },
        {
          "key_field": "movement_id",
          "kind": "sql",
          "layer": "native:e95b94fd338e7086320f",
          "query": "SELECT movement_id, warehouse_id, product_id, units, event_day, movement_type, source_modified_at_utc FROM [dbo].[stock_movements_round_two_20261003] WHERE movement_id = 900099"
        },
        {
          "key_field": "movement_id",
          "kind": "dax",
          "layer": "native:4caf47d120d4fd198ffe",
          "query": "EVALUATE FILTER('Movements', 'Movements'[movement_id] = 900099)"
        }
      ]
    },
    "tool": "record_trace"
  },
  {
    "arguments": {
      "layer": "native:9e3796a26d8d5c1a039e",
      "purpose": "lookup",
      "query": "SELECT COUNT(*) AS rows_observed, MIN(movement_id) AS min_id, MAX(movement_id) AS max_id, SUM(CASE WHEN event_day LIKE '2026-09-1%' THEN 1 ELSE 0 END) AS rows_sep_10_19, MIN(event_day) AS min_day, MAX(event_day) AS max_day FROM [app].[stock_movements_round_two_20261003]"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "layer": "native:e95b94fd338e7086320f",
      "purpose": "lookup",
      "query": "SELECT COUNT(*) AS rows_observed, MIN(movement_id) AS min_id, MAX(movement_id) AS max_id FROM [dbo].[stock_movements_round_two_20261003]"
    },
    "tool": "run_sql"
  },
  {
    "arguments": {
      "layer": "native:4caf47d120d4fd198ffe",
      "purpose": "lookup",
      "query": "EVALUATE ROW(\"rows\", COUNTROWS('Movements'), \"min_id\", MIN('Movements'[movement_id]), \"max_id\", MAX('Movements'[movement_id]))"
    },
    "tool": "run_dax"
  },
  {
    "arguments": {
      "cause": "I couldn't find movement900099 (movement_id 900099) anywhere along the declared path. It isn't in the application source table app.stock_movements_round_two_20261003 (ordersops), and it isn't in the landing lakehouse table dbo.stock_movements_round_two_20261003 either. The Movements table, which feeds the Movement Units measure and visual, doesn't have it. None of these lookups returned duplicates, errors or truncated results. All three layers currently hold the same 360 rows with movement IDs 1 to 360, and the application source covers event days 2026-09-10 to 2026-09-18. So no load or model step dropped the record. The source system doesn't have it now. These were reads of current rows only, so they can't show whether the record existed earlier and was later removed. Load runs: the latest audited application load ran from 2026-10-28 08:15:49 to 08:17:21 UTC and succeeded, reading 360 rows and writing 360. An earlier run at 05:59 UTC failed (error 2011, a controlled fixture failure before the original activities), but later runs succeeded. The latest Copy Job run, 08:16:11 to 08:16:41 UTC, and the latest model refresh, 08:22:02 to 08:22:28 UTC, also succeeded.",
      "checked": [
        "native:9e3796a26d8d5c1a039e",
        "native:e95b94fd338e7086320f",
        "native:4caf47d120d4fd198ffe"
      ],
      "evidence_ids": [
        "case-evidence:17d30c300c6eac8683206b2b98acc1ab4f8e293e6c3cb73cc935390b3f538da4",
        "case-evidence:d64b11b560864f763c45755a300a83f158d75080bfe167f3f9bdbe8653875d9e",
        "case-evidence:98531dc7b7205fa68ba724cdb28f051c16c875b1fe0f644f59b2b43557310757",
        "case-evidence:9abb4662ae4893a7e61ad39ac34cd82cace05230296ea248a6e62433074285f6",
        "case-evidence:00bd10391e5946d74270b7e6f9535476277ad33927526533d595ab0b08a73044"
      ],
      "numbers": [
        900099,
        0,
        0,
        0,
        360,
        360,
        360,
        1,
        360
      ],
      "verdict": "not found"
    },
    "tool": "submit_finding"
  },
  {
    "arguments": {
      "cause": "I couldn't find movement900099 (movement_id 900099) anywhere along the declared path. It isn't in the application source table app.stock_movements_round_two_20261003 (ordersops), and it isn't in the landing lakehouse table dbo.stock_movements_round_two_20261003 either. The Movements table, which feeds the Movement Units measure and visual, doesn't have it. None of these lookups returned duplicates, errors or truncated results. All three layers currently hold the same 360 rows with movement IDs 1 to 360, and the application source covers event days 2026-09-10 to 2026-09-18. So no load or model step dropped the record. The source system doesn't have it now. These were reads of current rows only, so they can't show whether the record existed earlier and was later removed. Load runs: the latest audited application load ran from 2026-10-28 08:15:49 to 08:17:21 UTC and succeeded, reading 360 rows and writing 360. An earlier run at 05:59 UTC failed (error 2011, a controlled fixture failure before the original activities), but later runs succeeded. The latest Copy Job run, 08:16:11 to 08:16:41 UTC, and the latest model refresh, 08:22:02 to 08:22:28 UTC, also succeeded.",
      "checked": [
        "native:9e3796a26d8d5c1a039e",
        "native:e95b94fd338e7086320f",
        "native:4caf47d120d4fd198ffe"
      ],
      "evidence_ids": [
        "case-evidence:17d30c300c6eac8683206b2b98acc1ab4f8e293e6c3cb73cc935390b3f538da4",
        "case-evidence:d64b11b560864f763c45755a300a83f158d75080bfe167f3f9bdbe8653875d9e",
        "case-evidence:98531dc7b7205fa68ba724cdb28f051c16c875b1fe0f644f59b2b43557310757",
        "case-evidence:9abb4662ae4893a7e61ad39ac34cd82cace05230296ea248a6e62433074285f6",
        "case-evidence:00bd10391e5946d74270b7e6f9535476277ad33927526533d595ab0b08a73044"
      ],
      "numbers": [
        0,
        0,
        0,
        360,
        360,
        360,
        1,
        360
      ],
      "verdict": "not found"
    },
    "tool": "submit_finding"
  }
]
```

Queries:
```json
[
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 5.494409730999905,
    "executed_text": "SELECT TOP 251 [stock_movements_round_two_20261003].[movement_id] AS [movement_id], [stock_movements_round_two_20261003].[warehouse_id] AS [warehouse_id], [stock_movements_round_two_20261003].[product_id] AS [product_id], [stock_movements_round_two_20261003].[units] AS [units], [stock_movements_round_two_20261003].[event_day] AS [event_day], [stock_movements_round_two_20261003].[movement_type] AS [movement_type], [stock_movements_round_two_20261003].[source_modified_at_utc] AS [source_modified_at_utc] FROM [app].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003] WHERE [stock_movements_round_two_20261003].[movement_id] = CAST(@p0 AS BIGINT)",
    "id": "query:bdedfe48009b34298fc1bf0731481d8a2df82358caebb949cb38358392592d5e:1",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [
      {
        "name": "@p0",
        "value": "900099"
      }
    ],
    "purpose": "record",
    "result": {
      "column_types": {
        "event_day": "String",
        "movement_id": "Int64",
        "movement_type": "String",
        "product_id": "Int64",
        "source_modified_at_utc": "DateTime",
        "units": "Int64",
        "warehouse_id": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T09:31:15.720167+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T09:31:11.028484+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": []
    },
    "result_digest": "41a3a4aa81b95533dbf8a2c0c58f2057b4b7131d2d60d388f7a7c12c36d21459",
    "row_count": 0,
    "signature": "bdedfe48009b34298fc1bf0731481d8a2df82358caebb949cb38358392592d5e",
    "status": "SUCCEEDED",
    "text": "SELECT movement_id, warehouse_id, product_id, units, event_day, movement_type, source_modified_at_utc FROM [app].[stock_movements_round_two_20261003] WHERE movement_id = 900099",
    "time": "2026-10-28T09:31:10.518451+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003"
    ],
    "duration_seconds": 7.729615850003029,
    "executed_text": "SELECT TOP 251 [stock_movements_round_two_20261003].[movement_id] AS [movement_id], [stock_movements_round_two_20261003].[warehouse_id] AS [warehouse_id], [stock_movements_round_two_20261003].[product_id] AS [product_id], [stock_movements_round_two_20261003].[units] AS [units], [stock_movements_round_two_20261003].[event_day] AS [event_day], [stock_movements_round_two_20261003].[movement_type] AS [movement_type], [stock_movements_round_two_20261003].[source_modified_at_utc] AS [source_modified_at_utc] FROM [dbo].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003] WHERE [stock_movements_round_two_20261003].[movement_id] = CAST(@p0 AS BIGINT)",
    "id": "query:020aa8165ca0133cf8757ee88d18b6c6d3ca248625ac2234cc20682a9b017fe8:2",
    "layer": "native:e95b94fd338e7086320f",
    "parameters": [
      {
        "name": "@p0",
        "value": "900099"
      }
    ],
    "purpose": "record",
    "result": {
      "column_types": {
        "event_day": "String",
        "movement_id": "Int64",
        "movement_type": "String",
        "product_id": "Int64",
        "source_modified_at_utc": "DateTime",
        "units": "Int64",
        "warehouse_id": "Int64"
      },
      "execution_identity": {
        "database": "round_two_bronze_20261003",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": []
    },
    "result_digest": "e6391919c0d9f64cebad618f448013b4abc781f488355851c8cd8392689f0a65",
    "row_count": 0,
    "signature": "020aa8165ca0133cf8757ee88d18b6c6d3ca248625ac2234cc20682a9b017fe8",
    "status": "SUCCEEDED",
    "text": "SELECT movement_id, warehouse_id, product_id, units, event_day, movement_type, source_modified_at_utc FROM [dbo].[stock_movements_round_two_20261003] WHERE movement_id = 900099",
    "time": "2026-10-28T09:31:16.022664+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements",
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/movement_id"
    ],
    "duration_seconds": 6.145039356997586,
    "executed_text": "EVALUATE TOPN(251,FILTER('Movements','Movements'[movement_id] = 900099))",
    "id": "query:d7db8db53326dd8f00c6a1855dc98b93442628dedb2d2dd655f5a5deea788a4c:3",
    "layer": "native:4caf47d120d4fd198ffe",
    "parameters": [],
    "purpose": "record",
    "result": {
      "rows": [],
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "6d8473f198d04906aa4cffdd9011fc4eb28edf41a038dcf583a1257c21213a1f",
    "row_count": 0,
    "signature": "d7db8db53326dd8f00c6a1855dc98b93442628dedb2d2dd655f5a5deea788a4c",
    "status": "SUCCEEDED",
    "text": "EVALUATE FILTER('Movements', 'Movements'[movement_id] = 900099)",
    "time": "2026-10-28T09:31:23.758693+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements",
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/0c89889c-6fe6-49ab-91e9-4b00a51070e6/table/Movements/columns/movement_id"
    ],
    "duration_seconds": 4.193634477996966,
    "executed_text": "EVALUATE TOPN(251,ROW(\"rows\",COUNTROWS('Movements'),\"min_id\",MIN('Movements'[movement_id]),\"max_id\",MAX('Movements'[movement_id])))",
    "id": "query:86d78a40e34596f1fb18fe2c0bb953642422048783e2d7c40cb324f17311fe3d:4",
    "layer": "native:4caf47d120d4fd198ffe",
    "parameters": [],
    "purpose": "lookup",
    "result": {
      "rows": [
        {
          "[max_id]": 360,
          "[min_id]": 1,
          "[rows]": 360
        }
      ],
      "warnings": [
        "attestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
      ]
    },
    "result_digest": "477428a6ad04b6e2975fb40952c902b71667173c7c4264acf3dd62db7616a4c7",
    "row_count": 1,
    "signature": "86d78a40e34596f1fb18fe2c0bb953642422048783e2d7c40cb324f17311fe3d",
    "status": "SUCCEEDED",
    "text": "EVALUATE ROW(\"rows\", COUNTROWS('Movements'), \"min_id\", MIN('Movements'[movement_id]), \"max_id\", MAX('Movements'[movement_id]))",
    "time": "2026-10-28T09:31:39.290682+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945"
    ],
    "duration_seconds": 4.326621673993941,
    "executed_text": "SELECT TOP 251 COUNT(*) AS [rows_observed], MIN([stock_movements_round_two_20261003].[movement_id]) AS [min_id], MAX([stock_movements_round_two_20261003].[movement_id]) AS [max_id], SUM(CASE WHEN [stock_movements_round_two_20261003].[event_day] LIKE @p2 THEN CAST(@p1 AS BIGINT) ELSE CAST(@p0 AS BIGINT) END) AS [rows_sep_10_19], MIN([stock_movements_round_two_20261003].[event_day]) AS [min_day], MAX([stock_movements_round_two_20261003].[event_day]) AS [max_day] FROM [app].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003]",
    "id": "query:7b82cdff3968eaaf49804da41169919d69a79119b6539fa7276565ff4db5e308:4",
    "layer": "native:9e3796a26d8d5c1a039e",
    "parameters": [
      {
        "name": "@p0",
        "value": "0"
      },
      {
        "name": "@p1",
        "value": "1"
      },
      {
        "name": "@p2",
        "value": "2026-09-1%"
      }
    ],
    "purpose": "lookup",
    "result": {
      "column_types": {
        "max_day": "String",
        "max_id": "Int64",
        "min_day": "String",
        "min_id": "Int64",
        "rows_observed": "Int64",
        "rows_sep_10_19": "Int64"
      },
      "connection_attempts": [
        {
          "attempt": 1,
          "finished_at": "2026-10-28T09:31:43.533854+00:00",
          "retry_delay_seconds": 0,
          "sql_error_number": null,
          "stage": null,
          "started_at": "2026-10-28T09:31:39.708524+00:00",
          "status": "SUCCEEDED"
        }
      ],
      "execution_identity": {
        "database": "ordersops",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@aeb4d0a9-e637-4a7e-8efc-63cf0c3827df",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "sql-orderops-9696025.database.windows.net"
      },
      "read_only_verified": true,
      "rows": [
        {
          "max_day": "2026-09-18",
          "max_id": "360",
          "min_day": "2026-09-10",
          "min_id": "1",
          "rows_observed": "360",
          "rows_sep_10_19": "360"
        }
      ]
    },
    "result_digest": "eb69340eb91d268067bb04de3a0f48de7a4e335af55fe8318ef0f4af00aa6622",
    "row_count": 1,
    "signature": "7b82cdff3968eaaf49804da41169919d69a79119b6539fa7276565ff4db5e308",
    "status": "SUCCEEDED",
    "text": "SELECT COUNT(*) AS rows_observed, MIN(movement_id) AS min_id, MAX(movement_id) AS max_id, SUM(CASE WHEN event_day LIKE '2026-09-1%' THEN 1 ELSE 0 END) AS rows_sep_10_19, MIN(event_day) AS min_day, MAX(event_day) AS max_day FROM [app].[stock_movements_round_two_20261003]",
    "time": "2026-10-28T09:31:39.283124+00:00",
    "truncated": false
  },
  {
    "asset_ids": [
      "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.stock_movements_round_two_20261003"
    ],
    "duration_seconds": 8.132655027002329,
    "executed_text": "SELECT TOP 251 COUNT(*) AS [rows_observed], MIN([stock_movements_round_two_20261003].[movement_id]) AS [min_id], MAX([stock_movements_round_two_20261003].[movement_id]) AS [max_id] FROM [dbo].[stock_movements_round_two_20261003] AS [stock_movements_round_two_20261003]",
    "id": "query:bd3dc0bb94a59083be9892833d31051306074463d15a54ba7ed841b6218a8237:4",
    "layer": "native:e95b94fd338e7086320f",
    "parameters": [],
    "purpose": "lookup",
    "result": {
      "column_types": {
        "max_id": "Int64",
        "min_id": "Int64",
        "rows_observed": "Int64"
      },
      "execution_identity": {
        "database": "round_two_bronze_20261003",
        "principal": "531419ef-1610-415a-b8bf-01a4b6aad751@dff91047-ebc2-4657-8dbe-5af328d57780",
        "provenance": "TRANSPORT_PERMISSION_CHECK",
        "server": "i4iptx6c5nlundn6llzsrvlxqa-tggz6fdgdqfevfreown6aav3ma.datawarehouse.fabric.microsoft.com"
      },
      "read_only_verified": true,
      "rows": [
        {
          "max_id": "360",
          "min_id": "1",
          "rows_observed": "360"
        }
      ]
    },
    "result_digest": "6300685427a817bfc1fc050363abfc5e18984ba73277afbc3d296dd122e83d7a",
    "row_count": 1,
    "signature": "bd3dc0bb94a59083be9892833d31051306074463d15a54ba7ed841b6218a8237",
    "status": "SUCCEEDED",
    "text": "SELECT COUNT(*) AS rows_observed, MIN(movement_id) AS min_id, MAX(movement_id) AS max_id FROM [dbo].[stock_movements_round_two_20261003]",
    "time": "2026-10-28T09:31:39.289319+00:00",
    "truncated": false
  }
]
```

Final answer:
```json
"not found. I couldn't find movement900099 (movement_id 900099) anywhere along the declared path. It isn't in the application source table app.stock_movements_round_two_20261003 (ordersops), and it isn't in the landing lakehouse table dbo.stock_movements_round_two_20261003 either. The Movements table, which feeds the Movement Units measure and visual, doesn't have it. None of these lookups returned duplicates, errors or truncated results. All three layers currently hold the same 360 rows with movement IDs 1 to 360, and the application source covers event days 2026-09-10 to 2026-09-18. So no load or model step dropped the record. The source system doesn't have it now. These were reads of current rows only, so they can't show whether the record existed earlier and was later removed. Load runs: the latest audited application load ran from 2026-10-28 08:15:49 to 08:17:21 UTC and succeeded, reading 360 rows and writing 360. An earlier run at 05:59 UTC failed (error 2011, a controlled fixture failure before the original activities), but later runs succeeded. The latest Copy Job run, 08:16:11 to 08:16:41 UTC, and the latest model refresh, 08:22:02 to 08:22:28 UTC, also succeeded.\nNumbers: 0, 0, 0, 360, 360, 360, 1, 360.\nChecked: ordersops, round_two_bronze_20261003, Application load fixture 20261003.\nNative comparisons are observational snapshots; aligned query-bound versions are not established.\nCatalog bookkeeping unavailable: collector containment (recovered from literal native address), current inventory availability, inventory content hashes (metadata digests are derived and labelled), inventory provenance, per-asset collector timestamps. This does not block investigation; successful queries establish present readability only.\nattestation limited: the engine can’t self-report the calling principal; the token and connection were verified separately"
```

Sealed expected:
```json
{
  "basis": "Native scenario observations verified before sealing; same fact-based class contract as sealed v2 dev template v2-record-absent-everywhere-v1. No DIA output used to author wording or expectations.",
  "case_id": "v3-record-absent-everywhere",
  "cause": "Record900099 is absent at source and every compared reachable layer; BLANK is not zero.",
  "estate": "fixture",
  "expectation_basis": "Practice source literals, declared definitions and reversible scenario plan; never an engine answer.",
  "fixture": "baseline",
  "id": "v3-record-absent-everywhere",
  "layer": "source application",
  "split": "HELD_OUT_V3",
  "variation": "independent new held-out v3",
  "verdict": "as designed"
}
```
