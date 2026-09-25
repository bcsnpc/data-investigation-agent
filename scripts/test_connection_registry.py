import copy
import json
from pathlib import Path
import unittest

from investigator.connection_registry import attach, prefix
from investigator.dynamic_reasoning import wire_contract, from_wire
from investigator.onboarding import encoded
from investigator.planner_projection import fit


class RegistryTests(unittest.TestCase):
    config={'sql':{'server':'server','database':'db','visibility_schema':'app'},
            'fabric':{'workspace_id':'workspace'}}

    def payload(self):
        return {'starting_measure_id':'fabric://workspace/model/table/T/measures/M',
                'observations':[],'candidates':[],'hypotheses':[],
                'context_entry_points':[
                    {'id':'sql://server/db/object/1','kind':'SqlObject','name':'source'},
                    {'id':'fabric://workspace/model/table/T','kind':'SemanticTable','name':'T'},
                    {'id':'fabric://workspace/lake','kind':'Lakehouse','name':'lake'},
                    {'id':'sql://server/other/object/1','kind':'SqlObject','name':'other'}]}

    def test_registry_cost_constant_and_handles_round_trip(self):
        deltas=set()
        for n in (1,7,14,28,120):
            payload=self.payload()
            payload['context_entry_points']=[dict(payload['context_entry_points'][i%4],
                id=payload['context_entry_points'][i%4]['id']+'/'+str(i)) for i in range(n)]
            before=copy.deepcopy(payload);after=attach(payload,self.config,48000)
            deltas.add(len(encoded(after))-len(encoded(before)))
            self.assertEqual(payload,before)
            self.assertEqual(after['context_entry_points'],before['context_entry_points'])
            wire,_,handles=wire_contract(after)
            self.assertEqual(wire['connections'],after['connections'])
            self.assertEqual(len(handles),n)
            for handle,identity in handles.items():
                result=from_wire({'next':{'kind':'LOOKUP','operation':'asset','value':handle},'hypotheses':[]},handles)
                self.assertEqual(result['lookup']['value'],identity)
                self.assertEqual(handle[0],prefix(identity,after['connections']))
        self.assertEqual(len(deltas),1)

    def test_connection_roots_are_not_replaced_by_asset_handles(self):
        payload=self.payload()
        payload['context_entry_points'].append({'id':'fabric://workspace/model','kind':'SemanticModel','name':'model'})
        after=attach(payload,self.config,48000)
        wire,_,handles=wire_contract(after)
        self.assertIn('fabric://workspace/model',handles.values())
        self.assertEqual(wire['connections']['p']['connection'],'fabric://workspace/model')

    def test_identity_boundaries_do_not_grant_other_connections_membership(self):
        registry=attach(self.payload(),self.config,48000)['connections']
        for identity in ('sql://server/db2/object/1','fabric://workspace2/model','not-a-uri'):
            self.assertEqual(prefix(identity,registry),'a')
        self.assertEqual(prefix('fabric://workspace/model/table/T',registry),'p')
        self.assertEqual(prefix('fabric://workspace/model2',registry),'f')

    def test_saturated_payload_is_unchanged_including_evidence(self):
        payload=self.payload();ceiling=len(encoded(payload))
        self.assertIs(attach(payload,self.config,ceiling),payload)
        self.assertIs(attach(payload,self.config,ceiling-1),payload)

    def test_golden_directory_retained_when_registry_fits_or_is_omitted(self):
        case=json.loads((Path(__file__).parent/'fixtures/planner-view/directory-coverage.json').read_text())
        from unittest.mock import patch
        from types import SimpleNamespace
        from investigator import dynamic_reasoning
        state={'model_id':'model','observations':[],'decisions':[],'discovery_version':'synthetic',
               'planner_calls':0,'input_characters':0,'envelope':{'measure_id':self.payload()['starting_measure_id'],
               'dimension_ids':[],'limits':{'planner_calls':12,'input_characters':384000}}}
        with patch.object(dynamic_reasoning.context_search,'latest',return_value={**case,'version':'synthetic'}):
            payload=dynamic_reasoning.enrich(SimpleNamespace(get=lambda _: {'context':{'model_assets':[]}}),state,{'observations':[]})
        for ceiling in (len(encoded(payload)),48000):
            before=fit(copy.deepcopy(payload),ceiling);after=attach(before,self.config,ceiling)
            self.assertEqual(after['context_entry_points'],before['context_entry_points'])
            self.assertEqual(len(after['context_entry_points']),28)
            self.assertEqual(sum(e['kind']=='SqlObject' for e in after['context_entry_points']),11)
            self.assertLessEqual(len(encoded(after)),ceiling)

    def test_all_recorded_call_shapes_preserve_directory_and_sql_coverage(self):
        # Only lengths/counts from historical calls, no captured metadata or queries.
        shapes=json.loads((Path(__file__).parent/'fixtures/planner-view/ownership-shapes.json').read_text())
        self.assertEqual(len(shapes),53)
        for shape in shapes:
            payload=self.payload()
            payload['context_entry_points']=[{'id':str(i),'kind':'SqlObject' if i<shape['sql_objects'] else 'Other','name':'object'} for i in range(shape['entries'])]
            payload['padding']=''
            payload['padding']='x'*(shape['characters']-len(encoded(payload)))
            self.assertEqual(len(encoded(payload)),shape['characters'])
            after=attach(payload,self.config,48000)
            self.assertEqual(after.get('context_entry_points'),payload['context_entry_points'])
            self.assertLessEqual(len(encoded(after)),48000)


if __name__=='__main__':unittest.main()
