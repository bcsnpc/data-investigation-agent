import unittest
from graph_coverage_report import coverage,dependency_observations

def node(id,kind,**props):return {'id':id,'kind':kind,'owner':'owner','confidence':'DECLARED','properties':props}
def edge(id,source,target,confidence='DECLARED',scope='scope'):
    return {'id':id,'source':source,'target':target,'kind':'COMPUTED_FROM','owner':'owner','confidence':confidence,
      'properties':{},'verification':{'state':'CURRENT' if confidence=='VERIFIED' else 'NOT_VERIFIED',
      'evidence_ids':['receipt'] if confidence=='VERIFIED' else [],'scope_hash':scope if confidence=='VERIFIED' else None}}

class CoverageTests(unittest.TestCase):
    def graph(self):return {'nodes':[node('v','VISUAL'),node('c','COLUMN',native_kind='SqlColumn',system_of_record=True)],
      'edges':[edge('e','v','c')]}
    def test_declared_reach_does_not_earn_verification(self):
        g=self.graph();r=coverage(g,g)['baseline_cohort']
        self.assertEqual(r['reaches_declared_source_column'],1);self.assertEqual(r['complete_verified_paths'],0)
    def test_terminal_column_is_not_undeclared_system_of_record(self):
        g=self.graph();g['nodes'][1]['properties'].pop('system_of_record');r=coverage(g,g)['baseline_cohort']
        self.assertEqual(r['reaches_declared_source_column'],0);self.assertEqual(r['reaches_terminal_physical_column'],1)
    def test_unavailable_owner_stops_even_verified_edge(self):
        g=self.graph();g['edges'][0]=edge('e','v','c','VERIFIED');g['unavailable_owners']={'owner':{'reason':'403'}}
        r=coverage(g,g)['baseline_cohort'];self.assertEqual(r['unavailable'],1);self.assertEqual(r['complete_verified_paths'],0)
    def test_all_branches_must_be_verified_and_source_bound(self):
        g=self.graph();g['edges'][0]=edge('e','v','c','VERIFIED');self.assertEqual(coverage(g,g)['baseline_cohort']['complete_verified_paths'],1)
        g['nodes'].append(node('gap','BOUNDARY'));g['edges'].append(edge('x','v','gap'))
        self.assertEqual(coverage(g,g)['baseline_cohort']['complete_verified_paths'],0)
    def test_missing_original_and_new_starts_are_separate(self):
        baseline=self.graph();g=self.graph();g['nodes'][0]['id']='new';g['edges'][0]['source']='new'
        r=coverage(g,baseline);self.assertEqual(r['removed_start_ids'],['v']);self.assertEqual(r['new_start_ids'],['new'])
    def test_info_unavailable_cannot_be_called_collected(self):
        a={'id':'obs','kind':'EngineDependencyMetadata','metadata':{'result':{'status':'UNAVAILABLE','request':{'kind':'CALCULATIONS'},'rows':[],'unknown':'Write required'}}}
        r=dependency_observations([a])[0];self.assertEqual(r['status'],'UNAVAILABLE');self.assertEqual(r['row_count'],0)

if __name__=='__main__':unittest.main()
