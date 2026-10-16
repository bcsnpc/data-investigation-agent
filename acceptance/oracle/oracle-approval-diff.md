# Oracle approval amendments — diff before sealing

Changed records: 68 / 68. No original golden or split changed. No seal or scoring.

## original:family-B-noisy

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "display_names": ["Inventory Health", "Receipt Share"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "display_names": ["Inventory Health", "Receipt Share"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-B-terse

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "display_names": ["Inventory Health", "Receipt Share"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "display_names": ["Inventory Health", "Receipt Share"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-B-typo

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "display_names": ["Inventory Health", "Receipt Share"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "display_names": ["Inventory Health", "Receipt Share"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-D-noisy

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[{"field": "NUMBER", "question": "NUMBER clarification", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "display_names": ["Activity by warehouse", "Inventory Health"], "mode": "KEYED", "selected_filters": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "operator": "in", "values": ["North"]}], "dimension_ids": [], "cell_keys": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "value": "North"}]}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Human oracle decision 2026-10-09, R2 / corrected truth"}}]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Authored scope is a draft truth, not evidence of an executed procedure."}`

### true_report_and_page

Before: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}`

After: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "display_names": ["Activity by warehouse", "Inventory Health"], "mode": "KEYED", "selected_filters": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "operator": "in", "values": ["North"]}], "dimension_ids": [], "cell_keys": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "value": "North"}]}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

## original:family-D-terse

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[{"field": "NUMBER", "question": "NUMBER clarification", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "display_names": ["Activity by warehouse", "Inventory Health"], "mode": "KEYED", "selected_filters": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "operator": "in", "values": ["North"]}], "dimension_ids": [], "cell_keys": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "value": "North"}]}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Human oracle decision 2026-10-09, R2 / corrected truth"}}]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Authored scope is a draft truth, not evidence of an executed procedure."}`

### true_report_and_page

Before: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}`

After: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "display_names": ["Activity by warehouse", "Inventory Health"], "mode": "KEYED", "selected_filters": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "operator": "in", "values": ["North"]}], "dimension_ids": [], "cell_keys": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "value": "North"}]}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

## original:family-D-typo

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[{"field": "NUMBER", "question": "NUMBER clarification", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "display_names": ["Activity by warehouse", "Inventory Health"], "mode": "KEYED", "selected_filters": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "operator": "in", "values": ["North"]}], "dimension_ids": [], "cell_keys": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "value": "North"}]}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Human oracle decision 2026-10-09, R2 / corrected truth"}}]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Authored scope is a draft truth, not evidence of an executed procedure."}`

### true_report_and_page

Before: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}`

After: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "display_names": ["Activity by warehouse", "Inventory Health"], "mode": "KEYED", "selected_filters": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "operator": "in", "values": ["North"]}], "dimension_ids": [], "cell_keys": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "value": "North"}]}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

## original:family-E-mention

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "STALE", "basis": "Authored freshness question; no timing or tolerance inferred."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "DETERMINED", "value": {"state": "NUMBER", "value": "8765", "precision": {"state": "EXACT"}}, "basis": "Sealed authored reported state and precision, not an evaluated quantity."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_reported_figure

Before: `{"state": "DETERMINED", "value": {"state": "NUMBER", "value": "8765", "precision": {"state": "EXACT"}}, "basis": "Sealed authored reported state and precision, not an evaluated quantity."}`

After: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-E-noisy

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "STALE", "basis": "Authored freshness question; no timing or tolerance inferred."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "NUMBER", "reason": "C1: model-level currency/application request has no visual to choose."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Human oracle decision 2026-10-09, C1"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "STALE", "basis": "Authored freshness question; no timing or tolerance inferred."}`

After: `{"state": "DETERMINED", "value": "STALE", "basis": "Human oracle decision 2026-10-09, C1"}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C1: no figure reported by this model-level request."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C1: model-level named measure; no visual target required."}`

## original:family-E-terse

### illegitimate_questions

Before: `[{"field": "NUMBER", "reason": "Model-level question has no displayed number or visual to select."}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "STALE", "basis": "Authored freshness question; no timing or tolerance inferred."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "NUMBER", "reason": "C1: model-level currency/application request has no visual to choose."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### required_disposition

Before: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Authored scope is a draft truth, not evidence of an executed procedure."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Human oracle decision 2026-10-09, C1"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "STALE", "basis": "Authored freshness question; no timing or tolerance inferred."}`

After: `{"state": "DETERMINED", "value": "STALE", "basis": "Human oracle decision 2026-10-09, C1"}`

### true_reported_figure

Before: `{"state": "NOT_APPLICABLE", "reason": "No figure is reported by this model-level question."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C1: no figure reported by this model-level request."}`

### true_target_and_cell

Before: `{"state": "NOT_APPLICABLE", "reason": "Model-level freshness/source question names a measure, not a displayed figure or visual."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C1: model-level named measure; no visual target required."}`

## original:family-E-typo

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "STALE", "basis": "Authored freshness question; no timing or tolerance inferred."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "NUMBER", "reason": "C1: model-level currency/application request has no visual to choose."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Human oracle decision 2026-10-09, C1"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "STALE", "basis": "Authored freshness question; no timing or tolerance inferred."}`

After: `{"state": "DETERMINED", "value": "STALE", "basis": "Human oracle decision 2026-10-09, C1"}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C1: no figure reported by this model-level request."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C1: model-level named measure; no visual target required."}`

