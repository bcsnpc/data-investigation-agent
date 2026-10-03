"""All inventory consumers share the scoped validator, including refusal delivery."""
import ast
from pathlib import Path
import unittest
from unittest.mock import patch
from investigator import declaration_inventory, report_scope, narrative_form, refusal_synthesis
from investigator.report_resolution import ResolutionRefused
from investigator.synthesis_digest import _context_evidence
from test_declared_reproduction import NeutralAdapter, SCOPE

class ScopedInventoryOnlyTests(unittest.TestCase):
    def test_every_inventory_validation_call_site_resolves_to_one_function(self):
        root=Path(__file__).parent/'investigator'; calls=[]; definitions=[]
        for path in root.rglob('*.py'):
            tree=ast.parse(path.read_text(encoding='utf-8-sig')); imported={}
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom):
                    for item in node.names: imported[item.asname or item.name]=((node.module or ''),item.name)
                if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name=='validate_inventory':
                    definitions.append(path.relative_to(root).as_posix())
            for node in ast.walk(tree):
                if not isinstance(node,ast.Call):continue
                fn=node.func
                if isinstance(fn,ast.Name) and fn.id in imported and imported[fn.id][1]=='validate_inventory':
                    self.assertEqual(imported[fn.id][0],'report_scope');calls.append(path.relative_to(root).as_posix())
                elif isinstance(fn,ast.Name) and fn.id=='validate_inventory':
                    self.assertEqual(path.name,'report_scope.py');calls.append(path.name)
                elif isinstance(fn,ast.Attribute) and fn.attr in ('validate','validate_inventory'):
                    owner=fn.value.id if isinstance(fn.value,ast.Name) else None
                    if fn.attr=='validate_inventory' or owner in ('declaration_inventory','inventory'):
                        self.assertEqual((owner,fn.attr),('report_scope','validate_inventory'))
                        calls.append(path.relative_to(root).as_posix())
        self.assertEqual(definitions,['report_scope.py'])
        self.assertFalse(hasattr(declaration_inventory,'validate'))
        self.assertEqual(set(calls),{'adapters/microsoft_process.py','adapters/report_predicates.py',
            'declared_reproduction.py','definition_target.py','report_resolution.py','report_scope.py','synthesis_digest.py'})
        self.assertGreaterEqual(len(calls),12)

    def test_synthesis_uses_original_scoped_inventory_consumer(self):
        declaration=NeutralAdapter().declared_context({'id':'top'},'measure',SCOPE)
        observation={**declaration['evidence'],'declaration_inventory':declaration['inventory'],
                     'process_roles':['declared_context_definition']}
        with patch.object(report_scope,'validate_inventory',wraps=report_scope.validate_inventory) as called:
            result=_context_evidence(observation)
        self.assertEqual(called.call_count,1)
        self.assertEqual(len(result['result']['declarations']),1)
        observation['declaration_inventory']['report_id']='foreign'
        with self.assertRaisesRegex(ValueError,'report differs'):_context_evidence(observation)

    def test_business_guard_rejects_identifier_form_in_every_narrative(self):
        for value in ('fabric://workspace/model/columns/warehouse_name','db.Sales','Customers_id',
                      '[Customers]','C:/file.sql','receipt_ab123456'):
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'identifier'):
                narrative_form.validate('The check for '+value+' was unavailable.',business=True)
        narrative_form.validate('Sales and Customers were checked.',business=True)

    def test_refusal_keeps_technical_reason_but_business_cannot_leak_it(self):
        reason='Target unavailable: value-existence observation unavailable for fabric://w/m/columns/warehouse_name.'
        state={'text':'What happened for North?','observations':[{'id':'refusal','tool':'process',
            'check_kind':'REPORT_SELECTION_REFUSED','reason':reason,'refusal_category':'UNAVAILABLE'}]}
        result=refusal_synthesis.render(state)
        business=result['business_output']['explanation']['text']
        self.assertIn('target check was unavailable',business)
        self.assertNotIn('fabric://',business);self.assertNotIn('Target ambiguity',business)
        self.assertIn(reason,result['technical_output']['explanation']['text'])
        self.assertEqual(result['refusal']['text'],reason)

    def test_business_refusal_validates_multiturn_question_without_leaking_structures(self):
        for question in ('What happened?\nWhat happened?', 'Why is {"quantity": 3} shown?'):
            state={'text':question,'observations':[{'id':'stop','tool':'process','check_kind':'INTAKE_REFUSED',
                                                  'reason':'More detail is required.'}]}
            result=refusal_synthesis.render(state)
            narrative_form.validate(result['business_output']['explanation']['text'],business=True)
            self.assertIn(question,result['technical_output']['explanation']['text'])
            self.assertNotIn('{',result['business_output']['explanation']['text'])

    def test_refusal_categories_are_explicit_not_inferred_from_reason(self):
        for category,prefix in (('AMBIGUOUS','Target ambiguity'),('UNAVAILABLE','Target unavailable'),
                                ('UNSUPPORTED','Target unsupported'),('VALUE_ABSENT','Target value absent')):
            error=ResolutionRefused(category,'Opaque producer detail.')
            self.assertEqual(error.category,category);self.assertTrue(str(error).startswith(prefix))
        with self.assertRaises(ValueError):ResolutionRefused('invented','detail')

if __name__=='__main__':unittest.main()
