"""Explicit investigation history tools, separate from scheduled SCAN collection.

One admitted native subject per tool call, no dispatcher, profile scan or cursor.
The caller supplies the normal INV physical meter and existing read identities.
"""
from copy import deepcopy
from .adapters.runtime_facts_microsoft import MicrosoftRuntimeFacts


class SubjectHistory:
    def __init__(self,*,subjects,allowed,http,retain,sql=None,refresh_http=None,now,ledger=None,estate=None):
        self.subjects=deepcopy(subjects);self.allowed=frozenset(allowed)
        self.http,self.retain,self.sql,self.refresh_http=http,retain,sql,refresh_http
        self.now,self.ledger,self.estate=now,ledger,estate

    def top_up(self,estate,subjects,*,now,force=False):
        if estate!=self.estate or not set(subjects)<=self.allowed:raise PermissionError('TRIAGE_HISTORY_OUTSIDE_ADMITTED_PATH')
        # These are the ticket's ready-made history checks, not the scheduled
        # collector: no estate listing, profiles, dispatcher or scan cursor.
        selected=[n for n in sorted(subjects) if self.subjects.get(n,{}).get('kind') in ('JOB','MODEL')][:10]
        for node in selected:self(node,{'JOB_RUN','RUN_HISTORY','SCHEDULE','REFRESH_RUN','REFRESH_STATE'})
        return {'status':'PATH_NATIVE_HISTORY_CHECKED','subjects':selected,'purpose':'INVESTIGATION',
            'unavailable_subjects':sorted(set(subjects)-set(selected))}

    def __call__(self,node,kinds,*,selector=None,text=None):
        if node not in self.allowed:raise PermissionError('HISTORY_OUTSIDE_ADMITTED_PATH')
        if node not in self.subjects:return {'status':'UNAVAILABLE','reason':'NATIVE_HISTORY_SUBJECT_NOT_CONFIGURED','node':node}
        at=self.now()
        adapter=MicrosoftRuntimeFacts({node:self.subjects[node]},http=self.http,retain=self.retain,
            sql=self.sql,refresh_http=self.refresh_http,now=lambda:at)
        adapter.list_changes([node]);facts=adapter.fetch(node,now=at)
        if selector is not None and self.subjects[node]['kind']=='JOB':
            facts=self.requested_job_history(adapter,node,facts,selector,text,at)
        if self.ledger:self.ledger.append(self.estate,facts)
        selected=[f for f in facts if f['kind'] in kinds]
        observed=[f for f in selected if f['state'] in ('OBSERVED','OBSERVED_NEGATIVE')]
        return {'status':'OBSERVED' if observed else 'UNAVAILABLE','node':node,
            'purpose':'INVESTIGATION','source':'native-subject-history','observed_at':at,
            'facts':selected,'coverage':[f for f in facts if f['kind']=='COVERAGE'],
            **({'automatic_updates': {'status': 'UNAVAILABLE_FROM_THIS_SURFACE',
                  'setting': 'Keep your Direct Lake data up to date',
                  'reason': 'The supported refresh-history and refresh-schedule responses do not expose the Direct Lake automatic-update switch.',
                  'owner_location': 'Semantic model settings → Refresh → Keep your Direct Lake data up to date',
                  'inference': 'No ON/OFF state is inferred from refresh dates or a schedule enabled flag.'}}
               if self.subjects[node]['kind']=='MODEL' else {})}


    def requested_job_history(self,adapter,node,facts,selector,text,at):
        from urllib.parse import quote,urlsplit,parse_qs
        from .operational_run_selection import validate,select
        from .adapters.runtime_facts_microsoft import native_runs,observation
        validate(selector,text)
        route=self.subjects[node];base='workspaces/'+route['workspace']+'/items/'+route['item']+'/jobs/instances'
        body,proof,error=adapter.cache[node]
        if error:return facts
        all_runs=native_runs(body.get('value'));proofs=[proof];pages=1;seen=set();paging_gap=None
        def history():
            incomplete=bool(body.get('continuationToken')or body.get('continuationUri')) or paging_gap is not None
            return observation(node,'RUN_HISTORY',{'runs':deepcopy(all_runs),'listing_complete':not incomplete,'pages_checked':pages},at,proofs,adapter.identity)
        while True:
            try:select(selector,[history()],text);break
            except ValueError as problem:
                if str(problem)not in ('REQUESTED_RUN_NOT_IN_RETAINED_HISTORY','REQUESTED_RUN_TIME_PRECISION_UNAVAILABLE'):break
            token=body.get('continuationToken')
            if not token and body.get('continuationUri'):
                link=urlsplit(body['continuationUri']);expected='https://api.fabric.microsoft.com/v1/'+base
                if link._replace(query='',fragment='').geturl()!=expected or link.fragment:raise ValueError('HISTORY_CONTINUATION_SCOPE')
                query=parse_qs(link.query,strict_parsing=True)
                if set(query)!={'continuationToken'}or len(query['continuationToken'])!=1:raise ValueError('HISTORY_CONTINUATION_QUERY')
                token=query['continuationToken'][0]
            if not token:break
            if not isinstance(token,str)or not 0<len(token)<=8192:raise ValueError('HISTORY_CONTINUATION_BOUND')
            if token in seen:paging_gap='NATIVE_HISTORY_CURSOR_REPEATED';break
            if pages>=6:paging_gap='NATIVE_HISTORY_SIX_PAGE_LIMIT';break
            seen.add(token)
            body,proof,error=adapter._get(base+'?continuationToken='+quote(token,safe=''))
            proofs.append(proof);pages+=1
            if error:paging_gap='NATIVE_HISTORY_PAGE_UNAVAILABLE:'+error;body={};break
            all_runs.extend(native_runs(body.get('value')))
        # Older pages are history, never a replacement for the current JOB_RUN.
        result=[f for f in facts if f['kind']!='RUN_HISTORY']+[history()]
        if paging_gap:result.append(adapter._gap(node,'COVERAGE',paging_gap,at,proofs))
        return result
