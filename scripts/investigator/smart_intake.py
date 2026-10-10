"""Durable text-ticket controller over the existing intake consumer.

Public replies contain only retained question/choice IDs. Scope adoption never
calls the provider again; changed metadata or unsupported inputs refuse loudly.
"""
import copy
from jsonschema import ValidationError
from .onboarding import Conflict, fields, text, digest
from . import ticket_protocol as protocol, intake_confirmation, ticket_clarification
from .ticket_state import Tickets
from .question_intake import snapshot
from .run_recording import operation


class SmartIntake:
    def __init__(self, workspace, configuration=None, ownership=None, *, auto_start=False):
        self.workspace=workspace;self.store=workspace.store
        self.auto_start=auto_start
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
        self._guard()
        from . import ticket_inputs
        document=ticket_inputs.document(request)
        ticket_inputs.route(request,document['text'],self.configuration)
        saved=self.tickets.submit(request,request['request_key'])
        if saved['ticket'].get('source_intake'):return saved
        if saved['ticket']['state']=='HELD':return saved
        options={'retain_extraction':True}
        if request.get('structured',{}).get('report_link') is not None:
            from .input_reference import preflight, from_input
            try:
                preflight(request)
                from_input(request,document['text'],snapshot(self.workspace)['models'])
            except ValueError as exc:
                return self.tickets.update(saved['ticket']['id'],saved['revision'],lambda current:
                    protocol.transition(current,'HELD',actor='AGENT',detail={
                        'reason':'DECLARED_REFERENCE_UNAVAILABLE','message':str(exc),
                        'source_input_hash':digest(request),'provider_calls':0}))
            options['input_request']=request
        source=self.workspace.intake.resolve({'text':document['text'],
            'request_key':'smart:'+saved['ticket']['id'],'parent_id':None},**options)
        def attach(ticket):
            ticket['source_intake']=source['id']
            if request.get('structured'):
                ticket['input_document']=document['provenance']
            ticket['history'].append({'from':ticket['state'],'to':ticket['state'],'actor':'AGENT',
                'detail':{'intake_id':source['id'],'status':source['status']}})
            return ticket
        saved=self.tickets.update(saved['ticket']['id'],saved['revision'],attach)
        return self._plan(saved,source)

    def _plan(self, saved, source):
        ticket=saved['ticket'];catalog=snapshot(self.workspace)
        payload={'text':source['text'],'models':catalog['models']}
        from .ticket_inputs import active_request
        from .input_reference import from_input
        input_request=active_request(saved)
        reference=from_input(input_request,source['text'],catalog['models'])
        if reference is not None:
            payload['_input_request']=input_request;payload['_ticket_reference']=reference
        from .onboarding import digest
        if source['catalog_hash']!=digest(catalog):raise Conflict('Ticket metadata changed before clarification')
        from .intake_extraction import retained_response
        raw=retained_response(source)
        if source.get('error')=='UNIMPLEMENTED_ROUTE' and raw and raw.get('kind')=='BUSINESS_MEANING':
            # Preserve the existing intent refusal; do not try to turn it into
            # a comparison merely by asking the user to select a visual.
            handoff=self._intent_handoff(raw,source,catalog['models'])
            if handoff is not None:
                def route_intent(current):
                    current=protocol.transition(current,'BUSINESS_VALIDATION',actor='AGENT',detail={
                        'owner':handoff['owner'],'package_hash':digest(handoff),'technical_ask_refused':source['refusal_reason']})
                    current['handoff']=handoff;return current
                return self.tickets.update(ticket['id'],saved['revision'],route_intent)
            return self.tickets.update(ticket['id'],saved['revision'],lambda current:
                protocol.transition(current,'HELD',actor='AGENT',detail={
                    'reason':source['refusal_reason'],'route':'BUSINESS_VALIDATION',
                    'handoff_unavailable':'BUSINESS_OWNER_BINDING_UNESTABLISHED'}))
        if source.get('error')=='UNIMPLEMENTED_ROUTE':
            # A user answer cannot implement a missing procedure. Retain the
            # original consumer refusal rather than asking unrelated questions.
            return self.tickets.update(ticket['id'],saved['revision'],lambda current:
                protocol.transition(current,'HELD',actor='AGENT',detail={
                    'reason':source['refusal_reason'],'capability':'UNIMPLEMENTED_ROUTE'}))
        def plan(current):
            comparison_conflict=False
            if reference is not None and 'REPORT_PAGE' not in self.configuration['must_confirm']:
                current['settled']['REPORT_PAGE']={'authority':'DECLARED_REFERENCE','value':copy.deepcopy(reference)}
            from .ticket_inputs import active_request
            request=active_request(saved)
            if source.get('proposal'):
                current=protocol.settle_from_intake(current,source['proposal'],payload,
                    must_confirm=self.configuration['must_confirm'])
            if request.get('structured') and 'COMPARISON' not in current['settled']:
                from .ticket_inputs import route as input_route
                declared=input_route(request,source['text'],self.configuration)
                if declared is not None:
                    from .ticket_route import from_request
                    try:explicit=from_request(raw,source['text'],code_gate=True) if raw else None
                    except (ValueError,ValidationError):explicit=None
                    comparison_conflict=bool(explicit and explicit['version']=='ticket-comparison-request-v1'
                                             and explicit['route']!=declared['route'])
                    if comparison_conflict:
                        current['history'].append({'from':current['state'],'to':current['state'],'actor':'AGENT',
                            'detail':{'reason':'CONFLICTING_USER_COMPARISONS','text_comparison':explicit,
                                      'supplied_comparison':declared}})
                    else:
                        current['settled']['COMPARISON']={'authority':'USER_SUPPLIED_INPUT','value':declared}
                        current['history'].append({'from':current['state'],'to':current['state'],'actor':'USER',
                            'detail':{'supplied_comparison':declared,'source_input_hash':digest(request)}})
            if raw and not comparison_conflict and 'COMPARISON' not in current['settled'] and 'COMPARISON' not in self.configuration['must_confirm']:
                from .ticket_route import settlement
                try:route=settlement(raw,source['text'],self.configuration,code_gate=True)
                except (ValueError,ValidationError):route=None
                if route is not None:
                    current['settled']['COMPARISON']={'authority':
                        'ESTATE_COMPARISON_POLICY' if route['version']=='ticket-comparison-policy-v1' else
                        'CODE_ESTABLISHED_REQUEST_COMPARISON','value':route}
                    current['history'].append({'from':current['state'],'to':current['state'],'actor':'AGENT',
                        'detail':{'settled_from_request':copy.deepcopy(route)}})
            from . import ticket_question_gate
            current,gate_events,blocked=ticket_question_gate.prepare(current,source,payload,self.configuration,
                                                                    comparison_conflict=comparison_conflict)
            for event in gate_events:
                current['history'].append({'from':current['state'],'to':current['state'],'actor':'AGENT',
                    'detail':{'event':'QUESTION_DROPPED',**event}})
            if blocked:
                return protocol.transition(current,'HELD',actor='AGENT',detail={'reason':blocked})
            offered=ticket_clarification.batch(current,source,payload,self.configuration)
            offered=ticket_question_gate.offer(current,source,payload,self.configuration,offered)
            if offered['blocked']:
                return protocol.transition(current,'HELD',actor='AGENT',detail={'reason':offered['blocked']})
            if offered['questions']:
                return intake_confirmation.offer(current,offered['questions'],offered['values'],
                    request_text=source['text'],models=payload['models'],
                    maximum=self.configuration['max_clarifying_rounds'])
            return current
        result=self.tickets.update(ticket['id'],saved['revision'],plan)
        return self._adopt(result) if not result['ticket']['questions'] and result['ticket']['state']!='HELD' else result

    def _intent_handoff(self, raw, source, models):
        """A meaning-only ticket carries the ask and definition, never invented findings."""
        from . import intake_extraction
        try:
            extraction=intake_extraction.spans(raw,source['text'])
            pairs=ticket_clarification.visual_candidates(protocol.new('intent'),extraction,
                                                         {'text':source['text'],'models':models})
            eligible={m['id'] for m,_ in pairs}
            candidates=[{**metric,'binding_id':digest([m['id'],metric['id']]),'model_id':m['id']}
                for m in models if m['id'] in eligible for metric in m['measures']]
            matched=[intake_extraction.match(i['quote']['quote'],candidates,'binding_id')
                     for i in extraction['measures'] if intake_extraction.primary_fact(i,extraction)]
            if not matched or len({m['binding_id'] for m in matched})!=1:return None
            measure=matched[0]
            owners={r['owner'] for r in self.ownership['business'] if r['measure_or_area']==measure['id']}
            if len(owners)!=1:return None
            model=next(m for m in models if m['id']==measure['model_id'])
            return {'kind':'BUSINESS_VALIDATION','owner':next(iter(owners)),
                'delivery':'RECORDED_NOT_SENT','subject':{'model_id':model['id'],'measure_id':measure['id']},
                'question':source['text'],'source_intake':source['id'],
                'retained_definition':model.get('business_definition',''),
                'limits':['No value or pipeline comparison was performed.',
                          'The engine does not decide business intent or correctness.']}
        except (ValueError,ValidationError):return None

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
        if saved['ticket']['state']=='HELD':return saved
        if set(saved['ticket']['confirmed'])&{'FIGURE','REPORT_OR_SCREENSHOT'}:
            try:return self._plan(saved,self.workspace.intake.get(saved['ticket']['source_intake']))
            except (ValueError,Conflict) as exc:
                return self.tickets.update(request['ticket_id'],saved['revision'],lambda ticket:
                    protocol.transition(ticket,'HELD',actor='AGENT',detail={'reason':str(exc)}))
        if 'REPORT_PAGE' not in saved['ticket']['settled'] and 'NUMBER' in saved['ticket']['confirmed']:
            source=self.workspace.intake.get(saved['ticket']['source_intake'])
            try:
                catalog=snapshot(self.workspace)
                if digest(catalog)!=source['catalog_hash']:raise Conflict('Ticket metadata changed before container settlement')
                saved=self.tickets.update(request['ticket_id'],saved['revision'],lambda ticket:
                    intake_confirmation.settle_container(ticket,request_text=source['text'],models=catalog['models']))
            except (ValueError,Conflict) as exc:
                return self.tickets.update(request['ticket_id'],saved['revision'],lambda ticket:
                    protocol.transition(ticket,'HELD',actor='AGENT',detail={'reason':str(exc)}))
        return self._adopt(saved)

    def _adopt(self, saved):
        ticket=saved['ticket']
        try:
            # Scope is established by the original validator, never by the
            # completeness of the UI's answer batch alone.
            adopted=self.workspace.intake._adopt_ticket(ticket['id'],saved['revision'],
                'smart-scope:'+ticket['id']+':'+str(saved['revision']),comparison_configuration=self.configuration)
        except (ValueError,Conflict) as exc:
            return self.tickets.update(ticket['id'],saved['revision'],lambda t:
                protocol.transition(t,'HELD',actor='AGENT',detail={'reason':str(exc)}))
        def ready(current):
            current['intake_id']=adopted['id']
            current['history'].append({'from':current['state'],'to':current['state'],'actor':'AGENT',
                'detail':{'scope_adopted':adopted['id'],'provider_calls':0}})
            return current
        saved=self.tickets.update(ticket['id'],saved['revision'],ready)
        return self._start_settled(saved) if self.auto_start else saved

    def _start_settled(self, saved):
        """Queue exactly the adopted scope through the existing governed start.

        Persist the preview before starting: a repeated submission cannot create
        another preview or retry an uncertain start after a host interruption.
        """
        ticket=saved['ticket']
        if not self.workspace.execution_enabled:
            return self.tickets.update(ticket['id'],saved['revision'],lambda current:
                protocol.transition(current,'HELD',actor='AGENT',detail={
                    'reason':'INTAKE_ONLY_HOST','scope_adopted':ticket['intake_id']}))
        source=self.workspace.intake.get(ticket['intake_id']);p=source['proposal']
        request={k:copy.deepcopy(p[k]) for k in ('model_id','measure_id','filters','dimension_ids')}
        request.update(symptom=source['text'],predecessor=None,intake_id=source['id'])
        try:
            preview=self.workspace.preview(request)
            def reserve(current):
                current['start_preview_id']=preview['id']
                current['history'].append({'from':current['state'],'to':current['state'],'actor':'AGENT',
                    'detail':{'reason':'AUTO_START_RESERVED','preview_id':preview['id'],
                              'limits':copy.deepcopy(preview['envelope']['limits'])}})
                return current
            saved=self.tickets.update(ticket['id'],saved['revision'],reserve)
            run=self.workspace.start(preview['id'])
            return self.attach({'ticket_id':ticket['id'],'revision':saved['revision'],'session_id':run['id']})
        except (ValueError,Conflict) as exc:
            return self.tickets.update(ticket['id'],saved['revision'],lambda current:
                protocol.transition(current,'HELD',actor='AGENT',detail={
                    'reason':'AUTO_START_REFUSED','message':str(exc),
                    'preview_id':current.get('start_preview_id')}))

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
        from .ticket_findings import from_state, TECHNICAL
        saved=self.tickets.get(request['ticket_id']);ticket=saved['ticket']
        if ticket['state']!='INVESTIGATING':raise Conflict('Ticket is not investigating')
        self._bound_session(ticket,ticket['session_id'])
        findings=from_state(self.workspace.agent.get(ticket['session_id']))
        def share(current):
            current=protocol.transition(current,'FINDINGS_SHARED',actor='AGENT',
                detail={'session_id':findings['session_id'],'findings_hash':digest(findings)})
            current['findings']=findings
            return self._handoff(current,'TECH_HANDOFF') if findings['classification'] in TECHNICAL else current
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
        text(request['text'],protocol.TEXT['maxLength'])
        if request['kind'] not in ('DISPUTE','REQUEST_CHANGE','EXPLAIN_RECORDED_RESULT','RESTATE_QUESTION'):
            raise ValueError('Unknown findings reply kind')
        saved=self.tickets.get(request['ticket_id']);ticket=saved['ticket']
        if request['kind']=='RESTATE_QUESTION':return self._restate(saved,request)
        if ticket['state'] not in ('FINDINGS_SHARED','BUSINESS_VALIDATION','TECH_HANDOFF'):
            raise Conflict('Ticket is not awaiting a findings reply')
        if 'findings' not in ticket and ticket.get('handoff',{}).get('kind')=='BUSINESS_VALIDATION':
            def owner_reply(current):
                current['history'].append({'from':current['state'],'to':current['state'],'actor':'USER',
                    'detail':{'reply_kind':request['kind'],'text':request['text'],
                              'owner':current['handoff']['owner'],'technical_findings':'NOT_OBTAINED'}})
                return current
            return self.tickets.update(ticket['id'],request['revision'],owner_reply)
        from .ticket_findings import CONSISTENT
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
            if current['state']==kind and current.get('handoff'):return current
            return self._handoff(current,kind)
        return self.tickets.update(ticket['id'],request['revision'],reply)

    def _restate(self, saved, request):
        """User changes the question; preserve old evidence without its authority."""
        ticket=saved['ticket']
        if saved['revision']!=request['revision']:raise Conflict('Ticket changed before the new question')
        if ticket['state'] not in ('NEW','CLARIFYING','FINDINGS_SHARED','BUSINESS_VALIDATION','TECH_HANDOFF','HELD'):
            raise Conflict('Ticket is not waiting for a changed question')
        from .ticket_inputs import active_request,document
        changed={'text':request['text'],'request_key':'smart-restatement:'+ticket['id']+':'+str(saved['revision'])}
        derived=document(changed)
        prior_input=copy.deepcopy(ticket['form_input'] if ticket.get('form_input') else active_request(saved))
        scoped=('source_intake','intake_id','session_id','findings','handoff','retained_answer',
                'input_document','choice_context','choice_values','clarification_offers','reply_keys','unavailable_fields',
                'form_input','form_catalog_hash','form_choices')
        def change(current):
            archived={'revision':saved['revision'],'input_request':prior_input,
                'confirmed':copy.deepcopy(current['confirmed']),'settled':copy.deepcopy(current['settled']),
                'questions':copy.deepcopy(current['questions']),'rounds':current['rounds']}
            for field in scoped:
                if field in current:archived[field]=current.pop(field)
            current.setdefault('question_versions',[]).append(archived)
            current['prior_clarifying_rounds']=current.get('prior_clarifying_rounds',0)+current['rounds']
            current.update(current_input=changed,questions=[],confirmed={},settled={},rounds=0)
            return protocol.transition(current,'CLARIFYING',actor='USER',detail={
                'reply_kind':'RESTATE_QUESTION','input_hash':digest(changed),
                'prior_question_revision':saved['revision'],'prior_evidence_use':'HISTORICAL_ONLY'})
        updated=self.tickets.update(ticket['id'],saved['revision'],change)
        try:
            source=self.workspace.intake.resolve({'text':derived['text'],
                'request_key':changed['request_key'],'parent_id':None},retain_extraction=True)
        except Exception as exc:
            return self.tickets.update(ticket['id'],updated['revision'],lambda current:
                protocol.transition(current,'HELD',actor='AGENT',detail={
                    'reason':'RESTATEMENT_INTAKE_FAILED','exception_type':type(exc).__name__,'message':str(exc),
                    'source_request_key':changed['request_key']}))
        def attach(current):
            current['source_intake']=source['id']
            current['history'].append({'from':current['state'],'to':current['state'],'actor':'AGENT',
                'detail':{'intake_id':source['id'],'status':source['status'],'new_question':True}})
            return current
        updated=self.tickets.update(ticket['id'],updated['revision'],attach)
        return self._plan(updated,source)

    def _handoff(self, current, kind):
        from .ticket_findings import package
        finding=current['findings'];process=finding['assessment']['support']['process']
        if kind=='BUSINESS_VALIDATION':
            adopted=self.workspace.intake.get(current['intake_id'])
            selectors={adopted['proposal']['measure_id']};key='measure_or_area';rows=self.ownership['business']
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
