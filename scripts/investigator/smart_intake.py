"""Durable text-ticket controller over the existing intake consumer.

Public replies contain only retained question/choice IDs. Scope adoption never
calls the provider again; changed metadata or unsupported inputs refuse loudly.
"""
import copy
from .onboarding import Conflict, fields, text, digest
from . import ticket_protocol as protocol, intake_confirmation, ticket_clarification
from .ticket_state import Tickets
from .question_intake import snapshot
from .run_recording import operation


class SmartIntake:
    def __init__(self, workspace, configuration=None, ownership=None):
        self.workspace=workspace;self.store=workspace.store
        self.configuration=ticket_clarification.settings(configuration)
        from jsonschema import Draft202012Validator
        self.ownership=copy.deepcopy(ownership or {'business':[],'technical':[]})
        Draft202012Validator(protocol.OWNERSHIP).validate(self.ownership)
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

    def _bound_session(self, ticket, identity):
        view=self.workspace.session(identity)
        if (view.get('intake') or {}).get('id')!=ticket.get('intake_id'):
            raise Conflict('Investigation was not created from this ticket scope')
        adopted=self.workspace.intake.get(ticket['intake_id'])
        from .intake_confirmation import authority_hash
        if adopted['confirmation_ticket']['authority_hash']!=authority_hash(ticket):
            raise Conflict('Ticket decisions changed after scope adoption')
        return view

    @operation('ticket_attach')
    def attach(self, request):
        """Link an existing governed workspace run; this never starts a read."""
        self._guard();fields(request,['ticket_id','revision','session_id'])
        saved=self.tickets.get(request['ticket_id']);ticket=saved['ticket']
        self._bound_session(ticket,request['session_id'])
        def attach(current):
            current=protocol.transition(current,'INVESTIGATING',actor='AGENT',
                detail={'session_id':request['session_id']})
            current['session_id']=request['session_id'];return current
        return self.tickets.update(ticket['id'],request['revision'],attach)

    @operation('ticket_share')
    def share(self, request):
        self._guard();fields(request,['ticket_id','revision'])
        from .ticket_findings import from_state
        saved=self.tickets.get(request['ticket_id']);ticket=saved['ticket']
        if ticket['state']!='INVESTIGATING':raise Conflict('Ticket is not investigating')
        self._bound_session(ticket,ticket['session_id'])
        findings=from_state(self.workspace.agent.get(ticket['session_id']))
        def share(current):
            current=protocol.transition(current,'FINDINGS_SHARED',actor='AGENT',
                detail={'session_id':findings['session_id'],'findings_hash':digest(findings)})
            current['findings']=findings;return current
        return self.tickets.update(ticket['id'],request['revision'],share)

    @operation('ticket_finish')
    def finish(self, request):
        """Compose once through the existing governed synthesis producer."""
        self._guard();fields(request,['ticket_id','revision'])
        saved=self.tickets.get(request['ticket_id']);ticket=saved['ticket']
        if saved['revision']!=request['revision']:raise Conflict('Ticket changed before synthesis')
        if ticket['state']!='INVESTIGATING':raise Conflict('Ticket is not investigating')
        self._bound_session(ticket,ticket['session_id'])
        state=self.workspace.agent.get(ticket['session_id'])
        if state['status'] in ('READY','PLANNING','EXECUTING'):
            raise Conflict('Investigation is still running')
        if not state.get('synthesis'):
            from .run_recording import seal_read_stage
            seal_read_stage(self.workspace.agent,ticket['session_id'])
            state=self.workspace.agent.synthesize(ticket['session_id'])
        if (state.get('synthesis') or {}).get('status')!='COMPLETED':
            return self.tickets.update(ticket['id'],request['revision'],lambda current:
                protocol.transition(current,'HELD',actor='AGENT',detail={
                    'reason':'SYNTHESIS_DID_NOT_COMPLETE','session_id':state['id'],
                    'synthesis':copy.deepcopy(state.get('synthesis')),'stop_reason':state.get('stop_reason')}))
        return self.share(request)

    @operation('ticket_close')
    def close(self, request):
        self._guard();fields(request,['ticket_id','revision'])
        return self.tickets.update(request['ticket_id'],request['revision'],lambda ticket:
            protocol.transition(ticket,'CLOSED',actor='USER',detail={'agreement':True}))

    @operation('ticket_respond')
    def respond(self, request):
        self._guard();fields(request,['ticket_id','revision','kind','text'])
        text(request['text'],2000)
        if request['kind'] not in ('DISPUTE','REQUEST_CHANGE','EXPLAIN_RECORDED_RESULT'):
            raise ValueError('Unknown findings reply kind')
        saved=self.tickets.get(request['ticket_id']);ticket=saved['ticket']
        if ticket['state']!='FINDINGS_SHARED':raise Conflict('Ticket is not awaiting a findings reply')
        from .ticket_findings import CONSISTENT, package
        finding=ticket['findings']
        self._bound_session(ticket,ticket['session_id'])
        def reply(current):
            current['history'].append({'from':current['state'],'to':current['state'],'actor':'USER',
                'detail':{'reply_kind':request['kind'],'text':request['text']}})
            if request['kind']=='EXPLAIN_RECORDED_RESULT':
                current['retained_answer']={'outputs':copy.deepcopy(finding['outputs']),
                    'qualification':'This describes retained evidence, not a new reading of current data.'}
                return current
            kind='BUSINESS_VALIDATION' if request['kind']=='DISPUTE' and finding['classification'] in CONSISTENT else 'TECH_HANDOFF'
            assessment=finding['assessment'];process=assessment['support']['process']
            if kind=='BUSINESS_VALIDATION':
                adopted=self.workspace.intake.get(current['intake_id'])
                selector=adopted['proposal']['measure_id'];key='measure_or_area';rows=self.ownership['business']
                selectors={selector}
            else:
                key='layer_or_pipeline';rows=self.ownership['technical']
                selectors={process['visibility_boundary']['deepest_layer'],process['baseline_above']['layer']}
            owners={row['owner'] for row in rows if row[key] in selectors}
            if len(owners)!=1:
                current['history'].append({'from':current['state'],'to':current['state'],'actor':'AGENT',
                    'detail':{'handoff_unavailable':'OWNERSHIP_AMBIGUOUS' if owners else 'OWNERSHIP_UNDECLARED',
                              'requested_kind':kind}})
                return current
            owner=next(iter(owners));handoff=package(finding,kind,owner)
            current=protocol.transition(current,kind,actor='AGENT',detail={'owner':owner,'package_hash':digest(handoff)})
            current['handoff']=handoff;return current
        return self.tickets.update(ticket['id'],request['revision'],reply)
