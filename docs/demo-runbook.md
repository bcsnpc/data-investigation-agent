# Investigator demo: ticket to evidence to defect draft

For a business audience, use the [business-user demo](business-user-demo.md):
Orders -> report screenshot -> plain-language question -> investigation -> result.
The operator review flow below remains available for a technical audience.

## What this demonstration proves

This is a repeatable, isolated demonstration of the existing investigator review
UI, ticket API, approval, worker, record comparison, local cause verification and
defect-draft preparation. The scenario subtracts a refund twice in Gold.
It uses three coherent fixture orders and the shared Gold transformation logic.
It does not modify the live 100,000-order SQL/Fabric estate.

The lab planner uses a fixed USD / Net Cash / all-orders scope, not an LLM.
Narrative text does not change that scope. The UI identifies this explicitly.
The verified cause is local replay evidence, not a production root-cause claim.

## Start a fresh presentation

In PowerShell, from the existing configured project environment:

```powershell
Set-Location D:\data_investigation_agent
$demoFolder = '.local/demo-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
python scripts/demo.py prepare --folder $demoFolder
python scripts/demo.py inject --folder $demoFolder
$env:INVESTIGATOR_API_TOKEN = [guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
Set-Clipboard -Value $env:INVESTIGATOR_API_TOKEN
python scripts/demo.py serve --folder $demoFolder --port 8772
```

Open http://127.0.0.1:8772 and paste the token into Connect. Keep PowerShell
running. If port 8772 is occupied, stop the earlier demo or select another port.
Injection reports NOT_READY because the fixture intentionally differs from its
baseline. This is expected. No cloud credentials are required for the lab.

## Eight-minute presentation

1. **Context (one minute).** Explain that the live estate has 100,000 related
   orders, SQL ingestion, Fabric layers, a semantic model and reports. You may
   show the existing [orders portal](https://orderops-portal-9696025.azurewebsites.net)
   and [Fabric workspace](https://app.powerbi.com/groups/09cea7db-63ec-41f0-9cf0-872a6dc5c61d/list).
   These require their existing logins and are optional context; their current
   availability is not part of the isolated rehearsal acceptance.
2. **State the boundary.** Say: "I will now reproduce a controlled defect in an
   isolated dataset so we can demonstrate evidence and approval safely."
3. **Submit (one minute).** Expand Start a new investigation. Title: `Net cash
   is USD 99 too low`. Report: `Lab Net Cash`. Leave page and order blank.
   Description: `Compare Silver and Gold net cash in USD and explain affected
   orders.` Click Submit ticket, then Generate draft.
4. **Review (one minute).** Open the draft. Verify Net Cash, USD, all orders.
   Check the confirmation box and click Approve and queue. The UI opens the
   approved child ticket. Refresh status after a few seconds if needed.
5. **Evidence (two minutes).** Show COMPLETED / TECHNICAL_DEFECT. Silver total
   is 154.0000; Gold is 55.0000; difference is -99.0000 USD. ORD-000001 is
   affected. The local replay verifies that the refund was subtracted twice.
   Explain that a mismatch alone would not prove a cause; replay supplies the
   additional evidence for this supported scenario.
6. **Draft (one minute).** Click Prepare routing review. Show the proposed
   defect, affected order, impact and simulated Demo Data Team owner. Leave it
   awaiting review. No GitHub issue or email is sent by this demo.
7. **Close (one minute).** State the remaining production gaps from
   [demo-pending.md](demo-pending.md). Do not present the fixed lab planner as
   autonomous LLM reasoning or this local replay as live Power BI verification.

## Reset and repeat

Press Ctrl+C in the server PowerShell, then:

```powershell
python scripts/demo.py reset --folder $demoFolder
Remove-Item Env:INVESTIGATOR_API_TOKEN
Set-Clipboard -Value ''
```

Reset must return READY. Saved tickets, findings and drafts remain available in
the folder for review. Use a fresh timestamped folder for the next presentation.
The server processes one approved investigation per session; it stops processing
after that job or after 15 minutes. Restart for another session.

## Automated rehearsal / fallback evidence

```powershell
$rehearsalFolder = '.local/rehearsal-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
python scripts/demo.py rehearse --folder $rehearsalFolder
Get-Content "$rehearsalFolder/rehearsal.json"
```

This drives the real review API and worker in-process, checks the classification
and impact, prepares the draft and resets even on failure. PASSED is printed
only after the complete path succeeds. The saved JSON includes ticket, plan,
investigation, draft and reset evidence. Existing folders are never overwritten.
It is a fallback evidence record, not a substitute for the browser presentation.
