"""Offline proof of one declared semantic SUM/partition route, never a read."""
import base64, hashlib, json, re, sqlite3
from pathlib import Path
from contextlib import contextmanager
from .estate_installation import configuration
from .microsoft_process import MicrosoftProcessAdapter, SEMANTIC_ENGINE, SQL_ENGINE
from ..onboarding import digest, encoded
from ..process_debugging import attest_surface
from ..process_quantity import quantity
from ..process_tape import Tape, bytes_of


from investigator.adapters.sql_principal import expected as sql_principal


class _ScanStore:
    """Existing compilers see one hash-checked scan in RAM; no estate database."""
    def __init__(self,scan,model):
        self.model=model;self.environment='readiness-compiler'
        self.db=sqlite3.connect(':memory:');self.db.row_factory=sqlite3.Row
        self.db.execute('CREATE TABLE enterprise_scans(id,environment,status,started,body,hash)')
        self.db.execute('INSERT INTO enterprise_scans VALUES(?,?,?,?,?,?)',
            ('retained',self.environment,'COMPLETE',0,encoded(scan),digest(scan)))
    @contextmanager
    def connect(self):yield self.db
    def get(self,identity):
        if identity!=self.model['id']:raise ValueError('Unknown compiler model')
        return self.model


def _unique(rows,message):
    if len(rows)!=1:raise ValueError(message)
    return rows[0]


def required_copy_bindings(receipt,manifest,inventory):
    """Recompile each declared Copy quantity from its served definition."""
    from .copy_quantity import resolve,approval_sample
    from ..estate_readiness import binding_identity
    scan=receipt['scan'];entries={e['id']:e for e in inventory['declarations']}
    result=[]
    for declaration in inventory['discovered_declarations']:
        if declaration['form']!='DECLARED_COPY':continue
        target=declaration['owner'];column=declaration['column'];entry=entries[declaration['id']]
        proof,reason=resolve(scan,target,column)
        if proof is None:raise ValueError('SCOPED_COPY_MAPPING_UNESTABLISHED: '+reason)
        if (declaration['content_hash']!=proof['definition_hash'] or
                entry['disposition']!='RESOLVED' or entry['dependencies']!=[proof['source']['id']]):
            raise ValueError('SCOPED_COPY_DECLARATION_DIFFERS')
        def layer(asset):
            return _unique([l['id']for l in manifest['layers']if l['asset_id']==asset],
                           'SCOPED_COPY_LAYER_UNESTABLISHED')
        boundary={'from_layer':layer(proof['source']['id']),'to_layer':layer(target)}
        proposal=approval_sample(scan,target,column,boundary=boundary,context_id='current-definition',
            cell={},precision={})['proposal']
        result.append(binding_identity(proposal))
    return result


