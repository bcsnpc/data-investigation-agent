import json
from pathlib import Path
import unittest

import probe_execution_surfaces as probes
import read_onelake_header as reader
from investigator.process_debugging import Probe

SURFACE={'engine':'POWER_BI_DAX','connection':'workspace','object':'model'}
REQUEST={'workspace':'w','lakehouse':'l','table':'t'}
SECRET_VALUE=987654321


class Adapter:
    def __init__(self,probe=None,error=None,ingestion=None):
        self.probe,self.error,self.result=probe,error,ingestion
    def evaluate(self,layer,measure_id,scope):
        if self.error:raise self.error
        return self.probe
    def ingestion(self,path,scope):
        if self.error:raise self.error
        return self.result


PATH={'layers':[{'id':'top','kind':'presentation'}]}


class SemanticProbeTests(unittest.TestCase):
    def test_receipt_hashes_value_and_never_carries_it(self):
        probe=Probe('OBSERVED','top',evidence={'id':'e','request_hash':'h','completeness':'COMPLETE_RESPONSE',
                    'values':[{'baseline':SECRET_VALUE}]},value={'baseline':SECRET_VALUE},execution_surface=SURFACE)
        result=probes.probe_semantic(Adapter(probe),PATH,'m')
        self.assertEqual(result['status'],'REACHABLE')
        self.assertEqual(result['execution_surface'],SURFACE)
        self.assertEqual(result['values_sha256'],probes.values_hash({'baseline':SECRET_VALUE}))
        self.assertNotIn(str(SECRET_VALUE),json.dumps(result))

    def test_failure_is_explicit_unavailability_not_a_substitute(self):
        result=probes.probe_semantic(Adapter(error=RuntimeError('boom')),PATH,'m')
        self.assertEqual((result['status'],result['stage'],result['error_type']),('UNAVAILABLE','evaluate','RuntimeError'))
        self.assertNotIn('values_sha256',result)
        self.assertNotIn('boom',json.dumps(result))

    def test_unavailable_probe_status_is_not_upgraded(self):
        probe=Probe('UNAVAILABLE','top',reason='The presentation reader could not establish a baseline.',
                    execution_surface=SURFACE)
        result=probes.probe_semantic(Adapter(probe),PATH,'m')
        self.assertEqual(result['status'],'UNAVAILABLE');self.assertIsNone(result['values_sha256'])

    def test_reachable_receipt_requires_a_complete_surface(self):
        probe=Probe('OBSERVED','top',evidence={'id':'e'},value=1,execution_surface={'engine':'X','connection':'','object':'o'})
        with self.assertRaisesRegex(ValueError,'execution surface'):
            probes.probe_semantic(Adapter(probe),PATH,'m')


class SourceQueryTests(unittest.TestCase):
    def test_choice_is_by_asset_identity_not_name(self):
        objects={'id-b':{'metadata':{'schema_name':'s','name':'aaa'}},
                 'id-a':{'metadata':{'schema_name':'s','name':'zzz'}}}
        identity,query=probes.source_query(objects)
        self.assertEqual(identity,'id-a');self.assertEqual(query,'SELECT COUNT_BIG(*) AS probe FROM [s].[zzz]')

    def test_no_objects_is_not_applicable(self):
        self.assertEqual(probes.source_query({}),(None,None))


class CommitProbeTests(unittest.TestCase):
    def test_missing_binding_is_not_applicable(self):
        result=probes.probe_commit(Adapter(ingestion={'status':'UNAVAILABLE','reason':'No declared data asset was resolved.'}),PATH,{})
        self.assertEqual(result['status'],'NOT_APPLICABLE')

    def test_unavailable_commit_keeps_error_type(self):
        result=probes.probe_commit(Adapter(ingestion={'status':'UNAVAILABLE','evidence':{'delta_commit':
            {'status':'UNAVAILABLE','error_type':'HTTPError'}}}),PATH,{'request':REQUEST})
        self.assertEqual((result['status'],result['error_type']),('UNAVAILABLE','HTTPError'))


