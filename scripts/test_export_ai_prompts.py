import tempfile
import unittest
from pathlib import Path
from export_ai_prompts import inventory, render


class PromptExportTests(unittest.TestCase):
    def test_dynamic_inline_prompt_and_tools_are_preserved_without_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = """raise RuntimeError('must never import')
INSTRUCTIONS = 'Answer only from native evidence. Never invent a cause or choose another named target.'
def request_for(payload):
    system = 'Grade verdict, layer and cause independently. A bare clarification is a failure.'
    system += payload['rubric']
    return model.complete(system=system, messages=payload['messages'])
def toolbox():
    return [{'name':'read', 'description':'Bounded native read'}]
"""
            Path(tmp, 'example.py').write_text(source)
            result = render(inventory(tmp))
            self.assertIn("system += payload['rubric']", result)
            self.assertIn("'description':'Bounded native read'", result)
            self.assertIn('INSTRUCTIONS =', result)
            self.assertNotIn("raise RuntimeError", result)


if __name__ == '__main__':
    unittest.main()
