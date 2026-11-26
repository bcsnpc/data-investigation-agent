# Estate templating audit

2026-11-25. Inventory only; no runtime or template changes were made for this audit. Scope: every tracked code/configuration/prompt/test/infrastructure file with a recognized estate identifier, address, connection or fixture literal. Historical evidence and sealed sets are excluded. Each row points to the original line rather than copying a possibly sensitive connection string. Generic words are deliberately over-inclusive; inspect the line before deciding it needs a template parameter. Dynamic values without a literal cannot be identified by this scan.

Estate configuration belongs in the installation manifest. Identity IDs and Key Vault references belong in deployment identity configuration; secret values stay in Key Vault. Resource names belong in infrastructure parameters. Synthetic fixtures belong in test data and never determine a client route.

Occurrences: estate config: 1001, identity/secrets: 85, infrastructure: 271, test-only: 2925.

## estate config

| Source | Matched identifier or marker |
|---|---|
| config/permission-map.yaml:27 | id-dia |
| config/permission-map.yaml:41 | orderops_investigator |
| config/permission-map.yaml:61 | billingapp |
| config/permission-map.yaml:72 | fixture |
| config/permission-map.yaml:74 | 149f8d99-1c66-4a0a-9624-759be002bb60 |
| config/permission-map.yaml:77 | fixture |
| config/permission-map.yaml:84 | fixture |
| config/permission-map.yaml:86 | 149f8d99-1c66-4a0a-9624-759be002bb60 |
| config/permission-map.yaml:89 | fixture |
| config/permission-map.yaml:96 | fixture |
| config/permission-map.yaml:98 | fixture |
| config/permission-map.yaml:101 | fixture |
| config/permission-map.yaml:108 | fixture |
| config/permission-map.yaml:110 | fixture |
| config/permission-map.yaml:113 | fixture |
| config/permission-map.yaml:121 | fixture |
| config/permission-map.yaml:123 | fixture |
| config/permission-map.yaml:126 | fixture |
| config/permission-map.yaml:134 | fixture |
| config/permission-map.yaml:136 | fixture |
| config/permission-map.yaml:139 | fixture |
| config/permission-map.yaml:148 | fixture |
| config/permission-map.yaml:150 | fixture |
| config/permission-map.yaml:153 | fixture |
| config/permission-map.yaml:161 | fixture |
| config/permission-map.yaml:163 | fixture |
| config/permission-map.yaml:166 | fixture |
| config/permission-map.yaml:177 | 7d67bb36-04f6-4182-95aa-da5d515248fa |
| config/permission-map.yaml:189 | 7d67bb36-04f6-4182-95aa-da5d515248fa |
| config/permission-map.yaml:276 | d028fa2b-0d1b-4dd8-b423-37dd161cd5d0 |
| config/permission-map.yaml:288 | d028fa2b-0d1b-4dd8-b423-37dd161cd5d0 |
| config/permission-map.yaml:373 | fixture |
| config/permission-map.yaml:375 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e, powerbi:// |
| config/permission-map.yaml:378 | fixture |
| config/permission-map.yaml:386 | fixture |
| config/permission-map.yaml:388 | 2f322058-f720-40a0-bd1e-d174b8e7f5da |
| config/permission-map.yaml:391 | fixture |
| config/permission-map.yaml:398 | fixture |
| config/permission-map.yaml:400 | 2f322058-f720-40a0-bd1e-d174b8e7f5da |
| config/permission-map.yaml:401 | fixed-identity |
| config/permission-map.yaml:403 | fixture |
| config/permission-map.yaml:413 | 7d67bb36-04f6-4182-95aa-da5d515248fa, c6c1091c-3bde-46ca-94fc-58f62d1e4188, powerbi:// |
| config/permission-map.yaml:425 | 5099b9ff-1f27-488c-98c5-01c030dc4f3c |
| config/permission-map.yaml:437 | 5099b9ff-1f27-488c-98c5-01c030dc4f3c |
| config/permission-map.yaml:438 | fixed-identity |
| config/permission-map.yaml:448 | ordersops |
| config/permission-map.yaml:450 | database.windows.net, ordersops, sql-orderops |
| config/permission-map.yaml:453 | fixture |
| config/permission-map.yaml:460 | ordersops |
| config/permission-map.yaml:462 | database.windows.net, ordersops, sql-orderops |
| config/permission-map.yaml:465 | fixture |
| config/permission-map.yaml:473 | billingapp |
| config/permission-map.yaml:475 | billingapp, database.windows.net, sql-orderops |
| config/permission-map.yaml:485 | billingapp |
| config/permission-map.yaml:487 | billingapp, database.windows.net, sql-orderops |
| config/permission-map.yaml:829 | 531419ef-1610-415a-b8bf-01a4b6aad751 |
| config/permission-map.yaml:855 | orderops_investigator |
| config/permission-map.yaml:881 | 2dd2f5c3-f7af-4804-b79e-6019e63efa60 |
| config/permission-map.yaml:894 | ddd4d3cf-9cfd-440e-ac5b-be127caa46ea |
| docs/prompts.md:45 | fixture |
| docs/prompts.md:50 | fixture |
| docs/prompts.md:815 | semantic model |
| docs/prompts.md:984 | fixture |
| docs/prompts.md:989 | fixture |
| docs/prompts.md:2262 | semantic model |
| docs/prompts.md:2638 | fixture |
| docs/prompts.md:2643 | fixture |
| docs/prompts.md:4008 | semantic model |
| docs/prompts.md:4385 | fixture |
| scripts/audit_directlake_bridge.py:7 | lakehouse |
| scripts/audit_directlake_bridge.py:20 | fixture |
| scripts/audit_directlake_bridge.py:24 | workspace/ |
| scripts/audit_directlake_bridge.py:40 | lakehouse |
| scripts/audit_intake_ground_truth.py:41 | warehouse |
| scripts/audit_lineage_tape.py:65 | lakehouse |
| scripts/build_powerbi_model.py:73 | SemanticModel |
| scripts/build_powerbi_model.py:77 | SemanticModel |
| scripts/build_powerbi_reports.py:23 | powerbi:// |
| scripts/build_powerbi_reports.py:98 | semantic_model |
| scripts/check_model_freshness.py:21 | SemanticModel |
| scripts/check_model_scores.py:47 | fixture |
| scripts/cloud_guided_investigator.py:237 | Lakehouse, lakehouse, warehouse |
| scripts/cloud_guided_investigator.py:238 | workspaces/ |
| scripts/cloud_offline_worker.py:43 | fixture |
| scripts/cloud_value_mapping.py:45 | Warehouse |
| scripts/cloud_value_mapping.py:47 | WAREHOUSE |
| scripts/cloud_value_mapping.py:57 | WAREHOUSE |
| scripts/cloud_value_mapping.py:61 | WAREHOUSE |
| scripts/cloud_value_mapping.py:63 | lakehouse |
| scripts/cloud_value_mapping.py:64 | LAKEHOUSE |
| scripts/cloud_value_mapping.py:66 | lakehouse |
| scripts/cloud_value_mapping.py:67 | LAKEHOUSE |
| scripts/cloud_value_mapping.py:86 | Lakehouse, Warehouse |
| scripts/cloud_value_mapping.py:117 | Lakehouse |
| scripts/cloud_value_mapping.py:118 | Lakehouse |
| scripts/cloud_value_mapping.py:121 | Lakehouse |
| scripts/cloud_value_mapping.py:132 | Warehouse |
| scripts/collect_lineage_evidence.py:15 | lakehouse |
| scripts/collect_lineage_evidence.py:18 | Lakehouse, lakehouse |
| scripts/collect_lineage_evidence.py:24 | lakehouse, workspaces/ |
| scripts/collect_report_metadata.py:21 | SemanticModel |
| scripts/collect_report_metadata.py:22 | SemanticModel |
| scripts/collect_snapshot_lineage.py:17 | lakehouse |
| scripts/connect_fixture_reader.py:1 | fixture |
| scripts/connect_fixture_reader.py:26 | fixture |
| scripts/connect_fixture_reader.py:75 | fixture |
| scripts/connect_fixture_reader.py:89 | fixture |
| scripts/connect_fixture_reader.py:113 | fixture |
| scripts/cross_layer_investigation.py:97 | Lakehouse, lakehouse |
| scripts/cross_layer_investigation.py:98 | semantic_model |
| scripts/cross_layer_investigation.py:147 | semantic_model |
| scripts/cross_layer_investigation.py:149 | lakehouse, workspaces/ |
| scripts/deploy_gold_notebook.py:13 | lakehouse |
| scripts/deploy_gold_notebook.py:14 | lakehouse |
| scripts/deploy_gold_notebook.py:19 | lakehouse |
| scripts/deploy_gold_notebook.py:20 | lakehouse |
| scripts/deploy_gold_notebook.py:24 | workspaces/ |
| scripts/deploy_powerbi.py:1 | semantic model |
| scripts/deploy_powerbi.py:17 | workspaces/ |
| scripts/deploy_powerbi.py:23 | workspaces/ |
| scripts/deploy_powerbi.py:25 | workspaces/ |
| scripts/deploy_powerbi.py:39 | SemanticModel |
| scripts/deploy_reporting_dimensions.py:8 | ordersops |
| scripts/deploy_reporting_dimensions.py:9 | lakehouse |
| scripts/deploy_reporting_dimensions.py:13 | lakehouse |
| scripts/deploy_reporting_dimensions.py:14 | lakehouse |
| scripts/deploy_reporting_dimensions.py:17 | workspaces/ |
| scripts/deploy_reporting_dimensions.py:20 | workspaces/ |
| scripts/deploy_reporting_dimensions.py:22 | workspaces/ |
| scripts/deploy_silver_notebook.py:14 | lakehouse |
| scripts/deploy_silver_notebook.py:16 | lakehouse |
| scripts/deploy_silver_notebook.py:17 | lakehouse |
| scripts/deploy_silver_notebook.py:23 | lakehouse |
| scripts/deploy_silver_notebook.py:24 | lakehouse |
| scripts/deploy_silver_notebook.py:29 | workspaces/ |
| scripts/deploy_snapshot_publication.py:19 | lakehouse |
| scripts/deploy_snapshot_publication.py:24 | lakehouse |
| scripts/deploy_snapshot_publication.py:25 | lakehouse |
| scripts/deploy_snapshot_publication.py:29 | workspaces/ |
| scripts/deploy_snapshot_publication.py:34 | workspaces/ |
| scripts/deploy_snapshot_publication.py:36 | workspaces/ |
| scripts/deploy_snapshot_publication.py:48 | workspaces/ |
| scripts/dia.py:32 | fixture |
| scripts/dia.py:49 | fixture |
| scripts/dia.py:59 | fixture |
| scripts/dia.py:112 | fixture |
| scripts/evaluate_acceptance.py:1 | fixture |
| scripts/evaluate_acceptance.py:51 | fixture |
| scripts/evaluate_acceptance.py:52 | FIXTURE |
| scripts/evaluate_acceptance.py:54 | fixture |
| scripts/evaluate_acceptance.py:57 | fixture |
| scripts/evaluate_acceptance.py:64 | fixture |
| scripts/evaluate_acceptance.py:75 | fixture |
| scripts/evaluate_acceptance.py:98 | fixture |
| scripts/evaluate_multilayer_matrix.py:74 | fixture |
| scripts/export_synthesis_eval.py:41 | fixture |
| scripts/export_synthesis_eval.py:47 | fixture |
| scripts/export_synthesis_eval.py:52 | fixture |
| scripts/fabric_api.py:7 | 09cea7db-63ec-41f0-9cf0-872a6dc5c61d |
| scripts/fabric_sql_auth.py:15 | database.windows.net |
| scripts/fixture/apply.py:1 | fixture |
| scripts/fixture/apply.py:3 | Workspace/ |
| scripts/fixture/apply.py:4 | fixture |
| scripts/fixture/apply.py:27 | Fixture |
| scripts/fixture/apply.py:32 | fixture |
| scripts/fixture/apply.py:63 | workspaces/ |
| scripts/fixture/apply.py:67 | workspaces/ |
| scripts/fixture/apply.py:70 | Lakehouse |
| scripts/fixture/apply.py:75 | workspaces/ |
| scripts/fixture/apply.py:82 | Fixture |
| scripts/fixture/apply.py:84 | Fixture |
| scripts/fixture/apply.py:87 | workspaces/ |
| scripts/fixture/apply.py:92 | workspaces/ |
| scripts/fixture/apply.py:95 | workspaces/ |
| scripts/fixture/apply.py:100 | Fixture |
| scripts/fixture/apply.py:102 | fixture |
| scripts/fixture/apply.py:104 | lakehouse |
| scripts/fixture/apply.py:105 | warehouse |
| scripts/fixture/apply.py:124 | lakehouse |
| scripts/fixture/apply.py:126 | warehouse, workspaces/ |
| scripts/fixture/apply.py:130 | WAREHOUSE |
| scripts/fixture/apply.py:131 | WAREHOUSE |
| scripts/fixture/apply.py:132 | 20261003 |
| scripts/fixture/apply.py:152 | semanticModel |
| scripts/fixture/apply.py:154 | warehouse |
| scripts/fixture/apply.py:187 | fixture |
| scripts/fixture/apply.py:212 | 20261003 |
| scripts/fixture/apply.py:222 | fixture |
| scripts/fixture/apply.py:223 | fixture |
| scripts/fixture/apply.py:235 | fixture |
| scripts/fixture/apply.py:236 | fixture |
| scripts/fixture/apply.py:240 | fixture |
| scripts/fixture/apply.py:244 | fixture |
| scripts/fixture/apply.py:258 | Fixture |
| scripts/fixture/apply.py:263 | fixture |
| scripts/fixture/apply.py:264 | Fixture |
| scripts/fixture/apply.py:293 | FIXTURE |
| scripts/fixture/apply.py:308 | workspaces/ |
| scripts/fixture/apply.py:311 | workspaces/ |
| scripts/fixture/apply.py:322 | fixture |
| scripts/fixture/apply.py:329 | fixture |
| scripts/fixture/apply.py:334 | workspaces/ |
| scripts/fixture/apply.py:403 | workspaces/ |
| scripts/fixture/apply.py:410 | workspaces/ |
| scripts/fixture/apply.py:418 | workspaces/ |
| scripts/fixture/control.py:1 | fixture |
| scripts/fixture/control.py:15 | fixture |
| scripts/fixture/control.py:23 | Fixture |
| scripts/fixture/control.py:52 | workspaces/ |
| scripts/fixture/control.py:56 | workspace/ |
| scripts/fixture/control.py:94 | workspaces/ |
| scripts/fixture/definitions.py:1 | fixture |
| scripts/fixture/definitions.py:14 | fixture |
| scripts/fixture/definitions.py:17 | fixture |
| scripts/fixture/definitions.py:23 | fixture |
| scripts/fixture/definitions.py:35 | lakehouse |
| scripts/fixture/definitions.py:36 | lakehouse |
| scripts/fixture/definitions.py:38 | lakehouse |
| scripts/fixture/definitions.py:40 | lakehouse |
| scripts/fixture/definitions.py:41 | lakehouse |
| scripts/fixture/definitions.py:42 | WAREHOUSE |
| scripts/fixture/guided_report.py:17 | fixture |
| scripts/fixture/pipeline_runtime.py:1 | Fixture |
| scripts/fixture/pipeline_schedule.py:27 | workspaces/ |
| scripts/fixture/rebuild.py:1 | fixture |
| scripts/fixture/rebuild.py:15 | fixture |
| scripts/fixture/rebuild.py:19 | warehouse |
| scripts/fixture/rebuild.py:64 | fixture |
| scripts/fixture/rebuild.py:73 | LAKEHOUSE, fixture |
| scripts/fixture/rebuild.py:75 | fixture |
| scripts/fixture/rebuild.py:78 | LAKEHOUSE, fixture |
| scripts/fixture/rebuild.py:83 | fixture |
| scripts/fixture/rebuild.py:84 | WAREHOUSE, warehouse |
| scripts/fixture/rebuild.py:86 | lakehouse |
| scripts/fixture/rebuild.py:87 | fixture |
| scripts/fixture/rebuild.py:88 | Warehouse |
| scripts/fixture/rebuild.py:93 | fixture |
| scripts/fixture/rebuild.py:94 | fixture |
| scripts/fixture/rebuild.py:96 | warehouse |
| scripts/fixture/rebuild.py:97 | fixture |
| scripts/fixture/rebuild.py:103 | fixture |
| scripts/fixture/rebuild.py:104 | fixture |
| scripts/fixture/rebuild.py:127 | fixture |
| scripts/fixture/seed.py:1 | fixture |
| scripts/fixture/seed.py:15 | 7ccafe59-0460-4c8a-a691-bfdfa75a2b25, fixture |
| scripts/fixture/seed.py:23 | Fixture |
| scripts/fixture/seed.py:27 | Fixture |
| scripts/fixture/seed.py:33 | Fixture |
| scripts/fixture/seed.py:41 | Fixture |
| scripts/fixture/seed.py:43 | Fixture |
| scripts/fixture/seed.py:45 | Fixture |
| scripts/fixture/seed.py:47 | Fixture |
| scripts/fixture/seed.py:49 | Fixture |
| scripts/fixture/seed.py:52 | Fixture |
| scripts/fixture/seed.py:54 | Fixture |
| scripts/fixture/seed.py:56 | Fixture |
| scripts/fixture/seed.py:57 | Fixture |
| scripts/fixture/seed.py:58 | Fixture |
| scripts/fixture/seed.py:69 | Fixture |
| scripts/fixture/seed.py:73 | Fixture |
| scripts/fixture/seed.py:82 | lakehouse |
| scripts/fixture/seed.py:89 | Fixture, lakehouse |
| scripts/fixture/seed.py:90 | lakehouse |
| scripts/fixture/seed.py:91 | Fixture, lakehouse |
| scripts/fixture/seed.py:93 | Fixture |
| scripts/fixture/seed.py:97 | lakehouse |
| scripts/fixture/seed.py:99 | lakehouse |
| scripts/fixture/seed.py:103 | FIXTURE |
| scripts/fixture/source_access.py:1 | fixture |
| scripts/fixture/source_access.py:12 | dia-investigator, orderops_investigator |
| scripts/fixture/source_access.py:24 | billingapp |
| scripts/fixture/source_access.py:41 | fixture |
| scripts/fixture/source_access.py:46 | fixture |
| scripts/fixture/source_access.py:49 | billingapp |
| scripts/fixture/source_access.py:50 | fixture |
| scripts/fixture/source_access.py:54 | dia-investigator, orderops_investigator |
| scripts/fixture/source_access.py:65 | fixture |
| scripts/fixture/source_access.py:67 | fixture |
| scripts/fixture/source_access.py:68 | FIXTURE |
| scripts/fixture/source_access.py:69 | FIXTURE |
| scripts/fixture/source_access.py:74 | billingapp |
| scripts/fixture/source_access.py:76 | fixture |
| scripts/fixture/source_history.py:11 | 20261003 |
| scripts/fixture/source_history.py:12 | warehouse |
| scripts/fixture/source_history.py:60 | fixture |
| scripts/fixture/source_latency.py:1 | fixture |
| scripts/fixture/source_latency.py:12 | Fixture |
| scripts/fixture/source_latency.py:13 | fixture |
| scripts/fixture/source_latency.py:17 | FIXTURE, Fixture |
| scripts/fixture/source_latency.py:35 | 20261003 |
| scripts/fixture/source_latency.py:37 | 20261003 |
| scripts/fixture/source_latency.py:45 | fixture |
| scripts/fixture/source_latency.py:90 | Fixture |
| scripts/fixture/source_latency.py:93 | FIXTURE, Fixture |
| scripts/fixture/source_latency.py:98 | Fixture |
| scripts/fixture/source_scopes.py:7 | warehouse |
| scripts/fixture/source_temporal.py:54 | 20261003 |
| scripts/fixture/source_temporal.py:56 | 20261003 |
| scripts/fixture/source_temporal.py:112 | fixture |
| scripts/fixture/source_temporal.py:132 | fixture |
| scripts/fixture/source_temporal.py:135 | fixture |
| scripts/fixture/source_temporal.py:157 | FIXTURE |
| scripts/fixture/source_temporal.py:160 | Fixture |
| scripts/fixture/templates/application-model.json:7 | 20261003, Application load fixture, SemanticModel, fixture |
| scripts/fixture/templates/application-model.json:12 | semanticModel |
| scripts/fixture/templates/application-model.json:17 | 20261003, WAREHOUSE, warehouse |
| scripts/fixture/templates/audit-pipeline.json:41 | WAREHOUSE |
| scripts/fixture/templates/audit-pipeline.json:43 | Warehouse |
| scripts/fixture/templates/audit-pipeline.json:45 | WAREHOUSE |
| scripts/fixture/templates/copy-job.json:12 | ordersops |
| scripts/fixture/templates/copy-job.json:20 | Lakehouse |
| scripts/fixture/templates/copy-job.json:22 | Lakehouse |
| scripts/fixture/templates/copy-job.json:42 | 20261003 |
| scripts/fixture/templates/copy-job.json:53 | 20261003 |
| scripts/fixture/templates/copy-job.json:73 | warehouse |
| scripts/fixture/templates/copy-job.json:76 | warehouse |
| scripts/fixture/templates/inventory-report.json:4 | 149f8d99-1c66-4a0a-9624-759be002bb60, 692f3ead-d1d1-4f7f-984b-51e54f3e7497 |
| scripts/fixture/templates/inventory-report.json:24 | Warehouse, warehouse |
| scripts/fixture/templates/inventory-report.json:29 | Warehouse |
| scripts/fixture/templates/inventory-report.json:44 | Warehouse, warehouse |
| scripts/fixture/templates/inventory-report.json:69 | powerbi://, semanticmodel |
| scripts/fixture/templates/original-model.json:7 | SemanticModel, Warehouse |
| scripts/fixture/templates/original-model.json:12 | semanticModel |
| scripts/fixture/templates/original-model.json:17 | WAREHOUSE, Warehouse, warehouse |
| scripts/fixture/templates/predicate-report.json:7 | fixture, semantic model |
| scripts/fixture/templates/predicate-report.json:12 | warehouse |
| scripts/fixture/templates/predicate-report.json:62 | warehouse |
| scripts/fixture/templates/predicate-report.json:82 | Warehouse, fixture, powerbi://, semanticmodel |
| scripts/fixture/templates/warehouse-report.json:4 | 149f8d99-1c66-4a0a-9624-759be002bb60, 7826f034-ab61-4d8f-8125-27c1d60a73a5 |
| scripts/fixture/templates/warehouse-report.json:5 | Warehouse |
| scripts/fixture/templates/warehouse-report.json:9 | Warehouse |
| scripts/fixture/templates/warehouse-report.json:14 | Warehouse |
| scripts/fixture/templates/warehouse-report.json:34 | Warehouse, warehouse |
| scripts/fixture/templates/warehouse-report.json:39 | Warehouse |
| scripts/fixture/templates/warehouse-report.json:49 | Warehouse, warehouse |
| scripts/fixture/templates/warehouse-report.json:69 | powerbi://, semanticmodel |
| scripts/fixture_load_audit.py:1 | fixture |
| scripts/gold_snapshot_input.py:27 | lakehouse |
| scripts/gold_snapshot_input.py:31 | lakehouse |
| scripts/graph_coverage_report.py:7 | Lakehouse, Warehouse |
| scripts/import_fixture.py:1 | fixture |
| scripts/import_fixture.py:23 | Fixture |
| scripts/import_fixture.py:34 | fixture |
| scripts/import_fixture.py:59 | Fixture |
| scripts/import_fixture.py:133 | Fixture |
| scripts/import_fixture.py:141 | fixture |
| scripts/ingestion_contract.py:8 | lakehouse |
| scripts/ingestion_contract.py:10 | lakehouse |
| scripts/ingestion_contract.py:17 | lakehouse |
| scripts/intake_regression_fixture.py:1 | fixture |
| scripts/intake_regression_fixture.py:4 | fixture |
| scripts/intake_regression_fixture.py:7 | fixture |
| scripts/intake_regression_fixture.py:11 | Fixture |
| scripts/intake_regression_fixture.py:13 | fixture |
| scripts/intake_regression_fixture.py:14 | fixture |
| scripts/intake_regression_fixture.py:18 | fixture |
| scripts/investigation_query_worker.py:75 | database.windows.net, warehouse |
| scripts/investigator/acceptance_context.py:1 | fixture |
| scripts/investigator/acceptance_context.py:16 | fixture |
| scripts/investigator/acceptance_context.py:17 | fixture |
| scripts/investigator/acceptance_context.py:18 | fixture |
| scripts/investigator/acceptance_context.py:23 | fixture |
| scripts/investigator/acceptance_context.py:24 | Fixture |
| scripts/investigator/acceptance_context.py:32 | fixture |
| scripts/investigator/acceptance_context.py:33 | fixture |
| scripts/investigator/acceptance_context.py:35 | Fixture |
| scripts/investigator/acceptance_context.py:36 | Fixture |
| scripts/investigator/acceptance_context.py:39 | fixture |
| scripts/investigator/acceptance_context.py:43 | fixture |
| scripts/investigator/acceptance_context.py:46 | fixture |
| scripts/investigator/acceptance_context.py:49 | Fixture |
| scripts/investigator/acceptance_context.py:51 | fixture |
| scripts/investigator/acceptance_context.py:52 | fixture |
| scripts/investigator/acceptance_context.py:56 | fixture |
| scripts/investigator/acceptance_context.py:58 | fixture |
| scripts/investigator/acceptance_context.py:59 | fixture |
| scripts/investigator/acceptance_context.py:60 | fixture |
| scripts/investigator/acceptance_context.py:62 | fixture |
| scripts/investigator/acceptance_context.py:63 | fixture |
| scripts/investigator/acceptance_context.py:65 | fixture |
| scripts/investigator/acceptance_context.py:69 | Fixture |
| scripts/investigator/acceptance_context.py:70 | fixture |
| scripts/investigator/acceptance_context.py:73 | fixture |
| scripts/investigator/acceptance_context.py:81 | workspace/ |
| scripts/investigator/acceptance_context.py:99 | fixture |
| scripts/investigator/acceptance_context.py:120 | fixture |
| scripts/investigator/acceptance_context.py:121 | fixture |
| scripts/investigator/acceptance_context.py:123 | fixture |
| scripts/investigator/acceptance_context.py:139 | fixture |
| scripts/investigator/acceptance_context.py:146 | fixture |
| scripts/investigator/acceptance_context.py:149 | fixture |
| scripts/investigator/adapters/access_probes.py:182 | id-dia |
| scripts/investigator/adapters/access_probes.py:191 | database.windows.net |
| scripts/investigator/adapters/access_probes.py:209 | id-dia |
| scripts/investigator/adapters/ai_native_catalog.py:32 | Lakehouse, Warehouse |
| scripts/investigator/adapters/ai_native_catalog.py:42 | SemanticModel |
| scripts/investigator/adapters/ai_native_catalog.py:56 | Lakehouse, Warehouse |
| scripts/investigator/adapters/ai_native_catalog.py:155 | Lakehouse |
| scripts/investigator/adapters/ai_native_catalog.py:158 | Lakehouse |
| scripts/investigator/adapters/ai_native_catalog.py:160 | Warehouse |
| scripts/investigator/adapters/ai_native_catalog.py:252 | Warehouse |
| scripts/investigator/adapters/ai_native_catalog.py:262 | Lakehouse |
| scripts/investigator/adapters/ai_native_catalog.py:277 | Lakehouse, Warehouse |
| scripts/investigator/adapters/ai_native_catalog.py:287 | Lakehouse, Warehouse |
| scripts/investigator/adapters/ai_native_catalog.py:293 | Lakehouse, Warehouse |
| scripts/investigator/adapters/ai_native_catalog.py:369 | Lakehouse, Warehouse |
| scripts/investigator/adapters/binding_catalog.py:28 | Warehouse |
| scripts/investigator/adapters/binding_catalog.py:114 | Warehouse |
| scripts/investigator/adapters/binding_verification.py:29 | semantic-model |
| scripts/investigator/adapters/claim_projection.py:172 | Warehouse |
| scripts/investigator/adapters/code_definition.py:17 | workspaces/ |
| scripts/investigator/adapters/code_verification.py:36 | Warehouse, warehouse |
| scripts/investigator/adapters/code_verification.py:37 | warehouse |
| scripts/investigator/adapters/code_verification.py:38 | warehouse |
| scripts/investigator/adapters/code_verification.py:39 | Warehouse |
| scripts/investigator/adapters/code_verification.py:41 | warehouse |
| scripts/investigator/adapters/code_verification.py:44 | Warehouse |
| scripts/investigator/adapters/code_verification.py:47 | Warehouse |
| scripts/investigator/adapters/code_verification.py:53 | Lakehouse |
| scripts/investigator/adapters/code_verification.py:62 | lakehouse |
| scripts/investigator/adapters/connection_rotation.py:145 | fixture |
| scripts/investigator/adapters/copy_quantity.py:51 | Lakehouse |
| scripts/investigator/adapters/declared_chain.py:59 | Lakehouse |
| scripts/investigator/adapters/enrichment_stub.py:9 | fixture |
| scripts/investigator/adapters/enrichment_stub.py:14 | fixture |
| scripts/investigator/adapters/estate_graph_static.py:13 | SemanticModel |
| scripts/investigator/adapters/estate_graph_static.py:15 | Lakehouse, Warehouse |
| scripts/investigator/adapters/estate_graph_static.py:16 | Lakehouse, Warehouse |
| scripts/investigator/adapters/estate_graph_static.py:37 | Lakehouse, Warehouse |
| scripts/investigator/adapters/estate_graph_static.py:156 | SemanticModel |
| scripts/investigator/adapters/estate_graph_static.py:170 | semanticmodel |
| scripts/investigator/adapters/estate_graph_static.py:173 | SemanticModel |
| scripts/investigator/adapters/estate_graph_static.py:236 | Warehouse |
| scripts/investigator/adapters/estate_graph_static.py:291 | Warehouse |
| scripts/investigator/adapters/estate_graph_static.py:359 | SemanticModel |
| scripts/investigator/adapters/estate_graph_static.py:406 | SemanticModel |
| scripts/investigator/adapters/estate_graph_static.py:476 | Lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:491 | Lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:506 | Lakehouse, Warehouse |
| scripts/investigator/adapters/estate_graph_static.py:508 | Warehouse |
| scripts/investigator/adapters/estate_graph_static.py:510 | Lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:514 | Lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:516 | lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:526 | Lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:529 | Lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:542 | Warehouse |
| scripts/investigator/adapters/estate_graph_static.py:543 | Lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:573 | Lakehouse, Warehouse |
| scripts/investigator/adapters/estate_graph_static.py:628 | Warehouse |
| scripts/investigator/adapters/estate_graph_static.py:636 | Warehouse |
| scripts/investigator/adapters/estate_graph_static.py:642 | Warehouse |
| scripts/investigator/adapters/estate_graph_static.py:723 | lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:736 | lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:737 | Lakehouse, lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:743 | lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:746 | lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:747 | Lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:757 | Lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:765 | SemanticModel |
| scripts/investigator/adapters/estate_graph_static.py:766 | SemanticModel |
| scripts/investigator/adapters/estate_graph_static.py:771 | lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:772 | lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:773 | Lakehouse, lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:774 | lakehouse |
| scripts/investigator/adapters/estate_graph_static.py:780 | lakehouse |
| scripts/investigator/adapters/federated_reader.py:12 | database.windows.net |
| scripts/investigator/adapters/federated_reader.py:18 | fb60f99c-7a34-4190-8149-302f77469936 |
| scripts/investigator/adapters/federated_reader.py:48 | database.windows.net |
| scripts/investigator/adapters/form_candidate_values.py:79 | fixture |
| scripts/investigator/adapters/graph_change_collector.py:42 | workspaces/ |
| scripts/investigator/adapters/graph_change_collector.py:87 | SemanticModel |
| scripts/investigator/adapters/graph_change_collector.py:89 | workspaces/ |
| scripts/investigator/adapters/graph_change_collector.py:96 | SemanticModel |
| scripts/investigator/adapters/graph_change_collector.py:108 | SemanticModel |
| scripts/investigator/adapters/graph_code_columns.py:34 | Lakehouse |
| scripts/investigator/adapters/graph_code_columns.py:41 | Lakehouse |
| scripts/investigator/adapters/graph_container_schema.py:24 | Lakehouse, Warehouse |
| scripts/investigator/adapters/graph_container_schema.py:26 | Lakehouse, Warehouse |
| scripts/investigator/adapters/graph_container_schema.py:38 | Lakehouse, Warehouse |
| scripts/investigator/adapters/graph_container_schema.py:46 | Lakehouse, Warehouse |
| scripts/investigator/adapters/graph_copy_bindings.py:30 | Lakehouse, Warehouse |
| scripts/investigator/adapters/graph_dependencies.py:52 | semantic-model |
| scripts/investigator/adapters/graph_health_native.py:22 | Lakehouse, Warehouse |
| scripts/investigator/adapters/graph_script_procedures.py:11 | Warehouse |
| scripts/investigator/adapters/graph_script_procedures.py:17 | Warehouse |
| scripts/investigator/adapters/graph_script_sql.py:1 | Warehouse |
| scripts/investigator/adapters/graph_script_sql.py:11 | Warehouse, warehouse |
| scripts/investigator/adapters/graph_script_sql.py:13 | warehouse |
| scripts/investigator/adapters/graph_script_sql.py:16 | Lakehouse, Warehouse |
| scripts/investigator/adapters/graph_script_sql.py:18 | Lakehouse, Warehouse |
| scripts/investigator/adapters/graph_script_sql.py:50 | Warehouse |
| scripts/investigator/adapters/graph_sql_changes.py:63 | Warehouse |
| scripts/investigator/adapters/guided_security.py:21 | Lakehouse, SemanticModel, Warehouse |
| scripts/investigator/adapters/guided_security.py:26 | SemanticModel |
| scripts/investigator/adapters/guided_security.py:37 | workspaces/ |
| scripts/investigator/adapters/investigative_native.py:29 | FIXTURE |
| scripts/investigator/adapters/known-platform-limits.md:3 | LAKEHOUSE |
| scripts/investigator/adapters/known-platform-limits.md:4 | lakehouse |
| scripts/investigator/adapters/known-platform-limits.md:11 | Warehouse, lakehouse |
| scripts/investigator/adapters/known-platform-limits.md:12 | lakehouse |
| scripts/investigator/adapters/known-platform-limits.md:13 | lakehouse |
| scripts/investigator/adapters/known-platform-limits.md:14 | Warehouse |
| scripts/investigator/adapters/known-platform-limits.md:20 | dia-scanner |
| scripts/investigator/adapters/known-platform-limits.md:22 | Fixture |
| scripts/investigator/adapters/load_audit.py:20 | Lakehouse |
| scripts/investigator/adapters/load_audit.py:21 | LAKEHOUSE, Warehouse, lakehouse |
| scripts/investigator/adapters/load_audit.py:22 | Warehouse |
| scripts/investigator/adapters/load_audit.py:28 | warehouse |
| scripts/investigator/adapters/load_audit.py:33 | Warehouse |
| scripts/investigator/adapters/load_audit.py:40 | Warehouse |
| scripts/investigator/adapters/load_audit.py:69 | Warehouse |
| scripts/investigator/adapters/managed_identity.py:17 | database.windows.net |
| scripts/investigator/adapters/managed_identity.py:23 | database.windows.net |
| scripts/investigator/adapters/managed_identity.py:33 | cfa8b339-82a2-471a-a3c9-0fc0be7a4093 |
| scripts/investigator/adapters/microsoft_copy_mapping.py:20 | Lakehouse |
| scripts/investigator/adapters/microsoft_copy_mapping.py:92 | Lakehouse |
| scripts/investigator/adapters/microsoft_copy_mapping.py:95 | Lakehouse |
| scripts/investigator/adapters/microsoft_process.py:17 | Warehouse |
| scripts/investigator/adapters/microsoft_process.py:391 | SemanticModel |
| scripts/investigator/adapters/microsoft_process.py:429 | Lakehouse |
| scripts/investigator/adapters/microsoft_process.py:431 | warehouse |
| scripts/investigator/adapters/microsoft_process.py:432 | Warehouse, warehouse |
| scripts/investigator/adapters/microsoft_process.py:433 | warehouse |
| scripts/investigator/adapters/microsoft_process.py:434 | warehouse |
| scripts/investigator/adapters/microsoft_process.py:435 | warehouse |
| scripts/investigator/adapters/microsoft_process.py:439 | Warehouse |
| scripts/investigator/adapters/microsoft_process.py:450 | Lakehouse, Warehouse, warehouse |
| scripts/investigator/adapters/microsoft_process.py:465 | warehouse |
| scripts/investigator/adapters/microsoft_process.py:466 | WAREHOUSE |
| scripts/investigator/adapters/microsoft_process.py:467 | warehouse |
| scripts/investigator/adapters/microsoft_process.py:468 | Lakehouse, Warehouse |
| scripts/investigator/adapters/microsoft_process.py:658 | lakehouse |
| scripts/investigator/adapters/microsoft_process.py:670 | lakehouse |
| scripts/investigator/adapters/microsoft_process.py:765 | Warehouse |
| scripts/investigator/adapters/microsoft_process.py:767 | Warehouse |
| scripts/investigator/adapters/microsoft_process.py:768 | Warehouse |
| scripts/investigator/adapters/microsoft_process.py:995 | lakehouse |
| scripts/investigator/adapters/microsoft_process.py:997 | lakehouse |
| scripts/investigator/adapters/microsoft_readiness.py:99 | Semantic model, SemanticModel |
| scripts/investigator/adapters/native_catalog_projection.py:18 | Lakehouse, Warehouse |
| scripts/investigator/adapters/native_catalog_projection.py:19 | Lakehouse, Warehouse |
| scripts/investigator/adapters/native_catalog_projection.py:25 | Lakehouse, SemanticModel, Warehouse |
| scripts/investigator/adapters/platform_lineage.py:17 | Lakehouse, SemanticModel, Warehouse |
| scripts/investigator/adapters/platform_lineage.py:45 | workspaces/ |
| scripts/investigator/adapters/platform_preflight_receipts.py:56 | database.windows.net |
| scripts/investigator/adapters/platform_preflight_receipts.py:60 | database.windows.net |
| scripts/investigator/adapters/reasoning_anthropic.py:153 | fixture |
| scripts/investigator/adapters/retained_endpoints.py:22 | lakehouse |
| scripts/investigator/adapters/retained_endpoints.py:52 | lakehouse |
| scripts/investigator/adapters/retained_endpoints.py:54 | Lakehouse |
| scripts/investigator/adapters/retained_endpoints.py:58 | Lakehouse, lakehouse |
| scripts/investigator/adapters/runtime_facts_microsoft.py:99 | Warehouse |
| scripts/investigator/adapters/runtime_facts_microsoft.py:189 | workspaces/ |
| scripts/investigator/adapters/runtime_facts_microsoft.py:232 | WAREHOUSE |
| scripts/investigator/adapters/runtime_facts_microsoft.py:259 | workspaces/ |
| scripts/investigator/adapters/runtime_facts_microsoft.py:274 | WAREHOUSE |
| scripts/investigator/adapters/runtime_facts_microsoft.py:394 | workspaces/ |
| scripts/investigator/adapters/scanner_admin.py:8 | workspaces/ |
| scripts/investigator/adapters/scanner_admin.py:34 | workspaces/ |
| scripts/investigator/adapters/scanner_admin.py:37 | workspaces/ |
| scripts/investigator/adapters/scanner_identity.py:15 | database.windows.net |
| scripts/investigator/adapters/scanner_policy.py:80 | lakehouse, semanticModel, warehouse, workspaces/ |
| scripts/investigator/adapters/scanner_policy.py:97 | workspaces/ |
| scripts/investigator/adapters/scanner_policy.py:121 | workspaces/ |
| scripts/investigator/adapters/scanner_policy.py:123 | workspaces/ |
| scripts/investigator/adapters/scanner_policy.py:124 | workspaces/ |
| scripts/investigator/adapters/scanner_policy.py:125 | workspaces/ |
| scripts/investigator/adapters/scanner_policy.py:152 | workspaces/ |
| scripts/investigator/adapters/source_delivery.py:45 | lakehouse |
| scripts/investigator/adapters/vault_user_cache.py:17 | database.windows.net |
| scripts/investigator/adapters/warehouse_catalog.py:1 | Warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:8 | warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:9 | Warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:19 | warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:20 | Warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:32 | warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:35 | Warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:37 | Warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:50 | warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:53 | warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:56 | Warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:66 | warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:69 | Warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:71 | Warehouse |
| scripts/investigator/adaptive_runtime.py:668 | lakehouse, warehouse |
| scripts/investigator/adaptive_runtime.py:669 | lakehouse, warehouse |
| scripts/investigator/adaptive_runtime.py:670 | workspaces/ |
| scripts/investigator/adaptive_runtime.py:680 | warehouse |
| scripts/investigator/archive_migration.py:66 | workspace/ |
| scripts/investigator/claim_clarification.py:220 | semantic model |
| scripts/investigator/context_search.py:84 | semantic=model |
| scripts/investigator/daily_smoke.py:202 | database.windows.net |
| scripts/investigator/discovery_collect.py:28 | lakehouse, warehouse |
| scripts/investigator/discovery_collect.py:35 | warehouse |
| scripts/investigator/discovery_collect.py:36 | warehouse |
| scripts/investigator/discovery_collect.py:37 | lakehouse |
| scripts/investigator/discovery_collect.py:106 | workspaces/ |
| scripts/investigator/discovery_collect.py:119 | SemanticModel |
| scripts/investigator/discovery_collect.py:121 | workspaces/ |
| scripts/investigator/discovery_collect.py:133 | SemanticModel |
| scripts/investigator/discovery_collect.py:135 | SemanticModel |
| scripts/investigator/discovery_collect.py:138 | Lakehouse |
| scripts/investigator/discovery_collect.py:140 | lakehouse, workspaces/ |
| scripts/investigator/discovery_collect.py:145 | Lakehouse |
| scripts/investigator/discovery_collect.py:150 | Lakehouse |
| scripts/investigator/discovery_collect.py:152 | Lakehouse |
| scripts/investigator/discovery_collect.py:156 | lakehouse |
| scripts/investigator/discovery_collect.py:157 | lakehouse |
| scripts/investigator/discovery_collect.py:158 | lakehouse, workspaces/ |
| scripts/investigator/discovery_collect.py:160 | Lakehouse |
| scripts/investigator/discovery_collect.py:165 | lakehouse |
| scripts/investigator/discovery_collect.py:167 | Lakehouse |
| scripts/investigator/discovery_collect.py:170 | Lakehouse |
| scripts/investigator/discovery_collect.py:172 | Lakehouse |
| scripts/investigator/discovery_collect.py:180 | Lakehouse |
| scripts/investigator/discovery_collect.py:181 | Lakehouse |
| scripts/investigator/discovery_collect.py:182 | lakehouse |
| scripts/investigator/discovery_collect.py:183 | Warehouse |
| scripts/investigator/discovery_collect.py:184 | warehouse |
| scripts/investigator/discovery_collect.py:185 | warehouse |
| scripts/investigator/discovery_collect.py:186 | warehouse, workspaces/ |
| scripts/investigator/discovery_collect.py:188 | Warehouse |
| scripts/investigator/discovery_collect.py:191 | warehouse |
| scripts/investigator/discovery_collect.py:193 | Warehouse |
| scripts/investigator/discovery_collect.py:196 | Warehouse |
| scripts/investigator/discovery_collect.py:198 | Warehouse |
| scripts/investigator/discovery_collect.py:199 | Warehouse |
| scripts/investigator/discovery_collect.py:200 | Warehouse |
| scripts/investigator/discovery_collect.py:201 | warehouse |
| scripts/investigator/discovery_collect.py:205 | warehouse |
| scripts/investigator/discovery_collect.py:206 | warehouse |
| scripts/investigator/discovery_collect.py:208 | warehouse, workspaces/ |
| scripts/investigator/discovery_collect.py:210 | Warehouse |
| scripts/investigator/discovery_collect.py:215 | warehouse |
| scripts/investigator/discovery_collect.py:216 | Warehouse |
| scripts/investigator/discovery_collect.py:219 | Warehouse |
| scripts/investigator/discovery_collect.py:220 | Warehouse |
| scripts/investigator/discovery_collect.py:221 | warehouse |
| scripts/investigator/discovery_collect.py:224 | Warehouse |
| scripts/investigator/discovery_collect.py:228 | SemanticModel |
| scripts/investigator/dynamic_reasoning.py:485 | Lakehouse, Warehouse |
| scripts/investigator/enterprise_discovery.py:63 | SemanticModel |
| scripts/investigator/enterprise_discovery.py:198 | semanticmodel |
| scripts/investigator/enterprise_discovery.py:222 | SemanticModel |
| scripts/investigator/estate_graph_repository.py:247 | fixture |
| scripts/investigator/estate_manifest.py:117 | fixture |
| scripts/investigator/estate_manifest.py:119 | fixture |
| scripts/investigator/estate_manifest.py:159 | fixture |
| scripts/investigator/facts_migration.py:20 | id-dia |
| scripts/investigator/facts_migration.py:21 | id-dia |
| scripts/investigator/facts_worker_verification.py:16 | id-dia |
| scripts/investigator/facts_worker_verification.py:18 | id-dia |
| scripts/investigator/grounded_answers.py:263 | semantic model |
| scripts/investigator/guided_intake.py:4 | fixture |
| scripts/investigator/guided_runtime_reads.py:43 | Semantic model |
| scripts/investigator/intake_extraction.py:132 | semantic-model |
| scripts/investigator/investigator_harness.py:67 | fixture |
| scripts/investigator/investigator_harness.py:68 | fixture |
| scripts/investigator/live_gateway.py:195 | workspaces/ |
| scripts/investigator/local_bundle.py:1 | fixture |
| scripts/investigator/local_bundle.py:15 | fixture |
| scripts/investigator/operational_fastpath.py:60 | fixture |
| scripts/investigator/parallel_run.py:3 | Workspace/ |
| scripts/investigator/parallel_run.py:53 | fixture |
| scripts/investigator/physical_binding.py:34 | Lakehouse |
| scripts/investigator/planner_recording.py:209 | fixture |
| scripts/investigator/process_tape.py:310 | fixture |
| scripts/investigator/process_tape.py:311 | fixture |
| scripts/investigator/process_tape.py:312 | fixture |
| scripts/investigator/process_tape.py:317 | FIXTURE |
| scripts/investigator/process_tape.py:320 | FIXTURE |
| scripts/investigator/process_tape.py:321 | FIXTURE |
| scripts/investigator/proof_preflight.py:44 | SemanticModel |
| scripts/investigator/proof_preflight.py:76 | FIXTURE |
| scripts/investigator/proof_preflight.py:117 | semanticModel, workspaces/ |
| scripts/investigator/proof_preflight.py:119 | workspaces/ |
| scripts/investigator/proof_preflight.py:121 | semanticModel, workspaces/ |
| scripts/investigator/proof_preflight.py:122 | semanticModel, workspaces/ |
| scripts/investigator/proof_requirements.py:17 | fixture |
| scripts/investigator/query_context.py:35 | lakehouse |
| scripts/investigator/question_intake.py:28 | semantic model |
| scripts/investigator/regression_features.json:80 | fixture |
| scripts/investigator/round23_calendar.py:1 | fixture |
| scripts/investigator/run_recording.py:121 | fixture |
| scripts/investigator/run_recording.py:122 | fixture |
| scripts/investigator/runtime.py:22 | fixture |
| scripts/investigator/transformation_reader.py:80 | fixture |
| scripts/investigator/translation_eval.py:1 | fixture |
| scripts/investigator/translation_eval.py:60 | fixture |
| scripts/investigator/translation_eval.py:71 | fixture |
| scripts/investigator/translation_eval.py:94 | fixture |
| scripts/investigator/translation_eval.py:109 | fixture |
| scripts/investigator/workspace_api.py:56 | workspace/ |
| scripts/investigator/workspace_api.py:64 | workspace/ |
| scripts/investigator/workspace_api.py:68 | workspace/ |
| scripts/investigator/workspace_api.py:70 | workspace/ |
| scripts/investigator/workspace_api.py:72 | workspace/ |
| scripts/investigator/workspace_api.py:76 | workspace/ |
| scripts/investigator/workspace_api.py:78 | workspace/ |
| scripts/investigator/workspace_api.py:81 | workspace/ |
| scripts/investigator/workspace_api.py:84 | workspace/ |
| scripts/investigator/workspace_api.py:85 | workspace/ |
| scripts/investigator/workspace_api.py:89 | workspace/ |
| scripts/investigator/workspace_api.py:91 | workspace/ |
| scripts/investigator/workspace_api.py:92 | workspace/ |
| scripts/investigator/workspace_api.py:108 | workspace/ |
| scripts/investigator/workspace_api.py:110 | workspace/ |
| scripts/investigator/workspace_api.py:111 | workspace/ |
| scripts/investigator/workspace_api.py:120 | workspace/ |
| scripts/investigator/workspace_api.py:123 | workspace/ |
| scripts/investigator/workspace_api.py:126 | workspace/ |
| scripts/investigator/workspace_api.py:128 | workspace/ |
| scripts/investigator/workspace_api.py:143 | workspace/ |
| scripts/investigator/workspace_api.py:145 | workspace/ |
| scripts/investigator/workspace_api.py:148 | workspace/ |
| scripts/investigator/workspace_api.py:150 | workspace/ |
| scripts/investigator/workspace_api.py:153 | workspace/ |
| scripts/investigator/workspace_api.py:155 | workspace/ |
| scripts/investigator/workspace_api.py:158 | workspace/ |
| scripts/investigator/workspace_api.py:161 | workspace/ |
| scripts/investigator/workspace_api.py:164 | workspace/ |
| scripts/investigator/workspace_api.py:166 | workspace/ |
| scripts/investigator/workspace_api.py:167 | workspace/ |
| scripts/investigator/workspace_api.py:176 | workspace/ |
| scripts/investigator/workspace_api.py:177 | workspace/ |
| scripts/investigator/workspace_api.py:178 | workspace/ |
| scripts/investigator/workspace_api.py:183 | workspace/ |
| scripts/investigator/workspace_api.py:184 | workspace/ |
| scripts/investigator/workspace_api.py:186 | workspace/ |
| scripts/investigator/workspace_api.py:187 | workspace/ |
| scripts/investigator/workspace_api.py:219 | workspace/ |
| scripts/investigator/workspace_api.py:221 | workspace/ |
| scripts/investigator/workspace_api.py:223 | workspace/ |
| scripts/investigator/workspace_api.py:224 | workspace/ |
| scripts/investigator/workspace_api.py:231 | workspace/ |
| scripts/investigator/workspace_api.py:233 | workspace/ |
| scripts/investigator/workspace_api.py:235 | workspace/ |
| scripts/investigator/workspace_api.py:238 | workspace/ |
| scripts/investigator/workspace_api.py:239 | workspace/ |
| scripts/lab_freshness.py:28 | fixture |
| scripts/lineage_graph.py:43 | lakehouse |
| scripts/lineage_graph.py:44 | lakehouse |
| scripts/lineage_graph.py:49 | Lakehouse |
| scripts/lineage_graph.py:83 | lakehouse, workspace/ |
| scripts/lineage_graph.py:96 | Lakehouse |
| scripts/lineage_graph.py:151 | Lakehouse |
| scripts/lineage_graph.py:153 | Warehouse |
| scripts/lineage_graph.py:157 | warehouse |
| scripts/lineage_graph.py:158 | Warehouse, warehouse |
| scripts/lineage_graph.py:159 | warehouse |
| scripts/lineage_graph.py:190 | semanticmodel |
| scripts/lineage_graph.py:191 | SemanticModel |
| scripts/managed_sql_worker.py:163 | database.windows.net |
| scripts/metadata_connectors.py:40 | workspaces/ |
| scripts/metadata_connectors.py:43 | SemanticModel |
| scripts/metadata_connectors.py:44 | workspaces/ |
| scripts/metadata_connectors.py:47 | workspaces/ |
| scripts/metadata_connectors.py:50 | lakehouse, workspaces/ |
| scripts/metadata_connectors.py:65 | SemanticModel |
| scripts/metadata_connectors.py:71 | SemanticModel |
| scripts/metadata_inventory.py:70 | SemanticModel |
| scripts/metadata_inventory.py:140 | workspaces/ |
| scripts/metadata_inventory.py:146 | workspaces/ |
| scripts/metadata_inventory.py:150 | SemanticModel |
| scripts/metadata_inventory.py:151 | SemanticModel |
| scripts/metadata_inventory.py:153 | SemanticModel |
| scripts/metadata_inventory.py:158 | Lakehouse |
| scripts/metadata_inventory.py:159 | lakehouse, workspaces/ |
| scripts/metadata_inventory.py:164 | Lakehouse |
| scripts/metadata_inventory.py:166 | Lakehouse |
| scripts/metadata_inventory.py:174 | SemanticModel |
| scripts/metadata_worker.py:30 | Lakehouse |
| scripts/multilayer_lab.py:1 | fixture |
| scripts/multilayer_lab.py:21 | fixture |
| scripts/multilayer_lab.py:22 | fixture |
| scripts/multilayer_lab.py:28 | fixture |
| scripts/multilayer_lab.py:29 | fixture |
| scripts/multilayer_lab.py:76 | fixture |
| scripts/onelake_metadata.py:12 | lakehouse |
| scripts/onelake_metadata.py:13 | lakehouse |
| scripts/onelake_metadata.py:54 | lakehouse |
| scripts/onelake_metadata.py:57 | lakehouse |
| scripts/owner_demo.py:69 | fixture |
| scripts/platform-literal-debt-ceiling.json:6 | fixture |
| scripts/platform-literal-debt-ceiling.json:19 | fixture |
| scripts/platform-literal-debt-ceiling.json:29 | fixture |
| scripts/platform-literal-debt-ceiling.json:48 | fixture |
| scripts/platform-literal-debt.json:3 | fixture |
| scripts/platform-literal-debt.json:13 | fixture |
| scripts/platform-literal-debt.json:23 | fixture |
| scripts/platform-literal-debt.json:36 | fixture |
| scripts/platform_blob_transfer.py:25 | blob.core.windows.net |
| scripts/platform_health.py:76 | database.windows.net |
| scripts/probe_execution_surfaces.py:120 | lakehouse |
| scripts/probe_execution_surfaces.py:145 | lakehouse |
| scripts/prove_ledger_verdicts.py:18 | warehouse |
| scripts/prove_ledger_verdicts.py:35 | fixture |
| scripts/prove_ledger_verdicts.py:43 | warehouse |
| scripts/prove_ledger_verdicts.py:71 | warehouse |
| scripts/prove_ledger_verdicts.py:76 | warehouse |
| scripts/prove_ledger_verdicts.py:84 | warehouse |
| scripts/provision_model_month.py:125 | database.windows.net |
| scripts/publish_import_fixture.py:1 | fixture |
| scripts/publish_import_fixture.py:11 | fixture |
| scripts/publish_import_fixture.py:26 | Fixture |
| scripts/publish_import_fixture.py:108 | fixture |
| scripts/publish_import_fixture.py:109 | fixture |
| scripts/publish_import_fixture.py:111 | workspaces/ |
| scripts/publish_import_fixture.py:114 | semanticModel, workspaces/ |
| scripts/publish_import_fixture.py:115 | Fixture |
| scripts/publish_import_fixture.py:119 | semanticModel, workspaces/ |
| scripts/publish_import_fixture.py:120 | Fixture |
| scripts/publish_import_fixture.py:123 | semantic_model |
| scripts/publish_import_fixture.py:127 | semantic_model |
| scripts/publish_import_fixture.py:148 | Fixture |
| scripts/publish_import_fixture.py:156 | semantic_model |
| scripts/read_onelake_commit.py:37 | lakehouse |
| scripts/read_onelake_commit.py:44 | lakehouse |
| scripts/read_onelake_header.py:15 | lakehouse |
| scripts/read_onelake_header.py:17 | lakehouse |
| scripts/read_xmla_failure.py:1 | semantic model |
| scripts/read_xmla_failure.py:53 | fixture |
| scripts/record_bronze_publication.py:27 | lakehouse |
| scripts/record_bronze_publication.py:29 | lakehouse |
| scripts/record_bronze_publication.py:30 | workspaces/ |
| scripts/record_bronze_publication.py:32 | lakehouse |
| scripts/record_gold_publication.py:20 | lakehouse |
| scripts/record_gold_publication.py:22 | workspaces/ |
| scripts/record_silver_publication.py:20 | lakehouse |
| scripts/record_silver_publication.py:23 | lakehouse |
| scripts/record_silver_publication.py:24 | workspaces/ |
| scripts/refresh_powerbi.py:1 | semantic model |
| scripts/refresh_powerbi.py:8 | lakehouse, semantic_model |
| scripts/refresh_powerbi.py:12 | workspaces/ |
| scripts/refresh_powerbi.py:34 | Semantic model |
| scripts/refresh_powerbi.py:46 | semantic model |
| scripts/renew_platform_cost_observation.py:68 | rg-dia |
| scripts/renew_platform_cost_observation.py:74 | rg-dia |
| scripts/report_definition_evidence.py:37 | semanticmodel |
| scripts/report_definition_evidence.py:42 | SemanticModel |
| scripts/report_definition_evidence.py:44 | semanticmodel |
| scripts/report_list_worker.py:24 | fixture |
| scripts/report_round25_cohort.py:24 | fixture |
| scripts/resynthesize_mechanisms.py:43 | fixture |
| scripts/resynthesize_mechanisms.py:69 | fixture |
| scripts/resynthesize_mechanisms.py:70 | fixture |
| scripts/revise_conversational_oracle.py:139 | fixture |
| scripts/revise_conversational_oracle.py:180 | warehouse |
| scripts/round25_quality.py:223 | fixture |
| scripts/round25_quality.py:233 | fixture |
| scripts/round25_quality.py:297 | Fixture |
| scripts/round25_quality.py:335 | fixture |
| scripts/round25_quality.py:342 | fixture |
| scripts/run_enterprise_discovery.py:43 | warehouse |
| scripts/run_enterprise_discovery.py:52 | warehouse |
| scripts/run_enterprise_discovery.py:53 | warehouse |
| scripts/run_native_diagnostic.py:82 | fixture |
| scripts/semantic_snapshot.py:21 | lakehouse |
| scripts/serve_lab_review.py:21 | 194e3b0c-9c06-4c83-aaba-cae2736e3164 |
| scripts/serve_lab_review.py:23 | 6b901118-25b6-4a69-8c78-8f19b392690b |
| scripts/serve_lab_review.py:25 | ccfeffbc-44c0-4a66-aad9-38baf4055ce1 |
| scripts/silver_snapshot_input.py:38 | lakehouse |
| scripts/silver_snapshot_input.py:42 | lakehouse |
| scripts/silver_snapshot_input.py:63 | lakehouse |
| scripts/snapshot_identity_reader.py:30 | database.windows.net |
| scripts/testdata/graph-interpreter-citation-proposals.json:6 | Fixture |
| scripts/testdata/graph-interpreter-citation-proposals.json:163 | Fixture |
| scripts/testdata/graph-interpreter-span-failure.json:5 | Fixture |
| scripts/upload_source_snapshot.py:19 | lakehouse |
| scripts/upload_source_snapshot.py:24 | lakehouse |
| scripts/upload_source_snapshot.py:47 | lakehouse |
| scripts/validate_lineage.py:22 | Lakehouse |
| scripts/validate_metadata_inventory.py:19 | Lakehouse |
| scripts/validate_metadata_inventory.py:25 | lakehouse |
| scripts/validate_metadata_inventory.py:26 | Lakehouse |
| scripts/validate_metadata_inventory.py:27 | SemanticModel |
| scripts/validate_metadata_inventory.py:34 | lakehouse |
| scripts/validate_powerbi.py:14 | semantic_model |
| scripts/validate_powerbi.py:25 | lakehouse |
| scripts/validate_powerbi.py:56 | semantic_model |
| scripts/validate_powerbi.py:61 | lakehouse |
| scripts/verify_dependency_context.py:10 | Fixture, fixture |
| scripts/verify_dependency_context.py:29 | Fixture |
| scripts/verify_dependency_context.py:30 | fixture |
| scripts/verify_dependency_context.py:31 | Fixture |
| scripts/verify_dependency_context.py:56 | fixture |
| scripts/verify_fixture_code_sources.py:13 | 7ccafe59-0460-4c8a-a691-bfdfa75a2b25, fixture |
| scripts/verify_fixture_code_sources.py:15 | fixture |
| scripts/verify_fixture_code_sources.py:16 | fixture |
| scripts/verify_fixture_code_sources.py:42 | Fixture |
| scripts/verify_investigator_workspace.py:134 | fixture |
| scripts/verify_investigator_workspace.py:135 | fixture |
| scripts/verify_investigator_workspace.py:201 | fixture |
| scripts/verify_investigator_workspace.py:203 | fixture |
| scripts/verify_reader_runtime.py:1 | fixture |
| scripts/verify_reader_runtime.py:3 | fixture |
| scripts/verify_reader_runtime.py:17 | fixture |
| scripts/verify_reader_runtime.py:27 | fixture |
| scripts/verify_reader_runtime.py:50 | fixture |
| scripts/verify_reader_runtime.py:52 | FIXTURE |
| scripts/verify_reader_runtime.py:60 | FIXTURE |
| scripts/verify_reader_runtime.py:76 | Fixture |
| scripts/verify_reader_runtime.py:82 | fixture |
| scripts/verify_reader_runtime.py:83 | fixture |
| scripts/verify_reader_runtime.py:85 | Fixture |
| scripts/verify_reader_runtime.py:86 | fixture |
| scripts/verify_reader_runtime.py:97 | fixture |
| scripts/verify_reader_runtime.py:98 | Fixture |
| scripts/verify_reader_runtime.py:100 | Fixture |
| scripts/verify_reader_runtime.py:132 | fixture |
| scripts/verify_reader_runtime.py:136 | fixture |
| scripts/verify_reader_runtime.py:142 | fixture |
| scripts/verify_reader_runtime.py:145 | fixture |
| scripts/verify_reader_runtime.py:149 | Fixture |
| tests/tickets/derive_baseline_cases.py:1 | Fixture |
| tests/tickets/derive_baseline_cases.py:7 | fixture |
| tests/tickets/derive_baseline_cases.py:15 | fixture |
| tests/tickets/derive_baseline_cases.py:17 | fixture |
| tests/tickets/independent-baseline-arithmetic.json:3 | fixture |
| tests/tickets/independent-drafts-access-dev.json:1 | billingapp, dia-investigator, orderops_investigator |
| tests/tickets/independent-drafts-access-heldout.json:1 | billingapp, dia-investigator, orderops_investigator |
| tests/tickets/independent-drafts-blocked-heldout.json:1 | 20261003, Application load fixture, FIXTURE, fixture, ordersops, semantic model |
| tests/tickets/independent-drafts-context-dev.json:1 | warehouse |
| tests/tickets/independent-drafts-context-heldout.json:1 | warehouse |
| tests/tickets/independent-drafts-final-nine-dev.json:1 | 20261003 |
| tests/tickets/independent-drafts-final-nine-heldout.json:1 | 20261003, Application load fixture, Warehouse, semantic model |
| tests/tickets/independent-drafts-history-gap-dev.json:1 | ordersops |
| tests/tickets/independent-drafts-history-gap-heldout.json:1 | ordersops |
| tests/tickets/independent-drafts-real-failures.json:10 | fixture |
| tests/tickets/independent-drafts-real-failures.json:11 | fixture |
| tests/tickets/independent-drafts-real-failures.json:13 | 20261003 |
| tests/tickets/independent-drafts-real-failures.json:16 | fixture |
| tests/tickets/independent-drafts-real-failures.json:17 | fixture |
| tests/tickets/independent-drafts-real-failures.json:19 | 20261003 |
| tests/tickets/independent-drafts-real-failures.json:25 | Warehouse |
| tests/tickets/independent-drafts-real-failures.json:31 | Warehouse |
| tests/tickets/independent-drafts-stale-dev.json:1 | 20261003, Application load fixture, lakehouse, semantic model, warehouse |
| tests/tickets/independent-drafts-stale-heldout.json:1 | 20261003, Application load fixture, lakehouse, semantic model, warehouse |
| tests/tickets/independent-drafts-waiting-dev.json:1 | 20261003, fixture |
| tests/tickets/independent-drafts-waiting-heldout.json:1 | Warehouse |
| tests/tickets/injections.md:7 | fixture |
| tests/tickets/injections.md:11 | b4871498-bd35-45be-916c-9a642568012c, fixture |
| tests/tickets/injections.md:12 | 76c60248-b830-433b-9880-90593da28e7e |
| tests/tickets/injections.md:13 | fc8438fd-2c18-4196-9191-33e26481e2e0 |
| tests/tickets/injections.md:15 | 62eb1a7f-19c2-466f-85ec-cda6bc231fb9 |
| tests/tickets/injections.md:21 | fixture |
| tests/tickets/injections.md:33 | fixture |
| tests/tickets/injections.md:38 | fixture |
| tests/tickets/injections.md:45 | Fixture, fixture |
| tests/tickets/injections.md:49 | 605f92df-b2e4-4851-8263-51d7ade0ad1e, fixture |
| tests/tickets/injections.md:51 | fixture |
| tests/tickets/injections.md:53 | fixture |
| tests/tickets/injections.md:55 | fixture, ordersops |
| tests/tickets/injections.md:57 | fixture |
| tests/tickets/injections.md:59 | fixture |
| tests/tickets/injections.md:65 | Warehouse, fixture |
| tests/tickets/injections.md:67 | warehouse |
| tests/tickets/injections.md:71 | billingapp, fixture |
| tests/tickets/injections.md:73 | 659ea59a-256f-4673-a661-0d6f3359d9be, Warehouse, fixture |
| tests/tickets/injections.md:77 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 20261003, Application load fixture, fixture, lakehouse |
| tests/tickets/injections.md:88 | fixture |
| tests/tickets/injections.md:94 | 30fc840e-2343-4420-9c47-0d763dd694f3 |
| tests/tickets/injections.md:99 | 95a3d0f6-ef3a-4d1c-8815-0af704190707 |
| tests/tickets/injections.md:101 | 623ed85f-40dc-4f32-b6f8-447a8468d318 |
| tests/tickets/injections.md:110 | fixture |
| tests/tickets/injections.md:125 | fixture |
| tests/tickets/injections.md:155 | 03d815b4-3134-4792-9d2a-a0475374b6d4 |
| tests/tickets/injections.md:173 | fixture |
| tests/tickets/injections.md:197 | f5181b94-b40a-4a0a-afda-970e040d8f7f |
| tests/tickets/injections.md:200 | fixture |
| tests/tickets/injections.md:227 | fixture |
| tests/tickets/injections.md:254 | fixture |
| tests/tickets/injections.md:287 | fixture |
| tests/tickets/injections.md:308 | fixture |
| tests/tickets/injections.md:344 | fixture |
| tests/tickets/injections.md:371 | fixture |
| tests/tickets/injections.md:374 | fixture |
| tests/tickets/injections.md:377 | fixture |
| tests/tickets/injections.md:404 | fixture |
| tests/tickets/injections.md:428 | fixture |
| tests/tickets/injections.md:431 | fixture |
| tests/tickets/injections.md:440 | fixture |
| tests/tickets/injections.md:464 | 625f3197-0754-46b7-b2f5-8a3666cb27b7, eeff6b5a-59db-48c1-b6ef-4875fe29cf3a |
| tests/tickets/injections.md:488 | e0773fcf-6fb9-456a-bd08-44839e3a539f |
| tests/tickets/injections.md:491 | fixture |
| tests/tickets/injections.md:519 | 20261003, Application load fixture |
| tests/tickets/injections.md:522 | fixture |
| tests/tickets/injections.md:540 | fixture |
| tests/tickets/injections.md:572 | 1221447d-8e70-4bf0-beca-528ff36c33c3 |
| tests/tickets/injections.md:575 | fixture |
| tests/tickets/injections.md:599 | acb61da4-c7aa-4aa5-b7e3-0be7d613aa1c |
| tests/tickets/injections.md:602 | fixture |
| tests/tickets/injections.md:614 | 3e0fe208-bece-4164-a89f-42930ab377f8 |
| tests/tickets/injections.md:617 | fixture |
| tests/tickets/injections.md:629 | fixture |
| tests/tickets/injections.md:653 | fixture |
| tests/tickets/injections.md:669 | 85942e74-bd08-407b-8c4b-02692a51512e, fixture |
| tests/tickets/injections.md:674 | f238f1ba-1142-4b55-bdc1-958c61911343 |
| tests/tickets/injections.md:680 | 85942e74-bd08-407b-8c4b-02692a51512e |
| tests/tickets/round22-old-refresh-contract.json:1 | 149f8d99-1c66-4a0a-9624-759be002bb60 |
| tests/tickets/scored-set-v1-heldout.json:1 | 20261003, Application load fixture, Warehouse, billingapp, dia-investigator, fixture, lakehouse, orderops_investigator, ordersops, semantic model, warehouse |

