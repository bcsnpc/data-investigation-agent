import copy
import hashlib
from io import BytesIO
from io import StringIO
from contextlib import redirect_stdout
import json
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch
import unittest

import test_adaptive_investigation as fixture
from investigator import source_scope, source_diagnostics, comparisons
from investigator.adaptive_candidates import catalog
from investigator.admin_api import create_app
from investigator.onboarding import Conflict
from test_native_diagnostics import database


class TypedSourceTests(unittest.TestCase):
    def compile(self, values, sql_type='int', operator='in', **extra):
        return source_scope.compile_filter({'column_id':'col','operator':operator,'values':values},
                                           {'data_type':sql_type,**extra},'[column]',0)

    def test_half_open_dates_are_parameters_with_explicit_iso_conversion(self):
        query, params=self.compile(['2026-01-01','2026-02-01'],'datetime2','range')
        self.assertEqual(query,'([column]>=CONVERT(datetime2,@p0,126) AND [column]<CONVERT(datetime2,@p1,126))')
        self.assertEqual([p['value'] for p in params],['2026-01-01T00:00:00','2026-02-01T00:00:00'])
        self.assertNotIn('2026',query)

    def test_nulls_preserve_membership_and_never_become_zero(self):
        query,params=self.compile([None,0])
        self.assertIn('[column] IS NULL',query);self.assertIn('CAST(@p0 AS int)',query)
        self.assertEqual(params,[{'name':'@p0','value':'0'}])
        self.assertEqual(self.compile([None])[0],'([column] IS NULL)')

    def test_sql_integer_bounds_and_json_types(self):
        for sql_type, values in [('tinyint',[-1,256]),('smallint',[-32769,32768]),('int',[-2147483649,2147483648]),
                                ('bigint',[2**53,True,1.0,'1'])]:
            for value in values:
                with self.subTest(type=sql_type,value=value),self.assertRaises(ValueError):self.compile([value],sql_type)
        self.assertEqual(self.compile([255],'tinyint')[1][0]['value'],'255')

    def test_exact_decimal_parameter_and_rounding_guard(self):
        query,params=self.compile(['12.34'],'decimal',precision=10,scale=2)
        self.assertIn('decimal(10,2)',query);self.assertEqual(params[0]['value'],'12.34')
        for value in ['1.001','100000000','1e2',1.2,'NaN']:
            with self.subTest(value=value),self.assertRaises(ValueError):self.compile([value],'decimal',precision=10,scale=2)

    def test_large_scale_validation_is_independent_of_decimal_context(self):
        query,params=self.compile(['999999999.9999'],'decimal',precision=38,scale=20)
        self.assertIn('decimal(38,20)',query)
        self.assertEqual(params[0]['value'],'999999999.9999')

    def test_money_range_and_missing_precision(self):
        with self.assertRaises(ValueError):self.compile(['214748.3648'],'smallmoney')
        with self.assertRaises(ValueError):self.compile(['1.00'],'decimal')
        self.assertEqual(self.compile(['-214748.3648'],'smallmoney')[1][0]['value'],'-214748.3648')

    def test_booleans_are_not_integer_inputs(self):
        query,params=self.compile([True,False],'bit')
        self.assertIn('AS bit',query);self.assertEqual([p['value'] for p in params],['1','0'])
        with self.assertRaises(ValueError):self.compile([1],'bit')
        with self.assertRaises(ValueError):self.compile([False,True],'bit','range')

    def test_temporal_inputs_cannot_lose_timezone_time_or_precision(self):
        for value in ['2026-01-01T00:00:00Z','2026-01-01T00:00:00-06:00','2026-01-01T00:00:00.1',
                      '01/02/2026','2026-02-30','1899-01-01']:
            with self.subTest(value=value),self.assertRaises(ValueError):self.compile([value],'datetime2')
        with self.assertRaises(ValueError):self.compile(['2026-01-01T00:00:01'],'date')
        self.assertIn('CONVERT(date',self.compile(['2026-01-01'],'date')[0])

    def test_invalid_ranges_and_semantic_duplicates(self):
        for values in [[None,2],[2,2],[3,2],[1],[1,2,3]]:
            with self.subTest(values=values),self.assertRaises(ValueError):self.compile(values,operator='range')
        with self.assertRaises(ValueError):self.compile(['1','1.00'],'decimal',precision=10,scale=2)
        with self.assertRaises(ValueError):self.compile(['2026-01-01','2026-01-01T00:00:00'],'datetime2')

    def test_strings_are_bounded_parameters_and_range_is_rejected(self):
        attack="USD'); DROP TABLE app.orders; --"
        query,params=self.compile([attack],'nvarchar')
        self.assertNotIn('DROP',query);self.assertEqual(params[0]['value'],attack)
        with self.assertRaises(ValueError):self.compile(['\U0001f600'*101],'nvarchar')
        with self.assertRaises(ValueError):self.compile(['a','b'],'nvarchar','range')

    def test_unsupported_and_injected_sql_type_rejected(self):
        for kind in ['float','real','datetimeoffset','datetime','uniqueidentifier','int);DROP TABLE x;--']:
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.compile([1],kind)

    def test_catalog_does_not_advertise_unknown_decimal_or_computed_filter(self):
        self.assertEqual(source_scope.describe({'data_type':'decimal'})['state'],'UNSUPPORTED')
        self.assertEqual(source_scope.describe({'data_type':'int','computed_definition':'1+1'})['state'],'UNSUPPORTED')