def validate_declared_route(route,*,manifest,scan):
    """Recompile, verify scoped native receipts, and derive the neutral boundary.

    The caller binds the complete historical proof artifact by hash. Neither a
    producer status nor its claimed boundary grants readiness here.
    """
    observations=route['selected_observations']
    path=Path(route['captured_run_tape'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=route['captured_run_tape_sha256']:
        raise ValueError('Original native tape hash differs')
    tape=Tape(path)
    if tape.events[-1]['kind']!='FINAL':raise ValueError('Original native tape is not sealed complete')
    original=json.loads(base64.b64decode(tape.events[-1]['body']))['result']
    if tape.bootstrap.get('entry_point')=='code_verifier' and tape.bootstrap.get('state',{}).get('inputs',{}).get('native_route_contract')=='declared-native-pair-v1':
        original=original['native_route']
    if original['id']!=route['session_id']:raise ValueError('Original native session differs')
    original_observations={o['id']:o for o in original['observations']}
    if any(o['id'] not in original_observations or bytes_of(o)!=bytes_of(original_observations[o['id']]) for o in observations):
        raise ValueError('Selected native evidence differs from sealed original')
    if bytes_of(route['read_receipts'])!=bytes_of(original['process_read_receipts']):
        raise ValueError('Native read receipts differ from sealed original')
    if len({o['id'] for o in observations})!=len(observations):raise ValueError('Duplicate route evidence identity')
    comparison=_unique([o for o in observations if 'upper_evidence_id' in o], 'One native boundary comparison required')
    by_id={o['id']:o for o in observations}
    upper=by_id[comparison['upper_evidence_id']];lower=by_id[comparison['lower_evidence_id']]
    if upper['tool']!='bounded_dax' or lower['tool']!='bounded_fabric_sql':raise ValueError('Native semantic and SQL receipts required')
    for receipt in (upper,lower):
        if receipt.get('read_address')!={'kind':'BASELINE','restrictions':[]}:
            raise ValueError('Declared route requires an unfiltered whole-entity read address')
        if receipt.get('declared_context')!={'version':1,'scope':'WHOLE_ENTITY','filters':[],'dimension_ids':[]}:
            raise ValueError('Declared route requires equivalent whole-entity context')
        if receipt.get('surface_report_binding')!='VALUE_QUERY':raise ValueError('Native attestation must be value-query bound')
        logical=[r.get('logical_receipt',r) for r in route['read_receipts']]
        _unique([r for r in logical if r.get('receipt_id')==receipt['id'] and r.get('status')=='COMPLETED'],
                'One completed native receipt required for each quantity')
    measure_id=upper['measure_id']
    if lower['measure_id']!=measure_id:raise ValueError('Route measures differ')
    members=scan['assets'];measure=_unique([a for a in members if a['id']==measure_id and a['kind']=='Measure' and a.get('availability')=='CURRENT'], 'Current measure declaration missing')
    table=_unique([a for a in members if a['id']==measure['parent_id'] and a['kind']=='SemanticTable'],'Semantic table declaration missing')
    root=table['parent_id'];model_asset=_unique([a for a in members if a['id']==root and a['kind']=='SemanticModel'],'Semantic model declaration missing')
    definition=_unique([a for a in members if a.get('parent_id')==root and a.get('kind')=='DefinitionPart' and a.get('name')=='model.bim' and a.get('availability')=='CURRENT'],'Current model definition missing')
    document=json.loads(definition['metadata']['content'])['model']
    native_table=_unique([t for t in document['tables'] if t['name']==table['name']],'Model table declaration ambiguous')
    native_measure=_unique([m for m in native_table['measures'] if m['name']==measure['name']],'Model measure declaration ambiguous')
    expression=native_measure['expression']
    if isinstance(expression,list):expression='\n'.join(expression)
    if expression!=measure['metadata']['expression']:raise ValueError('Parsed measure differs from original definition')
    match=re.fullmatch(r"\s*SUM\s*\(\s*(?:'((?:''|[^'])+)'|([A-Za-z_][\w]*))\s*\[((?:\]\]|[^\]])+)\]\s*\)\s*",expression,re.I)
    if not match:raise ValueError('Declared route is not a direct additive SUM')
    if (match.group(1) or match.group(2)).replace("''", "'")!=native_table['name']:raise ValueError('SUM reads another semantic table')
    column_name=match.group(3).replace(']]',']')
    native_column=_unique([c for c in native_table['columns'] if c['name']==column_name],'SUM column declaration missing')
    parsed_column=_unique([a for a in members if a.get('parent_id')==table['id'] and a.get('kind')=='SemanticColumn' and a.get('name')==column_name],'Parsed SUM column missing')
    if any(parsed_column['metadata'].get(k)!=native_column.get(k) for k in ('sourceColumn','dataType')):
        raise ValueError('Parsed SUM column differs from original definition')
    if table['metadata'].get('partitions')!=native_table.get('partitions'):raise ValueError('Parsed partition differs from definition')
    config=configuration(manifest)
    model={'id':'readiness-model','enabled':True,'revision':'retained','context_id':'retained',
        'workspace':config['fabric']['workspace_id'],'native_id':root.rsplit('/',1)[1],
        'context':{'model_assets':[a for a in members if a['id']==root or a['id'].startswith(root+'/')]}}
    store=_ScanStore(scan,model)
    def forbidden(*args,**kwargs):raise ValueError('Readiness compiler attempted a live dispatch')
    adapter=MicrosoftProcessAdapter(store,config,model,forbidden,forbidden)
    try:
        binding=adapter._partition_binding({'assets':[table]})
        if binding.get('status')!='RESOLVED':raise ValueError('Partition does not resolve uniquely')
        if not binding.get('unchanged_connection'):raise ValueError('Partition contains intervening operations')
        native_path=_unique([o for o in original['observations'] if o.get('declared_source_binding',{}).get('asset',{}).get('id')==binding['asset']['id']], 'Original native partition proof missing')
        old_definition=native_path['declared_source_binding'].get('unchanged_connection') or {}
        if old_definition.get('definition_hash')!=binding['unchanged_connection']['definition_hash']:
            raise ValueError('Current definition differs from sealed native definition')
        layer={'id':binding['asset']['id'],'binding':binding,'declared_columns':native_table['columns'],'semantic_column':column_name}
        compiled,reason=adapter._lower_quantity(layer,{'filters':[],'dimension_ids':[]})
        if compiled is None:raise ValueError(reason)
        plans=[]
        class Compiled(Exception):pass
        def stop(plan,*args):plans.append(plan);raise Compiled()
        adapter._native_read=stop
        try:adapter.evaluate({'id':table['id']},measure_id,{'filters':[],'dimension_ids':[]})
        except Compiled:pass
    finally:store.db.close()
    if not plans or plans[0]['query']!=upper['query'] or compiled['query']!=lower['query']:
        raise ValueError('Current compiled quantity statements differ from native receipts')
    if comparison['upper_layer']!=table['id'] or comparison['lower_layer']!=binding['asset']['id']:
        raise ValueError('Native comparison identifies a different declared boundary')
    expected=[{'engine':SEMANTIC_ENGINE,'connection':model['workspace'],'object':model['native_id'],'identity':config['fabric']['native_reader']['account']},
              {'engine':SQL_ENGINE,'connection':'sql://'+config['fabric']['sql_reader']['server'],'object':compiled['database'],'identity':sql_principal(config['fabric']['sql_reader'])}]
    attestations=[]
    for receipt,surface in zip((upper,lower),expected):
        if receipt['execution_surface']!=surface:raise ValueError('Native receipt surface differs from the declared reader route')
        attestation=attest_surface(surface,receipt['surface_report'],('engine','identity','object'))
        if attestation.get('missing_required_fields') or attestation['consistency']!='MATCHED':raise ValueError('Native receipt required fields are not attested')
        if attestation!=receipt['surface_attestation']:raise ValueError('Native attestation record differs from recomputed evidence')
        attestations.append(attestation)
    if quantity(upper['values'])!=quantity(lower['values']) or comparison.get('values_equal') is not True:
        raise ValueError('Native quantities do not demonstrate the declared direct route agreement')
    def layer_id(asset):
        return _unique([l['id'] for l in manifest['layers'] if asset==l['asset_id'] or asset.startswith(l['asset_id']+'/')],'Declared boundary layer absent or ambiguous')
    boundary={'from_layer':layer_id(binding['asset']['id']),'to_layer':layer_id(table['id'])}
    result={'boundary':boundary,'assets':[table['id'],binding['asset']['id']],
        'measure_id':measure_id,'constraints':{'kind':'WHOLE_ENTITY_QUANTITY','measure_ids':[measure_id],'filters':[],'dimension_ids':[]},
        'receipt_ids':[upper['id'],lower['id']],'comparison_id':comparison['id'],
        'definition_asset_id':definition['id'],'definition_hash':binding['unchanged_connection']['definition_hash'],
        'compiled_queries':[plans[0]['query'],compiled['query']], 'attestations':attestations,
        'native_final_hash':digest(original),'native_tape_sha256':route['captured_run_tape_sha256'],
        'limits':['PARTIAL: connection is unattested on both native surfaces.','SNAPSHOT_UNVERIFIED: query-bound aligned served versions were not reported; historical quantity agreement does not establish currency.']}
    result['route_identity']=digest(result)
    return result
