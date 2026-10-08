"""A number at another addressed visual cannot answer the stated referent."""
import copy
import json
from pathlib import Path
import unittest
from investigator.visual_target import resolve, validate, TargetUnresolved
from investigator.question_intake import validate as validate_intake
from investigator.adapters import report_cells
import test_declared_predicate_adapter as fixture


def span(text, quote):
    start=text.index(quote)
    return {'start':start,'end':start+len(quote),'quote':quote}


class ReferentTests(unittest.TestCase):
    def setUp(self):
        self.ticket='Global card shows 8765; Warehouse matrix TOTAL also shows 8765.'
        self.catalog=[{'target_id':'card','report_id':'report','measure_ids':['measure'],
                       'names':['Global card'],'grouping_columns':[],'unsupported':None},
                      {'target_id':'matrix','report_id':'report','measure_ids':['measure'],
                       'names':['Warehouse matrix'],'grouping_columns':['warehouse','product'],'unsupported':None}]

    def resolve(self, name, mode='UNGROUPED', total=None):
        return resolve({'source':span(self.ticket,name),'mode':mode,
                        'mode_source':span(self.ticket,total) if total else None},
                       ticket=self.ticket,candidates=self.catalog,report_id='report',measure_id='measure')

    def test_missing_named_target_refuses_with_candidates_even_when_values_match(self):
        with self.assertRaises(TargetUnresolved) as caught:
            resolve(None,ticket=self.ticket,candidates=self.catalog,report_id='report',measure_id='measure')
        self.assertEqual(len(caught.exception.candidates),2)

    def test_card_and_total_remain_different_referents(self):
        card=self.resolve('Global card')
        total=self.resolve('Warehouse matrix','TOTAL','TOTAL')
        self.assertNotEqual(card['target_id'],total['target_id'])
        total['source']=card['source']
        with self.assertRaises(TargetUnresolved):
            validate(total,ticket=self.ticket,candidates=self.catalog,report_id='report',measure_id='measure')

    def test_unstated_total_is_not_invented(self):
        with self.assertRaises(TargetUnresolved):self.resolve('Warehouse matrix','TOTAL')

    def test_two_visuals_with_the_same_stated_name_refuse(self):
        self.catalog.append(dict(self.catalog[0],target_id='other-card'))
        with self.assertRaises(TargetUnresolved):self.resolve('Global card')

    def test_keyed_target_requires_every_declared_group_before_admission(self):
        from investigator.visual_target import complete
        target=self.resolve('Warehouse matrix','KEYED')
        with self.assertRaises(TargetUnresolved):
            complete(target,self.catalog,[{'column_id':'warehouse','operator':'in','values':['North']}])
        complete(target,self.catalog,[{'column_id':field,'operator':'in','values':['selected']}
                                      for field in ('warehouse','product')])

    def test_wire_handles_preserve_every_visual_and_grouping_column(self):
        from investigator.question_intake import wire_contract
        payload={'text':self.ticket,'models':[{'id':'model','measures':[{'id':'measure','name':'Quantity'}],
            'columns':[{'column_id':x,'name':x} for x in ('warehouse','product')],
            'reports':[{'id':'report','name':'Report'}],'visuals':copy.deepcopy(self.catalog)}]}
        before=copy.deepcopy(payload)
        wire,_,_=wire_contract(payload)
        self.assertEqual(payload,before)
        self.assertEqual(len(wire['models'][0]['visuals']),len(self.catalog))
        self.assertEqual(wire['models'][0]['visuals'][1]['grouping_columns'],['m0c0','m0c1'])
        self.assertEqual(wire['models'][0]['visuals'][0]['measure_ids'],['m0v0'])

    def test_sealed_wrong_cell_proposal_fails_before_any_procedure_read(self):
        source=json.loads((Path(__file__).parent/'fixtures/round_ten/wrong-cell-sealed-excerpt.json').read_text())
        proposal=source['proposal'];measure=proposal['measure_id'];report=proposal['report_binding']['report_id']
        model={'id':proposal['model_id'],'columns':[],'measures':[{'id':measure,'name':'Handled Quantity'}],
               'reports':[{'id':report,'name':'Round Ten Visual Variety'}],
               'visuals':[dict(c,report_id=report,measure_ids=[measure]) for c in self.catalog]}
        with self.assertRaises(TargetUnresolved) as caught:
            validate_intake(copy.deepcopy(proposal),{'text':source['ticket'],'models':[model]})
        self.assertEqual(len(caught.exception.candidates),2)
        self.assertEqual(source['wrong_answer_cell']['mode'],'TOTAL')


