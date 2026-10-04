import copy,unittest
from investigator.source_delivery import classify,instant,declaration,validate,render_account
from investigator.process_debugging import vertical
from investigator import process_outcomes
from test_system_of_record import SourceAdapter


def audit():
    from investigator.adapters.load_audit import classify
    return classify([audit_row()],'producer')


def audit_row():
    return {'run_id':'load','pipeline_name':'producer','status':'Succeeded','start_time_utc':'2026-10-04T02:00:00Z',
            'end_time_utc':'2026-10-04T02:01:00Z','rows_read':'2','rows_written':'2',
            'accounting_state':'OBSERVED_COPY_OUTPUT','high_watermark':None}


def rows(modified='2026-10-04 01:59:59.9999999'):
    return [{'key':'1','version':'9','modified':modified},{'key':'2','version':'10','modified':modified}]


def typed(data):return [{k:{'type':'STRING','value':v} for k,v in r.items()} for r in data]


class DeliveryAdapter(SourceAdapter):
    def capabilities(self):return set(super().capabilities())|{'source_delivery'}
    def source_delivery(self,boundary,scope):
        s=rows(self.modified);d=s[:1];job=audit();facts=classify(job,s,d)
        a={'id':'audit','tool':'bounded_fabric_sql','values':typed([audit_row()]),'request_hash':'sealed',
            'completeness':'COMPLETE_RESPONSE','surface_attestation':{'consistency':'MATCHED'},
            'metadata':{'load_accounting':job,'declared_audit':{'producer_asset_id':'producer'}}}
        def read(identity,data):return {'id':identity,'tool':'bounded_sql','completeness':'COMPLETE_RESPONSE',
            'request_hash':'sealed','values':typed(data),'surface_attestation':{'consistency':'MATCHED','missing_required_fields':[]},
            'surface_report_binding':'VALUE_QUERY'}
        marker={'id':'delivery','tool':'process','check_kind':'SOURCE_DELIVERY','audit_result':job,'audit_evidence_id':'audit',
            'limitations':['Independent serving surfaces can update at different times.'],
            'row_evidence':{'source':['source-pages'],'destination':['destination-pages']},'delivery_result':facts}
        return {**facts,'evidence':marker,'observations':[a,read('source-pages',s),read('destination-pages',d),marker]}


