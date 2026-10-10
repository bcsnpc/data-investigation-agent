# Shared intake questionnaire

Web, chat and API use `GET /api/workspace/questionnaire/schema`. The closed
`intake-questionnaire-v1` schema and ordered field descriptors are defined once
in `scripts/investigator/intake_questionnaire.py`. Both browser presentations
render those descriptors and submit to the same consumer.

| Order | Field | Required | Choices and source |
| --- | --- | --- | --- |
| 1 | Report | Yes | `questionnaire/catalog`: existing reader's estate-scoped live report list, bound by native ID to approved definitions. |
| 2 | Page / tab | Yes | POST `questionnaire/pages` with `report_id` and `refresh`: existing live page list; only pages with approved executable definitions are selectable. |
| 3 | Visual | No | POST `questionnaire/visuals` with report/page IDs: approved retained visual titles, explicitly labelled as saved definitions. This is **not a live visual list**. |
| 4 | Comparing with | Yes | Another report (report + page), another page (page), application (optional source value + screenshot), or nothing specific. The schema's disjoint branches forbid unrelated fields. |
| 5 | Description | No | Original user text, at most 2,000 characters. Structured span extraction supplies the question kind, precision and missing cell facts. |
| 6 | Screenshot | No | Existing upload, metered extraction and user-review endpoints; `screenshot_review_id` refers to retained reviewed evidence. Available throughout intake and discussion. |

All endpoints require the existing local workspace bearer key and same-origin
loopback access. Submission uses POST `questionnaire` with the schema version,
an idempotent `request_key`, `report_id`, `page_id`, nullable `visual_id`, the
`comparing` branch, description, and optionally a screenshot review ID. Reusing
an idempotency key with changed input refuses. Picked IDs must belong to their
selected report and page. A grouped visual does not imply a total or row key.
The existing controller asks once about an actual disagreement with the text;
it does not ask the user to repeat already-established picks.

Another report/page submissions retain both selections and stop with
`UNIMPLEMENTED_ROUTE`. The current procedure does not establish faithful
equivalence between these two requested scopes; the UI must not pretend that
two dropdowns implement the comparison. The optional source value remains a
user-supplied source claim, separately retained, never a displayed report figure
or independently attested source read.

## DECIDED WITHOUT REVIEW

A picked visual establishes identity and definition scope. Reading its current
quantity cannot establish what appeared on the user's screen with unknown
interactive selections. I rejected automatically transcribing a fresh query
result into `reported_figure`: that would manufacture a reproduction which
could not fail. Exact description spans or reviewed screenshot evidence supply
the reported figure; otherwise the existing missing-figure limitation stands.

Live report and page lists do not imply access to visual definitions. The
existing reader's tested Get Definition request returned HTTP404 EntityNotFound
(Round Twelve intake checkpoint), and the report-list adapter exposes reports
and pages only. I retained explicitly labelled approved visual titles rather
than calling them live or changing reader scope. This requested live-visual
part remains unmet; no new grant or publisher substitution is hidden here.

The old model-only selector, page-picture picker, separate value field, cell
mode/keys and extra comparison choices are hidden in the portal. Their code and
legacy `/forms` and `/questions` ports remain for compatibility and regression
coverage. Neither the oracle nor accepted targets changes to suit the new UI.

## Ticket lifecycle

The response contains a durable ticket ID. `/?ticket=ID` opens the same ticket
page for web/chat/API clients after local sign-in. It displays submitted facts,
retained process-stage progress, questions, discussion and saved outputs. A chat
submission ends with “Ticket submitted” and this link. Existing reply, finish,
close and handoff operations retain their revision fences and governed reads.

POST `tickets/ID/comments` requires `revision`, `request_key`, `text`, nullable
`attachment_id` and nullable `review_id`. The server fixes the caller as USER;
an API caller cannot impersonate the agent. Attachments are stored through the
existing screenshot service; a review must belong to the attached image. A
comment does not silently replace an admitted scope or launch a replacement
investigation. Agent screenshot requests use the same retained thread.
GET `tickets/ID/progress` reads saved events and makes no estate request.

POST `tickets/ID/screenshot-reply` explicitly uses a reviewed image to answer an
unresolved form's pending question. It requires the current revision, review ID
and idempotency key. It retains the earlier input and review provenance, checks
the existing description bound without truncation, and reruns the same admission
checks. An already-admitted scope cannot be replaced through this endpoint.
