"""Graph promotion through the existing binding compiler, seals and verifier.

This adapter does not turn an ordinary scalar equality into a dependency proof.
It attaches a retained, revalidated bounded binding profile to its exact column
edge. The existing surface-difference and snapshot contracts remain authoritative.
"""
import copy
import json
from .. import estate_graph_contract as c
from ..graph_verification import VerificationResolver,QUALIFICATION
from ..lineage_binding import Ledger,revalidate_verification,seal
from ..onboarding import digest
from ..receipt_integrity import verify as verify_seal,TABLES
from ..raw_surface_report import validate as validate_raw_report
from .binding_verification import BindingVerificationRoute


def original_probe(route,observation,plan):
    """Recheck the terminal producer row, then compare the recompiled statement."""
    evidence=observation['evidence'];kind=evidence.get('tool');identity=evidence.get('id')
    if kind not in ('bounded_sql','bounded_fabric_sql'):raise ValueError('GRAPH_BINDING_QUERY_SURFACE_UNSUPPORTED')
    with route.process.store.connect() as db:
        sealed=verify_seal(db,kind,identity)
        if sealed['state']!='SEALED':raise ValueError('GRAPH_BINDING_ORIGINAL_QUERY_UNSEALED')
        row=db.execute('SELECT model_id,created,status,request,result FROM '+TABLES[kind]+' WHERE id=?',(identity,)).fetchone()
    if not row or row[0]!=route.process.model['id'] or row[2]!='COMPLETED':
        raise ValueError('GRAPH_BINDING_ORIGINAL_QUERY_SCOPE_OR_STATUS')
    request,result=json.loads(row[3]),json.loads(row[4]);validate_raw_report(request,result)
    compiled={key:value for key,value in request.items() if key!='plan'}
    if (digest(compiled)!=evidence.get('request_hash') or result.get('rows')!=evidence.get('values')
            or request.get('read_address')!=observation['address']
            or request.get('context_id')!=observation['context']
            or request.get('plan',{}).get('query',request.get('query'))!=plan['compiled']['query']
            or result.get('surface_report')!=evidence.get('surface_report')
            or result.get('surface_report_binding')!='VALUE_QUERY'):
        raise ValueError('GRAPH_BINDING_ORIGINAL_QUERY_DIFFERS')
    return {'receipt_id':identity,'seal':sealed['hash'],'created':c.timestamp(row[1])}


