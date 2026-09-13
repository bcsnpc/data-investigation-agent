"""Validate the complete Gold output receipt against registered Silver inputs."""
from uuid import UUID

TABLES={'order_summary','order_line_summary','sales_daily','sales_by_customer',
        'sales_by_product','refund_summary','dim_date','dim_customer','dim_product'}


def validate(binding, report, root):
    if report.get('status')!='READY' or report.get('silver_binding')!=binding:
        raise ValueError('Ready Gold receipt with exact Silver binding required')
    UUID(report['run_id'])
    if report.get('silver_run_id')!=binding['report']['run_id']:
        raise ValueError('Silver run differs')
    if not report.get('checks') or not all(v is True for v in report['checks'].values()):
        raise ValueError('Gold checks did not pass')
    outputs=report.get('outputs',{})
    if set(outputs)!=TABLES or set(report.get('counts',{}))!=TABLES:
        raise ValueError('Complete nine-table Gold publication required')
    identities=set()
    for name,row in outputs.items():
        identity=str(UUID(row['delta_table_id']))
        if identity in identities or row['path']!=root+'/Tables/'+name:
            raise ValueError('Gold identity or path differs')
        identities.add(identity)
        if type(row.get('delta_version')) is not int or row['delta_version']<0:
            raise ValueError('Pinned Gold version required')
        if type(row.get('rows')) is not int or row['rows']<0 or row['rows']!=report['counts'][name]:
            raise ValueError('Gold count differs')
        if row.get('content_reconciled') is not True or not row.get('schema',{}).get('fields'):
            raise ValueError('Gold reconciliation/schema missing')
    return {'status':'SOURCE_TO_GOLD_PUBLISHED','gold_run_id':report['run_id'],
            'source_snapshot_id':binding['report']['bronze_binding']['source_snapshot_id'],
            'tables':len(outputs),'scope':'Publisher-reconciled pinned Gold outputs; semantic framing remains separate'}
