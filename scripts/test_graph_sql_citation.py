import copy,hashlib,unittest
from investigator.adapters.graph_sql_citation import review,statements

CODE='CREATE PROCEDURE [out].[build]\nAS\nBEGIN\n DELETE FROM [out].[facts];\n INSERT INTO [out].[facts] (id,amount)\n SELECT s.id,s.amount FROM [src].[facts] s;\nEND;'
class CitationTests(unittest.TestCase):
    def test_all_original_live_proposals_preserve_the_nineteen_inadequate_quotes(self):
        import json
        from pathlib import Path
        data=json.loads((Path(__file__).parent/'testdata/graph-interpreter-citation-proposals.json').read_bytes())
        total=adequate=0
        for case in data['cases']:
            task={k:case[k]for k in ('code','definition_hash')};task['source_id']='retained-case-'+str(case['task'])
            labels=sorted({p[k]for p in case['proposals']for k in ('source_label','target_label')})
            task['nodes']=[{'id':label,'label':label}for label in labels]
            edges=[{'id':str(i),'kind':p['kind'],'source':p['source_label'],'target':p['target_label'],
                'provenance':{'definition_hash':task['definition_hash'],'source_id':task['source_id'],'span':p['span']},
                'properties':{'quote':p['quote']}}for i,p in enumerate(case['proposals'])]
            before=copy.deepcopy(edges);rows=review(task,edges);self.assertEqual(edges,before)
            total+=len(rows);adequate+=sum(r['original_quote_adequate']for r in rows)
        self.assertEqual((total,adequate,total-adequate),(26,7,19))

    def sample(self):
        start=CODE.index(' SELECT');end=CODE.index('\nEND;')
        task={'code':CODE,'definition_hash':hashlib.sha256(CODE.encode()).hexdigest(),'source_id':'retained',
            'nodes':[{'id':'source','label':'src.facts.amount'},{'id':'target','label':'out.facts.amount'}]}
        edge={'id':'proposal','kind':'COPIED_TO','source':'source','target':'target',
            'provenance':{'definition_hash':task['definition_hash'],'source_id':'retained','span':{'kind':'TEXT','start':start,'end':end}},
            'properties':{'quote':CODE[start:end]}}
        return task,edge
    def test_derived_statement_does_not_rewrite_original_incomplete_quote(self):
        task,edge=self.sample();before=copy.deepcopy(edge);row=review(task,[edge])[0]
        self.assertFalse(row['original_quote_adequate']);self.assertEqual(edge,before)
        s=row['derived_statement'];self.assertEqual(task['code'][s['start']:s['end']],s['quote'])
        self.assertIn('INSERT',s['quote']);self.assertFalse(row['execution_established'])
    def test_full_statement_quote_passes(self):
        task,edge=self.sample();s,_=statements(CODE)
        edge['provenance']['span']={'kind':'TEXT','start':s['start'],'end':s['end']};edge['properties']['quote']=s['quote']
        self.assertTrue(review(task,[edge])[0]['original_quote_adequate'])
    def test_wrong_column_mapping_refuses(self):
        task,edge=self.sample();task['nodes'][1]['label']='out.facts.id'
        with self.assertRaisesRegex(ValueError,'MAPPING_NOT_SUPPORTED'):review(task,[edge])
    def test_span_cannot_use_python_negative_or_clipped_offsets(self):
        for start,end in ((-1,len(CODE)),(0,len(CODE)+1),(False,1)):
            task,edge=self.sample();edge['provenance']['span'].update(start=start,end=end)
            edge['properties']['quote']=CODE[start:end]
            with self.assertRaisesRegex(ValueError,'ORIGINAL_QUOTE_DIFFERS'):review(task,[edge])
    def test_unqualified_join_column_and_unknown_alias_refuse(self):
        for query in ('INSERT INTO out.facts (id) SELECT id FROM src.a a JOIN src.b b ON a.id=b.id;',
                      'INSERT INTO out.facts (id) SELECT z.id FROM src.a a;'):
            with self.assertRaisesRegex(ValueError,'AMBIGUOUS|UNRESOLVED'):statements(query)
    def test_dynamic_procedure_is_not_interpreted(self):
        with self.assertRaises(ValueError):statements('CREATE PROCEDURE x AS BEGIN EXEC(@sql); END;')

if __name__=='__main__':unittest.main()
