import copy
from io import BytesIO
import json
import unittest
from unittest.mock import MagicMock

import test_keyed_readback as fixture
from test_adaptive_investigation import decision
from investigator import record_bindings as reviews, record_readback as records
from investigator.adaptive_candidates import catalog
from investigator.admin_api import create_app
from investigator.onboarding import Conflict


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        h=fixture.ReadbackTests();h.setUp();self.addCleanup(h.doCleanups);self.h=h
        for key in ('store','config','model','envelope','agent','planner','native','source','runtime'):
            setattr(self,key,getattr(h,key))
        self.body={k:h.nplan[k] for k in ('revision','context_id','key_column_ids','limit')}
        self.body.update(measure_id=self.envelope['measure_id'],native_object_id=h.nplan['object_id'],
                         source_object_id=h.splan['object_id'],column_bindings=h.mapping,filter_bindings=h.filters,
                         grain='One record per entity key',date_basis='No date restriction in this scope',confirmed=True)
        self.envelope.update(record_selection='reviewed_mappings',source_tests=[])

    def register(self,body=None):return reviews.register(self.store,'model',body or self.body,'reviewer',self.config)
    def candidates(self):return catalog(self.store,self.config,self.envelope)
    def selected(self):return [c for c in self.candidates()[0] if c['tool'].endswith('_records')]

    def test_review_records_authority_and_hash_without_query(self):
        r=self.register()
        self.assertEqual(reviews.read(self.store,'model',r['id']),r)
        self.assertEqual(r['authority'],'TEAM_CONFIRMED_INTENT');self.assertFalse(r['equivalence_verified'])
        self.assertEqual(len(reviews.listing(self.store,'model')),1)
        self.native.assert_not_called();self.source.assert_not_called()

    def test_draft_preview_validates_scope_without_confirmation_or_persistence(self):
        body=dict(self.body,confirmed=False)
        result=reviews.preview(self.store,'model',{'mapping':body,'filters':self.envelope['filters']},self.config)
        self.assertEqual(result['status'],'DRAFT_VALIDATED');self.assertFalse(result['review_saved'])
        self.assertEqual(result['authority'],'UNCONFIRMED_DRAFT');self.assertEqual(result['cloud_calls'],0)
        self.assertEqual(reviews.listing(self.store,'model'),[])
        self.assertFalse(body['confirmed']);self.assertEqual(len(result['projections']),2)
        self.native.assert_not_called();self.source.assert_not_called()
        with self.assertRaises(ValueError):self.register(body)

    def test_draft_invalid_scope_fails_instead_of_silently_broadening(self):
        with self.assertRaises(ValueError):
            reviews.preview(self.store,'model',{'mapping':dict(self.body,confirmed=False),'filters':[]},self.config)

    def test_reuse_across_ticket_values_with_no_manual_plans(self):
        r=self.register();first=self.selected()
        self.assertEqual(len(first),2)
        self.envelope['filters'][0]['values']=['EUR']
        second=self.selected()
        self.assertNotEqual(first[0]['id'],second[0]['id'])
        for c in second:
            self.assertEqual(c['plan']['filters'][0]['values'],['EUR'])
            self.assertEqual(c['record_mapping']['hash'],r['hash'])
        self.assertNotIn('record_tests',self.envelope)

    def test_missing_and_ambiguous_mappings_never_choose_arbitrarily(self):
        self.assertTrue(any(g['reason']=='CURRENT_RECORD_MAPPING_MISSING' for g in self.candidates()[1]))
        self.register();self.register()
        self.assertEqual(self.selected(),[])
        self.assertTrue(any(g['reason']=='RECORD_MAPPING_AMBIGUOUS' for g in self.candidates()[1]))

    def test_revoke_disambiguates_without_erasing_history(self):
        a=self.register();b=self.register();self.assertEqual(self.selected(),[])
        reviews.revoke(self.store,'model',b['id'],'Superseded','reviewer')
        self.assertEqual({c['record_mapping']['id'] for c in self.selected()},{a['id']})
        self.assertIsNotNone(reviews.read(self.store,'model',b['id'])['revocation'])

    def test_invalid_contracts_rejected_before_persistence(self):
        for change in [{'confirmed':False},{'limit':True},{'limit':251},{'revision':0},{'measure_id':'missing'},
                       {'native_object_id':'missing'},{'source_object_id':'missing'},{'key_column_ids':['amount','amount']},
                       {'key_column_ids':['missing']},{'filter_bindings':[]},{'grain':''}]:
            with self.subTest(change=change),self.assertRaises(ValueError):self.register(dict(self.body,**change))
        self.assertEqual(reviews.listing(self.store,'model'),[])

    def test_cross_table_and_type_mismatch_rejected(self):
        self.model['context']['reports'][0]['model_assets'][-1]['metadata']['dataType']='string'
        with self.assertRaises(ValueError):self.register()
        self.model['context']['reports'][0]['model_assets'][-1]['metadata']['dataType']='decimal'
        self.model['context']['reports'][0]['model_assets'][-1]['parent_id']='other'
        with self.assertRaises(ValueError):self.register()

    def test_overlapping_filter_projection_mapping_must_agree(self):
        body=copy.deepcopy(self.body);body['filter_bindings']=[{'native_column_id':'key','source_column_id':self.h.splan['object_id']+'/currency'}]
        with self.assertRaises(ValueError):self.register(body)

    def test_extra_scope_is_gap_not_dropped(self):
        self.register();self.envelope['filters'].append({'column_id':'key','values':['A']})
        self.assertEqual(self.selected(),[])
        self.assertTrue(any(g['reason']=='RECORD_MAPPING_SCOPE_OR_CATALOG_GAP' for g in self.candidates()[1]))

    def test_manual_discovery_mix_rejected(self):
        for change in [{'record_selection':'anything'},{'record_tests':[{}]},{'record_pairs':[{}]}]:
            with self.subTest(change=change),self.assertRaises(ValueError):catalog(self.store,self.config,dict(self.envelope,**change))

    def test_plan_cannot_change_reviewed_projection_or_limit(self):
        self.register();c=self.selected()[0]
        for change in [{'limit':2},{'column_ids':['key']},{'key_column_ids':['amount']}]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                records.build(self.store,dict(c['plan'],**change),self.config,c['tool'])

    def test_review_revocation_blocks_existing_direct_plan(self):
        r=self.register();c=self.selected()[0]
        reviews.revoke(self.store,'model',r['id'],'Withdrawn','reviewer')
        with self.assertRaises(Conflict):records.build(self.store,c['plan'],self.config,c['tool'])

    def test_revocation_holds_adaptive_session_before_planner(self):
        r=self.register();identity=self.agent.create(self.envelope,'revoked')['id']
        reviews.revoke(self.store,'model',r['id'],'Withdrawn','reviewer')
        result=self.agent.run(identity)
        self.assertEqual(result['status'],'HELD');self.assertEqual(result['stop_reason'],'ADMISSION_CHANGED')
        self.planner.assert_not_called();self.native.assert_not_called();self.source.assert_not_called()

    def test_new_ambiguity_holds_pinned_session(self):
        self.register();identity=self.agent.create(self.envelope,'ambiguous')['id'];self.register()
        self.assertEqual(self.agent.run(identity)['status'],'HELD');self.planner.assert_not_called()

    def test_context_revision_requires_new_review(self):
        self.register();self.model['revision']+=1;self.envelope['revision']+=1
        self.assertEqual(self.selected(),[])
        with self.assertRaises(Conflict):self.register()

    def test_tampered_review_rejected(self):
        r=self.register()
        with self.store.connect() as db:db.execute("UPDATE record_mappings SET body='{}' WHERE id=?",(r['id'],))
        with self.assertRaises(ValueError):reviews.read(self.store,'model',r['id'])
        with self.assertRaises(ValueError):self.candidates()

    def test_different_evidence_changes_planner_next_action_and_saved_pair(self):
        self.register();seen=[]
        for amount in ('10','11'):
            self.source.return_value=self.h.sql_rows([('A','10',1)])
            def planner(payload):
                count=len(payload['observations'])
                if count==0:return decision(self.h.helper.choose(payload)),{}
                if count==1:
                    self.native.return_value=self.h.native_rows([('A',amount,1)]);tool='native_records'
                elif count==2:tool='source_records'
                else:
                    pair=payload['record_comparisons'][0];seen.append(pair['status'])
                    self.assertIn('reviewed_mapping',pair)
                    return decision(question='Which intended state should apply?' if pair['difference_count'] else None),{}
                return decision(next(c['id'] for c in payload['candidates'] if c['tool']==tool)),{}
            self.planner.side_effect=planner
            # Restore scalar transport before the next independent ticket.
            from test_native_diagnostics import response
            self.native.return_value=response([{'[m0]':5}])
            result=self.agent.run(self.agent.create(self.envelope,'case-'+amount)['id'])
            self.assertEqual(result['status'],'COMPLETED' if amount=='10' else 'NEEDS_INPUT')
            self.assertEqual(result['cloud_calls'],3)
            calls=self.source.call_count;self.agent.run(result['id']);self.assertEqual(self.source.call_count,calls)
        self.assertEqual(seen,['OBSERVED_EQUAL','OBSERVED_DIFFERENCE'])

    def test_saved_receipt_retains_review_provenance(self):
        r=self.register();c=self.selected()[0]
        result=records.run(self.store,c['plan'],self.config,c['tool'],self.h.ntransport)
        saved=records.read(self.store,'model',result['id'])
        self.assertEqual(saved['request']['reviewed_mapping']['hash'],r['hash'])
        reviews.revoke(self.store,'model',r['id'],'Retired','reviewer')
        self.assertEqual(records.read(self.store,'model',result['id'])['request'],saved['request'])

    def test_revocation_during_read_holds_result_and_does_not_retry(self):
        r=self.register();c=self.selected()[0]
        def transport(request):
            reviews.revoke(self.store,'model',r['id'],'Withdrawn during read','reviewer')
            return self.h.native_rows([('A','10',1)])
        execute=MagicMock(side_effect=transport)
        result=records.run(self.store,c['plan'],self.config,c['tool'],execute)
        self.assertEqual(result['status'],'HELD');execute.assert_called_once()
        self.assertNotIn('rows',result['result'])

    def test_source_filter_cannot_escape_registered_columns(self):
        self.register();c=next(c for c in self.selected() if c['tool']=='source_records')
        plan=copy.deepcopy(c['plan']);plan['filters'][0]['column_id']=self.h.splan['object_id']+'/entity_id'
        with self.assertRaises(Conflict):records.build(self.store,plan,self.config,c['tool'])

    def test_direct_durable_run_rechecks_review_before_dispatch(self):
        r=self.register();c=self.selected()[0]
        run=self.runtime.create({'model_id':'model','call_budget':1,'actions':[{'tool':c['tool'],'input':c['plan']}]},'direct')
        reviews.revoke(self.store,'model',r['id'],'Withdrawn','reviewer')
        with self.assertRaises(Conflict):self.runtime.execute(run['id'])
        self.h.ntransport.assert_not_called()

    def test_disablement_prevents_registration_and_preserves_review_history(self):
        r=self.register();self.model['enabled']=False
        with self.assertRaises(Conflict):self.register()
        self.assertEqual(reviews.read(self.store,'model',r['id'])['hash'],r['hash'])

    def test_duplicate_projection_and_unsupported_native_type_rejected(self):
        body=copy.deepcopy(self.body);body['column_bindings'].append(body['column_bindings'][0])
        with self.assertRaises(ValueError):self.register(body)
        self.model['context']['reports'][0]['model_assets'][-1]['metadata']['dataType']='double'
        with self.assertRaises(ValueError):self.register()

    def test_mapping_for_child_only_unlocks_after_child_scalar(self):
        from investigator.adaptive_candidates import available
        self.register(dict(self.body,measure_id='Child'))
        candidates,_=self.candidates()
        visible=available(candidates,[{'tool':'native','measure_id':'Unseen ratio','dimension_id':None,'status':'COMPLETED'}],[])
        self.assertFalse(any(c['tool'].endswith('_records') for c in visible))
        visible=available(candidates,[{'tool':'native','measure_id':'Child','dimension_id':None,'status':'COMPLETED'}],[])
        self.assertEqual(len([c for c in visible if c['tool'].endswith('_records')]),2)

    def test_revocation_is_idempotent_and_retains_first_reason(self):
        r=self.register()
        first=reviews.revoke(self.store,'model',r['id'],'Original reason','reviewer')
        second=reviews.revoke(self.store,'model',r['id'],'Replacement reason','other')
        self.assertEqual(first,second)

    def test_admin_api_lifecycle_and_preview_are_query_free(self):
        app=create_app(self.store,'a'*32,'r'*32,investigations=self.agent)
        def call(method,path,body=None,token='a'*32):
            statuses=[];raw=json.dumps(body).encode()
            output=b''.join(app({'PATH_INFO':'/api/v2/admin/models/model/'+path,'REQUEST_METHOD':method,
                                'HTTP_AUTHORIZATION':'Bearer '+token,'CONTENT_TYPE':'application/json',
                                'CONTENT_LENGTH':str(len(raw)),'wsgi.input':BytesIO(raw)},lambda s,h:statuses.append(s)))
            return statuses[0],json.loads(output)
        self.assertEqual(call('POST','record-mappings',self.body,token='r'*32)[0],'403 Forbidden')
        status,review=call('POST','record-mappings',self.body);self.assertEqual(status,'200 OK')
        self.assertEqual(call('GET','record-mappings/'+review['id'])[1]['hash'],review['hash'])
        self.assertEqual(len(call('GET','record-mappings')[1]),1)
        status,preview=call('POST','diagnostic-preview',self.envelope)
        self.assertEqual(status,'200 OK');self.assertEqual(preview['cloud_calls'],0)
        self.assertEqual(len([c for c in preview['candidates'] if c['tool'].endswith('_records')]),2)
        self.assertEqual(call('POST','record-mappings/'+review['id']+'/revoke',{'reason':'Retired'})[0],'200 OK')
        self.native.assert_not_called();self.source.assert_not_called();self.planner.assert_not_called()


if __name__=='__main__':unittest.main()