## identity/secrets

| Source | Matched identifier or marker |
|---|---|
| config/permission-map.yaml:5 | c22c5e9b-5005-4a48-af98-51d614e6021a |
| config/permission-map.yaml:10 | 23de217f-6e14-49cf-9acd-47dcd83cb82f |
| config/permission-map.yaml:11 | skynwhy.com |
| config/permission-map.yaml:15 | 439ceb25-d200-4f02-95cf-4b1318faca62 |
| config/permission-map.yaml:16 | 531419ef-1610-415a-b8bf-01a4b6aad751 |
| config/permission-map.yaml:18 | dff91047-ebc2-4657-8dbe-5af328d57780 |
| config/permission-map.yaml:21 | dbb49594-6c70-4989-a6c8-c4f237c4a021 |
| config/permission-map.yaml:22 | 86a9d95a-466c-443e-9eb9-91f870ffe15a |
| config/permission-map.yaml:26 | 21e3405b-57e9-4581-834e-971b465f80ec |
| config/permission-map.yaml:31 | 21e3405b-57e9-4581-834e-971b465f80ec |
| config/permission-map.yaml:36 | 21e3405b-57e9-4581-834e-971b465f80ec |
| config/permission-map.yaml:45 | 8a582d2a-ecb4-4320-bf72-75a529a0d382 |
| config/permission-map.yaml:46 | skynwhy.com |
| config/permission-map.yaml:50 | dc89155f-9a9a-4daa-9c20-7eff55818ccd |
| config/permission-map.yaml:51 | 2dd2f5c3-f7af-4804-b79e-6019e63efa60 |
| config/permission-map.yaml:55 | 59dd402b-1510-4289-96fb-f1d34d4494c5 |
| config/permission-map.yaml:56 | ddd4d3cf-9cfd-440e-ac5b-be127caa46ea |
| config/permission-map.yaml:64 | 248525da-278c-4a6c-b5c3-cc3e7728d3ce |
| config/permission-map.yaml:65 | 531419ef-1610-415a-b8bf-01a4b6aad751 |
| config/permission-map.yaml:66 | aeb4d0a9-e637-4a7e-8efc-63cf0c3827df |
| config/permission-map.yaml:67 | billingapp, ordersops |
| config/permission-map.yaml:500 | dff91047-ebc2-4657-8dbe-5af328d57780 |
| config/permission-map.yaml:512 | dff91047-ebc2-4657-8dbe-5af328d57780 |
| config/permission-map.yaml:524 | dff91047-ebc2-4657-8dbe-5af328d57780 |
| config/permission-map.yaml:536 | dff91047-ebc2-4657-8dbe-5af328d57780 |
| config/permission-map.yaml:718 | kv-dia- |
| config/permission-map.yaml:755 | kv-dia- |
| config/permission-map.yaml:792 | kv-dia- |
| config/permission-map.yaml:805 | kv-dia- |
| config/permission-map.yaml:817 | kv-dia- |
| config/permission-map.yaml:868 | skynwhy.com |
| infra/estates/fixture-code-git.json:19 | orderops_investigator |
| infra/estates/fixture-code-git.json:27 | dff91047-ebc2-4657-8dbe-5af328d57780 |
| infra/estates/fixture-code-git.json:32 | dff91047-ebc2-4657-8dbe-5af328d57780 |
| infra/estates/fixture-code-git.json:33 | skynwhy.com |
| infra/estates/fixture-code-git.json:34 | 8a582d2a-ecb4-4320-bf72-75a529a0d382 |
| infra/estates/fixture-code-git.json:40 | skynwhy.com |
| infra/estates/fixture-code-git.json:162 | skynwhy.com |
| infra/estates/fixture-code-git.json:225 | orderops_investigator |
| infra/estates/fixture-code-git.json:226 | orderops_investigator |
| infra/estates/fixture-code-git.json:238 | ddd4d3cf-9cfd-440e-ac5b-be127caa46ea |
| infra/estates/fixture-lineage-proposer.json:19 | orderops_investigator |
| infra/estates/fixture-lineage-proposer.json:27 | dff91047-ebc2-4657-8dbe-5af328d57780 |
| infra/estates/fixture-lineage-proposer.json:32 | dff91047-ebc2-4657-8dbe-5af328d57780 |
| infra/estates/fixture-lineage-proposer.json:33 | skynwhy.com |
| infra/estates/fixture-lineage-proposer.json:34 | 8a582d2a-ecb4-4320-bf72-75a529a0d382 |
| infra/estates/fixture-lineage-proposer.json:40 | skynwhy.com |
| infra/estates/fixture-lineage-proposer.json:79 | skynwhy.com |
| infra/estates/fixture-lineage-proposer.json:89 | skynwhy.com |
| infra/estates/fixture-lineage-proposer.json:283 | skynwhy.com |
| infra/estates/fixture-lineage-proposer.json:346 | orderops_investigator |
| infra/estates/fixture-lineage-proposer.json:347 | orderops_investigator |
| infra/estates/fixture-lineage-proposer.json:359 | ddd4d3cf-9cfd-440e-ac5b-be127caa46ea |
| infra/estates/fixture.json:20 | orderops_investigator |
| infra/estates/fixture.json:28 | dff91047-ebc2-4657-8dbe-5af328d57780 |
| infra/estates/fixture.json:33 | dff91047-ebc2-4657-8dbe-5af328d57780 |
| infra/estates/fixture.json:34 | skynwhy.com |
| infra/estates/fixture.json:35 | 8a582d2a-ecb4-4320-bf72-75a529a0d382 |
| infra/estates/fixture.json:41 | skynwhy.com |
| infra/estates/fixture.json:80 | skynwhy.com |
| infra/estates/fixture.json:90 | skynwhy.com |
| infra/estates/fixture.json:284 | skynwhy.com |
| infra/estates/fixture.json:347 | orderops_investigator |
| infra/estates/fixture.json:348 | orderops_investigator |
| infra/estates/fixture.json:360 | ddd4d3cf-9cfd-440e-ac5b-be127caa46ea |
| infra/metadata/development.json:9 | orderops_investigator |
| infra/metadata/development.json:16 | dff91047-ebc2-4657-8dbe-5af328d57780 |
| infra/metadata/development.json:20 | skynwhy.com |
| scripts/fixture/source_history.py:3 | fixture |
| scripts/investigator/adapters/connection_rotation.py:122 | workspaces/ |
| scripts/investigator/adapters/known-platform-limits.md:24 | Fixture, Warehouse |
| scripts/investigator/adapters/record_presence.py:100 | Warehouse |
| scripts/investigator/adapters/source_delivery.py:71 | Warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:34 | warehouse |
| scripts/investigator/adapters/warehouse_catalog.py:68 | warehouse |
| scripts/investigator/planner_recording.py:1 | fixture |
| scripts/investigator/postgres_connection.py:17 | database.windows.net |
| scripts/review_round25_disagreements.py:26 | kv-dia- |
| scripts/setup_bedrock_identity.py:50 | kv-dia- |
| tests/tickets/injections.md:69 | billingapp, dia-investigator, fixture, orderops_investigator |
| tests/tickets/injections.md:79 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, b1a57512-f71a-41a3-b868-4ee2999c42b9, fixture |
| tests/tickets/injections.md:81 | warehouse |
| tests/tickets/injections.md:104 | fixture, semantic-model, semanticmodel |
| tests/tickets/scored-set-v1-dev-expected.json:1 | 20261003, Application load fixture, Warehouse, fixture, orderops_investigator, warehouse |
| tests/tickets/scored-set-v1-heldout-expected.json:1 | 20261003, Application load fixture, Warehouse, fixture, orderops_investigator, warehouse |

