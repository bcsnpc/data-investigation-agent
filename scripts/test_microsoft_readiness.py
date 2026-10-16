import copy,json,unittest,tempfile,hashlib
from pathlib import Path
from investigator.adapters.microsoft_readiness import validate_declared_route
from investigator.adapters.microsoft_self_report import compose
from investigator.process_debugging import attest_surface
import test_estate_manifest


def fixture():
    manifest=test_estate_manifest.ManifestTests().fixture();manifest['system_of_record']=None;manifest['lineage']['bindings']=[]
    manifest['layers']=copy.deepcopy(manifest['layers'][:2])
    fabric=manifest['adapters'][0]['options']['fabric'];workspace='fabric://'+fabric['workspace_id']
    root=manifest['layers'][0]['asset_id'].split('/table/')[0]
    gold=manifest['layers'][1]['asset_id'].split('/table/')[0]
    upper=root+'/table/Ledger';lower=gold+'/table/Rows';endpoint=workspace+'/55555555-5555-4555-8555-555555555555'
    for layer,asset in zip(manifest['layers'],(upper,lower)):layer['asset_id']=asset;layer['reach']['address']=asset
    partition={'name':'Ledger','mode':'directLake','source':{'type':'entity','schemaName':'dbo','entityName':'Rows','expressionSource':'Data'}}
    columns=[{'name':'units','sourceColumn':'units','dataType':'int64'}]
    measure=upper+'/measures/Figure';expression="SUM('Ledger'[units])"
    document={'model':{'tables':[{'name':'Ledger','columns':columns,'measures':[{'name':'Figure','expression':expression}],'partitions':[partition]}],
        'expressions':[{'name':'Data','expression':'let database = Sql.Database("'+fabric['sql_reader']['server']+'", "'+endpoint.rsplit('/',1)[1]+'") in database'}]}}
    def asset(id,kind,name,parent,metadata=None):return {'id':id,'kind':kind,'name':name,'parent_id':parent,'availability':'CURRENT','provenance':'DISCOVERED','metadata':metadata or {}}
    scan={'assets':[asset(root,'SemanticModel','Model',workspace),asset(upper,'SemanticTable','Ledger',root,{'partitions':[partition]}),
        asset(measure,'Measure','Figure',upper,{'expression':expression}),asset(upper+'/columns/units','SemanticColumn','units',upper,columns[0]),
        asset(root+'/part/model.bim','DefinitionPart','model.bim',root,{'content':json.dumps(document)}),
        asset(endpoint,'SQLEndpoint','GoldOps',workspace),asset(gold,'Lakehouse','Serving',workspace),asset(lower,'LakehouseTable','Rows',gold)],
        'graph':{'edges':[{'source':endpoint,'target':gold,'relation':'NATIVE_CASCADEDELETE'}]},'coverage':{}}
    def receipt(id,tool,query,surface):
        report={k:v for k,v in surface.items()if k!='connection'}
        return {'id':id,'tool':tool,'measure_id':measure,'query':query,'values':[{'value':{'type':'decimal','value':'17'}}],
            'read_address':{'kind':'BASELINE','restrictions':[]},'declared_context':{'version':1,'scope':'WHOLE_ENTITY','filters':[],'dimension_ids':[]},
            'surface_report_binding':'VALUE_QUERY','execution_surface':surface,'surface_report':report,
            'surface_attestation':attest_surface(surface,report,('engine','identity','object'))}
    a=receipt('upper','bounded_dax',compose('EVALUATE ROW("baseline", [Figure])'),{'engine':'OLAP Server','connection':fabric['workspace_id'],'object':root.rsplit('/',1)[1],'identity':fabric['native_reader']['account']})
    b=receipt('lower','bounded_fabric_sql','SELECT SUM([units]) AS [quantity] FROM [dbo].[Rows]',{'engine':'Microsoft Azure SQL Data Warehouse','connection':'sql://'+fabric['sql_reader']['server'],'object':'GoldOps','identity':fabric['sql_reader']['account']})
    c={'id':'comparison','upper_evidence_id':'upper','lower_evidence_id':'lower','upper_layer':upper,'lower_layer':lower,'values_equal':True}
    route={'selected_observations':[a,b,c],'read_receipts':[{'receipt_id':id,'status':'COMPLETED'}for id in('upper','lower')]}
    return manifest,scan,route


