# Delivery output composition

2026-10-04, Round Four A4. Engine-owned load accounting uses singular row/was
for one absent source row, plural rows/were for zero or more than one, and correct
row/rows for the activity's own counters. The gap filler sentence is removed;
the recorded delivery account states the finding directly.

Pre-run output inspection also found that the source-consistency branch omitted
its existing delivery/membership accounts. It now preserves those accounts, so
the business output can state expected-record absence rather than only agreement
of totals. No new membership inference or outcome eligibility was added.

Validation: 13 delivery, 11 system-of-record and 9 synthesis-narrative tests passed.
Tests cover zero/one/two grammar, filler exclusion and membership-account retention.
No investigation or cloud read, no ledger row. No planner catalog content is added;
directory/SQL coverage is unchanged. Engine bytes changed; prior freezes invalidated.
The two consistency scenarios remain to be run after all fixes merge.
