# Business-user demo

This is the presenter flow to use instead of asking a user to compare technical
data layers. It runs against the same isolated order dataset throughout.

1. Open **Orders**. Payments are $253, refunds $99, retained amount $154.
2. Open **Reports**. The Net Cash report shows $55, with USD / all demo orders
   visibly selected. Save a PNG screenshot of this page and the Orders page.
3. Click **Ask about this report**. Enter: "The Net Cash amount on this report
   looks lower than expected. Can you check why?"
4. Attach the report screenshot and optionally the Orders screenshot. Click
   **Investigate this report**. No layer names or diagnosis are needed from the user.
5. The backend records receipt, report validation, record checks, calculation
   verification and completion. The UI polls actual persisted state; no simulated
   progress timer or staged result is used. Small demo checks finish quickly.
6. Show the business explanation, reported $55, expected $154, difference -$99,
   affected order ORD-000001 and suggested next step. Technical evidence is collapsed.

## Start

```powershell
Set-Location D:\data_investigation_agent
$businessDemo = '.local/business-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
python scripts/demo.py prepare --folder $businessDemo
python scripts/demo.py inject --folder $businessDemo
$env:INVESTIGATOR_API_TOKEN = [guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
Set-Clipboard -Value $env:INVESTIGATOR_API_TOKEN
python scripts/business_demo.py --folder $businessDemo --port 8773
```

Open http://127.0.0.1:8773 and paste the token to connect. The browser screenshots
must be PNG and smaller than 3 MB each. Stop the server before resetting:

```powershell
python scripts/demo.py reset --folder $businessDemo
Remove-Item Env:INVESTIGATOR_API_TOKEN
Set-Clipboard -Value ''
```

## Evidence and limits

Report snapshots, question, PNG attachment bytes, attachment hashes, case status
and real activity timestamps are retained in `business.sqlite` under the selected
folder. Detailed investigation evidence is in `evidence.sqlite`. Repeated identical
submission keys return the original case; changed requests with the same key are
rejected. Changed source fingerprints prevent a conclusion about a stale report.
An interrupted process leaves unfinished cases INTERRUPTED, without automatic retry.

These Orders and Reports pages are local demo views, not the deployed Azure portal
or Power BI UI. Their values are read from the shared isolated data, not static
screen mockups. The supported check is Net Cash / USD / all demo orders. The user's
question and screenshots are retained but do not determine scope: the selected
report supplies scope. Arbitrary screenshot interpretation/OCR, LLM-led scope
selection, and live report reconciliation remain pending. No external message,
issue or correction is applied. Production approval holds are not bypassed.

## Recorded acceptance

Browser case `bbc79219-bba9-432f-8e01-208503a9d693` completed with the expected
business result. Both stored attachment hashes matched the actual Orders and
Report screenshots byte for byte. No browser errors were reported. All 366 script
tests passed, including five new business-flow tests. Lab reset to READY afterward.

Recording: `.local/business-video/business-user-demo.mp4` (88 seconds, captioned,
no voiceover). Screenshots: `orders.png`, `report.png`, and `result.png` in the same
folder. These artifacts remain local and are not committed to GitHub.
