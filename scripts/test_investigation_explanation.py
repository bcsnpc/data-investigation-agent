import copy
from contextlib import closing
import json
from pathlib import Path
import tempfile
import unittest
from investigation_explanation import catalog, explain, latest, render
from ticket_workflow import TicketStore


class ExplanationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=TicketStore(Path(self.temp.name)/'workflow.sqlite')
        self.item={'id':'run','classification':'UNRESOLVED','request':{'observations':{'net_cash':[
            {'layer':'sql','status':'UNAVAILABLE'},
            {'layer':'gold','status':'AVAILABLE','data':'1529.6400','currency':'USD','filters':{'order_id':'ORD-000002'}},
            {'layer':'semantic','status':'AVAILABLE','data':'1529.6400','currency':'USD','filters':{'order_id':'ORD-000002'}}]}},
            'result':{'metrics':{'net_cash':{'boundaries':[{'status':'NOT_COMPARABLE'},{'status':'INSUFFICIENT_EVIDENCE'}]}}}}
        self.selection={'finding_ids':['observation-1'],'next_step_ids':['review-scope']}

    def test_model_cannot_omit_limits_or_change_exact_values(self):
        result=render(self.selection,catalog(self.item))
        text=json.dumps(result)
        for expected in ['1529.6400 USD','unavailable','NOT_COMPARABLE','INSUFFICIENT_EVIDENCE','UNRESOLVED']:
            self.assertIn(expected,text)
        self.assertFalse(result['automatic_defect_routing'])
        for row in result['findings']+result['next_steps']:
            self.assertTrue(row['references'])

    def test_unknown_claims_extra_fields_duplicates_and_empty_rejected(self):
        for selection in [dict(self.selection,classification='TECHNICAL_DEFECT'),
                          dict(self.selection,finding_ids=['invented-total']),
                          dict(self.selection,next_step_ids=['repair-source']),
                          dict(self.selection,finding_ids=[]),
                          dict(self.selection,finding_ids=['observation-1']*2)]:
            with self.subTest(selection=selection),self.assertRaises(ValueError):render(selection,catalog(self.item))

    def test_comparisons_require_same_scope_and_finite_numbers(self):
        self.assertIn('equal observed',catalog(self.item)['findings']['comparison-net_cash']['text'])
        for value in ['NaN','not-a-number']:
            item=copy.deepcopy(self.item);item['request']['observations']['net_cash'][2]['data']=value
            self.assertNotIn('comparison-net_cash',catalog(item)['findings'])
        for key,value in [('currency','EUR'),('filters',{'order_id':'ORD-000003'})]:
            item=copy.deepcopy(self.item);item['request']['observations']['net_cash'][2][key]=value
            self.assertNotIn('comparison-net_cash',catalog(item)['findings'])
        item=copy.deepcopy(self.item);item['request']['observations']['net_cash'][2]['data']='1530'
        self.assertIn('different observed',catalog(item)['findings']['comparison-net_cash']['text'])

    def test_persisted_selection_rerenders_and_stale_evidence_rejected(self):
        record=explain(self.store,self.item,lambda facts:(self.selection,{'total_tokens':10}))
        self.assertEqual(record['status'],'VALIDATED')
        record['explanation']['limitations']='Invented claim';record['classification']='TECHNICAL_DEFECT'
        with closing(self.store.connect()) as db:
            db.execute('UPDATE investigation_explanations SET record=?',(json.dumps(record),))
            db.commit()
        restored=latest(self.store,self.item)
        self.assertEqual(restored['classification'],'UNRESOLVED')
        self.assertNotIn('Invented claim',restored['explanation']['limitations'])
        changed=copy.deepcopy(self.item);changed['classification']='EXPECTED_BEHAVIOR'
        self.assertIsNone(latest(self.store,changed))
        record['selection']['finding_ids']=['invented']
        with closing(self.store.connect()) as db:
            db.execute('UPDATE investigation_explanations SET record=?',(json.dumps(record),));db.commit()
        self.assertIsNone(latest(self.store,self.item))

    def test_failed_attempt_is_sanitized_and_does_not_hide_evidence(self):
        def fail(_):raise RuntimeError('secret provider detail')
        record=explain(self.store,self.item,fail)
        self.assertEqual(record['status'],'FAILED');self.assertNotIn('secret',json.dumps(record))
        self.assertIsNone(latest(self.store,self.item))


if __name__=='__main__':unittest.main()
