import contextlib
import io
import sys
import run_delivery
from email.message import EmailMessage
from unittest.mock import patch,MagicMock
import unittest
from delivery_transports import GithubTransport,SmtpTransport


class TransportTests(unittest.TestCase):
    def test_github_fixed_origin_tls_and_one_request(self):
        with patch('delivery_transports.http.client.HTTPSConnection') as factory:
            conn=factory.return_value;conn.getresponse.return_value.status=201
            conn.getresponse.return_value.read.return_value=b'{"number":1}'
            result=GithubTransport('fixture-token')('POST','/repos/fixture/repo/issues',{'title':'Test','body':'body'})
            self.assertEqual(result,(201,{'number':1}));self.assertEqual(conn.request.call_count,1)
            self.assertEqual(factory.call_args.args,('api.github.com',));self.assertEqual(factory.call_args.kwargs['timeout'],20)
            self.assertTrue(factory.call_args.kwargs['context'].check_hostname);conn.close.assert_called_once()

    def test_github_redirect_never_followed(self):
        with patch('delivery_transports.http.client.HTTPSConnection') as factory:
            conn=factory.return_value;conn.getresponse.return_value.status=302;conn.getresponse.return_value.read.return_value=b'private'
            self.assertEqual(GithubTransport('fixture-token')('POST','/repos/fixture/repo/issues',{}),(302,{}))
            self.assertEqual(conn.request.call_count,1)

    def test_github_timeout_and_response_limit_hold(self):
        for failure in ('timeout','size'):
            with patch('delivery_transports.http.client.HTTPSConnection') as factory:
                conn=factory.return_value
                if failure=='timeout':conn.request.side_effect=TimeoutError('private-token')
                else:conn.getresponse.return_value.read.return_value=b'x'*(2*1024*1024+1)
                with self.assertRaises(RuntimeError) as error:GithubTransport('fixture-token')('POST','/repos/fixture/repo/issues',{})
                self.assertNotIn('private-token',str(error.exception));self.assertEqual(conn.request.call_count,1)
                conn.close.assert_called_once()

    def test_invalid_paths_never_connect(self):
        with patch('delivery_transports.http.client.HTTPSConnection') as factory:
            for path in ('https://other.invalid','//other.invalid','/repos/a/b/issues/1','/repos/a/b/issues\r\nX: y'):
                with self.assertRaises(ValueError):GithubTransport('fixture-token')('POST',path,{})
            factory.assert_not_called()

    def test_smtp_starttls_before_auth_and_single_send(self):
        with patch('delivery_transports.smtplib.SMTP') as factory:
            conn=factory.return_value;conn.send_message.return_value={}
            result=SmtpTransport('smtp.example.invalid',587,'fixture','fixture').send_message(EmailMessage(),from_addr='a@example.invalid',to_addrs=['b@example.invalid'])
            self.assertEqual(result,{})
            self.assertEqual([c[0] for c in conn.method_calls],['ehlo','starttls','ehlo','login','send_message','close'])
            self.assertTrue(conn.starttls.call_args.kwargs['context'].check_hostname)

    def test_smtp_tls_failure_does_not_authenticate_or_retry(self):
        with patch('delivery_transports.smtplib.SMTP') as factory:
            conn=factory.return_value;conn.starttls.side_effect=RuntimeError('private')
            with self.assertRaises(RuntimeError):SmtpTransport('smtp.example.invalid',587,'fixture','fixture').send_message(EmailMessage(),from_addr='a',to_addrs=['b'])
            conn.login.assert_not_called();conn.send_message.assert_not_called();conn.close.assert_called_once()

    def test_smtp_implicit_tls(self):
        with patch('delivery_transports.smtplib.SMTP_SSL') as factory:
            conn=factory.return_value;conn.send_message.return_value={'b':(550,b'refused')}
            result=SmtpTransport('smtp.example.invalid',465,'fixture','fixture').send_message(EmailMessage(),from_addr='a',to_addrs=['b'])
            self.assertIn('b',result);self.assertTrue(factory.call_args.kwargs['context'].check_hostname)
            self.assertEqual(conn.send_message.call_count,1)

    def test_cli_requires_explicit_external_confirmation(self):
        argv=['run_delivery.py','create-issue','--workflow','missing','--evidence','missing','--ownership','missing']
        with patch.object(sys,'argv',argv), patch('run_delivery.GithubTransport') as transport, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):run_delivery.main()
            transport.assert_not_called()

    def test_plaintext_port_rejected(self):
        with self.assertRaises(ValueError):SmtpTransport('smtp.example.invalid',25,'fixture','fixture')


if __name__=='__main__':unittest.main()
