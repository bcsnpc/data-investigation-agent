# Independent billing rendering tickets for owner and reviewer

2026-10-10. These six tickets are copied verbatim from the independently captured tester files. No outcome expectation has been assigned. Nothing below is taken from the sealed defect list.

## What is established about the rendering symptoms

Recent Collections displays ?Error fetching data for this visual?. The retained error details are: ?The filter on 'PaymentDate'[date] is not valid. Check that the data type of the 'PaymentDate'[date] field matches the filter you're trying to apply.? The retained published definition references PaymentDate.date, and the published model declares that column dateTime. The definition uses a relative-date filter. The message establishes a filter/rendering failure; the precise incompatibility has not been proved. No fix has been applied.

Top Accounts shows its title but no bars, accounts or values; Show as a table was also empty. Visible Account and Invoiced Amount filters were All. The retained definition binds Account and Invoiced Amount. Overview displayed an invoice value, so empty business data has not been established. The cause of the empty chart/table remains unknown. This is not evidence of a particular pipeline defect or row-security behavior.

Screenshots were captured in the administrator's browser, not as diagnostic-reader proof. The retained published model has no authored RLS roles; a later service edit has not been independently excluded.

## Verbatim independent tickets

### ticket-07.txt

```text
Top accounts is just blank

Report: Subscription Billing
Page: Accounts
Visual: Top Accounts by Invoice Value

I can see the title but no account names, bars or values. I left the page, looked at Recent Collections and came back; it was still blank. The visible Account and Invoiced Amount filters both say (All).

There are invoices in the application for Aster, Birch and Cedar. I expected to see a ranking with some accounts on it, even if the list only shows a few.
```

### ticket-08.txt

```text
can't get Cedar's row

i tried Show as a table on Top Accounts by Invoice Value and that was empty too. no rows or total that i could read.

Cedar has invoice 103 for 250 on October 1 in the app. I wanted to check Cedar's row rather than guess from a chart, but couldn't find it. Can we get the account values visible in the table view?
```

### ticket-09.txt

```text
Overview has 950 but Accounts has nothing to check it against

Subscription Billing's first page shows Invoiced Amount 950. On Accounts, Top Accounts by Invoice Value gives me an empty chart and the table view is empty too.

I expected the account page to show at least the biggest contributors to the first-page amount. It currently looks like one page has invoices and the other has none. I can't explain the total to the team from these two pages.
```

### ticket-10.txt

```text
FW: Weekly collections update - number unavailable

Subject: FW: Weekly collections update
Priority: normal

Hello,

On Subscription Billing > Recent Collections, Collected in the Last Seven Days says "Error fetching data for this visual". I can't read a weekly collection amount at all. The main Subscription Billing page does show Collected Amount 550.

Please get the recent figure visible, or tell us when we can use it for the weekly update. I expected a number, including zero if there are no payments in the period.

Regards,
Operations
--- forwarded for the morning review ---
No attachment.
```

### ticket-11.txt

```text
Seven-day title but the number of days looks empty

On Recent Collections I selected the collection visual and expanded its date filter. It says "is in the last", then the duration box looks empty with a "1-10000" hint, then "days". Include today is checked. The filter summary says is (All).

The visual is titled Collected in the Last Seven Days. I expected to see 7 in that box or a clear date range. Can you confirm what period this view is meant to use? I didn't enter or apply a different value.
```

### ticket-12.txt

```text
Which day drops out of the recent payment figure?

The recent collections date filter has Include today checked. In the app, payments are Aster 200 on October 2, Birch 100 on October 3 and Cedar 250 on October 4.

For a seven-day check on October 9, should October 2 still count, or does the period start on October 3? That makes a difference between 550 and 350. The visual currently errors so I can't check it there. I expected the start and end dates to be visible so we all use the same weekly number.
```
