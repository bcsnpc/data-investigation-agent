"""Transactional graph history on the existing PostgreSQL shared-state authority."""
import copy
import json
from . import estate_graph_contract as contract
from .shared_state import StateConflict,encoded,sha

DDL='''
CREATE TABLE IF NOT EXISTS estate_graph_history(
 estate TEXT NOT NULL, record_kind TEXT NOT NULL, identity TEXT NOT NULL,
 owner TEXT NOT NULL, valid_from TEXT NOT NULL, valid_to TEXT,
 body TEXT NOT NULL, body_hash TEXT NOT NULL,
 PRIMARY KEY(estate,record_kind,identity,valid_from));
CREATE INDEX IF NOT EXISTS estate_graph_history_time ON estate_graph_history(estate,valid_from,valid_to);
CREATE TABLE IF NOT EXISTS estate_graph_owner_versions(
 estate TEXT NOT NULL, owner TEXT NOT NULL, definition_hash TEXT NOT NULL,
 observed_at TEXT NOT NULL, PRIMARY KEY(estate,owner));
CREATE TABLE IF NOT EXISTS estate_graph_changes(
 estate TEXT NOT NULL, changed_at TEXT NOT NULL, owner TEXT NOT NULL,
 before_hash TEXT, after_hash TEXT NOT NULL, detail TEXT NOT NULL,
 PRIMARY KEY(estate,owner,changed_at));
'''


def structural(value):
    if value is None:return None
    value=copy.deepcopy(value)
    value['provenance'].pop('observed_at',None)
    if 'base_confidence' in value:
        verification=value['properties'].pop('query_verification',{})
        value['confidence']=value['base_confidence']
        value['verification']={'state':'NOT_VERIFIED','evidence_ids':[],'scope_hash':None}
        if value['provenance']['source']=='QUERY_VERIFICATION':
            value['provenance']['source']=verification.get('origin_source') or ('MODEL_PROPOSAL' if value['base_confidence']=='INFERRED' else 'STATIC_DEFINITION')
    return value


