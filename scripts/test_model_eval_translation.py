import json,tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock,patch
import test_investigator_workspace as fixture
from investigator.model_eval_translation import run_case,azure_propose
from investigator.translation_eval import request
from investigator.process_tape import Tape


class ModelTranslationTests(unittest.TestCase):
    def test_evaluation_uses_installed_adapter_prompt_projection_and_wire(self):
        from investigator.translation_proposer import SCHEMA
        from investigator.adapters.translation_model import Provider,INSTRUCTIONS,wire_schema
        g=json.loads((Path(__file__).resolve().parents[1]/'acceptance/model_steps/translation.json').read_text())
        req=request(g['cases'][0]);options={'timeout_seconds':10,'max_output_tokens':1500,'max_payload_characters':8000}
        with patch('ticket_planner._azure_generate',return_value=({'expression':'untrusted'},{'usage':{'output_tokens':2}})) as generate:
            value,metadata=azure_propose({'translation':req},SCHEMA,options)
        self.assertEqual(generate.call_args.args[0],Provider(options=options).input(req))
        wire=generate.call_args.kwargs['schema']
        self.assertEqual(wire['properties']['objects']['items']['anyOf'],[
            {'type':'object','additionalProperties':False,'required':['id','kind'],
             'properties':{'id':{'type':'string','enum':['items']},'kind':{'type':'string','enum':['TABLE']}}}])
        self.assertEqual(wire['properties']['expression'],wire_schema(SCHEMA)['properties']['expression'])
        self.assertTrue(generate.call_args.kwargs['instructions'].startswith(INSTRUCTIONS))
        self.assertNotIn('available_cells',generate.call_args.args[0])
        self.assertTrue(SCHEMA['properties']['objects']['uniqueItems'])

    def test_producer_can_express_only_consumer_catalog_identity_kind_pairs(self):
        from investigator.translation_proposer import SCHEMA,validate
        from investigator.adapters.translation_model import Provider,wire_schema
        from jsonschema import Draft202012Validator
        g=json.loads((Path(__file__).resolve().parents[1]/'acceptance/model_steps/translation.json').read_text())
        req=request(g['cases'][0]);req['metadata']['objects']['items.k']='COLUMN'
        generate=MagicMock(return_value=({},{}))
        Provider(options={'timeout_seconds':10,'max_output_tokens':1500,'max_payload_characters':8000},generate=generate).propose(req,SCHEMA)
        item=wire_schema(generate.call_args.args[1])['properties']['objects']['items']
        for identity,kind in req['metadata']['objects'].items():
            Draft202012Validator(item).validate({'id':identity,'kind':kind})
        for bad in ({'id':'k','kind':'COLUMN'},{'id':'items','kind':'COLUMN'},{'id':'outside','kind':'TABLE'}):
            self.assertTrue(list(Draft202012Validator(item).iter_errors(bad)))
        self.assertEqual(SCHEMA['properties']['objects']['items']['properties']['id']['maxLength'],500)

    def test_one_proposal_is_metered_and_verified_locally_without_estate_routes(self):
        h=fixture.WorkspaceTests();h.setUp();self.addCleanup(h.doCleanups)
        g=json.loads((Path(__file__).resolve().parents[1]/'acceptance/model_steps/translation.json').read_text())
        c=g['cases'][0];r=request(c)
        p={k:r[k] for k in ('kind','definition_hash','target_engine','grouping','evaluation_timestamp')}
        p.update(objects=[{'id':'items','kind':'TABLE'}],expression='k in (select k from items order by v desc,k asc limit 2)')
        provider=MagicMock(return_value=(p,{'usage':{'input_tokens':5,'output_tokens':6}}))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'translation.tape.json'
            result=run_case(h.agent,g,c,provider,path,'translation-evaluation')
            self.assertEqual(result['evaluation']['verification']['status'],'VERIFIED')
            self.assertEqual(result['model_calls'],1);self.assertEqual(provider.call_count,1)
            self.assertNotIn('native_sql',provider.call_args.args[0]['translation'])
            self.assertEqual(Tape(path).bootstrap['entry_point'],'model_eval_translation')
            h.native.assert_not_called();h.source.assert_not_called();h.planner.assert_not_called()


if __name__=='__main__':unittest.main()
