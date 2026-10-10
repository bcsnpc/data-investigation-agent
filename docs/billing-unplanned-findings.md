# Billing unplanned findings — 2026-10-10 UTC

The owner-authored ticket/screenshot capture was copied, hashed and committed before reading the sealed author-only inventory. All 25 source files match their committed Git blob hashes; capture manifest SHA-256 is `5d85963c56744a0c65d48a38669f0625f344098b2bcee8929f55a5924e40a682`. No ticket text was edited. Independent tester evidence is absent.

| Observed visual | Finding | Planned versus unplanned | Evidence |
|---|---|---|---|
| Recent Collections / Collected in the Last Seven Days | The rendered visual returns “Error fetching data for this visual”; visible details say “The filter on 'PaymentDate'[date] is not valid. Check that the data type of the 'PaymentDate'[date] field matches the filter you're trying to apply.” | **Unplanned build issue.** Sealed inventory item8 plans a relative-date restriction that the investigation adapter may refuse faithfully; it does not plan failure of the report renderer itself. The specific cause of the invalid filter is not established by the message alone. | Captured screens03/04; published visual d000098148395c529959 carries `type: RelativeDate`, date column PaymentDate.date and dynamic seven-day bounds. Published model declares that column dateTime. This rules out an intentionally absent field in the authored model; it does not prove service compatibility of the authored filter representation. |
| Accounts / Top Accounts by Invoice Value | The chart displays a title and blank plotting area without visible account values during the retained visits; visible filters show Account(All) and Invoiced Amount(All). | **Unplanned rendering/build symptom, cause unknown.** Inventory item8 plans Top2 ranking and possible adapter unsupported-form refusal, not an empty report. No proof that this is empty business data, a permanent failure, RLS, or the TopN predicate's correctness. | Captured screens02/05; published visual c0daabb8323e576e96a5 is clusteredBarChart with Account category, Invoiced Amount value and TopN subquery Top2. Baseline application invoices exist; overview Invoiced Amount renders950. |

Do not fix either issue in this round. The estate stays as captured for the runs. No expectations have been written for these symptoms: owner and reviewer decide them separately. Tickets08/09 and related date-scope/collections questions are owner-authored observations, not planted-defect acceptance claims.

## Row-level security evidence

The exact published authored model `fixture-code/billing/published-20261009/model.bim`, SHA-256 `145c628cf77a92ebb839aec30ca864c5c344efc9655b9ace57d8787a539dbd2a`, contains no `model.roles` collection and no row-security role declarations. The recorded model publication supplies this file as its model definition. **No RLS was authored/published in this fixture definition.** No administrator-versus-reader RLS comparison has been performed, and a later independent service edit has not been ruled out by the retained file alone. Screenshots came from `admin@skynwhy.com`, so they are not reader-access or reader-view verification. If live definition checking finds roles, record a dated correction; administrators' views may then differ from normal users.

No estate, permission, identity or engine change in this offline audit. No model calls or investigation run; draft #423 remains draft.

## Independent tester tickets ? sealed 2026-10-10 UTC

The fresh independent tester supplied15 text tickets (no .form.json or screenshots in the supplied tickets folder). Copied and committed unchanged before reading them or deriving expectations; capture manifest SHA256 `6b2dbf84c28987252ba78fe0cbc439040cd5810b7e11a90fd714623a70fbb6a1`, initial commit9659fe4 in draft#423. The owner explicitly attests independence; this session did not write them.

Six tickets touch the two unplanned rendering issues. No expectations for these symptoms have been derived from the sealed defect inventory; owner and reviewer must decide them.

| Independent tester ticket | Unplanned issue touched | Retained observation/question |
|---|---|---|
| ticket-07.txt | Blank Top Accounts | Title visible, no accounts/bars/values after revisiting; visible filters All. |
| ticket-08.txt | Blank Top Accounts | Show as a table also empty; requested Cedar's invoice row. |
| ticket-09.txt | Blank Top Accounts | Overview950 versus empty Accounts chart/table; cannot inspect contributors. |
| ticket-10.txt | Recent Collections error | Error fetching data for this visual; weekly figure unavailable, overview550. |
| ticket-11.txt | Recent Collections filter/rendering issue | Duration box appears empty with1-10000 hint and All summary despite seven-day title; no filter edit performed. This is a related observed build symptom, not an established cause of the error. |
| ticket-12.txt | Recent Collections error | Error prevents checking date boundaries; asks October2 versusOctober3 inclusion. |

The other nine tickets remain available for later expectation review and scoring. This classification is not an outcome expectation. Preserve all15 independent tickets and all18 owner-authored tickets separately, including unplanned-issue tickets; pending owner/reviewer expectations are reported as pending, never counted as a pass or failure. Report separate scores for each evidence class, followed by a clearly labelled combined result with each class's numerator/denominator retained. No tickets have been investigated in this capture step.
