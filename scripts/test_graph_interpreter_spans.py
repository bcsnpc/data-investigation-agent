import hashlib
import json
from pathlib import Path
import unittest
from investigator.graph_interpreter import propose,source_lines,referenced_span


class SourceReferenceTests(unittest.TestCase):
    def test_retained_failed_capture_stays_invalid_new_line_reference_is_exact(self):
        fixture=json.loads((Path(__file__).parent/'testdata'/'graph-interpreter-span-failure.json').read_text())
        source=fixture['code']
        self.assertEqual(hashlib.sha256(source.encode()).hexdigest(),fixture['definition_hash'])
        self.assertEqual(len(fixture['failed_edges']),6)
        for old in fixture['failed_edges']:
            self.assertEqual((old['start'],old['end']),(235,400))
            self.assertNotEqual(source[old['start']:old['end']],old['quote'])
        # New producer must explicitly choose these references. This test does
        # not rewrite, search-repair, or reclassify the historical model answer.
        lines=source_lines(source)
        start,end,quote=referenced_span(source,lines,7,8)
        self.assertEqual(quote,' INSERT INTO [silver].[invoices] (invoice_id,account_id,invoice_date,amount,status)\n'
            ' SELECT invoice_id,account_id,invoice_date,amount,status FROM [bronze].[invoices];\n')
        self.assertEqual(source[start:end],quote)
        self.assertNotEqual((start,end),(235,400))

    def test_unicode_crlf_and_final_unterminated_line_preserved(self):
        source='-- café 😀\r\nSELECT amount\r\nFROM app.source'
        lines=source_lines(source)
        self.assertEqual(''.join(line['text'] for line in lines),source)
        self.assertEqual(lines[1]['start'],len('-- café 😀\r\n'))
        start,end,quote=referenced_span(source,lines,2,3)
        self.assertEqual(source[start:end],'SELECT amount\r\nFROM app.source')
        self.assertEqual(quote,source[start:end]);self.assertEqual(end,len(source))

    def test_no_search_or_repair_for_invalid_reference(self):
        source='SELECT value\nSELECT value\n';lines=source_lines(source)
        self.assertNotEqual(referenced_span(source,lines,1,1)[:2],referenced_span(source,lines,2,2)[:2])
        for first,last in ((0,1),(2,1),(1,3),(True,1)):
            with self.assertRaisesRegex(ValueError,'LINE_REFERENCE'):referenced_span(source,lines,first,last)
        lines[0]['text']='changed'
        with self.assertRaisesRegex(ValueError,'SPAN_DIFFERS'):referenced_span(source,lines,1,1)

    def test_model_never_supplies_quote_or_numeric_character_offsets(self):
        source='-- code evidence\noutput = input\n'
        calls=[]
        def producer(request,schema):
            calls.append(request)
            self.assertEqual(request['span_contract'],'SOURCE_LINE_REFERENCES_V2')
            fields=schema['properties']['edges']['items']['properties']
            self.assertNotIn('quote',fields);self.assertNotIn('start',fields)
            return {'edges':[{'source':'out','target':'in','kind':'COMPUTED_FROM','first_line':2,'last_line':2,
                'explanation':'The assignment uses the named input.'}]}
        got=propose(estate='e',owner='o',code=source,definition_hash=hashlib.sha256(source.encode()).hexdigest(),
            source_id='definition',observed_at='2026-10-13T00:00:00Z',nodes=[{'id':'out','kind':'COLUMN','label':'Output'},
            {'id':'in','kind':'COLUMN','label':'Input'}],producer=producer,model_call=lambda request,fn:fn())
        edge=got['edges'][0];span=edge['provenance']['span']
        self.assertEqual(source[span['start']:span['end']],edge['properties']['quote'])
        self.assertEqual(edge['confidence'],'INFERRED');self.assertFalse(edge['properties']['execution_established'])
        self.assertEqual(len(calls),1)


if __name__=='__main__':unittest.main()
