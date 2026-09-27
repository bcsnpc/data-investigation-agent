import copy,json,unittest
from investigator.adapters.notebook_quantities import DeclaredQuantities,Unsupported
from investigator.adapters.declared_chain import extend
from investigator.process_debugging import vertical,Probe

def definition():
    tables=[{'name':'events','columns':[['key','int'],['amount','int']], 'rows':[[1,2]]},
            {'name':'lookup','columns':[['key','int'],['rate','int']], 'rows':[[1,3]]}]
    return """import json
from pyspark.sql import functions as F
rows=json.loads(%r)
paths={'raw':'raw/','clean':'clean/','served':'served/'}
for table in rows:
    schema=', '.join(name+' '+('long' if kind=='int' else 'string') for name,kind in table['columns'])
    data=spark.createDataFrame(table['rows'],schema)
    data.write.format('delta').mode('errorifexists').save(paths['raw']+table['name'])
    spark.read.format('delta').load(paths['raw']+table['name']).dropDuplicates().write.format('delta').mode('errorifexists').save(paths['clean']+table['name'])
events=spark.read.format('delta').load('clean/events')
lookup=spark.read.format('delta').load('clean/lookup')
joined=events.join(lookup,['key'],'left').withColumn('value',F.col('amount')*F.col('rate'))
joined.write.format('delta').mode('errorifexists').save('served/output')
""" % json.dumps(tables)

class QuantityTraceTests(unittest.TestCase):
    def test_tracks_unchanged_column_and_explicit_multiplicity_without_data(self):
        q=DeclaredQuantities(definition())
        output=q.writes['served/output'];self.assertEqual(output.origins['amount'],('clean/events','amount'))
        self.assertNotIn('value',output.origins)
        self.assertEqual(output.operations[0]['operation'],'JOIN')
        self.assertIn('multiply',output.operations[0]['grain'])
        self.assertEqual(q.writes['clean/events'].origins['amount'],('raw/events','amount'))
        self.assertEqual(q.writes['clean/events'].operations[0]['operation'],'DEDUPE')
        self.assertEqual(q.writes['raw/events'].origins,{})
        self.assertNotIn('rows',vars(output))

    def test_unsupported_dedupe_filter_udf_shadow_and_ambiguous_columns_fail_closed(self):
        for before,after in [('.dropDuplicates()',".dropDuplicates(['key'])"),
                             ("events.join(lookup,['key'],'left')","events.filter('amount > 0')"),
                             ("F.col('amount')*F.col('rate')","F.explode(F.col('amount'))"),
                             ('import json','import json\njson = 1'),
                             ('import json','import json\nimport another_module as spark'),
                             ('schema)', 'schema, verifySchema=False)'),
                             ('rate','amount')]:
            with self.subTest(after=after),self.assertRaises((Unsupported,ValueError)):
                DeclaredQuantities(definition().replace(before,after))

    def context(self):
        assets=[]
        for path in ['served/output','clean/events','clean/lookup','raw/events','raw/lookup']:
            parent,name=path.split('/')
            assets.append({'id':path,'kind':'LakehouseTable','name':name,'parent_id':parent,
                'availability':'CURRENT','metadata':{'location':path}})
        assets.append({'id':'definition','kind':'DefinitionPart','parent_id':'job','availability':'CURRENT',
                       'metadata':{'path':'notebook-content.py','content':definition()}})
        layers=[{'id':'report','kind':'presentation'}, {'id':'served/output','kind':'declared_source',
                  'measure':{},'semantic_column':'amount','declared_columns':[{'name':'amount','sourceColumn':'amount'}]}]
        return {'assets':assets},layers

    def test_extension_uses_declared_column_branch_not_rates_and_no_guessed_application(self):
        context,layers=self.context();path,contracts,gap=extend(context,layers)
        self.assertEqual([l['id'] for l in path],['report','served/output','clean/events','raw/events'])
        self.assertEqual([c['operations'][0]['operation'] for c in contracts],['JOIN','DEDUPE'])
        self.assertIn('No declared upstream read',gap['reason'])
        self.assertEqual(gap['upper_layer'],'raw/events')
        context['assets'].append({**context['assets'][1],'id':'other'})
        path,_,gap=extend(context,layers)
        self.assertEqual(len(path),2);self.assertIn('ambiguous',gap['reason'])

    def test_changed_measured_column_is_not_traced_as_equivalent(self):
        context,layers=self.context()
        context['assets'][-1]['metadata']['content']=definition().replace("withColumn('value'","withColumn('amount'")
        path,_,gap=extend(context,layers)
        self.assertEqual(len(path),2);self.assertIn('derived/unsupported',gap['reason'])

