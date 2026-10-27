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

    def __call__(self,node,kinds):
        if node not in self.allowed:raise PermissionError('HISTORY_OUTSIDE_ADMITTED_PATH')
        if node not in self.subjects:return {'status':'UNAVAILABLE','reason':'NATIVE_HISTORY_SUBJECT_NOT_CONFIGURED','node':node}
        at=self.now()
        adapter=MicrosoftRuntimeFacts({node:self.subjects[node]},http=self.http,retain=self.retain,
            sql=self.sql,refresh_http=self.refresh_http,now=lambda:at)
        adapter.list_changes([node]);facts=adapter.fetch(node,now=at)
        if self.ledger:self.ledger.append(self.estate,facts)
        selected=[f for f in facts if f['kind'] in kinds]
        observed=[f for f in selected if f['state'] in ('OBSERVED','OBSERVED_NEGATIVE')]
        return {'status':'OBSERVED' if observed else 'UNAVAILABLE','node':node,
            'purpose':'INVESTIGATION','source':'native-subject-history','observed_at':at,
            'facts':selected,'coverage':[f for f in facts if f['kind']=='COVERAGE']}
