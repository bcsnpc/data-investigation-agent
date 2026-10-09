"""Durable text-ticket controller over the existing intake consumer.

Public replies contain only retained question/choice IDs. Scope adoption never
calls the provider again; changed metadata or unsupported inputs refuse loudly.
"""
import copy
from .onboarding import Conflict, fields, text
from . import ticket_protocol as protocol, intake_confirmation, ticket_clarification
from .ticket_state import Tickets
from .question_intake import snapshot
from .run_recording import operation


class SmartIntake:
    def __init__(self, workspace, configuration=None):
        self.workspace=workspace;self.store=workspace.store
        self.configuration=ticket_clarification.settings(configuration)
        self.tickets=Tickets(self.store)

    def _guard(self):
        if self.workspace.agent.config.get('_estate',{}).get('recording',{}).get('tape_class')=='PRIVACY_PROJECTED':
            raise Conflict('Interactive projected capture is not available; no raw fallback is permitted')

    @operation('ticket_submit')
    def submit(self, request):
        self._guard();fields(request,['text','request_key']);text(request['text'],2000);text(request['request_key'],100)
        saved=self.tickets.submit(request,request['request_key'])
        if saved['ticket'].get('source_intake'):return saved
        source=self.workspace.intake.resolve({'text':request['text'],
            'request_key':'smart:'+saved['ticket']['id'],'parent_id':None},retain_extraction=True)
        def attach(ticket):
            ticket['source_intake']=source['id']
            ticket['history'].append({'from':ticket['state'],'to':ticket['state'],'actor':'AGENT',
                'detail':{'intake_id':source['id'],'status':source['status']}})
            return ticket
        saved=self.tickets.update(saved['ticket']['id'],saved['revision'],attach)
        return self._plan(saved,source)

    def _plan(self, saved, source):
        ticket=saved['ticket'];catalog=snapshot(self.workspace)
        payload={'text':source['text'],'models':catalog['models']}
        from .onboarding import digest
        if source['catalog_hash']!=digest(catalog):raise Conflict('Ticket metadata changed before clarification')
        def plan(current):
            if source.get('proposal'):
                current=protocol.settle_from_intake(current,source['proposal'],payload,
                    must_confirm=self.configuration['must_confirm'])
            offered=ticket_clarification.batch(current,source,payload,self.configuration)
            if offered['blocked']:
                return protocol.transition(current,'HELD',actor='AGENT',detail={'reason':offered['blocked']})
            if offered['questions']:
                return intake_confirmation.offer(current,offered['questions'],offered['values'],
                    request_text=source['text'],models=payload['models'],
                    maximum=self.configuration['max_clarifying_rounds'])
            return current
        result=self.tickets.update(ticket['id'],saved['revision'],plan)
        return self._adopt(result) if not result['ticket']['questions'] and result['ticket']['state']!='HELD' else result

    @operation('ticket_reply')
    def reply(self, request):
        self._guard();fields(request,['ticket_id','revision','answers','request_key']);text(request['request_key'],100)
        saved=self.tickets.get(request['ticket_id'])
        # A repeated request is safe only if the same sealed reply was applied.
        prior=saved['ticket'].get('reply_keys',{}).get(request['request_key'])
        from .onboarding import digest
        if prior is not None:
            if prior!=digest(request):raise Conflict('Reply key reused with different answers')
            return saved
        def answer(ticket):
            result=protocol.answer(ticket,request['answers'])
            result.setdefault('reply_keys',{})[request['request_key']]=digest(request)
            return result
        saved=self.tickets.update(request['ticket_id'],request['revision'],answer)
        return self._adopt(saved)

    def _adopt(self, saved):
        ticket=saved['ticket']
        try:
            # Scope is established by the original validator, never by the
            # completeness of the UI's answer batch alone.
            adopted=self.workspace.intake._adopt_ticket(ticket['id'],saved['revision'],
                'smart-scope:'+ticket['id']+':'+str(saved['revision']))
        except (ValueError,Conflict) as exc:
            return self.tickets.update(ticket['id'],saved['revision'],lambda t:
                protocol.transition(t,'HELD',actor='AGENT',detail={'reason':str(exc)}))
        def ready(current):
            current['intake_id']=adopted['id']
            current['history'].append({'from':current['state'],'to':current['state'],'actor':'AGENT',
                'detail':{'scope_adopted':adopted['id'],'provider_calls':0}})
            return current
        return self.tickets.update(ticket['id'],saved['revision'],ready)
