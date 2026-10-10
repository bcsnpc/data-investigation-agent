"""Durable form submissions sharing the existing findings/start lifecycle."""
import copy
from jsonschema import Draft202012Validator, ValidationError
from . import form_intake, form_scope, ticket_protocol as protocol
from .onboarding import digest, Conflict, fields
from .question_intake import snapshot
from .run_recording import operation


class Forms:
    def __init__(self, workspace):
        self.workspace=workspace

    @property
    def smart(self): return self.workspace.smart_intake

    @property
    def configuration(self): return self.smart.configuration

    @property
    def ownership(self): return self.smart.ownership

    @property
    def auto_start(self): return self.smart.auto_start

    def catalog(self, *, refresh=False):
        if type(refresh) is not bool:raise ValueError('Refresh must be boolean')
        current=snapshot(self.workspace)
        from .ticket_clarification import settings
        result={'catalog_hash':digest(current), 'models':copy.deepcopy(current['models']),
                'comparison_choices':settings(self.workspace.intake_configuration)['comparison_choices'],
                'source':'RETAINED_APPROVED_CONTEXT', 'live_lists_connected':False}
        lists=getattr(self.workspace,'report_lists',None)
        if lists is not None:
            live=lists.bound_catalog(current['models'],refresh=refresh)
            result.update(models=live['models'],source=live['source'],live_lists_connected=True,
                          unbound_reports=live['unbound_reports'],cached=live['cached'],
                          cache_ttl_seconds=live['cache_ttl_seconds'],identity=live['identity'])
        return result

    def pages(self,request):
        fields(request,['report_id','refresh'])
        lists=getattr(self.workspace,'report_lists',None)
        if lists is None:raise Conflict('Live page lists are not connected on this host')
        return lists.bound_pages(request['report_id'],snapshot(self.workspace)['models'],refresh=request['refresh'])

    @operation('form_submit')
    def submit(self, request):
        self.smart._guard()
        try:Draft202012Validator(form_intake.SCHEMA).validate(request)
        except ValidationError as exc:raise ValueError('Form does not satisfy the closed input contract') from exc
        saved=self.smart.tickets.submit(request,request['request_key'])
        if saved['revision']!=0:return saved
        catalog=snapshot(self.workspace)
        def retain(ticket):
            ticket['form_input']=copy.deepcopy(request)
            ticket['form_catalog_hash']=digest(catalog)
            ticket['history'].append({'from':'NEW','to':'NEW','actor':'USER',
                'detail':{'form_input_hash':digest(request),'catalog_hash':digest(catalog)}})
            return ticket
        saved=self.smart.tickets.update(saved['ticket']['id'],saved['revision'],retain)
        return self._plan(saved,catalog)

    def _hold(self,saved,reason):
        return self.smart.tickets.update(saved['ticket']['id'],saved['revision'],lambda t:
            protocol.transition(t,'HELD',actor='AGENT',detail={'reason':reason}))

    def _plan(self,saved,catalog):
        request=saved['ticket']['form_input']
        try:result=form_intake.resolve(request,catalog['models'],self.workspace.intake_configuration)
        except ValueError as exc:return self._hold(saved,str(exc))
        if result['status']=='HELD':return self._hold(saved,result['reason'])
        if request['comparison']=='BUSINESS_MEANING' and result['status']=='BOUND':
            measure=result['scope']['measure_id']
            owners={r['owner'] for r in self.smart.ownership['business'] if r['measure_or_area']==measure}
            if len(owners)!=1:return self._hold(saved,'BUSINESS_OWNER_BINDING_UNESTABLISHED')
            model=next(m for m in catalog['models'] if m['id']==result['scope']['model_id'])
            handoff={'kind':'BUSINESS_VALIDATION','owner':next(iter(owners)),
                'delivery':'RECORDED_NOT_SENT','subject':{'model_id':model['id'],'measure_id':measure},
                'question':form_scope.document(request,self.workspace.intake_configuration)['text'],
                'retained_definition':model.get('business_definition',''),
                'limits':['No value or pipeline comparison was performed.',
                          'The engine does not decide business intent or correctness.']}
            def route(current):
                current=protocol.transition(current,'BUSINESS_VALIDATION',actor='AGENT',detail={
                    'owner':handoff['owner'],'package_hash':digest(handoff)})
                current['handoff']=handoff;return current
            return self.smart.tickets.update(saved['ticket']['id'],saved['revision'],route)
        if request['description'] and request.get('description_resolution')!='FORM_SELECTIONS' and not saved['ticket'].get('source_intake'):
            doc=form_scope.document(request,self.workspace.intake_configuration)
            source=self.workspace.intake.resolve({'text':doc['text'],
                'request_key':'form-description:'+saved['ticket']['id'],'parent_id':None},retain_extraction=True)
            def attach(current):
                current['source_intake']=source['id'];return current
            saved=self.smart.tickets.update(saved['ticket']['id'],saved['revision'],attach)
            if source['status']!='PROPOSED':
                return self._hold(saved,source.get('refusal_reason') or source.get('question') or source.get('error') or 'DESCRIPTION_REQUIRES_CLARIFICATION')
        description=None
        if saved['ticket'].get('source_intake') and request.get('description_resolution')!='FORM_SELECTIONS':
            source=self.workspace.intake.get(saved['ticket']['source_intake'])
            if source['status']!='PROPOSED':return self._hold(saved,'DESCRIPTION_REQUIRES_CLARIFICATION')
            description=source['proposal']
        try:
            scope=form_scope.resolved_scope(request,catalog['models'],self.workspace.intake_configuration,description)
            form_scope.build(request,catalog['models'],self.workspace.intake_configuration,description_proposal=description)
        except Conflict as exc:
            if str(exc).startswith('Description conflicts'):return self._conflict(saved,catalog,str(exc),description)
            if result['status']=='NEEDS_INPUT':return self._ask(saved,catalog,result)
            return self._hold(saved,str(exc))
        except ValueError as exc:return self._hold(saved,str(exc))
        def settle(current):
            for field,value in [('REPORT_PAGE',{k:scope[k] for k in ('report_id','page_id')}),
                                ('NUMBER',{k:scope[k] for k in ('target_id','cell_mode','reported_figure')}),
                                ('COMPARISON',{'route':scope['comparison']})]:
                current['settled'][field]={'authority':'USER_SUPPLIED_FORM' if request.get({'REPORT_PAGE':'report_id','NUMBER':'target_id','COMPARISON':'comparison'}[field]) is not None else 'VALIDATED_DESCRIPTION_AND_DEFINITION','value':copy.deepcopy(value)}
            return current
        saved=self.smart.tickets.update(saved['ticket']['id'],saved['revision'],settle)
        try:adopted=self.workspace.intake._adopt_form(saved)
        except (ValueError,Conflict) as exc:return self._hold(saved,str(exc))
        def ready(current):
            current['intake_id']=adopted['id']
            current['history'].append({'from':current['state'],'to':current['state'],'actor':'AGENT',
                'detail':{'scope_adopted':adopted['id'],'authority':'USER_SUPPLIED_FORM','provider_calls':0}})
            return current
        saved=self.smart.tickets.update(saved['ticket']['id'],saved['revision'],ready)
        return self.smart._start_settled(saved) if self.smart.auto_start else saved

    def _conflict(self,saved,catalog,reason,description):
        """A persisted user decision, never a model choice between inputs."""
        request=saved['ticket']['form_input'];p=description
        updates={'description_resolution':'FORM_SELECTIONS'}
        alternatives=[]
        if form_intake.resolve(request,catalog['models'],self.workspace.intake_configuration)['status']=='BOUND':
            alternatives.append(('Use my selected form details',updates))
        target=p.get('target_visual');binding=p.get('report_binding') or {}
        visual=next((v for m in catalog['models'] for v in m.get('visuals',[]) if target and v['target_id']==target['target_id']),None)
        if visual:
            figure=p.get('reported_figure',{'state':'UNSPECIFIED'})
            route=(p.get('ticket_route') or {}).get('route')
            alternatives.append(('Use the described '+next(iter(visual.get('names',[])),visual['target_id']),{
                'report_id':binding.get('report_id'),'page_id':visual['page_id'],'target_id':visual['target_id'],
                'cell_mode':target['mode'],'comparison':None if route=='DECLARED_SUBJECT' else route,
                'value_seen':figure.get('source',{}).get('quote'),
                'cell_keys':[{'column_id':f['column_id'],'value':f['values'][0]} for f in p.get('filters',[]) if target['mode']=='KEYED' and f['operator']=='in' and len(f['values'])==1]}))
        if not alternatives:return self._hold(saved,reason+'; no complete alternative is established')
        q={'id':'form-conflict-'+str(saved['revision']),'field':'NUMBER','question':reason+'. Which should I check?',
           'choices':[{'id':digest(v),'label':label,'highlight':None} for label,v in alternatives]}
        def offer(current):
            current=protocol.ask(current,[q],maximum=self.smart.configuration['max_clarifying_rounds'])
            current['form_choices']={digest(v):copy.deepcopy(v) for _,v in alternatives}
            return current
        return self.smart.tickets.update(saved['ticket']['id'],saved['revision'],offer)

    def _ask(self,saved,catalog,result):
        request=saved['ticket']['form_input'];wanted=result['questions'][0]['field'];options=[]
        if wanted=='REPORT_PAGE':
            for model in catalog['models']:
                for report in model.get('reports',[]):
                    if request['report_id'] and report['id']!=request['report_id']:continue
                    pages={v['page_id'] for v in model.get('visuals',[]) if v['report_id']==report['id']}
                    for page in sorted(pages):
                        sample=next(v for v in model['visuals'] if v['page_id']==page)
                        label=report.get('name',report['id'])+' / '+next(iter(sample.get('page_names',[])),page)
                        options.append((label,{'report_id':report['id'],'page_id':page}))
        elif wanted=='COMPARISON':
            from .ticket_clarification import settings
            options=[(c['label'],{'comparison':c['route']}) for c in settings(self.workspace.intake_configuration)['comparison_choices']]
        else:
            if result['questions'][0].get('reason')=='CELL_KEYS_UNRESOLVED':
                return self._hold(saved,'CELL_KEYS_UNRESOLVED: supply every grouped cell key; no total was substituted')
            for model in catalog['models']:
                for visual in model.get('visuals',[]):
                    if visual['report_id']!=request['report_id'] or visual['page_id']!=request['page_id']:continue
                    if visual.get('unsupported') or len(visual['measure_ids'])!=1:continue
                    if request['target_id'] and visual['target_id']!=request['target_id']:continue
                    modes=['TOTAL','KEYED'] if visual['grouping_columns'] else ['UNGROUPED']
                    for mode in modes:
                        label=next(iter(visual.get('names',[])),visual['target_id'])+' / '+{
                            'UNGROUPED':'single number','KEYED':'one row','TOTAL':'total row'}[mode]
                        options.append((label,{'target_id':visual['target_id'],'cell_mode':mode}))
        if not options:return self._hold(saved,'No executable retained choice for '+wanted)
        if len(options)>100:return self._hold(saved,'Form clarification choices exceed consumer bound')
        question={'id':'form-'+wanted.lower()+'-'+str(saved['revision']),'field':wanted,
            'question':{'NUMBER':'Which displayed cell do you mean?','REPORT_PAGE':'Which report and page?',
                        'COMPARISON':'What are you comparing against?'}[wanted],
            'choices':[{'id':digest(value),'label':label,'highlight':None} for label,value in options]}
        def offer(current):
            current=protocol.ask(current,[question],maximum=self.smart.configuration['max_clarifying_rounds'])
            current['form_choices']={digest(v):copy.deepcopy(v) for _,v in options}
            return current
        return self.smart.tickets.update(saved['ticket']['id'],saved['revision'],offer)

    @operation('form_reply')
    def reply(self,request):
        fields(request,['ticket_id','revision','answers','request_key'])
        saved=self.smart.tickets.get(request['ticket_id'])
        if not saved['ticket'].get('form_input'):raise ValueError('Ticket is not a form')
        prior=saved['ticket'].get('reply_keys',{}).get(request['request_key'])
        if prior is not None:
            if prior!=digest(request):raise Conflict('Form reply key changed')
            return saved
        catalog=snapshot(self.workspace)
        if digest(catalog)!=saved['ticket']['form_catalog_hash']:raise Conflict('Form choices are stale')
        def answer(current):
            updates={}
            for a in request['answers']:
                if not a.get('unavailable'):
                    updates.update(current['form_choices'][a['choice_id']])
            current=protocol.answer(current,request['answers'])
            current['form_input'].update(updates)
            current.setdefault('reply_keys',{})[request['request_key']]=digest(request)
            return current
        saved=self.smart.tickets.update(request['ticket_id'],request['revision'],answer)
        if saved['ticket']['state']=='HELD':return saved
        return self._plan(saved,catalog)
