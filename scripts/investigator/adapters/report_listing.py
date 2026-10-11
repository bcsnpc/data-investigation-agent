"""Estate-scoped live report/page lists; reader-only, metered, identity-scoped cache.

These are selection metadata, never discovery approval or quantity evidence.
Visual-definition access is deliberately not implied by successful page listing.
"""
import copy
import threading
import time
from uuid import UUID


class ReportLists:
    def __init__(self, workspace_ids, identity, read, *, ttl_seconds=300, clock=time.monotonic):
        self.workspaces=tuple(sorted({str(UUID(v)) for v in workspace_ids}))
        if not self.workspaces or not isinstance(identity,str) or not identity:
            raise ValueError('Explicit estate workspace scope and reader identity required')
        if type(ttl_seconds) is not int or not 1<=ttl_seconds<=3600:
            raise ValueError('Live-list cache TTL must be 1..3600 seconds')
        self.identity=identity;self.read=read;self.ttl=ttl_seconds;self.clock=clock
        self.cache={};self.lock=threading.RLock()

    def _get(self, key, endpoint, refresh):
        if type(refresh) is not bool:raise ValueError('Refresh must be boolean')
        with self.lock:
            cached=self.cache.get(key)
            if not refresh and cached and self.clock()-cached['at']<self.ttl:
                return copy.deepcopy(cached['value']),True
            # Exceptions do not renew the cache or return expired/stale data.
            response=self.read(endpoint)
            if response.get('status_code')!=200:
                raise ValueError('Live metadata unavailable: HTTP '+str(response.get('status_code')))
            if any(response.get('body',{}).get(k) for k in ('@odata.nextLink','continuationToken','continuationUri')):
                raise ValueError('Live metadata is incomplete: continuation is not supported')
            value=response.get('body',{}).get('value')
            if not isinstance(value,list):raise ValueError('Live metadata collection missing')
            self.cache[key]={'at':self.clock(),'value':copy.deepcopy(value)}
            return copy.deepcopy(value),False

    def reports(self, *, refresh=False):
        rows=[];hits=[]
        for workspace in self.workspaces:
            values,hit=self._get(('reports',workspace),'groups/'+workspace+'/reports',refresh)
            hits.append(hit)
            for value in values:
                identity=str(UUID(value['id']))
                if not isinstance(value.get('name'),str) or not value['name']:
                    raise ValueError('Live report name unavailable')
                rows.append({'workspace_id':workspace,'report_id':identity,'name':value['name'],
                             'report_type':value.get('reportType'),
                             'supported':value.get('reportType')=='PowerBIReport'})
        if len({(r['workspace_id'],r['report_id']) for r in rows})!=len(rows):
            raise ValueError('Duplicate live report identity')
        return {'source':'LIVE_POWER_BI_READER_METADATA','identity':self.identity,
                'reports':rows,'cached':all(hits),'cache_ttl_seconds':self.ttl}

    def pages(self, workspace_id, report_id, *, refresh=False):
        workspace=str(UUID(workspace_id));report=str(UUID(report_id))
        if workspace not in self.workspaces:raise ValueError('Workspace outside estate scope')
        reports=self.reports(refresh=False)['reports']
        matches=[r for r in reports if r['workspace_id']==workspace and r['report_id']==report]
        if not matches:
            raise ValueError('Report absent from current live estate list; refresh the report list')
        if not matches[0]['supported']:
            raise ValueError('Listed report type is unsupported: '+str(matches[0]['report_type']))
        values,hit=self._get(('pages',workspace,report),'groups/'+workspace+'/reports/'+report+'/pages',refresh)
        rows=[]
        for value in values:
            if not all(isinstance(value.get(k),str) and value[k] for k in ('name','displayName')):
                raise ValueError('Live page identity/name unavailable')
            rows.append({'workspace_id':workspace,'report_id':report,'page_id':value['name'],
                         'name':value['displayName'],'order':value.get('order')})
        if len({r['page_id'] for r in rows})!=len(rows):raise ValueError('Duplicate live page identity')
        return {'source':'LIVE_POWER_BI_READER_METADATA','identity':self.identity,
                'pages':rows,'cached':hit,'cache_ttl_seconds':self.ttl}

    def bound_catalog(self, models, *, refresh=False):
        """Join exact native IDs, never report names or visual quantities."""
        from urllib.parse import urlsplit
        live=self.reports(refresh=refresh);result=copy.deepcopy(models);unbound=[]
        retained={}
        for model in result:
            for report in model.get('reports',[]):
                uri=urlsplit(report['id'])
                if uri.scheme!='fabric':continue
                try:key=(str(UUID(uri.netloc)),str(UUID(uri.path.strip('/'))))
                except ValueError:continue
                retained.setdefault(key,[]).append((model,report))
            model['reports']=[]
        for row in live['reports']:
            matches=retained.get((row['workspace_id'],row['report_id']),[])
            if row['supported'] and len(matches)==1:
                model,report=matches[0];report['name']=row['name'];model['reports'].append(report)
            else:
                unbound.append({**row,'id':'fabric://'+row['workspace_id']+'/'+row['report_id'],
                    'reason':'UNAPPROVED_OR_AMBIGUOUS_CONTEXT' if row['supported'] else 'UNSUPPORTED_REPORT_TYPE'})
        for model in result:
            identities={r['id'] for r in model['reports']}
            model['visuals']=[v for v in model.get('visuals',[]) if v['report_id'] in identities]
        return {**live,'models':result,'unbound_reports':unbound}

    def bound_pages(self,report_id,models,*,refresh=False):
        from urllib.parse import urlsplit
        matches=[r for m in models for r in m.get('reports',[]) if r['id']==report_id]
        if len(matches)!=1:raise ValueError('Report not uniquely bound in the approved context')
        uri=urlsplit(report_id)
        if uri.scheme!='fabric':raise ValueError('Report has no native metadata address')
        live=self.pages(str(UUID(uri.netloc)),str(UUID(uri.path.strip('/'))),refresh=refresh)
        retained={v['page_id'] for m in models for v in m.get('visuals',[]) if v['report_id']==report_id}
        rows=[]
        for page in live['pages']:
            identity=report_id+'/page/'+page['page_id']
            rows.append({'id':identity,'name':page['name'],'executable':identity in retained})
        return {**live,'pages':rows}
