"""Explicit live transports. Constructors do not connect; no retries or redirects."""
import http.client
import json
import re
import smtplib
import ssl


class GithubTransport:
    def __init__(self, token):
        if not isinstance(token,str) or not token or any(ord(c)<33 or ord(c)>126 for c in token): raise ValueError('GitHub token required')
        self._token=token

    def __call__(self, method, path, payload=None):
        root=r'/repos/[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_][A-Za-z0-9_.-]*/issues'
        if not ((method=='POST' and re.fullmatch(root,path)) or (method=='GET' and re.fullmatch(root+r'\?state=all&sort=created&direction=desc&per_page=100&page=[1-5]',path))):
            raise ValueError('Unsupported GitHub operation')
        body=None if payload is None else json.dumps(payload).encode()
        if body is not None and len(body)>128*1024: raise ValueError('Issue payload too large')
        conn=http.client.HTTPSConnection('api.github.com',timeout=20,context=ssl.create_default_context())
        try:
            conn.request(method,path,body=body,headers={'Authorization':'Bearer '+self._token,
                'Accept':'application/vnd.github+json','Content-Type':'application/json',
                'User-Agent':'data-investigation-agent','X-GitHub-Api-Version':'2022-11-28'})
            response=conn.getresponse()
            raw=response.read(2*1024*1024+1)
            if len(raw)>2*1024*1024: raise ValueError('Response limit exceeded')
            if response.status not in (200,201): return response.status,{}
            return response.status,json.loads(raw)
        except Exception:
            raise RuntimeError('GitHub transport failed; outcome may be uncertain') from None
        finally:conn.close()


class SmtpTransport:
    def __init__(self, host, port, username, password):
        if not isinstance(host,str) or len(host)>253 or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]*',host): raise ValueError('SMTP hostname required')
        if type(port) is not int or port not in (465,587): raise ValueError('SMTP requires TLS port 465 or 587')
        if not username or not password: raise ValueError('SMTP credentials required')
        self.host,self.port,self._username,self._password=host,port,username,password

    def send_message(self,message,*,from_addr,to_addrs):
        connection=None
        try:
            context=ssl.create_default_context()
            if self.port==465:
                connection=smtplib.SMTP_SSL(self.host,self.port,timeout=20,context=context)
            else:
                connection=smtplib.SMTP(self.host,self.port,timeout=20)
                connection.ehlo();connection.starttls(context=context);connection.ehlo()
            connection.login(self._username,self._password)
            return connection.send_message(message,from_addr=from_addr,to_addrs=to_addrs)
        except Exception:
            raise RuntimeError('SMTP transport failed; outcome may be uncertain') from None
        finally:
            if connection is not None: connection.close()
