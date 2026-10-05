"""Receipt-first process accounting, independent of validated conclusions."""
from .onboarding import digest

SQL = {'bounded_sql', 'bounded_fabric_sql', 'source', 'source_records'}
SQL.update({'sql_identity','sql_database_permissions','sql_object_permissions','sql_quantity','sql_connection','sql_connection_retry'})
GUARDS = {'sql_identity','sql_database_permissions','sql_object_permissions'}
DAX = {'bounded_dax', 'native', 'native_records'}


def receipt(sequence, tool, result, error_type=None):
    body = result if isinstance(result, dict) else {}
    status = body.get('status')
    if status is None:
        status = 'COMPLETED' if body and not error_type else 'UNCERTAIN'
    return {'sequence': sequence, 'tool': tool, 'status': status,
            'receipt_id': body.get('id') if tool in SQL | DAX else None,
            'result_hash': digest(result) if result is not None else None,
            # Metadata responses have no query-receipt table. Retain their body
            # here; transports return bounded metadata, never auth headers.
            'metadata_response': body if tool not in SQL | DAX else None,
            'guard_receipt':body.get('guard_receipt'), 'error_type': error_type}


def accounting(state):
    """Count completed/failed attempts; never turn an unreturned read into success."""
    entries = state.get('physical_read_receipts',state.get('process_read_receipts'))
    if entries is None:
        entries = [o for o in state.get('observations', [])
                   if o.get('tool') in SQL | DAX and o.get('status') == 'COMPLETED']
    sql = sum(e['tool'] in SQL for e in entries)
    dax = sum(e['tool'] in DAX for e in entries)
    return {'reads_sql': sql, 'reads_dax': dax, 'reads_other': len(entries)-sql-dax,
            'reads_total': len(entries), 'physical_requests':len(entries),
            'guard_requests':sum(e['tool'] in GUARDS for e in entries),
            'connection_retry_requests':sum(e['tool']=='sql_connection_retry' or e.get('logical_tool')=='sql_connection_retry' for e in entries),
            'diagnostic_reads':state.get('cloud_calls',0) if state.get('read_accounting_version')=='diagnostic-operations-v1' else None,
            'guard_reuses':sum(e['status']=='REUSED' for e in state.get('guard_evidence',[])),
            'diagnostic_read_cap':state.get('envelope',{}).get('limits',{}).get('cloud_calls'),
            'reads_completed': sum(e['status'] in ('COMPLETED', 'AVAILABLE') for e in entries),
            'reads_unsuccessful_or_uncertain': sum(e['status'] not in ('COMPLETED', 'AVAILABLE') for e in entries),
            'read_accounting_source': 'PHYSICAL_READ_RECEIPTS' if 'physical_read_receipts' in state else 'PROCESS_READ_RECEIPTS' if 'process_read_receipts' in state else 'LEGACY_OBSERVATIONS'}