class ReviewedSourceTests(unittest.TestCase):
    def setUp(self):
        h=fixture.AdaptiveTests();h.setUp();self.addCleanup(h.doCleanups);self.helper=h
        for name in ('store','config','model','runtime','agent','envelope','source','native','planner'):
            setattr(self,name,getattr(h,name))
        self.plan=copy.deepcopy(self.envelope['source_tests'][0]['plan'])
        self.envelope.update(source_tests=[],source_selection='reviewed_mappings')
        self.body={'revision':3,'context_id':'ctx','measure_id':'Unseen ratio','source_object_id':self.plan['object_id'],
                   'source_operation':'count_rows','source_column_id':None,'grain':'entity','unit':'count',
                   'date_basis':'reviewed diagnostic scope only','blank_policy':'preserve','confirmed':True,
                   'filter_bindings':[{'native_column_id':'c','source_column_id':self.plan['object_id']+'/currency'}]}

    def register(self, **changes):
        return comparisons.register(self.store,'model',dict(self.body,**changes),'reviewer')['id']

    def sources(self):
        candidates,gaps=catalog(self.store,self.config,self.envelope)
        return [c for c in candidates if c['tool']=='source'],gaps

    def add_date(self):
        column=self.plan['object_id']+'/amount'
        with database(self.store.inventory) as db:
            raw=db.execute('SELECT metadata FROM assets WHERE id=?',(column,)).fetchone()[0]
            meta=dict(json.loads(raw),data_type='datetime2',scale=7)
            raw=json.dumps(meta,sort_keys=True,ensure_ascii=False)
            db.execute('UPDATE assets SET metadata=?,content_hash=? WHERE id=?',(raw,hashlib.sha256(raw.encode()).hexdigest(),column))
        self.model['context']['reports'][0]['model_assets'].append(
            {'id':'date','kind':'SemanticColumn','name':'business_date','parent_id':'t','metadata':{'dataType':'dateTime'}})
        self.body['filter_bindings'].append({'native_column_id':'date','source_column_id':column})
        self.envelope['filters'].append({'column_id':'date','operator':'range','values':['2026-01-01','2026-02-01']})
        return column

    def test_unique_review_generates_source_plan_without_manual_tests(self):
        identity=self.register();sources,gaps=self.sources()
        self.assertEqual(len(sources),1);plan=sources[0]['plan']
        self.assertEqual(plan['comparison_mapping_id'],identity)
        self.assertEqual(plan['filters'],self.plan['filters'])
        self.assertEqual(sources[0]['reviewed_mapping']['authority'],'TEAM_CONFIRMED_INTENT')
        self.assertFalse(sources[0]['reviewed_mapping']['equivalence_verified'])
        self.assertEqual(self.envelope['source_tests'],[])

    def test_missing_mapping_preserves_native_candidates(self):
        sources,gaps=self.sources();self.assertEqual(sources,[])
        self.assertIn('CURRENT_SOURCE_MAPPING_MISSING',[g['reason'] for g in gaps])
        candidates,_=catalog(self.store,self.config,self.envelope)
        self.assertTrue(any(c['tool']=='native' for c in candidates))

    def test_ambiguity_never_chooses_first_or_latest(self):
        first=self.register();self.register(unit='another reviewed meaning')
        sources,gaps=self.sources();self.assertEqual(sources,[])
        self.assertIn('SOURCE_MAPPING_AMBIGUOUS',[g['reason'] for g in gaps])
        comparisons.revoke(self.store,'model',first,'superseded','reviewer')
        self.assertEqual(len(self.sources()[0]),1)

    def test_missing_date_binding_cannot_broaden_scope(self):
        self.register();self.add_date()
        sources,gaps=self.sources();self.assertEqual(sources,[])
        self.assertIn('SOURCE_MAPPING_FILTER_COVERAGE_GAP',[g['reason'] for g in gaps])

    def test_date_scope_is_translated_completely_and_keeps_parameter_order(self):
        column=self.add_date();self.register();sources,_=self.sources()
        filters=sources[0]['plan']['filters']
        self.assertEqual(filters[1],dict(self.envelope['filters'][1],column_id=column))
        compiled=source_diagnostics.build(self.store,sources[0]['plan'],self.config)
        self.assertEqual([p['name'] for p in compiled['parameters']],['@p0','@p1','@p2'])
        self.assertIn('CONVERT(datetime2,@p1,126)',compiled['query'])

    def test_type_mismatch_is_not_implicit_conversion(self):
        self.model['context']['reports'][0]['model_assets'][1]['metadata']['dataType']='int64'
        self.envelope['filters']=[{'column_id':'c','operator':'in','values':[1]}]
        self.register();sources,gaps=self.sources();self.assertEqual(sources,[])
        self.assertIn('SOURCE_MAPPING_NOT_EXECUTABLE',[g['reason'] for g in gaps])

    def test_unknown_object_is_gap_not_query(self):
        self.register(source_object_id='unknown');sources,gaps=self.sources()
        self.assertEqual(sources,[]);self.source.assert_not_called()
        self.assertIn('SOURCE_MAPPING_NOT_EXECUTABLE',[g['reason'] for g in gaps])

    def test_stale_review_not_reused_for_new_context(self):
        self.register();self.model['revision']=4;self.envelope['revision']=4
        sources,gaps=self.sources();self.assertEqual(sources,[])
        self.assertIn('CURRENT_SOURCE_MAPPING_MISSING',[g['reason'] for g in gaps])

    def test_manual_and_automatic_scope_cannot_be_mixed(self):
        self.envelope['source_tests']=[{'measure_id':'Unseen ratio','plan':self.plan}]
        with self.assertRaises(ValueError):self.sources()

    def test_revocation_before_dispatch_holds_session(self):
        identity=self.register();run=self.agent.create(self.envelope,'revoke')
        comparisons.revoke(self.store,'model',identity,'withdrawn','reviewer')
        result=self.agent.run(run['id'])
        self.assertEqual(result['stop_reason'],'ADMISSION_CHANGED')
        self.source.assert_not_called();self.planner.assert_not_called()

    def test_tamper_before_dispatch_holds_session(self):
        self.register();run=self.agent.create(self.envelope,'tamper')
        with self.store.connect() as db:db.execute("UPDATE comparison_mappings SET hash='bad'")
        self.assertEqual(self.agent.run(run['id'])['stop_reason'],'ADMISSION_CHANGED')
        self.planner.assert_not_called()

    def test_revocation_during_source_read_holds_receipt(self):
        identity=self.register();sources,_=self.sources()
        def execute(request):
            comparisons.revoke(self.store,'model',identity,'withdrawn','reviewer')
            return {'value':'5','row_count':'5','nonblank_count':'5'}
        result=source_diagnostics.run(self.store,sources[0]['plan'],self.config,execute)
        self.assertEqual(result['status'],'HELD')

    def test_cross_model_access_and_plan_rebinding_rejected(self):
        identity=self.register();sources,_=self.sources();plan=sources[0]['plan']
        with self.assertRaises(KeyError):comparisons.mapping(self.store,'other',identity)
        with self.assertRaises(Conflict):source_diagnostics.build(self.store,dict(plan,operation='sum',column_id=self.plan['object_id']+'/amount'),self.config)

    def test_adaptive_planner_can_select_discovered_date_test_and_replay(self):
        self.add_date();identity=self.register()
        def planner(payload):
            if payload['observations']:return fixture.decision(),{}
            selected=next(c for c in payload['candidates'] if c['tool']=='source')
            self.assertEqual(selected['source_binding']['id'],identity)
            return fixture.decision(selected['id']),{}
        self.planner.side_effect=planner
        result=self.agent.run(self.agent.create(self.envelope,'date-read')['id'])
        self.assertEqual(result['status'],'COMPLETED');self.source.assert_called_once();self.native.assert_not_called()
        self.assertEqual(result['observations'][0]['reviewed_mapping']['id'],identity)
        self.assertFalse(result['outcome']['cause_verified'])
        self.agent.run(result['id']);self.source.assert_called_once()

    def test_new_mapping_invalidates_old_candidate_catalog(self):
        self.register();run=self.agent.create(self.envelope,'new-review')
        self.register(unit='new')
        self.assertEqual(self.agent.run(run['id'])['stop_reason'],'ADMISSION_CHANGED')

    def test_alignment_does_not_equate_boolean_integer_or_reorder_range(self):
        bindings=[{'native_column_id':'n','source_column_id':'s'}]
        def aligned(a,b,operator='in'):
            return comparisons.aligned([{'column_id':'n','operator':operator,'values':a}],
                                       [{'column_id':'s','operator':operator,'values':b}],bindings)
        self.assertFalse(aligned([True],[1]));self.assertFalse(aligned([1,2],[2,1],'range'))
        self.assertTrue(aligned([None,2],[2,None]));self.assertTrue(aligned(['2026-01-01','2026-02-01'],['2026-01-01','2026-02-01'],'range'))

    def test_admin_preview_has_no_cloud_calls_and_requires_admin(self):
        self.register();controller=MagicMock();controller.runtime.config=self.config
        app=create_app(self.store,'a'*32,'r'*32,investigations=controller)
        for token,status in [('r'*32,'403 Forbidden'),('a'*32,'200 OK')]:
            statuses=[];body=json.dumps(self.envelope).encode()
            raw=b''.join(app({'PATH_INFO':'/api/v2/admin/models/model/diagnostic-preview','REQUEST_METHOD':'POST',
                             'HTTP_AUTHORIZATION':'Bearer '+token,'CONTENT_TYPE':'application/json',
                             'CONTENT_LENGTH':str(len(body)),'wsgi.input':BytesIO(body)},lambda s,h:statuses.append(s)))
            self.assertEqual(statuses,[status])
            if status=='200 OK':self.assertEqual(json.loads(raw)['cloud_calls'],0)
        self.source.assert_not_called();self.native.assert_not_called();self.planner.assert_not_called()

    def test_completed_source_receipt_retained_but_mapping_no_longer_current(self):
        identity=self.register();sources,_=self.sources()
        receipt=source_diagnostics.run(self.store,sources[0]['plan'],self.config,self.source)
        self.assertTrue(source_diagnostics.evidence(self.store,'model',receipt['id'])['reviewed_mapping_current'])
        comparisons.revoke(self.store,'model',identity,'retired','reviewer')
        history=source_diagnostics.evidence(self.store,'model',receipt['id'])
        self.assertEqual(history['status'],'COMPLETED');self.assertFalse(history['reviewed_mapping_current'])

    def test_cli_preview_does_not_load_azure_key_or_create_runtime(self):
        import run_adaptive_investigation as cli
        self.register()
        with tempfile.TemporaryDirectory() as folder:
            envelope=Path(folder)/'envelope.json';envelope.write_text(json.dumps(self.envelope),encoding='utf-8')
            argv=['run','--config','unused','--database','unused','--environment','development','--envelope',str(envelope),'--preview']
            with patch('sys.argv',argv),patch.object(cli,'load_config',return_value=dict(self.config,storage={'database':'unused'})),patch.object(cli,'ModelStore',return_value=self.store),\
                 patch.object(cli,'Runtime') as runtime,patch.object(cli,'local_azure_key') as key,redirect_stdout(StringIO()) as output:
                self.assertEqual(cli.main(),0)
            runtime.assert_not_called();key.assert_not_called()
            self.assertEqual(json.loads(output.getvalue())['cloud_calls'],0)


if __name__=='__main__':unittest.main()