class AddressTests(unittest.TestCase):
    part=fixture.DeclaredPredicateAdapterTests.part
    modify=fixture.DeclaredPredicateAdapterTests.modify

    def setUp(self):fixture.DeclaredPredicateAdapterTests.setUp(self)

    def test_card_target_builds_only_the_card_address(self):
        doc=json.loads(self.visual['metadata']['content'])
        self.scope['target_visual']={'target_id':self.visual['id'],'measure_id':self.measure['id'],'mode':'UNGROUPED'}
        cells=report_cells.addresses(self.model,doc,self.visual['id'],self.measure['id'],self.scope)
        self.assertEqual(len(cells),1)
        self.assertEqual(cells[0]['target_id'],self.visual['id'])
        with self.assertRaisesRegex(ValueError,'TARGET_UNRESOLVED'):
            report_cells.addresses(self.model,doc,'different',self.measure['id'],self.scope)

    def test_resolved_global_card_reproduces_on_that_card_only(self):
        from investigator import declared_reproduction
        self.modify(self.page,lambda d:d.update(displayName='Global card'))
        self.scope['report_binding']={'resolution_kind':'STATED','report_id':self.report['report']['id'],
            'source':{'start':0,'end':6,'quote':'Report'}}
        self.scope['target_visual']=resolve({'source':span('Global card','Global card'),
            'mode':'UNGROUPED','mode_source':None},ticket='Global card',candidates=report_cells.catalog(self.model),
            report_id=self.report['report']['id'],measure_id=self.measure['id'])
        result=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],self.scope)
        self.assertEqual(result['finding']['label'],'REPRODUCED')
        self.assertEqual(result['finding']['cell']['target_id'],self.visual['id'])
        self.assertEqual(len(self.requests),2)

    def test_target_removed_never_dispatches_a_value_probe(self):
        from investigator import declared_reproduction
        self.scope['report_binding']={'resolution_kind':'STATED','report_id':self.report['report']['id'],
            'source':{'start':0,'end':6,'quote':'Report'}}
        result=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],self.scope)
        self.assertEqual(result['unsupported_form'],'TARGET_UNRESOLVED')
        self.assertEqual(self.requests,[])

    def test_hostile_adapter_cannot_read_another_cell_even_if_its_number_matches(self):
        from investigator.report_cell import validate as validate_cell
        from investigator.onboarding import digest
        cell={'target_id':'unrequested','measure_id':self.measure['id'],'mode':'UNGROUPED',
              'grouping_columns':[],'key_restrictions':[]}
        cell['id']=digest(cell)
        scope={'target_visual':{'target_id':'requested','measure_id':self.measure['id'],'mode':'UNGROUPED'}}
        with self.assertRaisesRegex(ValueError,'ticket referent'):
            validate_cell(cell,self.measure['id'],scope)

    def test_two_group_keys_required_and_no_substituted_total(self):
        doc=json.loads(self.visual['metadata']['content'])
        doc['visual']['visualType']='pivotTable'
        column=copy.deepcopy(self.column);column.update(id='other/product',name='Product')
        self.model['context']['model_assets'].append(column)
        from test_declared_predicate_adapter import field
        doc['visual']['query']['queryState']['Rows']={'projections':[{'field':field()},
            {'field':field(column='Product')}]}
        self.scope['target_visual']={'target_id':self.visual['id'],'measure_id':self.measure['id'],'mode':'KEYED'}
        with self.assertRaisesRegex(ValueError,'MISSING_CELL_KEYS: Product'):
            report_cells.addresses(self.model,doc,self.visual['id'],self.measure['id'],self.scope)
        self.scope['target_visual']['mode']='TOTAL'
        cells=report_cells.addresses(self.model,doc,self.visual['id'],self.measure['id'],self.scope)
        self.assertEqual(len(cells),1)
        self.assertEqual(cells[0]['mode'],'TOTAL')
        self.assertEqual(len(cells[0]['grouping_columns']),2)
        self.assertEqual(cells[0]['key_restrictions'],[])


if __name__=='__main__':unittest.main()
