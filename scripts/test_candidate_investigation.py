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
            events=[];reads=[];model=Mock();turn=[0]
            def native(layer,bound,**kwargs):
                reads.append(bound['query'])
                # SQL compiler parameterizes constants; use its native bound values.
                value=7 if '1' in str(bound['parameters'])else 9
                return {'rows':[{'value':value}]}
            def complete(**kwargs):
                turn[0]+=1
                if turn[0]==1:
                    return tool('check_target_candidates',{'checks':[
                        {'candidate':'card','layer':'serving','kind':'sql','query':'SELECT SUM(quantity) AS value FROM dbo.Items WHERE id=1'},
                        {'candidate':'sibling','layer':'serving','kind':'sql','query':'SELECT SUM(quantity) AS value FROM dbo.Items WHERE id=2'}]})
                record=next(value for value in engine.state['evidence'].values()if value.get('tool')=='check_target_candidates')
                evidence=next(key for key,value in engine.state['evidence'].items()if value==record)
                return tool('submit_finding',{'verdict':'not found','cause':'The reported figure matches Card; the causal rule is unmeasured.',
                    'numbers':[7,9],'checked':['serving'],'evidence_ids':[evidence],
                    'direct_answer':'Card matches 7 and Second card returns 9; the cause remains unresolved because its retained rule has not been read.',
                    'verdict_class':'UNRESOLVED','calculation_explanation':'The two queries sum quantity in their separate key scopes.',
                    'undecided':['The retained calculation rule has not been read.'],'routing':'ENGINEER',
                    'context_gap':{'type':'metric definition','note':'The retained calculation rule.'},'selected_target':'card'})
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
            self.assertEqual(result['status'],'ANSWERED')
            self.assertEqual(len(reads),2)
            self.assertEqual(result['target_resolution']['selected'],'card')
            self.assertNotIn('question',result)
            self.assertEqual(result['case']['context']['candidate_inventory']['candidates'][1]['retained_scope']['properties']['filters'],[{'id':2}])


if __name__=='__main__':unittest.main()
