"""Ticket translation versus deterministic inventory lookup; no estate calls."""
import copy
import json
import unittest
from unittest.mock import patch
from investigator import definition_target as target, declaration_inventory as inventory, declared_reproduction
from investigator.question_intake import Intake, azure_resolve, wire_contract, TARGET_INSTRUCTIONS
import test_declared_predicate_adapter as adapter_fixture
from test_declared_predicate_adapter import native_filter, filter_config
import test_target_figure_contract as contract_fixture
import test_question_intake as intake_fixture
from test_question_intake import proposal
from investigator.onboarding import digest

class InventoryResolutionTests(unittest.TestCase):
    def setUp(self):
        self.helper=contract_fixture.TargetContractTests();self.inv,self.entry=self.helper.declaration()
        self.options=[{'target_id':'visual','inventory':self.inv,'restrictions':copy.deepcopy(self.entry['restrictions'])}]
        self.columns=[{'column_id':'column','name':'Region'}]
        self.request={'source':{'start':0,'end':5,'quote':'North'}}
    def lookup(self,request=None):
        return target.lookup(request or self.request,ticket=(request or self.request)['source']['quote'],options=self.options,columns=self.columns)
    def test_one_active_match_resolves_with_entry_provenance(self):
        record,audit,proof=self.lookup()
        self.assertEqual(record['resolution_kind'],'EVIDENCE');self.assertEqual(record['inventory_entry_id'],self.entry['id'])
        self.assertEqual(proof['resolved_value'],'North');self.assertEqual(audit['match_count'],1)
    def test_zero_and_conditional_only_refuse(self):
        for conditional in (False,True):
            inv,e=self.helper.declaration('CONDITIONAL' if conditional else 'ACTIVE')
            if not conditional:e['restrictions'][0]['values']=['South']
            self.options=[{'inventory':inv,'restrictions':e['restrictions']}]
            with self.assertRaises(target.ResolutionRefused) as caught:self.lookup()
            self.assertEqual(caught.exception.record['resolution_kind'],'REFUSED')
            self.assertEqual(caught.exception.record['candidates'],[])
            self.assertIn('Target ambiguity',str(caught.exception))
    def test_two_columns_refuse_and_list_both_declarations(self):
        e=copy.deepcopy(self.entry);e['source']['location']='retained#another';e['id']=inventory.identity(e['source']);e['restrictions'][0]['field_id']='other'
        self.inv['discovered'].append(e['source']);self.inv['entries'].append(e);self.options[0]['restrictions']+=e['restrictions']
        with self.assertRaises(target.ResolutionRefused) as caught:self.lookup()
        self.assertEqual(len(caught.exception.record['candidates']),2)
        self.assertEqual({c['column_id'] for c in caught.exception.audit['candidates']},{'column','other'})
    def test_two_entries_for_one_column_are_not_collapsed(self):
        e=copy.deepcopy(self.entry);e['source']['location']='retained#another';e['id']=inventory.identity(e['source'])
        self.inv['discovered'].append(e['source']);self.inv['entries'].append(e);self.options[0]['restrictions']+=e['restrictions']
        with self.assertRaises(target.ResolutionRefused) as caught:self.lookup()
        self.assertEqual(len(set(caught.exception.record['candidates'])),2)
    def test_same_entry_seen_in_two_visuals_is_not_counted_twice(self):
        self.options.append(copy.deepcopy(self.options[0]))
        self.assertEqual(self.lookup()[1]['match_count'],1)
    def test_stated_column_still_checks_inventory_and_flags_no_match(self):
        request={'column_id':'column','source':{'start':0,'end':6,'quote':'Region'}}
        self.options=[]
        record,audit,_=self.lookup(request)
        self.assertEqual(record['resolution_kind'],'STATED');self.assertEqual(audit['status'],'STATED_NO_ACTIVE_MATCH')
        self.assertEqual(audit['match_count'],0)
    def test_invented_value_or_missing_inventory_cannot_resolve(self):
        with self.assertRaises(ValueError):self.lookup({'source':{'start':0,'end':5,'quote':'South'},'resolution_kind':'EVIDENCE'})
        self.options[0]['inventory']=None
        with self.assertRaises(ValueError):self.lookup()
    def test_active_column_provenance_cannot_attest_a_different_value(self):
        record,_,_=self.lookup()
        record['source']={'start':0,'end':5,'quote':'South'}
        with self.assertRaisesRegex(ValueError,'matching ACTIVE'):
            target.validate(record,ticket='South',inventory=self.inv,active=self.options[0]['restrictions'])

