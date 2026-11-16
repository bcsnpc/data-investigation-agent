# Round 26 provider benchmark checkpoint

Primary grades only; this is not the Round 26 held-out quality result. Original outcomes, exceptions and charges remain preserved. The owner reserved Claude credit for v5, so the two Opus stale cases were not run.

| Investigator | Correct / graded | Requested | Harmful flags | Mean recorded outcome cost |
|---|---:|---:|---:|---:|
| sol-cascade | 13/40 | 40 | 1 | $0.4422 |
| openai | 28/40 | 40 | 0 | $0.6858 |
| anthropic | 34/38 | 40 | 0 | $0.3903 |

The first 32 Sol/Astra cases used Claude Sonnet 4.6 batch grading. Remaining cases used Amazon Nova Pro, preserving the newly reserved Claude credit. Opus used GPT-6.1 Sol. These are mixed primary graders; no secondary/raw-review benchmark score is claimed. The Sol harmful flag remains a primary-grader flag, not an independent raw-review conclusion.

The owner resume instruction selects Astra for new dev and Opus for the once-only v5 run. No complete forty-case Opus support claim is made. The original benchmark image remains pinned and unchanged.

Native stale controls were restored: original 360-row source hash, real load completed, automatic updates ON persisted after reopen, own model refresh completed, native model total 7,661.

Dev01 is active on image `1114841e?`, source `b90371c7`: 12 failed forms plus the first pass of 40 free-text dev tickets. Earlier passed forms are not repeated. New delivery-after-ticket-cap candidate `ebfdbe45` is not deployed to this scored pass.
