# Investigation acceptance baseline

Run `python scripts/evaluate_acceptance.py` from the repository root. The report is
saved to `.local/acceptance-baseline.json`. CI also runs the baseline through unittest.

The harness exercises authenticated WSGI ticket submission, planning, draft review,
repeated approval, approved-only background execution, evidence persistence/detail,
automatic explanation requests, repeated-request reuse, and related ticket status.
Each case uses temporary SQLite stores and a fixture lineage graph. Cloud reads and
model selections are deterministic fixtures; no Azure credentials or business changes
are involved. This proves the connected local workflow, not live provider availability
or the full product's root-cause accuracy. Ground-truth assertions stay in the evaluator.

| Case | Observed result | Acceptance meaning |
|---|---|---|
| Equal values without snapshot proof | UNRESOLVED; all boundaries NOT_COMPARABLE | Matching totals are not promoted to expected behavior |
| Missing SQL evidence | UNRESOLVED; first boundary UNAVAILABLE | Missing evidence cannot become zero or prove a first divergence |
| Comparable Gold difference | Silver → Gold first verified divergence; UNRESOLVED | Comparable mismatch is detected without inventing a root cause |

Every case confirms one acquisition and one simulated explanation selection despite
repeated approval/explanation requests. Evidence, parent history and classification
remain intact. The report deliberately separates `workflow_passed: true` from
`product_acceptance_complete: false`.

Remaining acceptance gates:

- A no-defect scenario with verified business drivers that earns EXPECTED_BEHAVIOR.
- Root-cause verification against affected records and transformation evidence.
- Quantified impact and downstream owner attribution.
- Proven live snapshot compatibility or a supported alternative acquisition strategy.
- Isolated, injectable/resettable multi-layer defects with separate ground truth.
- Bug creation/notification policy and delivery tests after human-reviewed configuration.

Next implementation should establish the isolated defect-lab baseline and reset contract,
using existing returns/refunds/order data. Do not add reinstatement merely to reproduce
an illustrative scope example. Preserve the verified cloud baseline throughout.