class TableDataProbeTests(unittest.TestCase):
    def test_reads_listing_then_one_header_through_the_isolated_reader(self):
        calls=[]
        def read(request):
            calls.append(request)
            if request['mode']=='listing':return {'status':'AVAILABLE','http_status':200,'data_files':['l/Tables/t/a.parquet']}
            return {'status':'AVAILABLE','http_status':206,'bytes_read':4,'parquet_magic_matches':True}
        result=probes.probe_table_data(REQUEST,read)
        self.assertEqual(result['status'],'REACHABLE');self.assertEqual(result['data_files_listed'],1)
        self.assertEqual([c['mode'] for c in calls],['listing','header'])
        self.assertEqual(calls[1]['file'],'l/Tables/t/a.parquet')
        self.assertIn('no row was decoded',result['limitation'])

    def test_reader_failure_is_preserved_with_its_status(self):
        result=probes.probe_table_data(REQUEST,lambda r:{'status':'UNAVAILABLE','error_type':'HTTPError','http_status':403})
        self.assertEqual((result['status'],result['stage'],result['http_status']),('UNAVAILABLE','listing',403))

    def test_harness_exception_is_unavailable_not_raised(self):
        def read(request):raise ModuleNotFoundError('fabric_cli')
        result=probes.probe_table_data(REQUEST,read)
        self.assertEqual((result['status'],result['error_type']),('UNAVAILABLE','ModuleNotFoundError'))

    def test_non_parquet_header_is_not_reachable(self):
        responses=iter([{'status':'AVAILABLE','http_status':200,'data_files':['l/Tables/t/a.parquet']},
                        {'status':'AVAILABLE','http_status':206,'bytes_read':4,'parquet_magic_matches':False}])
        result=probes.probe_table_data(REQUEST,lambda r:next(responses))
        self.assertEqual(result['status'],'UNAVAILABLE');self.assertFalse(result['parquet_magic_matches'])

    def test_unbound_table_is_not_applicable(self):
        result=probes.probe_table_data(None,lambda r:self.fail('no call expected'))
        self.assertEqual(result['status'],'NOT_APPLICABLE')


class HeaderReaderTests(unittest.TestCase):
    WS='00000000-0000-0000-0000-000000000001';LH='00000000-0000-0000-0000-000000000002'

    def request(self,**extra):return dict(workspace=self.WS,lakehouse=self.LH,table='t',**extra)

    def test_header_read_is_ranged_and_bounded(self):
        calls=[]
        def get(url,headers,limit):calls.append((url,headers,limit));return 206,b'PAR1'
        result=reader.inspect(self.request(mode='header',file=self.LH+'/Tables/t/a.parquet'),get)
        self.assertEqual(calls[0][1:],({'Range':'bytes=0-3'},reader.HEADER_BYTES))
        self.assertEqual(result,{'status':'AVAILABLE','http_status':206,'bytes_read':4,'parquet_magic_matches':True})

    def test_header_refuses_a_file_outside_the_bound_table(self):
        for name in (self.LH+'/Tables/other/a.parquet',self.LH+'/Tables/t/../x/a.parquet',self.LH+'/Tables/t/_delta_log/0.json'):
            with self.assertRaisesRegex(ValueError,'data file'):
                reader.inspect(self.request(mode='header',file=name),lambda *a:self.fail('no call expected'))

    def test_listing_keeps_only_bound_parquet_files(self):
        body=json.dumps({'paths':[{'name':self.LH+'/Tables/t/b.parquet'},{'name':self.LH+'/Tables/t/_delta_log'},
                                  {'name':self.LH+'/Tables/u/a.parquet'}]}).encode()
        result=reader.inspect(self.request(mode='listing'),lambda *a:(200,body))
        self.assertEqual(result['data_files'],[self.LH+'/Tables/t/b.parquet'])

    def test_bounded_get_refuses_more_than_the_limit(self):
        class Response:
            status=206
            def __enter__(self):return self
            def __exit__(self,*a):return False
            def read(self,n):return b'PAR1PAR1'[:n]
        class Opener:
            def open(self,request,timeout):return Response()
        from unittest.mock import patch
        with patch('urllib.request.build_opener',lambda *a:Opener()):
            with self.assertRaisesRegex(ValueError,'Byte limit'):
                reader.bounded_get('token')('https://x',{},reader.HEADER_BYTES)


class ScopeTests(unittest.TestCase):
    def test_fabric_sql_endpoint_is_not_probed(self):
        for module in (probes,reader):
            self.assertNotIn('database.windows.net',Path(module.__file__).read_text(encoding='utf-8'))
        self.assertEqual(probes.PROBES,('semantic_dax','source_sql','onelake_commit_metadata','onelake_table_data'))


if __name__=='__main__':
    unittest.main()