## infrastructure

| Source | Matched identifier or marker |
|---|---|
| .github/workflows/cloud-worker.yml:101 | fixture |
| .github/workflows/code-sources.yml:21 | fixture |
| .github/workflows/known-domain-acceptance.yml:38 | fixture |
| .github/workflows/known-domain-acceptance.yml:42 | fixture |
| .github/workflows/round-ten-earned-acceptance.yml:45 | fixture |
| .github/workflows/validation.yml:28 | fixture |
| .github/workflows/validation.yml:85 | fixture |
| .github/workflows/validation.yml:86 | fixture |
| .github/workflows/validation.yml:88 | warehouse |
| .github/workflows/validation.yml:160 | fixture |
| .github/workflows/validation.yml:294 | fixture |
| .github/workflows/validation.yml:296 | fixture |
| .github/workflows/validation.yml:317 | fixture |
| .github/workflows/validation.yml:318 | workspace/ |
| .github/workflows/validation.yml:319 | workspace/ |
| config/permission-map.yaml:32 | id-dia, job-dia- |
| config/permission-map.yaml:37 | id-dia, job-dia- |
| config/permission-map.yaml:548 | pg-dia- |
| config/permission-map.yaml:560 | pg-dia- |
| config/permission-map.yaml:572 | pg-dia- |
| config/permission-map.yaml:584 | pg-dia- |
| config/permission-map.yaml:596 | pg-dia- |
| config/permission-map.yaml:608 | pg-dia- |
| config/permission-map.yaml:620 | pg-dia- |
| config/permission-map.yaml:632 | pg-dia- |
| config/permission-map.yaml:644 | pg-dia- |
| config/permission-map.yaml:656 | pg-dia- |
| config/permission-map.yaml:668 | pg-dia- |
| config/permission-map.yaml:681 | pg-dia- |
| config/permission-map.yaml:694 | blob.core.windows.net, diaplatform |
| config/permission-map.yaml:706 | blob.core.windows.net, diaplatform |
| config/permission-map.yaml:731 | blob.core.windows.net, diaplatform |
| config/permission-map.yaml:743 | blob.core.windows.net, diaplatform |
| config/permission-map.yaml:768 | blob.core.windows.net, diaplatform |
| config/permission-map.yaml:780 | blob.core.windows.net, diaplatform |
| config/permission-map.yaml:842 | job-dia-, rg-dia |
| config/permission-map.yaml:920 | pg-dia- |
| config/permission-map.yaml:932 | pg-dia- |
| config/permission-map.yaml:944 | pg-dia- |
| config/permission-map.yaml:957 | pg-dia- |
| config/permission-map.yaml:970 | pg-dia- |
| config/permission-map.yaml:983 | pg-dia- |
| config/permission-map.yaml:996 | pg-dia- |
| config/permission-map.yaml:1009 | pg-dia- |
| infra/estates/databricks.json:4 | lakehouse |
| infra/estates/databricks.json:16 | warehouse |
| infra/estates/fixture-code-git.json:14 | database.windows.net, sql-orderops |
| infra/estates/fixture-code-git.json:15 | ordersops |
| infra/estates/fixture-code-git.json:20 | orderops_investigator |
| infra/estates/fixture-code-git.json:24 | 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture-code-git.json:36 | 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture-code-git.json:42 | warehouse |
| infra/estates/fixture-code-git.json:54 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e |
| infra/estates/fixture-code-git.json:60 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e |
| infra/estates/fixture-code-git.json:66 | 149f8d99-1c66-4a0a-9624-759be002bb60, b0ab76f7-20c7-410e-90e4-2c4eb104059a |
| infra/estates/fixture-code-git.json:72 | 149f8d99-1c66-4a0a-9624-759be002bb60, b0ab76f7-20c7-410e-90e4-2c4eb104059a |
| infra/estates/fixture-code-git.json:78 | 149f8d99-1c66-4a0a-9624-759be002bb60, ba24d52c-fcf9-4f1f-a377-f4d38547d887 |
| infra/estates/fixture-code-git.json:84 | 149f8d99-1c66-4a0a-9624-759be002bb60, ba24d52c-fcf9-4f1f-a377-f4d38547d887 |
| infra/estates/fixture-code-git.json:90 | 09ba0ef9-7342-4179-a49e-1fc8adf48d82, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture-code-git.json:96 | 09ba0ef9-7342-4179-a49e-1fc8adf48d82, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture-code-git.json:102 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture-code-git.json:108 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture-code-git.json:114 | 149f8d99-1c66-4a0a-9624-759be002bb60, 20261003, 33618b8d-46eb-4fe7-b80b-122c331260a3 |
| infra/estates/fixture-code-git.json:120 | 149f8d99-1c66-4a0a-9624-759be002bb60, 20261003, 33618b8d-46eb-4fe7-b80b-122c331260a3 |
| infra/estates/fixture-code-git.json:126 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture-code-git.json:132 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture-code-git.json:142 | 149f8d99-1c66-4a0a-9624-759be002bb60, bea673e0-a206-461e-9b2f-1b3b827e80de |
| infra/estates/fixture-code-git.json:145 | 149f8d99-1c66-4a0a-9624-759be002bb60, bea673e0-a206-461e-9b2f-1b3b827e80de |
| infra/estates/fixture-code-git.json:151 | 149f8d99-1c66-4a0a-9624-759be002bb60, b4871498-bd35-45be-916c-9a642568012c |
| infra/estates/fixture-code-git.json:154 | 149f8d99-1c66-4a0a-9624-759be002bb60, b4871498-bd35-45be-916c-9a642568012c |
| infra/estates/fixture-code-git.json:248 | fixture |
| infra/estates/fixture-code-git.json:262 | 149f8d99-1c66-4a0a-9624-759be002bb60, b4871498-bd35-45be-916c-9a642568012c |
| infra/estates/fixture-code-git.json:263 | 149f8d99-1c66-4a0a-9624-759be002bb60, 57e128c3-6ba0-4aaf-9464-81164ecdc782 |
| infra/estates/fixture-code-git.json:284 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture-code-git.json:285 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture-code-git.json:286 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture-code-git.json:287 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture-code-git.json:292 | fixture |
| infra/estates/fixture-code-git.json:297 | fixture |
| infra/estates/fixture-code-git.json:308 | fixture |
| infra/estates/fixture-code-git.json:309 | 7ccafe59-0460-4c8a-a691-bfdfa75a2b25 |
| infra/estates/fixture-code-git.json:319 | fixture |
| infra/estates/fixture-code-git.json:320 | 7ccafe59-0460-4c8a-a691-bfdfa75a2b25 |
| infra/estates/fixture-code-git.json:354 | d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9 |
| infra/estates/fixture-code-git.json:392 | fixture |
| infra/estates/fixture-code-git.json:399 | fixture |
| infra/estates/fixture-code-git.json:407 | fixture |
| infra/estates/fixture-code-git.json:408 | fixture |
| infra/estates/fixture-code-git.json:416 | fixture |
| infra/estates/fixture-code-git.json:422 | Warehouse |
| infra/estates/fixture-code-git.json:430 | fixture |
| infra/estates/fixture-lineage-proposer.json:14 | database.windows.net, sql-orderops |
| infra/estates/fixture-lineage-proposer.json:15 | ordersops |
| infra/estates/fixture-lineage-proposer.json:20 | orderops_investigator |
| infra/estates/fixture-lineage-proposer.json:24 | 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture-lineage-proposer.json:36 | 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture-lineage-proposer.json:42 | warehouse |
| infra/estates/fixture-lineage-proposer.json:54 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e |
| infra/estates/fixture-lineage-proposer.json:60 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e |
| infra/estates/fixture-lineage-proposer.json:81 | 3484a2bc-98c5-4cef-be5c-a6215484075e |
| infra/estates/fixture-lineage-proposer.json:88 | 3484a2bc-98c5-4cef-be5c-a6215484075e |
| infra/estates/fixture-lineage-proposer.json:97 | 149f8d99-1c66-4a0a-9624-759be002bb60, b0ab76f7-20c7-410e-90e4-2c4eb104059a |
| infra/estates/fixture-lineage-proposer.json:103 | 149f8d99-1c66-4a0a-9624-759be002bb60, b0ab76f7-20c7-410e-90e4-2c4eb104059a |
| infra/estates/fixture-lineage-proposer.json:118 | 149f8d99-1c66-4a0a-9624-759be002bb60, ba24d52c-fcf9-4f1f-a377-f4d38547d887 |
| infra/estates/fixture-lineage-proposer.json:124 | 149f8d99-1c66-4a0a-9624-759be002bb60, ba24d52c-fcf9-4f1f-a377-f4d38547d887 |
| infra/estates/fixture-lineage-proposer.json:139 | 09ba0ef9-7342-4179-a49e-1fc8adf48d82, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture-lineage-proposer.json:145 | 09ba0ef9-7342-4179-a49e-1fc8adf48d82, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture-lineage-proposer.json:163 | warehouse |
| infra/estates/fixture-lineage-proposer.json:173 | warehouse |
| infra/estates/fixture-lineage-proposer.json:182 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture-lineage-proposer.json:188 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture-lineage-proposer.json:194 | 149f8d99-1c66-4a0a-9624-759be002bb60, 20261003, 33618b8d-46eb-4fe7-b80b-122c331260a3 |
| infra/estates/fixture-lineage-proposer.json:200 | 149f8d99-1c66-4a0a-9624-759be002bb60, 20261003, 33618b8d-46eb-4fe7-b80b-122c331260a3 |
| infra/estates/fixture-lineage-proposer.json:215 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture-lineage-proposer.json:221 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture-lineage-proposer.json:242 | orderops_investigator |
| infra/estates/fixture-lineage-proposer.json:243 | ordersops |
| infra/estates/fixture-lineage-proposer.json:252 | ordersops |
| infra/estates/fixture-lineage-proposer.json:253 | orderops_investigator |
| infra/estates/fixture-lineage-proposer.json:263 | 149f8d99-1c66-4a0a-9624-759be002bb60, bea673e0-a206-461e-9b2f-1b3b827e80de |
| infra/estates/fixture-lineage-proposer.json:266 | 149f8d99-1c66-4a0a-9624-759be002bb60, bea673e0-a206-461e-9b2f-1b3b827e80de |
| infra/estates/fixture-lineage-proposer.json:272 | 149f8d99-1c66-4a0a-9624-759be002bb60, b4871498-bd35-45be-916c-9a642568012c |
| infra/estates/fixture-lineage-proposer.json:275 | 149f8d99-1c66-4a0a-9624-759be002bb60, b4871498-bd35-45be-916c-9a642568012c |
| infra/estates/fixture-lineage-proposer.json:369 | fixture |
| infra/estates/fixture-lineage-proposer.json:383 | 149f8d99-1c66-4a0a-9624-759be002bb60, b4871498-bd35-45be-916c-9a642568012c |
| infra/estates/fixture-lineage-proposer.json:384 | 149f8d99-1c66-4a0a-9624-759be002bb60, 57e128c3-6ba0-4aaf-9464-81164ecdc782 |
| infra/estates/fixture-lineage-proposer.json:405 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture-lineage-proposer.json:406 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture-lineage-proposer.json:407 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture-lineage-proposer.json:408 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture-lineage-proposer.json:413 | fixture |
| infra/estates/fixture-lineage-proposer.json:416 | fixture |
| infra/estates/fixture-lineage-proposer.json:426 | fixture |
| infra/estates/fixture-lineage-proposer.json:427 | 7ccafe59-0460-4c8a-a691-bfdfa75a2b25 |
| infra/estates/fixture-lineage-proposer.json:437 | fixture |
| infra/estates/fixture-lineage-proposer.json:438 | 7ccafe59-0460-4c8a-a691-bfdfa75a2b25 |
| infra/estates/fixture-lineage-proposer.json:472 | d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9 |
| infra/estates/fixture-lineage-proposer.json:510 | fixture |
| infra/estates/fixture-lineage-proposer.json:517 | fixture |
| infra/estates/fixture-lineage-proposer.json:525 | fixture |
| infra/estates/fixture-lineage-proposer.json:526 | fixture |
| infra/estates/fixture-lineage-proposer.json:534 | fixture |
| infra/estates/fixture-lineage-proposer.json:540 | Warehouse |
| infra/estates/fixture-lineage-proposer.json:548 | fixture |
| infra/estates/fixture.json:15 | database.windows.net, sql-orderops |
| infra/estates/fixture.json:16 | ordersops |
| infra/estates/fixture.json:21 | orderops_investigator |
| infra/estates/fixture.json:25 | 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture.json:37 | 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture.json:43 | warehouse |
| infra/estates/fixture.json:55 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e |
| infra/estates/fixture.json:61 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e |
| infra/estates/fixture.json:82 | 3484a2bc-98c5-4cef-be5c-a6215484075e |
| infra/estates/fixture.json:89 | 3484a2bc-98c5-4cef-be5c-a6215484075e |
| infra/estates/fixture.json:98 | 149f8d99-1c66-4a0a-9624-759be002bb60, b0ab76f7-20c7-410e-90e4-2c4eb104059a |
| infra/estates/fixture.json:104 | 149f8d99-1c66-4a0a-9624-759be002bb60, b0ab76f7-20c7-410e-90e4-2c4eb104059a |
| infra/estates/fixture.json:119 | 149f8d99-1c66-4a0a-9624-759be002bb60, ba24d52c-fcf9-4f1f-a377-f4d38547d887 |
| infra/estates/fixture.json:125 | 149f8d99-1c66-4a0a-9624-759be002bb60, ba24d52c-fcf9-4f1f-a377-f4d38547d887 |
| infra/estates/fixture.json:140 | 09ba0ef9-7342-4179-a49e-1fc8adf48d82, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture.json:146 | 09ba0ef9-7342-4179-a49e-1fc8adf48d82, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture.json:164 | warehouse |
| infra/estates/fixture.json:174 | warehouse |
| infra/estates/fixture.json:183 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture.json:189 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| infra/estates/fixture.json:195 | 149f8d99-1c66-4a0a-9624-759be002bb60, 20261003, 33618b8d-46eb-4fe7-b80b-122c331260a3 |
| infra/estates/fixture.json:201 | 149f8d99-1c66-4a0a-9624-759be002bb60, 20261003, 33618b8d-46eb-4fe7-b80b-122c331260a3 |
| infra/estates/fixture.json:216 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture.json:222 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture.json:243 | orderops_investigator |
| infra/estates/fixture.json:244 | ordersops |
| infra/estates/fixture.json:253 | ordersops |
| infra/estates/fixture.json:254 | orderops_investigator |
| infra/estates/fixture.json:264 | 149f8d99-1c66-4a0a-9624-759be002bb60, bea673e0-a206-461e-9b2f-1b3b827e80de |
| infra/estates/fixture.json:267 | 149f8d99-1c66-4a0a-9624-759be002bb60, bea673e0-a206-461e-9b2f-1b3b827e80de |
| infra/estates/fixture.json:273 | 149f8d99-1c66-4a0a-9624-759be002bb60, b4871498-bd35-45be-916c-9a642568012c |
| infra/estates/fixture.json:276 | 149f8d99-1c66-4a0a-9624-759be002bb60, b4871498-bd35-45be-916c-9a642568012c |
| infra/estates/fixture.json:370 | fixture |
| infra/estates/fixture.json:384 | 149f8d99-1c66-4a0a-9624-759be002bb60, b4871498-bd35-45be-916c-9a642568012c |
| infra/estates/fixture.json:385 | 149f8d99-1c66-4a0a-9624-759be002bb60, 57e128c3-6ba0-4aaf-9464-81164ecdc782 |
| infra/estates/fixture.json:406 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture.json:407 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture.json:408 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture.json:409 | database.windows.net, ordersops, sql-orderops |
| infra/estates/fixture.json:414 | fixture |
| infra/estates/fixture.json:417 | fixture |
| infra/estates/fixture.json:427 | fixture |
| infra/estates/fixture.json:428 | 7ccafe59-0460-4c8a-a691-bfdfa75a2b25 |
| infra/estates/fixture.json:438 | fixture |
| infra/estates/fixture.json:439 | 7ccafe59-0460-4c8a-a691-bfdfa75a2b25 |
| infra/estates/fixture.json:473 | d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9 |
| infra/estates/fixture.json:511 | fixture |
| infra/estates/fixture.json:518 | fixture |
| infra/estates/fixture.json:526 | fixture |
| infra/estates/fixture.json:527 | fixture |
| infra/estates/fixture.json:535 | fixture |
| infra/estates/fixture.json:541 | Warehouse |
| infra/estates/fixture.json:549 | fixture |
| infra/fabric/environment.json:2 | 09cea7db-63ec-41f0-9cf0-872a6dc5c61d |
| infra/fabric/environment.json:3 | 9d7d4a68-7f33-4a0b-8c2d-f3239eb5f6ad, lakehouse |
| infra/fabric/environment.json:4 | 3b685f1d-66c8-4323-85d3-4b86f3896b0c, lakehouse |
| infra/fabric/environment.json:5 | 8cf1c354-1677-4434-a452-1678a6b70aa4 |
| infra/fabric/environment.json:6 | 0e2514a0-33e6-4c26-b562-bb304a71f6af |
| infra/fabric/environment.json:7 | 7d169d18-02c5-468a-ad16-ad8d79156215 |
| infra/fabric/environment.json:10 | 11a2c0e9-47f6-4f48-9683-f68a69752ca0 |
| infra/fabric/environment.json:11 | 885d3567-c838-4a35-bbe2-136a5524cffe |
| infra/fabric/environment.json:12 | 63a22c91-21b2-4fb1-a41c-cc5a97ac4284 |
| infra/fabric/environment.json:13 | a3422248-584b-4bdb-8ab8-b12a90ec3074, lakehouse |
| infra/fabric/environment.json:14 | 0f60ea8d-e983-4048-bc28-48d3d2112e89 |
| infra/fabric/environment.json:15 | a05cdfd0-7e65-4c55-9a84-14d32af5aad1 |
| infra/fabric/environment.json:16 | e6559c75-d1ba-49bc-a87e-61cc47ecaf99 |
| infra/fabric/environment.json:17 | warehouse |
| infra/fabric/environment.json:18 | 701ab1fc-4a8e-48dc-92fd-8640740bb854 |
| infra/fabric/environment.json:19 | 307f3957-3002-4384-b007-2abb822cafe0 |
| infra/fabric/environment.json:20 | 5fa0e148-9455-401b-b43f-aca0009be596 |
| infra/fabric/environment.json:21 | a77a8464-06d8-42dc-9ec8-832e813346f4, semantic_model |
| infra/fabric/environment.json:23 | 0a81b8dc-7d16-46c6-ad2f-5a0bf97b92bd |
| infra/fabric/environment.json:24 | 44e960a6-d470-49e4-a791-cc9e8c5c6783 |
| infra/fabric/environment.json:25 | 5d5495a7-0385-4608-8958-c7dd12dd9a10 |
| infra/fabric/environment.json:27 | 63e0ebc6-d4e3-4544-8e9b-92c07778819e, semantic_model |
| infra/fabric/environment.json:29 | 3b9354f3-af21-4296-a936-91b4a299777a |
| infra/fabric/environment.json:32 | f7465b47-a127-49fa-91f4-24624a28aebf |
| infra/fabric/environment.json:33 | 8091da39-ff69-4a8e-ac86-7cb583270380 |
| infra/fabric/environment.json:34 | 26cedef4-8133-4446-a694-cbe8878bd3d8 |
| infra/fabric/environment.json:35 | ee41fc12-0e81-4d44-a68f-a4ce47cbdcde |
| infra/fabric/environment.json:36 | a28d6885-78a8-4f5a-b97b-59cdd90a265b |
| infra/fabric/environment.json:37 | 3b9354f3-af21-4296-a936-91b4a299777a |
| infra/fabric/environment.json:40 | 3b9354f3-af21-4296-a936-91b4a299777a |
| infra/fabric/environment.json:41 | a28d6885-78a8-4f5a-b97b-59cdd90a265b |
| infra/fabric/environment.json:42 | 885d3567-c838-4a35-bbe2-136a5524cffe |
| infra/fabric/environment.json:43 | 63a22c91-21b2-4fb1-a41c-cc5a97ac4284 |
| infra/fabric/environment.json:44 | 63a22c91-21b2-4fb1-a41c-cc5a97ac4284 |
| infra/fabric/environment.json:47 | 3b9354f3-af21-4296-a936-91b4a299777a |
| infra/fabric/environment.json:48 | 63a22c91-21b2-4fb1-a41c-cc5a97ac4284 |
| infra/fabric/environment.json:49 | a05cdfd0-7e65-4c55-9a84-14d32af5aad1 |
| infra/fabric/environment.json:50 | e6559c75-d1ba-49bc-a87e-61cc47ecaf99 |
| infra/fabric/environment.json:51 | e6559c75-d1ba-49bc-a87e-61cc47ecaf99 |
| infra/fabric/environment.json:54 | e6559c75-d1ba-49bc-a87e-61cc47ecaf99 |
| infra/fabric/environment.json:55 | 63e0ebc6-d4e3-4544-8e9b-92c07778819e |
| infra/fabric/environment.json:60 | 549f1a33-5b04-40c3-8b64-718d507e480c |
| infra/fabric/environment.json:61 | 4f443959-2657-4ca3-911a-0627441fa25f |
| infra/fabric/gold_models.py:1 | fixture |
| infra/llm/development.json:2 | d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9 |
| infra/llm/quality-evaluation.json:2 | d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9 |
| infra/llm/quality-gpt54-high.json:2 | d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9 |
| infra/llm/quality-gpt54-input-control.json:2 | d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9 |
| infra/llm/quality-gpt54-reasoning.json:2 | d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9 |
| infra/llm/quality-gpt54.json:2 | d5dd7d65-1b61-4025-b9f1-5f7b2f8d1ef9 |
| infra/metadata/development.json:4 | database.windows.net, sql-orderops |
| infra/metadata/development.json:5 | ordersops |
| infra/metadata/development.json:13 | 09cea7db-63ec-41f0-9cf0-872a6dc5c61d |
| infra/platform/platform.bicep:73 | ba92f5b4-2d11-453d-a403-e96b0029c9fe |
| infra/platform/platform.bicep:82 | 4633458b-17de-408a-b874-0445c86b69e6 |
| scripts/audit_directlake_bridge.py:32 | blob.core.windows.net, diaplatform |
| scripts/cloud_job_admission.py:22 | subscriptions/ |
| scripts/graph_scan_schedule_plan.py:17 | subscriptions/ |
| scripts/investigator/adapters/collector_schedule.py:10 | job-dia- |
| scripts/investigator/adapters/collector_schedule.py:28 | job-dia- |
| scripts/investigator/adapters/collector_schedule.py:66 | job-dia- |
| scripts/investigator/adapters/runner_deployment.py:42 | job-dia- |
| scripts/investigator/adapters/runner_deployment.py:44 | job-dia- |
| scripts/investigator/adapters/runner_deployment.py:79 | subscriptions/ |
| scripts/investigator/adapters/runner_deployment.py:81 | job-dia- |
| scripts/investigator/adapters/runner_deployment.py:125 | subscriptions/ |
| scripts/investigator/adapters/runner_graph_schedule.py:15 | job-dia- |
| scripts/investigator/adapters/runner_schedule.py:70 | subscriptions/ |
| scripts/renew_platform_cost_observation.py:14 | job-dia- |
| scripts/renew_platform_cost_observation.py:54 | subscriptions/ |
| tests/tickets/injections.md:61 | fixture, job-dia- |
| tests/tickets/injections.md:514 | job-dia- |
| tests/tickets/round22-definition-contracts.json:1 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 10431c90-79c8-4508-8c17-48ec6d08e638, 149f8d99-1c66-4a0a-9624-759be002bb60, 20261003, 220708c4-6b51-4be7-ba1a-fb91bbd09e0f, Application load fixture, SemanticModel, blob.core.windows.net, c2fe3283-9d89-4bee-b219-09de50cc38c5, diaplatform, fixture |
| tests/tickets/scored-set-v1-dev.json:1 | 20261003, Application load fixture, Warehouse, billingapp, dia-investigator, fixture, lakehouse, orderops_investigator, ordersops, semantic model, warehouse |

## test-only

