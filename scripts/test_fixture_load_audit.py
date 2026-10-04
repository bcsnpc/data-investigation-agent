import json
import unittest

from fixture_load_audit import copy_accounting


class CopyAccountingTests(unittest.TestCase):
    def test_failed_invocation_without_output_is_recordable_not_zero(self):
        for output in ("", "null", "[]", "broken json", "{}"):
            with self.subTest(output=output):
                row = copy_accounting(output)
                self.assertEqual(row["accounting_state"], "UNAVAILABLE_COPY_OUTPUT")
                for field in ("rows_read", "rows_written", "start_time_utc", "end_time_utc", "high_watermark"):
                    self.assertIsNone(row[field])

    def test_zero_is_observed_but_not_a_substitute_for_missing(self):
        row = copy_accounting('{"rowsRead":0,"rowsCopied":0}')
        self.assertEqual(row["accounting_state"], "OBSERVED_COPY_OUTPUT")
        self.assertEqual((row["rows_read"], row["rows_written"]), (0, 0))

    def test_only_own_output_establishes_counts(self):
        for output in ({"rowsRead":True,"rowsCopied":2}, {"rowsRead":2,"rowsWritten":2},
                       {"rowsRead":-1,"rowsCopied":2}, {"rowsRead":"2","rowsCopied":2},
                       {"rowsRead":2**63,"rowsCopied":2}):
            self.assertEqual(copy_accounting(json.dumps(output))["accounting_state"], "UNAVAILABLE_COPY_OUTPUT")

    def test_no_watermark_or_timestamps_invented_from_audit_time(self):
        row = copy_accounting('{"rowsRead":4,"rowsCopied":3,"startTime":"start","endTime":"end","highWatermark":"cut"}')
        self.assertEqual((row["rows_read"],row["rows_written"]), (4, 3))
        self.assertEqual((row["start_time_utc"],row["end_time_utc"],row["high_watermark"]), ("start","end","cut"))

    def test_live_invoke_shape_retains_activity_owned_counters(self):
        row = copy_accounting(json.dumps({"value":[{"id":"opaque", "status":"Succeeded",
            "activityRunStart":"start", "activityRunEnd":"end",
            "output":{"rowsRead":4,"rowsCopied":3,"watermarkInfo":None}}],"continuationToken":None}))
        self.assertEqual((row["rows_read"],row["rows_written"]), (4,3))
        self.assertEqual((row["start_time_utc"],row["end_time_utc"]), ("start","end"))
        self.assertIsNone(row["high_watermark"])
        self.assertIsNone(row["copy_run_id"])

    def test_no_selection_or_summing_from_ambiguous_or_paged_invocation(self):
        good = {"status":"Succeeded","output":{"rowsRead":4,"rowsCopied":3}}
        for wrapper in ({"value":[good,good]}, {"value":[good],"continuationToken":"more"},
                        {"value":[{"status":"Failed","output":good["output"]}]}):
            row = copy_accounting(json.dumps(wrapper))
            self.assertEqual(row["accounting_state"], "UNAVAILABLE_COPY_OUTPUT")
            self.assertIsNone(row["rows_read"])


if __name__ == "__main__":
    unittest.main()
