import hashlib,json,unittest
from investigator.adapters.estate_graph_static import extract
from investigator import estate_graph_contract as c

NOW='2026-10-13T01:00:00Z'
def asset(id,kind,name,parent=None,metadata=None):return {'id':id,'kind':kind,'name':name,'parent_id':parent,'metadata':metadata or {}}
def part(id,parent,name,content):return asset(id,'DefinitionPart',name,parent,{'content':content if isinstance(content,str) else json.dumps(content),'path':name})
def field(kind,table,name):return {kind:{'Expression':{'SourceRef':{'Entity':table}},'Property':name}}
class StaticTests(unittest.TestCase):
    def build(self,assets,**kwargs):
        self.blobs={};self.calls=[]
        def sink(raw):
            hash=hashlib.sha256(raw).hexdigest();self.blobs[hash]=raw;self.calls.append(hash)
            return {'sha256':hash,'bytes':len(raw),'uri':'cas://definitions/'+hash}
        result=extract('synthetic-estate',assets,sink,observed_at=NOW,**kwargs)
        self.assertEqual(len(self.calls),len(set(self.calls)))
        for item in result['nodes']+result['edges']:
            c.record(item,edge='source' in item)
            self.assertIn(item['provenance']['definition_hash'],self.blobs)
            self.assertNotEqual(item['confidence'],'VERIFIED')
        return result
    def assets(self):
        model='w/00000000-0000-0000-0000-000000000001'
        predicate={'Version':2,'Where':[{'Condition':{'In':{'Expressions':[field('Column','Data','Region')],'Values':[[{'Literal':{'Value':"'West'"}}]]}}}]}
        page={'name':'p','displayName':'Overview','filterConfig':{'filters':[{'name':'hidden-page','isHidden':True,'filter':predicate}]},
            'visualInteractions':[{'source':'s','target':'v','type':'DataFilter'}]}
        visual={'name':'v','visual':{'visualType':'card','query':{'field':field('Measure','Data','Amount')}}}
        slicer={'name':'s','visual':{'visualType':'slicer','objects':{'general':[{'properties':{'filter':{'filter':predicate}}}]},'query':{'field':field('Column','Data','Region')}}}
        return [asset('w','Workspace','Scope'),asset(model,'SemanticModel','Model','w'),
            asset(model+'/t','SemanticTable','Data',model),asset(model+'/t/c','SemanticColumn','Region',model+'/t'),
            asset(model+'/t/m','Measure','Amount',model+'/t',{'expression':'SUM(Data[Value])'}),
            asset('r','Report','Report','w'),part('binding','r','definition.pbir',{'datasetReference':{'byConnection':{'connectionString':'semanticmodelid='+model.split('/')[-1]}}}),
            asset('p','ReportPage','Overview','r',page),part('page-def','r','definition/pages/p/page.json',page),
            asset('v','ReportVisual','Card','p',visual),part('visual-def','r','definition/pages/p/visuals/v/visual.json',visual),
            asset('s','ReportVisual','Region choice','p',slicer),part('slicer-def','r','definition/pages/p/visuals/s/visual.json',slicer)]
    def test_hidden_filters_saved_slicer_and_interactions_reach_graph_with_exact_parts(self):
        graph=self.build(self.assets());nodes={n['id']:n for n in graph['nodes']}
        self.assertEqual(sum(n['kind']=='SLICER' for n in nodes.values()),1)
        filters=[n for n in nodes.values() if n['kind']=='FILTER'];self.assertEqual(len(filters),2)
        self.assertTrue(all(n['properties']['predicate_present'] for n in filters))
        self.assertTrue(any(n['properties']['hidden'] is True for n in filters))
        visual=next(n for n in nodes.values() if n['properties'].get('asset_id')=='v')
        self.assertEqual(visual['provenance']['source_id'],'visual-def')
        self.assertTrue(any(e['source']==visual['id'] and e['kind']=='FILTERED_BY' and e['properties'].get('inherited_from') for e in graph['edges']))
        self.assertTrue(any(e['kind']=='INTERACTS_WITH' for e in graph['edges']))
        self.assertTrue(any('Engine-resolved' in n['label'] for n in nodes.values()))
    def test_model_binding_ambiguity_never_guessed_by_measure_name(self):
        assets=self.assets();assets=[a for a in assets if a['id']!='binding']
        graph=self.build(assets)
        self.assertTrue(any('report-to-model' in n['label'] for n in graph['nodes']))
        self.assertTrue(any(e['confidence']=='UNKNOWN' for e in graph['edges']))
    def test_field_only_filter_preserved_as_no_predicate(self):
        assets=self.assets();assets[7]['metadata']['filterConfig']['filters'].append({'name':'field-only','field':field('Column','Data','Region')})
        graph=self.build(assets)
        self.assertTrue(any(n['kind']=='FILTER' and n['properties']['predicate_present'] is False for n in graph['nodes']))
    def test_roles_calculation_groups_parameters_and_m_steps(self):
        assets=self.assets();model=assets[1]['id']
        doc={'model':{'roles':[{'name':'Region role','tablePermissions':[{'name':'Data','filterExpression':'[Region] = "West"'}]}],
            'tables':[{'name':'Choices','calculationGroup':{},'columns':[{'name':'Field','extendedProperties':[{'name':'ParameterMetadata'}]}],
                'partitions':[{'source':{'type':'m','expression':'let Source = table,\n Filtered = Table.SelectRows(Source, each [A] > 0) in Filtered'}}]}]}}
        assets.append(part('bim',model,'model.bim',doc));graph=self.build(assets)
        for kind in ('SECURITY_ROLE','CALCULATION_GROUP','FIELD_PARAMETER','QUERY_STEP'):
            self.assertTrue(any(n['kind']==kind for n in graph['nodes']),kind)
        self.assertTrue(any(n['properties'].get('scope')=='RLS' for n in graph['nodes']))
    def test_sql_explicit_projection_and_hidden_where_are_column_bound(self):
        assets=[asset('db','SqlDatabase','db'),asset('src','SqlObject','app.source','db'),asset('src/c','SqlColumn','amount','src'),
            asset('view','SqlObject','app.view','db',{'type':'V','definitions':[{'definition':'CREATE VIEW app.view AS SELECT s.amount AS revenue FROM app.source s WHERE s.amount > 0'}]}),
            asset('view/c','SqlColumn','revenue','view')]
        graph=self.build(assets,source_asset_ids=['src']);nodes={n['id']:n for n in graph['nodes']}
        source=next(n for n in nodes.values() if n['properties'].get('asset_id')=='src/c')
        output=next(n for n in nodes.values() if n['properties'].get('asset_id')=='view/c')
        self.assertTrue(source['properties']['system_of_record'])
        self.assertTrue(any(e['source']==output['id'] and e['target']==source['id'] for e in graph['edges']))
        self.assertTrue(any(n['kind']=='FILTER' for n in nodes.values()))
    def test_dynamic_procedure_and_notebook_calls_are_unknown_not_fabricated_links(self):
        graph=self.build([asset('db','SqlDatabase','db'),asset('proc','SqlObject','app.proc','db',{'type':'P',
            'definitions':[{'definition':"DECLARE @q nvarchar(max) = 'SELECT 1'; EXEC(@q)"}]}),
            asset('nb','Notebook','Notebook'),part('py','nb','notebook-content.py',"frame = spark.table(name)\nframe.filter('amount > 0').write.saveAsTable(target)")])
        self.assertTrue(any(n['kind']=='PROCEDURE' for n in graph['nodes']))
        self.assertTrue(any(n['kind']=='FILTER' for n in graph['nodes']))
        self.assertGreater(sum(e['confidence']=='UNKNOWN' for e in graph['edges']),1)
        for n in graph['nodes']:
            if n['provenance']['source_id']=='py':self.assertEqual(n['provenance']['span']['kind'],'TEXT')
    def test_copy_mapping_text_not_mistaken_for_resolved_object(self):
        graph=self.build([asset('pipeline','DataPipeline','Load'),part('definition','pipeline','pipeline-content.json',
            {'properties':{'activities':[{'name':'Copy','type':'Copy','typeProperties':{'translator':{'mappings':[{'source':{'name':'a'},'sink':{'name':'b'}}]}}}]}})])
        self.assertTrue(any(n['kind']=='COPY_ACTIVITY' for n in graph['nodes']))
        self.assertTrue(any(e['kind']=='DERIVED_IN_STEP' for e in graph['edges']))
        self.assertTrue(any('connection' in n['label'] for n in graph['nodes']))
    def test_tmdl_headers_retained_without_dax_dependency_guess(self):
        graph=self.build([asset('m','SemanticModel','Model'),part('tmdl','m','definition/tables/Values.tmdl',"table 'Values'\n\tcolumn amount\n\tmeasure Total = SUM('Values'[amount])\n")])
        self.assertTrue(any(n['kind']=='MEASURE' for n in graph['nodes']))
        self.assertTrue(any(e['confidence']=='UNKNOWN' for e in graph['edges']))
    def test_asset_deletion_changes_snapshot_even_when_raw_definition_hash_set_does_not(self):
        assets=[asset('one','LakehouseTable','One'),asset('two','LakehouseTable','Two')]
        first=self.build(assets);second=self.build(assets[:1])
        self.assertNotEqual(first['definition_hash'],second['definition_hash'])

    def test_retained_metadata_tampering_is_refused_before_extraction(self):
        assets=self.assets();assets[0]['content_hash']='0'*64
        with self.assertRaisesRegex(ValueError,'RETAINED_METADATA_HASH'):self.build(assets)

    def test_string_mention_is_not_a_power_query_filter(self):
        result=self.build([asset('m','SemanticModel','Model'),part('m-code','m','query.m','let Label = "Table.SelectRows" in Label')])
        self.assertFalse(any(n['kind']=='FILTER' for n in result['nodes']))

    def test_definition_sink_cannot_return_unverified_or_missing_storage_reference(self):
        with self.assertRaisesRegex(ValueError,'DURABLE_DEFINITION'):
            extract('estate',self.assets(),lambda raw:{},observed_at=NOW)

class DefinitionSinkTests(unittest.TestCase):
    def test_existing_cas_restores_exact_definition_and_deduplicates(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import Mock
        from investigator.artifact_store import Files,LocalObjects
        from investigator.graph_definitions import DefinitionSink
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);files=Files(LocalObjects(root/'cas'));files.capture=Mock(wraps=files.capture)
            sink=DefinitionSink(files,'cas://definitions',recording_class='EXACT',scratch=root)
            raw=b'{"original": "raw retained bytes"}';first=sink(raw);self.assertEqual(first,sink(raw))
            self.assertEqual(files.capture.call_count,1)
            self.assertEqual(files.restore(first['sha256'],root/'restored').read_bytes(),raw)
            self.assertFalse(list(root.glob('graph-definition-*')))
    def test_projected_installation_does_not_fall_back_to_raw_capture(self):
        from investigator.graph_definitions import DefinitionSink
        with self.assertRaisesRegex(ValueError,'PROJECTED'):
            DefinitionSink(None,'cas://definitions',recording_class='PRIVACY_PROJECTED')

if __name__=='__main__':unittest.main()
