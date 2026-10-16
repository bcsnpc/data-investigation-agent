"""Confirmed page claims: explicit coverage and bounded observation, not cause."""
import copy,itertools
from decimal import Decimal,InvalidOperation
from .onboarding import Conflict,digest
from .claim_facts import merge
from .declared_reproduction import compose

KINDS=('PAGE_CONSISTENCY','PAGE_FRESHNESS')
LIMITS=['These observations use the retained definitions and the admitted reader.',
        'SNAPSHOT_UNVERIFIED: the value reads do not establish an aligned served version.',
        'A differing declared context or observed value does not establish a cause or business correctness.',
        'Scoring requires a readiness assessment for the actual requested capability and scope.']

def equal(left,right):
    if left is None or right is None:return left is right
    try:return Decimal(left)==Decimal(right)
    except (InvalidOperation,ValueError,TypeError):return left==right

class PageInvestigations:
    def __init__(self,workspace):self.workspace=workspace

    def _catalog(self):
        from .question_intake import snapshot
        return snapshot(self.workspace)

    def _hold(self,kind,reason,**extra):
        summary='The page check could not proceed with a faithful confirmed scope. No value or freshness conclusion was made.'
        return {'kind':kind,'status':'HELD','outcome':'INSUFFICIENT_EVIDENCE','reason':reason,
                'summary':summary,'business_summary':summary,'technical_summary':kind+': '+reason,'evidence':[],
                'limitations':list(LIMITS),'snapshot_status':'SNAPSHOT_UNVERIFIED',
                'scoring':'NOT_SCORED_ESTATE_GATE',**extra}

    def prepare(self,body,kind='PAGE_CONSISTENCY'):
        if kind not in KINDS:raise ValueError('Unknown page check kind')
        claim=body.get('claim',{});confirmation=body.get('confirmation')or{};admission=body.get('engine_admission')or{}
        if (body.get('status')!='CONFIRMED' or confirmation.get('authority')!='USER_CONFIRMED'
                or confirmation.get('interpretation_hash')!=digest(body.get('interpretation'))
                or admission.get('claim_hash')!=digest(claim) or admission.get('confirmation_hash')!=digest(confirmation)):
            return self._hold(kind,'CONFIRMED_RETAINED_CLAIM_REQUIRED')
        try:merge([],claim.get('facts',[]))
        except (ValueError,KeyError,TypeError):return self._hold(kind,'CLAIM_FACT_INTEGRITY_DIFFERS')
        catalog=self._catalog()
        if body.get('catalog_hash')!=digest(catalog) or confirmation.get('catalog_hash')!=digest(catalog):
            from .claim_clarification import interpretation
            try:current_interpretation=interpretation(claim,catalog)
            except (ValueError,KeyError,TypeError):return self._hold(kind,'CURRENT_CONFIRMED_CATALOG_REQUIRED')
            if digest(current_interpretation)!=confirmation['interpretation_hash']:
                return self._hold(kind,'CURRENT_CONFIRMED_CATALOG_REQUIRED')
        captured=body.get('captured_context')
        screenshot_docs=[d for d in body.get('documents',[])if d.get('request',{}).get('screenshot_evidence')]
        if captured or screenshot_docs:
            # Reload the authoritative marker, not a producer/client complete:true.
            identity=(captured or{}).get('review_id')or screenshot_docs[0]['request']['screenshot_evidence']['review_id']
            try:review=self.workspace.claim_screenshots.load(identity,catalog)
            except (Conflict,KeyError,ValueError):return self._hold(kind,'SCREENSHOT_CONTEXT_UNAVAILABLE')
            if captured and captured.get('review_hash')!=review['hash']:return self._hold(kind,'SCREENSHOT_REVIEW_HASH_DIFFERS')
            marker=review.get('visible_filter_scope')or{}
            # No complete screenshot-scope compiler exists in the installed port.
            # Any absence/positive producer label alone is not positive scope proof.
            return self._hold(kind,'SCREENSHOT_FILTER_SCOPE_NOT_COMPILED',captured_context={
                'review_id':identity,'review_hash':review['hash'],'visible_filter_scope':marker})
        settled=claim.get('settled',{});scope=copy.deepcopy(settled.get('scope')or{})
        if scope.get('kind')not in('PAGE','REPORT','VISUALS','METRIC')or not scope.get('report_id'):
            return self._hold(kind,'CONFIRMED_REPORT_SCOPE_REQUIRED')
        if scope['kind']in('PAGE','VISUALS','METRIC')and not scope.get('page_id'):return self._hold(kind,'CONFIRMED_PAGE_REQUIRED')
        if settled.get('time'):return self._hold(kind,'TIME_SCOPE_NOT_COMPILED')
        filters=copy.deepcopy(settled.get('filters',[]))
        if len(filters)==1 and isinstance(filters[0],list):filters=filters[0]
        if not isinstance(filters,list)or len(filters)>8 or any(not isinstance(f,dict)or set(f)!={'column_id','operator','value'}or
                not isinstance(f.get('column_id'),str)or f.get('operator')not in('EQ','IN')or
                (f['operator']=='IN'and(not isinstance(f['value'],list)or not f['value']))or
                (f['operator']=='EQ'and isinstance(f['value'],(dict,list)))for f in filters):
            return self._hold(kind,'FILTER_SCOPE_NOT_COMPILED')
        filters=[{'column_id':f['column_id'],'values':f['value']if f['operator']=='IN'else[f['value']]}for f in filters]
        models=[m for m in catalog['models']if any(r['id']==scope['report_id']for r in m.get('reports',[]))]
        binding=claim.get('selected_binding')or{}
        bindings=binding.get('bindings',[])if binding.get('kind')=='MULTIPLE'else([binding]if binding else[])
        if scope['kind']=='METRIC':
            scope.update(kind='VISUALS',visual_ids=list(dict.fromkeys(t for b in bindings for t in b.get('target_ids',[]))))
        bound_models={b.get('model_id')for b in bindings if b.get('model_id')}
        if len(bound_models)>1:return self._hold(kind,'CROSS_MODEL_PAGE_SCOPE_UNSUPPORTED')
        if bound_models:models=[m for m in models if m['id']in bound_models]
        if len(models)!=1:return self._hold(kind,'REPORT_MODEL_BINDING_UNRESOLVED')
        model=models[0]
        if any(b.get('report_id')not in(None,scope['report_id'])or(scope['kind']in('PAGE','VISUALS')and b.get('page_id')not in(None,scope.get('page_id')))for b in bindings):
            return self._hold(kind,'CONFIRMED_BINDING_SCOPE_DIFFERS')
        visuals=[v for v in model.get('visuals',[])if v['report_id']==scope['report_id']and(scope['kind']=='REPORT'or v.get('page_id')==scope.get('page_id'))]
        if any(t not in {v['target_id']for v in visuals}for b in bindings for t in b.get('target_ids',[])):
            return self._hold(kind,'CONFIRMED_TARGET_LEAVES_PAGE_SCOPE')
        if scope['kind']=='VISUALS':
            ids=scope.get('visual_ids')
            if not isinstance(ids,list)or not ids or any(t not in {v['target_id']for v in visuals}for t in ids):return self._hold(kind,'EXPLICIT_VISUAL_INVENTORY_REQUIRED')
            visuals=[v for v in visuals if v['target_id']in ids]
        if not visuals:return self._hold(kind,'NO_RETAINED_VISUALS_IN_SCOPE')
        if len(visuals)>60:return self._hold(kind,'PAGE_VISUAL_INVENTORY_EXCEEDS_BOUND')
        requested={b['measure_id']for b in bindings if b.get('measure_id')}
        all_measures={m['id']:m for m in model.get('measures',[])}
        if requested-set(all_measures):return self._hold(kind,'CONFIRMED_METRIC_NOT_CURRENT')
        if not requested and kind=='PAGE_CONSISTENCY':
            return self._hold(kind,'CONFIRMED_METRIC_BINDING_REQUIRED')
        if not requested:requested={m for v in visuals for m in v['measure_ids']}
        if not requested:return self._hold(kind,'NO_METRIC_SOURCES_IN_SCOPE')
        report=next(r for r in model['reports']if r['id']==scope['report_id'])
        dispositions=[];candidates=[]
        for visual in visuals:
            names=[n for n in visual.get('names',[])if n not in visual.get('page_names',[])]
            label=', '.join(names)or ', '.join(all_measures[m]['name']for m in visual['measure_ids']if m in all_measures)or'Retained visual'
            row={'visual_id':visual['target_id'],'label':label,'report_name':report['name'],
                 'page_name':', '.join(visual.get('page_names',[]))or'Retained page','measure_ids':list(visual['measure_ids']),'measure_dispositions':[]}
            relevant=sorted(set(visual['measure_ids'])&requested)
            if not relevant:row.update(disposition='OTHER_METRIC',reason='Not the confirmed metric')
            elif visual.get('unsupported'):row.update(disposition='UNSUPPORTED',reason=visual['unsupported'])
            elif kind=='PAGE_CONSISTENCY'and visual.get('grouping_columns'):
                row.update(disposition='UNRESOLVED_GROUPED_CELL',reason='No implicit total or group key was selected')
            else:
                row.update(disposition='PLANNED',reason=None)
                for measure in relevant:
                    declaration=visual.get('declared_scopes',{}).get(measure)
                    if kind=='PAGE_CONSISTENCY'and(not declaration or declaration.get('state')!='COMPLETE'):
                        row['measure_dispositions'].append({'measure_id':measure,'disposition':'INCOMPLETE_DECLARED_SCOPE'})
                        row.update(disposition='INCOMPLETE_DECLARED_SCOPE',reason='The retained visual scope is incomplete');continue
                    row['measure_dispositions'].append({'measure_id':measure,'disposition':'PLANNED'})
                    if kind=='PAGE_CONSISTENCY':
                        restrictions=compose(declaration['restrictions']+[{'field_id':f['column_id'],'operator':'IN','values':f['values']}for f in filters])
                        candidates.append({'model_id':model['id'],'target_id':visual['target_id'],'measure_id':measure,
                            'measure_name':all_measures[measure]['name'],'label':label,'mode':'UNGROUPED',
                            'scope':{'filters':copy.deepcopy(filters)},'declaration':copy.deepcopy(declaration),
                            'comparison_scope_hash':digest({'model_id':model['id'],'context_id':declaration['context_id'],
                                'context_hash':declaration['context_hash'],'measure_id':measure,'restrictions':restrictions})})
            dispositions.append(row)
        return {'kind':kind,'status':'PLANNED','model_id':model['id'],'measure_ids':sorted(requested),'scope':scope,
                'report_name':report['name'],'visuals':copy.deepcopy(visuals),'candidates':candidates,
                'coverage':{'scope_kind':scope['kind'],'requested_visual_ids':[v['target_id']for v in visuals],
                            'dispositions':dispositions,'checked_visual_ids':[]},'limitations':list(LIMITS)}

    def _admitted(self,body,adapter,kind):
        plan=self.prepare(body,kind)
        if plan['status']=='HELD':return plan
        if getattr(adapter,'model',{}).get('id')!=plan['model_id']:
            return self._hold(kind,'ADMITTED_MODEL_DIFFERS',coverage=plan['coverage'])
        current=self.workspace.store.get(plan['model_id'])
        if not current.get('enabled')or digest(current.get('context'))!=digest(adapter.model.get('context'))or current.get('revision')!=adapter.model.get('revision'):
            return self._hold(kind,'ADMITTED_CONTEXT_NOT_CURRENT',coverage=plan['coverage'])
        inventory=getattr(adapter,'page_visual_inventory',None)
        if not callable(inventory):return self._hold(kind,'PAGE_VISUAL_INVENTORY_UNAVAILABLE',coverage=plan['coverage'])
        raw=inventory(plan['scope']);existing=set(plan['coverage']['requested_visual_ids'])
        if len({v['visual_id']for v in raw})!=len(raw)or not existing<={v['visual_id']for v in raw}:
            return self._hold(kind,'PAGE_VISUAL_INVENTORY_INCOMPLETE',coverage=plan['coverage'])
        for visual in raw:
            if visual['visual_id']in existing:continue
            if visual.get('has_metric'):return self._hold(kind,'RETAINED_METRIC_VISUAL_WAS_OMITTED',coverage=plan['coverage'])
            plan['coverage']['requested_visual_ids'].append(visual['visual_id'])
            plan['coverage']['dispositions'].append({'visual_id':visual['visual_id'],'label':visual['label'],'measure_ids':[],
                'measure_dispositions':[],'disposition':'NON_QUANTITY_VISUAL','reason':'No metric is projected by this retained visual'})
        return plan

    def consistency(self,body,adapter):
        kind='PAGE_CONSISTENCY';plan=self._admitted(body,adapter,kind)
        if plan['status']=='HELD':return plan
        reader=getattr(adapter,'read_visual_quantity',None);verifier=getattr(adapter,'verify_visual_quantity',None)
        if not callable(reader)or not callable(verifier):return self._hold(kind,'PAGE_QUANTITY_READER_UNAVAILABLE',coverage=plan['coverage'])
        evidence=[];observed=[];failures={};coverage=copy.deepcopy(plan['coverage'])
        for candidate in plan['candidates']:
            try:probe=verifier(copy.deepcopy(candidate),reader(copy.deepcopy(candidate)))
            except (ValueError,KeyError,TypeError)as exc:
                failures[candidate['target_id']]=str(exc);continue
            attestation=probe.get('attestation',{})
            if probe.get('id')and probe.get('status')!='OBSERVED':evidence.append(copy.deepcopy(probe))
            if (probe.get('status')!='OBSERVED'or probe.get('complete')is not True or probe.get('surface_report_binding')!='VALUE_QUERY'
                    or attestation.get('consistency')!='MATCHED'or attestation.get('missing_required_fields')or not probe.get('id')
                    or probe.get('receipt_seal',{}).get('state')!='SEALED'):
                failures[candidate['target_id']]=probe.get('reason','Complete query-bound sealed observation required');continue
            evidence.append(copy.deepcopy(probe));observed.append((candidate,probe))
        for row in coverage['dispositions']:
            for metric in row['measure_dispositions']:
                if metric['disposition']=='INCOMPLETE_DECLARED_SCOPE':continue
                metric['disposition']='OBSERVED'if any(c['target_id']==row['visual_id']and c['measure_id']==metric['measure_id']for c,p in observed)else'UNAVAILABLE'
            if row['visual_id']in failures:row.update(disposition='UNAVAILABLE',reason=failures[row['visual_id']])
            elif row['disposition']=='PLANNED'and row['measure_dispositions']and all(m['disposition']=='OBSERVED'for m in row['measure_dispositions']):
                row.update(disposition='OBSERVED');coverage['checked_visual_ids'].append(row['visual_id'])
        comparisons=[]
        for (left,a),(right,b)in itertools.combinations(observed,2):
            if left['measure_id']!=right['measure_id']:outcome='NOT_COMPARABLE';reason='DIFFERENT_METRIC_BINDING'
            elif left['comparison_scope_hash']!=right['comparison_scope_hash']:outcome='NOT_COMPARABLE';reason='DIFFERENT_DECLARED_RESTRICTIONS'
            else:outcome='OBSERVED_AGREEMENT'if equal(a['value'],b['value'])else'OBSERVED_DIFFERENCE';reason=None
            comparisons.append({'left_visual_id':left['target_id'],'right_visual_id':right['target_id'],
                'left_label':left['label'],'right_label':right['label'],'measure_name':left['measure_name'],
                'outcome':outcome,'reason':reason,'left_value':a['value'],'right_value':b['value'],
                'evidence_ids':[a['id'],b['id']],'snapshot_status':'SNAPSHOT_UNVERIFIED','cause_established':False})
        comparable=[c for c in comparisons if c['outcome']!='NOT_COMPARABLE']
        overall='OBSERVED_DIFFERENCE'if any(c['outcome']=='OBSERVED_DIFFERENCE'for c in comparable)else'OBSERVED_AGREEMENT'if comparable else'NOT_COMPARABLE'
        partial=any(r['disposition']not in('OBSERVED','OTHER_METRIC','NON_QUANTITY_VISUAL')for r in coverage['dispositions'])
        summary=('Checked '+str(len(coverage['checked_visual_ids']))+' addressed visual(s) in '+plan['report_name']+'. ')
        if overall=='OBSERVED_DIFFERENCE':summary+='The reader returned different values under matching declared restrictions; an aligned snapshot and the cause are not established.'
        elif overall=='OBSERVED_AGREEMENT':summary+='The comparable reader values agreed under matching declared restrictions; this does not establish the rendered page or a shared served version.'
        else:summary+='No pair supported a same-context comparison; different restrictions, metrics or unavailable cells were not called defects.'
        if partial:summary+=' Some requested visuals remain unassessed; whole-page agreement was not established.'
        details=['Comparing '+c['left_label']+' and '+c['right_label']+': '+str(c['left_value'])+' versus '+str(c['right_value'])+
            (' under different declared restrictions.'if c['reason']=='DIFFERENT_DECLARED_RESTRICTIONS'else' for different metric bindings.'if c['reason']else' under matching declared restrictions.')for c in comparisons]
        business=summary+(' '+' '.join(details)if details else'')
        technical=business
        return {'kind':kind,'status':'PARTIAL'if partial else'NOT_COMPARABLE'if overall=='NOT_COMPARABLE'else'OBSERVED','outcome':overall,'summary':business,
            'business_summary':business,'technical_summary':technical,
            'coverage':coverage,'comparisons':comparisons,'evidence':evidence,'limitations':plan['limitations'],
            'snapshot_status':'SNAPSHOT_UNVERIFIED','cause_established':False,'scoring':'NOT_SCORED_ESTATE_GATE'}

    def freshness(self,body,adapter):
        kind='PAGE_FRESHNESS';plan=self._admitted(body,adapter,kind)
        if plan['status']=='HELD':return plan
        coverage=copy.deepcopy(plan['coverage']);evidence=[];timings=[];missing=[];load_cache={};refresh=None;covered_measures=set()
        available=set(adapter.capabilities())
        for measure in plan['measure_ids']:
            path=adapter.resolve_path(measure)
            if not isinstance(path,dict)or not path.get('layers'):
                missing.append({'measure_id':measure,'reason':'RESOLVED_SOURCE_PATH_UNAVAILABLE'});continue
            covered_measures.add(measure)
            if refresh is None:
                reader=getattr(adapter,'read_page_refresh',None)
                refresh=reader(path)if 'refresh_timing'in available and callable(reader)else{'status':'UNAVAILABLE','reason':'REFRESH_TIMING_CAPABILITY_UNDECLARED'}
                if refresh.get('status')=='OBSERVED'and refresh.get('evidence'):
                    evidence.append(copy.deepcopy(refresh['evidence']))
                else:missing.append({'layer':path['layers'][0]['id'],'kind':'REFRESH','reason':refresh.get('reason','REFRESH_TIMESTAMP_UNAVAILABLE')})
            boundaries=adapter.freshness_boundaries(path)if hasattr(adapter,'freshness_boundaries')else[]
            # The producer is carried by the input descriptor, but its run
            # completes the output layer of that boundary.
            by_upper={b['upper']['id']:b for b in boundaries}
            for index,layer in enumerate(path['layers']):
                role=next((r for r in adapter.config.get('layer_roles',[])if r['asset_id']==layer['id']),{})
                display=role.get('business_name')or role.get('role')or'Declared layer'
                row={'layer_id':layer['id'],'role':role.get('role','UNDECLARED'),'label':display,
                     'measure_id':measure,'last_refresh':None,'last_load':None,'evidence_ids':[],'scope':'RETAINED_ITEM_TIMING_ONLY'}
                if index==0 and refresh.get('status')=='OBSERVED'and refresh.get('evidence'):
                    row['last_refresh']={k:refresh.get(k)for k in('timestamp','started_at','run_id','timestamp_kind')};row['evidence_ids'].append(refresh['evidence']['id'])
                boundary=by_upper.get(layer['id'])
                if boundary:
                    producer=boundary['lower'].get('transformation_asset_id')
                    if producer not in load_cache:
                        reader=getattr(adapter,'read_page_load',None)
                        load_cache[producer]=reader(boundary)if callable(reader)else{'status':'UNAVAILABLE','reason':'LOAD_TIMING_READER_UNAVAILABLE'}
                    result=load_cache[producer];native_evidence=result.get('evidence')
                    if result.get('status')=='OBSERVED'and native_evidence and native_evidence.get('id'):
                        identity=native_evidence['id']
                        if identity not in {e['id']for e in evidence}:evidence.append(copy.deepcopy(native_evidence))
                        row['last_load']={k:result.get(k)for k in('timestamp','started_at','run_id','timestamp_kind','capture_currency_established')};row['evidence_ids'].append(identity)
                    else:missing.append({'layer':layer['id'],'kind':'LOAD','reason':result.get('reason','SUCCESSFUL_LOAD_TIMESTAMP_UNAVAILABLE')})
                elif index>0:missing.append({'layer':layer['id'],'kind':'LOAD','reason':'DECLARED_PRODUCER_TIMING_BINDING_UNAVAILABLE'})
                timings.append(row)
        for row in coverage['dispositions']:
            if row['disposition']=='PLANNED':
                reached=set(row['measure_ids'])&set(plan['measure_ids'])
                row['disposition']='TIMING_PATH_ATTEMPTED'if reached<=covered_measures else'TIMING_PATH_UNAVAILABLE'
                if row['disposition']=='TIMING_PATH_ATTEMPTED':coverage['checked_visual_ids'].append(row['visual_id'])
        found=sum(bool(t['last_refresh'])+bool(t['last_load'])for t in timings)
        details=[]
        for row in timings:
            for field,name in(('last_refresh','refresh'),('last_load','load')):
                value=row[field]
                details.append(row['label']+' '+name+': '+(value['timestamp']if value else'unavailable')+'.')
        summary=' '.join(details)+' Missing timing remains unknown; current freshness and the rendered page currency are not established.'
        return {'kind':kind,'status':'UNAVAILABLE'if not found else'PARTIAL'if missing else'OBSERVED','outcome':'TIMING_OBSERVED'if found else'TIMING_UNAVAILABLE',
            'summary':summary,'business_summary':summary,'technical_summary':summary,
            'coverage':coverage,'timings':timings,'missing':missing,'evidence':evidence,
            'limitations':plan['limitations']+['Retained refresh/job history is not proof of the latest actual data load or of the rendered page currency. No freshness deadline policy was supplied.'],
            'snapshot_status':'SNAPSHOT_UNVERIFIED','freshness_established':False,'scoring':'NOT_SCORED_ESTATE_GATE'}
