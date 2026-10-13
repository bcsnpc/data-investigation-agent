# Investigation playbook (owner design, 2026-10-12)

This is how the tool must handle every ticket, as an experienced BI
analyst would. Round eighteen builds toward it.

## Intake

- **Report name: required.**
- **Pages:** the user selects one or more.
- **Screenshots:** the user can upload several.
- **Description:** free text, in the user's own words.
- Comparison or expected value: optional.
- From the screenshots and description, the tool identifies the
  visual or visuals the user means, using the estate graph (titles,
  labels, numbers and visible slicer values).
- **Hidden filters** (visual, page and report filters, filter steps
  in Power Query or views, filters inside measures, RLS) are already
  in the graph. The tool applies them itself and never asks about
  them.
- **Ask immediately** when the tool can't understand the question, or
  can't tell which filters the user applied. Ask one plain question,
  using the names the user sees.

## Step 1: recreate the user's scenario first

Before any investigation, reproduce what the user saw: run the
visual's query with the same report, page, visual, the slicer and
filter values the user applied, and, where possible, the user's
security context (RLS). Then compare the result with the screenshot.

| Recreated result | What it means | What the tool does |
|---|---|---|
| **Matches the screenshot** | The number is real; the data really shows this | Go to step 2 |
| **Differs from the screenshot, and looks right** | The user saw an older or cached view | Rule out other causes first: different filters, a different RLS role, a refresh since the screenshot was taken. Then tell the user it looks like stale data on their side, ask them to refresh the browser or reset the report to default, and check again. **No further runs.** |
| **Differs from the screenshot, and still looks wrong** | The data changed since the screenshot, or the filters differ | Confirm the filters with the user if unsure, then go to step 2 using the current numbers |

## Step 1b: recreate the comparison, when there is one

What the tool does depends on what the user compares with:

| User compares with | What the tool does |
|---|---|
| **Another report, or another page of the same report** | **Recreate it too:** run that visual's query with the same filters, and check it matches what the user saw |
| **The source system** ("Epic shows 5", "the app shows 650") | **Recreate it too, by reading the source directly:** query the source tables with the same filters and scope. If the source app's screen applies its own logic and the direct read doesn't match the user's figure, ask which screen or report they used. |
| **A spreadsheet or export** | Don't recreate. Use the user's figure, or the uploaded file's total or record list, as given. |
| **Their own count** | Don't recreate. Use the number as given; ask for record IDs only for a records complaint. |
| **An earlier value** ("it showed 10 yesterday") | Don't recreate. Use table and refresh history to see what changed. |

Then compare the two paths on the estate graph: where do their rules,
filters, timing or grain differ?

- **Each side is correct by its own design:** an expected difference.
  Explain exactly why. If the user needs the numbers to match, they
  raise an enhancement request.
- **One side is wrong against its design:** a data problem. Follow that
  side down the layers to the step that breaks.

## Step 2: investigate against what the user expects

- **No reference given** ("looks wrong", "count is less"): run the whole
  lineage end to end. Confirm, layer by layer, whether the number is
  correct **as designed**. Report either the step where it departs
  from the design, or that it is consistent end to end.
- **Comparison given** (another report, the source app, a
  spreadsheet, the user's own count):
  - **If the number is wrong against the design:** a data defect. Name
    the layer and the step, with evidence.
  - **If the number is correct as designed but differs from the
    comparison:** explain exactly what causes the difference (a
    different rule, filter, timing or grain). Tell the user that if
    they need the numbers to match, they should raise an enhancement
    request. That decision is theirs.
- **Stale data or refresh delay:** last model refresh, last pipeline
  and notebook runs, last load time per layer, and where the delay
  starts.

## Step 3: always hand over to the dev team

Every ticket, whatever its ending, includes a **technical evidence
pack** for developers:

- what the tool did, step by step;
- the exact queries it ran (DAX and SQL), at each layer, with their
  results;
- the lineage path and filters applied, including hidden ones;
- where it stopped and why, if it held.

This lets a developer take over at any point without redoing the work.

## Architecture: focused agents, linked by a shared case file (owner proposal, to be proven by test)

**Status: proposal.** Adopt it only after an A/B test on the same
tickets (about 20, using saved and real-style tickets): the current
design against focused agents. Compare tickets resolved correctly,
harmful findings (which must stay at 0), cost, and time. Research
(2026-10-12) supports focused context for query writing and parallel
read-only work, but also reports that multi-agent gains are often
small, and that most failures come from vague hand-offs, agents
working on conflicting assumptions, and weak verification. The rules
below target exactly those failure modes.

Each activity is done by a **focused agent with a small context**. An
analyst gets good queries from a short, focused prompt. One agent
carrying everything gets worse results.

| Agent | Sees only | Produces |
|---|---|---|
| **Intake** | Screenshots, description, the graph's labels for that report | The claim: visual or visuals, metric, user filters, comparison, what's unclear |
| **Recreate** | The claim plus the visual's definition and filters from the graph | A DAX query, its result, and whether it matches the screenshot |
| **Fabric query** | One layer's table and columns from the graph, the filters, the number to compare | One SQL or Spark query plus its result |
| **Azure SQL query** | The source table and columns, the filters, the number to compare | One SQL query plus its result |
| **Analyst (consolidator)** | Only the compact per-layer results and evidence IDs | Where the number diverges, what to drill into next, and the ending |
| **Business presenter** | The analyst's conclusion, scoped to the user's RLS | A plain-language answer in the report's own labels |
| **Technical presenter** | The full evidence | The developer evidence pack: queries, results, path, filters |

**How they are linked (this is what makes it safe):**

- **A shared case file per ticket,** stored in the database. Agents
  never talk to each other directly. Each reads only the part of the
  case file it needs and writes its result back, with evidence IDs.
- **Code is the orchestrator**, not an LLM. It decides which agent runs
  next, runs independent agents in parallel (Fabric and Azure SQL
  layers at the same time), and stops on budget or step caps.
- **Every agent output is checked by code before it's saved:**
  - queries must pass the read-only guardrail parser;
  - results are stored as facts with evidence IDs;
  - the analyst may only cite evidence IDs that exist;
  - presenters may only restate the analyst's validated conclusion.
- **Decisions are made in one place.** Agents report facts; only the
  analyst concludes. That avoids separate agents making conflicting
  assumptions.
- **Agents are used only where they add something.** If the graph gives
  a direct path, code builds the query and no agent is needed. Query
  agents are for dynamic or unusual logic.
- **Different models per agent** where it helps: a cheaper model for
  query writing, a stronger one for the analyst.
- **Each agent is tested on its own,** with its own saved examples.

## Static vs dynamic

- **Direct paths** (a plain measure with known filters): code queries
  each layer.
- **Dynamic logic** (context-dependent DAX, slicer-driven `SWITCH` or
  `SELECTEDVALUE`, field parameters, calculation groups, interactions,
  RLS by user, dynamic SQL or Python): the LLM interprets it using the
  graph, the screenshot and the code. **Code then verifies the
  interpretation by running the query and matching the screenshot
  number** before anything is claimed. Each resolved path is saved to
  the graph.
