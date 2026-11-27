# R28 repair proof

The JSON report compares the same saved-response harness on PR #436 head and the repair revision. Only traces complete on both are comparable. All missing boundaries are reported; no new model response, query result or expectation was invented. Network connects are refused during replay. This is a bounded replay prototype, not a byte-exact tape replay or a quality grade.

`prompt-sizes-per-call.csv` records every observed investigation/evaluator packet before and after projection, measured offline with tiktoken o200k_base. The complete catalog and native evidence remain in saved captures; prompts contain scoped references and can fetch exact bodies by evidence ID. Intake scoping has separate synthetic tests.

`run_saved_traces.py` and `replay_engine.py` consume locally retained hash-verified practice indices and already-graded HealthNet captures under `.local/round-twenty-eight-fixes`. They require the local saved-index paths; no capture contents, expected answers, private grader packets or credentials are committed here. Run the harness in two separate processes with DIA_R28_CODE_ROOT and DIA_R27_REPLAY_CODE_ROOT selecting the old or repair scripts, then compare completed rows. No sealed unrun ticket is loaded.
