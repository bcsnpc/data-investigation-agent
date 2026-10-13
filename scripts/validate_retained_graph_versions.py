"""Offline change/revert proof from two hash-checked retained report contexts.

No collector contacts an estate. Derived SQLite/CAS files are written only to a
new output directory; source contexts and their native part bytes stay intact.
"""
import argparse
import copy
from contextlib import closing
from datetime import datetime,timedelta,timezone
import hashlib
import json
from pathlib import Path
import sqlite3

from investigator.onboarding import digest
from investigator.shared_state import SharedState,sha
from investigator.artifact_store import Files,LocalObjects
from investigator.graph_definitions import DefinitionSink
from investigator.graph_asset_catalog import AssetCatalog
from investigator.estate_graph_repository import GraphRepository
from investigator.estate_graph_incremental import IncrementalScanner
from investigator.estate_graph_api import GraphAPI
from investigator.live_gateway import Gateway
from investigator.adapters.estate_graph_static import extract_partitioned,asset_owners
from investigator.adapters.graph_change_collector import Assets
from metadata_inventory import expand_definition


def retained(database,context_id,report_id):
    with closing(sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True)) as db:
        row=db.execute('SELECT body,hash FROM model_contexts WHERE id=?',(context_id,)).fetchone()
    if row is None:raise ValueError('RETAINED_CONTEXT_MISSING')
    context=json.loads(row[0])
    if digest(context)!=row[1]:raise ValueError('RETAINED_CONTEXT_HASH_DIFFERS')
    candidates=[r for r in context['reports'] if r['report']['id']==report_id]
    if len(candidates)!=1:raise ValueError('RETAINED_REPORT_AMBIGUOUS_OR_MISSING')
    report=candidates[0];parts=report['report_definitions']
    native={p['metadata']['path']:p['metadata']['content'] for p in parts}
    if len(native)!=len(parts):raise ValueError('RETAINED_PART_PATH_DUPLICATE')
    expanded=Assets()
    expand_definition(expanded,report_id,'Report',native,report['report']['source'])
    # Existing native parts remain byte-identical; only missing expanded children
    # are deterministically reconstructed with the production collector helper.
    assets=[report['report'],*parts,*[a for a in expanded.values if a['kind']!='DefinitionPart']]
    return context,assets,{'context_id':context_id,'context_hash':row[1],
        'original_observed_at':context['scan_ended'],'native_parts':{
            path:hashlib.sha256(raw.encode()).hexdigest()for path,raw in sorted(native.items())}}


def normalized(value):
    value=copy.deepcopy(value)
    def walk(v):
        if isinstance(v,dict):
            for key in ('valid_from','valid_to','observed_at'):v.pop(key,None)
            for child in v.values():walk(child)
        elif isinstance(v,list):
            for child in v:walk(child)
    walk(value);return value


