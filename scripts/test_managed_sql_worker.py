import io
import json
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import managed_sql_worker as worker

AUTH={'mode':'managed_identity','client_id':'11111111-1111-1111-1111-111111111111',
      'principal_id':'22222222-2222-2222-2222-222222222222','tenant_id':'33333333-3333-3333-3333-333333333333'}


class Cursor:
    def __init__(self, permission=0, rows=None, extra=False):
        self.permission=permission; self.quantity=rows if rows is not None else [(7,)]
        self.calls=[]; self.extra=extra; self.quantity_active=False
    def execute(self, query, *values):
        self.calls.append((query,values)); self.quantity_active=False
        if query == worker.IDENTITY: self.rows=[('reader','synthetic')]
        elif 'fn_my_permissions' in query: self.rows=[(self.permission,)]
        else:
            self.rows=list(self.quantity); self.quantity_active=True
            self.description=[('value',int)]
            if '__surface_identity' in query:
                self.description += [(key,str) for key in ('__surface_identity','__surface_object','__surface_engine')]
        return self
    def fetchone(self):return self.rows.pop(0) if self.rows else None
    def nextset(self):return self.extra and self.quantity_active
    def close(self):pass


class Tests(unittest.TestCase):
    def setUp(self):
        self.payload={'server':'synthetic.database.windows.net','database':'synthetic','authentication':AUTH,
                      'query':'SELECT value FROM dbo.synthetic','read_only_objects':['dbo.synthetic'],
                      'max_rows':2,'result_columns':['value']}
        self.admit=Mock(side_effect=lambda value:{**value,'require_read_only':True})
        self.control=Mock()
        self.gateway=patch.dict(sys.modules,{'investigator.live_gateway':SimpleNamespace(
            authorize_sql_payload=self.admit,authorize_sql_control=self.control)})
        self.gateway.start();self.addCleanup(self.gateway.stop)
        self.tokens=Mock();self.tokens.get_token.return_value='memory-token'

    def run_worker(self, cursor=None, **kwargs):
        self.cursor=cursor or Cursor()
        self.connection=Mock();self.connection.cursor.return_value=self.cursor
        self.connect=Mock(return_value=self.connection)
        return worker.execute(self.payload,connect=self.connect,tokens=self.tokens,**kwargs)

    def test_four_physical_requests_guards_and_memory_only_token(self):
        sink=io.StringIO()
        result=self.run_worker(protocol=worker.Protocol(True,io.StringIO('ALLOW\n'*4),sink))
        events=[json.loads(row) for row in sink.getvalue().splitlines()]
        self.assertEqual([e['kind'] for e in events if e['physical_read']=='REQUEST'],
                         ['sql_identity','sql_database_permissions','sql_object_permissions','sql_quantity'])
        self.assertTrue(result['read_only_verified']);self.assertEqual(result['rows'],[{'value':'7'}])
        self.assertNotIn('memory-token',sink.getvalue()+json.dumps(result))
        self.assertIn('ApplicationIntent=ReadOnly',self.connect.call_args.args[0])
        self.assertEqual(self.connect.call_args.kwargs['attrs_before'][101],1)
        self.assertEqual(self.connection.timeout,30)
        self.connection.close.assert_called_once()

    def test_established_guard_reuse_issues_only_identity_and_quantity(self):
        self.run_worker(protocol=worker.Protocol(True,io.StringIO('ALLOW\nREUSE\nREUSE\nALLOW\n'),io.StringIO()))
        self.assertEqual(len(self.cursor.calls),2)

    def test_permissions_refuse_before_quantity(self):
        with self.assertRaisesRegex(ValueError,'permission guard'):
            self.run_worker(Cursor(permission=1))
        self.assertEqual(len(self.cursor.calls),2)

    def test_gateway_refusal_precedes_token_and_connection(self):
        self.admit.side_effect=ValueError('Denied')
        with self.assertRaisesRegex(ValueError,'Denied'):self.run_worker()
        self.tokens.get_token.assert_not_called();self.connect.assert_not_called()

    def test_unmetered_still_establishes_all_guards(self):
        self.run_worker();self.assertEqual(len(self.cursor.calls),4)

    def test_no_row_or_extra_result_overflow(self):
        for cursor in (Cursor(rows=[(1,),(2,),(3,)]), Cursor(extra=True)):
            with self.assertRaises(ValueError):self.run_worker(cursor)

    def test_fabric_surface_is_query_bound_and_empty_is_not_attested(self):
        self.payload['surface_kind']='FABRIC_SQL'
        result=self.run_worker(Cursor(rows=[(7,'reader','synthetic','Microsoft SQL Azure')]))
        self.assertEqual(result['surface_report']['identity'],'reader')
        self.assertEqual(result['surface_report_binding'],'VALUE_QUERY')
        self.assertIsNone(self.run_worker(Cursor(rows=[]))['surface_report'])
        with self.assertRaisesRegex(ValueError,'binding'):
            self.run_worker(Cursor(rows=[(7,'reader','other','Microsoft SQL Azure')]))

    def test_controls_are_separate_from_quantities(self):
        self.payload['control_mode']='PREWARM'
        self.assertEqual(self.run_worker()['status'],'CONNECTED')
        self.control.assert_called_once();self.admit.assert_not_called()
        self.connection.cursor.assert_not_called()

    def test_parameter_values_are_bound_not_formatted(self):
        query,args=worker.bind_parameters("SELECT '@p0', [@p0], @@VERSION WHERE x=@p0 OR y=@p0",[
            {'name':'@p0','value':"x';DROP TABLE sensitive--"}])
        self.assertEqual(query,"SELECT '@p0', [@p0], @@VERSION WHERE x=? OR y=?")
        self.assertEqual(len(args),2)
        with self.assertRaises(ValueError):worker.bind_parameters('SELECT @missing',[])

    def test_connection_string_rejects_host_injection(self):
        self.payload['server']='synthetic;UID=admin'
        with self.assertRaises(ValueError):self.run_worker()
        self.tokens.get_token.assert_not_called()

    def test_retained_error_has_stage_errno_and_no_driver_body(self):
        source=io.StringIO(json.dumps(self.payload)+'\n');sink=io.StringIO()
        def fail(payload, **kwargs):
            kwargs['progress']['stage']='connect'
            raise RuntimeError('28000','Private connection details (18456)')
        with patch.object(sys,'stdin',source),patch.object(sys,'stdout',sink),patch.object(worker,'execute',side_effect=fail):
            self.assertEqual(worker.main(),1)
        result=json.loads(sink.getvalue())
        self.assertEqual(result['stage'],'connect');self.assertEqual(result['error_number'],18456)
        self.assertEqual(result['sqlstate'],'28000');self.assertNotIn('Private',sink.getvalue())


if __name__=='__main__':unittest.main()