class DeliveryTests(unittest.TestCase):
    def test_last_modified_is_declared_not_guessed(self):
        value={'source_asset_id':'s','key_column_id':'k','version_column_id':'v','modified_column_id':'m','time_semantics':'UTC_LAST_MODIFIED'}
        self.assertEqual(declaration(value),value)
        for v in (dict(value,time_semantics='probably UTC'),dict(value,column='name'),dict(value,modified_column_id='')):
            with self.assertRaises(ValueError):declaration(v)

    def test_timestamp_keeps_seventh_digit_no_invented_tolerance(self):
        self.assertGreater(instant('2026-10-04 02:00:00.0000002'),instant('2026-10-04T02:00:00.0000001Z'))
        with self.assertRaises(ValueError):instant('10/04/2026 02:00:00')

    def test_missing_row_before_load_is_gap_after_load_is_latency(self):
        self.assertEqual(classify(audit(),rows(),rows()[:1])['status'],'GAP')
        self.assertEqual(classify(audit(),rows('2026-10-04T02:01:00.0000001Z'),rows()[:1])['status'],'LATENT')
        self.assertEqual(classify(audit(),rows('2026-10-04T02:00:30Z'),rows()[:1])['status'],'UNAVAILABLE')

    def test_own_accounting_not_a_recount_and_version_change_is_visible(self):
        s=rows();d=copy.deepcopy(s);d[0]['version']='8'
        result=classify(audit(),s,d)
        self.assertEqual(result['different_version_rows'],1)
        self.assertEqual(result['missing_rows'],0)
        self.assertEqual(result['accounting'],audit()['accounting'])
        self.assertIn('2 rows read and 2 rows written',render_account({'delivery_result':result},True))

    def test_unrelated_new_change_does_not_relabel_an_old_gap_and_mixed_causes_refuse(self):
        s=rows();s[0]['modified']='2026-10-04T02:02:00Z'
        self.assertEqual(classify(audit(),s,s[:1])['status'],'GAP')
        self.assertEqual(classify(audit(),s,[])['status'],'UNAVAILABLE')

    def test_failed_missing_duplicate_or_same_rows_do_not_establish_outcome(self):
        for a,s,d in (({'status':'UNAVAILABLE','reason':'Failed run'},rows(),rows()[:1]),
                      (audit(),rows()+rows(),rows()[:1]),(audit(),rows(),rows()),
                      (audit(),[{'key':None,'version':'9','modified':'bad'}],[])):
            self.assertEqual(classify(a,s,d)['status'],'UNAVAILABLE')

    def test_engine_source_outcomes_recompute_original_evidence(self):
        for modified,outcome in (('2026-10-04T01:59:59Z','INGESTION_GAP'),('2026-10-04T02:02:00Z','LOAD_LATENCY')):
            a=DeliveryAdapter(['report','delivery','application'],dict(report=12,delivery=12,application=13))
            a.modified=modified
            result=vertical(a,'m',{})
            self.assertEqual(result['classification'],outcome)
            observations={o['id']:o for o in result['_observations']}
            process_outcomes.validate(result,observations)
            for change in ('partial','wrong_counts','changed_rows'):
                obs=copy.deepcopy(observations)
                if change=='partial':obs['source-pages']['completeness']='PARTIAL'
                if change=='wrong_counts':obs['audit']['metadata']['load_accounting']['accounting']['rows_read']=999
                if change=='changed_rows':obs['source-pages']['values'][0]['version']['value']='invalid'
                with self.assertRaises(ValueError):process_outcomes.validate(result,obs)

    def test_declared_unreachable_stops_before_source_never_source_consistency(self):
        class Unreachable(SourceAdapter):
            def resolve_path(self,m):
                p=super().resolve_path(m);p['system_of_record']['reachable']=False;return p
        a=Unreachable(['report','delivery','application'],dict(report=12,delivery=12,application=13))
        r=vertical(a,'m',{})
        self.assertEqual(r['classification'],'CONSISTENT_TO_BOUNDARY')
        self.assertEqual(a.evaluated,['report','delivery'])
        self.assertEqual(r['support']['process']['visibility_boundary']['deepest_layer'],'delivery')
        self.assertEqual(r['support']['process']['visibility_boundary']['stopped_by'],'NO_ACCESS')
        self.assertTrue(any('configured unreachable' in s for s in r['limits']))

    def test_no_accounting_is_not_current(self):
        from investigator.adapters.load_audit import classify as classify_audit
        self.assertEqual(classify_audit([{'run_id':'bad'}],'producer')['status'],'UNAVAILABLE')

    def test_implemented_delivery_blocked_by_evidence_is_not_called_unimplemented(self):
        a=DeliveryAdapter(['report','delivery','application'],dict(report=12,delivery=12,application=13))
        a.source_delivery=lambda boundary,scope:{'status':'UNAVAILABLE','reason':'No valid completed audit row covers the pipeline.'}
        result=vertical(a,'m',{})
        p=result['support']['process']
        self.assertEqual(p['visibility_boundary']['stopped_by'],'CAPABILITY_UNAVAILABLE')
        self.assertEqual(p['missing_capability'],'Evidence unavailable: No valid completed audit row covers the pipeline.')

    def test_adapter_compiles_paginated_roles_and_audit_failure_prevents_membership_reads(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from investigator.adapters.source_delivery import read
        from investigator.query_sql import compile_query
        from sqlglot import parse_one,exp
        columns=[{'name':'event_key','data_type':'int'},{'name':'revision_token','data_type':'timestamp'},
                 {'name':'changed_at','data_type':'datetime2'}]
        source={'id':'source','metadata':{'schema_name':'business','name':'entries','type_desc':'USER_TABLE','columns':columns}}
        assets=[{'id':str(i),'kind':'SqlColumn','parent_id':'source','availability':'CURRENT','metadata':c}
                for i,c in enumerate(columns)]
        assets.append({'id':'fabric://ws/endpoint','kind':'SQLEndpoint','name':'destination'})
        proof={'source':source,'server':'application.server','database':'application','mapping':{'translator':{'mappings':[
            {'source':{'name':c['name']},'destination':{'name':c['name']}} for c in columns]}}}
        layer={'id':'source','copy_mapping_proof':proof}
        boundary={'lower':layer,'upper':{'binding':{'asset':{'id':'dest','parent_id':'fabric://ws/lake','name':'dbo.arrivals'}}}}
        config={'source_delivery':{'source_asset_id':'source','key_column_id':'0','version_column_id':'1','modified_column_id':'2','time_semantics':'UTC_LAST_MODIFIED'},
            'sql':{'auth':{'account':'source-reader'}},'fabric':{'sql_reader':{'server':'destination.server','account':'reader'}}}
        job={**audit(),'evidence':{'id':'audit'}}
        adapter=SimpleNamespace(config=config,store=None,model={'id':'model','revision':1,'context_id':'context'},
            job_history=lambda b:job,read_endpoint=lambda r:{'properties':{'sqlEndpointProperties':{'id':'endpoint','connectionString':'destination.server'}}},
            execute_lower=None,meter_read=None)
        calls=[]
        def execute(store,plan,config,tool,transport,catalog):
            compiled=compile_query(plan['query'],catalog,max_rows=plan['max_rows'])
            tree=parse_one(plan['query'],read='tsql');where=tree.args.get('where')
            after=int(where.this.expression.this) if where else 0
            n=360 if tool=='bounded_sql' else 359
            page=[{'key':str(k),'version':str(k),'modified':'2026-10-04 01:00:00.0000000'} for k in range(after+1,min(after+249,n)+1)]
            calls.append((tool,compiled))
            report=({'identity':'source-reader','engine':'Microsoft SQL Azure','object':'application'} if tool=='bounded_sql' else
                    {'identity':'reader','engine':'Microsoft Azure SQL Data Warehouse','object':'destination'})
            return {'id':'page-'+str(len(calls)),'status':'COMPLETED','request_hash':'sealed',
                'result':{'rows':typed(page),'surface_report':report,'surface_report_binding':'VALUE_QUERY','completeness':'COMPLETE_RESPONSE'}}
        with patch('investigator.context_search.latest',return_value={'assets':assets}),patch('investigator.adapters.source_delivery.run_query',side_effect=execute):
            result=read(adapter,boundary,{})
        self.assertEqual(result['status'],'GAP');self.assertEqual(result['missing_rows'],1)
        self.assertEqual(len(calls),4)
        self.assertEqual([len(c['parameters']) for _,c in calls],[0,1,0,1])
        adapter.job_history=lambda b:{'status':'UNAVAILABLE','reason':'Malformed audit timestamps'}
        with patch('investigator.context_search.latest',return_value={'assets':assets}),patch('investigator.adapters.source_delivery.run_query',side_effect=AssertionError('no membership reads')):
            self.assertEqual(read(adapter,boundary,{})['reason'],'Malformed audit timestamps')


if __name__=='__main__':unittest.main()
