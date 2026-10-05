import copy,unittest
from types import SimpleNamespace
from investigator.adapters.code_verification import VerificationRoute,resolve_objects
from investigator.onboarding import digest
from investigator.process_debugging import Probe
from test_lineage_binding import proposal


class RouteTests(unittest.TestCase):
    def setup_route(self):
        self.calls=[]
        def execute(layer,measure,compiled):
            self.calls.append(copy.deepcopy(compiled))
            surface={'engine':'SQL','connection':'sql://declared-server','object':compiled['database'],'identity':'reader'}
            from investigator.process_quantity import quantity
            rows=[{'quantity':7}]
            return Probe('OBSERVED',layer['id'],evidence={'id':'read-receipt','values':rows,
                'read_address':compiled['read_address'],'context_id':'retained'},value=quantity(rows),execution_surface=surface,surface_report=surface,
                surface_reportable=tuple(surface),surface_report_binding='VALUE_QUERY',
                surface_report_types={'engine':'ENGINE_PRODUCT','object':'DATABASE_CATALOG_NAME'})
        process=SimpleNamespace(model={'context_id':'retained'},config={'fabric':{'sql_reader':{'server':'declared-server'}}},_evaluate_lower=execute)
        objects={name:{'asset_id':name,'connection':'declared-server','database':database,
            'catalog':{'id':name,'metadata':{'schema_name':'dbo','name':'items','type_desc':'USER_TABLE',
                'columns':[{'name':'amount','data_type':'int'}]}}}
            for name,database in [('input-table','input-db'),('output-table','output-db')]}
        self.cell={'target_id':'target','measure_id':'measure','grouping_columns':[],
                   'key_restrictions':[],'mode':'UNGROUPED'}
        self.cell['id']=digest(self.cell)
        return VerificationRoute(process,objects=objects,context='retained',measure_id='measure',quantity_column='amount',restrictions=[])

    def test_actual_probe_context_must_match_the_verification_sample(self):
        route=self.setup_route();route.process.model['context_id']='different-retained-context'
        with self.assertRaisesRegex(ValueError,'actual probe context'):
            route.compile(proposal(),'SOURCE','retained',self.cell,{'state':'EXACT'})
        self.assertEqual(self.calls,[])

    def test_original_probe_address_cannot_be_replaced_by_caller_annotation(self):
        route=self.setup_route()
        original=route.process._evaluate_lower
        def wrong(layer,measure,compiled):
            probe=original(layer,measure,compiled)
            probe.evidence['read_address']={'kind':'BASELINE','restrictions':[]}
            return probe
        route.process._evaluate_lower=wrong
        plan=route.compile(proposal(),'SOURCE','retained',self.cell,{'state':'EXACT'})
        result=route.execute('SOURCE',plan)
        self.assertEqual(result['status'],'FAILED')
        self.assertIn('Original probe receipt context or cell address differs',result['reason'])
        self.assertEqual(result['evidence']['read_address'],{'kind':'BASELINE','restrictions':[]})

    def test_unrelated_column_cannot_be_read_under_existing_cell_identity(self):
        route=self.setup_route();p=proposal();p['target']['column']='other';p['expression']['column']='other'
        with self.assertRaisesRegex(NotImplementedError,'not the quantity'):
            route.compile(p,'SOURCE','retained',self.cell,{'state':'EXACT'})
        self.assertEqual(self.calls,[])

    def test_existing_probe_route_preserves_cell_and_original_receipt_attestation(self):
        route=self.setup_route();plan=route.compile(proposal(),'SOURCE','retained',self.cell,{'state':'EXACT'})
        result=route.execute('SOURCE',plan)
        self.assertEqual(result['status'],'COMPLETED');self.assertEqual(result['quantity'],{'state':'NUMBER','value':'7'})
        self.assertEqual(self.calls[0]['read_address'],{'kind':'CELL','cell':self.cell})
        self.assertEqual(result['evidence']['values'],[{'quantity':7}])
        self.assertEqual(result['evidence']['surface_report_receipt_id'],'read-receipt')

    def test_application_side_uses_its_own_guarded_reader_and_original_receipt(self):
        from unittest.mock import patch
        from application_sql_surface import ENGINE
        route=self.setup_route();process=route.process
        process.model.update(id='catalog-model',revision=3)
        process.store=object();process.meter_read=lambda tool,execute:execute()
        process.config['sql']={'server':'application-server','database':'application-db',
            'visibility_schema':'app','auth':{'account':'application-reader'}}
        route.objects['input-table'].update(surface='APPLICATION_SQL',connection='application-server',database='application-db')
        route.objects['input-table']['catalog']['metadata']['schema_name']='app'
        plan=route.compile(proposal(),'SOURCE','retained',self.cell,{'state':'EXACT'})
        def run(store,request,config,tool,execute):
            self.assertEqual(tool,'bounded_sql')
            self.assertEqual(request['context_id'],'retained')
            self.assertEqual(request['read_address'],{'kind':'CELL','cell':self.cell})
            self.assertIn('[app].[items]',request['query'])
            return {'id':'application-receipt','status':'COMPLETED','request_hash':'sealed-request',
                'result':{'rows':[{'quantity':'7'}],'completeness':'COMPLETE_RESPONSE',
                    'surface_report':{'engine':ENGINE,'object':'application-db','identity':'application-reader'},
                    'surface_report_binding':'VALUE_QUERY'}}
        with patch('investigator.flexible_tools.run',side_effect=run):
            result=route.execute('SOURCE',plan)
        self.assertEqual(result['status'],'COMPLETED')
        self.assertEqual(result['quantity'],{'state':'NUMBER','value':'7'})
        self.assertEqual(result['evidence']['id'],'application-receipt')
        self.assertEqual(result['evidence']['execution_surface']['identity'],'application-reader')
        self.assertEqual(result['evidence']['surface_attestation']['status'],'PARTIAL')
        self.assertEqual(self.calls,[])

    def test_filtered_scope_still_refuses_before_read(self):
        route=self.setup_route();route.restrictions=[{'field_id':'a','values':[1]}]
        with self.assertRaisesRegex(NotImplementedError,'Filtered or grouped'):
            route.compile(proposal(),'SOURCE','retained',self.cell,{'state':'EXACT'})
        self.assertEqual(self.calls,[])

    def test_connection_mismatch_cannot_fall_back_to_reader_server(self):
        route=self.setup_route();route.objects['input-table']['connection']='other-server'
        with self.assertRaisesRegex(ValueError,'endpoint differs'):
            route.compile(proposal(),'SOURCE','retained',self.cell,{'state':'EXACT'})
        self.assertEqual(self.calls,[])

    def test_context_and_cell_are_validated_before_compile(self):
        route=self.setup_route()
        with self.assertRaisesRegex(ValueError,'context differs'):
            route.compile(proposal(),'SOURCE','other-context',self.cell,{'state':'EXACT'})
        changed=copy.deepcopy(self.cell);changed['id']='forged'
        with self.assertRaisesRegex(ValueError,'identity differs'):
            route.compile(proposal(),'SOURCE','retained',changed,{'state':'EXACT'})
        self.assertEqual(self.calls,[])

    def test_exact_location_resolution_reuses_container_declaration_not_names(self):
        calls=[];parent='fabric://workspace/container'
        def endpoint(request):
            calls.append(request);return {'id':'container','properties':{'sqlEndpointProperties':{'id':'endpoint','connectionString':'server'}}}
        process=SimpleNamespace(config={'fabric':{'workspace_id':'workspace','sql_reader':{'server':'server'}}},read_endpoint=endpoint)
        context={'assets':[{'id':parent+'/table/a','parent_id':parent,'kind':'LakehouseTable','availability':'CURRENT','name':'a','metadata':{'location':'exact:a'}},
            {'id':parent+'/table/b','parent_id':parent,'kind':'LakehouseTable','availability':'CURRENT','name':'b','metadata':{'location':'exact:b'}},
            {'id':'fabric://workspace/endpoint','kind':'SQLEndpoint','availability':'CURRENT','name':'served-db'}]}
        objects,missing=resolve_objects(process,context,{'exact:a':{'amount':'long'},'exact:b':{'amount':'long'},'name-only:a':{'amount':'long'}})
        self.assertEqual(set(objects),{'exact:a','exact:b'});self.assertEqual(len(calls),1)
        self.assertEqual(objects['exact:a']['database'],'served-db');self.assertEqual(len(missing),1)
        context['assets'].append(copy.deepcopy(context['assets'][0]))
        objects,missing=resolve_objects(process,context,{'exact:a':{'amount':'long'}})
        self.assertFalse(objects);self.assertIn('ambiguous',missing[0]['reason'])

if __name__=='__main__':unittest.main()
