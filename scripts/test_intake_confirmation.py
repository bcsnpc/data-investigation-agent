import copy
import unittest
from investigator import intake_confirmation as confirmation, ticket_protocol as protocol, intake_extraction
from investigator.onboarding import digest
from investigator.question_intake import validate
from investigator.visual_target import TargetUnresolved
from test_intake_extraction import fixture


def confirm(payload, raw, target='card', figure=None, mode='UNGROUPED'):
    question={'id':'number','field':'NUMBER','question':'Which displayed figure should we check?',
              'choices':[{'id':'card','label':'Global card','highlight':None},
                         {'id':'matrix','label':'Warehouse matrix total','highlight':None}]}
    choice_values={digest(question)+'/'+c['id']:{'target_id':c['id'],
        'mode':mode if c['id']==target else 'TOTAL' if c['id']=='matrix' else 'UNGROUPED',
        'figure_source':figure} for c in question['choices']}
    ticket=confirmation.offer(protocol.new('ticket'),[question],choice_values,
                              request_text=payload['text'],models=payload['models'])
    ticket=protocol.answer(ticket,[{'question_id':'number','choice_id':target}])
    proof=confirmation.build(ticket,payload['text'])
    return {**payload,'_ticket_confirmation':proof},ticket,choice_values


class IntakeConfirmationTests(unittest.TestCase):
    def test_ambiguous_visual_resolves_only_from_recorded_user_choice(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        with self.assertRaises(TargetUnresolved):intake_extraction.resolve(raw,payload)
        confirmed,_,_=confirm(payload,raw)
        value=intake_extraction.resolve(raw,confirmed)
        validate(value,confirmed)
        self.assertEqual(value['target_visual']['target_id'],'card')
        self.assertIn('user_confirmation',value['target_visual']['match_basis']['matched'])
        self.assertEqual(value['extracted_ticket']['response'],raw)
        with self.assertRaises(ValueError):validate(value,payload)

    def test_competing_figures_preserved_after_user_selects_one(self):
        raw,payload=fixture('In Report, Quantity shows 16 and 17 for the same card.',
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None},
                     {'quote':'17','role':'COMPARISON','state':'NUMBER','precision_quote':None}],
            comparisons=['17'])
        source=intake_extraction.spans(raw,payload['text'])['figures'][1]['quote']
        confirmed,_,_=confirm(payload,raw,figure=source)
        value=intake_extraction.resolve(raw,confirmed)
        validate(value,confirmed)
        self.assertEqual(value['reported_figure']['value'],'17')
        self.assertEqual(value['extracted_ticket']['response'],raw)
        self.assertEqual(len(value['extracted_ticket']['spans']['figures']),2)

    def test_target_confirmation_does_not_erase_unsettled_figures(self):
        raw,payload=fixture('In Report, Quantity shows 16 and 17.',
            figures=[{'quote':v,'role':'PRIMARY','state':'NUMBER','precision_quote':None} for v in ('16','17')])
        confirmed,_,_=confirm(payload,raw)
        with self.assertRaises(intake_extraction.reported_figure.AmbiguousFigure):intake_extraction.resolve(raw,confirmed)

    def test_model_cannot_invent_confirmation_or_select_another_target(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        confirmed,_,_=confirm(payload,raw)
        value=intake_extraction.resolve(raw,confirmed)
        for key in ('target_visual','extracted_ticket'):
            bad=copy.deepcopy(value)
            if key=='target_visual':bad[key]['target_id']='matrix'
            else:bad[key]['confirmation']['fields']['NUMBER']['value']['target_id']='matrix'
            with self.subTest(key=key),self.assertRaises(ValueError):validate(bad,confirmed)

    def test_confirmation_never_adds_provider_context_or_selects_a_comparison_route(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        confirmed,_,_=confirm(payload,raw)
        self.assertEqual(intake_extraction.wire(payload),intake_extraction.wire(confirmed))
        self.assertEqual(intake_extraction.request_size(payload),intake_extraction.request_size(confirmed))
        confirmed['_ticket_confirmation']['fields']['COMPARISON']={
            'proof':{'question_id':'comparison','choice_id':'application','authority':'USER_CONFIRMED','question_hash':'retained'},
            'value':{'route':'APPLICATION'}}
        with self.assertRaisesRegex(ValueError,'CONFIRMATION_BRIDGE_UNIMPLEMENTED'):
            intake_extraction.resolve(raw,confirmed)

    def test_confirmation_requires_an_actual_retained_user_answer(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        _,ticket,values=confirm(payload,raw)
        ticket['history']=[e for e in ticket['history'] if e['actor']!='USER']
        with self.assertRaisesRegex(ValueError,'user answer'):confirmation.build(ticket,payload['text'])

    def test_changed_request_cannot_reuse_confirmation(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        confirmed,_,_=confirm(payload,raw)
        with self.assertRaises(Exception):intake_extraction.resolve(raw,{**confirmed,'text':'Changed request'})

    def test_confirmation_never_invents_a_reported_span(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        with self.assertRaises(ValueError):confirm(payload,raw,figure={'start':0,'end':2,'quote':'16'})

    def test_all_offered_choices_have_values_and_unknown_visuals_are_not_offered(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        _,ticket,values=confirm(payload,raw)
        question=ticket['history'][0]['detail']['questions'][0]
        for wrong in ({}, {**values,'extra':values[next(iter(values))]}):
            with self.assertRaisesRegex(ValueError,'Every offered choice'):
                confirmation.offer(protocol.new('other'),[question],wrong,
                    request_text=payload['text'],models=payload['models'])
        values[next(iter(values))]['target_id']='not-retained'
        with self.assertRaisesRegex(ValueError,'visual is absent'):
            confirmation.offer(protocol.new('other'),[question],values,
                request_text=payload['text'],models=payload['models'])

    def test_total_is_user_authority_but_keyed_scope_still_requires_keys(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        confirmed,_,_=confirm(payload,raw,target='matrix',mode='TOTAL')
        value=intake_extraction.resolve(raw,confirmed);validate(value,confirmed)
        self.assertEqual(value['target_visual']['mode'],'TOTAL')
        confirmed,_,_=confirm(payload,raw,target='matrix',mode='KEYED')
        with self.assertRaisesRegex(TargetUnresolved,'cell key'):validate(intake_extraction.resolve(raw,confirmed),confirmed)


if __name__=='__main__':unittest.main()
