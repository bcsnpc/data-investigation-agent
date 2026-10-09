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
    def test_visual_confirmation_also_binds_its_declared_report_without_a_separate_choice(self):
        from investigator.ticket_clarification import batch
        raw,payload=fixture('Quantity looks wrong.',reports=[])
        ticket=protocol.new('ticket');offer=batch(ticket,{'retained_extraction':raw},payload)
        retained=confirmation.offer(ticket,offer['questions'],offer['values'],request_text=payload['text'],models=payload['models'])
        answers=[]
        for q in retained['questions']:
            chosen=next(c for c in q['choices'] if q['field']=='COMPARISON' or
                        retained['choice_values'][digest(q)+'/'+c['id']]['target_id']=='card')
            answers.append({'question_id':q['id'],'choice_id':chosen['id']})
        replied=protocol.answer(retained,answers)
        replied=confirmation.settle_container(replied,request_text=payload['text'],models=payload['models'])
        self.assertEqual(replied['settled']['REPORT_PAGE']['value'],{'report_id':'report','page_id':None})
        proof=confirmation.build(replied,payload['text']);confirmed={**payload,'_ticket_confirmation':proof}
        value=intake_extraction.resolve(raw,confirmed);validate(value,confirmed)
        self.assertEqual(value['report_binding']['resolution_kind'],'USER_CONFIRMED')
        self.assertEqual(value['report_binding']['report_id'],'report')
        hostile=copy.deepcopy(proof);hostile['fields']['NUMBER']['value']['report_id']='foreign'
        with self.assertRaisesRegex(ValueError,'container differs'):
            confirmation.values(hostile,ticket=payload['text'],models=payload['models'])

    def test_user_confirmed_visual_supplies_its_unique_measure_without_fabricating_quote(self):
        raw,payload=fixture('In Report, this number looks wrong.',measures=[])
        with self.assertRaisesRegex(ValueError,'Starting measure is unresolved'):intake_extraction.resolve(raw,payload)
        confirmed,_,_=confirm(payload,raw)
        value=intake_extraction.resolve(raw,confirmed);validate(value,confirmed)
        self.assertIsNone(value['metric_quote']);self.assertEqual(value['measure_id'],'measure')
        self.assertEqual(value['extracted_ticket']['response']['measures'],[])
        with self.assertRaises(ValueError):validate(value,payload)

    def test_confirmed_multimeasure_visual_cannot_choose_one_measure(self):
        raw,payload=fixture('In Report, this number looks wrong.',measures=[])
        payload['models'][0]['visuals'][0]['measure_ids'].append('other')
        confirmed,_,_=confirm(payload,raw)
        with self.assertRaisesRegex(ValueError,'one unique starting measure'):intake_extraction.resolve(raw,confirmed)

    def test_repeated_numeral_requires_an_occurrence_and_conserves_both(self):
        raw,payload=fixture('In Report, Quantity shows 16; the application also shows 16.',
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        from investigator.question_intake import FigureQuoteAmbiguous
        with self.assertRaises(FigureQuoteAmbiguous):intake_extraction.resolve(raw,payload)
        start=payload['text'].rindex('16')
        source={'start':start,'end':start+2,'quote':'16'}
        confirmed,_,_=confirm(payload,raw,figure=source)
        value=intake_extraction.resolve(raw,confirmed);validate(value,confirmed)
        self.assertEqual(value['reported_figure']['source'],source)
        self.assertEqual(value['extracted_ticket']['response'],raw)
        spans=value['extracted_ticket']['spans']['figures']
        self.assertEqual([v['quote']['start'] for v in spans],
            [payload['text'].index('16'),start])
        changed=copy.deepcopy(value);changed['extracted_ticket']['spans']['figures'].pop(0)
        with self.assertRaisesRegex(ValueError,'Resolved extraction differs'):validate(changed,confirmed)

    def test_confirmed_numeral_cannot_strip_its_unknown_precision(self):
        raw,payload=fixture('In Report, Quantity shows about 16.',
            figures=[{'quote':'about 16','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        start=payload['text'].index('16')
        confirmed,_,_=confirm(payload,raw,figure={'start':start,'end':start+2,'quote':'16'})
        with self.assertRaisesRegex(ValueError,'not one retained extraction'):intake_extraction.resolve(raw,confirmed)
        source={'start':payload['text'].index('about'),'end':start+2,'quote':'about 16'}
        confirmed,_,_=confirm(payload,raw,figure=source)
        with self.assertRaises(intake_extraction.reported_figure.UnavailablePrecision):
            intake_extraction.resolve(raw,confirmed)

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

    def test_route_confirmation_never_adds_provider_context_or_reclassifies_the_subject(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        confirmed,ticket,_=confirm(payload,raw)
        q={'id':'comparison','field':'COMPARISON','question':'What are you comparing against?',
           'choices':[{'id':'application','label':'The application','highlight':None}]}
        ticket=confirmation.offer(ticket,[q],{digest(q)+'/application':{'route':'APPLICATION'}},
            request_text=payload['text'],models=payload['models'])
        ticket=protocol.answer(ticket,[{'question_id':'comparison','choice_id':'application'}])
        confirmed['_ticket_confirmation']=confirmation.build(ticket,payload['text'])
        self.assertEqual(intake_extraction.wire(payload),intake_extraction.wire(confirmed))
        self.assertEqual(intake_extraction.request_size(payload),intake_extraction.request_size(confirmed))
        value=intake_extraction.resolve(raw,confirmed);validate(value,confirmed)
        self.assertEqual(value['ticket_route']['route'],'APPLICATION')
        self.assertEqual(value['question_kind']['kind'],raw['kind'])
        with self.assertRaises(ValueError):validate(value,payload)

    def test_confirmation_requires_an_actual_retained_user_answer(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        _,ticket,values=confirm(payload,raw)
        ticket['history']=[e for e in ticket['history'] if e['actor']!='USER']
        with self.assertRaisesRegex(ValueError,'user answer'):confirmation.build(ticket,payload['text'])

    def test_changed_request_cannot_reuse_confirmation(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        confirmed,_,_=confirm(payload,raw)
        with self.assertRaises(Exception):intake_extraction.resolve(raw,{**confirmed,'text':'Changed request'})

    def test_changed_catalog_cannot_reuse_confirmation(self):
        raw,payload=fixture('In Report, Quantity looks wrong.')
        confirmed,_,_=confirm(payload,raw)
        changed=copy.deepcopy(confirmed);changed['models'][0]['visuals'][0]['names']=['Changed card']
        with self.assertRaisesRegex(ValueError,'catalog changed'):intake_extraction.resolve(raw,changed)

    def test_user_can_supply_missing_report_page_without_a_fabricated_quote(self):
        raw,payload=fixture('Quantity looks wrong.',reports=[])
        model=payload['models'][0]
        model['visuals'][0]['page_id']='overview';model['visuals'][1]['page_id']='details'
        q={'id':'report-page','field':'REPORT_PAGE','question':'Which report/page?',
           'choices':[{'id':'overview','label':'Report — Overview','highlight':None}]}
        ticket=confirmation.offer(protocol.new('ticket'),[q],{
            digest(q)+'/overview':{'report_id':'report','page_id':'overview'}},
            request_text=payload['text'],models=payload['models'])
        ticket=protocol.answer(ticket,[{'question_id':'report-page','choice_id':'overview'}])
        confirmed={**payload,'_ticket_confirmation':confirmation.build(ticket,payload['text'])}
        value=intake_extraction.resolve(raw,confirmed);validate(value,confirmed)
        self.assertEqual(value['report_binding']['resolution_kind'],'USER_CONFIRMED')
        self.assertIsNone(value['report_binding']['source'])
        self.assertEqual(value['target_visual']['target_id'],'card')
        self.assertEqual(value['extracted_ticket']['response'],raw)
        from investigator.report_scope import report_binding
        self.assertEqual(report_binding(value['report_binding'],reports=model['reports'],ticket=payload['text']),value['report_binding'])
        # The proof is authority supplied by the server, not an additional wire
        # variant a model may declare on its own.
        with self.assertRaises(ValueError):validate(value,payload)
        bad=copy.deepcopy(value);bad.pop('extracted_ticket')
        with self.assertRaisesRegex(ValueError,'cannot declare user report'):validate(bad,confirmed)

    def test_report_confirmation_keeps_real_target_ambiguity(self):
        raw,payload=fixture('Quantity looks wrong.',reports=[])
        q={'id':'report','field':'REPORT_PAGE','question':'Which report?',
           'choices':[{'id':'report','label':'Report','highlight':None}]}
        ticket=confirmation.offer(protocol.new('ticket'),[q],{
            digest(q)+'/report':{'report_id':'report','page_id':None}},
            request_text=payload['text'],models=payload['models'])
        ticket=protocol.answer(ticket,[{'question_id':'report','choice_id':'report'}])
        with self.assertRaises(TargetUnresolved):
            intake_extraction.resolve(raw,{**payload,'_ticket_confirmation':confirmation.build(ticket,payload['text'])})

    def test_confirmed_target_can_resolve_an_unmatched_original_title(self):
        raw,payload=fixture('In Report, Missing card Quantity looks wrong.',
            visuals=[{'quote':'Missing card','role':'PRIMARY','form':'TITLE'}])
        confirmed,_,_=confirm(payload,raw)
        value=intake_extraction.resolve(raw,confirmed);validate(value,confirmed)
        self.assertEqual(value['target_visual']['target_id'],'card')
        self.assertEqual(value['extracted_ticket']['response']['visuals'],raw['visuals'])

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
