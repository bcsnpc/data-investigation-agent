"""Offline expiry, short-connection and complete-catalog regressions."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock
import unittest
from investigator.postgres_connection import database_token


class ConnectionTests(unittest.TestCase):
    def test_real_psycopg_connection_timeout_subclass_retries_acquisition_once(self):
        from investigator.postgres_connection import connect,connection_timeout
        from psycopg.errors import ConnectionTimeout,InvalidPassword
        failure=ConnectionTimeout('connection timeout expired');native=object()
        connector=Mock(side_effect=[failure,native]);sleep=Mock()
        self.assertIs(connect(connector=connector,sleep=sleep,host='synthetic'),native)
        self.assertEqual(connector.call_count,2);sleep.assert_called_once_with(30)
        self.assertEqual(failure.postgres_connection_timing['operation'],'connect')
        self.assertIsNone(failure.postgres_connection_timing['idle_before_request_seconds'])
        self.assertFalse(connection_timeout(InvalidPassword('password authentication failed')))
        persistent=Mock(side_effect=ConnectionTimeout('connection timeout expired'))
        with self.assertRaises(ConnectionTimeout) as caught:connect(connector=persistent,sleep=Mock())
        self.assertEqual(persistent.call_count,2);self.assertEqual(caught.exception.postgres_connect_attempts,2)

    def test_settlement_reconnects_once_after_lost_commit_without_double_charging(self):
        from investigator.shared_state import SharedState
        from unittest.mock import patch
        with TemporaryDirectory()as folder:
            storage=SharedState.offline(Path(folder)/'state.sqlite');storage.migrate()
            storage.import_accounts('seed',{'accounts':[{'identity':'money','unit':'MICRODOLLARS','ceiling':'100','protected':'0','opening':'0','violated':False}],'provenance':{'source':'synthetic','owner_approval':'test'}})
            storage.reserve('money','same-reservation','worker',50)
            retry=SharedState(lambda:None,backend='postgresql',mode='offline');calls=[]
            def commit_then_drop(*args,**kwargs):
                calls.append(1);result=storage.settle(*args,**kwargs)
                if len(calls)==1:raise ConnectionError('synthetic lost commit response')
                return result
            with patch.object(retry,'_settle_once',side_effect=commit_then_drop),patch('time.sleep')as sleep:
                result=retry.settle('money','same-reservation','worker',20,full_snapshot=False)
            self.assertEqual(result['charged'],'20');self.assertEqual(len(calls),2)
            self.assertEqual(len(storage.snapshot('money')['reservations']),1)
            self.assertEqual(retry.connection_failures[0]['operation'],'RESERVATION_SETTLEMENT')
            sleep.assert_called_once_with(30)
    def test_safe_reconnect_is_bounded_and_never_retries_auth_or_sql_errors(self):
        from investigator.shared_state import SharedState
        from unittest.mock import patch
        retry=SharedState(lambda:None,backend='postgresql',mode='offline')
        for error,count in ((ConnectionError('lost'),2),(ValueError('invalid SQL or policy'),1)):
            call=Mock(side_effect=error)
            with self.subTest(error=type(error).__name__),patch('time.sleep'),self.assertRaises(type(error)):
                retry._retry_connection_operation('READ_TRANSACTION',call)
            self.assertEqual(call.call_count,count)
    def test_expiring_token_is_renewed_on_same_identity_audience(self):
        factory=Mock();one=Mock();two=Mock()
        one.__enter__=Mock(return_value=one);one.__exit__=Mock(return_value=False)
        two.__enter__=Mock(return_value=two);two.__exit__=Mock(return_value=False)
        one.get_token.return_value=SimpleNamespace(token='synthetic-expiring',expires_on=110)
        two.get_token.return_value=SimpleNamespace(token='synthetic-renewed',expires_on=5000)
        factory.side_effect=[one,two]
        self.assertEqual(database_token(factory,'same-id',clock=lambda:100),'synthetic-renewed')
        self.assertEqual([c.kwargs for c in factory.call_args_list],[{'client_id':'same-id'}]*2)
        for client in (one,two):client.get_token.assert_called_once_with('https://ossrdbms-aad.database.windows.net/.default')
    def test_two_unusable_tokens_do_not_reach_a_database(self):
        factory=Mock();value=Mock();value.__enter__=Mock(return_value=value);value.__exit__=Mock(return_value=False)
        value.get_token.return_value=SimpleNamespace(token='synthetic-expired',expires_on=1);factory.return_value=value
        with self.assertRaisesRegex(RuntimeError,'RENEWAL_UNAVAILABLE'):database_token(factory,'same',clock=lambda:100)
        self.assertEqual(factory.call_count,2)
    def test_shared_transactions_close_instead_of_holding_idle_socket(self):
        from investigator.shared_state import SharedState
        with TemporaryDirectory() as folder:
            state=SharedState.offline(Path(folder)/'state.sqlite')
            raw=state.connector;opened=[]
            def connect():
                result=raw();opened.append(result);return result
            state.connector=connect
            with state.transaction(_read_only=True) as db:db.execute('SELECT 1')
            with state.transaction(_read_only=True) as db:db.execute('SELECT 1')
            self.assertEqual(len(opened),2)
            import sqlite3
            for db in opened:
                with self.assertRaises(sqlite3.ProgrammingError):db.execute('SELECT 1')


class CatalogTests(unittest.TestCase):
    def test_intake_catalog_is_not_limited_to_a_200_node_ticket_path(self):
        from investigator.estate_graph_api import GraphAPI
        from investigator.estate_graph_repository import GraphRepository
        from investigator.shared_state import SharedState
        from investigator.live_gateway import Gateway
        from investigator import estate_graph_contract as c
        from investigator.guided_intake import Catalog
        from test_estate_graph import proof,T0
        with TemporaryDirectory() as folder:
            state=SharedState.offline(Path(folder)/'state.sqlite');repository=GraphRepository(state);repository.migrate()
            nodes=[c.node('report-'+str(i),'owner','REPORT','Report '+str(i),proof()) for i in range(1144)]
            repository.replace({'estate':'estate','owner':'owner','definition_hash':'a'*64,
                                'observed_at':T0,'nodes':nodes,'edges':[]})
            allowed=[n['id'] for n in nodes]
            gateway=Gateway({'version':1,'live_enabled':False,'identities':{'reader':{'role':'reader','graph':{'estate':allowed}}}})
            graph=GraphAPI(repository,gateway,identity='reader',estate='estate',allowed_objects=allowed)
            self.assertEqual(len(Catalog.from_graph(graph).reports()),1144)
            self.assertEqual(graph.max_nodes,100)

    def test_engineer_reply_is_scoped_attributed_and_cannot_become_native_job_fact(self):
        from investigator.facts_ledger import FactLedger,fact
        from investigator.shared_state import SharedState
        from investigator.estate_graph_repository import GraphRepository
        from test_estate_graph import graph,T0
        with TemporaryDirectory() as folder:
            state=SharedState.offline(Path(folder)/'state.sqlite');repo=GraphRepository(state);repo.migrate();repo.replace(graph())
            ledger=FactLedger(state);scope={'report':'report','visual':'visual'}
            ledger.record_engineer_reply('estate',case_id='case',subject='visual',author='Synthetic engineer',
                text='The selected visual maps to the retained measure.',scope=scope,at=T0)
            replies=ledger.engineer_replies('estate','visual',scope)
            self.assertEqual(len(replies),1);self.assertEqual(replies[0]['source'],'HUMAN_REPLY')
            self.assertEqual(ledger.engineer_replies('estate','visual',{'visual':'other'}),[])
            value=replies[0];value['kind']='JOB_RUN'
            with self.assertRaisesRegex(ValueError,'NOT_RUNTIME_PROOF'):fact(value)


if __name__=='__main__':unittest.main()
