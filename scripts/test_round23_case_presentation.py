import json
import unittest
from copy import deepcopy
from unittest.mock import Mock
from investigator.model_case_presentation import Presentation


class Tests(unittest.TestCase):
    def test_aliases_restore_only_addresses_never_query_text_key_or_reported_value(self):
        original='a'*64;query="SELECT 'ref_0001' AS actual_key FROM dbo.Items"
        context={'intake':{'report':original,'reported_figure':{'state':'NUMBER','value':'123'}},
            'layers':{original:{'objects':[{'id':'fabric://w/l/table/Items','definition':query}]}}}
        saved=deepcopy(context);p=Presentation(context,{},'instructions')
        def complete(**kw):
            self.assertIn(query.replace('"','\\"'),kw['system'])
            alias=p.forward[original]
            return {'content':[{'type':'tool_use','name':'record_trace','input':{'queries':[{'layer':alias,'query':query}],'key':alias}}]}
        response=p.complete(Mock(complete=complete),system='unused original',messages=[],tools=[])
        result=response['content'][0]['input']
        self.assertEqual(result['queries'][0]['layer'],original)
        self.assertEqual(result['queries'][0]['query'],query)
        self.assertEqual(result['key'],p.forward[original])
        self.assertEqual(context,saved)

    def test_deduplication_is_reversible_and_preserves_every_structured_fact(self):
        shared={'definition':'SELECT SUM(units) FROM dbo.Items '+('x'*200),'scope':{'date':'2026-10-27'}}
        raw={'first':shared,'second':deepcopy(shared),'third':[deepcopy(shared)]}
        projected=Presentation.deduplicate(raw)
        self.assertEqual(projected['second'],{'verbatim_reference':'#/first'})
        def expand(value):
            if isinstance(value,dict) and set(value)=={'verbatim_reference'}:
                result=projected
                for part in value['verbatim_reference'][2:].split('/'):
                    part=part.replace('~1','/').replace('~0','~');result=result[int(part)]if isinstance(result,list)else result[part]
                return expand(result)
            if isinstance(value,dict):return {k:expand(v)for k,v in value.items()}
            if isinstance(value,list):return [expand(v)for v in value]
            return value
        self.assertEqual(expand(projected),raw)

    def test_columnar_records_keep_null_and_missing_separate(self):
        values=[{'id':'a','n':None},{'id':'b','n':0}]
        wire=Presentation.columnar(values)
        self.assertEqual([dict(zip(wire['record_keys'],v)) for v in wire['record_values']],values)
        missing=[{'id':'a','n':None},{'id':'b'}]
        self.assertEqual(Presentation.columnar(missing),missing)

    def test_native_json_fields_include_full_code_and_original_serialization_is_untouched(self):
        code='SELECT SUM(units) FROM dbo.Items WHERE note = '+repr('addr1')+';'
        native=json.dumps({'model':{'tables':[{'name':'Items','expression':code,'documentation':'x'*400}]}})
        context={'retained_native_definitions':[{'metadata':{'content':native}}]};before=deepcopy(context);captured={}
        def complete(**kw):captured.update(kw);return {'content':[]}
        Presentation(context,{},'instructions').complete(Mock(complete=complete),system='',messages=[],tools=[])
        self.assertIn('native_json',captured['system'])
        self.assertIn(code,captured['system'])
        self.assertEqual(context,before)

    def test_later_evidence_address_is_usable_without_rewriting_native_rows(self):
        p=Presentation({}, {}, 'instructions');identity='case-evidence:'+'b'*64
        result=p.project({'evidence_id':identity,'result':{'rows':[{'key':identity}]}})
        self.assertEqual(result['result']['rows'][0]['key'],identity)
        self.assertEqual(p.restore({'id':result['evidence_id']})['id'],identity)


if __name__=='__main__':unittest.main()
