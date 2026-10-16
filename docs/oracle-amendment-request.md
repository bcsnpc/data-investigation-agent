# Oracle amendment request ? 2026-10-10 UTC

Request only. The sealed oracle is unchanged; owner and reviewer approval is required. Exact seal: be029b56a6de27195dac507bfb5010f0ce7abc2732702d9a230e5f4a8d38406c.

## original:family-A-mention

Exact ticket:

> Inventory Health e1b8e1 Handled Quantity is higher than source movements. Check the global discrepancy. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.

Oracle field: `true_reported_figure.state = NOT_STATED`. Reason: The admitted sealed record explicitly records no reported figure.

Agent used: `NUMBER`, value `8765`, precision `EXACT`; verbatim span 148:152 = `8765`.

## original:family-G-mention

Exact ticket:

> Inventory Health e1b8e1 Handled Quantity may contain incorrect source entries. Check source movements and inventory adjustments, without assuming adjustment business intent. The global Handled Quantity currently shows 8765. Internal request reference 4182 is only a tracking number, not the metric figure; please do not compare that reference to the data.

Oracle field: `true_reported_figure.state = NOT_STATED`. Reason: The admitted sealed record explicitly records no reported figure.

Agent used: `NUMBER`, value `8765`, precision `EXACT`; verbatim span 218:222 = `8765`.

Against the unchanged sealed oracle: **2 consequential-field mismatches**. If both requested figure amendments are approved, with every other truth field unchanged: **0 consequential-field mismatches** in this retained pass. This is a counterfactual audit, not a re-score or approval. Settlement would not necessarily increase: independent question/target gates still apply. The dev E-mention conflict remains separately diagnosed and unamended. No further held-out pass.
