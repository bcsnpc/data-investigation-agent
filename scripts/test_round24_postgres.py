import unittest
from unittest.mock import Mock,patch
from investigator.postgres_connection import ObservedConnection,dropped_connection,connection_timeout
class PostgreSQLTests(unittest.TestCase):
 def test_closed_socket_is_detected_without_sending_statement_and_has_idle_time(self):
  raw=Mock();raw.closed=True;conn=ObservedConnection(raw,clock=Mock(side_effect=[0,42,43,43]))
  with self.assertRaisesRegex(ConnectionError,'STALE_SOCKET')as error:conn.execute('SELECT 1')
  raw.execute.assert_not_called();self.assertEqual(error.exception.postgres_connection_timing['idle_before_request_seconds'],42)
  self.assertTrue(dropped_connection(error.exception))
 def test_real_timeout_subclass_is_retryable_but_auth_is_not(self):
  from psycopg.errors import ConnectionTimeout,InvalidPassword
  self.assertTrue(connection_timeout(ConnectionTimeout('connection timeout expired')))
  self.assertTrue(dropped_connection(ConnectionTimeout('connection timeout expired')))
  self.assertFalse(dropped_connection(InvalidPassword('authentication failed')))
 def test_external_request_is_refused_until_transaction_closed(self):
  from investigator.shared_state import TRANSACTION_ACTIVE
  from investigator.live_gateway import _network_unlocked,GatewayDenied
  token=TRANSACTION_ACTIVE.set(True)
  try:
   with patch('investigator.live_gateway._deny',side_effect=GatewayDenied('NETWORK_DURING_SHARED_STATE_TRANSACTION'))as denied,self.assertRaises(GatewayDenied):_network_unlocked()
   denied.assert_called_once_with('NETWORK_DURING_SHARED_STATE_TRANSACTION')
  finally:TRANSACTION_ACTIVE.reset(token)
  _network_unlocked()
if __name__=='__main__':unittest.main()