class AdapterWiringTests(unittest.TestCase):
    def setUp(self):
        self.h=adapter_fixture.DeclaredPredicateAdapterTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        # Make North a single declaration, rather than the old synthetic fixture's three.
        self.h.modify(self.h.visual,lambda d:d.update(filterConfig=filter_config(native_filter(('West',)))))
        self.h.modify(self.h.slicer,lambda d:d['visual']['objects']['general'][0]['properties']['filter'].update(filter=native_filter(('South',))))
    def resolution(self):
        from investigator.adapters.report_predicates import targets
        return target.lookup({'source':{'start':0,'end':5,'quote':'North'}},ticket='North',
            options=targets(self.h.model,self.h.measure['id']),columns=[{'column_id':self.h.column['id'],'name':'Region'}])[0]
    def test_adapter_consumes_contract_and_rechecks_original_inventory(self):
        self.h.scope['definition_target']=self.resolution()
        d=self.h.declaration();self.assertEqual(d['status'],'DECLARED')
        self.assertEqual(d['evidence']['metadata']['target_resolution'],self.h.scope['definition_target'])
        self.h.modify(self.h.page,lambda d:d.update(filterConfig=filter_config(native_filter(('Elsewhere',)))))
        self.assertIn('Target ambiguity',self.h.declaration()['reason'])
    def test_real_visual_ambiguity_stays_a_refusal(self):
        record=self.resolution()
        self.h.part('definition/pages/p/visuals/another/visual.json',json.loads(self.h.visual['metadata']['content']))
        self.h.scope['definition_target']=record
        d=self.h.declaration();self.assertEqual(d['status'],'UNDECLARED');self.assertIn('Target ambiguity',d['reason'])
    def test_no_figure_reason_precedes_target_and_inventory_with_real_adapter(self):
        scope={'reported_figure':{'state':'UNSPECIFIED'},'definition_target':{'bad':'target'}}
        with patch.object(self.h.adapter,'declared_context',side_effect=AssertionError('must not extract')):
            result=declared_reproduction.run(self.h.adapter,self.h.layer,self.h.measure['id'],scope)
        self.assertEqual(result['reason'],declared_reproduction.NO_FIGURE)
        from investigator import narrative_form
        payload={'evidence':[{'id':'unavailable','result':{'check_kind':'DECLARED_CONTEXT_REPRODUCTION_UNAVAILABLE','reason':result['reason']}}]}
        business=narrative_form.business('The other checks remain scoped.',payload)
        technical=narrative_form.technical('No mechanism established.',payload,{'limits':[],'technical_output':{}},{'text':'Provide the shown figure.'})
        self.assertIn('You did not provide the number',business)
        self.assertIn(declared_reproduction.NO_FIGURE,technical)
        self.assertNotIn('inventory',business+technical)

