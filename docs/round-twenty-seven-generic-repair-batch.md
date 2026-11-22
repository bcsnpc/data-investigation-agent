# Round 27 generic repair batch

These candidate repairs come from saved dev traces. They do not change the qualified image used for the eight pass-1 completion cases, any expectation, or any earlier result. Full-suite and image-shard qualification remain required before pass 2.

| Flag (default on, independently reversible) | Repair and retained boundary |
|---|---|
| `r27_delivery_reference_reformat` | Convert unambiguous same-case query references to their recorded layer for `checked`, and fetched evidence wrappers to original native evidence IDs. Unknown/cyclic references stay invalid; failed queries cannot support successful claims. |
| `r27_conclusion_detail_compatibility` | Separate the question-level disposition from supported technical access/presence details. Keep explicit-target, missing-evidence and contradictory-deviation checks. |
| `r27_terminal_calculation_consistency` | Preserve the validated answer's calculation explanation in the terminal summary, labelled delivered prose, never new native evidence. Unresolved results are not upgraded. |
| `r27_unicode_sql_literals` | Bind valid T-SQL national string literals as bounded Unicode parameters. SELECT-only roots, native object scope, length limits and write refusal remain enforced. |
| `r27_native_column_target` | Resolve table candidates inside an explicitly named container using named columns and retained native containment. Explicit table names win; equal candidates remain ambiguous. No data or extra catalog read is added. |

The last repair was checked against the retained fixture graph and the unchanged latency ticket: the old adapter returned no table; the new adapter returned the single Bronze table witnessed by `movement_id` and `units`. This is an offline routing check, not a live quality score.

Focused verification: 55 tests passed across delivery references, conclusion compatibility, terminal findings, Unicode query literals, native column targeting and feature flags. The first combined invocation lacked `PYTHONPATH=scripts` and failed imports; the corrected invocation passed. Earlier focused checks are retained separately. These checks do not replace qualification of the eventual batch.

The advisory evaluator remains explicitly enabled only in the selected test installation profile; its factory default remains off. Intake guards and saved-evidence delivery repair stay enabled.
