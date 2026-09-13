"""Compare the captured SQL order trace with the notebook's pinned Bronze trace."""
import json
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = json.loads((root/'.local/source-order-trace.json').read_text())
report = json.loads((root/'.local/fabric-silver-report.json').read_text())
mapping = {'orders':('order',['order_id']), 'order_lines':('lines',['order_line_id']),
 'payments':('payments',['payment_id']), 'shipments':('shipments',['shipment_id']),
 'shipment_lines':('shipmentLines',['shipment_id','order_line_id']),
 'refunds':('refunds',['refund_id']), 'refund_lines':('refundLines',['refund_id','order_line_id']),
 'audit_log':('audit',['event_id'])}
def normalize(value):
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value,(float,int)):
        return Decimal(str(value))
    if isinstance(value,str) and re.fullmatch(r'-?\d+(\.\d+)?',value):
        return Decimal(value)
    if isinstance(value,str) and re.match(r'^\d{4}-\d{2}-\d{2}[T ]',value):
        return datetime.fromisoformat(value.replace('Z','+00:00')).replace(tzinfo=None)
    return value
results={}
for table,(field,keys) in mapping.items():
    rows=source[field] if isinstance(source[field],list) else [source[field]]
    indexed={tuple(row[k] for k in keys):row for row in rows}
    observed=report['sample_order'][table]
    assert len(observed)==len(rows), f'Row count mismatch: {table}'
    for row in observed:
        other=indexed[tuple(row[k] for k in keys)]
        for column,value in row.items():
            assert column in other and normalize(value)==normalize(other[column]), f'Mismatch: {table}.{column}'
    results[table]=len(rows)
print(json.dumps({'order_id':'ORD-000002','result':'PASS','matched_rows':results}))
