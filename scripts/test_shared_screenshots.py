import base64
import copy
from contextlib import closing
import hashlib
from pathlib import Path
import sqlite3
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from investigator.screenshot_intake import Screenshots
from investigator.onboarding import Conflict
from investigator import shared_application as app
from investigator.shared_state import SharedState
from investigator.live_gateway import Gateway, GatewayDenied
from investigator.adapters import screenshot_blobs as blobs
from test_shared_application import SharedApplicationTests, store
from test_screenshot_intake import image_bytes


class Objects:
    def __init__(self):self.values={};self.deleted=[]
    def put(self,key,data):self.values[key]=data
    def get(self,key):return self.values[key]
    def delete(self,key):self.deleted.append(key);self.values.pop(key,None)


class SharedScreenshotTests(unittest.TestCase):
    def setUp(self):
        SharedApplicationTests.setUp(self);self.now=1000.;self.objects=Objects()
        self.workspace=SimpleNamespace(store=self.store,clock=lambda:self.now,agent=SimpleNamespace(config={}),intake_configuration=None)
        self.screens=Screenshots(self.workspace);self.screens.pixels._objects=self.objects
        self.raw=image_bytes()
        self.request={'name':'report.png','mime':'image/png','base64':base64.b64encode(self.raw).decode(),'request_key':'image'}

    def test_pixels_only_in_blob_and_defaults_expire_at_thirty_days(self):
        image=self.screens.upload(self.request)
        self.assertEqual(self.screens.image(image['id'],content=True)[1],self.raw)
        with closing(sqlite3.connect(self.store.database))as db:
            self.assertIsNone(db.execute('SELECT content FROM workspace_images').fetchone()[0])
            expires=db.execute('SELECT expires FROM workspace_image_objects').fetchone()[0]
        self.assertEqual(expires,1000+30*86400)
        self.assertNotIn(base64.b64encode(self.raw).decode(),str(app.source(self.store.database,'synthetic')))
        self.now=expires
        self.assertFalse(self.screens.image(image['id'])['available'])
        self.assertEqual(len(self.objects.deleted),1);self.assertFalse(self.objects.values)
        with self.assertRaisesRegex(Conflict,'removed or expired'):self.screens.image(image['id'],content=True)

    def test_estate_retention_and_scheduled_bounded_purge(self):
        from investigator.ticket_clarification import settings
        conf=settings();conf['screenshot_retention_days']=7;self.workspace.intake_configuration=conf
        self.screens=Screenshots(self.workspace);self.screens.pixels._objects=self.objects
        image=self.screens.upload(self.request);self.now+=7*86400
        result=self.screens.pixels.purge(limit=1)
        self.assertEqual(result['expired'],1);self.assertFalse(self.objects.values)
        self.assertFalse(self.screens.image(image['id'])['available'])

    def test_expiry_is_rechecked_after_blob_fetch_and_delete_failure_refuses(self):
        image=self.screens.upload(self.request)
        def late(key):self.now+=31*86400;return self.raw
        with patch.object(self.objects,'get',side_effect=late):
            with self.assertRaisesRegex(Conflict,'expired'):self.screens.image(image['id'],content=True)
        self.request['request_key']='two';image=self.screens.upload(self.request);self.now+=31*86400
        with patch.object(self.objects,'delete',side_effect=OSError('unavailable')):
            with self.assertRaises(OSError):self.screens.image(image['id'],content=True)

    def test_projected_pixels_and_immutable_raw_capture_refuse(self):
        self.workspace.agent.config={'_estate':{'recording':{'tape_class':'PRIVACY_PROJECTED'}}}
        with self.assertRaisesRegex(Conflict,'privacy projection'):self.screens.upload(self.request)
        self.workspace.agent.config={}
        from investigator.process_tape import Tape,active
        from test_process_tape import bootstrap
        with active(Tape(self.root/'capture.json',bootstrap())):
            with self.assertRaisesRegex(Conflict,'IMMUTABLE_CAPTURE'):self.screens.upload(self.request)
        self.assertFalse(self.objects.values)


class ScreenshotGatewayTests(unittest.TestCase):
    def setUp(self):
        self.account='https://syntheticstore.blob.core.windows.net';self.channel='images'
        self.raw=b'pixels';self.key=blobs.object_key('estate','12345678-1234-1234-1234-123456789012',hashlib.sha256(self.raw).hexdigest())
        self.url=self.account+'/screenshots/'+self.key
        self.gateway=Gateway({'version':1,'live_enabled':True,'identities':{
            self.channel:{'role':'platform','http':[],'platform_screenshots':[{'account_url':self.account,'container':'screenshots'}]}}})

    def test_scoped_pixels_allow_only_bound_exact_object_method_body(self):
        headers={'If-None-Match':'*','x-ms-blob-type':'BlockBlob'}
        with blobs.bind(self.gateway,self.channel,self.account,self.key,'PUT',self.raw):
            self.gateway.http(self.channel,'PUT',self.url,body=self.raw,headers=headers)
            for method,url,data,h in [('DELETE',self.url,None,{}),('PUT',self.url+'?comp=metadata',self.raw,headers),
                ('PUT',self.url.replace('/screenshots/','/tapes/'),self.raw,headers),
                ('PUT',self.url.replace('syntheticstore','otherstore'),self.raw,headers),
                ('PUT',self.url,b'changed',headers),('PUT',self.url,self.raw,{})]:
                with self.subTest(method=method,url=url):
                    with self.assertRaises(GatewayDenied):self.gateway.http(self.channel,method,url,body=data,headers=h)
        with self.assertRaises(GatewayDenied):self.gateway.http(self.channel,'GET',self.url)
        with blobs.bind(self.gateway,self.channel,self.account,self.key,'DELETE'):
            self.gateway.http(self.channel,'DELETE',self.url)
            with patch.dict('os.environ',{'DIA_LIVE_ACCESS_DISABLED':'1'}):
                with self.assertRaises(GatewayDenied):self.gateway.http(self.channel,'DELETE',self.url)


if __name__=='__main__':unittest.main()
