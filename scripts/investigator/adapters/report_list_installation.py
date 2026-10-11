"""Install only the manifest's existing reader; never default to publisher auth."""
import json
from ..onboarding import encoded, digest
from ..process_tape import uuid4
from .report_listing import ReportLists


def install(workspace,config):
    from metadata_config import ROOT
    reader=config['fabric'].get('native_reader')
    if not reader or not workspace.execution_enabled:return None
    from ..native_identity import profile
    profile(reader)
    scopes=[config['fabric']['workspace_id']]
    if 'workspace_ids' in reader and not set(scopes)<=set(reader['workspace_ids']):
        raise ValueError('Form lists exceed the existing reader scope')
    governor=workspace.agent.governor
    if governor is None:raise ValueError('Live report lists require request governance')
    with workspace.store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS workspace_form_controls(id TEXT PRIMARY KEY,body TEXT,hash TEXT)')
    def read(endpoint):
        identity=str(uuid4());session='form-controls:'+workspace.owner
        receipt={'id':identity,'classification':'CONTROL_METADATA','endpoint':endpoint,
            'identity':reader['account'],'principal_id':reader['principal_id'],
            'investigation_diagnostic_reads':0,'status':'RESERVED','before':governor.snapshot()}
        def save():
            with workspace.store.connect() as db:
                db.execute('INSERT OR REPLACE INTO workspace_form_controls VALUES(?,?,?)',
                           (identity,encoded(receipt),digest(receipt)))
        save()
        try:
            from ..physical_reads import run
            def execute():
                result=run([config['fabric']['auth']['python'],str(ROOT/'scripts/report_list_worker.py')],
                    input=json.dumps({'endpoint':endpoint,'workspace_ids':scopes,'reader':reader}),
                    capture_output=True,text=True,encoding='utf-8',timeout=120)
                if result.returncode:raise RuntimeError('Isolated reader report metadata unavailable')
                value=json.loads(result.stdout)
                if value.get('reader',{}).get('principal_id')!=reader['principal_id']:
                    raise ValueError('Report metadata receipt principal differs')
                return value
            result=governor.metered_read(session,identity,execute)
            receipt.update(status='AVAILABLE',response=result,response_hash=digest(result))
            return result
        except Exception as exc:
            receipt.update(status='UNAVAILABLE',error_type=type(exc).__name__)
            raise
        finally:
            receipt['after']=governor.snapshot();save()
    return ReportLists(scopes,reader['account'],read)
