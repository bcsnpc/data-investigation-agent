"""Behavioral discovery-to-ticket tests; publisher metadata is separate from runtime."""
import base64
import copy
import json
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4
from types import SimpleNamespace

from investigator.onboarding import ModelStore, Conflict
from investigator.enterprise_discovery import Discovery
from investigator.discovery_collect import Collector
from investigator.model_context import assets
from investigator.workspace import Workspace
from investigator.question_intake import snapshot
from investigator.native_diagnostics import build
from investigator.native_identity import allows


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.ws=str(uuid4());self.mid=str(uuid4());self.rid=str(uuid4())
        self.config={'fabric':{'workspace_id':self.ws},'sql':{'server':'approved.database.windows.net',
            'database':'source','visibility_schema':'business'}}
        self.store=ModelStore(self.root/'catalog.sqlite',self.root/'inventory.sqlite','test')
        self.discovery=Discovery(self.store,self.config);self.denied=set()
        self.items=[{'id':self.mid,'type':'SemanticModel','displayName':'Unfamiliar operations'},
                    {'id':self.rid,'type':'Report','displayName':'Unfamiliar report'}]
        self.parts={self.mid:{'model.bim':json.dumps({'model':{'tables':[{'name':'Entities',
            'columns':[{'name':'region','dataType':'string'},{'name':'amount','dataType':'int64'}],
            'measures':[{'name':'Total','expression':'SUM(Entities[amount])'},
                        {'name':'Double','expression':'[Total]*2'}]}], 'relationships':[]}})},
            self.rid:{'definition.pbir':json.dumps({'datasetReference':{'byConnection':{'connectionString':'semanticmodelid='+self.mid}}}),
                'definition/report.json':'{}','definition/pages/p/page.json':'{"name":"p"}',
                'definition/pages/p/visuals/v/visual.json':json.dumps({'name':'v','visual':{'query':{'Measure':{
                    'Expression':{'SourceRef':{'Entity':'Entities'}},'Property':'Total'}}}})}}
        self.sql_objects=[{'object_id':1,'schema_name':'business','name':'events','type_desc':'USER_TABLE'},
                          {'object_id':2,'schema_name':'secret','name':'restricted','type_desc':'USER_TABLE'}]
        self.bindings=[{'id':self.rid,'datasetId':self.mid}]
        self.relations=[]

    def transport(self,endpoint,method='get',audience='fabric'):
        if any(d in endpoint for d in self.denied):raise PermissionError('not authorized')
        if endpoint=='workspaces':body={'value':[{'id':self.ws,'displayName':'Approved'}]}
        elif endpoint.endswith('/items'):body={'value':self.items}
        elif endpoint.endswith('/reports'):body={'value':self.bindings}
        elif '/relations/upstream' in endpoint:
            body={'items':[dict(x,workspaceId=self.ws) for x in self.items],'relations':self.relations,
                  'workspaces':[{'id':self.ws,'displayName':'Approved'}]}
        elif '/getDefinition' in endpoint:
            mid=endpoint.split('/')[3]
            body={'definition':{'parts':[{'path':p,'payloadType':'InlineBase64','payload':base64.b64encode(v.encode()).decode()} for p,v in self.parts[mid].items()]}}
        elif endpoint.endswith('/tables'):body={'data':[{'name':'new_fact','schemaName':'dbo'}]}
        elif endpoint.endswith('/jobs/instances') or endpoint.endswith('/refreshes'):body={'value':[]}
        else:raise ValueError(endpoint)
        return {'status_code':200,'text':body}

    def sql(self,*args):
        return {'server':self.config['sql']['server'],'database':'source','collected_at_utc':str(uuid4()),
            'visibility_schema':'business','objects':copy.deepcopy(self.sql_objects),
            'columns':[{'object_id':o['object_id'],'column_id':1,'name':'id','data_type':'int','is_nullable':False} for o in self.sql_objects],
            'keys':[],'definitions':[],'foreign_keys':[],'checks':[],
            'permissions':[{'can_view_definition':True}]}

    def scan(self,key=None):
        return self.discovery.run(Collector(self.config,self.transport,self.sql).run,key or str(uuid4()))

    def test_new_model_report_and_objects_reach_intake_without_registration(self):
        self.assertEqual(self.store.list(),[])
        result=self.scan();models=self.store.list(True)
        self.assertEqual(len(models),1);model=models[0]
        self.assertEqual(model['business'],{});self.assertEqual(model['reports'],[self.rid])
        self.assertEqual(len(model['context']['measures']),2)
        profile=model['context']['domain_profile']
        self.assertEqual(profile['authority'],'STRUCTURAL_HYPOTHESES_ONLY')
        self.assertEqual(profile['tables'][0]['data_profile'],'NOT_MEASURED')
        self.assertEqual(len(profile['tables'][0]['measure_ids']),2)
        self.assertTrue(assets(model['context']))
        workspace=Workspace(SimpleNamespace(store=self.store))
        resolved=snapshot(workspace)
        self.assertEqual(resolved['models'][0]['reports'][0]['name'],'Unfamiliar report')
        self.assertTrue(any(e['relation']=='DEPENDS_ON' for e in result['body']['graph']['edges']))
        self.assertTrue(any(e['relation']=='USES' and '/visual/' in e['source'] for e in result['body']['graph']['edges']))
        self.assertFalse(any(a['name']=='secret.restricted' for a in result['body']['assets']))
        column=next(a['id'] for a in assets(model['context']) if a['name']=='region')
        plan={'model_id':model['id'],'revision':model['revision'],'context_id':model['context_id'],
              'measure_ids':[model['context']['measures'][0]['id']],'filters':[{'column_id':column,'values':['West']}],
              'dimension_id':None,'include_dependencies':False}
        self.assertIn('EVALUATE',build(model,plan)['query'])

    def test_reportless_model_is_queryable_catalog_without_fake_report(self):
        self.items=self.items[:1];self.bindings=[]
        self.scan();model=self.store.list(True)[0]
        self.assertEqual(model['reports'],[]);self.assertEqual(model['context']['reports'],[])
        self.assertEqual(len(Workspace(SimpleNamespace(store=self.store)).model(model['id'])['measures']),2)

    def test_repeat_detects_new_tables_and_definition_changes(self):
        self.scan();before=self.store.list(True)[0]['context_id']
        lh=str(uuid4());self.items.append({'id':lh,'type':'Lakehouse','displayName':'A new lake'})
        self.sql_objects.append({'object_id':3,'schema_name':'business','name':'new_view','type_desc':'VIEW'})
        doc=json.loads(self.parts[self.mid]['model.bim']);doc['model']['tables'].append({'name':'Another','columns':[{'name':'id','dataType':'int64'}]})
        doc['model']['relationships']=[{'name':'link','fromTable':'Another','fromColumn':'id','toTable':'Entities','toColumn':'amount'}]
        self.parts[self.mid]['model.bim']=json.dumps(doc)
        result=self.scan()['body']
        self.assertTrue(any(a['kind']=='LakehouseTable' for a in result['assets']))
        self.assertTrue(any(a['name']=='business.new_view' for a in result['assets']))
        self.assertTrue(any(a['kind']=='SemanticRelationship' for a in result['assets']))
        self.assertNotEqual(self.store.list(True)[0]['context_id'],before)
        self.assertTrue(any(c['state']=='CHANGED' for c in result['changes']))

    def test_definition_denial_retains_children_and_disables_dispatch(self):
        self.scan();self.denied.add(self.mid+'/getDefinition')
        result=self.scan()['body'];model=self.store.list()[0]
        self.assertFalse(model['enabled']);self.assertEqual(len(model['context']['measures']),2)
        self.assertFalse(any(c['state']=='REMOVED' for c in result['changes']))
        self.assertTrue(any(c['state']=='UNKNOWN_DUE_TO_PARTIAL_SCAN' for c in result['changes']))

    def test_listing_denial_is_not_deletion(self):
        self.scan();self.denied.add('/items')
        changes=self.scan()['body']['changes']
        self.assertFalse(any(c['state']=='REMOVED' for c in changes))
        self.assertTrue(self.store.list());self.assertFalse(self.store.list(True))

    def test_complete_removal_hides_model_and_keeps_history(self):
        self.scan();old=self.store.list()[0]
        self.items=[];self.bindings=[]
        result=self.scan()
        self.assertFalse(self.store.list(True));self.assertTrue(self.store.context(old['id'],old['context_id']))
        self.assertTrue(any(c['state']=='REMOVED' for c in result['body']['changes']))

    def test_duplicate_names_remain_distinct(self):
        another=str(uuid4());self.items.append({'id':another,'type':'SemanticModel','displayName':'Unfamiliar operations'})
        self.parts[another]=copy.deepcopy(self.parts[self.mid]);self.scan()
        models=snapshot(Workspace(SimpleNamespace(store=self.store)))['models']
        self.assertEqual(len(models),2);self.assertNotEqual(models[0]['id'],models[1]['id'])

    def test_explicit_deny_survives_rescan(self):
        self.scan();m=self.store.list(True)[0];self.store.enable(m['id'],m['revision'],False,'operator')
        self.scan();self.assertEqual(self.store.list(True),[])

    def test_replay_never_collects_and_policy_key_mismatch_rejected(self):
        first=self.scan('one')
        self.assertEqual(self.discovery.run(lambda:self.fail('replayed remote scan'),'one')['id'],first['id'])
        changed=Discovery(self.store,dict(self.config,extra='changed'))
        with self.assertRaises(Conflict):changed.run(lambda:None,'one')

    def test_workspace_reader_policy_admits_new_model_without_id_registration(self):
        reader={'mode':'isolated_reader','tenant_id':str(uuid4()),'principal_id':str(uuid4()),
                'account':'reader@example.com','workspace_ids':[self.ws]}
        self.assertTrue(allows(reader,self.ws,str(uuid4())))
        self.assertFalse(allows(reader,str(uuid4()),self.mid))

    def test_search_is_scoped_and_preserves_duplicate_matches(self):
        from investigator.context_search import search,get_asset
        self.scan()
        found=search(self.store,{'text':'Unfamiliar','limit':1})
        self.assertEqual(found['total'],2);self.assertTrue(found['truncated'])
        asset=get_asset(self.store,found['assets'][0]['id'])
        self.assertTrue(asset['coverage']);self.assertTrue(asset['edges'])
        model=get_asset(self.store,'fabric://'+self.ws+'/'+self.mid)
        self.assertEqual(model['observations'][0]['capability'],'refresh_history')
        self.assertEqual(model['observations'][0]['detail'],[])
        report=get_asset(self.store,'fabric://'+self.ws+'/'+self.rid)
        self.assertEqual(report['observations'],[])
        other=ModelStore(self.store.database,self.store.inventory,'another')
        with self.assertRaisesRegex(Conflict,'No discovered environment context'):
            search(other,{'text':'Unfamiliar','limit':10})

    def test_unchanged_scan_has_no_timestamp_only_change(self):
        self.scan();second=self.scan()['body']
        self.assertEqual(second['changes'],[])

    def test_budget_failure_does_not_erase_prior_inventory(self):
        self.scan()
        result=self.discovery.run(Collector(self.config,self.transport,self.sql,max_calls=1).run,'budget')['body']
        self.assertFalse(any(c['state']=='REMOVED' for c in result['changes']))
        self.assertTrue(result['assets'])

    def test_schema_policy_change_removes_old_schema_even_when_new_scan_fails(self):
        self.scan()
        self.config['sql']['visibility_schema']='other'
        self.discovery=Discovery(self.store,self.config)
        def denied(*args):raise PermissionError('denied')
        result=self.discovery.run(Collector(self.config,self.transport,denied).run,'new-policy')['body']
        self.assertFalse(any(a['kind'] in ('SqlObject','SqlColumn','SqlSchema') for a in result['assets']))
        self.assertTrue(any(c.get('reason')=='OUTSIDE_CURRENT_POLICY' for c in result['changes']))

    def test_conflicting_explicit_binding_is_a_gap_not_arbitrary_selection(self):
        self.bindings[0]['datasetId']=str(uuid4())
        result=self.scan()['body']
        self.assertFalse(result['report_bindings'])
        self.assertTrue(any(g.get('reason')=='CONFLICTING_EXPLICIT_MODEL_BINDINGS' for g in result['graph']['gaps']))

    def test_native_item_relations_retain_exact_type_and_scoped_identities(self):
        endpoint=str(uuid4());lakehouse=str(uuid4())
        self.items.extend([{'id':endpoint,'type':'SQLEndpoint','displayName':'Endpoint'},
                           {'id':lakehouse,'type':'Lakehouse','displayName':'Lake'}])
        self.relations=[{'itemId':self.mid,'dependentOnItemId':endpoint,'relationType':'Association'},
                        {'itemId':endpoint,'dependentOnItemId':lakehouse,'relationType':'CascadeDelete'}]
        result=self.scan()['body'];edges=result['graph']['edges']
        self.assertTrue(any(e['source'].endswith(endpoint) and e['target'].endswith(lakehouse)
                            and e['relation']=='NATIVE_CASCADEDELETE' for e in edges))
        self.assertEqual(result['coverage']['fabric://'+self.ws+'/'+self.mid+'/relations/upstream']['status'],'COMPLETE')

    def test_malformed_binding_does_not_erase_enumerated_model(self):
        self.bindings[0]['datasetId']='invalid'
        result=self.scan()['body']
        self.assertEqual(len(self.store.list(True)),1)
        self.assertEqual(result['coverage']['fabric://'+self.ws+'/report_bindings']['status'],'UNAVAILABLE')


if __name__=='__main__':unittest.main()