## original:family-H-noisy

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[{"field": "NUMBER", "question": "NUMBER clarification", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "display_names": ["Received Units", "Warehouse Performance"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Human oracle decision 2026-10-09, R2 / corrected truth"}}]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Authored scope is a draft truth, not evidence of an executed procedure."}`

### true_report_and_page

Before: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}`

After: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/page/808c90e3fbe05225bef0", "page_names": ["Warehouse Performance"]}, "basis": "Container of the sealed target in retained report parts."}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "display_names": ["Received Units", "Warehouse Performance"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

## original:family-H-terse

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[{"field": "NUMBER", "question": "NUMBER clarification", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "display_names": ["Received Units", "Warehouse Performance"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Human oracle decision 2026-10-09, R2 / corrected truth"}}]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Authored scope is a draft truth, not evidence of an executed procedure."}`

### true_report_and_page

Before: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}`

After: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/page/808c90e3fbe05225bef0", "page_names": ["Warehouse Performance"]}, "basis": "Container of the sealed target in retained report parts."}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "display_names": ["Received Units", "Warehouse Performance"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

## original:family-H-typo

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[{"field": "NUMBER", "question": "NUMBER clarification", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "display_names": ["Received Units", "Warehouse Performance"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Human oracle decision 2026-10-09, R2 / corrected truth"}}]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Authored scope is a draft truth, not evidence of an executed procedure."}`

### true_report_and_page

Before: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}`

After: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/page/808c90e3fbe05225bef0", "page_names": ["Warehouse Performance"]}, "basis": "Container of the sealed target in retained report parts."}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "display_names": ["Received Units", "Warehouse Performance"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

## original:family-I-noisy

### business_disposition

Before: `null`

After: `{"state": "DETERMINED", "value": "BUSINESS_VALIDATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_TECHNICAL_THEN_BUSINESS_VALIDATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### true_report_and_page

Before: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}`

After: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-I-terse

### business_disposition

Before: `null`

After: `{"state": "DETERMINED", "value": "BUSINESS_VALIDATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_TECHNICAL_THEN_BUSINESS_VALIDATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### true_report_and_page

Before: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}`

After: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-I-typo

### business_disposition

Before: `null`

After: `{"state": "DETERMINED", "value": "BUSINESS_VALIDATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_TECHNICAL_THEN_BUSINESS_VALIDATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### true_report_and_page

Before: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}`

After: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:question-change-days

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995", "report_name": "Declared predicate fixture 20261001", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}]`

After: `[{"field": "NUMBER", "reason": "R4: unsupported change-over-time request; no clarification converts it to a current-state route."}, {"field": "REPORT_PAGE", "reason": "R4: unsupported change-over-time request; no clarification converts it to a current-state route."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}, {"field": "COMPARISON", "question": "What are you comparing against?", "answer": {"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}]`

After: `[]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "UNSUPPORTED_ROUTE", "basis": "Human oracle decision 2026-10-09, R4: change over time"}`

### true_comparison_route

Before: `{"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}`

After: `{"state": "DETERMINED", "value": "CHANGE_OVER_TIME", "basis": "Human oracle decision 2026-10-09, R4: sixth route, not implemented"}`

## original:question-hiding-rows

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995", "report_name": "Declared predicate fixture 20261001", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995", "report_name": "Declared predicate fixture 20261001", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "NUMBER", "reason": "C4 / R5: owner names the card and exact reported figure."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "REPRODUCE_THEN_FILTER_EFFECT_OR_UNIMPLEMENTED_ROUTE", "basis": "Human oracle decision 2026-10-09, C4"}`

### target_predicate_evidence

Before: `null`

After: `{"context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995/part/definition%2Fpages%2F8b067ecb975e5af7a39b%2Fvisuals%2Fa32b6a48db655ac8a4f2%2Fvisual.json", "date_restrictions": [{"field_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/columns/event_day", "operator": "IN", "values": ["2026-09-15"]}], "source": "Preserved local definition; no value query."}`

### true_comparison_route

Before: `{"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C4: declared-subject FILTER_EFFECT, not a pipeline question."}`

### true_report_and_page

Before: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995", "report_name": "Declared predicate fixture 20261001", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}`

After: `{"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995", "report_name": "Declared predicate fixture 20261001", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995/page/8b067ecb975e5af7a39b", "page_names": ["Saved predicate selections"]}, "basis": "Human oracle decision 2026-10-09, C4 / R5"}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "DETERMINED", "value": {"state": "NUMBER", "value": "16", "precision": {"state": "EXACT"}}, "basis": "Human oracle decision 2026-10-09, C3 / R5"}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/2bc1cb2d-9230-4b8f-b7dc-c9f6b2151995/part/definition%2Fpages%2F8b067ecb975e5af7a39b%2Fvisuals%2Fa32b6a48db655ac8a4f2%2Fvisual.json", "display_names": ["Handled Quantity - extra visual predicate", "Saved predicate selections"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Human oracle decision 2026-10-09, C4 / R5"}`

## original:question-stale-no-sla

### illegitimate_questions

Before: `[{"field": "NUMBER", "reason": "Model-level question has no displayed number or visual to select."}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "STALE", "basis": "Authored freshness question; no timing or tolerance inferred."}}]`

After: `[{"field": "NUMBER", "reason": "Model-level question has no displayed number or visual to select."}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

## original:refusal-business-benchmark

### illegitimate_questions

Before: `[{"field": "NUMBER", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}, {"field": "REPORT_PAGE", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}, {"field": "COMPARISON", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}]`

After: `[{"field": "NUMBER", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}, {"field": "REPORT_PAGE", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C5: business-owner judgment, not a reported quantity."}`

## original:refusal-business-intent

### illegitimate_questions

Before: `[{"field": "NUMBER", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}, {"field": "REPORT_PAGE", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}, {"field": "COMPARISON", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}]`

After: `[{"field": "NUMBER", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}, {"field": "REPORT_PAGE", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C5: business-owner judgment, not a reported quantity."}`

## original:refusal-business-q49

### illegitimate_questions

Before: `[{"field": "NUMBER", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}, {"field": "REPORT_PAGE", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}, {"field": "COMPARISON", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}]`

After: `[{"field": "NUMBER", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}, {"field": "REPORT_PAGE", "reason": "Pure business meaning is refused technically; these questions cannot turn it into an authorized comparison."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C5: business-owner judgment, not a reported quantity."}`

## original:refusal-two-figures

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}, {"field": "COMPARISON", "question": "What are you comparing against?", "answer": {"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}]`

After: `[{"field": "FIGURE", "question": "FIGURE clarification", "answer": {"state": "DETERMINED", "value": {"answer": "Both values are showing, I can't say which", "disposition": "HOLD_TWO_REPORTED_FIGURES"}, "basis": "Human oracle decision 2026-10-09, R3"}}]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "HOLD_TWO_REPORTED_FIGURES", "basis": "Human oracle decision 2026-10-09, R3"}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "DETERMINED", "value": {"state": "AMBIGUOUS", "values": ["16", "17"], "precision": {"state": "EXACT"}, "selected_value": null}, "basis": "Human oracle decision 2026-10-09, R3: both reported values, no primary choice"}`

## original:refusal-unidentified-visual

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}, {"field": "REPORT_PAGE", "question": "Which report or page do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No unique authored container; do not use a candidate or engine nomination as user truth."}}]`

After: `[{"field": "REPORT_OR_SCREENSHOT", "question": "REPORT_OR_SCREENSHOT clarification", "answer": {"state": "DETERMINED", "value": {"answer": "I don't know / I don't have one", "disposition": "HOLD_UNIDENTIFIED_REFERENT"}, "basis": "Human oracle decision 2026-10-09, R3"}}]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "HOLD_UNIDENTIFIED_REFERENT", "basis": "Human oracle decision 2026-10-09, R3"}`

## original:refusal-unsupported-filter

### filter_details_answer

Before: `null`

After: `{"state": "DETERMINED", "value": "no details", "basis": "Human oracle decision 2026-10-09, R5"}`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}, {"field": "COMPARISON", "question": "What are you comparing against?", "answer": {"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}]`

After: `[]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "HOLD_UNSUPPORTED_FILTER", "basis": "Human oracle decision 2026-10-09, R5"}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "DETERMINED", "value": {"state": "NUMBER", "value": "16", "precision": {"state": "EXACT"}}, "basis": "Human oracle decision 2026-10-09, C3 / R5"}`

## original:refusal-unsupported-relative

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}, {"field": "COMPARISON", "question": "What are you comparing against?", "answer": {"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}]`

After: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "UNDETERMINED", "reason": "The human description matches 3 cards with different declared contexts. No page/card choice is supplied; never choose using the reported value.", "candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/50d1da38-4b5f-4d69-b967-976265655738/part/definition%2Fpages%2F7547db8624ef59509188%2Fvisuals%2Fc35f95e493de5d258b64%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/50d1da38-4b5f-4d69-b967-976265655738/part/definition%2Fpages%2F8b067ecb975e5af7a39b%2Fvisuals%2F7b8db703ca845710aca9%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/50d1da38-4b5f-4d69-b967-976265655738/part/definition%2Fpages%2F8b067ecb975e5af7a39b%2Fvisuals%2Fa32b6a48db655ac8a4f2%2Fvisual.json"]}, "reported_figure": {"state": "DETERMINED", "value": {"state": "NUMBER", "value": "16", "precision": {"state": "EXACT"}}, "basis": "Human oracle decision 2026-10-09, C3 / R5"}}, "basis": "Human oracle decision 2026-10-09, R2 / corrected truth"}}, {"field": "COMPARISON", "question": "What are you comparing against?", "answer": {"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "HOLD_UNLESS_RELATIVE_DATE_TRANSLATION_VERIFIED", "basis": "Human oracle decision 2026-10-09, R5"}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "DETERMINED", "value": {"state": "NUMBER", "value": "16", "precision": {"state": "EXACT"}}, "basis": "Human oracle decision 2026-10-09, C3 / R5"}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "UNDETERMINED", "reason": "The human description matches 3 cards with different declared contexts. No page/card choice is supplied; never choose using the reported value.", "candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/50d1da38-4b5f-4d69-b967-976265655738/part/definition%2Fpages%2F7547db8624ef59509188%2Fvisuals%2Fc35f95e493de5d258b64%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/50d1da38-4b5f-4d69-b967-976265655738/part/definition%2Fpages%2F8b067ecb975e5af7a39b%2Fvisuals%2F7b8db703ca845710aca9%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/50d1da38-4b5f-4d69-b967-976265655738/part/definition%2Fpages%2F8b067ecb975e5af7a39b%2Fvisuals%2Fa32b6a48db655ac8a4f2%2Fvisual.json"]}`

## original:visual-1

### illegitimate_questions

Before: `[{"field": "NUMBER", "reason": "Exact visual name uniquely locates the sealed target in its report; reported state is already sealed.", "evidence": ["Global card"]}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719", "report_name": "Round Ten Visual Variety", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/page/99d9ca357e3792ad6f70", "page_names": ["Global card"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "NUMBER", "reason": "Exact visual name uniquely locates the sealed target in its report; reported state is already sealed.", "evidence": ["Global card"]}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719", "report_name": "Round Ten Visual Variety", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/page/99d9ca357e3792ad6f70", "page_names": ["Global card"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

## original:visual-3

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719", "report_name": "Round Ten Visual Variety", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/page/5b9bd0d258d6c51b5929", "page_names": ["Warehouse and product matrix"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719", "report_name": "Round Ten Visual Variety", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/page/5b9bd0d258d6c51b5929", "page_names": ["Warehouse and product matrix"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/part/definition%2Fpages%2F5b9bd0d258d6c51b5929%2Fvisuals%2Fd72c75adb19cf1cb1f15%2Fvisual.json", "display_names": ["Handled Quantity - unfiltered", "Warehouse and product matrix"], "mode": "KEYED", "selected_filters": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Items/columns/product_name", "operator": "in", "values": ["Component 1"]}, {"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "operator": "in", "values": ["North"]}], "dimension_ids": [], "cell_keys": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Items/columns/product_name", "value": "Component 1"}, {"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "value": "North"}]}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "DETERMINED", "value": {"state": "NUMBER", "value": "149", "precision": {"state": "EXACT"}}, "basis": "Sealed authored reported state and precision, not an evaluated quantity."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/part/definition%2Fpages%2F5b9bd0d258d6c51b5929%2Fvisuals%2Fd72c75adb19cf1cb1f15%2Fvisual.json", "display_names": ["Handled Quantity - unfiltered", "Warehouse and product matrix"], "mode": "KEYED", "selected_filters": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Items/columns/product_name", "operator": "in", "values": ["Component 1"]}, {"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "operator": "in", "values": ["North"]}], "dimension_ids": [], "cell_keys": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Items/columns/product_name", "value": "Component 1"}, {"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "value": "North"}]}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "DETERMINED", "value": {"state": "NUMBER", "value": "149", "precision": {"state": "EXACT"}}, "basis": "Sealed authored reported state and precision, not an evaluated quantity."}}, "basis": "Human oracle decision 2026-10-09, R2 / corrected truth"}}]`

## original:visual-4

### illegitimate_questions

Before: `[{"field": "NUMBER", "reason": "Exact visual name uniquely locates the sealed target in its report; reported state is already sealed.", "evidence": ["Six active predicates"]}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719", "report_name": "Round Ten Visual Variety", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/page/0f86b2ef08bcd78983f1", "page_names": ["Six active predicates"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "NUMBER", "reason": "Exact visual name uniquely locates the sealed target in its report; reported state is already sealed.", "evidence": ["Six active predicates"]}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719", "report_name": "Round Ten Visual Variety", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/page/0f86b2ef08bcd78983f1", "page_names": ["Six active predicates"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

## original:visual-5

### illegitimate_questions

Before: `[{"field": "NUMBER", "reason": "Exact visual name uniquely locates the sealed target in its report; reported state is already sealed.", "evidence": ["Saved bookmark comparison"]}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719", "report_name": "Round Ten Visual Variety", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/page/901f43de8897c5136b1a", "page_names": ["Saved bookmark comparison"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "NUMBER", "reason": "Exact visual name uniquely locates the sealed target in its report; reported state is already sealed.", "evidence": ["Saved bookmark comparison"]}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719", "report_name": "Round Ten Visual Variety", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/page/901f43de8897c5136b1a", "page_names": ["Saved bookmark comparison"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

## original:family-B

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "display_names": ["Inventory Health", "Receipt Share"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "display_names": ["Inventory Health", "Receipt Share"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Fraction", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-D

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "display_names": ["Activity by warehouse", "Inventory Health"], "mode": "KEYED", "selected_filters": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "operator": "in", "values": ["North"]}], "dimension_ids": [], "cell_keys": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "value": "North"}]}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "display_names": ["Activity by warehouse", "Inventory Health"], "mode": "KEYED", "selected_filters": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "operator": "in", "values": ["North"]}], "dimension_ids": [], "cell_keys": [{"column_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Locations/columns/warehouse_name", "value": "North"}]}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Human oracle decision 2026-10-09, R2 / corrected truth"}}]`

