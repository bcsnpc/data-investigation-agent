"""No reference-estate identifiers in the installed investigation product."""
import ast
import copy
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
GUID = re.compile(r'\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b', re.I)
# Ambiguous ordinary nouns and engine contract keys (for example reason_code)
# are not identifiers. These names are distinctive reference-estate values.
NAMES = ('Handled Quantity', 'Round Ten Visual Variety', 'stock_movements',
         'movement_values', 'sql-orderops-9696025', 'ordersops', 'billingapp',
         'skynwhy.com', 'orderops_investigator', 'warehouse_bronze_e1b8e1')
ENTRYPOINTS = ('dia.py', 'run_estate_investigation.py', 'serve_investigator_workspace.py',
              'serve_investigations.py', 'serve_model_admin.py', 'estate_readiness.py',
              'metadata_worker.py', 'run_source_diagnostic.py', 'run_native_diagnostic.py')


def runtime_files():
    """Whole engine, adapters, UI and transitive local imports of public CLIs.

    Fixture builders, acceptance runners and archived demos are not installed
    investigation entrypoints. Imports from them into runtime join this scan.
    """
    found = set((SCRIPTS / 'investigator').rglob('*.py'))
    pending = list(found) + [SCRIPTS / name for name in ENTRYPOINTS]
    examined = set()
    while pending:
        path = pending.pop()
        if path in examined or not path.is_file():
            continue
        examined.add(path)
        found.add(path)
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            names = ([n.name for n in node.names] if isinstance(node, ast.Import)
                     else [node.module] if isinstance(node, ast.ImportFrom) and not node.level and node.module
                     else [])
            for name in names:
                stem = SCRIPTS.joinpath(*name.split('.'))
                for candidate in (stem.with_suffix('.py'), stem / '__init__.py'):
                    if candidate.is_file():
                        pending.append(candidate)
    for app in ('investigator-workspace', 'model-admin', 'investigation-review'):
        found.update(p for p in (ROOT / 'apps' / app).rglob('*')
                     if p.suffix in ('.js', '.html', '.css'))
    return sorted(found)


def findings(text, estate_guids):
    found = [name for name in NAMES if name.casefold() in text.casefold()]
    found += sorted(set(GUID.findall(text.lower())) & estate_guids)
    # A local development TCP port is not a business quantity.
    numeric_text = re.sub(r"add_argument\(['\"]--port['\"],\s*type=int,\s*default=\d+\)", 'port declaration', text)
    if re.search(r'\b(?:7,?661|8,?765)\b', numeric_text):
        found.append('reference-estate expected total')
    if re.search(r'(?i)\b(?:[a-z]:[\\/](?:dia-|data_investigation_agent)|family[-_][a-i]\b)', text):
        found.append('reference-estate local path or family')
    return found


class EstateNeutralityTests(unittest.TestCase):
    def test_installed_runtime_has_no_known_estate_literals(self):
        guids = set()
        for path in (ROOT / 'estates').glob('*.json'):
            guids.update(GUID.findall(path.read_text(encoding='utf8').lower()))
        bad = {p.relative_to(ROOT).as_posix(): findings(p.read_text(encoding='utf-8-sig'), guids)
               for p in runtime_files()}
        self.assertEqual({p: hits for p, hits in bad.items() if hits}, {})

    def test_adapter_platform_vocabulary_allowed_but_estate_values_rejected(self):
        self.assertEqual(findings('Microsoft Azure SQL Fabric EVALUATE SELECT reason_code', set()), [])
        for value in (*NAMES, '8765', 'family-G', r'D:\dia-round-eleven-links'):
            with self.subTest(value=value):
                self.assertTrue(findings(value, set()))
        guid = '149f8d99-1c66-4a0a-9624-759be002bb60'
        self.assertTrue(findings(guid, {guid}))

    def test_examples_use_the_existing_closed_contract_and_project_without_network(self):
        from investigator.estate_manifest import load, validate
        from investigator.adapters.estate_installation import configuration
        for name in ('fixture', 'billing'):
            with self.subTest(name=name):
                value = load(ROOT / 'estates' / (name + '.json'))
                self.assertEqual(value['version'], 'estate-manifest-v1')
                self.assertFalse('fixture_states' in value)
                self.assertEqual(configuration(value)['fabric']['workspace_id'],
                                 value['adapters'][0]['options']['fabric']['workspace_id'])
                bad = copy.deepcopy(value)
                bad['target_visual_override'] = 'not in the contract'
                with self.assertRaisesRegex(ValueError, 'Additional properties'):
                    validate(bad)

    def test_prompt_interpretation_no_longer_teaches_the_fixture_answer(self):
        from investigator.intake_extraction import INSTRUCTIONS
        self.assertFalse(findings(INSTRUCTIONS, set()))
        self.assertIn('A reported figure never chooses a target', INSTRUCTIONS)


if __name__ == '__main__':
    unittest.main()