class DepthTests(unittest.TestCase):
    def test_inconclusive_definition_does_not_turn_into_defect(self):
        from test_process_debugging import Adapter
        a=Adapter(['report','served','clean'],dict(report=10,served=10,clean=8))
        a.transformation_definition=lambda boundary:{'status':'COMPLETED','explains':None,
            'explanation':'Row multiplicity was not measured.','limitation':'No shared snapshot'}
        result=vertical(a,'measure',{})
        self.assertEqual(result['classification'],'NO_KNOWN_PATTERN')
        self.assertTrue(any(x['capability']=='transformation_definition' for x in result['technical_output']['skipped_steps']))

    def test_endpoint_binding_and_reader_are_required_before_quantity_execution(self):
        from test_independent_lower_read import Harness,WS
        from unittest.mock import patch
        h=Harness();endpoint='fabric://'+WS+'/endpoint'
        h.CONTEXT={'assets':[{'id':endpoint,'kind':'SQLEndpoint','name':'lower_db','availability':'CURRENT'}]}
        h.adapter.read_endpoint=lambda request:{'id':'lake','properties':{'sqlEndpointProperties':{
            'id':'endpoint','connectionString':'lower.example.invalid'}}}
        layer={'id':'input','kind':'declared_quantity','source_column':'amount',
               'binding':{'asset':{'parent_id':'fabric://'+WS+'/lake'},'provenance':'DECLARED_BY_DEFINITION'},
               'quantity_contract':{},'compiled':{'source_column':'amount','schema':'dbo','table':'events',
                'catalog':[{'id':'input','metadata':{'schema_name':'dbo','name':'events','type_desc':'USER_TABLE',
                    'columns':[{'name':'amount','data_type':'bigint'}]}}]}}
        self.assertEqual(h.evaluate(copy.deepcopy(layer)).status,'OBSERVED')
        self.assertEqual(len(h.lower_calls),1)
        h.adapter.read_endpoint=lambda request:{'id':'lake','properties':{'sqlEndpointProperties':{
            'id':'endpoint','connectionString':'another.example.invalid'}}}
        self.assertEqual(h.evaluate(copy.deepcopy(layer)).status,'UNAVAILABLE')
        self.assertEqual(len(h.lower_calls),1)
        self.assertEqual(h.evaluate(copy.deepcopy(layer),{'dimension_ids':['group']}).status,'NOT_COMPARABLE')
        h.adapter.lower_surface=None
        self.assertEqual(h.evaluate(copy.deepcopy(layer)).status,'UNAVAILABLE')
        self.assertEqual(len(h.lower_calls),1)

    def test_equal_boundaries_descend_and_divergence_names_unchecked_depth(self):
        from test_process_debugging import Adapter
        for values,expected in [(dict(report=10,served=10,clean=10,raw=10),3),
                                (dict(report=10,served=10,clean=8,raw=8),2)]:
            a=Adapter(['report','served','clean','raw'],values,explain=True)
            original=a.resolve_path
            def path(measure):
                p=original(measure);p['max_boundaries']=3;return p
            a.resolve_path=path
            result=vertical(a,'measure',{})
            self.assertEqual(result['technical_output']['boundary_summary']['comparisons_executed'],expected)
            for key in ('business_output','technical_output'):
                unchecked=result[key]['unverified_boundaries']
                self.assertEqual(len(unchecked),3-expected)
                if unchecked:self.assertEqual(unchecked[0]['lower_layer'],'raw')

    def test_unsupported_quantity_does_not_become_equality(self):
        from test_process_debugging import Adapter
        a=Adapter(['report','served','clean','raw'],dict(report=10,served=10,clean=10,raw=10),not_comparable=('clean',))
        result=vertical(a,'measure',{})
        self.assertEqual(result['technical_output']['boundary_summary']['comparisons_executed'],1)
        self.assertEqual(len(result['technical_output']['unverified_boundaries']),2)
        self.assertTrue(all(x['reason']=='No faithful translation' for x in result['technical_output']['unverified_boundaries']))

    def test_definition_receipt_retains_contract_and_rejects_mismatch(self):
        from investigator.synthesis_digest import _context_evidence
        from investigator.runtime import Conflict
        contract={'definition_asset_id':'definition','definition_hash':'hash','operations':[{'operation':'JOIN'}]}
        observation={'id':'receipt','tool':'context','process_roles':['transformation_definition'],
                     'asset_id':'definition','content_hash':'hash','operations':contract['operations'],
                     'quantity_contract':contract,'limitation':'No shared snapshot',
                     'judgment':{'status':'COMPLETED','limitation':'Multiplicity not measured'}}
        self.assertEqual(_context_evidence(observation)['result']['quantity_contract'],contract)
        observation['content_hash']='different'
        with self.assertRaises(Conflict):_context_evidence(observation)

    def test_ceiling_cannot_claim_or_probe_unchecked_layers(self):
        from test_process_debugging import Adapter
        # Use the established contract fixture, retaining its attested probes.
        a=Adapter(['report','served','clean','raw'],dict(report=10,served=10,clean=10,raw=10))
        original=a.resolve_path
        def path(measure):
            p=original(measure);p['max_boundaries']=0;return p
        a.resolve_path=path
        answer=vertical(a,'measure',{})
        self.assertEqual(answer['technical_output']['boundary_summary']['comparisons_executed'],0)
        for key in ('business_output','technical_output'):
            self.assertTrue(answer[key]['unverified_boundaries'])
            self.assertEqual(answer[key]['depth_ceiling'],0)
            self.assertTrue(any('Configured boundary ceiling' in x for x in answer[key]['mandatory_limits']))

if __name__=='__main__':unittest.main()