## original:family-E

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "STALE", "basis": "Authored freshness question; no timing or tolerance inferred."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-H

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/page/808c90e3fbe05225bef0", "page_names": ["Warehouse Performance"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5", "report_name": "Warehouse Performance e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/page/808c90e3fbe05225bef0", "page_names": ["Warehouse Performance"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "display_names": ["Received Units", "Warehouse Performance"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fd358e17b02c854bb845c%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fd358e17b02c854bb845c%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/7826f034-ab61-4d8f-8125-27c1d60a73a5/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "display_names": ["Received Units", "Warehouse Performance"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Inbound%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-I

### business_disposition

Before: `null`

After: `{"state": "DETERMINED", "value": "BUSINESS_VALIDATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### required_disposition

Before: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Authored scope is a draft truth, not evidence of an executed procedure."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_TECHNICAL_THEN_BUSINESS_VALIDATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## rebuilt:family-B

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "display_names": ["Inventory Health", "Receipt Share"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json"], "measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Inbound%20Fraction", "catalog_sha256": "51518d2c26de4ee9c262d35026e1ef7db1ed4f1f4fa62a2f5fe07a117af3f770", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "95583877-28b4-42cb-ac60-b286f5971e8c", "retained_context_hash": "d9b30d541ece9383f598ad6977bda03ec15090683cc6a4b1f82c0b0f786e4284", "candidate_scopes": [{"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}, {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd78c6da012ad590aa044%2Fvisual.json", "display_names": ["Inventory Health", "Receipt Share"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Inbound%20Fraction", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## rebuilt:family-D

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "display_names": ["Activity by warehouse", "Inventory Health"], "mode": "KEYED", "selected_filters": [{"column_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Locations/columns/warehouse_name", "operator": "in", "values": ["North"]}], "dimension_ids": [], "cell_keys": [{"column_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Locations/columns/warehouse_name", "value": "North"}]}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "display_names": ["Activity by warehouse", "Inventory Health"], "mode": "KEYED", "selected_filters": [{"column_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Locations/columns/warehouse_name", "operator": "in", "values": ["North"]}], "dimension_ids": [], "cell_keys": [{"column_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Locations/columns/warehouse_name", "value": "North"}]}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Human oracle decision 2026-10-09, R2 / corrected truth"}}]`

## rebuilt:family-E

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "STALE", "basis": "Authored freshness question; no timing or tolerance inferred."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "51518d2c26de4ee9c262d35026e1ef7db1ed4f1f4fa62a2f5fe07a117af3f770", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "95583877-28b4-42cb-ac60-b286f5971e8c", "retained_context_hash": "d9b30d541ece9383f598ad6977bda03ec15090683cc6a4b1f82c0b0f786e4284", "candidate_scopes": [{"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## rebuilt:family-H

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/f650bba1-7e5c-4f42-97b9-60b7c5608da8", "report_name": "Warehouse Performance e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/f650bba1-7e5c-4f42-97b9-60b7c5608da8/page/808c90e3fbe05225bef0", "page_names": ["Warehouse Performance"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/f650bba1-7e5c-4f42-97b9-60b7c5608da8", "report_name": "Warehouse Performance e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/f650bba1-7e5c-4f42-97b9-60b7c5608da8/page/808c90e3fbe05225bef0", "page_names": ["Warehouse Performance"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/f650bba1-7e5c-4f42-97b9-60b7c5608da8/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "display_names": ["Received Units", "Warehouse Performance"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/f650bba1-7e5c-4f42-97b9-60b7c5608da8/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/f650bba1-7e5c-4f42-97b9-60b7c5608da8/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fd358e17b02c854bb845c%2Fvisual.json"], "measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Inbound%20Quantity", "catalog_sha256": "51518d2c26de4ee9c262d35026e1ef7db1ed4f1f4fa62a2f5fe07a117af3f770", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "95583877-28b4-42cb-ac60-b286f5971e8c", "retained_context_hash": "d9b30d541ece9383f598ad6977bda03ec15090683cc6a4b1f82c0b0f786e4284", "candidate_scopes": [{"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/f650bba1-7e5c-4f42-97b9-60b7c5608da8/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/f650bba1-7e5c-4f42-97b9-60b7c5608da8/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fd358e17b02c854bb845c%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/f650bba1-7e5c-4f42-97b9-60b7c5608da8/part/definition%2Fpages%2F808c90e3fbe05225bef0%2Fvisuals%2Fcb317373005d5476a24e%2Fvisual.json", "display_names": ["Received Units", "Warehouse Performance"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Inbound%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## rebuilt:family-I

### business_disposition

Before: `null`

After: `{"state": "DETERMINED", "value": "BUSINESS_VALIDATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### required_disposition

Before: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Authored scope is a draft truth, not evidence of an executed procedure."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_TECHNICAL_THEN_BUSINESS_VALIDATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "51518d2c26de4ee9c262d35026e1ef7db1ed4f1f4fa62a2f5fe07a117af3f770", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "95583877-28b4-42cb-ac60-b286f5971e8c", "retained_context_hash": "d9b30d541ece9383f598ad6977bda03ec15090683cc6a4b1f82c0b0f786e4284", "candidate_scopes": [{"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C6"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-A-mention

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "DETERMINED", "value": {"state": "NUMBER", "value": "8765", "precision": {"state": "EXACT"}}, "basis": "Sealed authored reported state and precision, not an evaluated quantity."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}, {"field": "COMPARISON", "question": "What are you comparing against?", "answer": {"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_comparison_route

Before: `{"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C2"}`

### true_reported_figure

Before: `{"state": "DETERMINED", "value": {"state": "NUMBER", "value": "8765", "precision": {"state": "EXACT"}}, "basis": "Sealed authored reported state and precision, not an evaluated quantity."}`

After: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-A-noisy

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "LOOKS_WRONG", "basis": "An explicit wrong-looking-number ask without a named second referent."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "LOOKS_WRONG", "basis": "An explicit wrong-looking-number ask without a named second referent."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C2"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-A-terse

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "LOOKS_WRONG", "basis": "An explicit wrong-looking-number ask without a named second referent."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "LOOKS_WRONG", "basis": "An explicit wrong-looking-number ask without a named second referent."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C2"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-A-typo

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "LOOKS_WRONG", "basis": "An explicit wrong-looking-number ask without a named second referent."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "LOOKS_WRONG", "basis": "An explicit wrong-looking-number ask without a named second referent."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C2"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-C-noisy

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "display_names": ["Inventory Health", "Net Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "display_names": ["Inventory Health", "Net Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-C-terse

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "display_names": ["Inventory Health", "Net Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "display_names": ["Inventory Health", "Net Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-C-typo

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "display_names": ["Inventory Health", "Net Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "display_names": ["Inventory Health", "Net Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-F-noisy

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "LOOKS_WRONG", "basis": "An explicit wrong-looking-number ask without a named second referent."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "display_names": ["Inventory Health", "Movement Value"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "display_names": ["Inventory Health", "Movement Value"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-F-terse

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "LOOKS_WRONG", "basis": "An explicit wrong-looking-number ask without a named second referent."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "display_names": ["Inventory Health", "Movement Value"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "display_names": ["Inventory Health", "Movement Value"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-F-typo

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "LOOKS_WRONG", "basis": "An explicit wrong-looking-number ask without a named second referent."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "display_names": ["Inventory Health", "Movement Value"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "display_names": ["Inventory Health", "Movement Value"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-G-mention

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: retained candidate definitions establish the same measure and declared scope."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "DETERMINED", "value": {"state": "NUMBER", "value": "8765", "precision": {"state": "EXACT"}}, "basis": "Sealed authored reported state and precision, not an evaluated quantity."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_reported_figure

Before: `{"state": "DETERMINED", "value": {"state": "NUMBER", "value": "8765", "precision": {"state": "EXACT"}}, "basis": "Sealed authored reported state and precision, not an evaluated quantity."}`

After: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"model_id": "5b3eff46-631c-47b8-8211-049b5aa906ee", "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-G-noisy

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "NUMBER", "reason": "C1: model-level currency/application request has no visual to choose."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Human oracle decision 2026-10-09, C1"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C1"}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C1: no figure reported by this model-level request."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C1: model-level named measure; no visual target required."}`

## original:family-G-terse

### illegitimate_questions

Before: `[{"field": "NUMBER", "reason": "Model-level question has no displayed number or visual to select."}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "NUMBER", "reason": "C1: model-level currency/application request has no visual to choose."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### required_disposition

Before: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Authored scope is a draft truth, not evidence of an executed procedure."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Human oracle decision 2026-10-09, C1"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C1"}`

### true_reported_figure

Before: `{"state": "NOT_APPLICABLE", "reason": "No figure is reported by this model-level question."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C1: no figure reported by this model-level request."}`

### true_target_and_cell

Before: `{"state": "NOT_APPLICABLE", "reason": "Model-level freshness/source question names a measure, not a displayed figure or visual."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C1: model-level named measure; no visual target required."}`

## original:family-G-typo

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "NUMBER", "reason": "C1: model-level currency/application request has no visual to choose."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED", "basis": "Human oracle decision 2026-10-09, C1"}`

### true_comparison_route

Before: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C1"}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C1: no figure reported by this model-level request."}`

### true_target_and_cell

Before: `{"state": "UNDETERMINED", "reason": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent."}`

After: `{"state": "NOT_APPLICABLE", "reason": "C1: model-level named measure; no visual target required."}`

## original:question-change-week

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}]`

After: `[{"field": "NUMBER", "reason": "R4: unsupported change-over-time request; no clarification converts it to a current-state route."}, {"field": "REPORT_PAGE", "reason": "R4: unsupported change-over-time request; no clarification converts it to a current-state route."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}, {"field": "COMPARISON", "question": "What are you comparing against?", "answer": {"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}]`

After: `[]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "UNSUPPORTED_ROUTE", "basis": "Human oracle decision 2026-10-09, R4: change over time"}`

### true_comparison_route

Before: `{"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}`

After: `{"state": "DETERMINED", "value": "CHANGE_OVER_TIME", "basis": "Human oracle decision 2026-10-09, R4: sixth route, not implemented"}`

### unsolicited_earlier_value_answer

Before: `null`

After: `{"state": "DETERMINED", "value": "I don't have it", "basis": "Human oracle decision 2026-10-09, R4"}`

## original:refusal-nonexistent-column

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "LOOKS_WRONG", "basis": "An explicit wrong-looking-number ask without a named second referent."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": null}, "basis": "One exact report name in the authored ticket; no page was specified."}}, {"field": "NUMBER", "reason": "R5: user rejected warehouse_name; re-asking cannot substitute an existing column."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}]`

After: `[]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "HOLD_NONEXISTENT_COLUMN", "basis": "Human oracle decision 2026-10-09, R5"}`

## original:refusal-two-figures-total

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}, {"field": "COMPARISON", "question": "What are you comparing against?", "answer": {"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}]`

After: `[{"field": "FIGURE", "question": "FIGURE clarification", "answer": {"state": "DETERMINED", "value": {"answer": "Both values are showing, I can't say which", "disposition": "HOLD_TWO_REPORTED_FIGURES"}, "basis": "Human oracle decision 2026-10-09, R3"}}]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "HOLD_TWO_REPORTED_FIGURES", "basis": "Human oracle decision 2026-10-09, R3"}`

### true_reported_figure

Before: `{"state": "UNDETERMINED", "reason": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}`

After: `{"state": "DETERMINED", "value": {"state": "AMBIGUOUS", "values": ["8765", "8766"], "precision": {"state": "EXACT"}, "selected_value": null}, "basis": "Human oracle decision 2026-10-09, R3: both reported values, no primary choice"}`

## original:refusal-unidentified-measure

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No authored target answer is present; owner/reviewer must supply it or confirm permanent refusal."}}, {"field": "REPORT_PAGE", "question": "Which report or page do you mean?", "answer": {"state": "UNDETERMINED", "reason": "No unique authored container; do not use a candidate or engine nomination as user truth."}}]`

After: `[{"field": "REPORT_OR_SCREENSHOT", "question": "REPORT_OR_SCREENSHOT clarification", "answer": {"state": "DETERMINED", "value": {"answer": "I don't know / I don't have one", "disposition": "HOLD_UNIDENTIFIED_REFERENT"}, "basis": "Human oracle decision 2026-10-09, R3"}}]`

### required_disposition

Before: `{"state": "UNDETERMINED", "reason": "Original refusal remains unchanged. A conversational answer or a capability limitation needs owner/reviewer approval."}`

After: `{"state": "DETERMINED", "value": "HOLD_UNIDENTIFIED_REFERENT", "basis": "Human oracle decision 2026-10-09, R3"}`

## original:visual-2

### illegitimate_questions

Before: `[{"field": "NUMBER", "reason": "Exact visual name uniquely locates the sealed target in its report; reported state is already sealed.", "evidence": ["Warehouse matrix total"]}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719", "report_name": "Round Ten Visual Variety", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/page/7788dc14cd101535f3aa", "page_names": ["Warehouse matrix total"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "NUMBER", "reason": "Exact visual name uniquely locates the sealed target in its report; reported state is already sealed.", "evidence": ["Warehouse matrix total"]}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719", "report_name": "Round Ten Visual Variety", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/page/7788dc14cd101535f3aa", "page_names": ["Warehouse matrix total"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

## original:visual-6

### illegitimate_questions

Before: `[{"field": "NUMBER", "reason": "Exact visual name uniquely locates the sealed target in its report; reported state is already sealed.", "evidence": ["Calculated table card"]}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719", "report_name": "Round Ten Visual Variety", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/page/ca8355a38db5ec471f39", "page_names": ["Calculated table card"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "NUMBER", "reason": "Exact visual name uniquely locates the sealed target in its report; reported state is already sealed.", "evidence": ["Calculated table card"]}, {"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719", "report_name": "Round Ten Visual Variety", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/95b6d455-9150-4738-983d-ca6e7e0f3719/page/ca8355a38db5ec471f39", "page_names": ["Calculated table card"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

## original:family-A

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}, {"field": "COMPARISON", "question": "What are you comparing against?", "answer": {"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_comparison_route

Before: `{"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C2"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-C

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "display_names": ["Inventory Health", "Net Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "display_names": ["Inventory Health", "Net Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Quantity%20Balance", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-F

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "LOOKS_WRONG", "basis": "An explicit wrong-looking-number ask without a named second referent."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "display_names": ["Inventory Health", "Movement Value"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "display_names": ["Inventory Health", "Movement Value"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Extended%20Value", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## original:family-G

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "5551eb13ff159e6b2cc12041efdb0a228608f921566b11b848ce515389304e01", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "0bbcfa54-2023-4f59-87ce-9f62662f4a98", "retained_context_hash": "beae62970b86b9c5a91db45608cfaabe45e9ed6199bd8afccee0908673ab5ce6", "candidate_scopes": [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/692f3ead-d1d1-4f7f-984b-51e54f3e7497/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/3484a2bc-98c5-4cef-be5c-a6215484075e/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## rebuilt:family-A

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}, {"field": "COMPARISON", "question": "What are you comparing against?", "answer": {"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "51518d2c26de4ee9c262d35026e1ef7db1ed4f1f4fa62a2f5fe07a117af3f770", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "95583877-28b4-42cb-ac60-b286f5971e8c", "retained_context_hash": "d9b30d541ece9383f598ad6977bda03ec15090683cc6a4b1f82c0b0f786e4284", "candidate_scopes": [{"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_comparison_route

Before: `{"state": "UNDETERMINED", "reason": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}`

After: `{"state": "DETERMINED", "value": "APPLICATION", "basis": "Human oracle decision 2026-10-09, C2"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## rebuilt:family-C

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "NOT_APPLICABLE", "reason": "Explicit work on the declared subject; no external comparator is required. Internal route is DECLARED_SUBJECT."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "display_names": ["Inventory Health", "Net Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Quantity%20Balance", "catalog_sha256": "51518d2c26de4ee9c262d35026e1ef7db1ed4f1f4fa62a2f5fe07a117af3f770", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "95583877-28b4-42cb-ac60-b286f5971e8c", "retained_context_hash": "d9b30d541ece9383f598ad6977bda03ec15090683cc6a4b1f82c0b0f786e4284", "candidate_scopes": [{"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F886713d347e65e368f0c%2Fvisual.json", "display_names": ["Inventory Health", "Net Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Quantity%20Balance", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## rebuilt:family-F

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "LOOKS_WRONG", "basis": "An explicit wrong-looking-number ask without a named second referent."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "display_names": ["Inventory Health", "Movement Value"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Extended%20Value", "catalog_sha256": "51518d2c26de4ee9c262d35026e1ef7db1ed4f1f4fa62a2f5fe07a117af3f770", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "95583877-28b4-42cb-ac60-b286f5971e8c", "retained_context_hash": "d9b30d541ece9383f598ad6977bda03ec15090683cc6a4b1f82c0b0f786e4284", "candidate_scopes": [{"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F8ab0a65859d5586f8e6f%2Fvisual.json", "display_names": ["Inventory Health", "Movement Value"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Extended%20Value", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

## rebuilt:family-G

### illegitimate_questions

Before: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "COMPARISON", "reason": "Comparison is explicit in the authored question, or the subject needs no external comparator.", "evidence": {"state": "DETERMINED", "value": "APPLICATION", "basis": "Authored request to check source records; reachability is not assumed."}}]`

After: `[{"field": "REPORT_PAGE", "reason": "Report is stated exactly or supplied by the sealed target container; asking again adds no evidence.", "evidence": {"state": "DETERMINED", "value": {"report_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e", "report_name": "Inventory Health e1b8e1", "page_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/page/688de76fce97549d9756", "page_names": ["Inventory Health"]}, "basis": "Container of the sealed target in retained report parts."}}, {"field": "NUMBER", "reason": "R1: all candidate total/ungrouped definitions have the same measure and declared restrictions."}, {"field": "COMPARISON", "reason": "Human-reviewed comparison/declared subject is established; no route question needed."}]`

### legitimate_questions

Before: `[{"field": "NUMBER", "question": "Which displayed visual and cell do you mean?", "answer": {"state": "DETERMINED", "value": {"target": {"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}, "reported_figure": {"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}}, "basis": "Authored sealed visual/cell and figure; approval required before simulator use."}}]`

After: `[]`

### scope_equivalence_review

Before: `null`

After: `{"candidate_ids": ["fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json"], "measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity", "catalog_sha256": "51518d2c26de4ee9c262d35026e1ef7db1ed4f1f4fa62a2f5fe07a117af3f770", "method": "Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.", "retained_context_id": "95583877-28b4-42cb-ac60-b286f5971e8c", "retained_context_hash": "d9b30d541ece9383f598ad6977bda03ec15090683cc6a4b1f82c0b0f786e4284", "candidate_scopes": [{"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "restrictions": [], "cell": "UNGROUPED"}, {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2Fd21708a8bc35561c81f5%2Fvisual.json", "restrictions": [], "cell": "TOTAL"}], "status": "VERIFIED_EQUIVALENT_DECLARED_SCOPE"}`

### true_target_and_cell

Before: `{"state": "DETERMINED", "value": {"target_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/3fa351b8-ff17-4b0e-bbce-3a24b1f9536e/part/definition%2Fpages%2F688de76fce97549d9756%2Fvisuals%2F25189fcc5fe05539b3b6%2Fvisual.json", "display_names": ["Inventory Health", "Movement Units"], "mode": "UNGROUPED", "selected_filters": [], "dimension_ids": [], "cell_keys": []}, "basis": "Sealed authored target/cell and singleton grouping-key filters; no model result used."}`

After: `{"state": "DETERMINED", "value": {"measure_id": "fabric://d028fa2b-0d1b-4dd8-b423-37dd161cd5d0/ade205fe-52b1-43b5-980a-773b7b1de538/table/Activity/measures/Handled%20Quantity", "scope": [], "kind": "MEASURE_AT_SCOPE"}, "basis": "Human oracle decision 2026-10-09, R1"}`

# R1 evidence exceptions

- original:refusal-unsupported-relative: Retained evaluation definitions do not uniquely bind the human-described card; no predicate evidence may be invented. [{"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/50d1da38-4b5f-4d69-b967-976265655738/part/definition%2Fpages%2F7547db8624ef59509188%2Fvisuals%2Fc35f95e493de5d258b64%2Fvisual.json", "names": ["Handled Quantity - unfiltered", "Top-N verification"], "page": ["Top-N verification"]}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/50d1da38-4b5f-4d69-b967-976265655738/part/definition%2Fpages%2F8b067ecb975e5af7a39b%2Fvisuals%2F7b8db703ca845710aca9%2Fvisual.json", "names": ["Handled Quantity - page and slicers", "Saved predicate selections"], "page": ["Saved predicate selections"]}, {"target_id": "fabric://149f8d99-1c66-4a0a-9624-759be002bb60/50d1da38-4b5f-4d69-b967-976265655738/part/definition%2Fpages%2F8b067ecb975e5af7a39b%2Fvisuals%2Fa32b6a48db655ac8a4f2%2Fvisual.json", "names": ["Handled Quantity - extra visual predicate", "Saved predicate selections"], "page": ["Saved predicate selections"]}]

# Remaining undetermined records

{"id": "original:question-change-days", "fields": {"true_target_and_cell": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent.", "true_reported_figure": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}}
{"id": "original:refusal-two-figures", "fields": {"true_target_and_cell": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent.", "true_comparison_route": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}
{"id": "original:refusal-unidentified-visual", "fields": {"true_target_and_cell": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent.", "true_reported_figure": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number.", "true_report_and_page": "Neither a sealed target container nor one exact authored report name establishes a report/page."}}
{"id": "original:refusal-unsupported-filter", "fields": {"true_target_and_cell": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent.", "true_comparison_route": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}
{"id": "original:refusal-unsupported-relative", "fields": {"true_target_and_cell": "The human description matches 3 cards with different declared contexts. No page/card choice is supplied; never choose using the reported value.", "true_comparison_route": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}
{"id": "original:question-change-week", "fields": {"true_target_and_cell": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent.", "true_reported_figure": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}}
{"id": "original:refusal-nonexistent-column", "fields": {"true_target_and_cell": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent.", "true_reported_figure": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number."}}
{"id": "original:refusal-two-figures-total", "fields": {"true_target_and_cell": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent.", "true_comparison_route": "Ticket and sealed record do not choose one comparison route. A calculation question is not silently converted to LOOKS_WRONG."}}
{"id": "original:refusal-unidentified-measure", "fields": {"true_target_and_cell": "The one-shot sealed record supplies no true target. Candidate visuals are alternatives, not author intent.", "true_reported_figure": "A refusal record does not identify the intended primary figure; do not reinterpret null as zero, empty or an invented number.", "true_report_and_page": "Neither a sealed target container nor one exact authored report name establishes a report/page."}}
