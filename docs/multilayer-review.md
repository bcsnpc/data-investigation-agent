# Multi-layer evidence review

Retained local three-layer findings now appear in the investigation review UI. The existing
authenticated evidence endpoint summarizes per-order Bronze, Silver and Gold observations,
plus each adjacent boundary's recorded comparison status. The deterministic finding panel
shows the first observed local discrepancy, upstream/downstream totals, exact per-currency
differences and affected records.

For the propagated Silver case, Bronze/Silver shows USD 154 versus USD 164 and one affected
order; Silver/Gold shows matching USD 164 values. The UI retains UNRESOLVED, the scope
limitation and an explicit statement that root cause is unverified. Matching downstream
layers do not establish upstream correctness. No new routing eligibility is added.

This displays saved multi-layer findings. The normal lab worker still runs its original
two-layer investigation; generating a multi-layer run from ticket intake is separate work.
Browser verification attaches the existing saved fixture finding to an isolated review ticket.
No cloud, model, delivery or baseline mutation is needed for this display verification.

Three regression tests cover all layers/boundaries, authenticated detail with retained
impact and compatibility with legacy summaries. Browser checks cover visible boundary totals,
affected record, classification and mobile layout. Broader scenario evaluation, transformation
proof and live snapshot comparability remain pending.
