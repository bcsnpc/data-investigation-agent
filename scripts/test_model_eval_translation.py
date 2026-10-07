import json,tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock
import test_investigator_workspace as fixture
from investigator.model_eval_translation import run_case,evaluation_wire
from investigator.translation_eval import request
from investigator.process_tape import Tape


class ModelTranslationTests(unittest.TestCase):
    def test_provider_wire_makes_uniqueness_automatic_without_weakening_consumer(self):
        from jsonschema import Draft202012Validator
        from investigator.translation_proposer import SCHEMA
        g=json.loads((Path(__file__).resolve().parents[1]/'acceptance/model_steps/translation.json').read_text())
        req=request(g['cases'][0]);wire=evaluation_wire(req)
        fields=wire['properties']
        self.assertEqual(fields['objects']['minItems'],1);self.assertEqual(fields['objects']['maxItems'],1)
        self.assertEqual(fields['grouping']['maxItems'],0)
        self.assertTrue(SCHEMA['properties']['objects']['uniqueItems'])
        self.assertFalse(Draft202012Validator(fields['objects']).is_valid([{'id':'items','kind':'TABLE'}]*2))
        req['metadata']['objects']['other']='TABLE'
        with self.assertRaisesRegex(ValueError,'only one declared object'):evaluation_wire(req)

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