class DeclaredRouteTests(unittest.TestCase):
    def setUp(self):
        self.manifest,self.scan,self.route=fixture();self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.counter=0;self.seal()
    def seal(self):
        from investigator.process_tape import Tape
        from test_process_tape import bootstrap
        self.counter+=1;p=Path(self.temp.name)/str(self.counter)/'tape.json'
        definition=next(a for a in self.scan['assets']if a['kind']=='DefinitionPart')
        source={'id':'native-path','declared_source_binding':{'asset':{'id':self.route['selected_observations'][-1]['lower_layer']},
            'unchanged_connection':{'definition_hash':hashlib.sha256(definition['metadata']['content'].encode()).hexdigest()}}}
        Tape(p,bootstrap()).finish({'result':{'id':'native-session','observations':self.route['selected_observations']+[source],
            'process_read_receipts':self.route['read_receipts']}})
        self.route.update(captured_run_tape=str(p),captured_run_tape_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),session_id='native-session')
    def run_route(self):return validate_declared_route(self.route,manifest=self.manifest,scan=self.scan)
    def test_actual_compilers_derive_boundary_and_preserve_partial_snapshot_limits(self):
        before=copy.deepcopy((self.manifest,self.scan,self.route));result=self.run_route()
        self.assertEqual(result['boundary'],{'from_layer':'original-serving','to_layer':'original-model'})
        self.assertEqual(result['receipt_ids'],['upper','lower'])
        self.assertTrue(any('PARTIAL' in s for s in result['limits']))
        self.assertTrue(any('SNAPSHOT_UNVERIFIED' in s for s in result['limits']))
        self.assertEqual((self.manifest,self.scan,self.route),before)
    def test_producer_status_and_boundary_never_establish_readiness(self):
        self.route.update(status='VERIFIED',boundary={'from_layer':'invented','to_layer':'invented'})
        self.route['selected_observations'][1]['query']+=' WHERE 1=1'
        self.seal()
        with self.assertRaisesRegex(ValueError,'statements differ'):self.run_route()
    def test_query_bound_full_required_fields_checked_against_native_report(self):
        self.route['selected_observations'][0]['surface_report'].pop('engine')
        self.seal()
        with self.assertRaisesRegex(ValueError,'required fields'):self.run_route()
    def test_identity_only_matched_label_is_not_enough(self):
        o=self.route['selected_observations'][0];o['surface_report']={'identity':o['execution_surface']['identity']};o['surface_attestation']['status']='MATCHED'
        self.seal()
        with self.assertRaisesRegex(ValueError,'required fields'):self.run_route()
    def test_missing_original_receipt_refuses(self):
        self.route['read_receipts'].pop()
        self.seal()
        with self.assertRaisesRegex(ValueError,'completed native receipt'):self.run_route()
    def test_filtered_address_is_not_whole_entity(self):
        self.route['selected_observations'][0]['read_address']['restrictions']=[{'field_id':'key','operator':'IN','values':['North']}]
        self.seal()
        with self.assertRaisesRegex(ValueError,'unfiltered'):self.run_route()
    def test_changed_definition_and_source_column_cannot_pass(self):
        next(a for a in self.scan['assets']if a['kind']=='SemanticColumn')['metadata']['sourceColumn']='other'
        with self.assertRaisesRegex(ValueError,'SUM column differs'):self.run_route()
    def test_non_unique_declared_source_is_not_selected(self):
        source=copy.deepcopy(self.scan['assets'][-1]);source['id']+='-another';self.scan['assets'].append(source)
        with self.assertRaisesRegex(ValueError,'resolve uniquely'):self.run_route()
    def test_disagreeing_values_cannot_borrow_equal_flag(self):
        self.route['selected_observations'][1]['values'][0]['value']['value']='18'
        self.seal()
        with self.assertRaisesRegex(ValueError,'agreement'):self.run_route()
    def test_comparison_cannot_name_different_cell_or_surface(self):
        self.route['selected_observations'][-1]['upper_layer']='different'
        self.seal()
        with self.assertRaisesRegex(ValueError,'different declared boundary'):self.run_route()
    def test_mutated_value_with_same_receipt_id_cannot_borrow_sealed_proof(self):
        self.route['selected_observations'][1]['values'][0]['value']['value']='999'
        with self.assertRaisesRegex(ValueError,'sealed original'):self.run_route()
    def test_modified_native_receipt_array_cannot_borrow_tape_hash(self):
        self.route['read_receipts'][0]['status']='NOT_EXECUTED'
        with self.assertRaisesRegex(ValueError,'receipts differ'):self.run_route()

if __name__=='__main__':unittest.main()
