"""Synthetic acceptance fixture only; never imported by the investigator."""
import json
import unittest
import test_flexible_investigation as dynamic_fixture
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.workspace import Workspace
from investigator.question_intake import Intake,azure_resolve


class IntakeFixture(unittest.TestCase):
    def setUp(self):
        self.helper=dynamic_fixture.DynamicTests();self.helper.setUp();self.addCleanup(self.helper.doCleanups)
        f=self.helper.fixture
        definition=json.loads(f.parts[f.mid]['model.bim'])
        definition['model']['tables'][0]['measures'].append({'name':'Ratio','expression':'DIVIDE([Total],[Double])'})
        f.parts[f.mid]['model.bim']=json.dumps(definition)
        f.scan('intake-fixture')
        self.policy={'environment':self.helper.store.environment,
            'daily_limits':{'planner_calls':100,'cloud_calls':100,'input_characters':4000000,'output_tokens':200000},
            'max_inflight_planners':1,'no_progress_limit':2}
        def planner(payload):
            if not any(o.get('tool')=='bounded_dax' for o in payload['observations']):
                from investigator.model_context import assets
                context=self.helper.store.get(self.helper.model['id'])['context']
                measure=next(a for a in assets(context) if a['id']==payload['starting_measure_id'])
                text='EVALUATE ROW("value",['+measure['name'].replace(']',']]')+'])'
                return self.helper.decision('QUERY',query={'tool':'bounded_dax','text':text,'max_rows':20})
            return self.helper.decision('ASK',question='What intended business contract should these observations be compared with?')
        self.agent=AdaptiveRuntime(self.helper.runtime,planner,clock=lambda:1000,usage_policy=self.policy)
        self.workspace=Workspace(self.agent,execution_enabled=True,clock=lambda:1000)
        self.workspace.intake=Intake(self.workspace,azure_resolve)
