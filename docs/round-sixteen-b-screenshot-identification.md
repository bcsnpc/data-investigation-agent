# Screenshot identification - Part B

The production screenshot service uses on-device `Windows.Media.Ocr`, with line and word rectangles. It makes no model or estate request and creates no temporary image file. It reads existing bounded image attachments, compares visible report/page/visual labels against retained native page definitions, and retains the OCR, image SHA-256, candidate identities, definition hashes and identification method in a hash-checked review.

`ClaimScreenshots.identify`, `get`, `confirm` and `load` provide the API and controller ports. The controller receives only a review ID and reloads the stored body; client-supplied facts are rejected. Identify and confirm are recorded operations. A unique highest-scoring page is a candidate, not a causal finding or a business confirmation. Ties produce up to three choices using visible report/page names. Confirmation is appended separately, leaving the review's original hash unchanged. A confirmed portal/tab mapping is namespaced by the approved manifest hash and can identify later screenshots only while its retained definition fingerprint still matches. Any configuration change safely invalidates that namespace; this is conservative invalidation rather than a stable estate identifier. Injected test installations use their retained model/report identity inventory. Changed candidate catalogs refuse controller loading rather than silently rebinding the screenshot.

Metric facts come from actual matched visible labels. An observed figure is emitted only from a label and figure on the same line, or a unique nearby label/value pair with overlapping horizontal bounds. A number near two metric labels, a distant unlabeled number, unreadable content or an ambiguous page does not acquire a figure role. Both label and number rectangles are retained for a positional pair. A confirmed page supplies a page scope; screenshots do not invent a direction, comparator, hidden filter, RLS state, freshness or cause. Privacy-projected installations refuse image OCR before reading pixels or writing OCR reviews because image projection is not implemented.

Numeric value tiebreak is **not implemented for this screenshot route**. The existing governed candidate reader is available to form intake, but this route has not established a faithful translation of all visible filter selections into its admitted scope. It therefore does not issue a value query or assume an unfiltered total. It retains the ambiguity and asks a named page question. This is a remaining Part B limitation, not a successful tiebreak test.

## Offline OCR experiment

The experiment used **synthetic renderings of retained definitions**, not native Power BI screenshots and not independent tester captures. All 21 candidate pages competed: 18 fixture/lookalike pages and three billing pages. Labels were rendered as full pages, cropped visual-label sections and pages inside an unrelated portal header. Every image was passed through the real local Windows OCR bridge; no generated transcript was supplied to the recognizer. Definition-derived expectations and rendering generation share a source, so this measures this bounded recognition exercise and cannot establish native screenshot accuracy.

| Variant | Cases | Correct report/page | Held | Wrong identification |
|---|---:|---:|---:|---:|
| Full labels | 21 | 19 | 2 | 0 |
| Cropped labels | 21 | 3 | 18 | 0 |
| Portal frame | 21 | 19 | 2 | 0 |
| Total | 63 | 41 | 22 | 0 |

The full/portal holds are two fixture lookalikes. Crops generally omit the distinguishing report names; the service retains that ambiguity. Private evidence is `.local/round-sixteen/screenshot-benchmark-v3/result.json`, including each image SHA, real OCR rectangles, competing candidate scores and expected/actual page identity. The companion `catalog.json` and 63 PNGs remain local. This experiment used zero estate reads and zero model calls.

Seventeen focused tests passed, including the real controller integration test with deterministic OCR, retained fact IDs and provenance, positional number ambiguity, stale catalog/mapping refusals, append-only confirmation, named choices, client-fact rejection and projection refusal. The real local OCR bridge additionally recognized a rendered `Subscription Billing` title with word positions. The experiment is distinct from the owner's bounded production smoke and exact replay results, which are recorded separately.
