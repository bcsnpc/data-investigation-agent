# Intake rejection questions

The retained Sol-plus-Astra development diagnostic has eleven remaining questions. Three carry a direct-target resolution rejection, two carry an ambiguous numeral/precision-span rejection, and six returned a question without a structured validation rejection. These are saved dev traces only; no held-out wording or new estate/model reads were used for this audit.

The extraction-failure fallback always considered a report missing, including when a known catalog table or measure was already present. It now preserves that target and asks about figure interpretation, or offers actual table/measure choices when that target's textual grounding remains unresolved. The underlying rejection is retained explicitly. Real target ties and quantity/precision failures still refuse admission after the bounded retry. No target, value or scope is guessed.

Synthetic regressions cover a too-wide quantity span followed by an exact span (proceeds), two rejected spans (asks about the figure without re-asking for a report), ambiguous tables (offers tables), and an ungrounded table mention (nonempty catalog choices). The running provider benchmark stays on its earlier pinned image. Earlier 28/40 and 29/40 intake results remain historical observations; no higher ready rate is claimed for this correction without a new measured development pass.