def validate(database,before_id,after_id,report_id,output):
    before,old,old_proof=retained(database,before_id,report_id)
    after,new,new_proof=retained(database,after_id,report_id)
    changed=[p for p in sorted(old_proof['native_parts'].keys()|new_proof['native_parts'].keys())
             if old_proof['native_parts'].get(p)!=new_proof['native_parts'].get(p)]
    if not changed:raise ValueError('RETAINED_DEFINITIONS_IDENTICAL')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    state=SharedState.offline(output/'graph.sqlite');repo=GraphRepository(state);repo.migrate()
    sink=DefinitionSink(Files(LocalObjects(output/'cas')),'cas://retained-version-proof',recording_class='EXACT')
    estate='retained-version-proof'
    catalog=AssetCatalog(repo,sink,extract_partitioned,asset_owners,allowed_owners=[report_id])
    assets=[*before['model_assets'],*old]
    start=datetime.now(timezone.utc)
    moments=[(start+timedelta(seconds=i)).isoformat()for i in range(4)]
    catalog.seed(estate,assets,observed_at=moments[0],
        source_observations={a['id']:before['scan_ended']for a in assets})
    class RetainedCollector:
        identity='retained-context-version-proof'
        configured_owners=(report_id,)
        payload={'assets':old,'source_asset_ids':[]}
        fetched=[]
        def list_changes(self):
            return {'items':[{'owner':report_id,'fingerprint':sha(self.payload),'deleted':False}],'complete':False}
        def fetch(self,owner):
            if owner!=report_id:raise ValueError('RETAINED_OWNER_SCOPE')
            self.fetched.append(owner);return copy.deepcopy(self.payload)
    source=RetainedCollector();scanner=IncrementalScanner(repo,source,None,reconcile=catalog.refresh)
    def filters(at=None):
        graph=repo.records(estate,at=at,limit=10000)
        if graph['truncated']:raise ValueError('RETAINED_GRAPH_TRUNCATED')
        ids=[n['id']for n in graph['nodes']]
        gateway=Gateway({'version':1,'live_enabled':False,'identities':{'operator':{'graph':{estate:ids}}}})
        api=GraphAPI(repo,gateway,identity='operator',estate=estate,allowed_objects=ids,at=at,max_nodes=200,max_edges=500,max_bytes=256000)
        return {n['id']:api.filters_on(n['id'])for n in graph['nodes']if n['kind']=='PAGE'}
    baseline=filters();historical=filters(moments[0]);history_before=repo.changes(estate,limit=1000)
    def historical_content(value):
        value=copy.deepcopy(value)
        for page in value.values():
            for row in page['nodes']+page['edges']:row.pop('valid_to',None)
        return value
    # First cursor observation is the known retained baseline, not an estate read.
    observations=[scanner.run(estate,moments[1])]
    source.payload={'assets':new,'source_asset_ids':[]}
    observations.append(scanner.run(estate,moments[2]));changed_filters=filters()
    if normalized(changed_filters)==normalized(baseline):raise ValueError('FILTER_CHANGE_NOT_RETURNED')
    if historical_content(filters(moments[0]))!=historical_content(historical):raise ValueError('ORIGINAL_GRAPH_VERSION_CHANGED')
    source.payload={'assets':old,'source_asset_ids':[]}
    observations.append(scanner.run(estate,moments[3]));reverted=filters()
    if normalized(reverted)!=normalized(baseline):raise ValueError('FILTER_REVERT_DIFFERS')
    if historical_content(filters(moments[0]))!=historical_content(historical):raise ValueError('ORIGINAL_GRAPH_VERSION_CHANGED')
    if any(o['status']=='UNAVAILABLE'for scan in observations for o in scan['owners']):
        raise ValueError('RETAINED_SCAN_UNAVAILABLE')
    history=repo.changes(estate,limit=1000)
    unaffected={h['owner']for h in history_before}-{report_id}
    if [h for h in history if h['owner']in unaffected]!=[h for h in history_before if h['owner']in unaffected]:
        raise ValueError('UNRELATED_OWNER_HISTORY_CHANGED')
    receipt={'status':'PASSED','kind':'OFFLINE_RETAINED_DEFINITION_CHANGE_REVERT','estate_reads':0,'model_calls':0,
        'source_database':str(Path(database).resolve()),'report_id':report_id,'before':old_proof,'after':new_proof,
        'changed_native_parts':changed,'baseline_filters_sha256':sha(normalized(baseline)),
        'changed_filters_sha256':sha(normalized(changed_filters)),'reverted_filters_sha256':sha(normalized(reverted)),
        'original_as_of_preserved':True,'unrelated_owner_history_unchanged':True,
        'fetched_owners':source.fetched,'scans':observations,'history':history,
        'qualification':'Retained metadata exercised offline; simulated observation timestamps are not fresh estate observations. No live controlled edit was performed.'}
    for filename,value in [('before-filters.json',baseline),('after-filters.json',changed_filters),('reverted-filters.json',reverted),('receipt.json',receipt)]:
        (output/filename).write_text(json.dumps(value,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('database','before-context','after-context','report','output'):p.add_argument('--'+name,required=True)
    a=p.parse_args();r=validate(a.database,a.before_context,a.after_context,a.report,a.output)
    print(json.dumps({k:r[k]for k in ('status','changed_native_parts','baseline_filters_sha256','changed_filters_sha256','reverted_filters_sha256','estate_reads','model_calls')},indent=2))


if __name__=='__main__':main()
