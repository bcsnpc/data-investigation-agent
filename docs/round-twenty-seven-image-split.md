# Pass 1 plumbing image split

Owner-approved 2026-11-20 (observed execution UTC Nov21). New old-image admissions stopped; three screenshot tickets already in flight are draining. The original image is f19ed639, source0b12e9e5. New sourcebe73c5ff contains only the two investigator plumbing repairs; the additional scoring-profile code was already used by the host graders and changes no investigator behavior. Qualification: https://github.com/bcsnpc/data-investigation-agent/actions/runs/44871935757 . Full suite is pending; all eight shards passed. No new-image investigation is admitted before full qualification.

Original outcomes, journals, captures and grades are unchanged. A split receipt will pin each outcome to its actual image. The effective mixed-image pass and the original-image observations will be reported separately. Calibration $14.34 and the existing $3 reserve remain protected.

The following trace-established cases may run once on the qualified repair image, subject to normal remaining-budget admission. They are labelled **plumbing defect**, not deleted or rewritten.

| Case | First wrong step | Evidence |
|---|---|---|
| form__v2-before-temporal-retention-v1 | query transport | Pure sys catalog SELECT denied by the transport as SQL_OBJECT_NOT_ALLOWED. |
| text__R17-09-v1 | query transport | Pure sys catalog SELECT denied by the transport as SQL_OBJECT_NOT_ALLOWED. |
| text__older-export-movement-1-v1 | query transport | Pure sys catalog SELECT denied by the transport as SQL_OBJECT_NOT_ALLOWED. |
| form__v2-record-absent-everywhere-v1 | query transport | Pure sys catalog SELECT denied by the transport as SQL_OBJECT_NOT_ALLOWED. |
| text__R17-08-v1 | delivery evaluator | First evaluator max_tokens; question/support/target true; claims absent, with no earlier substantive rejection. |

Malformed output alone does not qualify a case. In particular, a partial evaluator response that already rejects unsupported factual support is evidence of a conclusion/citation problem preceding the plumbing limitation; those cases are excluded from this one-time rerun list. No golden record or acceptance expectation changes.
