"""Receipt-bound mapped value agreement, deliberately below full VERIFIED."""
import copy
from decimal import Decimal,InvalidOperation,localcontext
import hashlib
import re
from . import estate_graph_contract as c

VERSION='graph-value-check-v1'
MAPPING_VERSION='graph-value-mapping-v1'
QUALIFICATION='Values agree under this recorded mapping; semantic equivalence and business correctness are not established.'
PIN_KEYS=('graph_hash','scope_hash','mapping_hash','endpoint_hashes','definition_hash')


def hash_value(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):raise ValueError('GRAPH_VALUE_HASH_REQUIRED')
    return value


def scope_hash(mapping):
    return c.digest({key:mapping[key] for key in ('visual_address','visual_cell','inventory','active_restrictions')})


def number(value):
    if not isinstance(value,str) or len(value)>200 or not re.fullmatch(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?',value):
        raise ValueError('GRAPH_VALUE_EXACT_DECIMAL_REQUIRED')
    try:n=Decimal(value)
    except InvalidOperation:raise ValueError('GRAPH_VALUE_EXACT_DECIMAL_REQUIRED') from None
    if not n.is_finite():raise ValueError('GRAPH_VALUE_EXACT_DECIMAL_REQUIRED')
    return n


def typed(value):
    if not isinstance(value,dict) or set(value)!={'state','typed_value'}:raise ValueError('GRAPH_VALUE_RESULT_STATE')
    if value['state']=='BLANK':
        if value['typed_value'] is not None:raise ValueError('GRAPH_VALUE_BLANK_IS_NOT_ZERO')
        return None
    payload=value['typed_value']
    if value['state']!='VALUE' or not isinstance(payload,dict) or set(payload)!={'type','value'} or payload['type']not in ('DECIMAL','INT64'):
        raise ValueError('GRAPH_VALUE_RESULT_STATE')
    result=number(payload['value'])
    if payload['type']=='INT64' and ('.'in payload['value'] or not -(2**63)<=result<2**63):raise ValueError('GRAPH_VALUE_INTEGER_REQUIRED')
    return result


def matches(left,right,tolerance):
    a,b=typed(left),typed(right)
    if a is None or b is None:return a is None and b is None
    with localcontext() as context:
        context.prec=500
        return abs(a-b)<=tolerance


class ValueVerificationResolver:
    """Only installed evidence readers can earn the distinct mapped-value grade."""
    def __init__(self,checks,mappings,reads,*,current_pins):
        self.checks,self.mappings,self.reads,self.current_pins=checks,mappings,reads,current_pins

    def __call__(self,evidence_id):
        check=self.checks(evidence_id)
        fields={'version','id','producer','estate','edge_id','source','target','scope_hash','definition_hash','graph_hash',
                'mapping_id','source_read','target_read','explanation_read','observed_at'}
        if (not isinstance(check,dict) or set(check)!=fields or check['version']!=VERSION
                or check['producer']!='LINEAGE_VALUE_CHECK' or check['id']!=evidence_id):raise ValueError('GRAPH_VALUE_CHECK_REQUIRED')
        c.timestamp(check['observed_at'])
        mapping=self.mappings(check['mapping_id'])
        fields={'version','id','producer','estate','edge_id','source','target','scope_hash','definition_hash','graph_hash',
                'source_statement_hash','target_statement_hash','visual_address','visual_cell','inventory','active_restrictions',
                'report_binding','report_catalog','mapping','mapping_hash','tolerance','endpoint_hashes'}
        if (not isinstance(mapping,dict) or set(mapping)!=fields or mapping['version']!=MAPPING_VERSION
                or mapping['producer']!='LINEAGE_VALUE_COMPILER' or mapping['id']!=check['mapping_id']):raise ValueError('GRAPH_VALUE_MAPPING_REQUIRED')
        for key in ('estate','edge_id','source','target','scope_hash','definition_hash','graph_hash'):
            if mapping[key]!=check[key]:raise ValueError('GRAPH_VALUE_MAPPING_PIN_DIFFERS:'+key)
        for key in ('scope_hash','definition_hash','graph_hash','source_statement_hash','target_statement_hash','mapping_hash'):hash_value(mapping[key])
        if mapping['mapping_hash']!=c.digest(mapping['mapping']) or mapping['scope_hash']!=scope_hash(mapping):raise ValueError('GRAPH_VALUE_SCOPE_OR_MAPPING_HASH_DIFFERS')
        if not isinstance(mapping['endpoint_hashes'],dict) or set(mapping['endpoint_hashes'])!={'source','target'}:raise ValueError('GRAPH_VALUE_ENDPOINT_PINS_REQUIRED')
        for v in mapping['endpoint_hashes'].values():hash_value(v)
        pins=self.current_pins(copy.deepcopy(mapping))
        if not isinstance(pins,dict) or set(pins)!=set(PIN_KEYS) or any(pins[key]!=mapping[key]for key in PIN_KEYS):raise ValueError('GRAPH_VALUE_CURRENT_PIN_DIFFERS')
        address=mapping['visual_address']
        if (not isinstance(address,dict) or set(address)!={'report_id','page_id','target_id'} or not all(c.text(v)for v in address.values())
                or address['report_id']!=mapping['report_binding'].get('report_id') or address['target_id']!=mapping['visual_cell'].get('target_id')):
            raise ValueError('GRAPH_VALUE_VISUAL_ADDRESS_REQUIRED')
        from .report_cell import validate as cell_validate
        cell_validate(mapping['visual_cell'],mapping['visual_cell']['measure_id'])
        from .report_scope import validate_inventory
        entries=validate_inventory(mapping['inventory'],mapping['active_restrictions'],binding=mapping['report_binding'],reports=mapping['report_catalog'])
        if any(e['disposition']=='UNSUPPORTED'for e in entries):raise ValueError('GRAPH_VALUE_UNSUPPORTED_DECLARATION')
        translation=mapping['mapping']
        if not isinstance(translation,dict) or 'restriction_mappings' not in translation:raise ValueError('GRAPH_VALUE_RESTRICTION_MAPPING_REQUIRED')
        mapped=translation['restriction_mappings'];restrictions=mapping['active_restrictions']+mapping['visual_cell']['key_restrictions']
        expected=sorted(c.digest(r)for r in restrictions)
        if (not isinstance(mapped,list) or sorted(m.get('restriction_hash','')for m in mapped if isinstance(m,dict))!=expected
                or len(mapped)!=len(expected)):raise ValueError('GRAPH_VALUE_RESTRICTION_COVERAGE')
        for m in mapped:
            if (set(m)!={'restriction_hash','source','target','definition_hash'} or not isinstance(m['source'],dict) or not m['source']
                    or not isinstance(m['target'],dict) or not m['target']):raise ValueError('GRAPH_VALUE_RESTRICTION_MAPPING_REQUIRED')
            hash_value(m['definition_hash'])
        tolerance=mapping['tolerance']
        if (not isinstance(tolerance,dict) or set(tolerance)!={'kind','value','source'} or tolerance['kind']!='ABSOLUTE'
                or not c.text(tolerance['source'])):raise ValueError('GRAPH_VALUE_EXPLICIT_TOLERANCE_REQUIRED')
        allowed=number(tolerance['value'])
        if allowed<0:raise ValueError('GRAPH_VALUE_NEGATIVE_TOLERANCE')
        reads=[];attestations=[]
        def read(identity,side,statement_hash):
            receipt=self.reads(identity)
            fields={'id','producer','status','estate','object_id','scope_hash','definition_hash','mapping_hash','endpoint_hash',
                    'statement_hash','statement','value','attestation','snapshot','observed_at'}
            if (not isinstance(receipt,dict) or set(receipt)!=fields or receipt['id']!=identity or receipt['producer']!='QUERY_READ'
                    or receipt['status']!='SUCCEEDED'):raise ValueError('GRAPH_VALUE_SUCCESSFUL_READ_REQUIRED')
            for key in ('estate','scope_hash','definition_hash','mapping_hash'):
                if receipt[key]!=mapping[key]:raise ValueError('GRAPH_VALUE_READ_PIN_DIFFERS:'+key)
            if (receipt['object_id']!=mapping[side] or receipt['endpoint_hash']!=mapping['endpoint_hashes'][side]
                    or receipt['statement_hash']!=statement_hash or not isinstance(receipt['statement'],str)
                    or hashlib.sha256(receipt['statement'].encode()).hexdigest()!=statement_hash):raise ValueError('GRAPH_VALUE_READ_STATEMENT_OR_ENDPOINT_DIFFERS')
            a=receipt['attestation']
            if not isinstance(a,dict) or set(a)!={'declared','reported','reportable','binding'} or a['binding']!='VALUE_QUERY':raise ValueError('GRAPH_VALUE_ATTESTATION_REQUIRED')
            from .process_debugging import attest_surface
            attested=attest_surface(a['declared'],a['reported'],a['reportable'])
            if (attested['status']not in ('MATCHED','PARTIAL') or attested.get('missing_required_fields') or 'identity'not in attested.get('attested_fields',[])):
                raise ValueError('GRAPH_VALUE_ATTESTATION_REQUIRED')
            c.timestamp(receipt['observed_at']);typed(receipt['value'])
            reads.append(receipt);attestations.append(attested)
            return receipt
        source=read(check['source_read'],'source',mapping['source_statement_hash'])
        target=read(check['target_read'],'target',mapping['target_statement_hash'])
        equal=matches(source['value'],target['value'],allowed);explained=False
        if not equal:
            statement=translation.get('explanation_statement');definition=translation.get('explanation_definition_hash')
            if not check['explanation_read'] or not isinstance(statement,str) or not statement:raise ValueError('GRAPH_VALUE_UNEXPLAINED_DIFFERENCE')
            hash_value(definition)
            endpoint_side=translation.get('explanation_endpoint_side');value_side=translation.get('explanation_value_side')
            if endpoint_side not in ('source','target') or value_side not in ('source','target') or endpoint_side==value_side:
                raise ValueError('GRAPH_VALUE_EXPLANATION_CANNOT_COMPARE_ITSELF')
            explanation=read(check['explanation_read'],endpoint_side,hashlib.sha256(statement.encode()).hexdigest())
            against=source if value_side=='source' else target
            if not matches(explanation['value'],against['value'],allowed):raise ValueError('GRAPH_VALUE_EXPLANATION_DOES_NOT_REPRODUCE')
            explained=True
        elif check['explanation_read'] is not None:raise ValueError('GRAPH_VALUE_UNNEEDED_EXPLANATION')
        aligned=all(isinstance(r['snapshot'],dict) and r['snapshot'].get('query_bound')is True and r['snapshot'].get('alignment_id')for r in reads)
        aligned=bool(aligned and len({r['snapshot']['alignment_id']for r in reads})==1)
        qualifications=[QUALIFICATION]
        if explained:qualifications[0]='The observed difference is numerically explained under this recorded mapping; semantic equivalence and business correctness are not established.'
        if any(e['disposition']=='ACTIVE'and e['assumption']=='SAVED_DEFAULT'for e in entries):qualifications.append('Saved slicer defaults are assumed; current viewer selections were not established.')
        if any(a['status']=='PARTIAL'for a in attestations):qualifications.append('Surface attestation is partial; unattested fields remain unestablished.')
        if not aligned:qualifications.append('SNAPSHOT_UNVERIFIED: aligned query-bound served versions were not established.')
        return {'producer':'VALUE_QUERY_VERIFICATION','status':'VALUE_VERIFIED','estate':check['estate'],
            'scope_hash':check['scope_hash'],'definition_hashes':[check['definition_hash']],'edge_ids':[check['edge_id']],
            'source':check['source'],'target':check['target'],'observed_at':check['observed_at'],'qualification':' '.join(qualifications),
            'origin_source':'STATIC_DEFINITION','snapshot':'ALIGNED_QUERY_BOUND' if aligned else 'SNAPSHOT_UNVERIFIED',
            'alignment_id':reads[0]['snapshot']['alignment_id']if aligned else None,
            'requires_reverification':not aligned,'pins':{k:copy.deepcopy(mapping[k])for k in PIN_KEYS},
            'mapping_id':mapping['id'],'tolerance':copy.deepcopy(tolerance),'values_equal':equal,'difference_explained':explained,
            'attestations':attestations,'read_ids':[r['id']for r in reads]}


def value_path(resolver,evidence_ids,*,edges,start,terminal):
    """Conserve the declared dependency path; a partial proof is not a full path."""
    if not isinstance(resolver,ValueVerificationResolver):raise ValueError('GRAPH_TRUSTED_VALUE_RECEIPT_RESOLVER_REQUIRED')
    if (not isinstance(edges,list) or not 1<=len(edges)<=20 or len({e['id']for e in edges})!=len(edges)
            or not isinstance(evidence_ids,list) or len(evidence_ids)>20 or len(set(evidence_ids))!=len(evidence_ids)):
        raise ValueError('GRAPH_VALUE_PATH_BOUND')
    for edge in edges:c.record(edge,edge=True)
    if any(e['kind']in ('CONTAINS','INTERACTS_WITH')for e in edges):raise ValueError('GRAPH_VALUE_PATH_NOT_DEPENDENCY')
    expected={e['id']:e for e in edges}
    adjacency={}
    for edge in edges:adjacency.setdefault(edge['source'],[]).append(edge['target'])
    visiting=set();visited=set()
    def walk(node):
        if node in visiting:raise ValueError('GRAPH_VALUE_PATH_CYCLE')
        if node in visited:return
        visiting.add(node)
        for target in adjacency.get(node,[]):walk(target)
        visiting.remove(node);visited.add(node)
    walk(start)
    if any(e['source']not in visited for e in edges):raise ValueError('GRAPH_VALUE_PATH_DISCONNECTED')
    if terminal in adjacency:raise ValueError('GRAPH_VALUE_PATH_TERMINAL_HAS_DEPENDENCIES')
    proofs=[resolver(i)for i in evidence_ids]
    if len({p['edge_ids'][0]for p in proofs})!=len(proofs):raise ValueError('GRAPH_VALUE_PATH_DUPLICATE_PROOF')
    if len({(p['estate'],p['scope_hash'],p['pins']['graph_hash'])for p in proofs})>1:raise ValueError('GRAPH_VALUE_PATH_PIN_DIFFERS')
    proved={}
    for proof in proofs:
        edge=expected.get(proof['edge_ids'][0])
        if (not edge or edge['source']!=proof['source'] or edge['target']!=proof['target']
                or edge['provenance']['definition_hash']not in proof['definition_hashes'] or edge['confidence']=='UNKNOWN'):
            raise ValueError('GRAPH_VALUE_PATH_EDGE_DIFFERS')
        proved[edge['id']]=proof
    reached={start};pending=dict(proved)
    while pending:
        ready=[i for i,p in pending.items()if p['source']in reached]
        if not ready:raise ValueError('GRAPH_VALUE_PATH_DISCONNECTED')
        for identity in ready:reached.add(pending.pop(identity)['target'])
    missing=sorted(set(expected)-set(proved));complete=not missing and terminal in reached
    return {'status':'VALUE_VERIFIED' if complete else 'PARTIAL','complete':complete,'start':start,'requested_terminal':terminal,
        'reached':sorted(reached),'missing_edges':missing,'edge_evidence':list(evidence_ids),
        'qualification':' '.join(dict.fromkeys(p['qualification']for p in proofs)) if complete else 'Mapped value path is incomplete. '+ ' '.join(dict.fromkeys(p['qualification']for p in proofs)),
        'snapshot':'ALIGNED_QUERY_BOUND'if proofs and all(p['snapshot']=='ALIGNED_QUERY_BOUND'for p in proofs) and len({p['alignment_id']for p in proofs})==1 else 'SNAPSHOT_UNVERIFIED'}