class GraphRepository:
    def __init__(self,state,*,verification_resolver=None):
        self.state=state;self.verification_resolver=verification_resolver

    def migrate(self):
        self.state.migrate()
        with self.state.transaction() as db:
            for statement in DDL.split(';'):
                if statement.strip():db.execute(statement)

    def _current(self,db,estate,kind):
        table='estate_graph_nodes' if kind=='nodes' else 'estate_graph_edges'
        rows=self.state.sql(db,'SELECT identity,body FROM '+table+' WHERE estate=?',(estate,)).fetchall()
        return {identity:json.loads(body) for identity,body in rows}

    def _proof(self,item,estate=None):
        if item['confidence']!='VERIFIED':return
        if self.verification_resolver is None:raise ValueError('GRAPH_VERIFIED_RECEIPT_RESOLVER_REQUIRED')
        from .graph_verification import VerificationResolver
        if not isinstance(self.verification_resolver,VerificationResolver):
            raise ValueError('GRAPH_TRUSTED_EDGE_RECEIPT_RESOLVER_REQUIRED')
        proofs=[self.verification_resolver(identity) for identity in item['verification']['evidence_ids']]
        for proof in proofs:
            if (proof.get('producer')!='QUERY_VERIFICATION' or proof.get('status')!='VERIFIED'
                    or proof.get('scope_hash')!=item['verification']['scope_hash']
                    or item['provenance']['definition_hash'] not in proof.get('definition_hashes',[])
                    or item['id'] not in proof.get('edge_ids',[])):
                raise ValueError('GRAPH_VERIFIED_RECEIPT_SCOPE_DIFFERS')
            if proof['source']!=item.get('source') or proof['target']!=item.get('target'):
                raise ValueError('GRAPH_VERIFIED_RECEIPT_ENDPOINT_DIFFERS')
            if estate is not None and proof['estate']!=estate:raise ValueError('GRAPH_VERIFIED_RECEIPT_ESTATE_DIFFERS')
            item['properties']['query_verification']={'qualification':proof['qualification'],'snapshot':proof['snapshot'],
                'origin_source':'MODEL_PROPOSAL' if item['base_confidence']=='INFERRED' else proof['origin_source'],
                'requires_reverification':proof.get('requires_reverification',proof['snapshot'] not in ('SNAPSHOT_VERIFIED','ALIGNED_QUERY_BOUND'))}

    def verify_edges(self,estate,evidence_ids,*,observed_at):
        """Append earned proof without inventing a changed definition hash."""
        from .graph_verification import VerificationResolver
        if not isinstance(self.verification_resolver,VerificationResolver):
            raise ValueError('GRAPH_TRUSTED_EDGE_RECEIPT_RESOLVER_REQUIRED')
        if not isinstance(evidence_ids,list) or not 1<=len(evidence_ids)<=20 or len(set(evidence_ids))!=len(evidence_ids):
            raise ValueError('GRAPH_VERIFICATION_BOUND')
        now=contract.timestamp(observed_at)
        proofs=[(eid,self.verification_resolver(eid)) for eid in evidence_ids]
        if len({p['edge_ids'][0] for _,p in proofs})!=len(proofs):raise ValueError('GRAPH_DUPLICATE_VERIFICATION_EDGE')
        with self.state.transaction() as db:
            current=self._current(db,estate,'edges');updates=[]
            for evidence_id,proof in proofs:
                if proof['estate']!=estate:raise ValueError('GRAPH_VERIFIED_RECEIPT_ESTATE_DIFFERS')
                edge_id=proof['edge_ids'][0];before=current.get(edge_id)
                if before is None or before['confidence']=='UNKNOWN':raise ValueError('GRAPH_UNRESOLVED_EDGE_CANNOT_VERIFY')
                after=copy.deepcopy(before);after['confidence']='VERIFIED'
                after['provenance']={**after['provenance'],'source':'QUERY_VERIFICATION','observed_at':now}
                after['verification']={'state':'CURRENT','evidence_ids':[evidence_id],'scope_hash':proof['scope_hash']}
                after['properties']['query_verification']={'qualification':proof['qualification'],'snapshot':proof['snapshot']}
                contract.record(after,edge=True);self._proof(after,estate)
                latest=self.state.sql(db,'SELECT valid_from FROM estate_graph_history WHERE estate=? AND record_kind=? AND identity=? AND valid_to IS NULL',(estate,'edges',edge_id)).fetchone()
                if not latest or now<=latest[0] or now<contract.timestamp(proof['observed_at']):raise StateConflict('GRAPH_VERIFICATION_TIME_MUST_ADVANCE')
                updates.append(after)
            for after in updates:
                self.state.sql(db,'UPDATE estate_graph_history SET valid_to=? WHERE estate=? AND record_kind=? AND identity=? AND valid_to IS NULL',(now,estate,'edges',after['id']))
                self.state.sql(db,'INSERT INTO estate_graph_history VALUES(?,?,?,?,?,?,?,?)',(estate,'edges',after['id'],after['owner'],now,None,encoded(after),sha(after)))
                self.state.sql(db,'UPDATE estate_graph_edges SET confidence=?,provenance=?,body=? WHERE estate=? AND identity=?',
                    (after['confidence'],encoded(after['provenance']),encoded(after),estate,after['id']))
                self.state.sql(db,'INSERT INTO estate_graph_changes VALUES(?,?,?,?,?,?)',(estate,now,'verification:'+after['id'],
                    after['provenance']['definition_hash'],after['provenance']['definition_hash'],encoded([{'kind':'edges','id':after['id'],'change':'QUERY_VERIFIED','evidence_ids':after['verification']['evidence_ids']}])) )
        return {'status':'UPDATED','changed':len(updates)}

    def replace(self,value):
        return self.replace_many([value])

    def replace_many(self,values):
        """Atomically reconcile changed owners with one current projection read.

        Incoming owners may refer to each other regardless of input order. A
        batch is one estate and observation timestamp. Unchanged owners are
        skipped, not deleted/reinserted or charged as changes.
        """
        if not isinstance(values,list) or not 1<=len(values)<=1000:raise ValueError('GRAPH_BATCH_BOUND')
        values=[contract.snapshot(value) for value in values]
        estate=values[0]['estate'];now=contract.timestamp(values[0]['observed_at'])
        if any(value['estate']!=estate or contract.timestamp(value['observed_at'])!=now for value in values):
            raise ValueError('GRAPH_BATCH_ESTATE_OR_TIME_DIFFERS')
        if len({value['owner'] for value in values})!=len(values):raise ValueError('GRAPH_BATCH_DUPLICATE_OWNER')
        with self.state.transaction() as db:
            versions={owner:(hash,observed) for owner,hash,observed in self.state.sql(db,
                'SELECT owner,definition_hash,observed_at FROM estate_graph_owner_versions WHERE estate=?',(estate,)).fetchall()}
            pending=[]
            for value in values:
                prior=versions.get(value['owner'])
                if prior and prior[0]==value['definition_hash']:continue
                if prior and now<=prior[1]:raise StateConflict('GRAPH_CHANGE_TIME_MUST_ADVANCE')
                pending.append(value)
            if not pending:return {'status':'UNCHANGED','changed':0}
            owners={value['owner'] for value in pending}
            old={kind:self._current(db,estate,kind) for kind in ('nodes','edges')}
            new={kind:{key:copy.deepcopy(item) for key,item in entries.items() if item['owner'] not in owners} for kind,entries in old.items()}
            for value in pending:
                for kind in ('nodes','edges'):
                    for item in value[kind]:
                        if item['id'] in new[kind]:raise StateConflict('GRAPH_IDENTITY_OWNED_BY_ANOTHER_ITEM')
                        previous=old[kind].get(item['id'])
                        if previous and previous['owner']!=item['owner']:raise StateConflict('GRAPH_IDENTITY_OWNED_BY_ANOTHER_ITEM')
                        self._proof(item,estate)
                        new[kind][item['id']]=copy.deepcopy(previous) if previous and structural(previous)==structural(item) else item
                        if (kind=='edges' and previous and previous['confidence']=='VERIFIED'
                                and item['confidence']!='VERIFIED' and structural(previous)!=structural(item)):
                            new[kind][item['id']]['verification']={**copy.deepcopy(previous['verification']),'state':'STALE'}
            changed_nodes={identity for identity in old['nodes'].keys()|new['nodes'].keys() if old['nodes'].get(identity)!=new['nodes'].get(identity)}
            batch_hash=contract.digest([(value['owner'],value['definition_hash']) for value in sorted(pending,key=lambda value:value['owner'])])
            for identity,item in list(new['edges'].items()):
                missing=[key for key in (item['source'],item['target']) if key not in new['nodes']]
                if missing and item['owner'] in owners:raise ValueError('GRAPH_ENDPOINT_NOT_DECLARED')
                if missing:
                    for endpoint in ('source','target'):
                        if item[endpoint] in missing:
                            original=item[endpoint];gap_id=contract.identity(estate,item['owner'],'BOUNDARY',['deleted',original,batch_hash])
                            proof={**item['provenance'],'definition_hash':batch_hash,'observed_at':now,'source_id':item['owner']}
                            gap={'reason':'A referenced object was removed from its current definition: '+original,
                                 'remedy':'Recollect the dependent definition and resolve its reference to an existing object.'}
                            new['nodes'][gap_id]=contract.node(gap_id,item['owner'],'BOUNDARY','Removed dependency',proof,confidence='UNKNOWN',unknown=gap)
                            item[endpoint]=gap_id;item['unknown']=gap;item['confidence']='UNKNOWN';item['base_confidence']='UNKNOWN'
                if missing or (identity in old['edges'] and {item['source'],item['target']} & changed_nodes and item['confidence']=='VERIFIED'):
                    item['confidence']=item['base_confidence']
                    if item['verification']['evidence_ids']:item['verification']['state']='STALE'
                    item['provenance']={**item['provenance'],'observed_at':now}
                    if item['provenance']['source']=='QUERY_VERIFICATION':
                        item['provenance']['source']=item['properties'].get('query_verification',{}).get('origin_source') or ('STATIC_DEFINITION' if item['base_confidence']!='INFERRED' else 'MODEL_PROPOSAL')
                contract.record(item,edge=True)
            changed=[]; history_updates=[]; history_inserts=[]
            active_versions={(kind,identity):stamp for kind,identity,stamp in self.state.sql(db,
                'SELECT record_kind,identity,valid_from FROM estate_graph_history WHERE estate=? AND valid_to IS NULL',(estate,)).fetchall()}
            for kind in ('nodes','edges'):
                for identity in sorted(old[kind].keys()|new[kind].keys()):
                    before=old[kind].get(identity);after=new[kind].get(identity)
                    if before==after:continue
                    latest=active_versions.get((kind,identity))
                    if latest and now<=latest:raise StateConflict('GRAPH_RECORD_CHANGE_TIME_MUST_ADVANCE')
                    owner=(after or before)['owner']
                    changed.append({'kind':kind,'id':identity,'owner':owner,'change':'DELETED' if after is None else 'ADDED' if before is None else 'CHANGED'})
                    history_updates.append((now,estate,kind,identity))
                    if after is not None:
                        history_inserts.append((estate,kind,identity,after['owner'],now,None,encoded(after),sha(after)))
            self.state.sqlmany(db,'UPDATE estate_graph_history SET valid_to=? WHERE estate=? AND record_kind=? AND identity=? AND valid_to IS NULL',history_updates)
            self.state.sqlmany(db,'INSERT INTO estate_graph_history VALUES(?,?,?,?,?,?,?,?)',history_inserts)
            self.state.sql(db,'DELETE FROM estate_graph_edges WHERE estate=?',(estate,))
            self.state.sql(db,'DELETE FROM estate_graph_nodes WHERE estate=?',(estate,))
            self.state.sqlmany(db,'INSERT INTO estate_graph_nodes VALUES(?,?,?,?,?)',
                [(estate,item['id'],item['confidence'],encoded(item['provenance']),encoded(item)) for item in new['nodes'].values()])
            self.state.sqlmany(db,'INSERT INTO estate_graph_edges VALUES(?,?,?,?,?,?,?)',
                [(estate,item['id'],item['source'],item['target'],item['confidence'],encoded(item['provenance']),encoded(item)) for item in new['edges'].values()])
            for value in pending:
                owner=value['owner'];prior=versions.get(owner)
                if prior:self.state.sql(db,'UPDATE estate_graph_owner_versions SET definition_hash=?,observed_at=? WHERE estate=? AND owner=?',(value['definition_hash'],now,estate,owner))
                else:self.state.sql(db,'INSERT INTO estate_graph_owner_versions VALUES(?,?,?,?)',(estate,owner,value['definition_hash'],now))
                self.state.sql(db,'INSERT INTO estate_graph_changes VALUES(?,?,?,?,?,?)',(estate,now,owner,prior[0] if prior else None,value['definition_hash'],encoded([change for change in changed if change['owner']==owner])))
        return {'status':'UPDATED','changed':len(changed),'changes':changed}

    def records(self,estate,*,at=None,identities=None,limit=1000):
        if type(limit) is not int or not 1<=limit<=10000:raise ValueError('GRAPH_READ_BOUND')
        when=contract.timestamp(at) if at else None
        with self.state.transaction() as db:
            where='estate=?';args=[estate]
            if when:where+=' AND valid_from<=? AND (valid_to IS NULL OR valid_to>?)';args.extend([when,when])
            else:where+=' AND valid_to IS NULL'
            if identities is not None:
                if not identities:return {'nodes':[],'edges':[],'truncated':False}
                if len(identities)>1000:raise ValueError('GRAPH_ALLOWLIST_BOUND')
                where+=' AND identity IN ('+','.join('?' for _ in identities)+')';args.extend(sorted(identities))
            rows=self.state.sql(db,'SELECT record_kind,body,body_hash,valid_from,valid_to FROM estate_graph_history WHERE '+where+' ORDER BY record_kind,identity LIMIT ?',(*args,limit+1)).fetchall()
        result={'nodes':[],'edges':[],'truncated':len(rows)>limit}
        for kind,raw,hash,valid_from,valid_to in rows[:limit]:
            item=json.loads(raw)
            if sha(item)!=hash:raise StateConflict('GRAPH_HISTORY_HASH_DIFFERS')
            result[kind].append({**item,'valid_from':valid_from,'valid_to':valid_to})
        from .graph_scan_health import unavailable
        collection=unavailable(self.state,estate,{item['owner'] for kind in ('nodes','edges') for item in result[kind]},at=when)
        if collection:
            result['unavailable_owners']=collection
            owners={item['id']:item['owner'] for item in result['nodes']}
            for item in result['edges']:
                affected={item['owner'],owners.get(item['source']),owners.get(item['target'])} & collection.keys()
                if affected and item['confidence']=='VERIFIED':
                    item['confidence']=item['base_confidence']
                    item['verification']={**item['verification'],'state':'STALE'}
        return result

    def changes(self,estate,*,limit=100):
        if type(limit) is not int or not 1<=limit<=1000:raise ValueError('GRAPH_CHANGE_BOUND')
        with self.state.transaction() as db:
            rows=self.state.sql(db,'SELECT changed_at,owner,before_hash,after_hash,detail FROM estate_graph_changes WHERE estate=? ORDER BY changed_at DESC LIMIT ?',(estate,limit)).fetchall()
        return [{'at':at,'owner':owner,'before_hash':before,'after_hash':after,'changes':json.loads(detail)} for at,owner,before,after,detail in rows]
