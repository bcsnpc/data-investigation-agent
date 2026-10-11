# Billing report observation and ticket summary

Observed on 2026-10-09 America/Chicago (2026-10-10 UTC). Wrote 18 authored business-user tickets in tickets/. These are generated test tickets based on observations, not messages received from real customers or independently approved acceptance expectations.

## What was inspected

- Rendered Subscription Billing report, its Subscription Billing, Accounts and Recent Collections pages, visible cards and visible filter pane. Did not enter Edit, inspect model definitions, or read DAX.
- Overview cards: Invoiced Amount 950; Collected Amount 550; MRR All Plans 600; Churned Accounts 1; Usage Overage 600.
- Accounts: Top Accounts by Invoice Value remained without visible rows/amounts during the observed visits. Visible filters after selecting the visual: Account (All), Invoiced Amount (All). No account-specific report number was invented.
- Recent Collections: Collected in the Last Seven Days displayed "Error fetching data for this visual". The user-visible details said: "The filter on 'PaymentDate'[date] is not valid. Check that the data type of the 'PaymentDate'[date] field matches the filter you're trying to apply." This is a displayed error, not an independently established diagnosis.
- Read-only billing application lookups: accounts Aster, Birch, Cedar and Dune; their invoices, payments, subscription statuses, plan allowances/prices, usage and Aster's plan history. No lakehouse, warehouse, notebooks, pipelines or intermediate data were inspected.

## Application observations and arithmetic

- October 1 invoices: Aster 250 ISSUED, Birch 100 ISSUED, Cedar 250 ISSUED, Dune 100 VOID. All four sum to 700; issued invoices sum to 600.
- Payments: Aster invoice 101, 200 on October 2; Birch invoice 102, 100 on October 3; Cedar invoice 103, 250 on October 4. Sum 550.
- Active subscriptions: Aster Growth 250, Birch Starter 100, Cedar Growth 250. Sum 600. Dune Starter 100 is CHURNED; including it gives 700. One account has CHURNED status.
- Plan allowances: Starter 1000 units; Growth 3000 units. Usage: Aster 3500, Birch 1100, Cedar 2800, Dune 500. Total usage 7900. The explicitly hypothetical per-account excess calculation is 500 + 100 + 0 + 0 = 600; no model definition was inspected to confirm that this is the report's definition.
- Aster plan history: Starter September 1 through September 30; Growth from October 1.

## Scope and identity limits

The browser connection is now available. The existing Chrome Power BI session was admin@skynwhy.com; screenshots capture reading view through that session. They do not verify investigator-reader's report permissions or its RLS results. No sign-in, permission, report, model or data changes were made.

Application lookups used billing_tester_reader on billingapp only, with its existing Windows Credential Manager credential. No password was printed, copied into this folder or included in a ticket. First connection attempt returned "Database 'billingapp' on server 'sql-orderops-9696025.database.windows.net' is not currently available"; the subsequent connection succeeded. No cause is inferred from that transient failure.

No excluded defects, sealed records, oracle, expectations, acceptance inputs, engine scripts, tapes, ledgers or delivery records were opened or copied for this task. This is the continuing owner session, not the independent fresh tester session requested in tester-session-billing.md; the tickets must not be represented as blind independent testing.

Mix: exact application comparisons, correct-looking values needing clarification, freshness and date-scope questions, definition questions, visible errors, a blank Top Accounts visual, vague and typo tickets, a forwarded email and a ticket with competing comparison numbers. No matrix cell, chart point or slicer selection was invented: none was available in the inspected pages. Some tickets intentionally concern the same observed number with different user questions; they are not 18 distinct confirmed defects.

Screenshots are under screenshots/. The initial Accounts screenshot and the later Accounts screenshot preserve separate observed states. The source files and any existing independent tester work were not overwritten.
