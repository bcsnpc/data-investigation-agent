"""An admitted application quantity with same-statement reader self-description."""
from run_source_diagnostic import read_once, SourceReadError

ENGINE='Microsoft SQL Azure'
REPORT={'identity':'__application_identity','engine':'__application_engine','object':'__application_object'}


def read(config, request, *, execute=read_once):
    if not request.get('require_read_only') or not request.get('read_only_objects'):
        raise ValueError('Application quantity requires the existing object/session read-only guards')
    if set(request['result_columns']) & set(REPORT.values()):
        raise ValueError('Application quantity collides with surface-report columns')
    payload=dict(request,query=("SELECT q.*, CURRENT_USER AS [__application_identity], "
        "CAST(SERVERPROPERTY('EngineEdition') AS int) AS [__application_engine], "
        "DB_NAME() AS [__application_object] FROM ("+request['query']+") AS q"),
        result_columns=list(request['result_columns'])+list(REPORT.values()),response_mode='records')
    result=execute(config,payload)
    if result.get('error'):
        raise SourceReadError(result.get('sql_error_number'),result.get('error_kind'))
    if result.get('read_only_verified') is not True:raise ValueError('Application guards did not establish read-only execution')
    rows=result.get('rows')
    if not isinstance(rows,list) or not rows:raise ValueError('Application surface report missing')
    reports=[];values=[]
    for row in rows:
        if not isinstance(row,dict) or not set(REPORT.values())<=set(row):
            raise ValueError('Application value query omitted surface description')
        edition=row[REPORT['engine']]
        if str(edition)!='5':raise ValueError('Application engine edition differs from the declared Azure SQL surface')
        reports.append({'identity':row[REPORT['identity']],'engine':ENGINE,'object':row[REPORT['object']]})
        values.append({k:v for k,v in row.items() if k not in REPORT.values()})
    if any(p!=reports[0] for p in reports):raise ValueError('Application self-description differs across result rows')
    return dict(result,rows=values,surface_report=reports[0],surface_report_binding='VALUE_QUERY')
