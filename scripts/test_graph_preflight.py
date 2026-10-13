import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch

from investigator.cloud_preflight import operator_graph_coverage


class GraphPreflightTests(unittest.TestCase):
    def graph(self):
        return {'nodes':[{'id':'n','kind':'TABLE','confidence':'DECLARED','properties':{'definition':'private definition'}}],
                'edges':[],'truncated':False}

    def test_operator_summary_exact_estate_bound_no_raw_graph(self):
        repo=Mock();repo.records.return_value=self.graph()
        result=operator_graph_coverage('selected-estate',repository=repo)
        repo.records.assert_called_once_with('selected-estate',limit=10000)
        self.assertEqual(result['nodes_by_kind'],{'TABLE':1})
        self.assertEqual(result['status'],'AVAILABLE')
        self.assertFalse(result['readiness_evidence'])
        self.assertNotIn('private definition',json.dumps(result))
        self.assertNotIn('nodes',result)

    def test_empty_unavailable_owners_and_truncation_explicit(self):
        repo=Mock();repo.records.return_value={'nodes':[],'edges':[],'truncated':False}
        self.assertEqual(operator_graph_coverage('e',repository=repo)['reason'],'NO_RETAINED_GRAPH')
        graph=self.graph();graph['unavailable_owners']={'owner':{'reason':'GRAPH_OWNER_NOT_VISIBLE'}}
        repo.records.return_value=graph
        self.assertEqual(operator_graph_coverage('e',repository=repo)['status'],'PARTIAL')
        graph['truncated']=True
        result=operator_graph_coverage('e',repository=repo)
        self.assertEqual(result['status'],'TRUNCATED');self.assertTrue(result['counts_are_partial'])
        self.assertIn('owner',result['unavailable_owners'])

    def test_no_configuration_and_failed_read_do_not_claim_coverage_or_leak(self):
        with patch('investigator.shared_state.configured_state',return_value=None):
            self.assertEqual(operator_graph_coverage('e')['reason'],'SHARED_GRAPH_STATE_NOT_CONFIGURED')
        repo=Mock();repo.records.side_effect=RuntimeError('password=do-not-log')
        result=operator_graph_coverage('e',repository=repo)
        self.assertEqual(result['status'],'UNAVAILABLE');self.assertEqual(result['error_type'],'RuntimeError')
        self.assertNotIn('do-not-log',json.dumps(result))

    def test_cli_optional_summary_does_not_change_checks_status_or_exit(self):
        from preflight_installation import main
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);platform=root/'platform.json';platform.write_text('{}')
            base=['--manifest',str(Path(__file__).parents[1]/'infra/estates/fixture.json'),'--platform',str(platform)]
            reports=[]
            with patch('builtins.print'),patch('preflight_installation.operator_graph_coverage',return_value={'status':'AVAILABLE'})as coverage:
                for i,args in enumerate(([],['--graph-coverage-estate','exact-operator-estate'])):
                    output=root/f'{i}.json'
                    self.assertEqual(main([*base,'--output',str(output),*args]),2)
                    reports.append(json.loads(output.read_text()))
                coverage.assert_called_once_with('exact-operator-estate')
            self.assertEqual(reports[0]['checks'],reports[1]['checks'])
            self.assertEqual(reports[0]['status'],reports[1]['status'])
            self.assertNotIn('graph_coverage',reports[0])
            self.assertEqual(reports[1]['control_operations'],1)
            self.assertEqual(reports[1]['estate_reads'],0)

    def test_invalid_operator_scope_refuses_before_read(self):
        repo=Mock()
        for estate in ('','  ','line\nbreak',None):
            with self.assertRaises(ValueError):operator_graph_coverage(estate,repository=repo)
        repo.records.assert_not_called()


if __name__=='__main__':unittest.main()
