# Round Ten D — recorded character audit

Updated 2026-10-08 America/Chicago. Zero provider calls and zero estate requests. All 35 recorded requests are decoded without altering their tapes.

The 7,997,743 daily total includes 5,276,574 characters reserved before this batch. This batch reserved 2,721,169, or **77,747.69 per call**, not 228k. Provider wire size and the governor reservation are separate measurements. No counter was corrected or refunded.

| Component | Mean characters |
| --- | --- |
| instructions | 8,311.66 |
| ticket_text | 232.49 |
| visuals | 9,211.00 |
| metadata | 29,560.00 |
| other_input | 327.77 |
| input_syntax | 178.77 |
| schema | 6,447.00 |
| fixed | 171.00 |
| escaping_and_wire_syntax | 4,767.66 |
| wire | 59,207.34 |
| reserved | 77,747.69 |

Model metadata excludes visual arrays; examples=0 denotes no separate example block (inline examples remain counted in instructions). Other input holds the consumer-owned enums and route flags plus retry detail when present. Input syntax and outer escaping are measured separately so each row sums exactly to the recorded request size.

The dominant component is model metadata, including all models, measures, typed columns and native table identifiers. The whole-catalog snapshot dates to c7c7b208; ef ace31e (spelled `eface31e`) added the per-model complete visual inventory on 2026-10-07. The latter adds visual cost but is not the largest component. Round Ten C also increased instructions 7,732→8,291 and schema 6,261→6,289 on its controlled before/after input; it did not create the whole-catalog expansion.

| Ticket / attempt | Prompt | Ticket | Visuals | Model metadata | Other input | Input syntax | Schema | Fixed options | Escaping/syntax | Request | Reserved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| family-A-mention/1 | 8291 | 285 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59220 | 77784 |
| family-A-noisy/1 | 8291 | 377 | 9211 | 29560 | 315 | 181 | 6447 | 171 | 4771 | 59324 | 77882 |
| family-A-terse/1 | 8291 | 103 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59038 | 77602 |
| family-A-typo/1 | 8291 | 132 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59067 | 77631 |
| family-B-noisy/1 | 8291 | 393 | 9211 | 29560 | 315 | 181 | 6447 | 171 | 4771 | 59340 | 77898 |
| family-B-terse/1 | 8291 | 119 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59054 | 77618 |
| family-B-typo/1 | 8291 | 154 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59089 | 77653 |
| family-C-noisy/1 | 8291 | 372 | 9211 | 29560 | 315 | 181 | 6447 | 171 | 4771 | 59319 | 77877 |
| family-C-terse/1 | 8291 | 97 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59032 | 77596 |
| family-C-typo/1 | 8291 | 133 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59068 | 77632 |
| family-D-noisy/1 | 8291 | 402 | 9211 | 29560 | 315 | 181 | 6447 | 171 | 4771 | 59349 | 77907 |
| family-D-terse/1 | 8291 | 128 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59063 | 77627 |
| family-D-typo/1 | 8291 | 163 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59098 | 77662 |
| family-E-mention/1 | 8291 | 306 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59241 | 77805 |
| family-E-noisy/1 | 8291 | 398 | 9211 | 29560 | 315 | 181 | 6447 | 171 | 4771 | 59345 | 77903 |
| family-E-terse/1 | 8291 | 124 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59059 | 77623 |
| family-E-typo/1 | 8291 | 153 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59088 | 77652 |
| family-F-noisy/1 | 8291 | 391 | 9211 | 29560 | 315 | 181 | 6447 | 171 | 4771 | 59338 | 77896 |
| family-F-terse/1 | 8291 | 117 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59052 | 77616 |
| family-F-typo/1 | 8291 | 152 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59087 | 77651 |
| family-G-mention/1 | 8291 | 355 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59290 | 77854 |
| family-G-noisy/1 | 8291 | 447 | 9211 | 29560 | 315 | 181 | 6447 | 171 | 4771 | 59394 | 77952 |
| family-G-terse/1 | 8291 | 173 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59108 | 77672 |
| family-G-typo/1 | 8291 | 202 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59137 | 77701 |
| family-H-noisy/1 | 8291 | 417 | 9211 | 29560 | 315 | 181 | 6447 | 171 | 4771 | 59364 | 77922 |
| family-H-noisy/2 | 8532 | 417 | 9211 | 29560 | 464 | 205 | 6447 | 171 | 4782 | 59789 | 78091 |
| family-H-terse/1 | 8291 | 143 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59078 | 77642 |
| family-H-terse/2 | 8532 | 143 | 9211 | 29560 | 464 | 199 | 6447 | 171 | 4776 | 59503 | 77811 |
| family-H-typo/1 | 8291 | 178 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59113 | 77677 |
| family-H-typo/2 | 8532 | 178 | 9211 | 29560 | 464 | 199 | 6447 | 171 | 4776 | 59538 | 77846 |
| family-I-noisy/1 | 8291 | 401 | 9211 | 29560 | 315 | 181 | 6447 | 171 | 4771 | 59348 | 77906 |
| family-I-terse/1 | 8291 | 127 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59062 | 77626 |
| family-I-typo/1 | 8291 | 158 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59093 | 77657 |
| question-change-days/1 | 8291 | 154 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59089 | 77653 |
| question-change-week/1 | 8291 | 145 | 9211 | 29560 | 315 | 175 | 6447 | 171 | 4765 | 59080 | 77644 |