| Source | Matched identifier or marker |
|---|---|
| scripts/fixtures/archived_ticket_planner.py:1 | fixture |
| scripts/fixtures/cloud-owner-demo-form.json:6 | 149f8d99-1c66-4a0a-9624-759be002bb60, 692f3ead-d1d1-4f7f-984b-51e54f3e7497 |
| scripts/fixtures/cloud-owner-demo-form.json:7 | 149f8d99-1c66-4a0a-9624-759be002bb60, 692f3ead-d1d1-4f7f-984b-51e54f3e7497 |
| scripts/fixtures/cloud-owner-demo-form.json:12 | 149f8d99-1c66-4a0a-9624-759be002bb60, 692f3ead-d1d1-4f7f-984b-51e54f3e7497 |
| scripts/fixtures/context_pin_a_failure.json:3 | fbf26f10-038a-472c-b009-48933e4e42b2 |
| scripts/fixtures/context_pin_a_failure.json:4 | 5b3eff46-631c-47b8-8211-049b5aa906ee |
| scripts/fixtures/context_pin_a_failure.json:6 | 841e425e-fe17-4bb0-9d06-b4623f49de5b |
| scripts/fixtures/context_pin_a_failure.json:9 | d3b6e8e0-7911-4e62-b3f4-2d319c6ef131 |
| scripts/fixtures/intake-nine-families.json:12 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:16 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:20 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:24 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:28 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:34 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:36 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:46 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:48 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:60 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25 |
| scripts/fixtures/intake-nine-families.json:72 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25, 91b207a5-abc8-4431-a788-f3982d720aa5, a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:75 | fixture |
| scripts/fixtures/intake-nine-families.json:238 | fixture |
| scripts/fixtures/intake-nine-families.json:252 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:253 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:270 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:274 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:278 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:282 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:286 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:292 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:294 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:304 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:306 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:318 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25 |
| scripts/fixtures/intake-nine-families.json:330 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25, 91b207a5-abc8-4431-a788-f3982d720aa5, a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:333 | fixture |
| scripts/fixtures/intake-nine-families.json:496 | fixture |
| scripts/fixtures/intake-nine-families.json:510 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:511 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:528 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:532 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:536 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:540 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:544 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:550 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:552 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:562 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:564 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:576 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25 |
| scripts/fixtures/intake-nine-families.json:588 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25, 91b207a5-abc8-4431-a788-f3982d720aa5, a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:591 | fixture |
| scripts/fixtures/intake-nine-families.json:754 | fixture |
| scripts/fixtures/intake-nine-families.json:768 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:769 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:786 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:790 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:794 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:798 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:802 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:808 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:810 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:820 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:822 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:834 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25 |
| scripts/fixtures/intake-nine-families.json:846 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25, 91b207a5-abc8-4431-a788-f3982d720aa5, a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:849 | fixture |
| scripts/fixtures/intake-nine-families.json:1012 | fixture |
| scripts/fixtures/intake-nine-families.json:1026 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:1027 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1044 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:1048 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:1052 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1056 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1060 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1066 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1068 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1078 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1080 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1092 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25 |
| scripts/fixtures/intake-nine-families.json:1104 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25, 91b207a5-abc8-4431-a788-f3982d720aa5, a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:1107 | fixture |
| scripts/fixtures/intake-nine-families.json:1270 | fixture |
| scripts/fixtures/intake-nine-families.json:1284 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:1285 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1302 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:1306 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:1310 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1314 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1318 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1324 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1326 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1336 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1338 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1350 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25 |
| scripts/fixtures/intake-nine-families.json:1362 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25, 91b207a5-abc8-4431-a788-f3982d720aa5, a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:1365 | fixture |
| scripts/fixtures/intake-nine-families.json:1528 | fixture |
| scripts/fixtures/intake-nine-families.json:1542 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:1543 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1560 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:1564 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:1568 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1572 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1576 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1582 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1584 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1594 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1596 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1608 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25 |
| scripts/fixtures/intake-nine-families.json:1620 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25, 91b207a5-abc8-4431-a788-f3982d720aa5, a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:1623 | fixture |
| scripts/fixtures/intake-nine-families.json:1786 | fixture |
| scripts/fixtures/intake-nine-families.json:1800 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:1801 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1818 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:1822 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:1826 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1830 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1834 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1840 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1842 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1852 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1854 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:1866 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25 |
| scripts/fixtures/intake-nine-families.json:1878 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25, 91b207a5-abc8-4431-a788-f3982d720aa5, a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:1881 | fixture |
| scripts/fixtures/intake-nine-families.json:2044 | fixture |
| scripts/fixtures/intake-nine-families.json:2058 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:2059 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2076 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:2080 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:2084 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2088 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2092 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2098 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2100 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2110 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2112 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2124 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25 |
| scripts/fixtures/intake-nine-families.json:2136 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25, 91b207a5-abc8-4431-a788-f3982d720aa5, a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:2139 | fixture |
| scripts/fixtures/intake-nine-families.json:2302 | fixture |
| scripts/fixtures/intake-nine-families.json:2316 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:2317 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2334 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:2338 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:2342 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2346 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2350 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2356 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2358 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2368 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2370 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2382 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25 |
| scripts/fixtures/intake-nine-families.json:2394 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25, 91b207a5-abc8-4431-a788-f3982d720aa5, a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:2397 | fixture |
| scripts/fixtures/intake-nine-families.json:2560 | fixture |
| scripts/fixtures/intake-nine-families.json:2592 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:2596 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:2600 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2604 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2608 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2614 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2616 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2626 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2628 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2640 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25 |
| scripts/fixtures/intake-nine-families.json:2652 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25, 91b207a5-abc8-4431-a788-f3982d720aa5, a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:2655 | fixture |
| scripts/fixtures/intake-nine-families.json:2818 | fixture |
| scripts/fixtures/intake-nine-families.json:2850 | 50780c14-5261-43be-8163-e1e2e41e49c1 |
| scripts/fixtures/intake-nine-families.json:2854 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:2858 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2862 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2866 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2872 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2874 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2884 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2886 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2898 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25 |
| scripts/fixtures/intake-nine-families.json:2909 | a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:2927 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2929 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2939 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2941 | 143721df-0bf8-44df-8f30-721b04a345da, 91b207a5-abc8-4431-a788-f3982d720aa5 |
| scripts/fixtures/intake-nine-families.json:2965 | 143721df-0bf8-44df-8f30-721b04a345da, 81f0f144-0a7b-4643-9794-a7de51678b25, 91b207a5-abc8-4431-a788-f3982d720aa5, a9309e4c-15b1-4841-9051-f7ddff64d42c |
| scripts/fixtures/intake-nine-families.json:2968 | fixture |
| scripts/fixtures/intake-nine-families.json:3139 | fixture |
| scripts/fixtures/planner-view/directory-coverage.json:6 | Lakehouse |
| scripts/fixtures/planner-view/directory-coverage.json:12 | Lakehouse |
| scripts/fixtures/planner-view/directory-coverage.json:18 | Lakehouse |
| scripts/fixtures/planner-view/directory-coverage.json:24 | Lakehouse |
| scripts/fixtures/planner-view/directory-coverage.json:30 | Lakehouse |
| scripts/fixtures/planner-view/directory-coverage.json:36 | Lakehouse |
| scripts/fixtures/planner-view/directory-coverage.json:42 | Lakehouse |
| scripts/fixtures/planner-view/directory-coverage.json:48 | Lakehouse |
| scripts/fixtures/planner-view/directory-coverage.json:54 | Lakehouse |
| scripts/fixtures/planner-view/directory-coverage.json:60 | Lakehouse |
| scripts/fixtures/planner-view/directory-coverage.json:66 | Lakehouse |
| scripts/fixtures/planner-view/directory-coverage.json:72 | Lakehouse |
| scripts/fixtures/planner-view/expected.json:14 | workspace/ |
| scripts/fixtures/planner-view/expected.json:22 | workspace/ |
| scripts/fixtures/planner-view/expected.json:25 | workspace/ |
| scripts/fixtures/planner-view/expected.json:69 | workspace/ |
| scripts/fixtures/planner-view/expected.json:72 | workspace/ |
| scripts/fixtures/planner-view/expected.json:100 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:14 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:22 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:23 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:24 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:25 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:26 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:27 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:28 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:29 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:32 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:33 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:34 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:35 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:36 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:37 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:38 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:39 | workspace/ |
| scripts/fixtures/planner-view/inputs.json:60 | workspace/ |
| scripts/fixtures/round-six-declared-copy-verification.json:8 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/fixtures/round-six-declared-copy-verification.json:10 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/fixtures/round-six-declared-copy-verification.json:12 | a64b0401-bb16-42ec-bb87-64b5ae90a044 |
| scripts/fixtures/round-six-declared-copy-verification.json:23 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/fixtures/round-six-declared-copy-verification.json:25 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/fixtures/round-six-declared-copy-verification.json:27 | a64b0401-bb16-42ec-bb87-64b5ae90a044 |
| scripts/fixtures/round-six-declared-copy-verification.json:31 | a64b0401-bb16-42ec-bb87-64b5ae90a044 |
| scripts/fixtures/round-six-declared-copy-verification.json:40 | warehouse |
| scripts/fixtures/round-six-declared-copy-verification.json:41 | Warehouse |
| scripts/fixtures/round-six-declared-copy-verification.json:42 | skynwhy.com |
| scripts/fixtures/round-six-declared-copy-verification.json:43 | 20261003 |
| scripts/fixtures/round-six-declared-copy-verification.json:45 | 9dd10fc1-2505-4420-a503-3366c37d8a11 |
| scripts/fixtures/round-six-declared-copy-verification.json:50 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/fixtures/round-six-declared-copy-verification.json:56 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/fixtures/round-six-declared-copy-verification.json:58 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/fixtures/round-six-declared-copy-verification.json:91 | Warehouse |
| scripts/fixtures/round-six-declared-copy-verification.json:92 | skynwhy.com |
| scripts/fixtures/round-six-declared-copy-verification.json:93 | 20261003 |
| scripts/fixtures/round-six-declared-copy-verification.json:96 | 9dd10fc1-2505-4420-a503-3366c37d8a11 |
| scripts/fixtures/round-six-declared-copy-verification.json:130 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/fixtures/round-six-declared-copy-verification.json:132 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/fixtures/round-six-declared-copy-verification.json:134 | a64b0401-bb16-42ec-bb87-64b5ae90a044 |
| scripts/fixtures/round-six-declared-copy-verification.json:137 | a64b0401-bb16-42ec-bb87-64b5ae90a044 |
| scripts/fixtures/round-six-declared-copy-verification.json:139 | database.windows.net, sql-orderops |
| scripts/fixtures/round-six-declared-copy-verification.json:141 | orderops_investigator |
| scripts/fixtures/round-six-declared-copy-verification.json:142 | ordersops |
| scripts/fixtures/round-six-declared-copy-verification.json:144 | 71bf8923-a468-4907-a721-0873a0e4373e |
| scripts/fixtures/round-six-declared-copy-verification.json:145 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/fixtures/round-six-declared-copy-verification.json:151 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/fixtures/round-six-declared-copy-verification.json:153 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6, 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/fixtures/round-six-declared-copy-verification.json:187 | orderops_investigator |
| scripts/fixtures/round-six-declared-copy-verification.json:188 | ordersops |
| scripts/fixtures/round-six-declared-copy-verification.json:191 | 71bf8923-a468-4907-a721-0873a0e4373e |
| scripts/fixtures/round-six-declared-copy-verification.json:236 | database.windows.net, ordersops, sql-orderops |
| scripts/fixtures/round-six-declared-copy-verification.json:243 | 149f8d99-1c66-4a0a-9624-759be002bb60, 57e128c3-6ba0-4aaf-9464-81164ecdc782 |
| scripts/fixtures/round-six-declared-copy-verification.json:253 | database.windows.net, ordersops, sql-orderops |
| scripts/fixtures/round-six-declared-copy-verification.json:258 | 149f8d99-1c66-4a0a-9624-759be002bb60, 20261003, 33618b8d-46eb-4fe7-b80b-122c331260a3 |
| scripts/fixtures/round-six-declared-copy-verification.json:270 | Warehouse |
| scripts/fixtures/round-six-declared-copy-verification.json:275 | 20261003 |
| scripts/fixtures/round-six-declared-copy-verification.json:276 | 20261003 |
| scripts/fixtures/round-six-declared-copy-verification.json:279 | 20261003 |
| scripts/fixtures/round-six-declared-copy-verification.json:280 | ordersops |
| scripts/fixtures/round27-retired-ablations/test_declared_source_comparison.py.txt:9 | fixture |
| scripts/fixtures/round27-retired-ablations/test_declared_source_comparison.py.txt:24 | fixture |
| scripts/fixtures/round27-retired-ablations/test_declared_source_comparison.py.txt:33 | fixture |
| scripts/fixtures/round27-retired-ablations/test_declared_source_comparison.py.txt:44 | fixture |
| scripts/fixtures/round27-retired-ablations/test_declared_source_comparison.py.txt:47 | fixture |
| scripts/fixtures/round27-retired-ablations/test_declared_source_comparison.py.txt:51 | fixture |
| scripts/fixtures/round27-retired-ablations/test_record_arrival_history.py.txt:24 | warehouse |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:15 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:22 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:31 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:35 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:42 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:45 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:48 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:64 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:67 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:70 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:73 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:76 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:80 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:89 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_analysis_projection.py.txt:93 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_candidate_native_pruning.py.txt:5 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_candidate_native_pruning.py.txt:10 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_consistency_feedback.py.txt:9 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_consistency_feedback.py.txt:16 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_consistency_feedback.py.txt:19 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_consistency_feedback.py.txt:26 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_consistency_feedback.py.txt:29 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_consistency_feedback.py.txt:35 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_consistency_feedback.py.txt:38 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_consistency_feedback.py.txt:43 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_consistency_feedback.py.txt:46 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_consistency_feedback.py.txt:49 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_native_table_reference.py.txt:58 | Warehouse |
| scripts/fixtures/round27-retired-ablations/test_round27_scope_verdict.py.txt:6 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_scope_verdict.py.txt:8 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_scope_verdict.py.txt:25 | fixture |
| scripts/fixtures/round27-retired-ablations/test_round27_scope_verdict.py.txt:32 | fixture |
| scripts/fixtures/round_fourteen/false-duplicate-report-questions.json:4 | workspace/ |
| scripts/fixtures/round_six_i_empty_same_referent.json:2 | 4b2965df-b9cc-49e7-9645-9e2938151f7b |
| scripts/fixtures/round_six_i_empty_same_referent.json:5 | fixture, warehouse |
| scripts/fixtures/round_ten/business-intent-sealed-excerpt.json:7 | 5b3eff46-631c-47b8-8211-049b5aa906ee |
| scripts/fixtures/round_ten/business-intent-sealed-excerpt.json:8 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e |
| scripts/fixtures/round_ten/business-intent-sealed-excerpt.json:29 | 149f8d99-1c66-4a0a-9624-759be002bb60, 692f3ead-d1d1-4f7f-984b-51e54f3e7497 |
| scripts/fixtures/round_ten/business-intent-sealed-excerpt.json:38 | 149f8d99-1c66-4a0a-9624-759be002bb60, 692f3ead-d1d1-4f7f-984b-51e54f3e7497 |
| scripts/fixtures/round_ten/wrong-cell-sealed-excerpt.json:7 | 5b3eff46-631c-47b8-8211-049b5aa906ee |
| scripts/fixtures/round_ten/wrong-cell-sealed-excerpt.json:8 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e |
| scripts/fixtures/round_ten/wrong-cell-sealed-excerpt.json:49 | 149f8d99-1c66-4a0a-9624-759be002bb60, 95b6d455-9150-4738-983d-ca6e7e0f3719 |
| scripts/fixtures/round_ten/wrong-cell-sealed-excerpt.json:58 | 149f8d99-1c66-4a0a-9624-759be002bb60, 95b6d455-9150-4738-983d-ca6e7e0f3719 |
| scripts/fixtures/round_ten/wrong-cell-sealed-excerpt.json:70 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e |
| scripts/fixtures/round_ten/wrong-cell-sealed-excerpt.json:71 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e, warehouse |
| scripts/fixtures/round_ten/wrong-cell-sealed-excerpt.json:75 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e |
| scripts/fixtures/round_ten/wrong-cell-sealed-excerpt.json:77 | 149f8d99-1c66-4a0a-9624-759be002bb60, 95b6d455-9150-4738-983d-ca6e7e0f3719 |
| scripts/fixtures/sql_group_binding.json:2 | 39503ca8-e318-493f-a6d1-201563c0b444 |
| scripts/fixtures/sql_group_binding.json:4 | warehouse |
| scripts/fixtures/sql_group_binding.json:8 | warehouse |
| scripts/fixtures/synthesis_failures_226.json:6 | 17095597-a4ce-4b70-a918-a4036302a91c, 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f, 34f5188b-c6f8-46aa-b12c-1b54d8862be1, 3572cdc8-30ee-405c-a418-7dbb621af21d, e546c474-87d7-4c6f-a2ce-97800c8a0353 |
| scripts/fixtures/synthesis_failures_226.json:8 | 17095597-a4ce-4b70-a918-a4036302a91c |
| scripts/fixtures/synthesis_failures_226.json:9 | 3572cdc8-30ee-405c-a418-7dbb621af21d |
| scripts/fixtures/synthesis_failures_226.json:10 | 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f |
| scripts/fixtures/synthesis_failures_226.json:11 | 34f5188b-c6f8-46aa-b12c-1b54d8862be1 |
| scripts/fixtures/synthesis_failures_226.json:12 | e546c474-87d7-4c6f-a2ce-97800c8a0353 |
| scripts/fixtures/synthesis_failures_226.json:15 | 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f, 34f5188b-c6f8-46aa-b12c-1b54d8862be1, e546c474-87d7-4c6f-a2ce-97800c8a0353 |
| scripts/fixtures/synthesis_failures_226.json:16 | 17095597-a4ce-4b70-a918-a4036302a91c, 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f |
| scripts/fixtures/synthesis_failures_226.json:17 | 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f, 34f5188b-c6f8-46aa-b12c-1b54d8862be1 |
| scripts/fixtures/synthesis_failures_226.json:20 | 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f, 34f5188b-c6f8-46aa-b12c-1b54d8862be1, e546c474-87d7-4c6f-a2ce-97800c8a0353 |
| scripts/fixtures/synthesis_failures_226.json:21 | 17095597-a4ce-4b70-a918-a4036302a91c |
| scripts/fixtures/synthesis_failures_226.json:22 | 3572cdc8-30ee-405c-a418-7dbb621af21d |
| scripts/fixtures/synthesis_failures_226.json:25 | 17095597-a4ce-4b70-a918-a4036302a91c, 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f, 34f5188b-c6f8-46aa-b12c-1b54d8862be1, 3572cdc8-30ee-405c-a418-7dbb621af21d, e546c474-87d7-4c6f-a2ce-97800c8a0353, lakehouse |
| scripts/fixtures/synthesis_failures_226.json:27 | 3572cdc8-30ee-405c-a418-7dbb621af21d |
| scripts/fixtures/synthesis_failures_226.json:28 | 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f |
| scripts/fixtures/synthesis_failures_226.json:29 | 34f5188b-c6f8-46aa-b12c-1b54d8862be1 |
| scripts/fixtures/synthesis_failures_226.json:30 | e546c474-87d7-4c6f-a2ce-97800c8a0353 |
| scripts/fixtures/synthesis_failures_226.json:31 | 17095597-a4ce-4b70-a918-a4036302a91c |
| scripts/fixtures/synthesis_failures_226.json:34 | 17095597-a4ce-4b70-a918-a4036302a91c, 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f, 34f5188b-c6f8-46aa-b12c-1b54d8862be1, 3572cdc8-30ee-405c-a418-7dbb621af21d, e546c474-87d7-4c6f-a2ce-97800c8a0353 |
| scripts/fixtures/synthesis_failures_226.json:36 | 17095597-a4ce-4b70-a918-a4036302a91c |
| scripts/fixtures/synthesis_failures_226.json:37 | 3572cdc8-30ee-405c-a418-7dbb621af21d |
| scripts/fixtures/synthesis_failures_226.json:38 | 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f |
| scripts/fixtures/synthesis_failures_226.json:39 | 34f5188b-c6f8-46aa-b12c-1b54d8862be1 |
| scripts/fixtures/synthesis_failures_226.json:40 | e546c474-87d7-4c6f-a2ce-97800c8a0353 |
| scripts/fixtures/synthesis_failures_226.json:43 | 17095597-a4ce-4b70-a918-a4036302a91c, 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f, 34f5188b-c6f8-46aa-b12c-1b54d8862be1, e546c474-87d7-4c6f-a2ce-97800c8a0353 |
| scripts/fixtures/synthesis_failures_226.json:45 | 17095597-a4ce-4b70-a918-a4036302a91c |
| scripts/fixtures/synthesis_failures_226.json:46 | 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f |
| scripts/fixtures/synthesis_failures_226.json:47 | 34f5188b-c6f8-46aa-b12c-1b54d8862be1 |
| scripts/fixtures/synthesis_failures_226.json:48 | e546c474-87d7-4c6f-a2ce-97800c8a0353 |
| scripts/fixtures/synthesis_failures_226.json:50 | 17095597-a4ce-4b70-a918-a4036302a91c, 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f, 34f5188b-c6f8-46aa-b12c-1b54d8862be1, e546c474-87d7-4c6f-a2ce-97800c8a0353 |
| scripts/fixtures/synthesis_failures_226.json:56 | 17095597-a4ce-4b70-a918-a4036302a91c |
| scripts/fixtures/synthesis_failures_226.json:61 | 3572cdc8-30ee-405c-a418-7dbb621af21d |
| scripts/fixtures/synthesis_failures_226.json:66 | 31e40b4c-fcbf-4f49-950d-ddc6cb385d2f |
| scripts/fixtures/synthesis_failures_226.json:71 | 34f5188b-c6f8-46aa-b12c-1b54d8862be1 |
| scripts/fixtures/synthesis_failures_226.json:76 | e546c474-87d7-4c6f-a2ce-97800c8a0353 |
| scripts/fixtures/synthesis_failures_226.json:89 | 51fbcb22-d034-4c3c-b48f-6215feda523f |
| scripts/fixtures/synthesis_failures_226.json:90 | 55945f94-a8f6-45a9-bb66-22e91b4eaea5 |
| scripts/fixtures/synthesis_failures_226.json:91 | 98347cc7-9997-4d1d-85dc-181e37046349 |
| scripts/fixtures/synthesis_failures_226.json:107 | 51fbcb22-d034-4c3c-b48f-6215feda523f |
| scripts/fixtures/synthesis_failures_226.json:108 | 55945f94-a8f6-45a9-bb66-22e91b4eaea5 |
| scripts/fixtures/synthesis_failures_226.json:109 | 98347cc7-9997-4d1d-85dc-181e37046349 |
| scripts/fixtures/synthesis_failures_226.json:114 | 65a94fc4-adbd-4c93-b497-0a465dcb801e |
| scripts/fixtures/synthesis_failures_226.json:119 | 65a94fc4-adbd-4c93-b497-0a465dcb801e |
| scripts/fixtures/synthesis_failures_226.json:120 | f725d2bc-80e9-40be-ac6d-18b9f9204ef7 |
| scripts/fixtures/synthesis_failures_226.json:121 | dac4543c-983a-4664-babe-23459b289d15 |
| scripts/fixtures/synthesis_failures_226.json:129 | 65a94fc4-adbd-4c93-b497-0a465dcb801e |
| scripts/fixtures/synthesis_failures_226.json:134 | 1424e6f4-26cb-4528-a801-8f707334fceb |
| scripts/fixtures/synthesis_failures_226.json:139 | 62d5704f-c9d6-40d4-a64e-a1d44a0394dc |
| scripts/fixtures/synthesis_failures_226.json:144 | f725d2bc-80e9-40be-ac6d-18b9f9204ef7 |
| scripts/fixtures/synthesis_failures_226.json:149 | dac4543c-983a-4664-babe-23459b289d15 |
| scripts/fixtures/synthesis_failures_226.json:154 | 51fbcb22-d034-4c3c-b48f-6215feda523f |
| scripts/fixtures/synthesis_failures_226.json:159 | 55945f94-a8f6-45a9-bb66-22e91b4eaea5 |
| scripts/fixtures/synthesis_failures_226.json:164 | d02de7aa-1702-4a73-834d-dbe8c5a12413 |
| scripts/fixtures/synthesis_failures_226.json:169 | 98347cc7-9997-4d1d-85dc-181e37046349 |
| scripts/fixtures/synthesis_failures_226.json:174 | e285ceae-0853-429c-921f-0bf611a8aaf5 |
| scripts/fixtures/synthesis_failures_226.json:187 | e78ae96d-1362-4b05-99ba-bc2f0df7c581 |
| scripts/fixtures/synthesis_failures_226.json:188 | 8b13b0cd-ebf0-46c4-967b-db8515b33f88 |
| scripts/fixtures/synthesis_failures_226.json:189 | 1052471d-5f7e-41e8-b1ec-2f27cfd807e7 |
| scripts/fixtures/synthesis_failures_226.json:190 | 8cbd04e2-1320-4ce9-b566-2f0aa69abe9f |
| scripts/fixtures/synthesis_failures_226.json:203 | warehouse |
| scripts/fixtures/synthesis_failures_226.json:205 | e78ae96d-1362-4b05-99ba-bc2f0df7c581 |
| scripts/fixtures/synthesis_failures_226.json:206 | 8b13b0cd-ebf0-46c4-967b-db8515b33f88 |
| scripts/fixtures/synthesis_failures_226.json:207 | 1052471d-5f7e-41e8-b1ec-2f27cfd807e7 |
| scripts/fixtures/synthesis_failures_226.json:208 | 8cbd04e2-1320-4ce9-b566-2f0aa69abe9f |
| scripts/fixtures/synthesis_failures_226.json:213 | 9433c33f-2ff8-4ccc-b786-d523a7ab84b2 |
| scripts/fixtures/synthesis_failures_226.json:214 | 1052471d-5f7e-41e8-b1ec-2f27cfd807e7 |
| scripts/fixtures/synthesis_failures_226.json:219 | 9433c33f-2ff8-4ccc-b786-d523a7ab84b2 |
| scripts/fixtures/synthesis_failures_226.json:227 | 9433c33f-2ff8-4ccc-b786-d523a7ab84b2 |
| scripts/fixtures/synthesis_failures_226.json:232 | 8628aee9-8ac6-4dfe-ab6d-79119689072f |
| scripts/fixtures/synthesis_failures_226.json:237 | fb791247-6346-43d1-a023-f849494ce7de |
| scripts/fixtures/synthesis_failures_226.json:242 | e78ae96d-1362-4b05-99ba-bc2f0df7c581 |
| scripts/fixtures/synthesis_failures_226.json:247 | 1052471d-5f7e-41e8-b1ec-2f27cfd807e7 |
| scripts/fixtures/synthesis_failures_226.json:252 | 8b13b0cd-ebf0-46c4-967b-db8515b33f88 |
| scripts/fixtures/synthesis_failures_226.json:257 | 7ecec9b7-0a54-4c8c-8c46-d27e2b350dfd |
| scripts/fixtures/synthesis_failures_226.json:262 | bbf78455-17d9-4fbb-926c-5daf91dcbbb6 |
| scripts/fixtures/synthesis_failures_226.json:267 | 9f9c3bad-d797-4f4a-86d3-0e977a258f42 |
| scripts/fixtures/synthesis_failures_226.json:272 | 9680548d-3183-411a-902c-ca2d5a689d3f |
| scripts/fixtures/synthesis_failures_226.json:277 | 4f152469-e448-4b2d-8dd7-f2f5b0943d6d |
| scripts/fixtures/synthesis_failures_226.json:282 | 8cbd04e2-1320-4ce9-b566-2f0aa69abe9f |
| scripts/fixtures/synthesis_failures_226.json:287 | b5216903-fff3-423a-9a5c-a712365f1e9f |
| scripts/fixtures/synthesis_failures_226.json:298 | warehouse |
| scripts/fixtures/synthesis_failures_226.json:300 | 292489c6-80c3-4be8-97f2-1c65b6d1f3e6 |
| scripts/fixtures/synthesis_failures_226.json:301 | c0b0ebc9-b7e0-465b-8790-7221187a05fc |
| scripts/fixtures/synthesis_failures_226.json:302 | 8f190552-83a1-4bd1-80c1-a7014de81966 |
| scripts/fixtures/synthesis_failures_226.json:303 | 97127552-8e69-4316-9950-821b22dd1cbb |
| scripts/fixtures/synthesis_failures_226.json:304 | bb367a25-a0b1-484e-95f9-3b173471caba |
| scripts/fixtures/synthesis_failures_226.json:305 | 95becf16-9e49-4a5b-833e-63d5026f8cb5 |
| scripts/fixtures/synthesis_failures_226.json:309 | warehouse |
| scripts/fixtures/synthesis_failures_226.json:313 | 51e7ec42-ef1f-4d00-b02e-ee022e9049b1 |
| scripts/fixtures/synthesis_failures_226.json:318 | warehouse |
| scripts/fixtures/synthesis_failures_226.json:320 | 292489c6-80c3-4be8-97f2-1c65b6d1f3e6 |
| scripts/fixtures/synthesis_failures_226.json:321 | c0b0ebc9-b7e0-465b-8790-7221187a05fc |
| scripts/fixtures/synthesis_failures_226.json:322 | 8f190552-83a1-4bd1-80c1-a7014de81966 |
| scripts/fixtures/synthesis_failures_226.json:323 | bb367a25-a0b1-484e-95f9-3b173471caba |
| scripts/fixtures/synthesis_failures_226.json:324 | 95becf16-9e49-4a5b-833e-63d5026f8cb5 |
| scripts/fixtures/synthesis_failures_226.json:329 | 8f190552-83a1-4bd1-80c1-a7014de81966 |
| scripts/fixtures/synthesis_failures_226.json:330 | 97127552-8e69-4316-9950-821b22dd1cbb |
| scripts/fixtures/synthesis_failures_226.json:331 | aaa5dc3e-abea-4768-819d-def2c7390daa |
| scripts/fixtures/synthesis_failures_226.json:336 | 51e7ec42-ef1f-4d00-b02e-ee022e9049b1 |
| scripts/fixtures/synthesis_failures_226.json:344 | 51e7ec42-ef1f-4d00-b02e-ee022e9049b1 |
| scripts/fixtures/synthesis_failures_226.json:349 | f33c1f05-91e5-482a-8357-36f182177915 |
| scripts/fixtures/synthesis_failures_226.json:354 | 402689d6-ed41-4266-b9f5-ec25673a3f3f |
| scripts/fixtures/synthesis_failures_226.json:359 | 703fb07a-b534-44a7-b47d-3cd3cada1c5e |
| scripts/fixtures/synthesis_failures_226.json:364 | 292489c6-80c3-4be8-97f2-1c65b6d1f3e6 |
| scripts/fixtures/synthesis_failures_226.json:369 | c0b0ebc9-b7e0-465b-8790-7221187a05fc |
| scripts/fixtures/synthesis_failures_226.json:374 | 8f190552-83a1-4bd1-80c1-a7014de81966 |
| scripts/fixtures/synthesis_failures_226.json:379 | 97127552-8e69-4316-9950-821b22dd1cbb |
| scripts/fixtures/synthesis_failures_226.json:384 | aaa5dc3e-abea-4768-819d-def2c7390daa |
| scripts/fixtures/synthesis_failures_226.json:389 | bb367a25-a0b1-484e-95f9-3b173471caba |
| scripts/fixtures/synthesis_failures_226.json:394 | 95becf16-9e49-4a5b-833e-63d5026f8cb5 |
| scripts/test_acceptance_context.py:9 | fixture |
| scripts/test_acceptance_context.py:10 | fixture |
| scripts/test_acceptance_context.py:13 | fixture |
| scripts/test_acceptance_context.py:16 | fixture |
| scripts/test_acceptance_context.py:18 | fixture |
| scripts/test_acceptance_context.py:21 | fixture |
| scripts/test_acceptance_context.py:22 | fixture |
| scripts/test_acceptance_context.py:29 | fixture |
| scripts/test_acceptance_context.py:30 | fixture |
| scripts/test_acceptance_context.py:34 | fixture |
| scripts/test_acceptance_context.py:35 | fixture |
| scripts/test_acceptance_context.py:38 | fixture |
| scripts/test_acceptance_context.py:39 | fixture |
| scripts/test_acceptance_context.py:40 | 00000000-0000-4000-8000-000000000003 |
| scripts/test_acceptance_context.py:41 | fixture |
| scripts/test_acceptance_context.py:42 | fixture |
| scripts/test_acceptance_context.py:44 | fixture |
| scripts/test_acceptance_context.py:47 | fixture |
| scripts/test_acceptance_context.py:49 | fixture |
| scripts/test_access_budget_policy.py:23 | id-dia |
| scripts/test_access_budget_policy.py:24 | id-dia |
| scripts/test_access_budget_policy.py:28 | id-dia, postgres.database.azure.com |
| scripts/test_access_check.py:17 | fixture |
| scripts/test_access_check.py:40 | fixture |
| scripts/test_access_check.py:70 | fixture |
| scripts/test_access_check.py:88 | 248525da-278c-4a6c-b5c3-cc3e7728d3ce |
| scripts/test_access_check.py:90 | billingapp, ordersops |
| scripts/test_access_check.py:105 | database.windows.net |
| scripts/test_action_budget.py:10 | fixture |
| scripts/test_action_budget.py:11 | fixture |
| scripts/test_action_budget.py:43 | fixture |
| scripts/test_action_budget.py:48 | fixture |
| scripts/test_action_budget.py:60 | fixture |
| scripts/test_action_budget.py:74 | fixture |
| scripts/test_action_budget.py:84 | fixture |
| scripts/test_action_budget.py:91 | fixture |
| scripts/test_adaptive_investigation.py:6 | fixture |
| scripts/test_adaptive_investigation.py:7 | fixture |
| scripts/test_adaptive_investigation.py:22 | fixture |
| scripts/test_adaptive_investigation.py:29 | fixture |
| scripts/test_agent_intake_settlement.py:8 | fixture |
| scripts/test_agent_intake_settlement.py:14 | fixture |
| scripts/test_agent_intake_settlement.py:17 | 00000000-0000-0000-0000-000000000001, 00000000-0000-0000-0000-000000000002 |
| scripts/test_agent_intake_settlement.py:19 | 00000000-0000-0000-0000-000000000003 |
| scripts/test_agent_intake_settlement.py:20 | 00000000-0000-0000-0000-000000000004 |
| scripts/test_agent_intake_settlement.py:32 | fixture |
| scripts/test_agent_intake_settlement.py:60 | Warehouse |
| scripts/test_agent_intake_settlement.py:61 | Warehouse |
| scripts/test_agent_intake_tools.py:10 | fixture |
| scripts/test_agent_intake_tools.py:11 | fixture |
| scripts/test_agent_intake_tools.py:12 | fixture |
| scripts/test_agent_resume_api.py:12 | fixture |
| scripts/test_agent_resume_api.py:15 | workspace/ |
| scripts/test_agent_resume_api.py:27 | workspace/ |
| scripts/test_agent_resume_api.py:35 | workspace/ |
| scripts/test_agent_resume_api.py:43 | fixture |
| scripts/test_agent_resume_api.py:63 | workspace/ |
| scripts/test_agent_resume_api.py:79 | fixture |
| scripts/test_agent_resume_api.py:84 | workspace/ |
| scripts/test_agent_resume_api.py:101 | workspace/ |
| scripts/test_agent_resume_api.py:115 | workspace/ |
| scripts/test_agent_resume_api.py:130 | fixture |
| scripts/test_agent_resume_api.py:131 | workspace/ |
| scripts/test_agent_resume_api.py:134 | fixture |
| scripts/test_agent_resume_api.py:149 | fixture |
| scripts/test_agent_resume_api.py:150 | workspace/ |
| scripts/test_agent_resume_api.py:153 | fixture |
| scripts/test_agent_resume_api.py:164 | fixture |
| scripts/test_agent_resume_api.py:165 | workspace/ |
| scripts/test_agent_resume_capture.py:10 | fixture |
| scripts/test_agent_resume_capture.py:16 | fixture |
| scripts/test_agent_ticket.py:13 | fixture |
| scripts/test_agent_ticket.py:14 | fixture |
| scripts/test_agent_ticket.py:22 | fixture |
| scripts/test_agent_ticket.py:23 | fixture |
| scripts/test_agent_ticket.py:24 | fixture |
| scripts/test_agent_ticket.py:37 | fixture |
| scripts/test_agent_ticket.py:63 | fixture |
| scripts/test_agent_ticket.py:92 | fixture |
| scripts/test_agent_ticket.py:94 | fixture |
| scripts/test_agent_ticket.py:180 | fixture |
| scripts/test_agent_ticket.py:182 | fixture |
| scripts/test_agent_ticket.py:183 | fixture |
| scripts/test_agent_ticket.py:187 | fixture |
| scripts/test_agent_ticket.py:201 | fixture |
| scripts/test_agent_ticket.py:205 | fixture |
| scripts/test_agent_ticket.py:209 | fixture |
| scripts/test_agent_ticket.py:211 | fixture |
| scripts/test_agent_ticket.py:212 | fixture |
| scripts/test_agent_ticket.py:213 | fixture |
| scripts/test_agent_ticket.py:224 | fixture |
| scripts/test_agent_ticket.py:226 | fixture |
| scripts/test_agent_ticket.py:227 | fixture |
| scripts/test_agent_ticket.py:230 | fixture |
| scripts/test_agent_ticket.py:245 | fixture |
| scripts/test_application_quantity.py:4 | fixture |
| scripts/test_application_quantity.py:12 | fixture |
| scripts/test_application_quantity.py:13 | fixture |
| scripts/test_application_quantity.py:14 | fixture |
| scripts/test_application_quantity.py:18 | Lakehouse |
| scripts/test_application_quantity.py:81 | fixture |
| scripts/test_application_quantity.py:105 | fixture |
| scripts/test_approved_categorical_replay.py:17 | fixture |
| scripts/test_approved_categorical_replay.py:40 | fixture |
| scripts/test_archive_background.py:84 | fixture |
| scripts/test_archive_migration.py:45 | fixture |
| scripts/test_archive_migration.py:51 | Fixture |
| scripts/test_archive_migration.py:57 | fixture |
| scripts/test_archive_migration.py:176 | fixture |
| scripts/test_archive_migration.py:193 | fixture |
| scripts/test_archive_migration.py:288 | fixture |
| scripts/test_archive_runtime_references.py:8 | 08086928-0113-4a0c-9c4e-8061f3980b14 |
| scripts/test_archive_runtime_references.py:20 | 08086928-0113-4a0c-9c4e-8061f3980b14 |
| scripts/test_arithmetic_routing.py:22 | Fixture |
| scripts/test_artifact_identity_cache.py:9 | 12345678-1234-1234-1234-123456789abc, 22345678-1234-1234-1234-123456789abc |
| scripts/test_artifact_store.py:24 | fixture |
| scripts/test_batched_database_audit.py:26 | fixture |
| scripts/test_batched_database_audit.py:28 | fixture |
| scripts/test_batched_database_audit.py:29 | fixture |
| scripts/test_batched_database_audit.py:58 | fixture |
| scripts/test_batched_database_audit.py:62 | fixture |
| scripts/test_batched_database_audit.py:96 | fixture |
| scripts/test_batched_database_audit.py:100 | fixture |
| scripts/test_billing_figure_occurrences.py:6 | fixture |
| scripts/test_billing_figure_occurrences.py:31 | fixture |
| scripts/test_billing_figure_occurrences.py:36 | fixture |
| scripts/test_billing_shared_intake.py:5 | fixture |
| scripts/test_billing_shared_intake.py:26 | fixture |
| scripts/test_billing_shared_intake.py:37 | fixture |
| scripts/test_billing_shared_intake.py:48 | fixture |
| scripts/test_billing_shared_intake.py:54 | fixture |
| scripts/test_binding_catalog.py:13 | Warehouse |
| scripts/test_binding_catalog.py:36 | Warehouse |
| scripts/test_binding_sample.py:168 | fixture |
| scripts/test_bronze_publication.py:11 | fixture |
| scripts/test_bronze_publication.py:23 | fixture |
| scripts/test_bronze_publication.py:29 | fixture |
| scripts/test_bronze_publication.py:33 | fixture |
| scripts/test_bronze_publication.py:35 | fixture |
| scripts/test_budget_connection.py:48 | Fixture |
| scripts/test_budget_connection.py:51 | Fixture |
| scripts/test_budget_delta.py:9 | fixture |
| scripts/test_budget_delta.py:103 | fixture |
| scripts/test_budget_delta.py:129 | fixture |
| scripts/test_budget_delta_v2.py:7 | fixture |
| scripts/test_budget_delta_v2.py:142 | fixture |
| scripts/test_budget_delta_v2.py:168 | fixture |
| scripts/test_budget_replay_transaction.py:13 | fixture |
| scripts/test_budget_replay_transaction.py:21 | fixture |
| scripts/test_budget_replay_transaction.py:55 | fixture |
| scripts/test_build_phase_run_caps.py:60 | fixture |
| scripts/test_build_phase_run_caps.py:63 | fixture |
| scripts/test_build_phase_run_caps.py:72 | fixture |
| scripts/test_build_phase_run_caps.py:78 | fixture |
| scripts/test_build_phase_run_caps.py:82 | fixture |
| scripts/test_build_phase_run_caps.py:88 | fixture |
| scripts/test_business_vocabulary.py:9 | fixture |
| scripts/test_business_vocabulary.py:10 | fixture |
| scripts/test_business_vocabulary.py:15 | fixture |
| scripts/test_business_vocabulary.py:16 | fixture |
| scripts/test_business_vocabulary.py:17 | fixture |
| scripts/test_business_vocabulary.py:21 | fixture |
| scripts/test_business_vocabulary.py:25 | fixture |
| scripts/test_business_vocabulary.py:38 | fixture |
| scripts/test_business_vocabulary.py:46 | fixture |
| scripts/test_business_vocabulary.py:58 | fixture |
| scripts/test_business_vocabulary.py:61 | fixture |
| scripts/test_business_vocabulary.py:66 | fixture |
| scripts/test_business_vocabulary.py:67 | fixture |
| scripts/test_business_vocabulary.py:73 | fixture |
| scripts/test_business_vocabulary.py:74 | fixture |
| scripts/test_business_vocabulary.py:84 | fixture |
| scripts/test_business_vocabulary.py:96 | fixture |
| scripts/test_business_vocabulary.py:110 | fixture |
| scripts/test_business_vocabulary.py:117 | fixture |
| scripts/test_business_vocabulary.py:125 | 163ce520-ec47-4824-975c-96f5c749205f |
| scripts/test_calculation_intake.py:306 | warehouse |
| scripts/test_calculation_intake.py:307 | warehouse |
| scripts/test_calculation_intake.py:341 | warehouse |
| scripts/test_calculation_intake.py:342 | warehouse |
| scripts/test_calculation_intake.py:345 | warehouse |
| scripts/test_calculation_intake.py:346 | warehouse |
| scripts/test_capability_evidence.py:12 | fixture |
| scripts/test_capability_evidence.py:17 | fixture |
| scripts/test_capture_publication_retry.py:12 | fixture |
| scripts/test_capture_publication_retry.py:20 | fixture |
| scripts/test_capture_publication_retry.py:30 | fixture |
| scripts/test_capture_transaction_publication.py:14 | fixture |
| scripts/test_catalog_scans.py:10 | fixture |
| scripts/test_catalog_scans.py:19 | fixture |
| scripts/test_catalog_scans.py:20 | fixture |
| scripts/test_catalog_scans.py:21 | fixture |
| scripts/test_catalog_scans.py:25 | fixture |
| scripts/test_catalog_scans.py:38 | fixture |
| scripts/test_catalog_scans.py:53 | fixture |
| scripts/test_catalog_scans.py:75 | fixture |
| scripts/test_catalog_scans.py:77 | fixture |
| scripts/test_catalog_scans.py:78 | fixture |
| scripts/test_catalog_scans.py:85 | fixture |
| scripts/test_catalog_scans.py:89 | fixture |
| scripts/test_catalog_scans.py:91 | fixture |
| scripts/test_catalog_transaction.py:8 | fixture |
| scripts/test_catalog_transaction.py:9 | fixture |
| scripts/test_catalog_transaction.py:61 | fixture |
| scripts/test_catalog_transaction.py:62 | fixture |
| scripts/test_categorical_filter_replay.py:19 | fixture |
| scripts/test_causal_question_coverage.py:5 | fixture |
| scripts/test_causal_question_coverage.py:10 | fixture |
| scripts/test_checksum_archive.py:138 | fixture |
| scripts/test_claim_glossary_evidence.py:8 | fixture |
| scripts/test_claim_glossary_evidence.py:13 | fixture |
| scripts/test_claim_glossary_evidence.py:14 | fixture |
| scripts/test_claim_glossary_evidence.py:15 | fixture |
| scripts/test_claim_glossary_evidence.py:16 | fixture |
| scripts/test_claim_glossary_evidence.py:17 | fixture |
| scripts/test_claim_glossary_evidence.py:18 | fixture |
| scripts/test_claim_glossary_evidence.py:19 | fixture |
| scripts/test_claim_glossary_evidence.py:21 | fixture |
| scripts/test_claim_glossary_evidence.py:24 | fixture |
| scripts/test_claim_glossary_evidence.py:47 | fixture |
| scripts/test_claim_glossary_evidence.py:98 | fixture |
| scripts/test_claim_glossary_evidence.py:102 | fixture |
| scripts/test_claim_handoff.py:6 | fixture |
| scripts/test_claim_handoff.py:13 | fixture |
| scripts/test_claim_handoff.py:65 | fixture |
| scripts/test_claim_handoff.py:84 | fixture |
| scripts/test_claim_handoff.py:90 | fixture |
| scripts/test_claim_handoff.py:99 | fixture |
| scripts/test_claim_investigations.py:12 | fixture |
| scripts/test_claim_investigations.py:159 | 12345678-1234-1234-1234-123456789abc |
| scripts/test_claim_investigations.py:334 | fixture |
| scripts/test_claim_investigations.py:335 | fixture |
| scripts/test_claim_investigations.py:336 | fixture |
| scripts/test_claim_investigations.py:341 | fixture |
| scripts/test_claim_investigations.py:350 | fixture |
| scripts/test_claim_investigations.py:351 | fixture |
| scripts/test_claim_investigations.py:352 | fixture |
| scripts/test_claim_investigations.py:357 | fixture |
| scripts/test_claim_investigations.py:373 | fixture |
| scripts/test_claim_investigations.py:384 | fixture |
| scripts/test_claim_investigations.py:394 | fixture |
| scripts/test_claim_investigations.py:403 | fixture |
| scripts/test_claim_investigations.py:412 | fixture |
| scripts/test_claim_investigations.py:420 | fixture |
| scripts/test_claim_legacy_execution.py:3 | fixture |
| scripts/test_claim_legacy_execution.py:9 | fixture |
| scripts/test_claim_legacy_execution.py:10 | fixture |
| scripts/test_claim_policy_repair.py:31 | 11111111-1111-4111-8111-111111111111, 22222222-2222-4222-8222-222222222222 |
| scripts/test_claim_policy_repair.py:41 | 33333333-3333-4333-8333-333333333333 |
| scripts/test_claim_projection.py:16 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_claim_reference.py:3 | fixture |
| scripts/test_claim_reference.py:10 | fixture |
| scripts/test_claim_reference.py:11 | fixture |
| scripts/test_claim_reference.py:52 | warehouse |
| scripts/test_claim_reference.py:58 | warehouse |
| scripts/test_claim_screenshot_integration.py:6 | fixture |
| scripts/test_claim_screenshot_integration.py:14 | fixture |
| scripts/test_claim_screenshot_ui.py:6 | workspace/ |
| scripts/test_claim_screenshot_ui.py:20 | workspace/ |
| scripts/test_claim_screenshots.py:8 | fixture |
| scripts/test_claim_screenshots.py:20 | fixture |
| scripts/test_claim_workspace_api.py:4 | fixture |
| scripts/test_claim_workspace_api.py:9 | fixture |
| scripts/test_claim_workspace_api.py:20 | workspace/ |
| scripts/test_claim_workspace_api.py:27 | workspace/ |
| scripts/test_claim_workspace_api.py:34 | workspace/ |
| scripts/test_claim_workspace_api.py:37 | workspace/ |
| scripts/test_claim_workspace_api.py:42 | workspace/ |
| scripts/test_claim_workspace_api.py:46 | workspace/ |
| scripts/test_claim_workspace_api.py:48 | workspace/ |
| scripts/test_claim_workspace_api.py:49 | workspace/ |
| scripts/test_claim_workspace_api.py:54 | workspace/ |
| scripts/test_claim_workspace_api.py:57 | workspace/ |
| scripts/test_claim_workspace_api.py:61 | workspace/ |
| scripts/test_clarification_grounding.py:11 | fixture |
| scripts/test_clarification_grounding.py:22 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_cloud_dax_authorization.py:26 | 10000000-0000-0000-0000-000000000001 |
| scripts/test_cloud_dax_authorization.py:27 | 10000000-0000-0000-0000-000000000002 |
| scripts/test_cloud_dax_authorization.py:28 | 10000000-0000-0000-0000-000000000003 |
| scripts/test_cloud_dax_authorization.py:29 | 10000000-0000-0000-0000-000000000004 |
| scripts/test_cloud_dax_authorization.py:30 | 10000000-0000-0000-0000-000000000005 |
| scripts/test_cloud_enrichment.py:18 | fixture |
| scripts/test_cloud_enrichment.py:19 | aeb4d0a9-e637-4a7e-8efc-63cf0c3827df |
| scripts/test_cloud_enrichment.py:20 | 21e3405b-57e9-4581-834e-971b465f80ec, 4a0140cc-f1b5-4b08-852d-8fcab6c130e8 |
| scripts/test_cloud_enrichment.py:21 | fixture |
| scripts/test_cloud_enrichment.py:25 | fixture |
| scripts/test_cloud_enrichment.py:26 | fixture |
| scripts/test_cloud_form_worker.py:151 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_cloud_form_worker.py:152 | 22222222-2222-4222-8222-222222222222 |
| scripts/test_cloud_form_worker.py:164 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_cloud_form_worker.py:175 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_cloud_form_worker.py:185 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_cloud_form_worker.py:186 | 22222222-2222-4222-8222-222222222222 |
| scripts/test_cloud_form_worker.py:187 | 33333333-3333-4333-8333-333333333333 |
| scripts/test_cloud_form_worker.py:194 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_cloud_form_worker.py:202 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_cloud_form_worker.py:207 | 22222222-2222-4222-8222-222222222222 |
| scripts/test_cloud_job_admission.py:6 | 11111111-1111-1111-1111-111111111111, subscriptions/ |
| scripts/test_cloud_ledger_investigator.py:28 | blob.core.windows.net |
| scripts/test_cloud_ledger_investigator.py:70 | blob.core.windows.net |
| scripts/test_cloud_ledger_investigator.py:141 | fixture |
| scripts/test_cloud_ledger_investigator.py:221 | fixture |
| scripts/test_cloud_ledger_investigator.py:243 | fixture |
| scripts/test_cloud_ledger_investigator.py:268 | fixture |
| scripts/test_cloud_ledger_investigator.py:269 | fixture |
| scripts/test_cloud_ledger_investigator.py:277 | fixture |
| scripts/test_cloud_ledger_investigator.py:279 | fixture |
| scripts/test_cloud_offline_worker.py:33 | workspace/ |
| scripts/test_cloud_offline_worker.py:34 | workspace/ |
| scripts/test_cloud_offline_worker.py:35 | workspace/ |
| scripts/test_cloud_offline_worker.py:36 | workspace/ |
| scripts/test_cloud_offline_worker.py:47 | fixture |
| scripts/test_cloud_preflight.py:11 | fixture |
| scripts/test_cloud_preflight.py:92 | fixture |
| scripts/test_cloud_replay_bootstrap.py:67 | blob.core.windows.net |
| scripts/test_cloud_replay_bootstrap.py:68 | blob.core.windows.net |
| scripts/test_cloud_replay_bootstrap.py:69 | blob.core.windows.net |
| scripts/test_cloud_replay_bootstrap.py:70 | blob.core.windows.net |
| scripts/test_cloud_replay_bootstrap.py:115 | blob.core.windows.net |
| scripts/test_cloud_replay_bootstrap.py:116 | blob.core.windows.net |
| scripts/test_cloud_replay_bootstrap.py:118 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_cloud_replay_bootstrap.py:119 | 22222222-2222-4222-8222-222222222222 |
| scripts/test_cloud_replay_bootstrap.py:120 | 33333333-3333-4333-8333-333333333333 |
| scripts/test_cloud_replay_bootstrap.py:142 | blob.core.windows.net |
| scripts/test_cloud_replay_bootstrap.py:143 | blob.core.windows.net |
| scripts/test_cloud_replay_bootstrap.py:144 | blob.core.windows.net |
| scripts/test_cloud_replay_bootstrap.py:146 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_cloud_replay_bootstrap.py:147 | 22222222-2222-4222-8222-222222222222 |
| scripts/test_cloud_replay_bootstrap.py:148 | 33333333-3333-4333-8333-333333333333 |
| scripts/test_cloud_runner_context.py:60 | fixture |
| scripts/test_cloud_runner_context.py:185 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_cloud_stage_environment.py:42 | 44444444-4444-4444-4444-444444444444 |
| scripts/test_cloud_value_mapping.py:9 | fixture |
| scripts/test_cloud_value_mapping.py:14 | fixture |
| scripts/test_cloud_value_mapping.py:25 | workspace/ |
| scripts/test_cloud_value_mapping.py:26 | Warehouse |
| scripts/test_cloud_value_mapping.py:27 | Warehouse |
| scripts/test_cloud_value_mapping.py:28 | Warehouse |
| scripts/test_cloud_value_mapping.py:36 | fixture |
| scripts/test_cloud_value_mapping.py:43 | fixture, workspace/ |
| scripts/test_cloud_value_mapping.py:46 | lakehouse |
| scripts/test_cloud_value_mapping.py:47 | Lakehouse, workspace/ |
| scripts/test_cloud_value_mapping.py:48 | LAKEHOUSE, workspace/ |
| scripts/test_cloud_value_mapping.py:51 | workspace/ |
| scripts/test_cloud_value_verifier.py:9 | fixture |
| scripts/test_cloud_value_verifier.py:30 | fixture |
| scripts/test_cloud_value_verifier.py:36 | fixture |
| scripts/test_cloud_value_verifier.py:41 | fixture |
| scripts/test_cloud_value_verifier.py:48 | fixture |
| scripts/test_cloud_value_verifier.py:53 | fixture |
| scripts/test_cloud_value_verifier.py:58 | fixture |
| scripts/test_cloud_value_verifier.py:63 | fixture |
| scripts/test_cloud_value_verifier.py:74 | fixture |
| scripts/test_cloud_value_verifier.py:90 | fixture |
| scripts/test_cloud_value_verifier.py:99 | fixture |
| scripts/test_cloud_value_verifier.py:109 | fixture |
| scripts/test_cloud_value_verifier.py:113 | fixture |
| scripts/test_cloud_value_verifier.py:118 | fixture |
| scripts/test_cloud_verification_capture.py:27 | fixture |
| scripts/test_cloud_verification_prewarm.py:75 | workspace/ |
| scripts/test_cloud_verification_proof.py:11 | fixture |
| scripts/test_cloud_verification_proof.py:19 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_cloud_verification_proof.py:20 | 44444444-4444-4444-8444-444444444444 |
| scripts/test_cloud_verification_proof.py:24 | 66666666-6666-4666-8666-666666666666 |
| scripts/test_cloud_verification_proof.py:25 | warehouse |
| scripts/test_cloud_verification_proof.py:27 | 22222222-2222-4222-8222-222222222222, 33333333-3333-4333-8333-333333333333 |
| scripts/test_cloud_verification_proof.py:33 | database.windows.net |
| scripts/test_cloud_verification_proof.py:42 | 77777777-7777-4777-8777-777777777777 |
| scripts/test_cloud_verification_proof.py:55 | fixture |
| scripts/test_cloud_verification_proof.py:56 | fixture |
| scripts/test_cloud_verification_proof.py:71 | fixture |
| scripts/test_cloud_verification_proof.py:279 | fixture |
| scripts/test_code_approval_controller.py:5 | fixture |
| scripts/test_code_approval_controller.py:10 | fixture |
| scripts/test_code_definition.py:10 | 11111111-1111-1111-1111-111111111111, 22222222-2222-2222-2222-222222222222 |
| scripts/test_code_definition.py:11 | 22222222-2222-2222-2222-222222222222 |
| scripts/test_code_definition.py:34 | 33333333-3333-3333-3333-333333333333 |
| scripts/test_code_sources.py:12 | fixture |
| scripts/test_code_sources.py:14 | 11111111-1111-1111-1111-111111111111, 22222222-2222-2222-2222-222222222222 |
| scripts/test_code_sources.py:15 | fixture |
| scripts/test_code_sources.py:16 | fixture |
| scripts/test_code_verification.py:116 | workspace/ |
| scripts/test_code_verification.py:120 | Lakehouse |
| scripts/test_code_verification.py:121 | Lakehouse |
| scripts/test_code_verification.py:122 | workspace/ |
| scripts/test_collected_refresh_consumer.py:11 | fixture |
| scripts/test_collector_schedule.py:12 | fixture |
| scripts/test_collector_schedule.py:23 | job-dia-, subscriptions/ |
| scripts/test_collector_schedule.py:37 | fixture |
| scripts/test_collector_schedule.py:58 | job-dia- |
| scripts/test_comparison_gates.py:11 | fixture |
| scripts/test_comparison_gates.py:17 | fixture |
| scripts/test_connection_registry.py:17 | workspace/ |
| scripts/test_connection_registry.py:21 | workspace/ |
| scripts/test_connection_registry.py:22 | Lakehouse, workspace/ |
| scripts/test_connection_registry.py:46 | SemanticModel, workspace/ |
| scripts/test_connection_registry.py:49 | workspace/ |
| scripts/test_connection_registry.py:50 | workspace/ |
| scripts/test_connection_registry.py:56 | workspace/ |
| scripts/test_connection_registry.py:57 | workspace/ |
| scripts/test_connection_registry.py:65 | fixture |
| scripts/test_connection_registry.py:83 | fixture |
| scripts/test_context_runtime.py:4 | fixture |
| scripts/test_context_runtime.py:8 | fixture |
| scripts/test_context_runtime.py:13 | fixture |
| scripts/test_continuation_catalog.py:31 | warehouse |
| scripts/test_copy_route_readiness.py:11 | fixture |
| scripts/test_copy_route_readiness.py:12 | fixture |
| scripts/test_cross_layer_investigation.py:122 | lakehouse, semantic_model |
| scripts/test_dax_self_report_composition.py:6 | fixture |
| scripts/test_dax_self_report_composition.py:9 | fixture |
| scripts/test_dax_self_report_composition.py:10 | fixture |
| scripts/test_declared_chain_depth.py:51 | Lakehouse |
| scripts/test_declared_chain_depth.py:161 | fixture |
| scripts/test_declared_lineage_round_trip.py:1 | fixture |
| scripts/test_declared_lineage_round_trip.py:46 | fixture |
| scripts/test_declared_lineage_round_trip.py:47 | fixture |
| scripts/test_declared_lineage_round_trip.py:55 | 20261003 |
| scripts/test_declared_load_audit.py:52 | Warehouse |
| scripts/test_declared_load_audit.py:53 | Warehouse |
| scripts/test_declared_load_audit.py:55 | Warehouse |
| scripts/test_declared_load_audit.py:61 | Warehouse |
| scripts/test_declared_load_audit.py:72 | lakehouse |
| scripts/test_declared_load_audit.py:74 | Lakehouse |
| scripts/test_declared_load_audit.py:79 | LAKEHOUSE |
| scripts/test_declared_reproduction.py:416 | fixture |
| scripts/test_declared_reproduction.py:417 | fixture |
| scripts/test_declared_reproduction.py:430 | fixture |
| scripts/test_declared_reproduction.py:436 | fixture |
| scripts/test_declared_source_comparison.py:9 | fixture |
| scripts/test_declared_source_comparison.py:24 | fixture |
| scripts/test_declared_source_comparison.py:33 | fixture |
| scripts/test_declared_source_comparison.py:44 | fixture |
| scripts/test_declared_source_comparison.py:47 | fixture |
| scripts/test_declared_source_comparison.py:51 | fixture |
| scripts/test_delivery_transports.py:16 | fixture |
| scripts/test_delivery_transports.py:24 | fixture |
| scripts/test_delivery_transports.py:33 | fixture |
| scripts/test_delivery_transports.py:40 | fixture |
| scripts/test_delivery_transports.py:46 | fixture |
| scripts/test_delivery_transports.py:54 | fixture |
| scripts/test_delivery_transports.py:60 | fixture |
| scripts/test_delivery_transports.py:71 | fixture |
| scripts/test_demo_admission.py:58 | 11111111-1111-1111-1111-111111111111, job-dia-, subscriptions/ |
| scripts/test_demo_launcher.py:14 | workspace/ |
| scripts/test_demo_launcher.py:33 | workspace/ |
| scripts/test_dependency_context.py:15 | fixture |
| scripts/test_dependency_context.py:20 | fixture |
| scripts/test_dependency_context.py:41 | fixture |
| scripts/test_dependency_context.py:119 | fixture |
| scripts/test_dependency_context.py:121 | fixture |
| scripts/test_dependency_context.py:187 | fixture |
| scripts/test_dependency_context.py:188 | fixture |
| scripts/test_dependency_context.py:189 | fixture |
| scripts/test_deploy_powerbi.py:9 | 00000000-0000-0000-0000-000000000002 |
| scripts/test_deploy_powerbi.py:13 | 00000000-0000-0000-0000-000000000001, 00000000-0000-0000-0000-000000000003 |
| scripts/test_deploy_powerbi.py:17 | 00000000-0000-0000-0000-000000000001, 00000000-0000-0000-0000-000000000003 |
| scripts/test_deploy_powerbi.py:26 | workspaces/ |
| scripts/test_dia_commands.py:17 | fixture |
| scripts/test_dia_commands.py:18 | fixture |
| scripts/test_dia_commands.py:22 | fixture |
| scripts/test_dia_commands.py:31 | fixture |
| scripts/test_dia_commands.py:36 | fixture |
| scripts/test_dia_commands.py:45 | fixture |
| scripts/test_dia_commands.py:47 | fixture |
| scripts/test_directlake_bridge.py:3 | lakehouse |
| scripts/test_directlake_bridge.py:5 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_directlake_bridge.py:6 | 00000000-0000-0000-0000-000000000002 |
| scripts/test_directlake_bridge.py:7 | 00000000-0000-0000-0000-000000000003 |
| scripts/test_directlake_bridge.py:8 | 00000000-0000-0000-0000-000000000004 |
| scripts/test_directlake_bridge.py:12 | fixture, lakehouse |
| scripts/test_directlake_bridge.py:14 | lakehouse |
| scripts/test_directlake_bridge.py:17 | SemanticModel |
| scripts/test_directlake_bridge.py:19 | Lakehouse, Warehouse, lakehouse |
| scripts/test_directlake_bridge.py:20 | Lakehouse, Warehouse, lakehouse |
| scripts/test_directlake_bridge.py:22 | Lakehouse, Warehouse, lakehouse |
| scripts/test_directlake_bridge.py:26 | warehouse |
| scripts/test_directlake_bridge.py:27 | fixture |
| scripts/test_directlake_bridge.py:33 | Warehouse, fixture |
| scripts/test_directlake_bridge.py:38 | fixture |
| scripts/test_directlake_bridge.py:47 | fixture |
| scripts/test_directlake_bridge.py:50 | lakehouse |
| scripts/test_directlake_bridge.py:51 | fixture |
| scripts/test_directlake_bridge.py:52 | lakehouse |
| scripts/test_directlake_bridge.py:53 | Lakehouse |
| scripts/test_directlake_bridge.py:54 | lakehouse |
| scripts/test_directlake_bridge.py:60 | fixture |
| scripts/test_directlake_bridge.py:61 | 00000000-0000-0000-0000-000000000005 |
| scripts/test_directlake_bridge.py:62 | Lakehouse |
| scripts/test_directlake_bridge.py:63 | Lakehouse, lakehouse |
| scripts/test_directlake_bridge.py:64 | Lakehouse |
| scripts/test_directlake_bridge.py:67 | fixture |
| scripts/test_directlake_bridge.py:69 | Lakehouse |
| scripts/test_directlake_bridge.py:70 | lakehouse |
| scripts/test_directlake_bridge.py:71 | Lakehouse |
| scripts/test_directlake_bridge.py:75 | fixture |
| scripts/test_directlake_bridge.py:87 | fixture |
| scripts/test_directlake_bridge.py:98 | fixture |
| scripts/test_directlake_bridge.py:110 | fixture |
| scripts/test_directlake_bridge.py:126 | fixture |
| scripts/test_directlake_bridge.py:136 | fixture |
| scripts/test_directlake_bridge.py:138 | lakehouse |
| scripts/test_directlake_bridge.py:139 | Lakehouse |
| scripts/test_directlake_bridge.py:140 | lakehouse |
| scripts/test_directlake_bridge.py:151 | fixture |
| scripts/test_directlake_bridge.py:153 | fixture |
| scripts/test_directlake_bridge.py:165 | fixture |
| scripts/test_directlake_bridge.py:166 | fixture |
| scripts/test_discovered_source_connection.py:7 | fixture |
| scripts/test_discovered_source_connection.py:11 | fixture |
| scripts/test_discovered_source_connection.py:12 | fixture |
| scripts/test_discovered_source_connection.py:14 | fixture |
| scripts/test_discovered_source_connection.py:16 | Lakehouse |
| scripts/test_discovered_source_connection.py:25 | database.windows.net |
| scripts/test_discovered_source_connection.py:34 | fixture |
| scripts/test_discovered_source_connection.py:44 | database.windows.net |
| scripts/test_discovered_source_connection.py:54 | database.windows.net |
| scripts/test_discovered_source_connection.py:55 | database.windows.net |
| scripts/test_discovered_source_connection.py:56 | database.windows.net |
| scripts/test_discovered_source_connection.py:74 | fixture |
| scripts/test_domain_profile.py:77 | workspace/ |
| scripts/test_email_delivery_adapter.py:4 | fixture |
| scripts/test_email_delivery_adapter.py:12 | fixture |
| scripts/test_email_delivery_adapter.py:13 | fixture |
| scripts/test_enrichment.py:20 | fixture |
| scripts/test_enrichment.py:41 | 11111111-1111-1111-1111-111111111111, 22222222-2222-2222-2222-222222222222, 33333333-3333-3333-3333-333333333333 |
| scripts/test_enterprise_discovery.py:26 | Warehouse |
| scripts/test_enterprise_discovery.py:36 | lakehouse |
| scripts/test_enterprise_discovery.py:38 | Lakehouse |
| scripts/test_enterprise_discovery.py:41 | lakehouse |
| scripts/test_enterprise_discovery.py:42 | Lakehouse |
| scripts/test_enterprise_discovery.py:47 | lakehouse |
| scripts/test_enterprise_discovery.py:50 | Lakehouse |
| scripts/test_enterprise_discovery.py:53 | lakehouse |
| scripts/test_enterprise_discovery.py:54 | Lakehouse |
| scripts/test_enterprise_discovery.py:64 | database.windows.net |
| scripts/test_enterprise_discovery.py:70 | warehouse |
| scripts/test_enterprise_discovery.py:72 | Warehouse |
| scripts/test_enterprise_discovery.py:75 | warehouse |
| scripts/test_enterprise_discovery.py:80 | warehouse |
| scripts/test_enterprise_discovery.py:82 | Warehouse |
| scripts/test_enterprise_discovery.py:87 | warehouse |
| scripts/test_enterprise_discovery.py:88 | Warehouse |
| scripts/test_enterprise_discovery.py:93 | warehouse |
| scripts/test_enterprise_discovery.py:98 | warehouse |
| scripts/test_enterprise_discovery.py:101 | Warehouse |
| scripts/test_enterprise_discovery.py:102 | Warehouse |
| scripts/test_enterprise_discovery.py:105 | warehouse |
| scripts/test_enterprise_discovery.py:112 | database.windows.net |
| scripts/test_enterprise_discovery.py:116 | SemanticModel |
| scripts/test_enterprise_discovery.py:122 | semanticmodel |
| scripts/test_enterprise_discovery.py:188 | Lakehouse |
| scripts/test_enterprise_discovery.py:194 | Lakehouse |
| scripts/test_enterprise_discovery.py:275 | SemanticModel |
| scripts/test_enterprise_discovery.py:338 | lakehouse |
| scripts/test_enterprise_discovery.py:340 | Lakehouse, lakehouse |
| scripts/test_enterprise_discovery.py:342 | lakehouse |
| scripts/test_enterprise_discovery.py:344 | lakehouse |
| scripts/test_envelope_review_api.py:5 | fixture |
| scripts/test_envelope_review_api.py:13 | fixture |
| scripts/test_envelope_workflow.py:8 | fixture |
| scripts/test_envelope_workflow.py:15 | fixture |
| scripts/test_essentials_intake.py:103 | fixture |
| scripts/test_essentials_intake.py:110 | fixture |
| scripts/test_essentials_intake.py:244 | workspace/ |
| scripts/test_essentials_intake.py:247 | workspace/ |
| scripts/test_essentials_intake.py:250 | workspace/ |
| scripts/test_estate_graph.py:70 | fixture |
| scripts/test_estate_graph.py:71 | fixture |
| scripts/test_estate_graph.py:83 | fixture |
| scripts/test_estate_graph.py:84 | fixture |
| scripts/test_estate_graph.py:104 | fixture |
| scripts/test_estate_graph.py:105 | fixture |
| scripts/test_estate_graph.py:116 | fixture |
| scripts/test_estate_graph.py:117 | fixture |
| scripts/test_estate_graph.py:146 | fixture |
| scripts/test_estate_graph.py:147 | fixture |
| scripts/test_estate_graph.py:159 | fixture |
| scripts/test_estate_graph.py:160 | fixture |
| scripts/test_estate_graph_static.py:30 | SemanticModel |
| scripts/test_estate_graph_static.py:53 | SemanticModel |
| scripts/test_estate_graph_static.py:61 | Warehouse |
| scripts/test_estate_graph_static.py:70 | warehouse |
| scripts/test_estate_graph_static.py:71 | Warehouse |
| scripts/test_estate_graph_static.py:72 | Warehouse |
| scripts/test_estate_graph_static.py:74 | Warehouse |
| scripts/test_estate_graph_static.py:92 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_estate_graph_static.py:98 | SemanticModel |
| scripts/test_estate_graph_static.py:101 | semanticmodel |
| scripts/test_estate_graph_static.py:160 | SemanticModel |
| scripts/test_estate_graph_static.py:164 | Lakehouse |
| scripts/test_estate_graph_static.py:173 | SemanticModel |
| scripts/test_estate_manifest.py:14 | fixture |
| scripts/test_estate_manifest.py:17 | fixture |
| scripts/test_estate_manifest.py:30 | fixture |
| scripts/test_estate_manifest.py:37 | fixture |
| scripts/test_estate_manifest.py:69 | fixture |
| scripts/test_estate_manifest.py:71 | fixture |
| scripts/test_estate_manifest.py:75 | fixture |
| scripts/test_estate_manifest.py:78 | fixture |
| scripts/test_estate_manifest.py:79 | fixture |
| scripts/test_estate_manifest.py:98 | fixture |
| scripts/test_estate_manifest.py:102 | fixture |
| scripts/test_estate_manifest.py:125 | fixture |
| scripts/test_estate_manifest.py:127 | fixture |
| scripts/test_estate_manifest.py:132 | fixture |
| scripts/test_estate_manifest.py:138 | fixture |
| scripts/test_estate_manifest.py:145 | fixture |
| scripts/test_estate_manifest.py:150 | fixture |
| scripts/test_estate_manifest.py:152 | fixture |
| scripts/test_estate_manifest.py:171 | fixture |
| scripts/test_estate_manifest.py:175 | fixture |
| scripts/test_estate_manifest.py:196 | fixture |
| scripts/test_estate_manifest.py:198 | fixture |
| scripts/test_estate_manifest.py:264 | fixture |
| scripts/test_estate_manifest.py:267 | fixture |
| scripts/test_estate_manifest.py:305 | fixture |
| scripts/test_estate_neutrality.py:15 | billingapp, ordersops, sql-orderops |
| scripts/test_estate_neutrality.py:16 | orderops_investigator, skynwhy.com, warehouse |
| scripts/test_estate_neutrality.py:25 | Fixture |
| scripts/test_estate_neutrality.py:79 | 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/test_estate_neutrality.py:85 | fixture |
| scripts/test_estate_neutrality.py:89 | fixture |
| scripts/test_estate_neutrality.py:97 | fixture |
| scripts/test_evidence_prose.py:6 | fixture |
| scripts/test_evidence_prose.py:7 | fixture |
| scripts/test_evidence_prose.py:30 | fixture |
| scripts/test_evidence_prose.py:50 | fixture |
| scripts/test_evidence_prose.py:72 | fixture |
| scripts/test_evidence_synthesis.py:8 | fixture |
| scripts/test_evidence_synthesis.py:54 | fixture |
| scripts/test_evidence_synthesis.py:395 | bcb2f0ac-61d2-4926-8384-23eb58230634 |
| scripts/test_evidence_synthesis.py:396 | 91b223d0-4fcf-43b2-9085-3f449287daba |
| scripts/test_evidence_synthesis.py:397 | 7aeca75e-5f56-4834-8eed-919f0264da79 |
| scripts/test_evidence_synthesis.py:398 | 0cd0119a-9229-47f9-8439-ae7cd5faf0b8 |
| scripts/test_evidence_synthesis.py:399 | 0dd49072-a9ed-4acb-8f82-7755cd446d6a |
| scripts/test_evidence_synthesis.py:408 | fixture |
| scripts/test_evidence_synthesis.py:409 | fixture |
| scripts/test_facts_ledger.py:34 | id-dia |
| scripts/test_facts_ledger.py:35 | id-dia |
| scripts/test_facts_ledger.py:207 | id-dia |
| scripts/test_federated_reader.py:31 | fb60f99c-7a34-4190-8149-302f77469936 |
| scripts/test_federated_sql_principal.py:12 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_federated_sql_principal.py:13 | 22222222-2222-4222-8222-222222222222 |
| scripts/test_federated_sql_principal.py:14 | 33333333-3333-4333-8333-333333333333 |
| scripts/test_federated_sql_principal.py:16 | 44444444-4444-4444-8444-444444444444 |
| scripts/test_federated_sql_principal.py:17 | 55555555-5555-4555-8555-555555555555 |
| scripts/test_federated_sql_principal.py:18 | 66666666-6666-4666-8666-666666666666 |
| scripts/test_federated_sql_principal.py:21 | warehouse |
| scripts/test_federated_sql_principal.py:23 | warehouse |
| scripts/test_federated_sql_principal.py:24 | Warehouse |
| scripts/test_federated_sql_principal.py:36 | warehouse |
| scripts/test_figure_same_referent.py:11 | fixture |
| scripts/test_figure_same_referent.py:33 | fixture |
| scripts/test_figure_same_referent.py:73 | fixture |
| scripts/test_figure_same_referent.py:76 | fixture |
| scripts/test_figure_same_referent.py:80 | fixture |
| scripts/test_filter_translation_forms.py:7 | fixture |
| scripts/test_filter_translation_forms.py:12 | fixture |
| scripts/test_fixture_apply.py:4 | fixture |
| scripts/test_fixture_apply.py:5 | fixture |
| scripts/test_fixture_apply.py:6 | fixture |
| scripts/test_fixture_apply.py:8 | d028fa2b-0d1b-4dd8-b423-37dd161cd5d0 |
| scripts/test_fixture_apply.py:9 | ec15bc07-8e88-436e-8dbe-485b9a7f4533, fixture |
| scripts/test_fixture_apply.py:11 | fixture |
| scripts/test_fixture_apply.py:22 | workspaces/ |
| scripts/test_fixture_apply.py:25 | fixture, warehouse |
| scripts/test_fixture_apply.py:26 | workspaces/ |
| scripts/test_fixture_apply.py:28 | fixture, warehouse |
| scripts/test_fixture_apply.py:56 | Lakehouse |
| scripts/test_fixture_apply.py:59 | fixture |
| scripts/test_fixture_apply.py:67 | fixture |
| scripts/test_fixture_code_sources.py:1 | Fixture |
| scripts/test_fixture_code_sources.py:9 | Fixture |
| scripts/test_fixture_code_sources.py:10 | fixture |
| scripts/test_fixture_code_sources.py:11 | fixture |
| scripts/test_fixture_code_sources.py:22 | fixture |
| scripts/test_fixture_control.py:3 | Fixture, fixture |
| scripts/test_fixture_control.py:5 | d028fa2b-0d1b-4dd8-b423-37dd161cd5d0 |
| scripts/test_fixture_control.py:13 | Fixture |
| scripts/test_fixture_control.py:16 | Fixture |
| scripts/test_fixture_control.py:20 | 00000000-0000-0000-0000-000000000000, workspaces/ |
| scripts/test_fixture_control.py:25 | workspaces/ |
| scripts/test_fixture_control.py:32 | workspaces/ |
| scripts/test_fixture_control.py:38 | lakehouse, workspaces/ |
| scripts/test_fixture_control.py:39 | lakehouse, workspaces/ |
| scripts/test_fixture_control.py:43 | lakehouse, workspaces/ |
| scripts/test_fixture_control.py:44 | lakehouse, workspaces/ |
| scripts/test_fixture_control.py:48 | workspaces/ |
| scripts/test_fixture_control.py:53 | workspaces/ |
| scripts/test_fixture_control.py:57 | workspaces/ |
| scripts/test_fixture_definitions.py:2 | fixture |
| scripts/test_fixture_definitions.py:3 | fixture |
| scripts/test_fixture_definitions.py:5 | Fixture |
| scripts/test_fixture_definitions.py:6 | lakehouse |
| scripts/test_fixture_definitions.py:7 | aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa, bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb, fixture, lakehouse, warehouse |
| scripts/test_fixture_definitions.py:8 | cccccccc-cccc-cccc-cccc-cccccccccccc, lakehouse |
| scripts/test_fixture_definitions.py:9 | lakehouse |
| scripts/test_fixture_definitions.py:10 | lakehouse |
| scripts/test_fixture_definitions.py:11 | lakehouse |
| scripts/test_fixture_definitions.py:12 | cccccccc-cccc-cccc-cccc-cccccccccccc, lakehouse |
| scripts/test_fixture_definitions.py:15 | fixture |
| scripts/test_fixture_definitions.py:23 | fixture |
| scripts/test_fixture_definitions.py:25 | aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa, bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb |
| scripts/test_fixture_failure_scenarios.py:3 | fixture |
| scripts/test_fixture_failure_scenarios.py:5 | fixture |
| scripts/test_fixture_failure_scenarios.py:10 | warehouse |
| scripts/test_fixture_failure_scenarios.py:11 | 20261003 |
| scripts/test_fixture_failure_scenarios.py:12 | warehouse |
| scripts/test_fixture_failure_scenarios.py:16 | 20261003 |
| scripts/test_fixture_failure_scenarios.py:52 | 20261003 |
| scripts/test_fixture_failure_scenarios.py:70 | 22222222-2222-2222-2222-222222222222 |
| scripts/test_fixture_failure_scenarios.py:85 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_fixture_failure_scenarios.py:91 | 22222222-2222-2222-2222-222222222222 |
| scripts/test_fixture_failure_scenarios.py:92 | workspaces/ |
| scripts/test_fixture_failure_scenarios.py:95 | 22222222-2222-2222-2222-222222222222 |
| scripts/test_fixture_failure_scenarios.py:104 | 22222222-2222-2222-2222-222222222222, 33333333-3333-3333-3333-333333333333 |
| scripts/test_fixture_failure_scenarios.py:105 | workspaces/ |
| scripts/test_fixture_load_audit.py:4 | fixture |
| scripts/test_fixture_model_autosync.py:2 | fixture |
| scripts/test_fixture_model_autosync.py:4 | 149f8d99-1c66-4a0a-9624-759be002bb60 |
| scripts/test_fixture_model_autosync.py:5 | 3484a2bc-98c5-4cef-be5c-a6215484075e |
| scripts/test_fixture_model_autosync.py:6 | 0c89889c-6fe6-49ab-91e9-4b00a51070e6 |
| scripts/test_fixture_pipeline_schedule.py:2 | fixture |
| scripts/test_fixture_pipeline_schedule.py:4 | 149f8d99-1c66-4a0a-9624-759be002bb60, 659ea59a-256f-4673-a661-0d6f3359d9be, b4871498-bd35-45be-916c-9a642568012c |
| scripts/test_fixture_reader.py:7 | fixture |
| scripts/test_fixture_reader.py:10 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_fixture_reader.py:53 | fixture |
| scripts/test_fixture_reader.py:55 | fixture |
| scripts/test_fixture_rebuild.py:5 | fixture |
| scripts/test_fixture_rebuild.py:10 | fixture |
| scripts/test_fixture_seed.py:3 | fixture |
| scripts/test_fixture_seed.py:6 | Fixture |
| scripts/test_fixture_seed.py:39 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_fixture_seed.py:47 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_fixture_source_access.py:2 | fixture |
| scripts/test_fixture_source_access.py:9 | billingapp |
| scripts/test_fixture_source_access.py:15 | ordersops |
| scripts/test_fixture_source_access.py:24 | fixture |
| scripts/test_fixture_source_access.py:36 | dia-investigator, orderops_investigator |
| scripts/test_fixture_source_access.py:39 | fixture |
| scripts/test_fixture_source_access.py:41 | fixture |
| scripts/test_fixture_source_access.py:43 | fixture |
| scripts/test_fixture_source_latency.py:5 | fixture |
| scripts/test_fixture_source_latency.py:6 | Fixture, fixture |
| scripts/test_fixture_source_latency.py:7 | fixture |
| scripts/test_fixture_source_latency.py:10 | fixture |
| scripts/test_fixture_source_latency.py:15 | fixture |
| scripts/test_fixture_source_latency.py:16 | fixture |
| scripts/test_fixture_source_latency.py:47 | Fixture |
| scripts/test_fixture_source_latency.py:49 | fixture |
| scripts/test_fixture_source_latency.py:56 | Fixture |
| scripts/test_fixture_source_latency.py:65 | Fixture |
| scripts/test_fixture_source_latency.py:69 | Fixture |
| scripts/test_fixture_source_latency.py:73 | Fixture |
| scripts/test_fixture_source_latency.py:75 | fixture |
| scripts/test_fixture_source_latency.py:89 | Fixture |
| scripts/test_fixture_source_latency.py:92 | fixture |
| scripts/test_fixture_source_scopes.py:2 | fixture |
| scripts/test_fixture_source_scopes.py:8 | warehouse |
| scripts/test_fixture_source_scopes.py:19 | warehouse |
| scripts/test_fixture_source_temporal.py:2 | fixture |
| scripts/test_fixture_source_temporal.py:3 | fixture |
| scripts/test_fixture_source_temporal.py:4 | fixture |
| scripts/test_fixture_source_temporal.py:11 | fixture |
| scripts/test_fixture_source_temporal.py:12 | warehouse |
| scripts/test_fixture_source_temporal.py:41 | fixture |
| scripts/test_fixture_source_temporal.py:53 | 20261003 |
| scripts/test_fixture_source_temporal.py:56 | 20261003 |
| scripts/test_fixture_source_temporal.py:57 | 20261003 |
| scripts/test_fixture_source_temporal.py:58 | 20261003 |
| scripts/test_fixture_source_temporal.py:59 | 20261003 |
| scripts/test_fixture_source_temporal.py:63 | 20261003 |
| scripts/test_fixture_source_temporal.py:64 | 20261003 |
| scripts/test_fixture_source_temporal.py:75 | 20261003 |
| scripts/test_fixture_source_temporal.py:90 | fixture |
| scripts/test_fixture_source_temporal.py:101 | fixture |
| scripts/test_fixture_source_temporal.py:108 | fixture |
| scripts/test_fixture_source_temporal.py:115 | fixture |
| scripts/test_flexible_investigation.py:6 | fixture |
| scripts/test_flexible_investigation.py:325 | fixture |
| scripts/test_flexible_investigation.py:326 | fixture |
| scripts/test_flexible_investigation.py:385 | fixture |
| scripts/test_form_candidates.py:54 | warehouse |
| scripts/test_form_candidates.py:59 | warehouse |
| scripts/test_form_controller.py:8 | fixture |
| scripts/test_form_controller.py:13 | fixture |
| scripts/test_form_controller.py:110 | fixture |
| scripts/test_form_controller.py:112 | fixture |
| scripts/test_form_controller.py:145 | warehouse |
| scripts/test_form_controller.py:148 | warehouse |
| scripts/test_form_controller.py:204 | workspace/ |
| scripts/test_form_controller.py:207 | workspace/ |
| scripts/test_form_controller.py:211 | workspace/ |
| scripts/test_form_controller.py:218 | workspace/ |
| scripts/test_form_controller.py:221 | workspace/ |
| scripts/test_form_controller.py:237 | warehouse |
| scripts/test_form_controller.py:240 | warehouse |
| scripts/test_form_controller.py:295 | warehouse |
| scripts/test_form_controller.py:328 | fixture |
| scripts/test_form_controller.py:379 | workspace/ |
| scripts/test_form_description.py:5 | fixture |
| scripts/test_form_description.py:10 | fixture |
| scripts/test_form_description.py:17 | warehouse |
| scripts/test_form_description.py:31 | warehouse |
| scripts/test_form_description.py:55 | warehouse |
| scripts/test_form_description.py:106 | fixture |
| scripts/test_form_description.py:142 | fixture |
| scripts/test_form_description.py:153 | warehouse |
| scripts/test_form_description.py:154 | warehouse |
| scripts/test_form_description.py:159 | warehouse |
| scripts/test_form_description.py:160 | warehouse |
| scripts/test_form_description.py:191 | warehouse |
| scripts/test_form_description.py:192 | warehouse |
| scripts/test_form_description.py:195 | warehouse |
| scripts/test_form_intake.py:11 | warehouse |
| scripts/test_form_intake.py:80 | warehouse |
| scripts/test_freshness_evidence.py:8 | fixture |
| scripts/test_freshness_evidence.py:9 | fixture |
| scripts/test_freshness_evidence.py:18 | fixture |
| scripts/test_freshness_evidence.py:28 | fixture |
| scripts/test_freshness_evidence.py:35 | fixture |
| scripts/test_freshness_evidence.py:185 | fixture |
| scripts/test_freshness_evidence.py:192 | fixture |
| scripts/test_git_code.py:10 | fixture |
| scripts/test_git_code.py:11 | fixture |
| scripts/test_git_code.py:34 | fixture |
| scripts/test_github_issue_adapter.py:4 | fixture |
| scripts/test_github_issue_adapter.py:11 | fixture |
| scripts/test_github_issue_adapter.py:12 | fixture |
| scripts/test_github_issue_adapter.py:26 | fixture |
| scripts/test_github_issue_adapter.py:34 | fixture |
| scripts/test_github_issue_adapter.py:77 | fixture |
| scripts/test_gold_publication.py:12 | fixture |
| scripts/test_gold_publication.py:23 | fixture |
| scripts/test_gold_publication.py:27 | fixture |
| scripts/test_gold_publication.py:36 | fixture |
| scripts/test_gold_publication.py:40 | fixture |
| scripts/test_graded_surface_attestation.py:157 | fixture |
| scripts/test_graph_code_columns.py:15 | Lakehouse |
| scripts/test_graph_code_columns.py:17 | Lakehouse |
| scripts/test_graph_code_columns.py:18 | Lakehouse |
| scripts/test_graph_code_columns.py:35 | warehouse |
| scripts/test_graph_code_columns.py:37 | Warehouse, warehouse |
| scripts/test_graph_code_columns.py:38 | Warehouse |
| scripts/test_graph_code_columns.py:54 | warehouse |
| scripts/test_graph_code_columns.py:58 | Warehouse |
| scripts/test_graph_code_columns.py:61 | Lakehouse |
| scripts/test_graph_code_columns.py:62 | Lakehouse |
| scripts/test_graph_code_columns.py:63 | Lakehouse |
| scripts/test_graph_code_columns.py:70 | Warehouse |
| scripts/test_graph_code_columns.py:75 | Warehouse |
| scripts/test_graph_container_schema.py:12 | Lakehouse |
| scripts/test_graph_container_schema.py:13 | Lakehouse |
| scripts/test_graph_container_schema.py:14 | Lakehouse |
| scripts/test_graph_container_schema.py:15 | Warehouse |
| scripts/test_graph_container_schema.py:23 | Lakehouse |
| scripts/test_graph_container_schema.py:28 | Lakehouse |
| scripts/test_graph_container_schema.py:58 | lakehouse |
| scripts/test_graph_dax_http.py:45 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_graph_dax_http.py:47 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_graph_dax_http.py:48 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_graph_dax_http.py:49 | 00000000-0000-0000-0000-000000000002 |
| scripts/test_graph_dependency_integration.py:10 | 00000000-0000-0000-0000-000000000001, 00000000-0000-0000-0000-000000000002 |
| scripts/test_graph_dependency_integration.py:19 | SemanticModel |
| scripts/test_graph_first_scan.py:15 | fixture |
| scripts/test_graph_incremental.py:144 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_graph_incremental.py:145 | 00000000-0000-0000-0000-000000000002 |
| scripts/test_graph_incremental.py:157 | workspaces/ |
| scripts/test_graph_interpreter_spans.py:10 | fixture |
| scripts/test_graph_interpreter_spans.py:11 | fixture |
| scripts/test_graph_interpreter_spans.py:12 | fixture |
| scripts/test_graph_interpreter_spans.py:13 | fixture |
| scripts/test_graph_interpreter_spans.py:14 | fixture |
| scripts/test_graph_part_b.py:13 | fixture |
| scripts/test_graph_part_b.py:93 | fixture |
| scripts/test_graph_part_b.py:102 | fixture |
| scripts/test_graph_part_b.py:105 | fixture |
| scripts/test_graph_part_b.py:112 | fixture |
| scripts/test_graph_partitions.py:11 | fixture |
| scripts/test_graph_partitions.py:76 | fixture |
| scripts/test_graph_preflight.py:48 | fixture |
| scripts/test_graph_safe_failures.py:30 | 00000000-0000-0000-0000-000000000002 |
| scripts/test_graph_safe_failures.py:33 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_graph_scan_schedule_plan.py:9 | 00000000-0000-0000-0000-000000000001, subscriptions/ |
| scripts/test_graph_scan_schedule_plan.py:27 | subscriptions/ |
| scripts/test_graph_sql_changes.py:18 | Warehouse |
| scripts/test_graph_sql_changes.py:40 | Warehouse |
| scripts/test_graph_value_verification.py:9 | fixture |
| scripts/test_graph_value_verification.py:12 | fixture |
| scripts/test_graph_value_verification.py:13 | fixture |
| scripts/test_graph_value_verification.py:51 | fixture |
| scripts/test_graph_value_verification.py:57 | fixture |
| scripts/test_graph_value_verification.py:67 | fixture |
| scripts/test_graph_value_verification.py:71 | fixture |
| scripts/test_graph_value_verification.py:73 | fixture |
| scripts/test_graph_value_verification.py:80 | fixture |
| scripts/test_graph_value_verification.py:82 | fixture |
| scripts/test_graph_value_verification.py:85 | fixture |
| scripts/test_graph_value_verification.py:89 | fixture |
| scripts/test_graph_value_verification.py:91 | fixture |
| scripts/test_graph_value_verification.py:93 | fixture |
| scripts/test_graph_value_verification.py:97 | fixture |
| scripts/test_graph_value_verification.py:103 | fixture |
| scripts/test_graph_value_verification.py:129 | fixture |
| scripts/test_graph_value_verification.py:144 | fixture |
| scripts/test_guarded_blob_transport.py:51 | blob.core.windows.net, fixture |
| scripts/test_guarded_blob_transport.py:99 | blob.core.windows.net |
| scripts/test_hybrid_ticket.py:68 | fixture |
| scripts/test_hybrid_ticket.py:163 | fixture |
| scripts/test_hybrid_ticket.py:166 | fixture |
| scripts/test_hybrid_ticket.py:169 | fixture |
| scripts/test_hybrid_ticket.py:204 | fixture |
| scripts/test_hybrid_ticket.py:205 | fixture |
| scripts/test_hybrid_ticket.py:206 | fixture |
| scripts/test_hybrid_ticket.py:207 | fixture |
| scripts/test_hybrid_ticket.py:214 | fixture |
| scripts/test_hybrid_ticket.py:230 | fixture |
| scripts/test_hybrid_ticket.py:231 | fixture |
| scripts/test_hybrid_ticket.py:233 | fixture |
| scripts/test_hybrid_ticket.py:234 | fixture |
| scripts/test_hybrid_ticket.py:238 | fixture |
| scripts/test_hybrid_ticket.py:242 | fixture |
| scripts/test_hybrid_ticket.py:244 | fixture |
| scripts/test_import_fixture.py:7 | fixture |
| scripts/test_import_fixture.py:8 | fixture |
| scripts/test_import_fixture.py:122 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_import_fixture.py:137 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_import_fixture.py:148 | 11111111-1111-1111-1111-111111111111, 44444444-4444-4444-4444-444444444444 |
| scripts/test_import_fixture.py:155 | semantic_model |
| scripts/test_import_fixture.py:159 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_import_fixture.py:161 | semantic_model |
| scripts/test_import_fixture.py:171 | 11111111-1111-1111-1111-111111111111, 22222222-2222-2222-2222-222222222222 |
| scripts/test_import_fixture.py:172 | 33333333-3333-3333-3333-333333333333, 44444444-4444-4444-4444-444444444444 |
| scripts/test_import_fixture.py:177 | fixture, workspaces/ |
| scripts/test_import_fixture.py:178 | semanticModel |
| scripts/test_import_fixture.py:179 | Fixture, semanticModel |
| scripts/test_independent_evaluation.py:9 | fixture |
| scripts/test_independent_evaluation.py:35 | fixture |
| scripts/test_independent_evaluation.py:59 | fixture |
| scripts/test_independent_evaluation.py:60 | fixture |
| scripts/test_independent_evaluation.py:93 | fixture |
| scripts/test_independent_lower_read.py:17 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_independent_lower_read.py:61 | Warehouse |
| scripts/test_independent_lower_read.py:109 | Warehouse |
| scripts/test_independent_lower_read.py:111 | Warehouse |
| scripts/test_independent_lower_read.py:177 | warehouse |
| scripts/test_input_reference.py:7 | fixture |
| scripts/test_input_reference.py:9 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_input_reference.py:10 | 22222222-2222-4222-8222-222222222222 |
| scripts/test_input_reference.py:16 | fixture |
| scripts/test_input_reference.py:70 | 33333333-3333-4333-8333-333333333333 |
| scripts/test_installation_secrets.py:35 | workspace/ |
| scripts/test_intake_candidates.py:12 | warehouse |
| scripts/test_intake_candidates.py:27 | warehouse |
| scripts/test_intake_confirmation.py:7 | fixture |
| scripts/test_intake_confirmation.py:13 | Warehouse |
| scripts/test_intake_confirmation.py:27 | fixture |
| scripts/test_intake_confirmation.py:41 | fixture |
| scripts/test_intake_confirmation.py:61 | fixture |
| scripts/test_intake_confirmation.py:70 | fixture |
| scripts/test_intake_confirmation.py:76 | fixture |
| scripts/test_intake_confirmation.py:93 | fixture |
| scripts/test_intake_confirmation.py:104 | fixture |
| scripts/test_intake_confirmation.py:115 | fixture |
| scripts/test_intake_confirmation.py:128 | fixture |
| scripts/test_intake_confirmation.py:134 | fixture |
| scripts/test_intake_confirmation.py:144 | fixture |
| scripts/test_intake_confirmation.py:160 | fixture |
| scripts/test_intake_confirmation.py:166 | fixture |
| scripts/test_intake_confirmation.py:171 | fixture |
| scripts/test_intake_confirmation.py:177 | fixture |
| scripts/test_intake_confirmation.py:201 | fixture |
| scripts/test_intake_confirmation.py:212 | fixture |
| scripts/test_intake_confirmation.py:220 | fixture |
| scripts/test_intake_confirmation.py:224 | fixture |
| scripts/test_intake_confirmation.py:237 | fixture |
| scripts/test_intake_explicit_statement.py:8 | fixture |
| scripts/test_intake_explicit_statement.py:10 | fixture, warehouse |
| scripts/test_intake_explicit_statement.py:15 | fixture |
| scripts/test_intake_explicit_statement.py:25 | fixture |
| scripts/test_intake_explicit_statement.py:40 | fixture |
| scripts/test_intake_explicit_statement.py:42 | fixture |
| scripts/test_intake_explicit_statement.py:47 | fixture |
| scripts/test_intake_explicit_statement.py:51 | fixture |
| scripts/test_intake_explicit_statement.py:58 | fixture |
| scripts/test_intake_explicit_statement.py:60 | fixture |
| scripts/test_intake_explicit_statement.py:68 | fixture |
| scripts/test_intake_explicit_statement.py:102 | fixture |
| scripts/test_intake_extraction.py:11 | fixture |
| scripts/test_intake_extraction.py:19 | warehouse |
| scripts/test_intake_extraction.py:23 | Warehouse |
| scripts/test_intake_extraction.py:24 | warehouse |
| scripts/test_intake_extraction.py:30 | fixture |
| scripts/test_intake_extraction.py:45 | fixture |
| scripts/test_intake_extraction.py:57 | fixture |
| scripts/test_intake_extraction.py:67 | warehouse |
| scripts/test_intake_extraction.py:68 | warehouse |
| scripts/test_intake_extraction.py:70 | warehouse |
| scripts/test_intake_extraction.py:74 | warehouse |
| scripts/test_intake_extraction.py:82 | Warehouse, fixture, warehouse |
| scripts/test_intake_extraction.py:83 | warehouse |
| scripts/test_intake_extraction.py:84 | Warehouse |
| scripts/test_intake_extraction.py:85 | Warehouse |
| scripts/test_intake_extraction.py:89 | warehouse |
| scripts/test_intake_extraction.py:93 | Warehouse, fixture, warehouse |
| scripts/test_intake_extraction.py:94 | warehouse |
| scripts/test_intake_extraction.py:95 | Warehouse |
| scripts/test_intake_extraction.py:96 | warehouse |
| scripts/test_intake_extraction.py:98 | warehouse |
| scripts/test_intake_extraction.py:109 | fixture |
| scripts/test_intake_extraction.py:117 | fixture |
| scripts/test_intake_extraction.py:122 | fixture |
| scripts/test_intake_extraction.py:132 | fixture |
| scripts/test_intake_extraction.py:135 | fixture |
| scripts/test_intake_extraction.py:152 | fixture |
| scripts/test_intake_extraction.py:160 | fixture |
| scripts/test_intake_extraction.py:171 | fixture |
| scripts/test_intake_extraction.py:181 | fixture |
| scripts/test_intake_extraction.py:198 | fixture |
| scripts/test_intake_extraction.py:206 | fixture |
| scripts/test_intake_extraction.py:217 | fixture |
| scripts/test_intake_extraction.py:228 | fixture |
| scripts/test_intake_extraction.py:236 | fixture |
| scripts/test_intake_extraction.py:242 | fixture |
| scripts/test_intake_extraction.py:253 | fixture |
| scripts/test_intake_extraction.py:261 | fixture |
| scripts/test_intake_extraction.py:266 | Warehouse, warehouse |
| scripts/test_intake_extraction.py:267 | Warehouse, fixture |
| scripts/test_intake_extraction.py:268 | warehouse |
| scripts/test_intake_extraction.py:269 | warehouse |
| scripts/test_intake_extraction.py:271 | Warehouse |
| scripts/test_intake_extraction.py:273 | warehouse |
| scripts/test_intake_extraction.py:279 | warehouse |
| scripts/test_intake_extraction.py:280 | fixture |
| scripts/test_intake_extraction.py:281 | warehouse |
| scripts/test_intake_extraction.py:283 | warehouse |
| scripts/test_intake_extraction.py:287 | warehouse |
| scripts/test_intake_extraction.py:293 | fixture |
| scripts/test_intake_extraction.py:302 | fixture |
| scripts/test_intake_extraction.py:310 | fixture |
| scripts/test_intake_extraction.py:316 | warehouse |
| scripts/test_intake_extraction.py:317 | fixture |
| scripts/test_intake_extraction.py:318 | warehouse |
| scripts/test_intake_extraction.py:325 | fixture |
| scripts/test_intake_extraction.py:337 | fixture |
| scripts/test_intake_extraction.py:344 | fixture |
| scripts/test_intake_extraction.py:353 | fixture |
| scripts/test_intake_extraction.py:370 | fixture |
| scripts/test_intake_extraction.py:397 | fixture |
| scripts/test_intake_extraction.py:400 | Warehouse |
| scripts/test_intake_extraction.py:414 | fixture |
| scripts/test_intake_extraction.py:420 | fixture |
| scripts/test_intake_extraction.py:423 | fixture |
| scripts/test_intake_extraction.py:436 | fixture |
| scripts/test_intake_extraction.py:441 | fixture |
| scripts/test_intake_extraction.py:442 | fixture |
| scripts/test_intake_extraction.py:455 | fixture |
| scripts/test_intake_families.py:12 | Fixture, fixture |
| scripts/test_intake_families.py:19 | FIXTURE, fixture |
| scripts/test_intake_families.py:26 | fixture |
| scripts/test_intake_families.py:28 | FIXTURE |
| scripts/test_intake_families.py:34 | fixture |
| scripts/test_intake_families.py:42 | fixture |
| scripts/test_intake_families.py:54 | fixture |
| scripts/test_intake_families.py:115 | fixture |
| scripts/test_intake_families.py:119 | fixture |
| scripts/test_intake_families.py:132 | Fixture |
| scripts/test_intake_inventory_resolution.py:8 | fixture |
| scripts/test_intake_inventory_resolution.py:10 | fixture |
| scripts/test_intake_inventory_resolution.py:11 | fixture |
| scripts/test_intake_inventory_resolution.py:17 | fixture |
| scripts/test_intake_inventory_resolution.py:69 | fixture |
| scripts/test_intake_inventory_resolution.py:70 | fixture |
| scripts/test_intake_inventory_resolution.py:103 | fixture |
| scripts/test_intake_inventory_resolution.py:106 | fixture |
| scripts/test_intake_matrix_address.py:4 | fixture |
| scripts/test_intake_matrix_address.py:12 | fixture |
| scripts/test_intake_matrix_address.py:22 | fixture |
| scripts/test_intake_matrix_address.py:29 | fixture |
| scripts/test_intake_matrix_address.py:43 | fixture |
| scripts/test_intake_matrix_address.py:55 | fixture |
| scripts/test_intake_matrix_address.py:66 | Warehouse, fixture |
| scripts/test_intake_matrix_address.py:67 | Warehouse |
| scripts/test_intake_matrix_address.py:70 | warehouse |
| scripts/test_intake_matrix_address.py:75 | fixture, warehouse |
| scripts/test_intake_matrix_address.py:77 | warehouse |
| scripts/test_intake_matrix_address.py:82 | fixture |
| scripts/test_intake_matrix_address.py:87 | fixture |
| scripts/test_intake_matrix_address.py:94 | warehouse |
| scripts/test_intake_matrix_address.py:97 | fixture |
| scripts/test_intake_matrix_address.py:98 | Warehouse |
| scripts/test_intake_matrix_address.py:99 | fixture |
| scripts/test_intake_matrix_address.py:100 | Warehouse |
| scripts/test_intake_matrix_address.py:105 | warehouse |
| scripts/test_intake_matrix_address.py:106 | warehouse |
| scripts/test_intake_matrix_address.py:110 | fixture |
| scripts/test_intake_matrix_address.py:112 | warehouse |
| scripts/test_intake_matrix_address.py:118 | fixture |
| scripts/test_intake_matrix_address.py:121 | fixture |
| scripts/test_intake_matrix_address.py:126 | fixture |
| scripts/test_intake_name_resolution.py:8 | fixture |
| scripts/test_intake_name_resolution.py:19 | fixture |
| scripts/test_intake_name_resolution.py:32 | Warehouse, warehouse |
| scripts/test_intake_name_resolution.py:33 | fixture |
| scripts/test_intake_name_resolution.py:34 | warehouse |
| scripts/test_intake_name_resolution.py:35 | Warehouse |
| scripts/test_intake_name_resolution.py:44 | warehouse |
| scripts/test_intake_name_resolution.py:45 | fixture |
| scripts/test_intake_name_resolution.py:46 | warehouse |
| scripts/test_intake_name_resolution.py:53 | warehouse |
| scripts/test_intake_name_resolution.py:54 | fixture |
| scripts/test_intake_name_resolution.py:55 | warehouse |
| scripts/test_intake_name_resolution.py:87 | fixture |
| scripts/test_intake_name_resolution.py:100 | fixture |
| scripts/test_intake_name_resolution.py:110 | Warehouse, warehouse |
| scripts/test_intake_name_resolution.py:111 | fixture |
| scripts/test_intake_name_resolution.py:112 | warehouse |
| scripts/test_intake_name_resolution.py:113 | Warehouse |
| scripts/test_intake_name_resolution.py:114 | warehouse |
| scripts/test_intake_name_resolution.py:119 | warehouse |
| scripts/test_intake_name_resolution.py:125 | fixture |
| scripts/test_intake_name_resolution.py:132 | Warehouse, warehouse |
| scripts/test_intake_name_resolution.py:133 | fixture |
| scripts/test_intake_name_resolution.py:134 | Warehouse |
| scripts/test_intake_name_resolution.py:135 | warehouse |
| scripts/test_intake_name_resolution.py:147 | fixture |
| scripts/test_intake_name_resolution.py:181 | fixture |
| scripts/test_intake_name_resolution.py:193 | fixture |
| scripts/test_intake_name_resolution.py:202 | fixture |
| scripts/test_intake_name_resolution.py:216 | fixture |
| scripts/test_intake_name_resolution.py:227 | fixture |
| scripts/test_intake_name_resolution.py:229 | fixture |
| scripts/test_intake_name_resolution.py:235 | fixture |
| scripts/test_intake_name_resolution.py:240 | fixture |
| scripts/test_intake_name_resolution.py:243 | fixture |
| scripts/test_intake_name_resolution.py:248 | Warehouse |
| scripts/test_intake_numeral_roles.py:15 | 20261003, Application load fixture, fixture |
| scripts/test_intake_numeral_roles.py:16 | 20261003, Application load fixture |
| scripts/test_intake_numeral_roles.py:25 | 20261003, Application load fixture |
| scripts/test_intake_numeral_roles.py:26 | 20261003, Application load fixture |
| scripts/test_intake_numeral_roles.py:80 | 20261003 |
| scripts/test_intake_questionnaire.py:5 | fixture |
| scripts/test_intake_questionnaire.py:9 | workspace/ |
| scripts/test_intake_questionnaire.py:13 | fixture |
| scripts/test_intake_questionnaire.py:56 | fixture |
| scripts/test_intake_questionnaire.py:135 | workspace/ |
| scripts/test_intake_questionnaire.py:137 | workspace/ |
| scripts/test_intake_questionnaire.py:140 | workspace/ |
| scripts/test_intake_quote_retry.py:6 | fixture |
| scripts/test_intake_quote_retry.py:11 | fixture |
| scripts/test_intake_quote_retry.py:29 | fixture |
| scripts/test_intake_quote_retry.py:63 | fixture |
| scripts/test_intake_quote_retry.py:77 | fixture |
| scripts/test_intake_rules.py:10 | fixture |
| scripts/test_intake_rules.py:70 | fixture |
| scripts/test_intake_rules.py:95 | fixture |
| scripts/test_intake_span_references.py:5 | fixture |
| scripts/test_intake_span_references.py:16 | fixture |
| scripts/test_intake_span_references.py:17 | fixture |
| scripts/test_intake_span_references.py:31 | fixture |
| scripts/test_intake_span_references.py:56 | warehouse |
| scripts/test_intake_span_references.py:61 | warehouse |
| scripts/test_intake_span_references.py:64 | warehouse |
| scripts/test_intake_span_references.py:65 | warehouse |
| scripts/test_intake_span_references.py:67 | warehouse |
| scripts/test_intake_span_references.py:78 | fixture |
| scripts/test_intake_span_references.py:85 | fixture |
| scripts/test_intake_vocabulary.py:62 | fixture |
| scripts/test_intake_vocabulary.py:64 | fixture |
| scripts/test_intake_vocabulary.py:79 | fixture |
| scripts/test_intake_vocabulary.py:81 | fixture |
| scripts/test_investigation_evidence_api.py:15 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_investigation_evidence_api.py:16 | 22222222-2222-2222-2222-222222222222 |
| scripts/test_investigation_evidence_api.py:70 | 33333333-3333-3333-3333-333333333333 |
| scripts/test_investigation_selection.py:15 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_investigation_selection.py:36 | semantic_model |
| scripts/test_investigation_selection.py:37 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_investigation_selection.py:38 | lakehouse |
| scripts/test_investigator_checkpoint.py:16 | fixture |
| scripts/test_investigator_checkpoint.py:19 | fixture |
| scripts/test_investigator_checkpoint.py:23 | fixture |
| scripts/test_investigator_frontier.py:4 | fixture |
| scripts/test_investigator_frontier.py:8 | fixture |
| scripts/test_investigator_frontier.py:22 | fixture |
| scripts/test_investigator_frontier.py:33 | fixture |
| scripts/test_investigator_frontier.py:40 | fixture |
| scripts/test_investigator_frontier.py:49 | fixture |
| scripts/test_investigator_harness.py:13 | fixture |
| scripts/test_investigator_harness.py:41 | fixture |
| scripts/test_investigator_harness.py:43 | fixture |
| scripts/test_investigator_harness.py:47 | fixture |
| scripts/test_investigator_harness.py:50 | fixture |
| scripts/test_investigator_harness.py:54 | fixture |
| scripts/test_investigator_harness.py:55 | fixture |
| scripts/test_investigator_harness.py:56 | fixture |
| scripts/test_investigator_harness.py:88 | fixture |
| scripts/test_investigator_harness.py:89 | fixture |
| scripts/test_investigator_harness.py:107 | fixture |
| scripts/test_investigator_harness.py:122 | fixture |
| scripts/test_investigator_harness.py:123 | fixture |
| scripts/test_investigator_harness.py:153 | fixture |
| scripts/test_investigator_harness.py:160 | fixture |
| scripts/test_investigator_harness.py:172 | blob.core.windows.net, fixture |
| scripts/test_investigator_heavy_reader.py:16 | fixture |
| scripts/test_investigator_heavy_reader.py:38 | fixture |
| scripts/test_investigator_heavy_reader.py:39 | fixture |
| scripts/test_investigator_playbook.py:4 | fixture |
| scripts/test_investigator_playbook.py:8 | fixture |
| scripts/test_investigator_workspace.py:16 | fixture |
| scripts/test_investigator_workspace.py:23 | fixture |
| scripts/test_investigator_workspace.py:70 | workspace/ |
| scripts/test_investigator_workspace.py:197 | workspace/ |
| scripts/test_investigator_workspace.py:198 | workspace/ |
| scripts/test_investigator_workspace.py:199 | workspace/ |
| scripts/test_investigator_workspace.py:202 | workspace/ |
| scripts/test_investigator_workspace.py:203 | workspace/ |
| scripts/test_investigator_workspace.py:205 | workspace/ |
| scripts/test_investigator_workspace.py:206 | workspace/ |
| scripts/test_investigator_workspace.py:215 | workspace/ |
| scripts/test_item_metadata_history.py:24 | fixture |
| scripts/test_item_metadata_history.py:85 | fixture |
| scripts/test_joint_native_capture.py:5 | fixture |
| scripts/test_joint_native_capture.py:16 | fixture |
| scripts/test_joint_native_capture.py:129 | fixture |
| scripts/test_joint_native_capture.py:132 | fixture |
| scripts/test_judge_composition_retry.py:5 | fixture |
| scripts/test_judge_composition_retry.py:12 | fixture |
| scripts/test_keyed_readback.py:10 | fixture |
| scripts/test_keyed_readback.py:22 | fixture |
| scripts/test_keyed_readback.py:239 | fixture |
| scripts/test_keyed_readback.py:242 | fixture |
| scripts/test_keyed_readback.py:243 | fixture |
| scripts/test_keyed_readback.py:288 | fixture |
| scripts/test_keyed_readback.py:296 | fixture |
| scripts/test_keyed_readback.py:297 | fixture |
| scripts/test_layer_roles.py:12 | semantic model |
| scripts/test_layer_roles.py:13 | semantic model |
| scripts/test_ledger_investigator.py:15 | warehouse |
| scripts/test_ledger_investigator.py:22 | fixture |
| scripts/test_ledger_investigator.py:53 | warehouse |
| scripts/test_ledger_investigator.py:66 | warehouse |
| scripts/test_ledger_investigator.py:97 | warehouse |
| scripts/test_ledger_investigator.py:106 | warehouse |
| scripts/test_ledger_investigator.py:370 | warehouse |
| scripts/test_ledger_investigator.py:374 | warehouse |
| scripts/test_ledger_investigator.py:386 | warehouse |
| scripts/test_ledger_investigator.py:394 | warehouse |
| scripts/test_ledger_investigator.py:402 | warehouse |
| scripts/test_ledger_investigator.py:414 | warehouse |
| scripts/test_ledger_investigator.py:423 | warehouse |
| scripts/test_ledger_investigator.py:484 | warehouse |
| scripts/test_ledger_investigator.py:603 | warehouse |
| scripts/test_ledger_investigator.py:666 | fixture |
| scripts/test_ledger_investigator.py:693 | warehouse |
| scripts/test_ledger_investigator.py:765 | fixture |
| scripts/test_ledger_investigator_ports.py:112 | warehouse |
| scripts/test_legacy_report_structure.py:8 | 11111111-1111-1111-1111-111111111111, 22222222-2222-2222-2222-222222222222 |
| scripts/test_legacy_report_structure.py:84 | workspaces/ |
| scripts/test_lineage.py:19 | fixture |
| scripts/test_lineage.py:30 | aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa |
| scripts/test_lineage.py:32 | SemanticModel |
| scripts/test_lineage.py:35 | semanticmodel |
| scripts/test_lineage.py:92 | SemanticModel |
| scripts/test_lineage.py:99 | SemanticModel |
| scripts/test_lineage_audit.py:9 | fixture |
| scripts/test_lineage_audit.py:17 | fixture |
| scripts/test_lineage_audit.py:22 | fixture |
| scripts/test_lineage_audit.py:28 | fixture |
| scripts/test_lineage_audit.py:54 | Lakehouse, lakehouse, workspace/ |
| scripts/test_lineage_audit.py:56 | lakehouse |
| scripts/test_lineage_limits.py:4 | fixture |
| scripts/test_lineage_limits.py:9 | fixture |
| scripts/test_lineage_limits.py:17 | fixture |
| scripts/test_lineage_limits.py:39 | fixture |
| scripts/test_lineage_limits.py:42 | fixture |
| scripts/test_lineage_runtime.py:2 | fixture |
| scripts/test_lineage_runtime.py:7 | fixture |
| scripts/test_live_gateway.py:13 | workspace/ |
| scripts/test_live_gateway.py:175 | blob.core.windows.net |
| scripts/test_live_gateway.py:177 | postgres.database.azure.com |
| scripts/test_live_gateway.py:183 | postgres.database.azure.com |
| scripts/test_live_gateway.py:186 | postgres.database.azure.com |
| scripts/test_live_gateway.py:191 | fixture |
| scripts/test_live_gateway.py:193 | fixture |
| scripts/test_live_gateway.py:194 | fixture |
| scripts/test_live_report_lists.py:4 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_live_report_lists.py:5 | 22222222-2222-4222-8222-222222222222 |
| scripts/test_live_report_lists.py:6 | 33333333-3333-4333-8333-333333333333 |
| scripts/test_local_accounting.py:41 | fixture |
| scripts/test_local_execution_approval.py:13 | fixture |
| scripts/test_local_execution_approval.py:14 | fixture |
| scripts/test_local_execution_approval.py:20 | fixture |
| scripts/test_local_execution_approval.py:23 | fixture |
| scripts/test_local_execution_approval.py:80 | fixture |
| scripts/test_local_execution_approval.py:84 | fixture |
| scripts/test_local_execution_approval.py:86 | fixture |
| scripts/test_local_execution_approval.py:90 | fixture |
| scripts/test_local_exported_process.py:20 | fixture |
| scripts/test_local_exported_process.py:104 | fixture |
| scripts/test_local_hospital_generator.py:10 | fixture |
| scripts/test_local_hospital_generator.py:13 | fixture |
| scripts/test_local_hospital_generator.py:14 | fixture |
| scripts/test_local_hospital_generator.py:15 | fixture |
| scripts/test_local_hospital_generator.py:16 | fixture, warehouse |
| scripts/test_local_hospital_generator.py:17 | fixture |
| scripts/test_local_hospital_generator.py:18 | fixture, warehouse |
| scripts/test_local_hospital_generator.py:19 | fixture |
| scripts/test_local_hospital_generator.py:20 | fixture |
| scripts/test_local_hospital_generator.py:21 | fixture |
| scripts/test_local_hospital_generator.py:22 | fixture |
| scripts/test_local_hospital_generator.py:23 | fixture |
| scripts/test_local_hospital_generator.py:24 | fixture, warehouse |
| scripts/test_local_hospital_generator.py:25 | fixture |
| scripts/test_local_hospital_generator.py:26 | fixture |
| scripts/test_local_hospital_generator.py:27 | fixture |
| scripts/test_local_hospital_generator.py:52 | lakehouse |
| scripts/test_local_hospital_generator.py:53 | warehouse |
| scripts/test_local_hospital_generator.py:61 | warehouse |
| scripts/test_local_hospital_generator.py:75 | d237966c-b0b6-4123-bc89-e69643f4bf1f |
| scripts/test_local_hospital_generator.py:87 | fixture |
| scripts/test_local_hospital_generator.py:89 | HealthNet |
| scripts/test_local_hospital_generator.py:95 | warehouse |
| scripts/test_local_hospital_generator.py:97 | hn_dw |
| scripts/test_local_hospital_generator.py:100 | warehouse |
| scripts/test_local_hospital_generator.py:117 | workspaces/ |
| scripts/test_local_hospital_generator.py:128 | workspaces/ |
| scripts/test_local_hospital_generator.py:133 | workspaces/ |
| scripts/test_local_hospital_generator.py:137 | warehouse |
| scripts/test_local_hospital_generator.py:138 | lakehouse, warehouse |
| scripts/test_local_hospital_generator.py:139 | warehouse |
| scripts/test_local_hospital_generator.py:142 | warehouse |
| scripts/test_local_hospital_generator.py:144 | warehouse |
| scripts/test_local_hospital_generator.py:145 | hn_dw |
| scripts/test_local_hospital_generator.py:156 | warehouse |
| scripts/test_local_hospital_generator.py:157 | lakehouse, warehouse |
| scripts/test_local_hospital_generator.py:158 | warehouse |
| scripts/test_local_hospital_generator.py:159 | Warehouse |
| scripts/test_local_hospital_generator.py:160 | warehouse |
| scripts/test_local_hospital_generator.py:163 | Warehouse |
| scripts/test_local_hospital_generator.py:164 | warehouse |
| scripts/test_local_hospital_generator.py:168 | warehouse |
| scripts/test_local_hospital_generator.py:172 | warehouse |
| scripts/test_local_hospital_generator.py:176 | HEALTHNET |
| scripts/test_local_hospital_generator.py:183 | HEALTHNET |
| scripts/test_local_hospital_generator.py:185 | HEALTHNET |
| scripts/test_local_hospital_generator.py:189 | fixture |
| scripts/test_local_hospital_generator.py:190 | hn_clinical |
| scripts/test_local_hospital_generator.py:198 | hn_billing |
| scripts/test_local_hospital_generator.py:246 | warehouse |
| scripts/test_local_hospital_generator.py:247 | warehouse |
| scripts/test_local_hospital_generator.py:255 | hn_dw |
| scripts/test_local_hospital_generator.py:258 | hn_billing |
| scripts/test_local_hospital_generator.py:264 | lakehouse, warehouse |
| scripts/test_local_hospital_generator.py:275 | hn_dw |
| scripts/test_local_hospital_generator.py:276 | HealthNet |
| scripts/test_local_hospital_generator.py:277 | HealthNet |
| scripts/test_local_hospital_generator.py:278 | HealthNet |
| scripts/test_local_hospital_generator.py:293 | lakehouse |
| scripts/test_local_hospital_generator.py:309 | fixture |
| scripts/test_local_hospital_generator.py:310 | HealthNet |
| scripts/test_local_hospital_generator.py:350 | hn_billing |
| scripts/test_local_hospital_generator.py:353 | hn_clinical |
| scripts/test_managed_identity_auth.py:15 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_managed_identity_auth.py:16 | 22222222-2222-2222-2222-222222222222 |
| scripts/test_managed_identity_auth.py:17 | 33333333-3333-3333-3333-333333333333 |
| scripts/test_managed_identity_auth.py:18 | 44444444-4444-4444-4444-444444444444 |
| scripts/test_managed_identity_auth.py:19 | 55555555-5555-5555-5555-555555555555 |
| scripts/test_managed_identity_auth.py:32 | fixture |
| scripts/test_managed_identity_auth.py:53 | cfa8b339-82a2-471a-a3c9-0fc0be7a4093 |
| scripts/test_managed_identity_auth.py:85 | database.windows.net |
| scripts/test_managed_identity_auth.py:105 | database.windows.net |
| scripts/test_managed_identity_auth.py:217 | fixture |
| scripts/test_managed_sql_worker.py:11 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_managed_sql_worker.py:12 | 22222222-2222-2222-2222-222222222222, 33333333-3333-3333-3333-333333333333 |
| scripts/test_managed_sql_worker.py:36 | database.windows.net |
| scripts/test_managed_worker_replay.py:14 | database.windows.net |
| scripts/test_mechanism_subject_grammar.py:5 | fixture |
| scripts/test_mechanism_subject_grammar.py:13 | fixture |
| scripts/test_mechanism_subject_grammar.py:18 | fixture |
| scripts/test_mechanism_subject_grammar.py:22 | fixture |
| scripts/test_mechanism_subject_grammar.py:25 | fixture |
| scripts/test_mechanism_subject_grammar.py:28 | fixture |
| scripts/test_metadata_connectors.py:65 | database.windows.net |
| scripts/test_metadata_connectors.py:67 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_metadata_connectors.py:72 | database.windows.net |
| scripts/test_metadata_connectors.py:107 | SemanticModel |
| scripts/test_metadata_connectors.py:108 | workspace/, workspaces/ |
| scripts/test_metadata_connectors.py:109 | workspace/, workspaces/ |
| scripts/test_metadata_connectors.py:110 | workspace/ |
| scripts/test_metadata_connectors.py:140 | lakehouse |
| scripts/test_metadata_connectors.py:141 | lakehouse |
| scripts/test_metadata_inventory.py:21 | Lakehouse |
| scripts/test_metadata_inventory.py:24 | Lakehouse |
| scripts/test_metadata_inventory.py:90 | SemanticModel |
| scripts/test_metric_visual_checks.py:3 | fixture |
| scripts/test_metric_visual_checks.py:10 | fixture |
| scripts/test_metric_visual_checks.py:36 | fixture |
| scripts/test_microsoft_copy_mapping.py:11 | Lakehouse |
| scripts/test_microsoft_readiness.py:9 | fixture |
| scripts/test_microsoft_readiness.py:10 | fixture |
| scripts/test_microsoft_readiness.py:15 | 55555555-5555-4555-8555-555555555555 |
| scripts/test_microsoft_readiness.py:23 | SemanticModel |
| scripts/test_microsoft_readiness.py:26 | Lakehouse |
| scripts/test_microsoft_readiness.py:35 | Warehouse |
| scripts/test_microsoft_readiness.py:43 | fixture |
| scripts/test_model_eval_reader.py:4 | fixture |
| scripts/test_model_eval_reader.py:17 | fixture |
| scripts/test_model_eval_translation.py:4 | fixture |
| scripts/test_model_eval_translation.py:44 | fixture |
| scripts/test_model_onboarding.py:45 | SemanticModel |
| scripts/test_model_onboarding.py:47 | semanticmodel |
| scripts/test_model_onboarding.py:49 | SemanticModel |
| scripts/test_model_only_installation.py:26 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_model_subject_input.py:5 | fixture |
| scripts/test_model_subject_input.py:13 | fixture |
| scripts/test_model_subject_input.py:34 | fixture |
| scripts/test_model_subject_input.py:41 | fixture |
| scripts/test_model_subject_input.py:58 | fixture |
| scripts/test_model_subject_input.py:75 | fixture |
| scripts/test_model_usage_reconciliation.py:2 | fixture |
| scripts/test_model_usage_reconciliation.py:6 | fixture |
| scripts/test_multilayer_lab.py:29 | fixture |
| scripts/test_multilayer_review.py:36 | fixture |
| scripts/test_narrative_form.py:5 | fixture |
| scripts/test_narrative_form.py:10 | fixture |
| scripts/test_narrative_form.py:22 | fixture |
| scripts/test_narrative_form.py:28 | fixture |
| scripts/test_narrative_form.py:37 | fixture |
| scripts/test_narrative_form.py:38 | fixture |
| scripts/test_narrative_form.py:39 | workspace/ |
| scripts/test_narrative_form.py:40 | workspace/ |
| scripts/test_narrative_form.py:41 | workspace/ |
| scripts/test_narrative_form.py:60 | fixture |
| scripts/test_narrative_form.py:76 | fixture |
| scripts/test_narrative_form.py:92 | fixture |
| scripts/test_narrative_form.py:104 | fixture |
| scripts/test_narrative_form.py:120 | fixture |
| scripts/test_narrative_form.py:137 | fixture |
| scripts/test_native_context_planning.py:23 | workspace/ |
| scripts/test_native_context_planning.py:26 | 22222222-2222-4222-8222-222222222222, workspace/ |
| scripts/test_native_context_planning.py:27 | SemanticModel |
| scripts/test_native_context_planning.py:29 | 22222222-2222-4222-8222-222222222222, semanticmodel |
| scripts/test_native_context_planning.py:30 | SemanticModel |
| scripts/test_native_context_planning.py:41 | fixture |
| scripts/test_native_diagnostics.py:15 | fixture |
| scripts/test_native_diagnostics.py:43 | fixture |
| scripts/test_native_diagnostics.py:123 | 00000000-0000-0000-0000-000000000001, 00000000-0000-0000-0000-000000000002 |
| scripts/test_native_diagnostics.py:128 | 00000000-0000-0000-0000-000000000001, 00000000-0000-0000-0000-000000000002 |
| scripts/test_normal_audit.py:85 | 11111111-1111-4111-8111-111111111111, 22222222-2222-4222-8222-222222222222 |
| scripts/test_normal_audit.py:89 | fixture |
| scripts/test_operational_intake.py:5 | fixture |
| scripts/test_operational_intake.py:16 | fixture |
| scripts/test_operational_intake.py:20 | fixture |
| scripts/test_operational_intake.py:44 | fixture |
| scripts/test_page_investigations.py:10 | fixture |
| scripts/test_page_investigations.py:32 | fixture |
| scripts/test_page_investigations.py:95 | fixture |
| scripts/test_page_investigations.py:102 | fixture |
| scripts/test_page_investigations.py:278 | fixture |
| scripts/test_parallel_usage_reservations.py:5 | fixture |
| scripts/test_parallel_usage_reservations.py:11 | fixture |
| scripts/test_path_narrative.py:4 | fixture |
| scripts/test_path_narrative.py:45 | fixture |
| scripts/test_physical_binding.py:13 | fixture |
| scripts/test_physical_binding.py:16 | fixture |
| scripts/test_physical_binding.py:17 | fixture |
| scripts/test_physical_binding.py:32 | fixture |
| scripts/test_physical_binding.py:33 | fixture |
| scripts/test_physical_binding.py:55 | Lakehouse, workspace/ |
| scripts/test_physical_transport_retry.py:62 | fixture |
| scripts/test_physical_transport_retry.py:67 | fixture |
| scripts/test_physical_transport_retry.py:70 | fixture |
| scripts/test_pipeline_adapter_owned.py:10 | fixture |
| scripts/test_pipeline_adapter_owned.py:27 | 12345678-1234-1234-1234-123456789abc |
| scripts/test_plan_archive_batches.py:31 | fixture |
| scripts/test_plan_review_api.py:9 | fixture |
| scripts/test_plan_review_api.py:17 | fixture |
| scripts/test_planner_projection.py:15 | FIXTURE, fixture |
| scripts/test_planner_projection.py:31 | FIXTURE |
| scripts/test_planner_projection.py:49 | FIXTURE |
| scripts/test_planner_projection.py:68 | FIXTURE |
| scripts/test_planner_projection.py:69 | FIXTURE |
| scripts/test_planner_projection.py:83 | fixture |
| scripts/test_planner_projection.py:169 | fixture |
| scripts/test_planner_projection.py:171 | fixture |
| scripts/test_planner_recording.py:12 | fixture |
| scripts/test_planner_recording.py:17 | fixture |
| scripts/test_planner_recording.py:18 | fixture |
| scripts/test_planner_recording.py:168 | fixture |
| scripts/test_planner_recording.py:170 | fixture |
| scripts/test_platform_blob_transfer.py:28 | database.windows.net |
| scripts/test_platform_blob_transfer.py:35 | blob.core.windows.net, fixture |
| scripts/test_platform_blob_transfer.py:40 | blob.core.windows.net, fixture |
| scripts/test_platform_blob_transfer.py:47 | fixture |
| scripts/test_platform_blob_transfer.py:54 | blob.core.windows.net, fixture |
| scripts/test_platform_blob_transfer.py:55 | blob.core.windows.net, fixture |
| scripts/test_platform_blob_transfer.py:56 | fixture |
| scripts/test_platform_cas.py:18 | blob.core.windows.net |
| scripts/test_platform_cas.py:51 | blob.core.windows.net |
| scripts/test_platform_deployment.py:16 | postgres.database.azure.com |
| scripts/test_platform_health.py:12 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_platform_health.py:13 | 22222222-2222-4222-8222-222222222222, 33333333-3333-4333-8333-333333333333 |
| scripts/test_platform_health.py:15 | postgres.database.azure.com |
| scripts/test_platform_health.py:16 | blob.core.windows.net |
| scripts/test_platform_literal_sweep.py:1 | fixture |
| scripts/test_platform_literal_sweep.py:11 | orderops_investigator |
| scripts/test_platform_literal_sweep.py:13 | fixture, warehouse |
| scripts/test_platform_literal_sweep.py:14 | fixture |
| scripts/test_platform_literal_sweep.py:36 | fixture |
| scripts/test_platform_literal_sweep.py:62 | 12345678-1234-1234-1234-123456789012, skynwhy.com |
| scripts/test_platform_literal_sweep.py:63 | fixture |
| scripts/test_platform_literal_sweep.py:65 | fixture |
| scripts/test_platform_preflight_receipts.py:45 | semantic_model |
| scripts/test_platform_preflight_receipts.py:65 | fixture |
| scripts/test_platform_proposers.py:12 | fixture |
| scripts/test_platform_proposers.py:72 | 00000000-0000-0000-0000-000000000001, 00000000-0000-0000-0000-000000000002 |
| scripts/test_platform_proposers.py:73 | 00000000-0000-0000-0000-000000000003 |
| scripts/test_platform_proposers.py:74 | SemanticModel |
| scripts/test_platform_proposers.py:76 | Lakehouse |
| scripts/test_platform_proposers.py:80 | workspaces/ |
| scripts/test_portal_ticket_navigation.py:11 | workspace/ |
| scripts/test_powerbi_contract.py:1 | semantic model |
| scripts/test_powerbi_contract.py:10 | SemanticModel |
| scripts/test_prepare_checksum_cleanup.py:15 | 08086928-0113-4a0c-9c4e-8061f3980b14 |
| scripts/test_prepare_checksum_cleanup.py:17 | fixture |
| scripts/test_prepare_checksum_cleanup.py:28 | fixture |
| scripts/test_prepare_checksum_cleanup.py:46 | fixture |
| scripts/test_prepare_live_enrichment.py:18 | fixture |
| scripts/test_prepare_live_enrichment.py:25 | fixture |
| scripts/test_prepare_live_enrichment.py:26 | fixture |
| scripts/test_prepare_live_enrichment.py:35 | fixture |
| scripts/test_prepare_runner_retry_inputs.py:16 | fixture |
| scripts/test_prepare_runner_retry_inputs.py:17 | 11111111-1111-1111-1111-111111111111, 22222222-2222-2222-2222-222222222222, 33333333-3333-3333-3333-333333333333, fixture |
| scripts/test_prepare_runner_retry_inputs.py:21 | fixture |
| scripts/test_prepare_runner_retry_inputs.py:23 | fixture |
| scripts/test_prepare_runner_retry_inputs.py:25 | fixture |
| scripts/test_prepare_runner_retry_inputs.py:30 | fixture |
| scripts/test_prepare_runner_retry_inputs.py:52 | fixture |
| scripts/test_privacy_end_to_end.py:105 | fixture |
| scripts/test_privacy_end_to_end.py:107 | 11111111-1111-4111-8111-111111111111, 22222222-2222-4222-8222-222222222222 |
| scripts/test_privacy_end_to_end.py:108 | 33333333-3333-4333-8333-333333333333 |
| scripts/test_privacy_end_to_end.py:119 | fixture |
| scripts/test_privacy_projection.py:230 | fixture |
| scripts/test_privacy_projection.py:303 | fixture |
| scripts/test_privacy_projection.py:306 | fixture |
| scripts/test_probe_execution_surfaces.py:10 | lakehouse |
| scripts/test_probe_execution_surfaces.py:112 | 00000000-0000-0000-0000-000000000001, 00000000-0000-0000-0000-000000000002 |
| scripts/test_probe_execution_surfaces.py:114 | lakehouse |
| scripts/test_probe_execution_surfaces.py:155 | warehouse |
| scripts/test_probe_execution_surfaces.py:157 | warehouse |
| scripts/test_probe_execution_surfaces.py:158 | warehouse |
| scripts/test_probe_execution_surfaces.py:164 | database.windows.net |
| scripts/test_process_adapter_factory.py:5 | fixture |
| scripts/test_process_adapter_factory.py:9 | fixture |
| scripts/test_process_adapter_factory.py:10 | fixture |
| scripts/test_process_adapter_factory.py:11 | fixture |
| scripts/test_process_adapter_factory.py:17 | fixture |
| scripts/test_process_adapter_factory.py:19 | fixture |
| scripts/test_process_adapter_factory.py:28 | fixture |
| scripts/test_process_adapter_factory.py:31 | fixture |
| scripts/test_process_adapter_factory.py:65 | fixture |
| scripts/test_process_adapter_factory.py:69 | fixture |
| scripts/test_process_adapter_factory.py:73 | fixture |
| scripts/test_process_adapter_factory.py:81 | fixture |
| scripts/test_process_adapter_factory.py:88 | fixture |
| scripts/test_process_adapter_factory.py:93 | fixture |
| scripts/test_process_debugging.py:6 | fixture |
| scripts/test_process_debugging.py:13 | fixture |
| scripts/test_process_debugging.py:14 | fixture |
| scripts/test_process_debugging.py:377 | fixture |
| scripts/test_process_debugging.py:378 | fixture |
| scripts/test_process_debugging.py:379 | fixture |
| scripts/test_process_debugging.py:387 | fixture |
| scripts/test_process_debugging.py:392 | fixture |
| scripts/test_process_debugging.py:393 | fixture |
| scripts/test_process_debugging.py:394 | fixture |
| scripts/test_process_debugging.py:405 | fixture |
| scripts/test_process_debugging.py:420 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_process_debugging.py:421 | 00000000-0000-0000-0000-000000000002 |
| scripts/test_process_debugging.py:423 | 00000000-0000-0000-0000-000000000002 |
| scripts/test_process_debugging.py:426 | Lakehouse |
| scripts/test_process_debugging.py:427 | Lakehouse |
| scripts/test_process_debugging.py:428 | Lakehouse |
| scripts/test_process_debugging.py:432 | SemanticModel |
| scripts/test_process_debugging.py:444 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_process_debugging.py:447 | SemanticModel |
| scripts/test_process_debugging.py:457 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_process_debugging.py:461 | SemanticModel |
| scripts/test_process_debugging.py:507 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_process_failure_address.py:4 | fixture |
| scripts/test_process_failure_address.py:18 | fixture |
| scripts/test_process_read_receipts.py:9 | fixture |
| scripts/test_process_read_receipts.py:17 | fixture |
| scripts/test_process_receipt_registry.py:77 | fixture |
| scripts/test_process_receipt_registry.py:78 | fixture |
| scripts/test_process_receipt_registry.py:107 | fixture |
| scripts/test_process_receipt_registry.py:109 | fixture |
| scripts/test_process_sqlite_diagnostics.py:15 | fixture |
| scripts/test_process_sqlite_diagnostics.py:17 | fixture |
| scripts/test_process_sqlite_diagnostics.py:52 | fixture |
| scripts/test_process_sqlite_diagnostics.py:69 | fixture |
| scripts/test_process_tape.py:47 | fixture |
| scripts/test_process_tape.py:48 | fixture |
| scripts/test_process_tape.py:209 | fixture |
| scripts/test_process_tape.py:211 | fixture |
| scripts/test_process_tape.py:246 | fixture |
| scripts/test_process_tape.py:248 | fixture |
| scripts/test_process_tape.py:257 | fixture |
| scripts/test_process_tape.py:280 | fixture |
| scripts/test_process_tape.py:281 | fixture |
| scripts/test_process_tape.py:301 | fixture |
| scripts/test_process_tape.py:302 | fixture |
| scripts/test_process_tape.py:309 | fixture |
| scripts/test_process_tape.py:314 | fixture |
| scripts/test_process_tape.py:315 | fixture |
| scripts/test_process_tape.py:331 | fixture |
| scripts/test_process_tape.py:355 | fixture |
| scripts/test_process_tape.py:356 | fixture |
| scripts/test_process_tape.py:372 | fixture |
| scripts/test_process_tape.py:432 | fixture |
| scripts/test_process_tape.py:436 | fixture |
| scripts/test_process_tape.py:553 | fixture |
| scripts/test_process_tape.py:555 | 00000000-0000-4000-8000-000000000001 |
| scripts/test_process_tape.py:559 | fixture |
| scripts/test_process_tape.py:562 | FIXTURE |
| scripts/test_process_tape.py:599 | fixture |
| scripts/test_process_tape.py:602 | fixture |
| scripts/test_process_tape.py:704 | fixture |
| scripts/test_profile_lineage_activation.py:13 | fixture |
| scripts/test_profile_lineage_activation.py:16 | fixture |
| scripts/test_profile_lineage_activation.py:71 | fixture |
| scripts/test_proof_preflight.py:12 | fixture |
| scripts/test_proof_preflight.py:25 | fixture |
| scripts/test_proof_preflight.py:27 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_proof_preflight.py:28 | 22222222-2222-2222-2222-222222222222 |
| scripts/test_proof_preflight.py:30 | SemanticModel |
| scripts/test_proof_preflight.py:99 | 33333333-3333-3333-3333-333333333333 |
| scripts/test_proof_preflight.py:117 | 33333333-3333-3333-3333-333333333333 |
| scripts/test_proof_preflight.py:195 | 33333333-3333-3333-3333-333333333333 |
| scripts/test_proof_preflight.py:203 | fixture, workspaces/ |
| scripts/test_proof_preflight.py:215 | workspaces/ |
| scripts/test_proposal_repairs.py:7 | fixture |
| scripts/test_proposal_repairs.py:15 | fixture |
| scripts/test_proposal_repairs.py:61 | fixture |
| scripts/test_proposal_repairs.py:81 | fixture |
| scripts/test_proposal_repairs.py:91 | fixture |
| scripts/test_proposal_repairs.py:103 | fixture |
| scripts/test_proposal_repairs.py:114 | fixture |
| scripts/test_proposal_repairs.py:121 | fixture |
| scripts/test_provider_terms.py:3 | fixture |
| scripts/test_provider_terms.py:11 | fixture |
| scripts/test_provider_terms.py:22 | fixture |
| scripts/test_provider_terms.py:29 | fixture |
| scripts/test_publication_lineage_contract.py:10 | fixture |
| scripts/test_publication_lineage_contract.py:11 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_publication_lineage_contract.py:12 | 22222222-2222-2222-2222-222222222222 |
| scripts/test_publication_lineage_contract.py:13 | 33333333-3333-3333-3333-333333333333 |
| scripts/test_publication_lineage_contract.py:23 | fixture |
| scripts/test_publication_lineage_contract.py:29 | fixture |
| scripts/test_publication_lineage_contract.py:35 | fixture |
| scripts/test_publication_lineage_contract.py:40 | fixture |
| scripts/test_publication_lineage_contract.py:51 | fixture |
| scripts/test_publication_lineage_contract.py:53 | 11111111-1111-1111-1111-111111111111, 44444444-4444-4444-4444-444444444444 |
| scripts/test_publication_lineage_contract.py:56 | fixture |
| scripts/test_publication_lineage_contract.py:61 | Lakehouse |
| scripts/test_question_account.py:43 | workspace/ |
| scripts/test_question_account.py:195 | fixture |
| scripts/test_question_account.py:198 | fixture |
| scripts/test_question_first_probes.py:3 | fixture |
| scripts/test_question_first_probes.py:7 | fixture |
| scripts/test_question_first_probes.py:8 | fixture |
| scripts/test_question_first_probes.py:9 | fixture |
| scripts/test_question_intake.py:11 | fixture |
| scripts/test_question_intake.py:168 | fixture |
| scripts/test_question_intake.py:450 | workspace/ |
| scripts/test_question_kind_budgets.py:9 | fixture |
| scripts/test_question_kind_budgets.py:44 | fixture |
| scripts/test_question_kind_budgets.py:92 | fixture |
| scripts/test_question_kind_budgets.py:108 | fixture |
| scripts/test_question_kind_budgets.py:109 | fixture |
| scripts/test_question_kind_budgets.py:141 | fixture |
| scripts/test_question_kind_budgets.py:144 | fixture |
| scripts/test_question_kind_budgets.py:165 | fixture |
| scripts/test_question_kind_budgets.py:168 | fixture |
| scripts/test_read_budget.py:138 | fixture |
| scripts/test_read_budget.py:144 | fixture |
| scripts/test_read_budget.py:166 | fixture |
| scripts/test_read_budget.py:168 | fixture |
| scripts/test_read_budget.py:170 | fixture |
| scripts/test_read_budget.py:248 | fixture |
| scripts/test_read_budget.py:252 | fixture |
| scripts/test_read_cell_address.py:4 | fixture |
| scripts/test_read_cell_address.py:8 | fixture |
| scripts/test_read_cell_address.py:9 | fixture |
| scripts/test_read_cell_address.py:10 | fixture |
| scripts/test_read_cell_address.py:11 | fixture |
| scripts/test_read_onelake_commit.py:44 | 00000000-0000-0000-0000-000000000001, 00000000-0000-0000-0000-000000000002 |
| scripts/test_read_onelake_commit.py:45 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_read_onelake_commit.py:52 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_read_onelake_commit.py:53 | 00000000-0000-0000-0000-000000000002, lakehouse |
| scripts/test_read_onelake_commit.py:62 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_read_onelake_commit.py:63 | 00000000-0000-0000-0000-000000000002, lakehouse |
| scripts/test_read_redundancy.py:5 | fixture |
| scripts/test_read_redundancy.py:10 | fixture |
| scripts/test_read_redundancy.py:26 | fixture |
| scripts/test_read_redundancy.py:49 | fixture |
| scripts/test_read_redundancy.py:62 | fixture |
| scripts/test_read_redundancy.py:76 | fixture |
| scripts/test_read_redundancy.py:89 | fixture |
| scripts/test_read_redundancy.py:161 | fixture |
| scripts/test_reader_execution.py:17 | fixture |
| scripts/test_reader_execution.py:18 | fixture |
| scripts/test_reader_execution.py:19 | fixture |
| scripts/test_reader_execution.py:21 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_reader_execution.py:22 | 22222222-2222-2222-2222-222222222222 |
| scripts/test_reader_execution.py:23 | 33333333-3333-3333-3333-333333333333 |
| scripts/test_reader_execution.py:24 | 44444444-4444-4444-4444-444444444444 |
| scripts/test_reader_execution.py:43 | fixture |
| scripts/test_reader_execution.py:46 | fixture |
| scripts/test_reader_execution.py:55 | fixture |
| scripts/test_reader_execution.py:109 | fixture |
| scripts/test_reader_execution.py:134 | 33333333-3333-3333-3333-333333333333, 44444444-4444-4444-4444-444444444444 |
| scripts/test_reader_execution.py:136 | fixture |
| scripts/test_reader_execution.py:149 | fixture |
| scripts/test_reader_execution.py:155 | fixture |
| scripts/test_reader_execution.py:162 | fixture |
| scripts/test_reader_execution.py:190 | fixture |
| scripts/test_reader_execution.py:202 | fixture |
| scripts/test_reader_execution.py:218 | fixture |
| scripts/test_reader_execution.py:241 | fixture |
| scripts/test_reader_execution.py:249 | fixture |
| scripts/test_reader_execution.py:250 | fixture |
| scripts/test_reader_runtime.py:8 | fixture |
| scripts/test_reader_runtime.py:11 | Fixture, fixture |
| scripts/test_reader_runtime.py:72 | fixture |
| scripts/test_reader_runtime.py:82 | fixture |
| scripts/test_reader_runtime.py:88 | fixture |
| scripts/test_reader_runtime.py:89 | Fixture |
| scripts/test_reader_runtime.py:96 | fixture |
| scripts/test_reader_runtime.py:97 | Fixture |
| scripts/test_record_aggregate.py:8 | fixture |
| scripts/test_record_aggregate.py:19 | fixture |
| scripts/test_record_arrival_history.py:24 | warehouse |
| scripts/test_record_discovery.py:7 | fixture |
| scripts/test_record_discovery.py:17 | fixture |
| scripts/test_refresh_comparison.py:148 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_refresh_comparison.py:149 | 00000000-0000-0000-0000-000000000002 |
| scripts/test_refresh_comparison.py:188 | 00000000-0000-0000-0000-000000000003 |
| scripts/test_report_cells.py:8 | fixture |
| scripts/test_report_cells.py:14 | fixture |
| scripts/test_report_cells.py:25 | fixture |
| scripts/test_report_cells.py:26 | fixture |
| scripts/test_report_definition_evidence.py:17 | 22222222-2222-4222-8222-222222222222 |
| scripts/test_report_definition_evidence.py:19 | SemanticModel |
| scripts/test_report_definition_evidence.py:21 | 22222222-2222-4222-8222-222222222222, semanticmodel |
| scripts/test_report_definition_evidence.py:24 | SemanticModel |
| scripts/test_report_definition_evidence.py:58 | 22222222-2222-4222-8222-222222222222, semanticmodel |
| scripts/test_report_drillthrough_context.py:9 | fixture |
| scripts/test_report_drillthrough_context.py:23 | fixture |
| scripts/test_report_drillthrough_context.py:27 | fixture |
| scripts/test_report_drillthrough_context.py:33 | fixture |
| scripts/test_report_drillthrough_context.py:36 | fixture |
| scripts/test_report_drillthrough_context.py:38 | fixture |
| scripts/test_report_drillthrough_context.py:39 | fixture |
| scripts/test_report_drillthrough_context.py:43 | fixture |
| scripts/test_report_layout.py:11 | 11111111-1111-1111-1111-111111111111, 22222222-2222-2222-2222-222222222222 |
| scripts/test_report_layout.py:36 | 11111111-1111-1111-1111-111111111111, 22222222-2222-2222-2222-222222222222 |
| scripts/test_report_link.py:6 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_report_link.py:7 | 22222222-2222-4222-8222-222222222222 |
| scripts/test_report_list_worker.py:8 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_report_list_worker.py:9 | 22222222-2222-4222-8222-222222222222 |
| scripts/test_report_list_worker.py:10 | 33333333-3333-4333-8333-333333333333 |
| scripts/test_report_list_worker.py:42 | database.windows.net |
| scripts/test_report_metadata.py:10 | 11111111-1111-4111-8111-111111111111 |
| scripts/test_report_metadata.py:11 | 22222222-2222-4222-8222-222222222222 |
| scripts/test_report_metadata.py:12 | 33333333-3333-4333-8333-333333333333 |
| scripts/test_report_metadata.py:15 | 44444444-4444-4444-8444-444444444444 |
| scripts/test_report_metadata.py:18 | SemanticModel |
| scripts/test_report_metadata.py:53 | 55555555-5555-4555-8555-555555555555 |
| scripts/test_report_scoped_cells.py:8 | fixture |
| scripts/test_report_scoped_cells.py:13 | fixture |
| scripts/test_report_scoped_cells.py:14 | fixture |
| scripts/test_report_scoped_cells.py:15 | fixture |
| scripts/test_report_scoped_cells.py:16 | fixture |
| scripts/test_report_slicer_context.py:11 | fixture |
| scripts/test_report_slicer_context.py:22 | fixture |
| scripts/test_report_slicer_context.py:28 | fixture |
| scripts/test_report_slicer_context.py:34 | fixture |
| scripts/test_report_slicer_context.py:36 | fixture |
| scripts/test_report_slicer_context.py:39 | fixture |
| scripts/test_report_slicer_context.py:44 | fixture |
| scripts/test_report_slicer_context.py:46 | fixture |
| scripts/test_reported_figure_punctuation.py:5 | fixture |
| scripts/test_reported_figure_punctuation.py:12 | fixture |
| scripts/test_reproduction_composition.py:42 | warehouse |
| scripts/test_reproduction_composition.py:44 | warehouse |
| scripts/test_reproduction_composition.py:45 | warehouse |
| scripts/test_reproduction_composition.py:91 | 3484a2bc-98c5-4cef-be5c-a6215484075e, workspace/ |
| scripts/test_resumable_archive.py:16 | blob.core.windows.net, fixture |
| scripts/test_resumable_archive.py:126 | blob.core.windows.net |
| scripts/test_resumable_archive.py:131 | 12345678-1234-1234-1234-123456789012 |
| scripts/test_resumable_archive.py:134 | fixture |
| scripts/test_retained_endpoints.py:13 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_retained_endpoints.py:14 | 00000000-0000-0000-0000-000000000002, lakehouse |
| scripts/test_retained_endpoints.py:15 | 00000000-0000-0000-0000-000000000003 |
| scripts/test_retained_endpoints.py:18 | lakehouse |
| scripts/test_retained_endpoints.py:19 | Lakehouse |
| scripts/test_retained_endpoints.py:29 | Lakehouse, lakehouse |
| scripts/test_retained_endpoints.py:51 | lakehouse |
| scripts/test_retained_endpoints.py:77 | lakehouse |
| scripts/test_retained_graph_continuation.py:18 | SemanticModel |
| scripts/test_retained_graph_continuation.py:22 | Lakehouse |
| scripts/test_retained_graph_continuation.py:23 | SemanticModel |
| scripts/test_retained_graph_versions.py:14 | workspace/ |
| scripts/test_retention.py:1 | fixture |
| scripts/test_retention.py:51 | fixture |
| scripts/test_retention.py:64 | fixture |
| scripts/test_retention.py:74 | fixture |
| scripts/test_retention.py:75 | fixture |
| scripts/test_reviewed_slicer_context.py:20 | 22222222-2222-4222-8222-222222222222, workspace/ |
| scripts/test_reviewed_source_scopes.py:12 | fixture |
| scripts/test_reviewed_source_scopes.py:97 | fixture |
| scripts/test_reviewed_source_scopes.py:211 | fixture |
| scripts/test_reviewed_source_scopes.py:214 | fixture |
| scripts/test_round22_scored_seal.py:38 | fixture |
| scripts/test_round23_fixture_control.py:5 | fixture |
| scripts/test_round23_fixture_control.py:6 | fixture |
| scripts/test_round23_intake_queries.py:164 | workspace/ |
| scripts/test_round23_live_facts.py:15 | fixture |
| scripts/test_round23_live_facts.py:27 | fixture |
| scripts/test_round23_live_facts.py:32 | fixture |
| scripts/test_round23_live_facts.py:41 | fixture |
| scripts/test_round23_live_facts.py:44 | fixture |
| scripts/test_round23_live_facts.py:55 | fixture |
| scripts/test_round23_live_facts.py:66 | fixture |
| scripts/test_round23_native_catalog.py:14 | workspace/ |
| scripts/test_round23_native_catalog.py:15 | SemanticModel |
| scripts/test_round23_native_catalog.py:29 | workspace/ |
| scripts/test_round23_native_catalog.py:49 | workspace/ |
| scripts/test_round23_native_catalog.py:51 | SemanticModel |
| scripts/test_round23_native_catalog.py:53 | semanticmodel |
| scripts/test_round23_native_catalog.py:55 | fixture |
| scripts/test_round23_native_catalog.py:58 | workspace/ |
| scripts/test_round23_native_catalog.py:59 | fixture |
| scripts/test_round23_native_catalog.py:62 | workspace/ |
| scripts/test_round23_native_catalog.py:76 | workspace/ |
| scripts/test_round23_native_catalog.py:77 | SemanticModel |
| scripts/test_round23_native_catalog.py:103 | fixture |
| scripts/test_round23_native_catalog.py:113 | Fixture, warehouse |
| scripts/test_round23_native_catalog.py:123 | warehouse |
| scripts/test_round23_native_catalog.py:129 | workspace/ |
| scripts/test_round23_native_catalog.py:130 | SemanticModel |
| scripts/test_round23_native_catalog.py:134 | workspace/, workspaces/ |
| scripts/test_round23_native_catalog.py:164 | lakehouse, workspace/ |
| scripts/test_round23_native_catalog.py:166 | Lakehouse |
| scripts/test_round23_native_catalog.py:167 | Lakehouse |
| scripts/test_round23_native_catalog.py:168 | workspace/ |
| scripts/test_round23_native_catalog.py:169 | lakehouse |
| scripts/test_round23_native_catalog.py:190 | lakehouse |
| scripts/test_round23_native_catalog.py:191 | lakehouse |
| scripts/test_round23_native_catalog.py:230 | Lakehouse |
| scripts/test_round23_native_catalog.py:238 | semantic=model, workspace/ |
| scripts/test_round23_native_catalog.py:242 | SemanticModel |
| scripts/test_round23_native_catalog.py:257 | workspace/ |
| scripts/test_round23_native_catalog.py:258 | SemanticModel |
| scripts/test_round23_platform.py:72 | database.windows.net |
| scripts/test_round23_reasoning.py:1 | fixture |
| scripts/test_round23_runtime_reads.py:11 | fixture |
| scripts/test_round23_runtime_reads.py:13 | fixture |
| scripts/test_round23_runtime_reads.py:16 | fixture |
| scripts/test_round23_runtime_reads.py:24 | 11111111-1111-1111-1111-111111111111, 22222222-2222-2222-2222-222222222222 |
| scripts/test_round23_triage_tools.py:31 | fixture, warehouse |
| scripts/test_round23_triage_tools.py:144 | fixture |
| scripts/test_round23_triage_tools.py:153 | fixture |
| scripts/test_round23_triage_tools.py:162 | fixture |
| scripts/test_round24_backtrack_routes.py:14 | fixture |
| scripts/test_round24_backtrack_routes.py:18 | fixture |
| scripts/test_round24_backtrack_routes.py:22 | warehouse |
| scripts/test_round24_control_errors.py:7 | fixture |
| scripts/test_round24_control_errors.py:11 | fixture |
| scripts/test_round24_control_errors.py:18 | fixture |
| scripts/test_round24_control_errors.py:21 | fixture |
| scripts/test_round24_control_errors.py:31 | fixture |
| scripts/test_round24_copy_bindings.py:6 | workspace/ |
| scripts/test_round24_copy_bindings.py:20 | fixture |
| scripts/test_round24_copy_bindings.py:21 | Lakehouse |
| scripts/test_round24_copy_bindings.py:44 | Lakehouse, lakehouse, workspace/ |
| scripts/test_round24_copy_bindings.py:45 | lakehouse |
| scripts/test_round24_legacy_native.py:2 | fixture |
| scripts/test_round24_legacy_native.py:6 | fixture |
| scripts/test_round24_legacy_native.py:12 | fixture |
| scripts/test_round24_legacy_native.py:16 | fixture |
| scripts/test_round24_paths.py:11 | workspace/ |
| scripts/test_round24_paths.py:12 | SemanticModel |
| scripts/test_round24_paths.py:27 | SemanticModel |
| scripts/test_round24_retained_schema.py:3 | fixture |
| scripts/test_round24_retained_schema.py:6 | fixture |
| scripts/test_round24_retained_schema.py:7 | fixture |
| scripts/test_round24_retained_schema.py:21 | fixture |
| scripts/test_round24_retained_schema.py:23 | fixture |
| scripts/test_round24_retained_schema.py:29 | fixture |
| scripts/test_round24_retained_schema.py:31 | fixture |
| scripts/test_round24_script_procedures.py:18 | warehouse |
| scripts/test_round24_script_procedures.py:29 | Warehouse |
| scripts/test_round24_smoke_configuration.py:6 | fixture |
| scripts/test_round25_cohort_report.py:28 | fixture |
| scripts/test_round25_cohort_report.py:29 | fixture |
| scripts/test_round25_cohort_report.py:38 | fixture |
| scripts/test_round25_cohort_report.py:39 | fixture |
| scripts/test_round25_cohort_report.py:40 | fixture |
| scripts/test_round25_cohort_report.py:48 | fixture |
| scripts/test_round25_independent_review.py:52 | fixture |
| scripts/test_round25_quality.py:56 | fixture |
| scripts/test_round25_quality.py:61 | fixture |
| scripts/test_round25_quality.py:62 | fixture |
| scripts/test_round25_quality.py:241 | fixture |
| scripts/test_round25_quality.py:337 | fixture |
| scripts/test_round25_quality.py:338 | fixture |
| scripts/test_round25_quality.py:339 | fixture |
| scripts/test_round25_quality.py:340 | fixture |
| scripts/test_round25_quality.py:341 | fixture |
| scripts/test_round26_bedrock_setup.py:37 | kv-dia- |
| scripts/test_round26_configured_ai_job.py:14 | fixture |
| scripts/test_round26_configured_ai_job.py:29 | fixture |
| scripts/test_round26_configured_ai_job.py:58 | fixture |
| scripts/test_round26_configured_ai_job.py:61 | fixture |
| scripts/test_round26_intake_candidates.py:25 | warehouse |
| scripts/test_round26_intake_fallbacks.py:47 | fixture, warehouse |
| scripts/test_round26_job_pagination.py:7 | aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa, bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb |
| scripts/test_round26_job_pagination.py:8 | workspaces/ |
| scripts/test_round26_job_pagination.py:15 | fixture |
| scripts/test_round26_job_pagination.py:41 | workspaces/ |
| scripts/test_round26_operational_fastpath.py:31 | fixture |
| scripts/test_round26_scope_candidates.py:13 | fixture |
| scripts/test_round26_scope_candidates.py:17 | fixture |
| scripts/test_round26_scope_candidates.py:24 | fixture |
| scripts/test_round26_scope_candidates.py:34 | fixture |
| scripts/test_round26_scope_candidates.py:36 | SemanticModel |
| scripts/test_round26_stale_setting.py:16 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_round26_stale_setting.py:17 | 22222222-2222-2222-2222-222222222222 |
| scripts/test_round26_step_costs.py:51 | fixture |
| scripts/test_round26_step_costs.py:52 | fixture |
| scripts/test_round27_analysis_projection.py:15 | fixture |
| scripts/test_round27_analysis_projection.py:22 | fixture |
| scripts/test_round27_analysis_projection.py:30 | fixture |
| scripts/test_round27_analysis_projection.py:34 | fixture |
| scripts/test_round27_analysis_projection.py:41 | fixture |
| scripts/test_round27_analysis_projection.py:44 | fixture |
| scripts/test_round27_analysis_projection.py:47 | fixture |
| scripts/test_round27_analysis_projection.py:63 | fixture |
| scripts/test_round27_analysis_projection.py:66 | fixture |
| scripts/test_round27_analysis_projection.py:69 | fixture |
| scripts/test_round27_analysis_projection.py:72 | fixture |
| scripts/test_round27_analysis_projection.py:75 | fixture |
| scripts/test_round27_analysis_projection.py:79 | fixture |
| scripts/test_round27_analysis_projection.py:88 | fixture |
| scripts/test_round27_analysis_projection.py:92 | fixture |
| scripts/test_round27_candidate_native_pruning.py:5 | fixture |
| scripts/test_round27_candidate_native_pruning.py:10 | fixture |
| scripts/test_round27_consistency_feedback.py:9 | fixture |
| scripts/test_round27_consistency_feedback.py:16 | fixture |
| scripts/test_round27_consistency_feedback.py:19 | fixture |
| scripts/test_round27_consistency_feedback.py:26 | fixture |
| scripts/test_round27_consistency_feedback.py:29 | fixture |
| scripts/test_round27_consistency_feedback.py:35 | fixture |
| scripts/test_round27_consistency_feedback.py:38 | fixture |
| scripts/test_round27_consistency_feedback.py:43 | fixture |
| scripts/test_round27_consistency_feedback.py:46 | fixture |
| scripts/test_round27_consistency_feedback.py:49 | fixture |
| scripts/test_round27_dev_backtrack_fixes.py:57 | 12345678-1234-1234-1234-123456789012 |
| scripts/test_round27_native_table_reference.py:58 | Warehouse |
| scripts/test_round27_scope_verdict.py:6 | fixture |
| scripts/test_round27_scope_verdict.py:8 | fixture |
| scripts/test_round27_scope_verdict.py:21 | fixture |
| scripts/test_round27_scope_verdict.py:28 | fixture |
| scripts/test_round_four_acceptance.py:8 | 00000000-0000-4000-8000-000000000001 |
| scripts/test_round_four_acceptance.py:14 | 00000000-0000-4000-8000-000000000001, fixture |
| scripts/test_round_four_acceptance.py:19 | fixture |
| scripts/test_round_four_acceptance.py:20 | fixture |
| scripts/test_round_four_acceptance.py:35 | fixture |
| scripts/test_round_four_acceptance.py:78 | fixture |
| scripts/test_round_thirteen_questionnaire_coverage.py:6 | fixture |
| scripts/test_round_thirteen_questionnaire_coverage.py:11 | fixture |
| scripts/test_round_thirteen_questionnaire_coverage.py:15 | warehouse |
| scripts/test_round_thirteen_questionnaire_coverage.py:28 | warehouse |
| scripts/test_round_thirteen_questionnaire_coverage.py:34 | Warehouse |
| scripts/test_round_thirteen_questionnaire_coverage.py:37 | Warehouse |
| scripts/test_round_thirteen_questionnaire_coverage.py:38 | Warehouse |
| scripts/test_round_thirteen_questionnaire_coverage.py:42 | warehouse |
| scripts/test_round_thirteen_questionnaire_coverage.py:61 | warehouse |
| scripts/test_round_thirteen_questionnaire_coverage.py:62 | warehouse |
| scripts/test_round_thirteen_questionnaire_coverage.py:73 | fixture |
| scripts/test_round_thirteen_questionnaire_coverage.py:84 | warehouse |
| scripts/test_round_thirteen_questionnaire_coverage.py:85 | fixture |
| scripts/test_round_thirteen_questionnaire_coverage.py:86 | warehouse |
| scripts/test_round_twenty_state.py:178 | blob.core.windows.net |
| scripts/test_round_twenty_state.py:181 | 11111111-1111-1111-1111-111111111111, subscriptions/ |
| scripts/test_route_readiness.py:29 | fixture |
| scripts/test_routing_delivery_rehearsal.py:8 | fixture |
| scripts/test_routing_delivery_rehearsal.py:15 | fixture |
| scripts/test_routing_delivery_rehearsal.py:75 | Fixture |
| scripts/test_routing_destination.py:5 | fixture |
| scripts/test_routing_destination.py:13 | fixture |
| scripts/test_routing_destination.py:19 | fixture |
| scripts/test_routing_destination.py:33 | fixture |
| scripts/test_routing_destination.py:54 | fixture |
| scripts/test_routing_drafts.py:20 | Fixture |
| scripts/test_routing_drafts.py:27 | Fixture |
| scripts/test_routing_review.py:7 | fixture |
| scripts/test_routing_review.py:16 | fixture |
| scripts/test_routing_review.py:32 | Fixture |
| scripts/test_run_capture_encoding.py:11 | fixture |
| scripts/test_run_context_pin.py:25 | fixture |
| scripts/test_run_context_pin.py:28 | fixture |
| scripts/test_run_context_pin.py:29 | fixture |
| scripts/test_run_context_pin.py:47 | fixture |
| scripts/test_run_context_pin.py:48 | fixture |
| scripts/test_run_context_pin.py:50 | fixture |
| scripts/test_run_context_pin.py:51 | fixture |
| scripts/test_run_context_pin.py:53 | fixture |
| scripts/test_run_context_pin.py:54 | fixture |
| scripts/test_run_context_pin.py:62 | fixture |
| scripts/test_run_database_audits.py:18 | fixture |
| scripts/test_run_database_audits.py:21 | fixture |
| scripts/test_run_database_audits.py:51 | fixture |
| scripts/test_run_history.py:54 | fixture |
| scripts/test_run_history.py:55 | fixture |
| scripts/test_run_timing.py:13 | fixture |
| scripts/test_runner_graph_schedule.py:23 | fixture |
| scripts/test_runner_graph_schedule.py:41 | job-dia- |
| scripts/test_runner_input_policy.py:7 | blob.core.windows.net |
| scripts/test_runner_prepare.py:9 | 11111111-1111-1111-1111-111111111111, subscriptions/ |
| scripts/test_runner_prepare.py:13 | blob.core.windows.net |
| scripts/test_runtime_facts_microsoft.py:16 | 149f8d99-1c66-4a0a-9624-759be002bb60, 3484a2bc-98c5-4cef-be5c-a6215484075e |
| scripts/test_runtime_facts_microsoft.py:24 | warehouse |
| scripts/test_runtime_facts_microsoft.py:29 | Warehouse |
| scripts/test_runtime_facts_microsoft.py:51 | workspaces/ |
| scripts/test_runtime_facts_microsoft.py:62 | e82f690b-6865-48b5-a38c-9a116cd9c132 |
| scripts/test_runtime_facts_microsoft.py:64 | 8274a34e-89ba-4db6-94a3-ca06a48c7c4a |
| scripts/test_runtime_facts_microsoft.py:114 | workspaces/ |
| scripts/test_runtime_facts_microsoft.py:165 | WAREHOUSE |
| scripts/test_runtime_governance.py:8 | fixture |
| scripts/test_runtime_governance.py:17 | fixture |
| scripts/test_runtime_governance.py:26 | fixture |
| scripts/test_runtime_governance.py:55 | fixture |
| scripts/test_runtime_governance.py:66 | fixture |
| scripts/test_runtime_governance.py:84 | fixture |
| scripts/test_runtime_governance.py:92 | fixture |
| scripts/test_runtime_governance.py:122 | fixture |
| scripts/test_runtime_governance.py:164 | fixture |
| scripts/test_runtime_governance.py:171 | fixture |
| scripts/test_runtime_governance.py:176 | fixture |
| scripts/test_runtime_governance.py:201 | fixture |
| scripts/test_runtime_governance.py:278 | fixture |
| scripts/test_runtime_transport.py:8 | fixture |
| scripts/test_runtime_transport.py:45 | fixture |
| scripts/test_runtime_transport.py:52 | fixture |
| scripts/test_scanner_guardrails.py:17 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_scanner_guardrails.py:18 | 22222222-2222-2222-2222-222222222222 |
| scripts/test_scanner_guardrails.py:19 | 33333333-3333-3333-3333-333333333333 |
| scripts/test_scanner_guardrails.py:31 | dia-scanner |
| scripts/test_scanner_guardrails.py:40 | dia-scanner |
| scripts/test_scanner_guardrails.py:43 | dia-scanner |
| scripts/test_scanner_guardrails.py:44 | dia-scanner |
| scripts/test_scanner_guardrails.py:50 | dia-scanner |
| scripts/test_scanner_guardrails.py:58 | workspaces/ |
| scripts/test_scanner_guardrails.py:59 | workspaces/ |
| scripts/test_scanner_guardrails.py:60 | semanticModel, workspaces/ |
| scripts/test_scanner_guardrails.py:62 | dia-scanner |
| scripts/test_scanner_guardrails.py:63 | dia-scanner |
| scripts/test_scanner_guardrails.py:66 | workspaces/ |
| scripts/test_scanner_guardrails.py:67 | workspaces/ |
| scripts/test_scanner_guardrails.py:68 | workspaces/ |
| scripts/test_scanner_guardrails.py:69 | workspaces/ |
| scripts/test_scanner_guardrails.py:70 | workspaces/ |
| scripts/test_scanner_guardrails.py:71 | workspaces/ |
| scripts/test_scanner_guardrails.py:72 | workspaces/ |
| scripts/test_scanner_guardrails.py:75 | dia-scanner |
| scripts/test_scanner_guardrails.py:76 | workspaces/ |
| scripts/test_scanner_guardrails.py:78 | dia-scanner, workspaces/ |
| scripts/test_scanner_guardrails.py:86 | dia-scanner |
| scripts/test_scanner_guardrails.py:90 | dia-scanner |
| scripts/test_scanner_guardrails.py:91 | dia-scanner |
| scripts/test_scanner_guardrails.py:92 | dia-scanner |
| scripts/test_scanner_guardrails.py:93 | dia-scanner |
| scripts/test_scanner_guardrails.py:94 | dia-scanner |
| scripts/test_scanner_guardrails.py:97 | workspaces/ |
| scripts/test_scanner_guardrails.py:99 | dia-scanner |
| scripts/test_scanner_guardrails.py:101 | dia-scanner |
| scripts/test_scanner_guardrails.py:110 | database.windows.net |
| scripts/test_scanner_guardrails.py:116 | workspaces/ |
| scripts/test_scanner_guardrails.py:118 | dia-scanner |
| scripts/test_scanner_guardrails.py:119 | workspaces/ |
| scripts/test_scanner_guardrails.py:120 | dia-scanner |
| scripts/test_scanner_http.py:34 | workspaces/ |
| scripts/test_scanner_http.py:37 | workspaces/ |
| scripts/test_scanner_http.py:41 | workspaces/ |
| scripts/test_scanner_http.py:55 | workspaces/ |
| scripts/test_scanner_http.py:56 | workspaces/ |
| scripts/test_scanner_http.py:71 | workspaces/ |
| scripts/test_scanner_http.py:77 | workspaces/ |
| scripts/test_scanner_http.py:81 | workspaces/ |
| scripts/test_scanner_http.py:86 | workspaces/ |
| scripts/test_scoped_inventory_only.py:52 | warehouse, workspace/ |
| scripts/test_scoped_inventory_only.py:59 | warehouse |
| scripts/test_screenshot_intake.py:11 | fixture |
| scripts/test_screenshot_intake.py:12 | fixture |
| scripts/test_screenshot_intake.py:23 | fixture |
| scripts/test_screenshot_intake.py:115 | fixture |
| scripts/test_screenshot_intake.py:126 | fixture |
| scripts/test_screenshot_intake.py:184 | workspace/ |
| scripts/test_screenshot_intake.py:200 | fixture |
| scripts/test_selection_descriptor.py:9 | fixture |
| scripts/test_selection_descriptor.py:29 | warehouse |
| scripts/test_selection_descriptor.py:30 | warehouse |
| scripts/test_selection_descriptor.py:31 | warehouse |
| scripts/test_selection_descriptor.py:34 | warehouse |
| scripts/test_selection_descriptor.py:44 | warehouse |
| scripts/test_selection_descriptor.py:45 | warehouse |
| scripts/test_selection_descriptor.py:50 | warehouse |
| scripts/test_selection_descriptor.py:53 | warehouse |
| scripts/test_selection_descriptor.py:55 | warehouse |
| scripts/test_selection_descriptor.py:63 | warehouse |
| scripts/test_selection_descriptor.py:64 | warehouse |
| scripts/test_selection_descriptor.py:66 | warehouse |
| scripts/test_selection_descriptor.py:76 | warehouse |
| scripts/test_selection_descriptor.py:86 | warehouse |
| scripts/test_selection_descriptor.py:98 | fixture |
| scripts/test_selection_descriptor.py:99 | fixture |
| scripts/test_selection_descriptor.py:100 | fixture |
| scripts/test_selection_descriptor.py:101 | fixture |
| scripts/test_selection_descriptor.py:102 | fixture |
| scripts/test_selection_descriptor.py:103 | fixture |
| scripts/test_selection_descriptor.py:104 | fixture |
| scripts/test_selection_descriptor.py:105 | fixture |
| scripts/test_selection_descriptor.py:114 | warehouse |
| scripts/test_selection_descriptor.py:119 | warehouse |
| scripts/test_selection_descriptor.py:142 | warehouse |
| scripts/test_semantic_snapshot.py:7 | fixture |
| scripts/test_semantic_snapshot.py:15 | fixture |
| scripts/test_semantic_snapshot.py:21 | fixture |
| scripts/test_semantic_snapshot.py:25 | fixture |
| scripts/test_semantics_control.py:16 | fixture |
| scripts/test_semantics_control.py:17 | fixture |
| scripts/test_semantics_control.py:64 | fixture |
| scripts/test_semantics_control.py:67 | fixture |
| scripts/test_semantics_control.py:68 | fixture |
| scripts/test_semantics_control.py:69 | fixture |
| scripts/test_semantics_control.py:97 | fixture |
| scripts/test_semantics_control.py:98 | fixture |
| scripts/test_semantics_control.py:99 | fixture |
| scripts/test_semantics_control.py:101 | fixture |
| scripts/test_session_replay.py:13 | fixture |
| scripts/test_session_replay.py:27 | fixture |
| scripts/test_session_replay.py:32 | fixture |
| scripts/test_session_replay.py:73 | fixture |
| scripts/test_session_replay.py:78 | fixture |
| scripts/test_session_replay.py:153 | fixture |
| scripts/test_shared_application_capture.py:11 | fixture |
| scripts/test_shared_application_capture.py:20 | fixture |
| scripts/test_shared_application_capture.py:72 | fixture |
| scripts/test_shared_application_capture.py:73 | fixture |
| scripts/test_shared_application_capture.py:74 | fixture |
| scripts/test_shared_application_capture.py:84 | fixture |
| scripts/test_shared_application_capture.py:85 | fixture |
| scripts/test_shared_application_capture.py:86 | fixture |
| scripts/test_shared_application_capture.py:88 | fixture |
| scripts/test_shared_application_capture.py:92 | fixture |
| scripts/test_shared_application_capture.py:94 | fixture |
| scripts/test_shared_application_capture.py:95 | fixture |
| scripts/test_shared_catalog_capture.py:19 | Fixture, fixture |
| scripts/test_shared_catalog_capture.py:42 | fixture |
| scripts/test_shared_catalog_capture.py:44 | fixture |
| scripts/test_shared_catalog_capture.py:54 | fixture |
| scripts/test_shared_catalog_capture.py:62 | fixture |
| scripts/test_shared_screenshots.py:19 | fixture |
| scripts/test_shared_screenshots.py:32 | fixture |
| scripts/test_shared_screenshots.py:83 | blob.core.windows.net |
| scripts/test_shared_screenshots.py:84 | 12345678-1234-1234-1234-123456789012 |
| scripts/test_shared_spend_replay_ordering.py:16 | fixture |
| scripts/test_shared_spend_replay_ordering.py:36 | fixture |
| scripts/test_shared_usage_replay.py:83 | fixture |
| scripts/test_silver_publication.py:8 | fixture |
| scripts/test_silver_publication.py:17 | fixture |
| scripts/test_silver_publication.py:21 | fixture |
| scripts/test_silver_publication.py:30 | fixture |
| scripts/test_silver_publication.py:35 | fixture |
| scripts/test_silver_snapshot_input.py:18 | fixture |
| scripts/test_silver_snapshot_input.py:19 | fixture |
| scripts/test_silver_snapshot_input.py:25 | fixture |
| scripts/test_silver_snapshot_input.py:32 | fixture |
| scripts/test_silver_snapshot_input.py:39 | fixture |
| scripts/test_slim_recording.py:15 | blob.core.windows.net |
| scripts/test_slim_recording.py:16 | 11111111-1111-1111-1111-111111111111 |
| scripts/test_slim_recording.py:17 | 22222222-2222-2222-2222-222222222222, 33333333-3333-3333-3333-333333333333 |
| scripts/test_smart_intake.py:7 | fixture |
| scripts/test_smart_intake.py:8 | fixture |
| scripts/test_smart_intake.py:13 | fixture |
| scripts/test_smart_intake.py:33 | fixture |
| scripts/test_smart_intake.py:44 | fixture |
| scripts/test_smart_intake.py:47 | fixture |
| scripts/test_smart_intake.py:60 | Warehouse, fixture |
| scripts/test_smart_intake.py:62 | Warehouse |
| scripts/test_smart_intake.py:118 | fixture |
| scripts/test_smart_intake.py:129 | fixture |
| scripts/test_smart_intake.py:144 | fixture |
| scripts/test_smart_intake.py:158 | fixture |
| scripts/test_smart_intake.py:171 | fixture |
| scripts/test_smart_intake.py:218 | fixture |
| scripts/test_smart_intake.py:233 | fixture |
| scripts/test_smart_intake.py:252 | fixture |
| scripts/test_smart_intake.py:261 | fixture |
| scripts/test_smart_intake.py:271 | fixture |
| scripts/test_smart_intake.py:300 | fixture |
| scripts/test_smart_intake.py:312 | fixture |
| scripts/test_smart_intake.py:328 | fixture |
| scripts/test_smart_intake.py:345 | fixture |
| scripts/test_smart_intake.py:353 | fixture |
| scripts/test_smart_intake.py:364 | fixture, warehouse |
| scripts/test_smart_intake.py:366 | warehouse |
| scripts/test_smart_intake.py:375 | warehouse |
| scripts/test_smart_intake.py:379 | fixture |
| scripts/test_smart_intake.py:388 | fixture |
| scripts/test_smart_intake.py:399 | fixture |
| scripts/test_smart_intake.py:400 | fixture |
| scripts/test_smart_intake.py:402 | fixture |
| scripts/test_smart_intake.py:413 | fixture |
| scripts/test_smart_intake.py:431 | fixture |
| scripts/test_smart_intake.py:439 | fixture |
| scripts/test_smart_intake.py:441 | fixture |
| scripts/test_smart_intake.py:474 | fixture |
| scripts/test_smart_intake.py:573 | workspace/ |
| scripts/test_smart_intake.py:576 | workspace/ |
| scripts/test_smart_intake.py:579 | workspace/ |
| scripts/test_smart_intake.py:580 | workspace/ |
| scripts/test_smart_intake.py:582 | workspace/ |
| scripts/test_smart_intake.py:586 | workspace/ |
| scripts/test_smart_intake.py:588 | workspace/ |
| scripts/test_smart_intake_eval.py:21 | fixture |
| scripts/test_smart_intake_eval.py:24 | fixture |
| scripts/test_smart_intake_eval.py:45 | fixture |
| scripts/test_smoke_gold_payload.py:11 | fixture |
| scripts/test_smoke_gold_payload.py:12 | warehouse |
| scripts/test_smoke_run_bound_capture.py:17 | blob.core.windows.net |
| scripts/test_smoke_run_bound_capture.py:32 | fixture |
| scripts/test_snapshot_attestation.py:161 | database.windows.net |
| scripts/test_snapshot_provenance.py:4 | 55cdeeb3-0772-494a-8e7f-f0df4da03353 |
| scripts/test_snapshot_provenance.py:5 | f4e5f3e9-455b-4f99-9a55-408268444b8c |
| scripts/test_snapshot_upload.py:41 | lakehouse |
| scripts/test_snapshot_upload.py:46 | lakehouse |
| scripts/test_snapshot_upload.py:48 | lakehouse |
| scripts/test_source_availability.py:6 | fixture |
| scripts/test_source_availability.py:45 | fixture |
| scripts/test_source_availability.py:50 | warehouse |
| scripts/test_source_availability.py:62 | fixture |
| scripts/test_source_availability.py:70 | fixture |
| scripts/test_source_availability.py:94 | fixture |
| scripts/test_source_availability.py:99 | fixture |
| scripts/test_source_availability.py:105 | fixture |
| scripts/test_source_availability.py:117 | fixture |
| scripts/test_source_availability.py:134 | fixture |
| scripts/test_source_delivery.py:166 | Warehouse |
| scripts/test_source_diagnostics.py:13 | fixture |
| scripts/test_source_diagnostics.py:19 | fixture |
| scripts/test_streaming_verification_snapshot.py:17 | fixture |
| scripts/test_streaming_verification_snapshot.py:25 | fixture |
| scripts/test_streaming_verification_snapshot.py:29 | fixture |
| scripts/test_streaming_verification_snapshot.py:30 | fixture |
| scripts/test_streaming_verification_snapshot.py:40 | fixture |
| scripts/test_streaming_verification_snapshot.py:68 | fixture |
| scripts/test_streaming_verification_snapshot.py:69 | fixture |
| scripts/test_surface_self_report.py:15 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_synthesis_narrative.py:6 | fixture |
| scripts/test_synthesis_narrative.py:123 | fixture |
| scripts/test_synthesis_registry.py:7 | fixture |
| scripts/test_synthesis_registry.py:14 | fixture |
| scripts/test_synthesis_registry.py:24 | fixture |
| scripts/test_synthesis_registry.py:30 | fixture |
| scripts/test_synthesis_registry.py:31 | warehouse |
| scripts/test_synthesis_registry.py:37 | fixture |
| scripts/test_synthesis_spine.py:11 | fixture |
| scripts/test_synthesis_spine.py:20 | fixture |
| scripts/test_synthesis_spine.py:54 | fixture |
| scripts/test_synthesis_spine.py:69 | fixture |
| scripts/test_synthesis_spine.py:80 | fixture |
| scripts/test_synthesis_spine.py:92 | fixture |
| scripts/test_synthesis_spine.py:108 | fixture |
| scripts/test_synthesis_spine.py:116 | fixture |
| scripts/test_synthesis_spine.py:124 | fixture |
| scripts/test_synthesis_spine.py:131 | fixture |
| scripts/test_synthesis_spine.py:146 | fixture |
| scripts/test_system_of_record.py:109 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_system_of_record.py:110 | 00000000-0000-0000-0000-000000000002 |
| scripts/test_tape_trace.py:45 | fixture |
| scripts/test_target_figure_contract.py:7 | Fixture, fixture |
| scripts/test_target_figure_contract.py:67 | Fixture |
| scripts/test_ticket_clarification.py:5 | fixture |
| scripts/test_ticket_clarification.py:10 | fixture |
| scripts/test_ticket_clarification.py:17 | fixture |
| scripts/test_ticket_clarification.py:24 | warehouse |
| scripts/test_ticket_clarification.py:28 | fixture |
| scripts/test_ticket_clarification.py:35 | fixture, warehouse |
| scripts/test_ticket_clarification.py:37 | warehouse |
| scripts/test_ticket_clarification.py:40 | warehouse |
| scripts/test_ticket_clarification.py:47 | warehouse |
| scripts/test_ticket_clarification.py:50 | fixture, warehouse |
| scripts/test_ticket_clarification.py:51 | warehouse |
| scripts/test_ticket_clarification.py:57 | fixture |
| scripts/test_ticket_clarification.py:72 | fixture |
| scripts/test_ticket_clarification.py:88 | fixture |
| scripts/test_ticket_clarification.py:94 | fixture |
| scripts/test_ticket_clarification.py:101 | fixture |
| scripts/test_ticket_clarification.py:110 | fixture |
| scripts/test_ticket_clarification.py:120 | fixture |
| scripts/test_ticket_comment_clock.py:11 | fixture |
| scripts/test_ticket_comment_clock.py:16 | fixture |
| scripts/test_ticket_findings.py:5 | fixture |
| scripts/test_ticket_findings.py:10 | fixture |
| scripts/test_ticket_planner.py:14 | fixture |
| scripts/test_ticket_planner.py:19 | fixture |
| scripts/test_ticket_planner.py:75 | fixture |
| scripts/test_ticket_protocol.py:13 | fixture |
| scripts/test_ticket_protocol.py:16 | Warehouse, fixture |
| scripts/test_ticket_protocol.py:17 | Warehouse |
| scripts/test_ticket_protocol.py:53 | fixture |
| scripts/test_ticket_protocol.py:55 | fixture |
| scripts/test_ticket_question_gate.py:5 | fixture |
| scripts/test_ticket_question_gate.py:10 | fixture |
| scripts/test_ticket_question_gate.py:20 | fixture |
| scripts/test_ticket_question_gate.py:26 | fixture |
| scripts/test_ticket_question_gate.py:32 | fixture |
| scripts/test_ticket_question_gate.py:38 | fixture |
| scripts/test_ticket_question_gate.py:45 | fixture |
| scripts/test_ticket_question_gate.py:51 | fixture |
| scripts/test_ticket_question_gate.py:58 | fixture, warehouse |
| scripts/test_ticket_question_gate.py:59 | warehouse |
| scripts/test_ticket_question_gate.py:64 | fixture |
| scripts/test_ticket_question_gate.py:69 | fixture |
| scripts/test_ticket_question_gate.py:75 | fixture |
| scripts/test_ticket_question_gate.py:90 | fixture |
| scripts/test_ticket_question_gate.py:96 | fixture |
| scripts/test_ticket_question_gate.py:113 | fixture |
| scripts/test_ticket_question_gate.py:120 | fixture |
| scripts/test_ticket_question_gate.py:126 | fixture |
| scripts/test_ticket_question_gate.py:136 | fixture |
| scripts/test_ticket_question_gate.py:149 | fixture |
| scripts/test_ticket_read_stage.py:17 | fixture |
| scripts/test_ticket_request_route.py:6 | fixture |
| scripts/test_ticket_request_route.py:12 | fixture |
| scripts/test_ticket_request_route.py:28 | fixture |
| scripts/test_ticket_request_route.py:34 | fixture |
| scripts/test_ticket_request_route.py:41 | fixture |
| scripts/test_ticket_request_route.py:51 | fixture |
| scripts/test_ticket_request_route.py:62 | fixture |
| scripts/test_ticket_request_route.py:76 | fixture |
| scripts/test_ticket_request_route.py:80 | fixture |
| scripts/test_ticket_request_route.py:83 | fixture |
| scripts/test_ticket_request_route.py:87 | fixture |
| scripts/test_ticket_route.py:19 | fixture |
| scripts/test_ticket_route.py:24 | fixture |
| scripts/test_ticket_route.py:32 | fixture |
| scripts/test_ticket_route.py:35 | fixture |
| scripts/test_ticket_route.py:37 | fixture |
| scripts/test_ticket_route.py:42 | fixture |
| scripts/test_ticket_route.py:44 | fixture |
| scripts/test_ticket_route.py:49 | fixture |
| scripts/test_ticket_route.py:51 | fixture |
| scripts/test_ticket_route.py:61 | fixture |
| scripts/test_ticket_route.py:63 | fixture |
| scripts/test_ticket_route.py:66 | fixture |
| scripts/test_ticket_route.py:68 | fixture |
| scripts/test_ticket_scope_adoption.py:8 | fixture |
| scripts/test_ticket_scope_adoption.py:9 | fixture |
| scripts/test_ticket_scope_adoption.py:14 | fixture |
| scripts/test_ticket_scope_adoption.py:16 | fixture |
| scripts/test_trace_footer.py:5 | fixture |
| scripts/test_trace_footer.py:14 | fixture |
| scripts/test_transformation_approval.py:5 | fixture |
| scripts/test_transformation_approval.py:9 | fixture |
| scripts/test_transformation_service.py:6 | fixture |
| scripts/test_transformation_service.py:11 | fixture |
| scripts/test_transformation_service_tape.py:6 | fixture |
| scripts/test_transformation_service_tape.py:7 | fixture |
| scripts/test_transformation_service_tape.py:16 | fixture |
| scripts/test_transformation_service_tape.py:20 | fixture |
| scripts/test_translation_eval.py:39 | fixture |
| scripts/test_translation_filter_definition.py:4 | fixture |
| scripts/test_translation_filter_definition.py:11 | fixture |
| scripts/test_translation_filter_definition.py:12 | fixture |
| scripts/test_translation_filter_definition.py:20 | fixture |
| scripts/test_translation_filter_definition.py:33 | fixture |
| scripts/test_translation_measure.py:5 | fixture |
| scripts/test_translation_measure.py:13 | fixture |
| scripts/test_translation_measure.py:14 | fixture |
| scripts/test_translation_measure.py:27 | Warehouse |
| scripts/test_translation_measure.py:36 | Warehouse |
| scripts/test_translation_native.py:5 | fixture |
| scripts/test_translation_native.py:12 | fixture |
| scripts/test_translation_native.py:13 | fixture |
| scripts/test_translation_proposer.py:43 | fixture |
| scripts/test_typed_scope.py:9 | fixture |
| scripts/test_typed_scope.py:15 | fixture |
| scripts/test_unified_runner.py:13 | fixture |
| scripts/test_unified_runner.py:241 | database.windows.net |
| scripts/test_unified_runner.py:271 | 11111111-1111-1111-1111-111111111111, subscriptions/ |
| scripts/test_unified_runner.py:296 | 11111111-1111-1111-1111-111111111111, job-dia-, subscriptions/ |
| scripts/test_unified_runner.py:317 | 11111111-1111-1111-1111-111111111111, subscriptions/ |
| scripts/test_unified_runner.py:318 | job-dia- |
| scripts/test_unified_runner.py:319 | job-dia- |
| scripts/test_unified_runner.py:346 | fixture |
| scripts/test_unified_runner.py:356 | blob.core.windows.net |
| scripts/test_unified_runner.py:359 | blob.core.windows.net |
| scripts/test_usage_optional_config.py:4 | fixture |
| scripts/test_usage_optional_config.py:10 | fixture |
| scripts/test_usage_optional_config.py:11 | fixture |
| scripts/test_usage_optional_config.py:12 | fixture |
| scripts/test_usage_optional_config.py:15 | fixture |
| scripts/test_usage_optional_config.py:23 | fixture |
| scripts/test_usage_snapshot_history.py:10 | fixture |
| scripts/test_usage_snapshot_history.py:51 | fixture |
| scripts/test_usage_snapshot_history.py:89 | fixture |
| scripts/test_v2_runtime.py:4 | fixture |
| scripts/test_v2_runtime.py:5 | fixture |
| scripts/test_v2_runtime.py:14 | fixture |
| scripts/test_v2_runtime.py:19 | fixture |
| scripts/test_visual_display_names.py:8 | fixture |
| scripts/test_visual_display_names.py:29 | fixture |
| scripts/test_visual_display_names.py:40 | fixture |
| scripts/test_visual_display_names.py:54 | workspace/ |
| scripts/test_visual_target.py:9 | fixture |
| scripts/test_visual_target.py:19 | Warehouse |
| scripts/test_visual_target.py:23 | Warehouse, warehouse |
| scripts/test_visual_target.py:37 | Warehouse |
| scripts/test_visual_target.py:44 | Warehouse |
| scripts/test_visual_target.py:94 | Warehouse |
| scripts/test_visual_target.py:96 | warehouse |
| scripts/test_visual_target.py:98 | warehouse |
| scripts/test_visual_target.py:103 | warehouse |
| scripts/test_visual_target.py:113 | fixture |
| scripts/test_visual_target.py:125 | fixture |
| scripts/test_visual_target.py:126 | fixture |
| scripts/test_visual_target.py:128 | fixture |
| scripts/test_warehouse_audit_catalog.py:3 | warehouse |
| scripts/test_warehouse_audit_catalog.py:6 | Warehouse |
| scripts/test_warehouse_audit_catalog.py:9 | warehouse |
| scripts/test_warehouse_audit_catalog.py:12 | Warehouse |
| scripts/test_warehouse_audit_catalog.py:13 | warehouse |
| scripts/test_warehouse_audit_catalog.py:24 | warehouse |
| scripts/test_warehouse_audit_catalog.py:26 | warehouse |
| scripts/test_warehouse_audit_catalog.py:30 | warehouse |
| scripts/test_warehouse_audit_catalog.py:31 | Warehouse |
| scripts/test_warehouse_audit_catalog.py:33 | warehouse |
| scripts/test_warehouse_audit_catalog.py:41 | warehouse |
| scripts/test_warehouse_copy_lineage.py:1 | Warehouse |
| scripts/test_warehouse_copy_lineage.py:9 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_warehouse_copy_lineage.py:10 | 00000000-0000-0000-0000-000000000002 |
| scripts/test_warehouse_copy_lineage.py:23 | Warehouse |
| scripts/test_warehouse_copy_lineage.py:24 | Warehouse |
| scripts/test_warehouse_copy_lineage.py:25 | SemanticModel |
| scripts/test_warehouse_copy_lineage.py:29 | warehouse |
| scripts/test_warehouse_copy_lineage.py:36 | warehouse |
| scripts/test_warehouse_copy_lineage.py:37 | SemanticModel |
| scripts/test_warehouse_copy_lineage.py:43 | WAREHOUSE |
| scripts/test_warehouse_copy_lineage.py:48 | warehouse |
| scripts/test_warehouse_copy_lineage.py:49 | Lakehouse |
| scripts/test_warehouse_copy_lineage.py:72 | Lakehouse |
| scripts/test_warehouse_copy_lineage.py:74 | Lakehouse |
| scripts/test_worker_replay_paths.py:167 | 00000000-0000-0000-0000-000000000001 |
| scripts/test_worker_replay_paths.py:168 | 00000000-0000-0000-0000-000000000002, lakehouse |
| scripts/test_workspace_admission.py:14 | fixture |
| scripts/test_workspace_admission.py:16 | fixture |
| scripts/test_workspace_admission.py:19 | fixture |
| scripts/test_workspace_admission.py:24 | fixture |
| scripts/test_workspace_admission.py:28 | fixture |
| scripts/test_workspace_admission.py:32 | fixture |
| scripts/test_workspace_admission.py:33 | fixture |
| scripts/test_workspace_admission.py:34 | fixture |
| scripts/test_workspace_admission.py:36 | fixture |
| scripts/test_workspace_admission.py:47 | fixture |
| scripts/test_workspace_admission.py:61 | fixture |
| tests/fixtures/round24-route-sources/scripts/investigator/adapters/ai_native_catalog.py:32 | Lakehouse, Warehouse |
| tests/fixtures/round24-route-sources/scripts/investigator/adapters/ai_native_catalog.py:42 | SemanticModel |
| tests/fixtures/round24-route-sources/scripts/investigator/adapters/ai_native_catalog.py:56 | Lakehouse, Warehouse |
| tests/fixtures/round24-route-sources/scripts/investigator/adapters/ai_native_catalog.py:155 | Lakehouse |
| tests/fixtures/round24-route-sources/scripts/investigator/adapters/ai_native_catalog.py:158 | Lakehouse |
| tests/fixtures/round24-route-sources/scripts/investigator/adapters/ai_native_catalog.py:160 | Warehouse |
| tests/fixtures/round24-route-sources/scripts/investigator/adapters/ai_native_catalog.py:248 | Warehouse |
| tests/fixtures/round24-route-sources/scripts/investigator/adapters/ai_native_catalog.py:258 | Lakehouse |
| tests/fixtures/round24-route-sources/scripts/investigator/adapters/ai_native_catalog.py:273 | Lakehouse, Warehouse |
| tests/fixtures/round24-route-sources/scripts/investigator/adapters/ai_native_catalog.py:283 | Lakehouse, Warehouse |
| tests/fixtures/round24-route-sources/scripts/investigator/adapters/ai_native_catalog.py:289 | Lakehouse, Warehouse |
| tests/fixtures/round24-route-sources/scripts/investigator/adapters/ai_native_catalog.py:365 | Lakehouse, Warehouse |
