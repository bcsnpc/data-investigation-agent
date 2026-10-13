"""Receipt-bound edge checks. Agreement is scoped evidence, not semantic truth.

Resolvers are installed trusted evidence-store readers, never model callbacks.
The compiler supplies independently bound endpoint statements; read receipts
must record those same statements, scope, definition and execution attestation.
"""
import copy
from . import estate_graph_contract as c

QUALIFICATION='SCOPED_QUERY_AGREEMENT_ONLY; semantic correctness and global equivalence are not established.'


class VerificationResolver:
    def __init__(self,checks,bindings,reads):
        self.checks,self.bindings,self.reads=checks,bindings,reads

    def __call__(self,evidence_id):
        check=self.checks(evidence_id)
        required={'id','producer','estate','edge_id','source','target','scope_hash','definition_hash',
                  'binding_id','source_read','target_read','observed_at'}
        if not isinstance(check,dict) or set(check)!=required or check['id']!=evidence_id or check['producer']!='LINEAGE_QUERY_CHECK':
            raise ValueError('GRAPH_CHECK_RECEIPT_REQUIRED')
        c.timestamp(check['observed_at'])
        binding=self.bindings(check['binding_id'])
        expected={'id','producer','estate','edge_id','source','target','scope_hash','definition_hash',
                  'source_statement_hash','target_statement_hash','dependency_witness'}
        if not isinstance(binding,dict) or set(binding)!=expected or binding['producer']!='LINEAGE_EDGE_COMPILER' or binding['id']!=check['binding_id']:
            raise ValueError('GRAPH_COMPILED_EDGE_BINDING_REQUIRED')
        for key in ('estate','edge_id','source','target','scope_hash','definition_hash'):
            if binding[key]!=check[key]:raise ValueError('GRAPH_CHECK_BINDING_DIFFERS:'+key)
        witness=binding['dependency_witness']
        if (not isinstance(witness,dict) or set(witness)!={'kind','definition_hash','source','target','span'}
                or witness['kind'] not in ('DECLARED_DEFINITION','ENGINE_DEPENDENCY','CHECKED_TRANSLATION')
                or any(witness[key]!=check[key] for key in ('definition_hash','source','target'))):
            raise ValueError('GRAPH_DEPENDENCY_WITNESS_REQUIRED')
        # The compiler, not a total equality test, binds a dependency to a span.
        c.provenance({'source':'STATIC_DEFINITION','source_id':binding['id'],
            'definition_hash':witness['definition_hash'],'observed_at':check['observed_at'],'span':witness['span']})
        reads=[]
        for side in ('source','target'):
            receipt=self.reads(check[side+'_read'])
            fields={'id','producer','status','estate','object_id','scope_hash','definition_hash',
                    'statement_hash','value','attestation','snapshot','observed_at'}
            if not isinstance(receipt,dict) or set(receipt)!=fields or receipt['id']!=check[side+'_read'] or receipt['producer']!='QUERY_READ' or receipt['status']!='SUCCEEDED':
                raise ValueError('GRAPH_SUCCESSFUL_QUERY_RECEIPT_REQUIRED')
            if (receipt['estate']!=check['estate'] or receipt['object_id']!=check[side]
                    or receipt['scope_hash']!=check['scope_hash'] or receipt['definition_hash']!=check['definition_hash']
                    or receipt['statement_hash']!=binding[side+'_statement_hash']):
                raise ValueError('GRAPH_QUERY_BINDING_DIFFERS:'+side)
            if receipt['attestation']!={'identity':'MATCHED','engine':'MATCHED','connection':'MATCHED','object':'MATCHED'}:
                raise ValueError('GRAPH_QUERY_ATTESTATION_INCOMPLETE')
            c.timestamp(receipt['observed_at'])
            value=receipt['value']
            if (not isinstance(value,dict) or set(value)!={'state','typed_value'}
                    or value['state'] not in ('VALUE','BLANK')
                    or (value['state']=='BLANK' and value['typed_value'] is not None)
                    or (value['state']=='VALUE' and value['typed_value'] is None)):
                raise ValueError('GRAPH_QUERY_RESULT_STATE_REQUIRED')
            reads.append(receipt)
        if c.canonical(reads[0]['value'])!=c.canonical(reads[1]['value']):
            raise ValueError('GRAPH_SCOPED_QUERIES_DISAGREE')
        aligned=all(isinstance(r['snapshot'],dict) and r['snapshot'].get('query_bound') is True
                    and r['snapshot'].get('alignment_id') for r in reads)
        aligned=bool(aligned and reads[0]['snapshot']['alignment_id']==reads[1]['snapshot']['alignment_id'])
        return {'producer':'QUERY_VERIFICATION','status':'VERIFIED','estate':check['estate'],
            'scope_hash':check['scope_hash'],'definition_hashes':[check['definition_hash']],
            'edge_ids':[check['edge_id']],'source':check['source'],'target':check['target'],
            'observed_at':check['observed_at'],'qualification':QUALIFICATION,
            'snapshot':'ALIGNED_QUERY_BOUND' if aligned else 'SNAPSHOT_UNVERIFIED'}


def verify_path(*,estate,edges,scope_hash,compiler,query_read,record_check,resolver,max_reads=12):
    """One bounded attempt per dependency edge; no hidden retries or inference.

    compiler(edge,scope) -> retained binding receipt; query_read(binding,side)
    executes under existing read accounting and returns an evidence ID.
    Caller must preserve both successes and partial failures. UNKNOWN edges
    cannot be made complete by this function. All admission happens before reads.
    """
    if not isinstance(edges,list) or not edges or len(edges)*2>max_reads or not 1<=max_reads<=40:
        raise ValueError('GRAPH_PATH_READ_CAP')
    if len({e['id'] for e in edges})!=len(edges):raise ValueError('GRAPH_PATH_DUPLICATE_EDGE')
    for edge in edges:
        c.record(edge,edge=True)
        if edge['confidence']=='UNKNOWN' or edge['kind'] in ('CONTAINS','INTERACTS_WITH'):
            raise ValueError('GRAPH_PATH_UNRESOLVED_EDGE')
    # Path is a connected dependency slice, not unrelated equal-value pairs.
    reached={edges[0]['source']};pending=list(edges)
    while pending:
        ready=[e for e in pending if e['source'] in reached]
        if not ready:raise ValueError('GRAPH_PATH_DISCONNECTED')
        for edge in ready:reached.add(edge['target']);pending.remove(edge)
    prepared=[]
    for edge in edges:
        binding=compiler(copy.deepcopy(edge),scope_hash)
        if any(binding.get(key)!=value for key,value in {'estate':estate,'edge_id':edge['id'],
                'source':edge['source'],'target':edge['target'],'scope_hash':scope_hash,
                'definition_hash':edge['provenance']['definition_hash']}.items()):
            raise ValueError('GRAPH_PATH_COMPILER_BINDING_DIFFERS')
        prepared.append((edge,binding))
    completed=[]
    for edge,binding in prepared:
        source=query_read(binding,'source');target=query_read(binding,'target')
        check_id=record_check(binding,source,target)
        proof=resolver(check_id)
        if proof['edge_ids']!=[edge['id']]:raise ValueError('GRAPH_PATH_RECEIPT_EDGE_DIFFERS')
        completed.append({'edge_id':edge['id'],'evidence_id':check_id,'proof':proof})
    return {'status':'VERIFIED','scope_hash':scope_hash,'edges':completed,'qualification':QUALIFICATION}
