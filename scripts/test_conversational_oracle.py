import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from investigator.conversational_oracle import load, score, target_differences, answer_batch
from investigator.onboarding import digest

ROOT=Path(__file__).resolve().parents[1]


class SealedOracleTests(unittest.TestCase):
    def setUp(self):
        self.oracle,self.seal=load(ROOT/'acceptance/oracle')

    def test_approved_exact_bytes_and_partition_are_fixed(self):
        self.assertEqual(self.seal['sha256'],'bc2819f1ab12ae93d2203a519a6318a6f9ecbc1a3220a466e664a00c495a9a6b')
        self.assertEqual(len(self.oracle['records']),68)
        self.assertEqual(sum(r['partition']=='held_out' for r in self.oracle['records']),28)

    def test_a1_preserves_superseded_seal_and_changes_only_reported_figures(self):
        import hashlib
        directory=ROOT/'acceptance/oracle'
        before=json.loads((directory/'oracle-before-a1.json').read_text())
        prior=json.loads((directory/'oracle-seal-before-a1.json').read_text())
        self.assertEqual(hashlib.sha256((directory/'oracle-before-a1.json').read_bytes()).hexdigest(),prior['sha256'])
        self.assertEqual(self.seal['supersedes']['sha256'],prior['sha256'])
        amendment=json.loads((directory/'oracle-amendment-a1.json').read_text())
        changed=[]
        for left,right in zip(before['records'],self.oracle['records']):
            a=copy.deepcopy(left);b=copy.deepcopy(right)
            old=a.pop('true_reported_figure');new=b.pop('true_reported_figure')
            self.assertEqual(a,b)
            if old!=new:
                changed.append(left['id'])
                self.assertEqual(old['state'],'NOT_STATED')
                source=new['value']['source']
                self.assertEqual(left['ticket'][source['start']:source['end']],source['quote'])
                self.assertEqual(new['value']['value'],source['quote'])
        self.assertEqual(set(changed),{c['id'] for c in amendment['changes']})
        self.assertEqual(len(changed),3)

    def test_one_oracle_byte_change_invalidates_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/'acceptance'
            shutil.copytree(ROOT/'acceptance/oracle',dest/'oracle')
            shutil.copytree(ROOT/'acceptance/model_steps',dest/'model_steps')
            with (dest/'oracle/oracle-draft.json').open('a') as f:f.write(' ')
            with self.assertRaisesRegex(ValueError,'Oracle seal mismatch'):load(dest/'oracle')

    def test_adoption_is_not_its_own_correctness_proof(self):
        o=next(r for r in self.oracle['records'] if r['id']=='original:family-D')
        target=o['true_target_and_cell']['value']
        p={'target_visual':{'target_id':target['target_id'],'mode':'KEYED'},
           'filters':target['selected_filters'],'dimension_ids':[],'reported_figure':{'state':'UNSPECIFIED'}}
        self.assertEqual(target_differences(o,p),[])
        p['filters']=[]
        self.assertIn('cell_keys',target_differences(o,p))

    def test_scope_equivalence_requires_reviewed_candidate_proof(self):
        o=next(r for r in self.oracle['records'] if r['true_target_and_cell'].get('value',{}).get('kind')=='MEASURE_AT_SCOPE')
        value=o['true_target_and_cell']['value']
        p={'measure_id':value['measure_id'],'model_id':value.get('model_id'),'filters':value['scope'],'dimension_ids':[],
           'target_visual':{'target_id':'wrong-cell','mode':'UNGROUPED'}}
        self.assertIn('unproved_equivalent_visual',target_differences(o,p))

    def test_illegitimate_choice_is_not_answered_to_manufacture_settlement(self):
        o=next(r for r in self.oracle['records'] if not r['legitimate_questions'])
        q={'id':'comparison','field':'COMPARISON','question':'Compared to what?',
           'choices':[{'id':'a','label':'Application','highlight':None}]}
        ticket={'questions':[q],'choice_values':{digest(q)+'/a':{'route':'APPLICATION'}}}
        self.assertEqual(answer_batch(ticket,o,[])['answers'],[])

    def test_transport_hold_cannot_pass_semantic_refusal(self):
        o=next(r for r in self.oracle['records'] if r['required_disposition']['value']=='UNSUPPORTED_ROUTE')
        row={'id':o['id'],'ticket_state':'HELD','ticket_history':[{'detail':{'reason':'UNIMPLEMENTED_ROUTE'}}],
             'failure':{'type':'UsageHold'},'adopted':False,'questions':0,'rounds':0}
        self.assertEqual(score([o],[row])['settled_within_one_round'],0)


if __name__=='__main__':unittest.main()