class BindingVerificationResolver(VerificationResolver):
    """No callback can declare VERIFIED: use installed producer and stored rows.

    attachments maps a verification's immutable ledger hash to one current graph
    edge ID. This is separate derived indexing; original ledger rows stay intact.
    """
    def __init__(self,*,estate,ledger,route,graph,attachments):
        if not isinstance(ledger,Ledger) or not isinstance(route,BindingVerificationRoute):
            raise ValueError('GRAPH_EXISTING_BINDING_PRODUCERS_REQUIRED')
        self.estate,self.ledger,self.route=estate,ledger,route
        self.graph=copy.deepcopy(graph);self.attachments=copy.deepcopy(attachments)

    def _column(self,table,column):
        if table not in self.route.objects:raise ValueError('GRAPH_BINDING_TABLE_UNRESOLVED')
        asset_id=self.route.objects[table]['asset_id']
        tables=[n['id'] for n in self.graph['nodes'] if n['properties'].get('asset_id')==asset_id]
        if len(tables)!=1:raise ValueError('GRAPH_BINDING_TABLE_NOT_IN_GRAPH')
        children={e['target'] for e in self.graph['edges'] if e['source']==tables[0] and e['kind']=='CONTAINS'}
        columns=[n['id'] for n in self.graph['nodes'] if n['id'] in children and n['kind'] in ('COLUMN','CALCULATED_COLUMN') and n['label']==column]
        if len(columns)!=1:raise ValueError('GRAPH_BINDING_COLUMN_NOT_UNIQUE')
        return columns[0]

    def __call__(self,evidence_id):
        if evidence_id not in self.attachments:raise ValueError('GRAPH_BINDING_ATTACHMENT_MISSING')
        rows=[row for row in self.ledger.records() if seal(row)==evidence_id]
        if len(rows)!=1:raise ValueError('GRAPH_BINDING_SEALED_VERIFICATION_MISSING')
        verification=revalidate_verification(rows[0])
        if verification.get('verification_version')!='binding-profile-v1' or verification['status']!='VERIFIED':
            raise ValueError('GRAPH_BINDING_PROFILE_NOT_VERIFIED')
        if verification['context']!=self.route.context:raise ValueError('GRAPH_BINDING_CONTEXT_DIFFERS')
        proposal=verification['proposal'];edge_id=self.attachments[evidence_id]
        edges=[e for e in self.graph['edges'] if e['id']==edge_id]
        if len(edges)!=1:raise ValueError('GRAPH_BINDING_EDGE_NOT_UNIQUE')
        edge=edges[0];c.record(edge,edge=True)
        if edge['confidence']=='UNKNOWN' or edge['kind'] not in ('COMPUTED_FROM','DERIVED_IN_STEP'):
            raise ValueError('GRAPH_BINDING_EDGE_KIND_UNSUPPORTED')
        output=self._column(proposal['target']['table'],proposal['target']['column'])
        inputs={self._column(source['table'],column) for source in proposal['sources'] for column in source['columns']}
        if (edge['source']!=output or edge['target'] not in inputs
                or edge['provenance']['definition_hash']!=proposal['location']['content_hash']):
            raise ValueError('GRAPH_BINDING_EDGE_DEFINITION_OR_ENDPOINT_DIFFERS')
        originals=[]
        # The actual installed adapter recompiles both queries from the exact
        # retained context; no execution or new value read occurs here.
        plans=[self.route.compile(proposal,side,verification['context'],verification['address']) for side in ('TARGET','SOURCE')]
        for observation,plan in zip(verification['observations'],plans):
            originals.append(original_probe(self.route,observation,plan))
        from ..surface_difference import wording
        return {'producer':'QUERY_VERIFICATION','status':'VERIFIED','estate':self.estate,
            'scope_hash':c.digest({'context':verification['context'],'address':verification['address']}),
            'definition_hashes':[proposal['location']['content_hash']],'edge_ids':[edge_id],
            'source':output,'target':edge['target'],'observed_at':max(r['created'] for r in originals),
            'qualification':QUALIFICATION+' '+wording(verification['surface_difference'])+' '+' '.join(verification['limits']),
            'snapshot':verification['snapshot_status'],'origin_source':'STATIC_DEFINITION' if proposal['extractor']=='STATIC' else 'MODEL_PROPOSAL',
            'original_receipts':originals,'surface_difference':verification['surface_difference'],
            'requires_reverification':verification['requires_reverification']}


def verify_binding(proposal,*,route,sample,budget,ledger):
    """The on-demand live producer, using existing guards and separate budget.

    Caller must first resolve/approve the path, install its reader and admit the
    physical pot. No synthetic values or fallback engine are supplied here.
    """
    if not isinstance(route,BindingVerificationRoute) or not isinstance(ledger,Ledger):
        raise ValueError('GRAPH_EXISTING_BINDING_PRODUCERS_REQUIRED')
    if not callable(getattr(route.process,'meter_read',None)):raise ValueError('GRAPH_BINDING_PHYSICAL_METER_REQUIRED')
    from ..binding_sample import verify
    from ..lineage_binding import VerificationHold
    try:
        result=verify(proposal,context=route.context,sample=sample,profile=route.target_profile(proposal),
            compiler=route.compile,execute=lambda side,plan:budget.read(side,lambda:route.execute(side,plan)))
    except VerificationHold as exc:
        ledger.append(exc.verification);raise
    ledger.append(result)
    return {'evidence_id':seal(result),'verification':result}
