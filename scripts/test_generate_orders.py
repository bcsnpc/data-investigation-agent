import contextlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from generate_orders import allocate, generate, validate

class BaselineTests(unittest.TestCase):
 def test_allocation_preserves_cents(self):
  self.assertEqual(allocate(10,[1,1,1]),[4,3,3])
  self.assertEqual(allocate(0,[100,200]),[0,0])

 def test_reproducible_and_rejects_corruption(self):
  with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
   a,b = Path(tmp)/'a',Path(tmp)/'b'
   generate(a,200,42)
   generate(b,200,42)
   self.assertEqual(json.loads((a/'manifest.json').read_text()),json.loads((b/'manifest.json').read_text()))
   conn = sqlite3.connect(a/'baseline.sqlite')
   mutations = [
    ("UPDATE order_lines SET line_total='0.00' WHERE rowid=1", 'line tax rounding|line arithmetic'),
    ("UPDATE orders SET customer_id='MISSING' WHERE rowid=1", 'customer chronology'),
    ("UPDATE refunds SET refund_amount='99999999.00' WHERE rowid=1", 'refund payment linkage'),
    ("UPDATE orders SET status='IMPOSSIBLE' WHERE rowid=1", 'current status'),
   ]
   for sql,expected in mutations:
    with self.subTest(expected=expected):
     conn.execute('SAVEPOINT corruption')
     conn.execute(sql)
     try:
      with self.assertRaisesRegex(ValueError,expected): validate(conn)
     finally:
      conn.execute('ROLLBACK TO corruption')
      conn.execute('RELEASE corruption')
   conn.close()

if __name__ == '__main__': unittest.main()
