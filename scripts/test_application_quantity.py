"""The application hop never follows a name or guesses copy equivalence."""
import copy,json,unittest
from unittest.mock import patch
import test_discovered_source_connection as fixtures
from investigator.adapters.copy_quantity import resolve
from investigator.adapters.declared_chain import extend
import application_sql_surface


class CopyQuantityTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.SourceConnectionTests('test_exact_declared_connection_binds_source_and_strips_credentials')
        self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        f=self.fixture
        doc=json.loads(f.parts[f.job]['copyjob-content.json'])
        prop=doc['properties'];prop['jobMode']='Batch'
        prop['source']['type']='AzureSqlTable';prop['source']['connectionSettings']['type']='AzureSqlDatabase'
        prop['destination']['type']='LakehouseTable';prop['destination']['connectionSettings']['typeProperties']['rootFolder']='Tables'
        p=doc['activities'][0]['properties'];p['source']['partitionSettings']={'partitionOption':'None'}
        p['destination'].update(writeBehavior='Overwrite',partitionOption='None')
        p.update(enableStaging=False,translator={'type':'TabularTranslator','mappings':[{'source':{'name':'id'},'destination':{'name':'id'}}]},
            typeConversionSettings={'typeConversion':{'allowDataTruncation':False,'treatBooleanAsNumber':False}})
        f.parts[f.job]['copyjob-content.json']=json.dumps(doc)
        original=f.sql
        def sql(*args):
            data=original(*args)
            for c in data['columns']:c['computed_definition']=None
            return data
        f.sql=sql
        self.context=f.scan()['body'];self.target='fabric://'+f.ws+'/'+f.lake+'/table/dbo.new_fact'

    def test_served_mapping_extends_to_exact_application_object(self):
        p,reason=resolve(self.context,self.target,'id')
        self.assertIsNone(reason);self.assertEqual(p['source']['name'],'business.events')
        layers=[{'id':'presentation','kind':'presentation'}, {'id':self.target,'kind':'declared_source',
            'measure':{},'semantic_column':'id','declared_columns':[{'name':'id','sourceColumn':'id'}]}]
        path,contracts,gap=extend(self.context,layers)
        self.assertIsNone(gap)
        self.assertEqual(path[-1]['id'],p['source']['id'])
        self.assertEqual(path[-1]['kind'],'application_quantity')
        self.assertEqual(path[-1]['binding']['provenance'],'DECLARED_BY_DEFINITION')
        self.assertEqual(contracts[0]['operations'][0]['operation'],'COPY')

    def test_unknown_predicate_incremental_append_expression_or_truncation_refuses(self):
        changes=[lambda d:d['activities'][0]['properties']['source'].update(query='select id from somewhere'),
            lambda d:d['properties'].update(jobMode='Incremental'),
            lambda d:d['properties']['source'].update(filter='unknown'),
            lambda d:d['activities'][0]['properties']['destination'].update(writeBehavior='Append'),
            lambda d:d['activities'][0]['properties']['translator']['mappings'][0]['source'].update(expression='id+1'),
            lambda d:d['activities'][0]['properties']['typeConversionSettings']['typeConversion'].update(allowDataTruncation=True)]
        for change in changes:
            context=copy.deepcopy(self.context)
            part=next(a for a in context['assets'] if a['kind']=='DefinitionPart' and a['metadata'].get('path')=='copyjob-content.json')
            doc=json.loads(part['metadata']['content']);change(doc);part['metadata']['content']=json.dumps(doc)
            with self.subTest(change=change):self.assertIsNone(resolve(context,self.target,'id')[0])

    def test_stale_connection_or_computed_source_or_ambiguous_edge_refuses(self):
        for change in ('stale','computed','ambiguous'):
            context=copy.deepcopy(self.context)
            if change=='stale':next(a for a in context['assets'] if a['kind']=='SourceConnection')['availability']='UNKNOWN'
            if change=='computed':next(a for a in context['assets'] if a['name']=='business.events')['metadata']['columns'][0]['computed_definition']='1+1'
            if change=='ambiguous':context['graph']['edges'] += [copy.deepcopy(e) for e in context['graph']['edges'] if e['source']==self.target and e['relation']=='DERIVED_FROM']
            with self.subTest(change=change):self.assertIsNone(resolve(context,self.target,'id')[0])

    def test_application_probe_uses_governed_source_catalog_and_retains_value_bound_report(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        from investigator.process_debugging import attest_surface
        f=self.fixture;model=f.store.list(True)[0]
        layers=[{'id':'presentation'}, {'id':self.target,'kind':'declared_source',
            'measure':{},'semantic_column':'id','declared_columns':[{'name':'id','sourceColumn':'id'}]}]
        layer=extend(self.context,layers)[0][-1]
        config=copy.deepcopy(f.config);config['sql']['auth']={'mode':'dpapi_file','credential_file':'unused','account':'reader'}
        calls=[]
        def read(config,request):
            calls.append(request)
            return {'rows':[{'quantity':'7'}],'column_types':{'quantity':'Int64'},'read_only_verified':True,
                'execution_identity':{'principal':'reader'},'surface_report':{'identity':'reader','engine':'Microsoft SQL Azure','object':'source'},
                'surface_report_binding':'VALUE_QUERY'}
        adapter=MicrosoftProcessAdapter(f.store,config,model,None,None)
        with patch('application_sql_surface.read',side_effect=read):
            probe=adapter.evaluate(layer,'measure',{})
        self.assertEqual(probe.status,'OBSERVED')
        self.assertEqual(probe.value,{'quantity':'7'})
        self.assertEqual(len(calls),1)
        self.assertTrue(calls[0]['require_read_only'])
        self.assertEqual(calls[0]['read_only_objects'],['[business].[events]'])
        self.assertEqual(probe.surface_report_binding,'VALUE_QUERY')
        self.assertEqual(attest_surface(probe.execution_surface,probe.surface_report)['consistency'],'MATCHED')

    def test_filtered_scope_or_missing_declared_identity_never_dispatches(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        f=self.fixture;model=f.store.list(True)[0]
        layers=[{'id':'presentation'}, {'id':self.target,'kind':'declared_source',
            'measure':{},'semantic_column':'id','declared_columns':[{'name':'id','sourceColumn':'id'}]}]
        layer=extend(self.context,layers)[0][-1]
        adapter=MicrosoftProcessAdapter(f.store,f.config,model,None,None)
        with patch('application_sql_surface.read',side_effect=AssertionError('must not dispatch')):
            self.assertEqual(adapter.evaluate(layer,'measure',{'filters':[{'column_id':'c','values':['x']}]}).status,'NOT_COMPARABLE')
            self.assertEqual(adapter.evaluate(layer,'measure',{}).status,'UNAVAILABLE')


class ApplicationSelfReportTests(unittest.TestCase):
    def request(self):return {'query':'SELECT SUM([id]) AS [quantity] FROM [business].[events]',
        'parameters':[],'require_read_only':True,'read_only_objects':['[business].[events]'],
        'max_rows':20,'result_columns':['quantity']}
    def response(self,edition='5'):
        return {'rows':[{'quantity':'2','__application_identity':'reader','__application_engine':edition,
            '__application_object':'application'}],'column_types':{'quantity':'Int64'},'read_only_verified':True}
    def test_guarded_quantity_and_self_description_are_one_statement_without_retry(self):
        calls=[]
        def execute(config,request):calls.append(request);return self.response()
        result=application_sql_surface.read({},self.request(),execute=execute)
        self.assertEqual(len(calls),1)
        self.assertIn(self.request()['query'],calls[0]['query'])
        self.assertEqual(calls[0]['read_only_objects'],self.request()['read_only_objects'])
        self.assertEqual(result['rows'],[{'quantity':'2'}])
        self.assertEqual(result['surface_report'],{'identity':'reader','engine':'Microsoft SQL Azure','object':'application'})
        self.assertEqual(result['surface_report_binding'],'VALUE_QUERY')
    def test_application_connection_retry_retains_error_and_guarded_result(self):
        from unittest.mock import Mock
        failure={'error':'SQL_READ_FAILED','stage':'connect','sql_error_number':40613}
        execute=Mock(side_effect=[failure,self.response()])
        with patch('sql_connect_retry.time.sleep'):
            # Explicit sleep injection avoids default-argument capture.
            import sql_connect_retry
            with patch('application_sql_surface.read_with_retry',
                side_effect=lambda read:sql_connect_retry.read_with_retry(read,lambda delay:None)):
                result=application_sql_surface.read({},self.request(),execute=execute)
        self.assertEqual(execute.call_count,2)
        self.assertEqual(result['connection_attempts'][0]['sql_error_number'],40613)
        self.assertEqual(result['connection_attempts'][1]['status'],'SUCCEEDED')
        self.assertTrue(result['read_only_verified'])
        self.assertEqual(result['rows'],[{'quantity':'2'}])
    def test_missing_guards_self_report_or_wrong_engine_is_not_attested(self):
        request=self.request();request['require_read_only']=False
        with self.assertRaises(ValueError):application_sql_surface.read({},request,execute=self.fail)
        for response in (self.response('6'),dict(self.response(),read_only_verified=False),{'rows':[{'quantity':'2'}],'read_only_verified':True}):
            with self.assertRaises(ValueError):application_sql_surface.read({},self.request(),execute=lambda *args:response)


if __name__=='__main__':unittest.main()
