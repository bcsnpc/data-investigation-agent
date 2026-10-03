"""Prefer the most specific failure the surface can give; never upgrade a failure."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import read_xmla_failure as xmla
from investigator.process_debugging import Probe, refine_failure, vertical

ROOT = Path(__file__).resolve().parents[1]
GENERIC = {'interface': 'FIRST', 'codes': ['GenericError'], 'specificity': 'GENERIC'}


class Detail:
    def __init__(self, detail=None, error=None):
        self.detail, self.error, self.calls = detail, error, 0

    def failure_detail(self, layer, probe):
        self.calls += 1
        if self.error:
            raise self.error
        return self.detail


def failed(failure=GENERIC):
    return Probe('UNAVAILABLE', 'top', reason='Generic reason.', query='Q', failure=dict(failure))


class RefinementTests(unittest.TestCase):
    def test_generic_failure_is_replaced_by_the_most_specific_one_obtained(self):
        adapter = Detail({'interface': 'SECOND', 'specificity': 'SPECIFIC', 'codes': ['AADSTS50173']})
        probe = refine_failure(adapter, {'failure_detail'}, {'id': 'top'}, failed())
        self.assertEqual(probe.status, 'UNAVAILABLE')  # never upgraded
        self.assertIn('AADSTS50173', probe.reason)
        self.assertIn('Generic reason.', probe.reason)  # the generic failure is kept, not erased
        self.assertEqual(probe.failure['refinement'], 'OBTAINED')
        self.assertEqual(probe.failure['codes'], ['GenericError'])
        self.assertEqual(probe.failure['most_specific']['codes'], ['AADSTS50173'])

    def test_refinement_is_attempted_only_for_generic_failures(self):
        adapter = Detail({'specificity': 'SPECIFIC', 'codes': ['X']})
        for failure in ({'specificity': 'SPECIFIC', 'codes': ['A']}, {'specificity': 'UNCERTAIN'}, None):
            probe = Probe('UNAVAILABLE', 'top', failure=failure)
            self.assertIs(refine_failure(adapter, {'failure_detail'}, {}, probe), probe)
        observed = Probe('OBSERVED', 'top', evidence={'id':'observed'},value=0, failure=dict(GENERIC))
        self.assertIs(refine_failure(adapter, {'failure_detail'}, {}, observed), observed)
        self.assertEqual(adapter.calls, 0)

    def test_undeclared_capability_is_recorded_not_called(self):
        adapter = Detail({'specificity': 'SPECIFIC', 'codes': ['X']})
        probe = refine_failure(adapter, set(), {}, failed())
        self.assertEqual((adapter.calls, probe.failure['refinement']), (0, 'NOT_DECLARED'))

    def test_second_interface_failure_keeps_the_generic_failure(self):
        probe = refine_failure(Detail(error=RuntimeError('boom')), {'failure_detail'}, {}, failed())
        self.assertEqual((probe.reason, probe.failure['refinement']), ('Generic reason.', 'FAILED'))
        self.assertEqual(probe.failure['refinement_error_type'], 'RuntimeError')

    def test_second_interface_without_codes_is_not_a_refinement(self):
        for detail in (None, {'specificity': 'GENERIC', 'codes': []}, {'specificity': 'SPECIFIC', 'codes': []}):
            probe = refine_failure(Detail(detail), {'failure_detail'}, {}, failed())
            self.assertEqual(probe.failure['refinement'], 'NO_SPECIFIC_FAILURE')
            self.assertEqual(probe.reason, 'Generic reason.')


class ProcedureTests(unittest.TestCase):
    class Adapter(Detail):
        def capabilities(self):
            return {'resolve_measure_path', 'evaluate_scoped_quantity', 'failure_detail'}

        def resolve_path(self, measure):
            return {'layers': [{'id': 'top'}], 'stopped_by': 'REACHED', 'evidence': {'id': 'path', 'tool': 'context'}}

        def evaluate(self, layer, measure, scope):
            return failed()

    def test_specific_failure_reaches_the_baseline_reason_and_both_outputs(self):
        adapter = self.Adapter({'interface': 'SECOND', 'specificity': 'SPECIFIC', 'codes': ['AADSTS50173']})
        result = vertical(adapter, 'measure', {})
        self.assertIn('AADSTS50173', result['support']['process']['baseline_above']['reason'])
        for output in ('business_output', 'technical_output'):
            self.assertEqual(result[output]['failures'][0]['specific_codes'], ['AADSTS50173'])
            self.assertEqual(result[output]['failures'][0]['generic_codes'], ['GenericError'])


class Store:
    """A real file-backed SQLite store, as receipts need."""
    def __init__(self):
        self.path = os.path.join(tempfile.mkdtemp(), 'receipts.sqlite')

    def connect(self):
        return sqlite3.connect(self.path)


class AdapterTests(unittest.TestCase):
    def adapter(self, detail=None, store=None):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        model = {'id': 'm', 'revision': 1, 'context_id': 'c', 'workspace': 'ws', 'native_id': 'n', 'name': 'Model',
                 'context': {}}
        return MicrosoftProcessAdapter(store or Store(), {'fabric': {}}, model, None, None, read_failure_detail=detail)

    def evaluate(self, result):
        adapter = self.adapter()
        with patch('investigator.adapters.microsoft_process.assets', return_value=[{'id': 'q', 'name': 'Q'}]), \
             patch('investigator.adapters.microsoft_process.MicrosoftProcessAdapter._native_read', return_value=result), \
             patch('investigator.flexible_tools.build', return_value={}):
            return adapter.evaluate({'id': 'top', 'kind': 'presentation'}, 'q', {})

    def test_masked_service_error_is_classified_generic(self):
        probe = self.evaluate({'id': 'r', 'status': 'FAILED', 'result': {'error_type': 'NativeRejected',
                               'http_status': 400, 'service_error_code': 'DatasetExecuteQueriesError'}})
        self.assertEqual((probe.status, probe.failure['specificity'], probe.failure['codes']),
                         ('UNAVAILABLE', 'GENERIC', ['DatasetExecuteQueriesError']))
        self.assertEqual(probe.failure['receipt_id'], 'r')

    def test_uncertain_and_other_failures_are_not_generic(self):
        self.assertEqual(self.evaluate({'id': 'r', 'status': 'INTERRUPTED', 'result': {'error_type': 'TimeoutError'}})
                         .failure['specificity'], 'UNCERTAIN')
        self.assertEqual(self.evaluate({'id': 'r', 'status': 'FAILED', 'result': {'service_error_code': 'Other'}})
                         .failure['specificity'], 'SPECIFIC')

    def test_capability_follows_the_configured_second_interface(self):
        self.assertIn('failure_detail', self.adapter(lambda r: {}).capabilities())
        self.assertNotIn('failure_detail', self.adapter().capabilities())
        self.assertIn('failure_detail', self.adapter().capability_gaps())

    def test_failure_detail_addresses_the_model_by_discovered_names(self):
        seen = {}
        def read(request):
            seen.update(request)
            return {'status': 'ERROR_CAPTURED', 'codes': ['AADSTS50173']}
        adapter = self.adapter(read)
        context = {'assets': [{'kind': 'Workspace', 'id': 'fabric://ws', 'name': 'Workspace Name'}]}
        with patch('investigator.adapters.microsoft_process.context_search.latest', return_value=context):
            detail = adapter.failure_detail({'id': 'top'}, failed())
        self.assertEqual(seen, {'workspace_name': 'Workspace Name', 'model_name': 'Model', 'query': 'Q'})
        self.assertEqual((detail['interface'], detail['specificity'], detail['codes']), ('XMLA', 'SPECIFIC', ['AADSTS50173']))
        self.assertTrue(detail['receipt_id'])

    def test_unaddressable_model_is_not_a_refinement(self):
        adapter = self.adapter(lambda r: self.fail('no call expected'))
        with patch('investigator.adapters.microsoft_process.context_search.latest', return_value={'assets': []}):
            self.assertEqual(adapter.failure_detail({'id': 'top'}, failed())['specificity'], 'GENERIC')


class SealingTests(unittest.TestCase):
    """Specific codes are evidence from the interface that reported them: a sealed receipt."""
    CONTEXT = {'assets': [{'kind': 'Workspace', 'id': 'fabric://ws', 'name': 'Workspace Name'}]}

    def detail(self, read, store):
        adapter = AdapterTests().adapter(read, store)
        with patch('investigator.adapters.microsoft_process.context_search.latest', return_value=self.CONTEXT):
            return adapter.failure_detail({'id': 'top'}, failed(dict(GENERIC, receipt_id='generic-receipt')))

    def row(self, store, identity):
        with store.connect() as db:
            status, request, result = db.execute('SELECT status,request,result FROM failure_details WHERE id=?',
                                                 (identity,)).fetchone()
        return status, json.loads(request), json.loads(result)

    def test_specific_codes_are_sealed_in_their_own_receipt(self):
        from investigator.receipt_integrity import verify
        store = Store()
        detail = self.detail(lambda r: {'status': 'ERROR_CAPTURED', 'stage': 'connect', 'codes': ['AADSTS50173'],
                                        'message': 'must never be stored'}, store)
        status, request, result = self.row(store, detail['receipt_id'])
        self.assertEqual(status, 'COMPLETED')
        self.assertEqual(result['codes'], ['AADSTS50173'])
        self.assertNotIn('must never be stored', json.dumps(result))
        self.assertEqual((request['interface'], request['refines_receipt_id']), ('XMLA', 'generic-receipt'))
        with store.connect() as db:
            self.assertEqual(verify(db, 'failure_detail', detail['receipt_id'])['state'], 'SEALED')

    def test_tampering_with_the_sealed_codes_is_detected(self):
        from investigator.receipt_integrity import verify
        from investigator.onboarding import Conflict
        store = Store()
        detail = self.detail(lambda r: {'status': 'ERROR_CAPTURED', 'codes': ['AADSTS50173']}, store)
        with store.connect() as db:
            db.execute('UPDATE failure_details SET result=? WHERE id=?',
                       (json.dumps({'codes': ['SomethingElse']}), detail['receipt_id']))
        with store.connect() as db, self.assertRaises(Conflict):
            verify(db, 'failure_detail', detail['receipt_id'])

    def test_unavailable_interface_still_leaves_a_sealed_failed_receipt(self):
        from investigator.receipt_integrity import verify
        store = Store()
        def read(request):
            raise RuntimeError('client missing')
        detail = self.detail(read, store)
        status, _, result = self.row(store, detail['receipt_id'])
        self.assertEqual((status, result['error_type'], detail['specificity']), ('FAILED', 'RuntimeError', 'GENERIC'))
        with store.connect() as db:
            self.assertEqual(verify(db, 'failure_detail', detail['receipt_id'])['state'], 'SEALED')

    def test_request_is_recorded_before_the_interface_is_called(self):
        store = Store()
        def read(request):
            with store.connect() as db:
                self.assertEqual(db.execute("SELECT status FROM failure_details").fetchone()[0], 'RUNNING')
            return {'status': 'NO_ERROR', 'codes': []}
        self.detail(read, store)

    def test_output_entry_points_at_the_sealed_receipt(self):
        from investigator.process_debugging import _failure_entry
        probe = refine_failure(Detail({'interface': 'XMLA', 'specificity': 'SPECIFIC', 'codes': ['AADSTS50173'],
                                       'receipt_id': 'sealed-1'}), {'failure_detail'}, {}, failed())
        self.assertEqual(_failure_entry(probe)['specific_receipt_id'], 'sealed-1')


class XmlaTransportTests(unittest.TestCase):
    MESSAGE = ('The database operation failed. AADSTS50173: The provided grant has expired due to it being revoked; '
               'AdalGrantHasExpiredDueToPasswordChangeErrorCode. Error 0xc1450012 while reading row 12345 of Secret.')

    def test_only_codes_leave_the_error_text(self):
        codes = xmla.extract_codes(self.MESSAGE)
        self.assertEqual(codes, ['AADSTS50173', 'AdalGrantHasExpiredDueToPasswordChangeErrorCode', '0xC1450012'])
        self.assertNotIn('12345', json.dumps(codes))
        self.assertNotIn('Secret', json.dumps(codes))
        self.assertEqual(xmla.extract_codes(None), [])

    def test_read_returns_codes_and_never_the_message(self):
        library = ROOT/'.local'/'test-adomd'/'Adomd.dll'
        request = {'library': '.local/test-adomd/Adomd.dll', 'workspace_name': 'W', 'model_name': 'M', 'query': 'Q'}
        def run(command, input, **kwargs):
            sent = json.loads(input)
            self.assertEqual(sorted(sent), ['access_token', 'library', 'model_name', 'query', 'workspace_name'])
            return subprocess.CompletedProcess(command, 1, json.dumps(
                {'status': 'ERROR_CAPTURED', 'stage': 'connect', 'error_type': 'AdomdErrorResponseException',
                 'message': self.MESSAGE}), '')
        with patch.object(xmla.Path, 'is_file', return_value=True):
            result = xmla.read(request, lambda r: 'token', run=run)
        self.assertEqual(result['codes'][0], 'AADSTS50173')
        self.assertNotIn('message', result)
        self.assertNotIn('Secret', json.dumps(result))

    def test_library_outside_local_is_refused(self):
        request = {'library': 'scripts/evil.dll', 'workspace_name': 'W', 'model_name': 'M', 'query': 'Q'}
        self.assertEqual(xmla.read(request, lambda r: self.fail('no token'), run=self.fail)['stage'], 'library')

    def test_script_names_workspace_and_model_and_accepts_fixed_fields(self):
        source = (ROOT/'infra/scripts/Read-XmlaFailure.ps1').read_text(encoding='utf-8-sig')
        self.assertIn("'access_token,library,model_name,query,workspace_name'", source)
        self.assertIn('Initial Catalog=', source)
        self.assertIn("'workspace_name','model_name','query','library'", source)

    def test_library_is_loaded_lazily_and_client_failures_are_not_surface_errors(self):
        source = (ROOT/'infra/scripts/Read-XmlaFailure.ps1').read_text(encoding='utf-8-sig')
        self.assertNotIn('Add-Type -Path', source)
        self.assertIn('Assembly]::LoadFrom', source)
        self.assertIn("$stage='client'", source)
        self.assertIn("{'ERROR_CAPTURED'}else{'UNAVAILABLE'}", source)


if __name__ == '__main__':
    unittest.main()