class IntakeWiringTests(unittest.TestCase):
    def setUp(self):
        self.h=intake_fixture.IntakeTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.h.request['text']='The ratio looks low for North.'
        self.h.h.request['filters'][0]['values']=['North']
        helper=contract_fixture.TargetContractTests();self.inv,self.entry=helper.declaration();self.entry['restrictions'][0]['field_id']='c'
        self.h.workspace.target_options=lambda *args:[{'inventory':self.inv,'restrictions':copy.deepcopy(self.entry['restrictions'])}]
        p=proposal();p.update(filters=[],scope_quotes=[],target_request={'source':{'start':24,'end':29,'quote':'North'}})
        self.h.resolver.return_value=(p,{'usage':{'output_tokens':80}})
    def test_intake_resolves_before_column_ambiguity_and_review_forwards(self):
        saved=self.h.resolve();self.assertEqual(saved['status'],'PROPOSED',saved.get('error'))
        self.assertEqual(saved['proposal']['definition_target']['resolution_kind'],'EVIDENCE')
        self.assertEqual(saved['proposal']['filters'][0]['values'],['North'])
        preview=self.h.review(saved)
        self.assertEqual(preview['envelope']['definition_target'],saved['proposal']['definition_target'])
        self.assertEqual(preview['envelope']['reported_figure'],{'state':'UNSPECIFIED'})
    def test_zero_match_is_named_ambiguity_and_retains_refused_record(self):
        self.entry['restrictions'][0]['values']=['South']
        saved=self.h.resolve();self.assertEqual(saved['status'],'NEEDS_INPUT')
        self.assertEqual(saved['definition_target']['resolution_kind'],'REFUSED')
        self.assertIn('Target ambiguity',saved['question']);self.assertIsNone(saved['proposal'])
        self.assertEqual(self.h.workspace.agent.governor.snapshot()['reserved_today']['planner_calls'],1)

    def test_stated_column_no_match_is_recorded_not_silently_accepted(self):
        column=self.h.workspace.model('model')['columns'][0]
        ticket='The ratio looks low for North on '+column['name']+'.'
        self.h.request['text']=ticket
        p=proposal();p['filters'][0]['values']=['North'];p['scope_quotes'][0]['quote']='North'
        start=ticket.index(column['name'])
        p['target_request']={'column_id':column['column_id'],'source':{'start':start,'end':start+len(column['name']),'quote':column['name']}}
        self.h.resolver.return_value=(p,{})
        self.h.workspace.target_options=lambda *args:[]
        saved=self.h.resolve();self.assertEqual(saved['status'],'PROPOSED',saved.get('error'))
        self.assertEqual(saved['proposal']['definition_target']['resolution_kind'],'STATED')
        self.assertEqual(saved['target_resolution']['status'],'STATED_NO_ACTIVE_MATCH')

class TranslationTests(unittest.TestCase):
    def payload(self):
        return {'text':'Revenue for North.','models':[{'id':'model','measures':[{'id':'measure','name':'Revenue'}],
            'columns':[{'column_id':'column','name':'Region'}]}]}
    def test_model_extracts_value_without_emitting_resolution_or_guessing_column(self):
        request={'source':{'quote':'North'}}
        response={'action':'PROPOSE','model_id':'m0','measure_id':'m0v0','metric_quote':'Revenue','question':None,
            'triage':'MISMATCH_COMPLAINT:VERTICAL','filters':[],'dimension_ids':[],'reported_candidates':[],
            'target_request':request}
        with patch('ticket_planner.azure_generate',return_value=(response,{})):
            value,_=azure_resolve(self.payload())
        self.assertEqual(value['target_request'],{'source':{'start':12,'end':17,'quote':'North'}});self.assertNotIn('definition_target',value)
        self.assertEqual(value['filters'],[])
    def test_context_coverage_is_unchanged_and_schema_cost_is_explicit(self):
        from investigator.onboarding import encoded
        payload=self.payload();wire,schema,_=wire_contract(payload)
        self.assertEqual(len(wire['models']),len(payload['models']))
        self.assertEqual(sum(len(m['columns']) for m in wire['models']),sum(len(m['columns']) for m in payload['models']))
        self.assertEqual(sum(len(m['measures']) for m in wire['models']),sum(len(m['measures']) for m in payload['models']))
        expected=copy.deepcopy(payload)
        expected['models'][0]['id']='m0'
        expected['models'][0]['measures'][0]['id']='m0v0'
        expected['models'][0]['columns'][0]['column_id']='m0c0'
        self.assertEqual(encoded(wire),encoded(expected))
        before=copy.deepcopy(schema);before['properties'].pop('target_request');before['required'].remove('target_request')
        self.assertGreater(len(encoded(schema)),len(encoded(before)))
        self.assertNotIn('definition_target',schema['properties'])

if __name__=='__main__':unittest.main()
