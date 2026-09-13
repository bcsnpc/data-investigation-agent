"""Validate a completed Silver receipt against its trusted Bronze binding."""
from uuid import UUID

SOURCES = dict(zip(
    ('dim_customer','dim_product','fact_order','fact_order_line','fact_payment','fact_shipment',
     'fact_shipment_line','fact_refund','fact_refund_line','fact_audit_event'),
    ('customers','products','orders','order_lines','payments','shipments',
     'shipment_lines','refunds','refund_lines','audit_log')))


def validate(binding, report, silver_root):
    if report.get('status') != 'READY' or report.get('bronze_binding') != binding:
        raise ValueError('Ready Silver receipt with exact input binding required')
    UUID(report['run_id'])
    outputs = report.get('outputs', {})
    if set(outputs) != set(SOURCES):
        raise ValueError('Complete Silver output mapping required')
    inputs = {r['source_table']:r for r in binding['tables']}
    identities = set()
    for name, row in outputs.items():
        identity = str(UUID(row['delta_table_id']))
        if identity in identities or row['path'] != silver_root+'/Tables/'+name:
            raise ValueError('Silver identity or destination differs')
        identities.add(identity)
        if type(row.get('delta_version')) is not int or row['delta_version'] < 0:
            raise ValueError('Pinned Silver version required')
        if type(row.get('rows')) is not int or row['rows'] != inputs[SOURCES[name]]['rows']:
            raise ValueError('Silver grain differs')
        if row.get('content_reconciled') is not True or not row.get('schema', {}).get('fields'):
            raise ValueError('Silver reconciliation and schema required')
    return {'status':'SOURCE_TO_SILVER_PUBLISHED','source_snapshot_id':binding['source_snapshot_id'],
            'silver_run_id':report['run_id'],'tables':len(outputs),
            'rows':sum(r['rows'] for r in outputs.values()),
            'scope':'Publisher-reconciled pinned Silver outputs; Gold/model propagation remains incomplete'}
