import copy
import unittest
from investigator import ticket_clarification as planner, ticket_protocol as protocol, intake_confirmation
from investigator.onboarding import digest
from test_intake_extraction import fixture


class TicketClarificationTests(unittest.TestCase):
    def test_named_container_limits_offer_without_using_values_or_picking_target(self):
        raw,payload=fixture('In Report, Quantity shows 16 and 17.',
            figures=[{'quote':v,'role':'PRIMARY','state':'NUMBER','precision_quote':None} for v in ('16','17')])
        other=copy.deepcopy(payload['models'][0]);other['id']='other-model'
        other['reports']=[{'id':'other-report','name':'Unrelated report'}]
        for visual in other['visuals']:
            visual['target_id']='other-'+visual['target_id'];visual['report_id']='other-report'
        payload['models'].append(other)
        offer=planner.batch(protocol.new('ticket'),{'retained_extraction':raw},payload)
        self.assertIsNone(offer['blocked'])
        numbers=[v for v in offer['values'].values() if 'figure_source' in v]
        self.assertEqual({v['target_id'] for v in numbers},{'card','matrix'})
        self.assertEqual({v['figure_source']['quote'] for v in numbers},{'16','17'})
        self.assertEqual(len(numbers),4)

    def test_competing_values_are_distinct_choices_for_each_target(self):
        raw,payload=fixture('In Report, Quantity shows 16 and 17.',
            figures=[{'quote':v,'role':'PRIMARY','state':'NUMBER','precision_quote':None} for v in ('16','17')])
        ticket=protocol.new('ticket')
        offered=planner.batch(ticket,{'retained_extraction':raw},payload)
        self.assertIsNone(offered['blocked'])
        self.assertEqual({q['field'] for q in offered['questions']},{'NUMBER','COMPARISON'})
        numbers=[v for v in offered['values'].values() if 'figure_source' in v]
        self.assertEqual(len(numbers),4)
        self.assertEqual({v['figure_source']['quote'] for v in numbers},{'16','17'})
        self.assertEqual({v['mode'] for v in numbers},{'UNGROUPED','TOTAL'})
        retained=intake_confirmation.offer(ticket,offered['questions'],offered['values'],
            request_text=payload['text'],models=payload['models'])
        self.assertEqual(retained['state'],'CLARIFYING')
        self.assertEqual(retained['rounds'],1)

    def test_no_figure_never_becomes_zero_or_empty(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        offer=planner.batch(protocol.new('ticket'),{'retained_extraction':raw},payload)
        self.assertIsNone(offer['blocked'])
        self.assertTrue(all(v['figure_source'] is None for v in offer['values'].values() if 'figure_source' in v))

    def test_all_occurrences_offered_without_picking_first(self):
        raw,payload=fixture('In Report, Quantity shows 16, unlike the old 16.',
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        offer=planner.batch(protocol.new('ticket'),{'retained_extraction':raw},payload)
        sources={v['figure_source']['start'] for v in offer['values'].values() if 'figure_source' in v}
        self.assertEqual(sources,{payload['text'].index('16'),payload['text'].rindex('16')})

    def test_bad_provenance_and_oversized_catalog_refuse_whole_offer(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        bad=copy.deepcopy(raw);bad['primary']='not in ticket'
        self.assertIsNotNone(planner.batch(protocol.new('ticket'),{'retained_extraction':bad},payload)['blocked'])
        model=payload['models'][0];card=model['visuals'][0]
        model['visuals']=[dict(card,target_id='card-'+str(i)) for i in range(101)]
        offered=planner.batch(protocol.new('ticket'),{'retained_extraction':raw},payload)
        self.assertIn('bound exceeded',offered['blocked']);self.assertEqual(offered['questions'],[])

    def test_nondefault_manifest_controls_choices_without_model_judgment(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        settings=copy.deepcopy(planner.DEFAULTS)
        settings['comparison_choices']=[{'route':'STALE','label':'Check lateness'}]
        settings['default_route']='STALE';settings['max_clarifying_rounds']=1
        offer=planner.batch(protocol.new('ticket'),{'retained_extraction':raw},payload,settings)
        q=next(q for q in offer['questions'] if q['field']=='COMPARISON')
        self.assertEqual(q['choices'][0]['label'],'Check lateness')
        self.assertEqual(offer['values'][digest(q)+'/'+q['choices'][0]['id']],{'route':'STALE'})

    def test_settled_fields_not_asked_again(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        ticket=protocol.new('ticket');ticket['settled']={f:{'authority':'USER_CONFIRMED'} for f in protocol.FIELDS}
        self.assertEqual(planner.batch(ticket,{'retained_extraction':raw},payload)['questions'],[])
