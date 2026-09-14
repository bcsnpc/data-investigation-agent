# Isolated demo acceptance

Rehearsed on 2026-09-14 using the existing review UI/API, worker and cause verifier.

| Check | Result |
| --- | --- |
| Automated ticket -> plan -> approval -> worker | PASSED |
| Saved local TECHNICAL_DEFECT with verified double-refund cause | PASSED |
| Silver 154 / Gold 55 / difference -99 USD, one affected order | PASSED |
| Review-only draft with simulated owner; no external delivery | PASSED |
| Browser login, ticket submission, scope review and approval | PASSED |
| Browser completed evidence and routing draft display | PASSED |
| Browser errors | None reported |
| Lab reset | READY |

Automated evidence: `.local/demo-acceptance-143/rehearsal.json`.
Browser evidence stores: `.local/demo-presenter/review/review.sqlite` and
`review-workflow.sqlite`. Browser investigation:
`8420f784-199c-4fc3-856b-f711a2b9d669`; approved ticket:
`8a121518-02d8-44a5-8e78-4d9b4b63ea8b`.
These ignored local artifacts are retained on the development machine.

The browser server was stopped and its temporary token removed after verification.
Use the [runbook](demo-runbook.md) to launch a fresh presentation. No live SQL,
Fabric, LLM, issue delivery or email call was part of this acceptance. Optional
live portal/report context was not revalidated in this rehearsal. See
[remaining work](demo-pending.md) for the production boundaries.
