# Round Ten C: preserved intake audit

Recorded 2026-10-08. Zero estate reads and zero model calls. Original runs and sealed tapes remain unchanged. Inventory below is the exact neutral wire inventory supplied in the recorded intake requests; candidate_visuals in each intake is the actual eligible inventory at refusal. For ASK decisions, the resolver was never called. Native identifiers are not reconstructed from current discovery.

| Batch | Cause | Count |
| --- | --- | --- |
| disabled | mixed-business-refusal | 5 |
| disabled | named-target-required | 12 |
| disabled | precision-ask | 2 |
| disabled | starting-measure-ask | 1 |
| rehearsal | mixed-business-refusal | 2 |
| rehearsal | named-target-required | 7 |

## rehearsal: family-A-case

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "3e0d9862-a79c-41c5-8fed-2f2e70f45501",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.",
    "request_key": "round-ten-rehearsal-family-A-once",
    "parent_id": null
  },
  "text": "In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791438546.3664114,
  "expires": 1791439446.3673255,
  "catalog_hash": "64151396b0ea0c7086a5412e230afb639a5f8ec46c8dd17c6ac3b76b57a34b59",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "5e2a45cb0d9c21d688d8f1aec6f7cd4e56dab01638e4139aac3af30dab58d3b7",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Extended%20Value",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Inbound%20Fraction",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 28,
          "end": 97,
          "quote": "Handled Quantity appears higher than the source stock movements total"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 28,
          "end": 44,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 3,
          "end": 26,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 3,
          "end": 26,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "67e1d48bc0d654bf26a14a4dd5097d7c19289d7d8f7b9ab9acba2027273f2b6a",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-3e0d9862-a79c-41c5-8fed-2f2e70f45501"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-3e0d9862-a79c-41c5-8fed-2f2e70f45501"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-3e0d9862-a79c-41c5-8fed-2f2e70f45501"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4525,
    "output": [
      {
        "id": "fc_00100c91aa283745016ac72edad058819489ed877c1c4ee3b7",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m1\",\"measure_id\":\"m1v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"FIGURE_DIFFERENCE\",\"source\":{\"quote\":\"Handled Quantity appears higher than the source stock movements total\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"MISMATCH_COMPLAINT:VERTICAL\"}",
        "call_id": "call_pjZK5G7y24WQq3AJuMognOvc",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4524,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [
          {
            "id": "m1r0",
            "name": "Rehearsal declared predicates 20261008"
          },
          {
            "id": "m1r1",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m1r2",
            "name": "Warehouse Performance e1b8e1"
          }
        ],
        "measures": [
          {
            "id": "m1v0",
            "name": "Activity Entries"
          },
          {
            "id": "m1v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m1v2",
            "name": "Extended Value"
          },
          {
            "id": "m1v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m1v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m1v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m1v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m1v7",
            "name": "Quantity Balance"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m1r0",
            "target_id": "m1t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m1r1",
            "target_id": "m1t5",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v2",
              "m1v3",
              "m1v4",
              "m1v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m1r1",
            "target_id": "m1t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m1r1",
            "target_id": "m1t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t8",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t11",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v0",
              "m1v1",
              "m1v5",
              "m1v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t12",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## rehearsal: family-B-case

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Receipt Share.

Recorded intake output, verbatim JSON:

```json
{
  "id": "ed032ea2-da7e-4340-8ede-71f3057a97fd",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "In Inventory Health e1b8e1, Inbound Fraction looks high. Check its current global value and explain the numerator and denominator using the actual measure definitions.",
    "request_key": "round-ten-rehearsal-family-B-once",
    "parent_id": null
  },
  "text": "In Inventory Health e1b8e1, Inbound Fraction looks high. Check its current global value and explain the numerator and denominator using the actual measure definitions.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791438575.9905753,
  "expires": 1791439475.9910076,
  "catalog_hash": "64151396b0ea0c7086a5412e230afb639a5f8ec46c8dd17c6ac3b76b57a34b59",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "5e2a45cb0d9c21d688d8f1aec6f7cd4e56dab01638e4139aac3af30dab58d3b7",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Receipt Share.",
  "candidate_visuals": [
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Extended%20Value",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Inbound%20Fraction",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    },
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Inventory Health",
        "Receipt Share"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Inbound%20Fraction"
      ],
      "grouping_columns": [],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 92,
          "end": 166,
          "quote": "explain the numerator and denominator using the actual measure definitions"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 28,
          "end": 44,
          "quote": "Inbound Fraction"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 3,
          "end": 26,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 3,
          "end": 26,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "9416054a507dc716690977304261740b8d99a9c5d877e1b5f0b321f9682d1820",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Receipt Share.",
      "evidence_id": "intake-refusal-ed032ea2-da7e-4340-8ede-71f3057a97fd"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: In Inventory Health e1b8e1, Inbound Fraction looks high. Check its current global value and explain the numerator and denominator using the actual measure definitions.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-ed032ea2-da7e-4340-8ede-71f3057a97fd"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: In Inventory Health e1b8e1, Inbound Fraction looks high. Check its current global value and explain the numerator and denominator using the actual measure definitions.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Receipt Share.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-ed032ea2-da7e-4340-8ede-71f3057a97fd"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4526,
    "output": [
      {
        "id": "fc_0c93a9d087a1865e016ac72ef661c0819395eb3de301b4c987",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m1\",\"measure_id\":\"m1v4\",\"metric_quote\":\"Inbound Fraction\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"METRIC_COMPONENTS\",\"source\":{\"quote\":\"explain the numerator and denominator using the actual measure definitions\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_hM8hHo7JVISqEjnlSRmybIl9",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4525,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [
          {
            "id": "m1r0",
            "name": "Rehearsal declared predicates 20261008"
          },
          {
            "id": "m1r1",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m1r2",
            "name": "Warehouse Performance e1b8e1"
          }
        ],
        "measures": [
          {
            "id": "m1v0",
            "name": "Activity Entries"
          },
          {
            "id": "m1v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m1v2",
            "name": "Extended Value"
          },
          {
            "id": "m1v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m1v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m1v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m1v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m1v7",
            "name": "Quantity Balance"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m1r0",
            "target_id": "m1t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m1r1",
            "target_id": "m1t5",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v2",
              "m1v3",
              "m1v4",
              "m1v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m1r1",
            "target_id": "m1t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m1r1",
            "target_id": "m1t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t8",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t11",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v0",
              "m1v1",
              "m1v5",
              "m1v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t12",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## rehearsal: family-C-case

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Net Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "e823f2c9-9895-4420-9ed8-c340bb0e3a47",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "In Inventory Health e1b8e1, Quantity Balance looks low. Inspect its current global value and the related calculations to explain what contributes to it.",
    "request_key": "round-ten-rehearsal-family-C-once",
    "parent_id": null
  },
  "text": "In Inventory Health e1b8e1, Quantity Balance looks low. Inspect its current global value and the related calculations to explain what contributes to it.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791438600.7689369,
  "expires": 1791439500.769377,
  "catalog_hash": "64151396b0ea0c7086a5412e230afb639a5f8ec46c8dd17c6ac3b76b57a34b59",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "5e2a45cb0d9c21d688d8f1aec6f7cd4e56dab01638e4139aac3af30dab58d3b7",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Net Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Inventory Health",
        "Net Movement Units"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Extended%20Value",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Inbound%20Fraction",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 28,
          "end": 44,
          "quote": "Quantity Balance"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 93,
          "end": 151,
          "quote": "the related calculations to explain what contributes to it"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 28,
          "end": 44,
          "quote": "Quantity Balance"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 3,
          "end": 26,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 3,
          "end": 26,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "57d8c177daf6b15229d1176e449ba18da2e3591067df7ff886cabfb1d9aa890f",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Net Movement Units.",
      "evidence_id": "intake-refusal-e823f2c9-9895-4420-9ed8-c340bb0e3a47"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: In Inventory Health e1b8e1, Quantity Balance looks low. Inspect its current global value and the related calculations to explain what contributes to it.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-e823f2c9-9895-4420-9ed8-c340bb0e3a47"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: In Inventory Health e1b8e1, Quantity Balance looks low. Inspect its current global value and the related calculations to explain what contributes to it.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Net Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-e823f2c9-9895-4420-9ed8-c340bb0e3a47"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4527,
    "output": [
      {
        "id": "fc_0d90695406fa44d6016ac72f0f05148195b414f55e449d1c19",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m1\",\"measure_id\":\"m1v7\",\"metric_quote\":\"Quantity Balance\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Quantity Balance\"}}],\"question_kind\":{\"kind\":\"METRIC_COMPONENTS\",\"source\":{\"quote\":\"the related calculations to explain what contributes to it\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_7H9sGeer9lqGTlXFVKam6usS",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4526,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [
          {
            "id": "m1r0",
            "name": "Rehearsal declared predicates 20261008"
          },
          {
            "id": "m1r1",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m1r2",
            "name": "Warehouse Performance e1b8e1"
          }
        ],
        "measures": [
          {
            "id": "m1v0",
            "name": "Activity Entries"
          },
          {
            "id": "m1v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m1v2",
            "name": "Extended Value"
          },
          {
            "id": "m1v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m1v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m1v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m1v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m1v7",
            "name": "Quantity Balance"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m1r0",
            "target_id": "m1t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m1r1",
            "target_id": "m1t5",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v2",
              "m1v3",
              "m1v4",
              "m1v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m1r1",
            "target_id": "m1t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m1r1",
            "target_id": "m1t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t8",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t11",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v0",
              "m1v1",
              "m1v5",
              "m1v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t12",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## rehearsal: family-D-case

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "e3b10e46-39e8-4a5c-b691-db888a60873c",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.",
    "request_key": "round-ten-rehearsal-family-D-once",
    "parent_id": null
  },
  "text": "In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791438626.2059488,
  "expires": 1791439526.2067637,
  "catalog_hash": "64151396b0ea0c7086a5412e230afb639a5f8ec46c8dd17c6ac3b76b57a34b59",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "5e2a45cb0d9c21d688d8f1aec6f7cd4e56dab01638e4139aac3af30dab58d3b7",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Extended%20Value",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Inbound%20Fraction",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 38,
          "end": 53,
          "quote": "warehouse North"
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 48,
          "end": 53,
          "quote": "North"
        },
        {
          "start": 113,
          "end": 118,
          "quote": "North"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 103,
          "end": 190,
          "quote": "Check the North selection and explain what report context you can and cannot reproduce."
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 48,
          "end": 53,
          "quote": "North"
        },
        {
          "start": 113,
          "end": 118,
          "quote": "North"
        }
      ]
    },
    {
      "field": "descriptor",
      "occurrences": [
        {
          "start": 38,
          "end": 47,
          "quote": "warehouse"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 55,
          "end": 71,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 3,
          "end": 26,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 3,
          "end": 26,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "7409d482203a325bcf6d72a759084667cb67ee739c7e64e4a78b9f3b5ec06a97",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-e3b10e46-39e8-4a5c-b691-db888a60873c"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-e3b10e46-39e8-4a5c-b691-db888a60873c"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: In Inventory Health e1b8e1 I selected warehouse North. Handled Quantity differs from the global total. Check the North selection and explain what report context you can and cannot reproduce.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-e3b10e46-39e8-4a5c-b691-db888a60873c"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4528,
    "output": [
      {
        "id": "fc_0591551e4bbccb4b016ac72f28afc08196afbd5796cf6fddf1",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m1\",\"measure_id\":\"m1v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[{\"role\":\"SELECTION\",\"source\":{\"quote\":\"warehouse North\"}},{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"North\"}}],\"question_kind\":{\"kind\":\"FILTER_EFFECT\",\"source\":{\"quote\":\"Check the North selection and explain what report context you can and cannot reproduce.\"}},\"target_request\":{\"value_source\":{\"quote\":\"North\"},\"column_source\":null,\"descriptor\":{\"state\":\"SEPARATED\",\"source\":{\"quote\":\"warehouse\"}}},\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"MISMATCH_COMPLAINT:VERTICAL\"}",
        "call_id": "call_FqiPvm9uDVjd2Q9e6NEqJtej",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4527,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [
          {
            "id": "m1r0",
            "name": "Rehearsal declared predicates 20261008"
          },
          {
            "id": "m1r1",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m1r2",
            "name": "Warehouse Performance e1b8e1"
          }
        ],
        "measures": [
          {
            "id": "m1v0",
            "name": "Activity Entries"
          },
          {
            "id": "m1v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m1v2",
            "name": "Extended Value"
          },
          {
            "id": "m1v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m1v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m1v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m1v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m1v7",
            "name": "Quantity Balance"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m1r0",
            "target_id": "m1t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m1r1",
            "target_id": "m1t5",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v2",
              "m1v3",
              "m1v4",
              "m1v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m1r1",
            "target_id": "m1t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m1r1",
            "target_id": "m1t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t8",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t11",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v0",
              "m1v1",
              "m1v5",
              "m1v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t12",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## rehearsal: family-E-case

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "cebe71cf-ebae-433e-8319-969c9d5b3c6f",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established. I have not supplied a freshness SLA.",
    "request_key": "round-ten-rehearsal-family-E-once",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established. I have not supplied a freshness SLA.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791438651.4421706,
  "expires": 1791439551.4425795,
  "catalog_hash": "64151396b0ea0c7086a5412e230afb639a5f8ec46c8dd17c6ac3b76b57a34b59",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "5e2a45cb0d9c21d688d8f1aec6f7cd4e56dab01638e4139aac3af30dab58d3b7",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Extended%20Value",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Inbound%20Fraction",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 24,
          "end": 157,
          "quote": "Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established."
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "b78dbbfa13c24ec5a2c0dfbd28900e621568c4881ad80a958b148fe31c8509be",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-cebe71cf-ebae-433e-8319-969c9d5b3c6f"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established. I have not supplied a freshness SLA.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-cebe71cf-ebae-433e-8319-969c9d5b3c6f"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established. I have not supplied a freshness SLA.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-cebe71cf-ebae-433e-8319-969c9d5b3c6f"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4529,
    "output": [
      {
        "id": "fc_0f02a6b2b7114014016ac72f4112bc8194b152e6e67d0116ea",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m1\",\"measure_id\":\"m1v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"FRESHNESS\",\"source\":{\"quote\":\"Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established.\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_LcpMAYDYUH1HW1vbxzhPY9hJ",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4528,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [
          {
            "id": "m1r0",
            "name": "Rehearsal declared predicates 20261008"
          },
          {
            "id": "m1r1",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m1r2",
            "name": "Warehouse Performance e1b8e1"
          }
        ],
        "measures": [
          {
            "id": "m1v0",
            "name": "Activity Entries"
          },
          {
            "id": "m1v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m1v2",
            "name": "Extended Value"
          },
          {
            "id": "m1v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m1v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m1v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m1v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m1v7",
            "name": "Quantity Balance"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m1r0",
            "target_id": "m1t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m1r1",
            "target_id": "m1t5",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v2",
              "m1v3",
              "m1v4",
              "m1v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m1r1",
            "target_id": "m1t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m1r1",
            "target_id": "m1t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t8",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t11",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v0",
              "m1v1",
              "m1v5",
              "m1v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t12",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## rehearsal: family-F-case

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.

Recorded intake output, verbatim JSON:

```json
{
  "id": "95f517d6-d6dd-4da7-9f57-882b3372f083",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Extended Value seems overstated. Investigate the current total, the upstream data and available transformation definitions to identify a supported explanation.",
    "request_key": "round-ten-rehearsal-family-F-once",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Extended Value seems overstated. Investigate the current total, the upstream data and available transformation definitions to identify a supported explanation.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791438675.413417,
  "expires": 1791439575.4138672,
  "catalog_hash": "64151396b0ea0c7086a5412e230afb639a5f8ec46c8dd17c6ac3b76b57a34b59",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "5e2a45cb0d9c21d688d8f1aec6f7cd4e56dab01638e4139aac3af30dab58d3b7",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.",
  "candidate_visuals": [
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Inventory Health",
        "Movement Value"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Extended%20Value"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Extended%20Value",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Inbound%20Fraction",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 24,
          "end": 55,
          "quote": "Extended Value seems overstated"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 38,
          "quote": "Extended Value"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "91f84d4dd35343697ed3a24ef6517707564e7066bfc3a5035bcbc5ce444213a1",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.",
      "evidence_id": "intake-refusal-95f517d6-d6dd-4da7-9f57-882b3372f083"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Extended Value seems overstated. Investigate the current total, the upstream data and available transformation definitions to identify a supported explanation.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-95f517d6-d6dd-4da7-9f57-882b3372f083"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Extended Value seems overstated. Investigate the current total, the upstream data and available transformation definitions to identify a supported explanation.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-95f517d6-d6dd-4da7-9f57-882b3372f083"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4530,
    "output": [
      {
        "id": "fc_0c4089649d9c2aff016ac72f59f2e881978f68c870bba0f27b",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m1\",\"measure_id\":\"m1v2\",\"metric_quote\":\"Extended Value\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"FIGURE_DIFFERENCE\",\"source\":{\"quote\":\"Extended Value seems overstated\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"MISMATCH_COMPLAINT:VERTICAL\"}",
        "call_id": "call_vWty5iG7q4RQUyiVcwzDkcuY",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4529,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [
          {
            "id": "m1r0",
            "name": "Rehearsal declared predicates 20261008"
          },
          {
            "id": "m1r1",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m1r2",
            "name": "Warehouse Performance e1b8e1"
          }
        ],
        "measures": [
          {
            "id": "m1v0",
            "name": "Activity Entries"
          },
          {
            "id": "m1v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m1v2",
            "name": "Extended Value"
          },
          {
            "id": "m1v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m1v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m1v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m1v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m1v7",
            "name": "Quantity Balance"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m1r0",
            "target_id": "m1t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m1r1",
            "target_id": "m1t5",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v2",
              "m1v3",
              "m1v4",
              "m1v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m1r1",
            "target_id": "m1t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m1r1",
            "target_id": "m1t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t8",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t11",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v0",
              "m1v1",
              "m1v5",
              "m1v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t12",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## rehearsal: family-G-case

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "5e328403-25a1-4f60-8140-d199b8fe3c69",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.",
    "request_key": "round-ten-rehearsal-family-G-once",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791438701.6757166,
  "expires": 1791439601.676554,
  "catalog_hash": "64151396b0ea0c7086a5412e230afb639a5f8ec46c8dd17c6ac3b76b57a34b59",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "5e2a45cb0d9c21d688d8f1aec6f7cd4e56dab01638e4139aac3af30dab58d3b7",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Extended%20Value",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Inbound%20Fraction",
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 41,
          "end": 77,
          "quote": "may include incorrect source entries"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "46ea7486287701454e113051ec203133dcb1b12e9535c7158d7dda413eebcd5b",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-5e328403-25a1-4f60-8140-d199b8fe3c69"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-5e328403-25a1-4f60-8140-d199b8fe3c69"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity may include incorrect source entries. Inspect source stock movements and related inventory adjustments for evidence. Do not assume an adjustment record alone proves the intended business rule.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-5e328403-25a1-4f60-8140-d199b8fe3c69"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4531,
    "output": [
      {
        "id": "fc_042cf07cb35d937a016ac72f73d9088193b34e94372e4f3232",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m1\",\"measure_id\":\"m1v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"SOURCE_CORRECTNESS\",\"source\":{\"quote\":\"may include incorrect source entries\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_KKQPqRqWdbFeLMm3zp9M7OdN",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4530,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [
          {
            "id": "m1r0",
            "name": "Rehearsal declared predicates 20261008"
          },
          {
            "id": "m1r1",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m1r2",
            "name": "Warehouse Performance e1b8e1"
          }
        ],
        "measures": [
          {
            "id": "m1v0",
            "name": "Activity Entries"
          },
          {
            "id": "m1v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m1v2",
            "name": "Extended Value"
          },
          {
            "id": "m1v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m1v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m1v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m1v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m1v7",
            "name": "Quantity Balance"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m1r0",
            "target_id": "m1t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m1r1",
            "target_id": "m1t5",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v2",
              "m1v3",
              "m1v4",
              "m1v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m1r1",
            "target_id": "m1t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m1r1",
            "target_id": "m1t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t8",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t11",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v0",
              "m1v1",
              "m1v5",
              "m1v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t12",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## rehearsal: family-H-case

Exact refusal/question: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.

Recorded intake output, verbatim JSON:

```json
{
  "id": "493a13dd-a2db-4a0c-b4be-96e3a4e98608",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Warehouse Performance e1b8e1 Inbound Quantity and Outbound Quantity are different. Explain whether the current observed difference follows their definitions, and state what business intent remains unknown.",
    "request_key": "round-ten-rehearsal-family-H-once",
    "parent_id": null
  },
  "text": "Warehouse Performance e1b8e1 Inbound Quantity and Outbound Quantity are different. Explain whether the current observed difference follows their definitions, and state what business intent remains unknown.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "UNIMPLEMENTED_ROUTE",
  "created": 1791438727.5815308,
  "expires": 1791439627.582279,
  "catalog_hash": "64151396b0ea0c7086a5412e230afb639a5f8ec46c8dd17c6ac3b76b57a34b59",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "5e2a45cb0d9c21d688d8f1aec6f7cd4e56dab01638e4139aac3af30dab58d3b7",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 83,
          "end": 205,
          "quote": "Explain whether the current observed difference follows their definitions, and state what business intent remains unknown."
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 29,
          "end": 67,
          "quote": "Inbound Quantity and Outbound Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 28,
          "quote": "Warehouse Performance e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "324737cf0fd1e0944944960d12a8aa0e7110b9e18c5a939d68ab7786b3b1f59b",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
      "evidence_id": "intake-refusal-493a13dd-a2db-4a0c-b4be-96e3a4e98608"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Warehouse Performance e1b8e1 Inbound Quantity and Outbound Quantity are different. Explain whether the current observed difference follows their definitions, and state what business intent remains unknown.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-493a13dd-a2db-4a0c-b4be-96e3a4e98608"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Warehouse Performance e1b8e1 Inbound Quantity and Outbound Quantity are different. Explain whether the current observed difference follows their definitions, and state what business intent remains unknown.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-493a13dd-a2db-4a0c-b4be-96e3a4e98608"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4532,
    "output": [
      {
        "id": "fc_0d93bc8042935637016ac72f8d20ec819798b58fba7a908240",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m1\",\"measure_id\":\"m1v5\",\"metric_quote\":\"Inbound Quantity and Outbound Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"BUSINESS_MEANING\",\"source\":{\"quote\":\"Explain whether the current observed difference follows their definitions, and state what business intent remains unknown.\"}},\"target_request\":null,\"report_quote\":\"Warehouse Performance e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_7xMC5LbmcCoZDYjsLlzypn32",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4531,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [
          {
            "id": "m1r0",
            "name": "Rehearsal declared predicates 20261008"
          },
          {
            "id": "m1r1",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m1r2",
            "name": "Warehouse Performance e1b8e1"
          }
        ],
        "measures": [
          {
            "id": "m1v0",
            "name": "Activity Entries"
          },
          {
            "id": "m1v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m1v2",
            "name": "Extended Value"
          },
          {
            "id": "m1v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m1v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m1v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m1v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m1v7",
            "name": "Quantity Balance"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m1r0",
            "target_id": "m1t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m1r1",
            "target_id": "m1t5",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v2",
              "m1v3",
              "m1v4",
              "m1v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m1r1",
            "target_id": "m1t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m1r1",
            "target_id": "m1t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t8",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t11",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v0",
              "m1v1",
              "m1v5",
              "m1v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t12",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## rehearsal: family-I-case

Exact refusal/question: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.

Recorded intake output, verbatim JSON:

```json
{
  "id": "bfef2f88-eaf8-41f2-8d95-238b0fbb1095",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "For Inventory Health e1b8e1 Handled Quantity, what does adjustment reason Q49 mean, and should those adjustments affect this metric?",
    "request_key": "round-ten-rehearsal-family-I-once",
    "parent_id": null
  },
  "text": "For Inventory Health e1b8e1 Handled Quantity, what does adjustment reason Q49 mean, and should those adjustments affect this metric?",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "UNIMPLEMENTED_ROUTE",
  "created": 1791438753.8842304,
  "expires": 1791439653.8852103,
  "catalog_hash": "64151396b0ea0c7086a5412e230afb639a5f8ec46c8dd17c6ac3b76b57a34b59",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "5e2a45cb0d9c21d688d8f1aec6f7cd4e56dab01638e4139aac3af30dab58d3b7",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 74,
          "end": 77,
          "quote": "Q49"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 46,
          "end": 132,
          "quote": "what does adjustment reason Q49 mean, and should those adjustments affect this metric?"
        }
      ]
    },
    {
      "field": "numeral",
      "occurrences": [
        {
          "start": 74,
          "end": 77,
          "quote": "Q49"
        }
      ]
    },
    {
      "field": "numeral",
      "occurrences": [
        {
          "start": 21,
          "end": 27,
          "quote": "e1b8e1"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 28,
          "end": 44,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 4,
          "end": 27,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "88a97435b9df40e998340732d83d96e3cee314fd847ede57e75e8367f5c751d0",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
      "evidence_id": "intake-refusal-bfef2f88-eaf8-41f2-8d95-238b0fbb1095"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: For Inventory Health e1b8e1 Handled Quantity, what does adjustment reason Q49 mean, and should those adjustments affect this metric?\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-bfef2f88-eaf8-41f2-8d95-238b0fbb1095"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: For Inventory Health e1b8e1 Handled Quantity, what does adjustment reason Q49 mean, and should those adjustments affect this metric?\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-bfef2f88-eaf8-41f2-8d95-238b0fbb1095"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4533,
    "output": [
      {
        "id": "fc_00d91d3475c7b5b7016ac72fa7ef648193a9f8b2f3777cf178",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m1\",\"measure_id\":\"m1v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":{\"source\":{\"quote\":\"Inventory Health e1b8e1 Handled Quantity\"},\"mode\":\"UNGROUPED\",\"mode_source\":null},\"value_mentions\":[{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Q49\"}}],\"question_kind\":{\"kind\":\"BUSINESS_MEANING\",\"source\":{\"quote\":\"what does adjustment reason Q49 mean, and should those adjustments affect this metric?\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[{\"role\":\"OTHER\",\"quote\":\"Q49\"},{\"role\":\"OTHER\",\"quote\":\"e1b8e1\"}],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_MrXb4mFiP2eMbJoMFasnKh53",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4532,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [
          {
            "id": "m1r0",
            "name": "Rehearsal declared predicates 20261008"
          },
          {
            "id": "m1r1",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m1r2",
            "name": "Warehouse Performance e1b8e1"
          }
        ],
        "measures": [
          {
            "id": "m1v0",
            "name": "Activity Entries"
          },
          {
            "id": "m1v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m1v2",
            "name": "Extended Value"
          },
          {
            "id": "m1v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m1v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m1v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m1v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m1v7",
            "name": "Quantity Balance"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m1r0",
            "target_id": "m1t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m1r0",
            "target_id": "m1t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m1r1",
            "target_id": "m1t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m1r1",
            "target_id": "m1t5",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v2",
              "m1v3",
              "m1v4",
              "m1v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m1r1",
            "target_id": "m1t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m1r1",
            "target_id": "m1t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t8",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m1v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t11",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m1c16"
            ],
            "measure_ids": [
              "m1v0",
              "m1v1",
              "m1v5",
              "m1v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m1r2",
            "target_id": "m1t12",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-A-mention

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "94058cce-7740-447b-9484-cb979bf1c1a8",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Handled Quantity is higher than source movements. Check the global discrepancy. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.",
    "request_key": "round-ten-b-declared-family-A-mention",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Handled Quantity is higher than source movements. Check the global discrepancy. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791425336.8309636,
  "expires": 1791426236.8318686,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 24,
          "end": 72,
          "quote": "Handled Quantity is higher than source movements"
        }
      ]
    },
    {
      "field": "reported_figure",
      "occurrences": [
        {
          "start": 148,
          "end": 152,
          "quote": "8765"
        }
      ]
    },
    {
      "field": "numeral",
      "occurrences": [
        {
          "start": 17,
          "end": 23,
          "quote": "e1b8e1"
        }
      ]
    },
    {
      "field": "numeral",
      "occurrences": [
        {
          "start": 181,
          "end": 185,
          "quote": "4182"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Quantity"
        },
        {
          "start": 115,
          "end": 131,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "visual",
      "occurrences": [
        {
          "start": 108,
          "end": 131,
          "quote": "global Handled Quantity"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "27c2012ee5cd093a7ee7dc16dc65ccb99a914b6755d9e612e52b1808eddbe50c",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-94058cce-7740-447b-9484-cb979bf1c1a8"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity is higher than source movements. Check the global discrepancy. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-94058cce-7740-447b-9484-cb979bf1c1a8"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity is higher than source movements. Check the global discrepancy. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-94058cce-7740-447b-9484-cb979bf1c1a8"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4095,
    "output": [
      {
        "id": "fc_0c5dda9a4cd8d9d0016ac6fb42a2b481909f320128156bcc77",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":{\"source\":{\"quote\":\"global Handled Quantity\"},\"mode\":\"UNGROUPED\",\"mode_source\":null},\"value_mentions\":[],\"question_kind\":{\"kind\":\"FIGURE_DIFFERENCE\",\"source\":{\"quote\":\"Handled Quantity is higher than source movements\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[{\"role\":\"FIGURE\",\"quote\":\"8765\"},{\"role\":\"OTHER\",\"quote\":\"e1b8e1\"},{\"role\":\"OTHER\",\"quote\":\"4182\"}],\"triage\":\"MISMATCH_COMPLAINT:VERTICAL\"}",
        "call_id": "call_wICSRffA3ygg8aAytcl6FABh",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4094,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-D-noisy

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "1b50fb7d-7fec-4254-b07d-728b32654852",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Forwarded warehouse help request\nFrom: shift supervisor\nSubject: D metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1: I selected North. Handled Quantity differs from the global value. Explain the selected warehouse scope.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations",
    "request_key": "round-ten-b-declared-family-D-noisy",
    "parent_id": null
  },
  "text": "Forwarded warehouse help request\nFrom: shift supervisor\nSubject: D metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1: I selected North. Handled Quantity differs from the global value. Explain the selected warehouse scope.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791425384.9423957,
  "expires": 1791426284.943317,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 228,
          "end": 233,
          "quote": "North"
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 156,
          "end": 160,
          "quote": "7321"
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 235,
          "end": 251,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 283,
          "end": 320,
          "quote": "Explain the selected warehouse scope."
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 228,
          "end": 233,
          "quote": "North"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 235,
          "end": 251,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 192,
          "end": 215,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 192,
          "end": 215,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "visual",
      "occurrences": [
        {
          "start": 192,
          "end": 215,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "adc13f13fd4c6ed483f9e18eb9480b71bd02e7908aaccb0c56c038a93c6b861d",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-1b50fb7d-7fec-4254-b07d-728b32654852"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Forwarded warehouse help request From: shift supervisor Subject: D metric follow-up Please ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure. Inventory Health e1b8e1: I selected North. Handled Quantity differs from the global value. Explain the selected warehouse scope. Previous email: we need evidence and its limits, not a guess. Regards, operations\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-1b50fb7d-7fec-4254-b07d-728b32654852"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Forwarded warehouse help request\nFrom: shift supervisor\nSubject: D metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1: I selected North. Handled Quantity differs from the global value. Explain the selected warehouse scope.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-1b50fb7d-7fec-4254-b07d-728b32654852"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4096,
    "output": [
      {
        "id": "fc_003a50e1eb4c96b0016ac6fb72939c8196aa2a38ee7ffd1ebb",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":{\"source\":{\"quote\":\"Inventory Health e1b8e1\"},\"mode\":\"UNGROUPED\",\"mode_source\":null},\"value_mentions\":[{\"role\":\"SELECTION\",\"source\":{\"quote\":\"North\"}},{\"role\":\"MENTION\",\"source\":{\"quote\":\"7321\"}},{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Handled Quantity\"}}],\"question_kind\":{\"kind\":\"FILTER_EFFECT\",\"source\":{\"quote\":\"Explain the selected warehouse scope.\"}},\"target_request\":{\"value_source\":{\"quote\":\"North\"},\"column_source\":null,\"descriptor\":{\"state\":\"VALUE_ONLY\",\"source\":null}},\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"MISMATCH_COMPLAINT:VERTICAL\"}",
        "call_id": "call_tZZf2YbOlyVplNI9UohwsEun",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4095,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-D-terse

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "47e084a5-48a5-44d4-824c-4d9de27006c4",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1: I selected North. Handled Quantity differs from the global value. Explain the selected warehouse scope.",
    "request_key": "round-ten-b-declared-family-D-terse",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1: I selected North. Handled Quantity differs from the global value. Explain the selected warehouse scope.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791425428.5781841,
  "expires": 1791426328.5797899,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 36,
          "end": 41,
          "quote": "North"
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 43,
          "end": 59,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 77,
          "end": 89,
          "quote": "global value"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 91,
          "end": 128,
          "quote": "Explain the selected warehouse scope."
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 36,
          "end": 41,
          "quote": "North"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 43,
          "end": 59,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "visual",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "9e473f716b72533289dcd03c42c36ba9b59d0fbf87fbf524b3526d246ede1581",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-47e084a5-48a5-44d4-824c-4d9de27006c4"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1: I selected North. Handled Quantity differs from the global value. Explain the selected warehouse scope.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-47e084a5-48a5-44d4-824c-4d9de27006c4"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1: I selected North. Handled Quantity differs from the global value. Explain the selected warehouse scope.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-47e084a5-48a5-44d4-824c-4d9de27006c4"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4097,
    "output": [
      {
        "id": "fc_02eb338ee64bd3c0016ac6fb9cd1e881978c95c672880cb9af",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":{\"source\":{\"quote\":\"Inventory Health e1b8e1\"},\"mode\":\"UNGROUPED\",\"mode_source\":null},\"value_mentions\":[{\"role\":\"SELECTION\",\"source\":{\"quote\":\"North\"}},{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Handled Quantity\"}},{\"role\":\"MENTION\",\"source\":{\"quote\":\"global value\"}}],\"question_kind\":{\"kind\":\"FILTER_EFFECT\",\"source\":{\"quote\":\"Explain the selected warehouse scope.\"}},\"target_request\":{\"value_source\":{\"quote\":\"North\"},\"column_source\":null,\"descriptor\":{\"state\":\"VALUE_ONLY\",\"source\":null}},\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"MISMATCH_COMPLAINT:VERTICAL\"}",
        "call_id": "call_1UwMrExJuV7HTX6wFAjdbDGj",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4096,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-E-mention

Exact refusal/question: The stated precision of the reported figure is unclear. At what precision should it be compared?

Recorded intake output, verbatim JSON:

```json
{
  "id": "395b43cc-1338-4ad8-a801-9719922cdbc3",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.",
    "request_key": "round-ten-b-declared-family-E-mention",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.",
  "turn": 1,
  "status": "NEEDS_INPUT",
  "proposal": null,
  "question": "The stated precision of the reported figure is unclear. At what precision should it be compared?",
  "error": null,
  "created": 1791425484.0954916,
  "expires": 1791426384.0965226,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [
    {
      "attempt": 1,
      "event": "INTAKE_RECORD_INVALID",
      "reservation_key": "resolve",
      "metadata": {
        "response_id": "resp_003ce9395a91b3bd016ac6fbd37028819382cba9d9adb3d64d",
        "model": "investigator-quality-54",
        "usage": {
          "input_tokens": 21667,
          "input_tokens_details": {
            "cache_write_tokens": 0,
            "cached_tokens": 21376
          },
          "output_tokens": 187,
          "output_tokens_details": {
            "reasoning_tokens": 0
          },
          "total_tokens": 21854
        },
        "quote_provenance": [
          {
            "field": "selection",
            "occurrences": [
              {
                "start": 24,
                "end": 40,
                "quote": "Handled Quantity"
              },
              {
                "start": 136,
                "end": 152,
                "quote": "Handled Quantity"
              }
            ]
          },
          {
            "field": "selection",
            "occurrences": [
              {
                "start": 24,
                "end": 40,
                "quote": "Handled Quantity"
              },
              {
                "start": 136,
                "end": 152,
                "quote": "Handled Quantity"
              }
            ]
          },
          {
            "field": "selection",
            "occurrences": [
              {
                "start": 169,
                "end": 173,
                "quote": "8765"
              }
            ]
          },
          {
            "field": "selection",
            "occurrences": [
              {
                "start": 202,
                "end": 206,
                "quote": "4182"
              }
            ]
          },
          {
            "field": "question_kind",
            "occurrences": [
              {
                "start": 41,
                "end": 93,
                "quote": "may be stale. Check freshness and processing history"
              }
            ]
          },
          {
            "field": "reported_figure",
            "occurrences": [
              {
                "start": 169,
                "end": 173,
                "quote": "8765"
              }
            ]
          },
          {
            "field": "numeral",
            "occurrences": [
              {
                "start": 202,
                "end": 206,
                "quote": "4182"
              }
            ]
          },
          {
            "field": "measure",
            "occurrences": [
              {
                "start": 24,
                "end": 40,
                "quote": "Handled Quantity"
              },
              {
                "start": 136,
                "end": 152,
                "quote": "Handled Quantity"
              }
            ]
          },
          {
            "field": "report",
            "occurrences": [
              {
                "start": 0,
                "end": 23,
                "quote": "Inventory Health e1b8e1"
              }
            ]
          },
          {
            "field": "report",
            "occurrences": [
              {
                "start": 0,
                "end": 23,
                "quote": "Inventory Health e1b8e1"
              }
            ]
          }
        ]
      },
      "rule": "INTAKE_RECORD_INVALID"
    },
    {
      "attempt": 2,
      "event": "INTAKE_RULE_RETRY",
      "reservation_key": "intake-rule-retry",
      "metadata": {
        "response_id": "resp_06593d353bcd67ca016ac6fbe0b0d48190b9ef95466a796db1",
        "model": "investigator-quality-54",
        "usage": {
          "input_tokens": 21750,
          "input_tokens_details": {
            "cache_write_tokens": 0,
            "cached_tokens": 3712
          },
          "output_tokens": 187,
          "output_tokens_details": {
            "reasoning_tokens": 0
          },
          "total_tokens": 21937
        },
        "quote_provenance": [
          {
            "field": "selection",
            "occurrences": [
              {
                "start": 24,
                "end": 40,
                "quote": "Handled Quantity"
              },
              {
                "start": 136,
                "end": 152,
                "quote": "Handled Quantity"
              }
            ]
          },
          {
            "field": "selection",
            "occurrences": [
              {
                "start": 169,
                "end": 173,
                "quote": "8765"
              }
            ]
          },
          {
            "field": "selection",
            "occurrences": [
              {
                "start": 202,
                "end": 206,
                "quote": "4182"
              }
            ]
          },
          {
            "field": "question_kind",
            "occurrences": [
              {
                "start": 41,
                "end": 93,
                "quote": "may be stale. Check freshness and processing history"
              }
            ]
          },
          {
            "field": "reported_figure",
            "occurrences": [
              {
                "start": 125,
                "end": 174,
                "quote": "The global Handled Quantity currently shows 8765."
              }
            ]
          },
          {
            "field": "numeral",
            "occurrences": [
              {
                "start": 175,
                "end": 206,
                "quote": "Internal request reference 4182"
              }
            ]
          },
          {
            "field": "measure",
            "occurrences": [
              {
                "start": 24,
                "end": 40,
                "quote": "Handled Quantity"
              },
              {
                "start": 136,
                "end": 152,
                "quote": "Handled Quantity"
              }
            ]
          }
        ]
      },
      "status": "NEEDS_INPUT",
      "question": "The stated precision of the reported figure is unclear. At what precision should it be compared?"
    }
  ],
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Quantity"
        },
        {
          "start": 136,
          "end": 152,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 169,
          "end": 173,
          "quote": "8765"
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 202,
          "end": 206,
          "quote": "4182"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 41,
          "end": 93,
          "quote": "may be stale. Check freshness and processing history"
        }
      ]
    },
    {
      "field": "reported_figure",
      "occurrences": [
        {
          "start": 125,
          "end": 174,
          "quote": "The global Handled Quantity currently shows 8765."
        }
      ]
    },
    {
      "field": "numeral",
      "occurrences": [
        {
          "start": 175,
          "end": 206,
          "quote": "Internal request reference 4182"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Quantity"
        },
        {
          "start": 136,
          "end": 152,
          "quote": "Handled Quantity"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "dba46d027c183f422a2c4a0b91216ec0c8f6e6fe9b0738ddffb6af538866cc3b",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "The stated precision of the reported figure is unclear. At what precision should it be compared?",
      "evidence_id": "intake-refusal-395b43cc-1338-4ad8-a801-9719922cdbc3"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The stated precision of the reported figure is unclear. At what precision should it be compared?\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-395b43cc-1338-4ad8-a801-9719922cdbc3"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The stated precision of the reported figure is unclear. At what precision should it be compared?\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-395b43cc-1338-4ad8-a801-9719922cdbc3"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4098,
    "output": [
      {
        "id": "fc_003ce9395a91b3bd016ac6fbd509688193ada000685a49eac1",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m5\",\"measure_id\":\"m5v1\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Handled Quantity\"}},{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Handled Quantity\"}},{\"role\":\"MENTION\",\"source\":{\"quote\":\"8765\"}},{\"role\":\"MENTION\",\"source\":{\"quote\":\"4182\"}}],\"question_kind\":{\"kind\":\"FRESHNESS\",\"source\":{\"quote\":\"may be stale. Check freshness and processing history\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[{\"role\":\"FIGURE\",\"quote\":\"8765\"},{\"role\":\"OTHER\",\"quote\":\"4182\"}],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_K5onZ7GVvxoELglHGHeLyL7E",
        "name": "resolve_business_question"
      }
    ]
  },
  {
    "ordinal": 8195,
    "output": [
      {
        "id": "fc_06593d353bcd67ca016ac6fbe233a88190899d156e3e68f9f2",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Handled Quantity\"}},{\"role\":\"MENTION\",\"source\":{\"quote\":\"8765\"}},{\"role\":\"MENTION\",\"source\":{\"quote\":\"4182\"}}],\"question_kind\":{\"kind\":\"FRESHNESS\",\"source\":{\"quote\":\"may be stale. Check freshness and processing history\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[{\"role\":\"FIGURE\",\"quote\":\"The global Handled Quantity currently shows 8765.\"},{\"role\":\"OTHER\",\"quote\":\"Internal request reference 4182\"}],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_5hgiIilBgiHYqYCsrNYmbcUd",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4097,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  },
  {
    "ordinal": 8194,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-E-noisy

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "e54a34bc-2cf3-413d-bef6-192a1af3708b",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Forwarded warehouse help request\nFrom: shift supervisor\nSubject: E metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations",
    "request_key": "round-ten-b-declared-family-E-noisy",
    "parent_id": null
  },
  "text": "Forwarded warehouse help request\nFrom: shift supervisor\nSubject: E metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791425553.1696074,
  "expires": 1791426453.170998,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 156,
          "end": 160,
          "quote": "7321"
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 216,
          "end": 232,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 216,
          "end": 285,
          "quote": "Handled Quantity may be stale. Check freshness and processing history"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 216,
          "end": 232,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 192,
          "end": 215,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 192,
          "end": 215,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "e9bbe527f4c654ca4dc6ffc0fe2e7b0f02a101b23da98f871aeb6ac3afd33a8f",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-e54a34bc-2cf3-413d-bef6-192a1af3708b"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Forwarded warehouse help request From: shift supervisor Subject: E metric follow-up Please ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure. Inventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied. Previous email: we need evidence and its limits, not a guess. Regards, operations\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-e54a34bc-2cf3-413d-bef6-192a1af3708b"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Forwarded warehouse help request\nFrom: shift supervisor\nSubject: E metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-e54a34bc-2cf3-413d-bef6-192a1af3708b"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4100,
    "output": [
      {
        "id": "fc_00346daaddd79e0d016ac6fc1a5f848194aa16edae4153fe59",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[{\"role\":\"MENTION\",\"source\":{\"quote\":\"7321\"}},{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Handled Quantity\"}}],\"question_kind\":{\"kind\":\"FRESHNESS\",\"source\":{\"quote\":\"Handled Quantity may be stale. Check freshness and processing history\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_eDpoj89UlVkZIFNEAhO3vwv8",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4099,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-E-terse

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "3ae2dcb7-de0a-4796-9066-4c5d6b1931f0",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied.",
    "request_key": "round-ten-b-declared-family-E-terse",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791425600.9030454,
  "expires": 1791426500.9048083,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 41,
          "end": 93,
          "quote": "may be stale. Check freshness and processing history"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "fe0002e1c112f66da1615bb74eceafcf6f3028cf0bae239191412886e2bcbc4d",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-3ae2dcb7-de0a-4796-9066-4c5d6b1931f0"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-3ae2dcb7-de0a-4796-9066-4c5d6b1931f0"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Check freshness and processing history; no freshness SLA is supplied.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-3ae2dcb7-de0a-4796-9066-4c5d6b1931f0"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4101,
    "output": [
      {
        "id": "fc_01582edc2fc403c9016ac6fc4cb4dc81938ebc53448b2332ff",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"FRESHNESS\",\"source\":{\"quote\":\"may be stale. Check freshness and processing history\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_RzjX9tL2ZK7mKzdknxu4WF54",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4100,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-E-typo

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "8e96d1a6-1c4d-4f2a-9991-f50063e2d082",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Handled Qunatity may be stale. chk freshness and processing history; no freshness SLA is supplied. thx, need the actual scope too",
    "request_key": "round-ten-b-declared-family-E-typo",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Handled Qunatity may be stale. chk freshness and processing history; no freshness SLA is supplied. thx, need the actual scope too",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791425649.4194083,
  "expires": 1791426549.4203298,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 41,
          "end": 121,
          "quote": "may be stale. chk freshness and processing history; no freshness SLA is supplied"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Qunatity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "0dae3506a082bb05b01f5d2444192e4216ac65deaa7a85a899d9a4822c28196c",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-8e96d1a6-1c4d-4f2a-9991-f50063e2d082"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Qunatity may be stale. chk freshness and processing history; no freshness SLA is supplied. thx, need the actual scope too\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-8e96d1a6-1c4d-4f2a-9991-f50063e2d082"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Qunatity may be stale. chk freshness and processing history; no freshness SLA is supplied. thx, need the actual scope too\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-8e96d1a6-1c4d-4f2a-9991-f50063e2d082"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4102,
    "output": [
      {
        "id": "fc_0bdbd65b7948cad4016ac6fc7b11808193a575d26ab97ee65d",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v3\",\"metric_quote\":\"Handled Qunatity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"FRESHNESS\",\"source\":{\"quote\":\"may be stale. chk freshness and processing history; no freshness SLA is supplied\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_pM2wMbgvs7XVf3wIPdC6KrEf",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4101,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-F-noisy

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.

Recorded intake output, verbatim JSON:

```json
{
  "id": "99deb672-6f30-4c49-ae11-516b2797df1b",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Forwarded warehouse help request\nFrom: shift supervisor\nSubject: F metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1 Extended Value seems overstated. Explain its global total and any supported source mechanism.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations",
    "request_key": "round-ten-b-declared-family-F-noisy",
    "parent_id": null
  },
  "text": "Forwarded warehouse help request\nFrom: shift supervisor\nSubject: F metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1 Extended Value seems overstated. Explain its global total and any supported source mechanism.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791425696.196147,
  "expires": 1791426596.1971362,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [
    {
      "attempt": 1,
      "event": "MISMATCH_SHAPE_REQUIRED",
      "reservation_key": "resolve",
      "metadata": {
        "response_id": "resp_032357c4ba16e03f016ac6fca964608193bdd7fccdddf713a4",
        "model": "investigator-quality-54",
        "usage": {
          "input_tokens": 21686,
          "input_tokens_details": {
            "cache_write_tokens": 0,
            "cached_tokens": 21376
          },
          "output_tokens": 118,
          "output_tokens_details": {
            "reasoning_tokens": 0
          },
          "total_tokens": 21804
        },
        "quote_provenance": [
          {
            "field": "question_kind",
            "occurrences": [
              {
                "start": 249,
                "end": 309,
                "quote": "Explain its global total and any supported source mechanism."
              }
            ]
          },
          {
            "field": "measure",
            "occurrences": [
              {
                "start": 216,
                "end": 230,
                "quote": "Extended Value"
              }
            ]
          }
        ]
      },
      "rule": "MISMATCH_SHAPE_REQUIRED"
    },
    {
      "attempt": 2,
      "event": "INTAKE_RULE_RETRY",
      "reservation_key": "intake-rule-retry",
      "metadata": {
        "response_id": "resp_07c32c64490f6c16016ac6fcb481108196a12c39e862a8ed22",
        "model": "investigator-quality-54",
        "usage": {
          "input_tokens": 21776,
          "input_tokens_details": {
            "cache_write_tokens": 0,
            "cached_tokens": 3712
          },
          "output_tokens": 126,
          "output_tokens_details": {
            "reasoning_tokens": 0
          },
          "total_tokens": 21902
        },
        "quote_provenance": [
          {
            "field": "question_kind",
            "occurrences": [
              {
                "start": 231,
                "end": 247,
                "quote": "seems overstated"
              }
            ]
          },
          {
            "field": "measure",
            "occurrences": [
              {
                "start": 192,
                "end": 248,
                "quote": "Inventory Health e1b8e1 Extended Value seems overstated."
              }
            ]
          },
          {
            "field": "report",
            "occurrences": [
              {
                "start": 192,
                "end": 215,
                "quote": "Inventory Health e1b8e1"
              }
            ]
          },
          {
            "field": "report",
            "occurrences": [
              {
                "start": 192,
                "end": 215,
                "quote": "Inventory Health e1b8e1"
              }
            ]
          }
        ]
      },
      "status": "HELD",
      "question": null
    }
  ],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.",
  "candidate_visuals": [
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Inventory Health",
        "Movement Value"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 231,
          "end": 247,
          "quote": "seems overstated"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 192,
          "end": 248,
          "quote": "Inventory Health e1b8e1 Extended Value seems overstated."
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 192,
          "end": 215,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 192,
          "end": 215,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "e44f9de512acce39fc44f2ed45311671a85461d599e9f4257e8798319c981d84",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.",
      "evidence_id": "intake-refusal-99deb672-6f30-4c49-ae11-516b2797df1b"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Forwarded warehouse help request From: shift supervisor Subject: F metric follow-up Please ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure. Inventory Health e1b8e1 Extended Value seems overstated. Explain its global total and any supported source mechanism. Previous email: we need evidence and its limits, not a guess. Regards, operations\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-99deb672-6f30-4c49-ae11-516b2797df1b"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Forwarded warehouse help request\nFrom: shift supervisor\nSubject: F metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1 Extended Value seems overstated. Explain its global total and any supported source mechanism.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-99deb672-6f30-4c49-ae11-516b2797df1b"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4103,
    "output": [
      {
        "id": "fc_032357c4ba16e03f016ac6fcab1a008193a321033167df1144",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v2\",\"metric_quote\":\"Extended Value\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"TRANSFORMATION_MECHANISM\",\"source\":{\"quote\":\"Explain its global total and any supported source mechanism.\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_dcFhAwaYdimjsb7JdgOFoP90",
        "name": "resolve_business_question"
      }
    ]
  },
  {
    "ordinal": 8205,
    "output": [
      {
        "id": "fc_07c32c64490f6c16016ac6fcb5f718819699412688d96bf405",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v2\",\"metric_quote\":\"Inventory Health e1b8e1 Extended Value seems overstated.\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"FIGURE_DIFFERENCE\",\"source\":{\"quote\":\"seems overstated\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"MISMATCH_COMPLAINT:VERTICAL\"}",
        "call_id": "call_Zh4sjcBe7Dz77sFLDn1EXPQu",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4102,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  },
  {
    "ordinal": 8204,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-F-terse

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.

Recorded intake output, verbatim JSON:

```json
{
  "id": "5d82d2ec-b1aa-4681-bbc2-dac26531bfbf",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Extended Value seems overstated. Explain its global total and any supported source mechanism.",
    "request_key": "round-ten-b-declared-family-F-terse",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Extended Value seems overstated. Explain its global total and any supported source mechanism.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791425752.52287,
  "expires": 1791426652.5238054,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [
    {
      "attempt": 1,
      "event": "MISMATCH_SHAPE_REQUIRED",
      "reservation_key": "resolve",
      "metadata": {
        "response_id": "resp_04f1f0834e79d0cc016ac6fce1081881969e77c13ab28d2acb",
        "model": "investigator-quality-54",
        "usage": {
          "input_tokens": 21626,
          "input_tokens_details": {
            "cache_write_tokens": 0,
            "cached_tokens": 21248
          },
          "output_tokens": 112,
          "output_tokens_details": {
            "reasoning_tokens": 0
          },
          "total_tokens": 21738
        },
        "quote_provenance": [
          {
            "field": "question_kind",
            "occurrences": [
              {
                "start": 86,
                "end": 116,
                "quote": "any supported source mechanism"
              }
            ]
          },
          {
            "field": "measure",
            "occurrences": [
              {
                "start": 24,
                "end": 38,
                "quote": "Extended Value"
              }
            ]
          }
        ]
      },
      "rule": "MISMATCH_SHAPE_REQUIRED"
    },
    {
      "attempt": 2,
      "event": "INTAKE_RULE_RETRY",
      "reservation_key": "intake-rule-retry",
      "metadata": {
        "response_id": "resp_056f540c908bf6f9016ac6fcec35f08190bdd236e7cac8abb7",
        "model": "investigator-quality-54",
        "usage": {
          "input_tokens": 21716,
          "input_tokens_details": {
            "cache_write_tokens": 0,
            "cached_tokens": 21376
          },
          "output_tokens": 115,
          "output_tokens_details": {
            "reasoning_tokens": 0
          },
          "total_tokens": 21831
        },
        "quote_provenance": [
          {
            "field": "question_kind",
            "occurrences": [
              {
                "start": 86,
                "end": 116,
                "quote": "any supported source mechanism"
              }
            ]
          },
          {
            "field": "measure",
            "occurrences": [
              {
                "start": 24,
                "end": 38,
                "quote": "Extended Value"
              }
            ]
          },
          {
            "field": "report",
            "occurrences": [
              {
                "start": 0,
                "end": 23,
                "quote": "Inventory Health e1b8e1"
              }
            ]
          },
          {
            "field": "report",
            "occurrences": [
              {
                "start": 0,
                "end": 23,
                "quote": "Inventory Health e1b8e1"
              }
            ]
          }
        ]
      },
      "status": "HELD",
      "question": null
    }
  ],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.",
  "candidate_visuals": [
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Inventory Health",
        "Movement Value"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 86,
          "end": 116,
          "quote": "any supported source mechanism"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 38,
          "quote": "Extended Value"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "a8838abde5443b47de95f161ffe0eebcd000f1ed8cafc5d478905497316d93ce",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.",
      "evidence_id": "intake-refusal-5d82d2ec-b1aa-4681-bbc2-dac26531bfbf"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Extended Value seems overstated. Explain its global total and any supported source mechanism.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-5d82d2ec-b1aa-4681-bbc2-dac26531bfbf"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Extended Value seems overstated. Explain its global total and any supported source mechanism.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-5d82d2ec-b1aa-4681-bbc2-dac26531bfbf"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4105,
    "output": [
      {
        "id": "fc_04f1f0834e79d0cc016ac6fce22e04819680cada64de9e3a64",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v2\",\"metric_quote\":\"Extended Value\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"TRANSFORMATION_MECHANISM\",\"source\":{\"quote\":\"any supported source mechanism\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_NwbXmFTw4JlpF4ccsSxUCkEn",
        "name": "resolve_business_question"
      }
    ]
  },
  {
    "ordinal": 8209,
    "output": [
      {
        "id": "fc_056f540c908bf6f9016ac6fced32d481909fbf6dfec92cb888",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v2\",\"metric_quote\":\"Extended Value\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"TRANSFORMATION_MECHANISM\",\"source\":{\"quote\":\"any supported source mechanism\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"MISMATCH_COMPLAINT:VERTICAL\"}",
        "call_id": "call_uQcRPIHxvOCVJsitQSeSSeot",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4104,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  },
  {
    "ordinal": 8208,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-F-typo

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.

Recorded intake output, verbatim JSON:

```json
{
  "id": "0f40e8cd-dcf2-49e4-ac00-aaf4e7511477",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Extended Value seems overstated. pls explain its global total and any supported source mechanism. thx, need the actual scope too",
    "request_key": "round-ten-b-declared-family-F-typo",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Extended Value seems overstated. pls explain its global total and any supported source mechanism. thx, need the actual scope too",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791425805.8361242,
  "expires": 1791426705.8370152,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [
    {
      "attempt": 1,
      "event": "MISMATCH_SHAPE_REQUIRED",
      "reservation_key": "resolve",
      "metadata": {
        "response_id": "resp_02f5de7f298287fb016ac6fd1443e0819391f789f282095a53",
        "model": "investigator-quality-54",
        "usage": {
          "input_tokens": 21636,
          "input_tokens_details": {
            "cache_write_tokens": 0,
            "cached_tokens": 21376
          },
          "output_tokens": 112,
          "output_tokens_details": {
            "reasoning_tokens": 0
          },
          "total_tokens": 21748
        },
        "quote_provenance": [
          {
            "field": "question_kind",
            "occurrences": [
              {
                "start": 90,
                "end": 120,
                "quote": "any supported source mechanism"
              }
            ]
          },
          {
            "field": "measure",
            "occurrences": [
              {
                "start": 24,
                "end": 38,
                "quote": "Extended Value"
              }
            ]
          }
        ]
      },
      "rule": "MISMATCH_SHAPE_REQUIRED"
    },
    {
      "attempt": 2,
      "event": "INTAKE_RULE_RETRY",
      "reservation_key": "intake-rule-retry",
      "metadata": {
        "response_id": "resp_08374e495d6e5c3e016ac6fd1e0fd88195af29274e931387a5",
        "model": "investigator-quality-54",
        "usage": {
          "input_tokens": 21726,
          "input_tokens_details": {
            "cache_write_tokens": 0,
            "cached_tokens": 21376
          },
          "output_tokens": 116,
          "output_tokens_details": {
            "reasoning_tokens": 0
          },
          "total_tokens": 21842
        },
        "quote_provenance": [
          {
            "field": "question_kind",
            "occurrences": [
              {
                "start": 24,
                "end": 55,
                "quote": "Extended Value seems overstated"
              }
            ]
          },
          {
            "field": "measure",
            "occurrences": [
              {
                "start": 24,
                "end": 38,
                "quote": "Extended Value"
              }
            ]
          },
          {
            "field": "report",
            "occurrences": [
              {
                "start": 0,
                "end": 23,
                "quote": "Inventory Health e1b8e1"
              }
            ]
          },
          {
            "field": "report",
            "occurrences": [
              {
                "start": 0,
                "end": 23,
                "quote": "Inventory Health e1b8e1"
              }
            ]
          }
        ]
      },
      "status": "HELD",
      "question": null
    }
  ],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.",
  "candidate_visuals": [
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Inventory Health",
        "Movement Value"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 24,
          "end": 55,
          "quote": "Extended Value seems overstated"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 38,
          "quote": "Extended Value"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "176c807527d526dedb4f480188d9eb2a833b6d31e637cc6e123a2abfa38cb153",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.",
      "evidence_id": "intake-refusal-0f40e8cd-dcf2-49e4-ac00-aaf4e7511477"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Extended Value seems overstated. pls explain its global total and any supported source mechanism. thx, need the actual scope too\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-0f40e8cd-dcf2-49e4-ac00-aaf4e7511477"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Extended Value seems overstated. pls explain its global total and any supported source mechanism. thx, need the actual scope too\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Value.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-0f40e8cd-dcf2-49e4-ac00-aaf4e7511477"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4107,
    "output": [
      {
        "id": "fc_02f5de7f298287fb016ac6fd1590408193bb1a36b9b151cd86",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v2\",\"metric_quote\":\"Extended Value\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"TRANSFORMATION_MECHANISM\",\"source\":{\"quote\":\"any supported source mechanism\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_WJi6sIdqF7JaQBz2o4lhFEPB",
        "name": "resolve_business_question"
      }
    ]
  },
  {
    "ordinal": 8213,
    "output": [
      {
        "id": "fc_08374e495d6e5c3e016ac6fd1f9ef4819594cadb4e150339e7",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v2\",\"metric_quote\":\"Extended Value\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"FIGURE_DIFFERENCE\",\"source\":{\"quote\":\"Extended Value seems overstated\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"MISMATCH_COMPLAINT:VERTICAL\"}",
        "call_id": "call_jWwTmNgbsjs24Xg8RViawvEY",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4106,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  },
  {
    "ordinal": 8212,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-G-mention

Exact refusal/question: The stated precision of the reported figure is unclear. At what precision should it be compared?

Recorded intake output, verbatim JSON:

```json
{
  "id": "b904fb45-2578-4715-8349-c71c7b6cfb5d",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.",
    "request_key": "round-ten-b-declared-family-G-mention",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.",
  "turn": 1,
  "status": "NEEDS_INPUT",
  "proposal": null,
  "question": "The stated precision of the reported figure is unclear. At what precision should it be compared?",
  "error": null,
  "created": 1791425870.4961882,
  "expires": 1791426770.49757,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Quantity"
        },
        {
          "start": 185,
          "end": 201,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 218,
          "end": 222,
          "quote": "8765"
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 251,
          "end": 255,
          "quote": "4182"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 41,
          "end": 127,
          "quote": "may contain incorrect source entries. Check source movements and inventory adjustments"
        }
      ]
    },
    {
      "field": "reported_figure",
      "occurrences": [
        {
          "start": 174,
          "end": 223,
          "quote": "The global Handled Quantity currently shows 8765."
        }
      ]
    },
    {
      "field": "numeral",
      "occurrences": [
        {
          "start": 224,
          "end": 255,
          "quote": "Internal request reference 4182"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Quantity"
        },
        {
          "start": 185,
          "end": 201,
          "quote": "Handled Quantity"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "fd7373225ac855b0969582b09eb9861795bf3aab2e877d80c69c5caf8f4ffcb5",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "The stated precision of the reported figure is unclear. At what precision should it be compared?",
      "evidence_id": "intake-refusal-b904fb45-2578-4715-8349-c71c7b6cfb5d"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The stated precision of the reported figure is unclear. At what precision should it be compared?\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-b904fb45-2578-4715-8349-c71c7b6cfb5d"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The stated precision of the reported figure is unclear. At what precision should it be compared?\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-b904fb45-2578-4715-8349-c71c7b6cfb5d"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4109,
    "output": [
      {
        "id": "fc_0cb9c6cd0c614346016ac6fd59428481979ee70487e5f24511",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m5\",\"measure_id\":\"m5v1\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Handled Quantity\"}},{\"role\":\"MENTION\",\"source\":{\"quote\":\"8765\"}},{\"role\":\"MENTION\",\"source\":{\"quote\":\"4182\"}}],\"question_kind\":{\"kind\":\"SOURCE_CORRECTNESS\",\"source\":{\"quote\":\"may contain incorrect source entries. Check source movements and inventory adjustments\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[{\"role\":\"FIGURE\",\"quote\":\"The global Handled Quantity currently shows 8765.\"},{\"role\":\"OTHER\",\"quote\":\"Internal request reference 4182\"}],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_hdhfqtfizKx5IbnklRfhyilx",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4108,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-G-noisy

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "788b2938-ef57-466c-96eb-e1a58c2ebf00",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Forwarded warehouse help request\nFrom: shift supervisor\nSubject: G metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations",
    "request_key": "round-ten-b-declared-family-G-noisy",
    "parent_id": null
  },
  "text": "Forwarded warehouse help request\nFrom: shift supervisor\nSubject: G metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791425924.0828998,
  "expires": 1791426824.0840123,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 216,
          "end": 232,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 233,
          "end": 319,
          "quote": "may contain incorrect source entries. Check source movements and inventory adjustments"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 192,
          "end": 270,
          "quote": "Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries."
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 192,
          "end": 215,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 192,
          "end": 215,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "71568fc3890d03f15aedc989abec56752a23fab5ed0e7f104930fb0c9acfae10",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-788b2938-ef57-466c-96eb-e1a58c2ebf00"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Forwarded warehouse help request From: shift supervisor Subject: G metric follow-up Please ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure. Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent. Previous email: we need evidence and its limits, not a guess. Regards, operations\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-788b2938-ef57-466c-96eb-e1a58c2ebf00"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Forwarded warehouse help request\nFrom: shift supervisor\nSubject: G metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-788b2938-ef57-466c-96eb-e1a58c2ebf00"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4110,
    "output": [
      {
        "id": "fc_0616c060e79a3a46016ac6fd8d0414819685698bc52e256225",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v3\",\"metric_quote\":\"Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries.\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Handled Quantity\"}}],\"question_kind\":{\"kind\":\"SOURCE_CORRECTNESS\",\"source\":{\"quote\":\"may contain incorrect source entries. Check source movements and inventory adjustments\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_dF6xa1hxleEVS4dE1mm7FAt3",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4109,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-G-terse

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "cbeb3848-84e1-4760-ba43-bcfb9c48fe2a",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent.",
    "request_key": "round-ten-b-declared-family-G-terse",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791425975.3059268,
  "expires": 1791426875.3068736,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 41,
          "end": 173,
          "quote": "may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent."
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "97d5406675b76799186c4630168a9ffa2bb41504fce4a49f042f2f1d686c6f2c",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-cbeb3848-84e1-4760-ba43-bcfb9c48fe2a"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-cbeb3848-84e1-4760-ba43-bcfb9c48fe2a"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-cbeb3848-84e1-4760-ba43-bcfb9c48fe2a"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4111,
    "output": [
      {
        "id": "fc_0ec9fad1e480b0a3016ac6fdbf8ca881969e98700722ee803b",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"SOURCE_CORRECTNESS\",\"source\":{\"quote\":\"may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent.\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_mQ52l9yxz5yPAGV4crXdAwFj",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4110,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-G-typo

Exact refusal/question: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.

Recorded intake output, verbatim JSON:

```json
{
  "id": "78393984-30d6-4f28-9f13-8ed00940d060",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Handled Qunatity may contain incorrect source entries. chk source movements and inventory adjustments, without assuming adjustment business intent. thx, need the actual scope too",
    "request_key": "round-ten-b-declared-family-G-typo",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Handled Qunatity may contain incorrect source entries. chk source movements and inventory adjustments, without assuming adjustment business intent. thx, need the actual scope too",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "TARGET_UNRESOLVED",
  "created": 1791426020.2252429,
  "expires": 1791426920.226172,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
  "candidate_visuals": [
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Inventory Health",
        "Movement Units"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity"
      ],
      "grouping_columns": [],
      "unsupported": null
    },
    {
      "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json",
      "report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497",
      "names": [
        "Activity by warehouse",
        "Inventory Health"
      ],
      "measure_ids": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction",
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance"
      ],
      "grouping_columns": [
        "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name"
      ],
      "unsupported": null
    }
  ],
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 41,
          "end": 170,
          "quote": "may contain incorrect source entries. chk source movements and inventory adjustments, without assuming adjustment business intent"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Qunatity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "54799b3e7b04750dcaf62f4187c1911dd953710d8742fd7e46d5822bd5d87f5e",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.",
      "evidence_id": "intake-refusal-78393984-30d6-4f28-9f13-8ed00940d060"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Qunatity may contain incorrect source entries. chk source movements and inventory adjustments, without assuming adjustment business intent. thx, need the actual scope too\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The required check could not be established. Its detailed blocker is retained in the technical explanation.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-78393984-30d6-4f28-9f13-8ed00940d060"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Qunatity may contain incorrect source entries. chk source movements and inventory adjustments, without assuming adjustment business intent. thx, need the actual scope too\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: TARGET_UNRESOLVED: A target visual must be named unambiguously. Candidate visuals: Activity by warehouse, Inventory Health, Movement Units.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-78393984-30d6-4f28-9f13-8ed00940d060"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4112,
    "output": [
      {
        "id": "fc_0e4ea4b27eb21dfb016ac6fded90308196a9ee17ea4ba0d6fe",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v3\",\"metric_quote\":\"Handled Qunatity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"SOURCE_CORRECTNESS\",\"source\":{\"quote\":\"may contain incorrect source entries. chk source movements and inventory adjustments, without assuming adjustment business intent\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_y0eeXR8Qa3wL2FaEz8fspJkm",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4111,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-H-noisy

Exact refusal/question: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.

Recorded intake output, verbatim JSON:

```json
{
  "id": "b7f35e47-c332-4122-a52b-1d8a1fbb2478",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Forwarded warehouse help request\nFrom: shift supervisor\nSubject: H metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nWarehouse Performance e1b8e1 Inbound Quantity differs from Outbound Quantity. Explain their definitions and what business intent stays unknown.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations",
    "request_key": "round-ten-b-declared-family-H-noisy",
    "parent_id": null
  },
  "text": "Forwarded warehouse help request\nFrom: shift supervisor\nSubject: H metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nWarehouse Performance e1b8e1 Inbound Quantity differs from Outbound Quantity. Explain their definitions and what business intent stays unknown.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "UNIMPLEMENTED_ROUTE",
  "created": 1791426072.4259353,
  "expires": 1791426972.427215,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [
    {
      "attempt": 1,
      "event": "MISMATCH_SHAPE_REQUIRED",
      "reservation_key": "resolve",
      "metadata": {
        "response_id": "resp_056ce4aba90d5e79016ac6fe1fede0819794541b5e669c9487",
        "model": "investigator-quality-54",
        "usage": {
          "input_tokens": 21689,
          "input_tokens_details": {
            "cache_write_tokens": 0,
            "cached_tokens": 21376
          },
          "output_tokens": 140,
          "output_tokens_details": {
            "reasoning_tokens": 0
          },
          "total_tokens": 21829
        },
        "quote_provenance": [
          {
            "field": "question_kind",
            "occurrences": [
              {
                "start": 270,
                "end": 335,
                "quote": "Explain their definitions and what business intent stays unknown."
              }
            ]
          },
          {
            "field": "measure",
            "occurrences": [
              {
                "start": 221,
                "end": 237,
                "quote": "Inbound Quantity"
              }
            ]
          }
        ]
      },
      "rule": "MISMATCH_SHAPE_REQUIRED"
    },
    {
      "attempt": 2,
      "event": "INTAKE_RULE_RETRY",
      "reservation_key": "intake-rule-retry",
      "metadata": {
        "response_id": "resp_00466b103ae89c07016ac6fe2a17d4819488d45b7006d06a8a",
        "model": "investigator-quality-54",
        "usage": {
          "input_tokens": 21779,
          "input_tokens_details": {
            "cache_write_tokens": 0,
            "cached_tokens": 21376
          },
          "output_tokens": 121,
          "output_tokens_details": {
            "reasoning_tokens": 0
          },
          "total_tokens": 21900
        },
        "quote_provenance": [
          {
            "field": "question_kind",
            "occurrences": [
              {
                "start": 270,
                "end": 335,
                "quote": "Explain their definitions and what business intent stays unknown."
              }
            ]
          },
          {
            "field": "measure",
            "occurrences": [
              {
                "start": 221,
                "end": 237,
                "quote": "Inbound Quantity"
              }
            ]
          },
          {
            "field": "report",
            "occurrences": [
              {
                "start": 192,
                "end": 220,
                "quote": "Warehouse Performance e1b8e1"
              }
            ]
          }
        ]
      },
      "status": "HELD",
      "question": null
    }
  ],
  "refusal_reason": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
  "quote_provenance": [
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 270,
          "end": 335,
          "quote": "Explain their definitions and what business intent stays unknown."
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 221,
          "end": 237,
          "quote": "Inbound Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 192,
          "end": 220,
          "quote": "Warehouse Performance e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "b6af0ea0b25bfaf194eee4f3eefce0437c7447c58640b6480f0ef864919ee884",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
      "evidence_id": "intake-refusal-b7f35e47-c332-4122-a52b-1d8a1fbb2478"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Forwarded warehouse help request From: shift supervisor Subject: H metric follow-up Please ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure. Warehouse Performance e1b8e1 Inbound Quantity differs from Outbound Quantity. Explain their definitions and what business intent stays unknown. Previous email: we need evidence and its limits, not a guess. Regards, operations\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-b7f35e47-c332-4122-a52b-1d8a1fbb2478"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Forwarded warehouse help request\nFrom: shift supervisor\nSubject: H metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nWarehouse Performance e1b8e1 Inbound Quantity differs from Outbound Quantity. Explain their definitions and what business intent stays unknown.\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-b7f35e47-c332-4122-a52b-1d8a1fbb2478"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4113,
    "output": [
      {
        "id": "fc_056ce4aba90d5e79016ac6fe211c548197a7036a22097c9428",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v5\",\"metric_quote\":\"Inbound Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":{\"source\":{\"quote\":\"Warehouse Performance e1b8e1\"},\"mode\":\"UNGROUPED\",\"mode_source\":null},\"value_mentions\":[],\"question_kind\":{\"kind\":\"METRIC_COMPONENTS\",\"source\":{\"quote\":\"Explain their definitions and what business intent stays unknown.\"}},\"target_request\":null,\"report_quote\":\"Warehouse Performance e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_Uz941d1ZrlcNBo3zgH40nwGj",
        "name": "resolve_business_question"
      }
    ]
  },
  {
    "ordinal": 8225,
    "output": [
      {
        "id": "fc_00466b103ae89c07016ac6fe2b083481948c84c602f3a5a1c9",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v5\",\"metric_quote\":\"Inbound Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":{\"kind\":\"BUSINESS_MEANING\",\"source\":{\"quote\":\"Explain their definitions and what business intent stays unknown.\"}},\"target_request\":null,\"report_quote\":\"Warehouse Performance e1b8e1\",\"reported_candidates\":[],\"triage\":\"MISMATCH_COMPLAINT:VERTICAL\"}",
        "call_id": "call_seurAlXevOxGsvF94nf7Hgfu",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4112,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  },
  {
    "ordinal": 8224,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-H-terse

Exact refusal/question: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.

Recorded intake output, verbatim JSON:

```json
{
  "id": "58e4d64f-bdba-4444-b4ab-f6c1d845abbe",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Warehouse Performance e1b8e1 Inbound Quantity differs from Outbound Quantity. Explain their definitions and what business intent stays unknown.",
    "request_key": "round-ten-b-declared-family-H-terse",
    "parent_id": null
  },
  "text": "Warehouse Performance e1b8e1 Inbound Quantity differs from Outbound Quantity. Explain their definitions and what business intent stays unknown.",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "UNIMPLEMENTED_ROUTE",
  "created": 1791426129.1248055,
  "expires": 1791427029.1262913,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [
    {
      "attempt": 1,
      "event": "MISMATCH_SHAPE_REQUIRED",
      "reservation_key": "resolve",
      "metadata": {
        "response_id": "resp_0bd2b3ffa96e89b4016ac6fe5868d4819381838be5127ac7c9",
        "model": "investigator-quality-54",
        "usage": {
          "input_tokens": 21629,
          "input_tokens_details": {
            "cache_write_tokens": 0,
            "cached_tokens": 21248
          },
          "output_tokens": 136,
          "output_tokens_details": {
            "reasoning_tokens": 0
          },
          "total_tokens": 21765
        },
        "quote_provenance": [
          {
            "field": "selection",
            "occurrences": [
              {
                "start": 29,
                "end": 45,
                "quote": "Inbound Quantity"
              }
            ]
          },
          {
            "field": "selection",
            "occurrences": [
              {
                "start": 59,
                "end": 76,
                "quote": "Outbound Quantity"
              }
            ]
          },
          {
            "field": "question_kind",
            "occurrences": [
              {
                "start": 78,
                "end": 103,
                "quote": "Explain their definitions"
              }
            ]
          },
          {
            "field": "measure",
            "occurrences": [
              {
                "start": 29,
                "end": 45,
                "quote": "Inbound Quantity"
              }
            ]
          }
        ]
      },
      "rule": "MISMATCH_SHAPE_REQUIRED"
    },
    {
      "attempt": 2,
      "event": "INTAKE_RULE_RETRY",
      "reservation_key": "intake-rule-retry",
      "metadata": {
        "response_id": "resp_074f765f195d4798016ac6fe62d8748195804c8af422168b3b",
        "model": "investigator-quality-54",
        "usage": {
          "input_tokens": 21719,
          "input_tokens_details": {
            "cache_write_tokens": 0,
            "cached_tokens": 21376
          },
          "output_tokens": 147,
          "output_tokens_details": {
            "reasoning_tokens": 0
          },
          "total_tokens": 21866
        },
        "quote_provenance": [
          {
            "field": "selection",
            "occurrences": [
              {
                "start": 29,
                "end": 45,
                "quote": "Inbound Quantity"
              }
            ]
          },
          {
            "field": "selection",
            "occurrences": [
              {
                "start": 59,
                "end": 76,
                "quote": "Outbound Quantity"
              }
            ]
          },
          {
            "field": "question_kind",
            "occurrences": [
              {
                "start": 78,
                "end": 143,
                "quote": "Explain their definitions and what business intent stays unknown."
              }
            ]
          },
          {
            "field": "measure",
            "occurrences": [
              {
                "start": 29,
                "end": 45,
                "quote": "Inbound Quantity"
              }
            ]
          },
          {
            "field": "report",
            "occurrences": [
              {
                "start": 0,
                "end": 28,
                "quote": "Warehouse Performance e1b8e1"
              }
            ]
          }
        ]
      },
      "status": "HELD",
      "question": null
    }
  ],
  "refusal_reason": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 29,
          "end": 45,
          "quote": "Inbound Quantity"
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 59,
          "end": 76,
          "quote": "Outbound Quantity"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 78,
          "end": 143,
          "quote": "Explain their definitions and what business intent stays unknown."
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 29,
          "end": 45,
          "quote": "Inbound Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 28,
          "quote": "Warehouse Performance e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "78bda48f219258fd0d3113a9339014f2c86e3b01598c21810f9135274eb79ffb",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
      "evidence_id": "intake-refusal-58e4d64f-bdba-4444-b4ab-f6c1d845abbe"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Warehouse Performance e1b8e1 Inbound Quantity differs from Outbound Quantity. Explain their definitions and what business intent stays unknown.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-58e4d64f-bdba-4444-b4ab-f6c1d845abbe"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Warehouse Performance e1b8e1 Inbound Quantity differs from Outbound Quantity. Explain their definitions and what business intent stays unknown.\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-58e4d64f-bdba-4444-b4ab-f6c1d845abbe"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4115,
    "output": [
      {
        "id": "fc_0bd2b3ffa96e89b4016ac6fe59b7cc819397a729d4d45230b4",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v5\",\"metric_quote\":\"Inbound Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Inbound Quantity\"}},{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Outbound Quantity\"}}],\"question_kind\":{\"kind\":\"METRIC_COMPONENTS\",\"source\":{\"quote\":\"Explain their definitions\"}},\"target_request\":null,\"report_quote\":\"Warehouse Performance e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_ZjYiLqeZrzRMueAd5ei7H6pI",
        "name": "resolve_business_question"
      }
    ]
  },
  {
    "ordinal": 8229,
    "output": [
      {
        "id": "fc_074f765f195d4798016ac6fe642d3c8195811cb5f1db7bec40",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v5\",\"metric_quote\":\"Inbound Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Inbound Quantity\"}},{\"role\":\"SUBJECT\",\"source\":{\"quote\":\"Outbound Quantity\"}}],\"question_kind\":{\"kind\":\"BUSINESS_MEANING\",\"source\":{\"quote\":\"Explain their definitions and what business intent stays unknown.\"}},\"target_request\":null,\"report_quote\":\"Warehouse Performance e1b8e1\",\"reported_candidates\":[],\"triage\":\"MISMATCH_COMPLAINT:VERTICAL\"}",
        "call_id": "call_cRiNR5QHuzL9gENpDZ8ichUk",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4114,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  },
  {
    "ordinal": 8228,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-H-typo

Exact refusal/question: Do you want the scope for “Inbound Qunatity” or for “Outbound Qunatity”? I need one starting metric because your note asks about both but also asks for “the actual scope too”.

Recorded intake output, verbatim JSON:

```json
{
  "id": "9af6a787-1613-417b-b010-8a0fcf6ab6bf",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Warehouse Performance e1b8e1 Inbound Qunatity differs from Outbound Qunatity. pls explain their definitions and what business intent stays unknown. thx, need the actual scope too",
    "request_key": "round-ten-b-declared-family-H-typo",
    "parent_id": null
  },
  "text": "Warehouse Performance e1b8e1 Inbound Qunatity differs from Outbound Qunatity. pls explain their definitions and what business intent stays unknown. thx, need the actual scope too",
  "turn": 1,
  "status": "NEEDS_INPUT",
  "proposal": null,
  "question": "Do you want the scope for “Inbound Qunatity” or for “Outbound Qunatity”? I need one starting metric because your note asks about both but also asks for “the actual scope too”.",
  "error": null,
  "created": 1791426198.315607,
  "expires": 1791427098.3171494,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "quote_provenance": [],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "798630ac87bd2ac885ca0a01c4b3368772f0a30070283c0b67c6ae51b8882fb4",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "Do you want the scope for “Inbound Qunatity” or for “Outbound Qunatity”? I need one starting metric because your note asks about both but also asks for “the actual scope too”.",
      "evidence_id": "intake-refusal-9af6a787-1613-417b-b010-8a0fcf6ab6bf"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Warehouse Performance e1b8e1 Inbound Qunatity differs from Outbound Qunatity. pls explain their definitions and what business intent stays unknown. thx, need the actual scope too\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: Do you want the scope for “Inbound Qunatity” or for “Outbound Qunatity”? I need one starting metric because your note asks about both but also asks for “the actual scope too”.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-9af6a787-1613-417b-b010-8a0fcf6ab6bf"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Warehouse Performance e1b8e1 Inbound Qunatity differs from Outbound Qunatity. pls explain their definitions and what business intent stays unknown. thx, need the actual scope too\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: Do you want the scope for “Inbound Qunatity” or for “Outbound Qunatity”? I need one starting metric because your note asks about both but also asks for “the actual scope too”.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-9af6a787-1613-417b-b010-8a0fcf6ab6bf"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4117,
    "output": [
      {
        "id": "fc_090ee434344a5282016ac6fe9e7340819586bd8219ac487d19",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"ASK\",\"model_id\":null,\"measure_id\":null,\"metric_quote\":null,\"question\":\"Do you want the scope for “Inbound Qunatity” or for “Outbound Qunatity”? I need one starting metric because your note asks about both but also asks for “the actual scope too”.\",\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[],\"question_kind\":null,\"target_request\":null,\"report_quote\":null,\"reported_candidates\":[],\"triage\":null}",
        "call_id": "call_sqFK6KenTCCLZo9V6G3941DH",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4116,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-I-noisy

Exact refusal/question: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.

Recorded intake output, verbatim JSON:

```json
{
  "id": "7ed58e8b-43df-473f-a719-6391cc4c7e95",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Forwarded warehouse help request\nFrom: shift supervisor\nSubject: I metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1 Handled Quantity: what does adjustment reason Q49 mean, and should those adjustments affect the metric?\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations",
    "request_key": "round-ten-b-declared-family-I-noisy",
    "parent_id": null
  },
  "text": "Forwarded warehouse help request\nFrom: shift supervisor\nSubject: I metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1 Handled Quantity: what does adjustment reason Q49 mean, and should those adjustments affect the metric?\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "UNIMPLEMENTED_ROUTE",
  "created": 1791426248.6691885,
  "expires": 1791427148.6704233,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 262,
          "end": 265,
          "quote": "Q49"
        }
      ]
    },
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 156,
          "end": 160,
          "quote": "7321"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 234,
          "end": 319,
          "quote": "what does adjustment reason Q49 mean, and should those adjustments affect the metric?"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 216,
          "end": 232,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 192,
          "end": 215,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "1e5422c04adfa61caacf5936d739e580a13d20f22d8ca698d432b2771b00509b",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
      "evidence_id": "intake-refusal-7ed58e8b-43df-473f-a719-6391cc4c7e95"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Forwarded warehouse help request From: shift supervisor Subject: I metric follow-up Please ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure. Inventory Health e1b8e1 Handled Quantity: what does adjustment reason Q49 mean, and should those adjustments affect the metric? Previous email: we need evidence and its limits, not a guess. Regards, operations\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-7ed58e8b-43df-473f-a719-6391cc4c7e95"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Forwarded warehouse help request\nFrom: shift supervisor\nSubject: I metric follow-up\nPlease ignore this email footer; the workstation inventory reference is 7321, not a reported metric figure.\nInventory Health e1b8e1 Handled Quantity: what does adjustment reason Q49 mean, and should those adjustments affect the metric?\nPrevious email: we need evidence and its limits, not a guess.\nRegards, operations\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-7ed58e8b-43df-473f-a719-6391cc4c7e95"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4118,
    "output": [
      {
        "id": "fc_029690f538436b43016ac6fed1c8348193976adb561c168bb9",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m5\",\"measure_id\":\"m5v1\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[{\"role\":\"MENTION\",\"source\":{\"quote\":\"Q49\"}},{\"role\":\"MENTION\",\"source\":{\"quote\":\"7321\"}}],\"question_kind\":{\"kind\":\"BUSINESS_MEANING\",\"source\":{\"quote\":\"what does adjustment reason Q49 mean, and should those adjustments affect the metric?\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_4rltC8v2qcVKnZ3ANzPS2LTM",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4117,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-I-terse

Exact refusal/question: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.

Recorded intake output, verbatim JSON:

```json
{
  "id": "1ad3ca63-069d-45d6-a8d4-ddf9711fccdf",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Handled Quantity: what does adjustment reason Q49 mean, and should those adjustments affect the metric?",
    "request_key": "round-ten-b-declared-family-I-terse",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Handled Quantity: what does adjustment reason Q49 mean, and should those adjustments affect the metric?",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "UNIMPLEMENTED_ROUTE",
  "created": 1791426302.4276292,
  "expires": 1791427202.4285207,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 70,
          "end": 73,
          "quote": "Q49"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 42,
          "end": 127,
          "quote": "what does adjustment reason Q49 mean, and should those adjustments affect the metric?"
        }
      ]
    },
    {
      "field": "numeral",
      "occurrences": [
        {
          "start": 17,
          "end": 23,
          "quote": "e1b8e1"
        }
      ]
    },
    {
      "field": "numeral",
      "occurrences": [
        {
          "start": 70,
          "end": 73,
          "quote": "Q49"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Quantity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "59517fb178ef18c36dcc3b975470234dad7159ecfd751394d9573af06d5b638c",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
      "evidence_id": "intake-refusal-1ad3ca63-069d-45d6-a8d4-ddf9711fccdf"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity: what does adjustment reason Q49 mean, and should those adjustments affect the metric?\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-1ad3ca63-069d-45d6-a8d4-ddf9711fccdf"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Quantity: what does adjustment reason Q49 mean, and should those adjustments affect the metric?\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-1ad3ca63-069d-45d6-a8d4-ddf9711fccdf"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4119,
    "output": [
      {
        "id": "fc_05562297a0f84009016ac6ff08e8b881958547ebd8fb4c4b11",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m3\",\"measure_id\":\"m3v3\",\"metric_quote\":\"Handled Quantity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[{\"role\":\"MENTION\",\"source\":{\"quote\":\"Q49\"}}],\"question_kind\":{\"kind\":\"BUSINESS_MEANING\",\"source\":{\"quote\":\"what does adjustment reason Q49 mean, and should those adjustments affect the metric?\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[{\"role\":\"OTHER\",\"quote\":\"e1b8e1\"},{\"role\":\"OTHER\",\"quote\":\"Q49\"}],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_zO0KNJXthiRlyaOdMdBji3PB",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4118,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## disabled: family-I-typo

Exact refusal/question: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.

Recorded intake output, verbatim JSON:

```json
{
  "id": "0c63e2f7-c545-48c6-a75a-630428900c80",
  "version": "process-debugging-intake-v2",
  "request": {
    "text": "Inventory Health e1b8e1 Handled Qunatity: what does adjustment reason Q49 mean, and should those adjustments affect the metric? thx, need the actual scope too",
    "request_key": "round-ten-b-declared-family-I-typo",
    "parent_id": null
  },
  "text": "Inventory Health e1b8e1 Handled Qunatity: what does adjustment reason Q49 mean, and should those adjustments affect the metric? thx, need the actual scope too",
  "turn": 1,
  "status": "HELD",
  "proposal": null,
  "question": null,
  "error": "UNIMPLEMENTED_ROUTE",
  "created": 1791426358.758326,
  "expires": 1791427258.7615485,
  "catalog_hash": "d2b80916dde3dfdea3e0633904c3078d3df280eb689dbb7e2032eb20133968b4",
  "engine_hash": "95fb8a951991b190826ca8ff487b4c908118cb11a0cc054a748e3eaf12861eee",
  "config_hash": "6da2dbfe047e69baaa9d0854fc7eb535013a400c6f6466a49c87be415960df75",
  "planner_hash": "18ada1dd45889f519c6c9c35f0f3a3979b1088f09cf4ea388f7bc9df8441aa0c",
  "screenshot_review": null,
  "data_queries": 0,
  "requires_scope_review": true,
  "cause_verified": false,
  "resolution_attempts": [],
  "refusal_reason": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
  "quote_provenance": [
    {
      "field": "selection",
      "occurrences": [
        {
          "start": 70,
          "end": 73,
          "quote": "Q49"
        }
      ]
    },
    {
      "field": "question_kind",
      "occurrences": [
        {
          "start": 42,
          "end": 127,
          "quote": "what does adjustment reason Q49 mean, and should those adjustments affect the metric?"
        }
      ]
    },
    {
      "field": "measure",
      "occurrences": [
        {
          "start": 24,
          "end": 40,
          "quote": "Handled Qunatity"
        }
      ]
    },
    {
      "field": "report",
      "occurrences": [
        {
          "start": 0,
          "end": 23,
          "quote": "Inventory Health e1b8e1"
        }
      ]
    }
  ],
  "refusal_outputs": {
    "version": 1,
    "provenance": "DETERMINISTIC_REFUSAL_RENDERING",
    "source_hash": "29b13cf15d7baedc2d9285f66d5c3bd41708e015036958f37e67ca4fd9df0032",
    "refusal": {
      "shape": "INTAKE_REFUSED",
      "stage": "intake",
      "text": "The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.",
      "evidence_id": "intake-refusal-0c63e2f7-c545-48c6-a75a-630428900c80"
    },
    "business_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Qunatity: what does adjustment reason Q49 mean, and should those adjustments affect the metric? thx, need the actual scope too\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.",
        "evidence_ids": [
          "intake-refusal-0c63e2f7-c545-48c6-a75a-630428900c80"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    },
    "technical_output": {
      "explanation": {
        "text": "You asked: Inventory Health e1b8e1 Handled Qunatity: what does adjustment reason Q49 mean, and should those adjustments affect the metric? thx, need the actual scope too\nAnswer to your question: Not answered.\n\nThe investigation stopped during intake.\nReason: The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.\nNo explanation of the reported difference was established.\nRecommended action: Resolve the stated blocker before a new investigation.\nRoles reached in path resolution: no declared layer identities were retained.",
        "evidence_ids": [
          "intake-refusal-0c63e2f7-c545-48c6-a75a-630428900c80"
        ]
      },
      "recommended_action": "Resolve the stated blocker before a new investigation."
    }
  }
}
```

Recorded model outputs (arguments retain their original string):

```json
[
  {
    "ordinal": 4120,
    "output": [
      {
        "id": "fc_0c0f88b077a52bcf016ac6ff4707b481959913f5b93e5a3943",
        "type": "function_call",
        "status": "completed",
        "arguments": "{\"action\":\"PROPOSE\",\"model_id\":\"m5\",\"measure_id\":\"m5v1\",\"metric_quote\":\"Handled Qunatity\",\"question\":null,\"filters\":[],\"dimension_ids\":[],\"visual_request\":null,\"value_mentions\":[{\"role\":\"MENTION\",\"source\":{\"quote\":\"Q49\"}}],\"question_kind\":{\"kind\":\"BUSINESS_MEANING\",\"source\":{\"quote\":\"what does adjustment reason Q49 mean, and should those adjustments affect the metric?\"}},\"target_request\":null,\"report_quote\":\"Inventory Health e1b8e1\",\"reported_candidates\":[],\"triage\":\"BUSINESS_QUESTION:NONE\"}",
        "call_id": "call_RFugfL8RjbhJkymoaV169N75",
        "name": "resolve_business_question"
      }
    ]
  }
]
```

Complete report visual inventory sent to intake:

```json
[
  {
    "ordinal": 4119,
    "models": [
      {
        "id": "m0",
        "reports": [],
        "measures": [
          {
            "id": "m0v0",
            "name": "Base cb5bda"
          },
          {
            "id": "m0v1",
            "name": "Kept cb5bda"
          },
          {
            "id": "m0v2",
            "name": "Outer cb5bda"
          },
          {
            "id": "m0v3",
            "name": "Ratio cb5bda"
          },
          {
            "id": "m0v4",
            "name": "Replaced cb5bda"
          }
        ],
        "visuals": []
      },
      {
        "id": "m1",
        "reports": [],
        "measures": [
          {
            "id": "m1v0",
            "name": "Movement Units"
          }
        ],
        "visuals": []
      },
      {
        "id": "m2",
        "reports": [
          {
            "id": "m2r0",
            "name": "Inventory Health f28cf2"
          },
          {
            "id": "m2r1",
            "name": "Warehouse Performance f28cf2"
          }
        ],
        "measures": [
          {
            "id": "m2v0",
            "name": "Issued Units"
          },
          {
            "id": "m2v1",
            "name": "Movement Rows"
          },
          {
            "id": "m2v2",
            "name": "Movement Units"
          },
          {
            "id": "m2v3",
            "name": "Movement Value"
          },
          {
            "id": "m2v4",
            "name": "Net Movement Units"
          },
          {
            "id": "m2v5",
            "name": "Receipt Share"
          },
          {
            "id": "m2v6",
            "name": "Received Units"
          },
          {
            "id": "m2v7",
            "name": "Value Per Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v4"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m2r0",
            "target_id": "m2t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m2r0",
            "target_id": "m2t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v2",
              "m2v3",
              "m2v4",
              "m2v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m2r0",
            "target_id": "m2t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m2r0",
            "target_id": "m2t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v1"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m2v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m2c21"
            ],
            "measure_ids": [
              "m2v0",
              "m2v1",
              "m2v6",
              "m2v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m2r1",
            "target_id": "m2t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m3",
        "reports": [
          {
            "id": "m3r0",
            "name": "Declared predicate fixture 20261001"
          },
          {
            "id": "m3r1",
            "name": "Round Nine translation filters 20261007"
          },
          {
            "id": "m3r2",
            "name": "Inventory Health e1b8e1"
          },
          {
            "id": "m3r3",
            "name": "Warehouse Performance e1b8e1"
          },
          {
            "id": "m3r4",
            "name": "Round Ten Visual Variety"
          }
        ],
        "measures": [
          {
            "id": "m3v0",
            "name": "Activity Entries"
          },
          {
            "id": "m3v1",
            "name": "Average Unit Value"
          },
          {
            "id": "m3v2",
            "name": "Extended Value"
          },
          {
            "id": "m3v3",
            "name": "Handled Quantity"
          },
          {
            "id": "m3v4",
            "name": "Inbound Fraction"
          },
          {
            "id": "m3v5",
            "name": "Inbound Quantity"
          },
          {
            "id": "m3v6",
            "name": "Outbound Quantity"
          },
          {
            "id": "m3v7",
            "name": "Quantity Balance"
          },
          {
            "id": "m3v8",
            "name": "Fixture Calculated Quantity"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Unfiltered control"
            ],
            "report_id": "m3r0",
            "target_id": "m3t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r0",
            "target_id": "m3t2",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Top-N verification"
            ],
            "report_id": "m3r1",
            "target_id": "m3t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - page and slicers",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - extra visual predicate",
              "Saved predicate selections"
            ],
            "report_id": "m3r1",
            "target_id": "m3t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v7"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m3r2",
            "target_id": "m3t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v2"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m3r2",
            "target_id": "m3t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v2",
              "m3v3",
              "m3v4",
              "m3v7"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m3r2",
            "target_id": "m3t9",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v4"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m3r2",
            "target_id": "m3t10",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t11",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v6"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t12",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v1"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t13",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v5"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t14",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v0",
              "m3v1",
              "m3v5",
              "m3v6"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m3r3",
            "target_id": "m3t15",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Six active predicates"
            ],
            "report_id": "m3r4",
            "target_id": "m3t16",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c14",
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse and product matrix"
            ],
            "report_id": "m3r4",
            "target_id": "m3t17",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m3c16"
            ],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Warehouse matrix total"
            ],
            "report_id": "m3r4",
            "target_id": "m3t18",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Handled Quantity - unfiltered",
              "Saved bookmark comparison"
            ],
            "report_id": "m3r4",
            "target_id": "m3t19",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v3"
            ],
            "names": [
              "Global card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t20",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m3v8"
            ],
            "names": [
              "Calculated table card",
              "Handled Quantity - unfiltered"
            ],
            "report_id": "m3r4",
            "target_id": "m3t21",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m4",
        "reports": [
          {
            "id": "m4r0",
            "name": "Inventory Health 0fd86f"
          },
          {
            "id": "m4r1",
            "name": "Warehouse Performance 0fd86f"
          }
        ],
        "measures": [
          {
            "id": "m4v0",
            "name": "Dispatch Volume"
          },
          {
            "id": "m4v1",
            "name": "Flow Balance"
          },
          {
            "id": "m4v2",
            "name": "Flow Entry Count"
          },
          {
            "id": "m4v3",
            "name": "Inventory Valuation"
          },
          {
            "id": "m4v4",
            "name": "Processed Units"
          },
          {
            "id": "m4v5",
            "name": "Receipt Proportion"
          },
          {
            "id": "m4v6",
            "name": "Receipt Volume"
          },
          {
            "id": "m4v7",
            "name": "Value Density"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v4"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v1"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m4r0",
            "target_id": "m4t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v3"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m4r0",
            "target_id": "m4t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v1",
              "m4v3",
              "m4v4",
              "m4v5"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m4r0",
            "target_id": "m4t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v5"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m4r0",
            "target_id": "m4t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v2"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v0"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m4v6"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m4c16"
            ],
            "measure_ids": [
              "m4v0",
              "m4v2",
              "m4v6",
              "m4v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m4r1",
            "target_id": "m4t9",
            "unsupported": null
          }
        ]
      },
      {
        "id": "m5",
        "reports": [
          {
            "id": "m5r0",
            "name": "Inventory Health 23619e"
          },
          {
            "id": "m5r1",
            "name": "Warehouse Performance 23619e"
          }
        ],
        "measures": [
          {
            "id": "m5v0",
            "name": "Event Row Count"
          },
          {
            "id": "m5v1",
            "name": "Handled Quantity"
          },
          {
            "id": "m5v2",
            "name": "Inbound Fraction"
          },
          {
            "id": "m5v3",
            "name": "Inbound Quantity"
          },
          {
            "id": "m5v4",
            "name": "Outbound Quantity"
          },
          {
            "id": "m5v5",
            "name": "Quantity Balance"
          },
          {
            "id": "m5v6",
            "name": "Stock Activity Value"
          },
          {
            "id": "m5v7",
            "name": "Value per Handled Unit"
          }
        ],
        "visuals": [
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v1"
            ],
            "names": [
              "Inventory Health",
              "Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t0",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v5"
            ],
            "names": [
              "Inventory Health",
              "Net Movement Units"
            ],
            "report_id": "m5r0",
            "target_id": "m5t1",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v6"
            ],
            "names": [
              "Inventory Health",
              "Movement Value"
            ],
            "report_id": "m5r0",
            "target_id": "m5t2",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v1",
              "m5v2",
              "m5v5",
              "m5v6"
            ],
            "names": [
              "Activity by warehouse",
              "Inventory Health"
            ],
            "report_id": "m5r0",
            "target_id": "m5t3",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v2"
            ],
            "names": [
              "Inventory Health",
              "Receipt Share"
            ],
            "report_id": "m5r0",
            "target_id": "m5t4",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v0"
            ],
            "names": [
              "Movement Rows",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t5",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v4"
            ],
            "names": [
              "Issued Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t6",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v7"
            ],
            "names": [
              "Value Per Unit",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t7",
            "unsupported": null
          },
          {
            "grouping_columns": [],
            "measure_ids": [
              "m5v3"
            ],
            "names": [
              "Received Units",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t8",
            "unsupported": null
          },
          {
            "grouping_columns": [
              "m5c16"
            ],
            "measure_ids": [
              "m5v0",
              "m5v3",
              "m5v4",
              "m5v7"
            ],
            "names": [
              "Activity by warehouse",
              "Warehouse Performance"
            ],
            "report_id": "m5r1",
            "target_id": "m5t9",
            "unsupported": null
          }
        ]
      }
    ]
  }
]
```

## Section 1 conclusion and visual-variety explanation

The reading is confirmed: the old resolver required a verbatim visual name before considering uniqueness; a null visual request therefore refused even a resolvable measure/report scope. The business-kind gate refused every BUSINESS_MEANING nomination, including mixed definition/figure questions. Nineteen of the29 audited attempts hit the first rule and seven the second; two asked for precision and one for a starting metric. These are not all the same failure, and removing the naming requirement does not prove that the actual inventory has a unique match.

The six visual-variety attempts were not six target refusals. Global card, matrix total and six-predicate card all reproduced and synthesized, but their completed outcome was CONSISTENT_TO_BOUNDARY rather than the sealed NO_COMPARABLE_PATH. The two-key matrix failed intake validation after its recorded retry. Bookmark and calculated-table runs completed NO_KNOWN_PATTERN without their expected reproduction. Their original labels, receipts, outputs and expectation seals remain unchanged; no predicted failure is substituted for those observations.

## Current rule and remaining genuine ambiguity

Resolution uses the declared report, resolved measure, any named page/visual and explicitly evidenced cell mode; it cannot use a queried value to choose a different visual. A unique candidate records RESOLVED plus matched/absent fields. Multiple candidates are TARGET_AMBIGUOUS, zero TARGET_UNRESOLVED. The present neutral inventory has no query results or selection-value predicates, so these absent facts cannot be silently used as target constraints. The wrong-cell regression still refuses; aggregate ?total? does not by itself select a matrix TOTAL cell.

The unchanged original families D/E/F/G/H/I each have two eligible retained visuals without an independently stated unique primary cell constraint. For example, E's Handled Quantity occurs in both Movement Units and Activity by warehouse. The new59-text golden suite records the honest ambiguity separately from the user's nine-resolved pass condition; a matching ambiguous HOLD does not earn that pass. No original outcome expectation was changed. A claimed9/9 obtained by picking the card would violate the corrected uniqueness rule.

## CI blind spot and context cost

The existing model-step job calls check_model_scores.py, which re-scores saved responses. Its intake scorer does not execute the current prompt or regenerate a response. Historical producer replay also pins its producer, deliberately preserving old behaviour. Thus72/72 could coexist with the live over-refusal. A separate current-prompt job now invokes the actual intake procedure with all59 sealed texts, the current schema and validator, an independent full-record threshold and the nine-resolved requirement. It never falls back to cached responses. Hosted authentication is not configured: only KNOWN_DOMAIN_REPLAY_KEY exists; a new model-provider Actions secret is awaiting the human decision. No credential has been copied or scope changed. Only scores/plans, not provider bodies, are configured for upload.

Same six-model input before/after:52 visual directory entries,39 measures,97 columns,0 SQL-object entries in this view; wire payload36,815 characters both times. Instructions7,732?8,291; schema6,261?6,289. The52-entry coverage invariant is tested; native parts remain outside the model-facing snapshot. Zero provider or estate calls were made for this cost measurement.
