from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock
import unittest
from investigator.guided_cases import Cases
from investigator.guided_intake import Catalog
from investigator.guided_investigator_installation import Factory
from investigator.intake_candidates import enumerate_targets
from investigator.shared_state import SharedState
from test_round23_intake_queries import graph,request,sql_objects
from test_round23_reasoning import MemoryCheckpoint,tool


class CandidateInvestigationTests(unittest.TestCase):
    def test_ambiguous_intake_reaches_checks_on_each_retained_scope_without_asking(self):
        self.run_case()

    def test_evaluator_specific_rejection_returns_to_loop_then_approves(self):
        self.run_case(rejections=1)

    def test_evaluator_stops_after_two_retries_and_downgrades_without_confident_draft(self):
        self.run_case(rejections=3)

    def test_soft_only_rejection_rewrites_from_saved_evidence_and_delivers(self):
        self.run_case(rejections=1,soft=True)

    def test_soft_only_rejections_never_downgrade_after_two_rewrites(self):
        self.run_case(rejections=3,soft=True)

    def test_missing_structured_field_gets_one_repair_without_native_reads(self):
        self.run_case(malformed=True)

    def run_case(self,rejections=0,soft=False,malformed=False):
        with TemporaryDirectory()as tmp:
            state=SharedState.offline(Path(tmp)/'state.sqlite');state.migrate()
            raw=graph();raw['nodes'] += [
                {'id':'sibling','kind':'VISUAL','label':'Second card','properties':{'filters':[{'id':2}]}},
                {'id':'table-node','kind':'TABLE','label':'Items'}]
            raw['edges'] += [{'source':'page','target':'sibling','kind':'CONTAINS'},
                             {'source':'sibling','target':'measure','kind':'COMPUTED_FROM'}]
            catalog=Catalog(raw)
            base=request();base.pop('visual');base.pop('page');base['reported_figure']['value']='7'
            inventory=enumerate_targets(catalog,text='The quantity is 7',proposal=base,explicit={'report':'report'})
            native_graph=Mock();native_graph.allowed={node['id']for node in raw['nodes']}
            native_graph.intake_catalog.return_value=raw
            native_graph.path_to_source.side_effect=lambda target:{'nodes':deepcopy(raw['nodes']),'edges':deepcopy(raw['edges'])}
            route={'kind':'SOURCE_SQL','config':{},'objects':sql_objects(),'asset_ids':['table'],
                   'path_nodes':['table-node'],'label':'Serving','dialect':'T-SQL'}
            events=[];reads=[];model=Mock();turn=[0];reviews=[0]
            def native(layer,bound,**kwargs):
                reads.append(bound['query'])
                # SQL compiler parameterizes constants; use its native bound values.
                value=7 if '1' in str(bound['parameters'])else 9
                return {'rows':[{'value':value}]}
            def complete(**kwargs):
                if kwargs['tools'][0]['name']=='repair_delivery':
                    import json
                    packet=json.loads(kwargs['messages'][0]['content'])
                    self.assertNotIn('case',packet)
                    self.assertIn('cited_evidence',packet)
                    draft=packet['draft']
                    draft.setdefault('calculation_explanation','The two queries sum quantity in their separate key scopes.')
                    return tool('repair_delivery',draft)
                if kwargs['tools'][0]['name']=='evaluate_delivery':
                    reviews[0]+=1
                    return tool('evaluate_delivery',{k:{'passed':not(k==('claims' if soft else 'question') and reviews[0]<=rejections),
                        'severity':'soft' if soft else 'hard',
                        'failure_kind':'citation_format' if soft else 'wrong_question',
                        'reason':('Citation formatting needs a rewrite.' if soft else 'The real layer difference does not answer the selected question.') if k==('claims' if soft else 'question') and reviews[0]<=rejections else 'Supported by the cited scoped checks.'}
                        for k in ('question','support','target','claims')})
                turn[0]+=1
                if turn[0]==1:
                    return tool('check_target_candidates',{'checks':[
                        {'candidate':'card','layer':'serving','kind':'sql','query':'SELECT SUM(quantity) AS value FROM dbo.Items WHERE id=1'},
                        {'candidate':'sibling','layer':'serving','kind':'sql','query':'SELECT SUM(quantity) AS value FROM dbo.Items WHERE id=2'}]})
                record=next(value for value in engine.state['evidence'].values()if value.get('tool')=='check_target_candidates')
                evidence=next(key for key,value in engine.state['evidence'].items()if value==record)
                response=tool('submit_finding',{'verdict':'not found','cause':'The reported figure matches Card; the causal rule is unmeasured.',
                    'numbers':[7,9],'checked':['serving'],'evidence_ids':[evidence],
                    'direct_answer':'Card matches 7 and Second card returns 9; the cause remains unresolved because its retained rule has not been read.',
                    'verdict_class':'UNRESOLVED','calculation_explanation':'The two queries sum quantity in their separate key scopes.',
                    'undecided':['The retained calculation rule has not been read.'],'routing':'ENGINEER',
                    'context_gap':{'type':'metric definition','note':'The retained calculation rule.'},'selected_target':'card'})
                if malformed:response['content'][0]['input'].pop('calculation_explanation')
                return response
            model.complete.side_effect=complete
            factory=Factory(state=state,graph=native_graph,routes={'serving':route},native=native,
                context_for=lambda *a:{},triage_for=lambda *a:SimpleNamespace(run=lambda:{'facts':[]}),
                model_for=lambda _:model,reserve=Mock(),persist=lambda c,event:events.append(event),
                job_runs=Mock(),refresh_history=Mock(),checkpoint_for=lambda _:MemoryCheckpoint())
            cases=Cases(state=state,graph=native_graph,estate='estate',engine_factory=factory)
            queued=cases.submit_candidates(request_key='one',intake=base,inventory=inventory,source={'kind':'FORM'})
            self.assertEqual(queued['status'],'QUEUED')
            engine=factory(queued)
            result=engine.run()
            self.assertEqual(result['status'],'UNRESOLVED' if rejections>=3 and not soft else 'ANSWERED')
            self.assertEqual(len(reads),2)
            if rejections<3 or soft:self.assertEqual(result['target_resolution']['selected'],'card')
            else:
                self.assertEqual(result['conclusion']['verdict_class'],'UNRESOLVED')
                self.assertIn('DELIVERY_EVALUATOR_REJECTED_AFTER_TWO_RETRIES',result['stop'])
                self.assertNotIn('Card matches 7 and Second card returns 9',result['business'])
            self.assertEqual(len(result['delivery_evaluations']),min(rejections+1,3))
            if rejections:
                self.assertFalse(result['delivery_evaluations'][0]['approved'])
                if not soft:self.assertIn('does not answer',result['delivery_evaluations'][0]['checks']['question']['reason'])
            if soft:self.assertEqual(len(result['delivery_repairs']),min(rejections,2))
            if malformed:self.assertEqual(len(result['delivery_repairs']),1)
            self.assertNotIn('question',result)
            self.assertEqual(result['case']['context']['candidate_inventory']['candidates'][1]['retained_scope']['properties']['filters'],[{'id':2}])


if __name__=='__main__':unittest.main()
