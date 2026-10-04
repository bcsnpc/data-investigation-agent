"""Build fixture audit rows exclusively from the copy activity's own output."""
import json


def copy_accounting(output_json):
    """Keep missing/invalid output distinct from a completed zero-row copy."""
    try:
        output = json.loads(output_json) if output_json else None
    except (TypeError, ValueError):
        output = None
    if not isinstance(output, dict):
        output = {}
    # InvokeCopyJob returns completed copy-activity records inside value. Do not
    # choose one out of several mappings, or accept an incomplete paged result.
    activity = None
    if "value" in output:
        entries = output["value"]
        if (isinstance(entries, list) and len(entries) == 1
                and not output.get("continuationToken")
                and isinstance(entries[0], dict)
                and entries[0].get("status") == "Succeeded"
                and isinstance(entries[0].get("output"), dict)):
            activity = entries[0]
            output = activity["output"]
        else:
            output = {}
    read, written = output.get("rowsRead"), output.get("rowsCopied")
    observed = all(type(n) is int and 0 <= n <= 2**63 - 1 for n in (read, written))
    def text(name):
        value = output.get(name)
        return value if isinstance(value, str) and value else None
    return {
        "copy_run_id": text("runId") or text("copyJobRunId"),
        "start_time_utc": (activity or {}).get("activityRunStart") or text("startTime"),
        "end_time_utc": (activity or {}).get("activityRunEnd") or text("endTime"),
        "rows_read": read if observed else None,
        "rows_written": written if observed else None,
        "high_watermark": text("highWatermark"),
        "accounting_state": "OBSERVED_COPY_OUTPUT" if observed else "UNAVAILABLE_COPY_OUTPUT",
        "watermark_state": "OBSERVED_COPY_OUTPUT" if text("highWatermark") else "UNAVAILABLE_COPY_OUTPUT",
    }
