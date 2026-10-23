"""Ticket-scoped graph/fact tools. Models select identifiers, never native SQL."""
import copy
from concurrent.futures import ThreadPoolExecutor
from jsonschema import Draft202012Validator
from .estate_graph_contract import canonical,timestamp
from .evidence_verdicts import Evidence,quantity


def literal_schema(value):
    if isinstance(value,dict):return {'type':'object','properties':{k:literal_schema(v) for k,v in value.items()},'required':list(value),'additionalProperties':False}
    if isinstance(value,list):return {'type':'array','items':{'anyOf':[literal_schema(v) for v in value]} if value else {},'minItems':len(value),'maxItems':len(value),'enum':[value]}
    kind='null' if value is None else 'boolean' if isinstance(value,bool) else 'number' if isinstance(value,(int,float)) else 'string'
    return {'type':kind,'enum':[value]}


class Tools:
    def __init__(self,graph,ledger,*,visual,now,persist,value_reader=None,collector=None,key=None,context=None,comparison=None,checks=None,request_kind='COMPARE',recording_class='EXACT'):
        from .privacy_capture import ACTIVE as PRIVACY_CAPTURE
        from .privacy_projection import ProjectionError
        if recording_class!='EXACT' or PRIVACY_CAPTURE.get() is not None:raise ProjectionError('LEDGER_INVESTIGATOR_PROJECTED_CAPTURE_NOT_INSTALLED')
        self.graph,self.ledger=graph,ledger;self.now=timestamp(now)
        self.visual,self.key,self.context=visual,key,copy.deepcopy(context or {})
        if request_kind not in ('FACT','COMPARE','DEFINITION'):raise ValueError('REQUEST_KIND_REQUIRED')
        self.request_kind=request_kind
        self.comparison=copy.deepcopy(comparison);self.reader=value_reader;self.collector=collector;self.checks=checks
        # GraphAPI must apply its path_records query; never request repository.records.
        self.path=copy.deepcopy(graph._slice([visual],traverse=False,path=True) if request_kind=='FACT' else graph.path_to_source(visual))
        if self.comparison and self.comparison.get('kind')=='report' and self.comparison.get('node') and self.comparison.get('node')!=visual:
            other=graph.path_to_source(self.comparison['node'])
            combined={node['id']:node for node in [*self.path['nodes'],*other['nodes']]}
            if len(combined)>200:raise ValueError('PAIRED_TICKET_PATH_BOUND')
            self.path['nodes']=list(combined.values())
            self.path['edges']=list({edge['id']:edge for edge in [*self.path['edges'],*other['edges']]}.values())
            self.path['stops']=[*self.path.get('stops',[]),*other.get('stops',[])]
            self.path['truncated']=self.path.get('truncated',False) or other.get('truncated',False)
        self.nodes={node['id']:node for node in self.path['nodes']}
        if visual not in self.nodes:raise ValueError('TARGET_NOT_IN_DECLARED_PATH')
        self.evidence=Evidence(self.nodes,persist);self._obtained={};self._reads={}
        self.depth={visual:0};queue=[visual]
        while queue:
            current=queue.pop(0)
            for edge in self.path['edges']:
                if edge['source']==current and edge['target'] in self.nodes and edge['target'] not in self.depth:
                    self.depth[edge['target']]=self.depth[current]+1;queue.append(edge['target'])
        self.path_id=self.evidence.add('PATH',list(self.nodes),self.path)
        self.gap_ids=[]
        for stop in self.path.get('stops',[]):
            if stop.get('node') in self.nodes:self.gap_ids.append(self.evidence.add('GAP',[stop['node']],{'reason':stop['reason']}))
        if self.path.get('truncated'):self.gap_ids.append(self.evidence.add('GAP',[visual],{'reason':'Ticket graph path is truncated at the configured slice limit.'}))
        self.boundary_ids=[]
        for edge in self.path['edges']:
            contract=edge.get('properties',{}).get('comparison_contract')
            if not contract:continue
            if edge.get('confidence') not in ('DECLARED','VERIFIED','VALUE_VERIFIED') or edge.get('provenance',{}).get('source')=='MODEL_PROPOSAL' or edge.get('verification',{}).get('state')=='STALE':
                self.gap_ids.append(self.evidence.add('GAP',[edge['source'],edge['target']],{'reason':'The proposed producer boundary is inferred, stale or unestablished.'}));continue
            if (set(contract)!={'job','quantity_preserving','kind'} or contract['job'] not in self.nodes
                    or type(contract['quantity_preserving'])is not bool):raise ValueError('BOUNDARY_CONTRACT_NOT_ON_PATH')
            self.boundary_ids.append(self.evidence.add('BOUNDARY',[edge['source'],edge['target'],contract['job']],
                {'downstream':edge['source'],'upstream':edge['target'],**contract,'edge_id':edge['id'],'support_ids':[self.path_id]}))
        names={'node_facts':['node'],'last_run':['job'],'last_refresh':['model'],'definition_of':['node'],
               'definition_diff':['node','from_time','to_time'],'refresh_facts':['path'],
               'compare_layers':['key','layers','filters'],'path_to_source':['visual'],
               'visual_context':['report','page','visual'],'filters_on':['page'],'table_columns':['table'],
               'freshness':['node'],'as_of':['node','at'],'get_evidence':['id'],'check_explanation':['comparison_id','kind']}
        self.schemas={}
        for name,fields in names.items():
            props={}
            for field in fields:
                if field in ('layers','path'):props[field]={'type':'array','minItems':1,'maxItems':100,'uniqueItems':True,'items':{'type':'string','enum':sorted(self.nodes)}}
                elif field=='filters':props[field]=literal_schema(self.context)
                elif field=='key':props[field]=literal_schema(self.key)
                elif field=='kind':props[field]={'enum':['DESIGN_CHECK','ACCESS_CHECK','HISTORY_CHECK']}
                elif field in ('from_time','to_time','at','id','comparison_id'):props[field]={'type':'string','minLength':1}
                else:props[field]={'type':'string','enum':sorted(self.nodes)}
            self.schemas[name]={'type':'object','properties':props,'required':fields,'additionalProperties':False}

    def _read(self,node,context):
        if node not in self.nodes:raise ValueError('READ_OUTSIDE_TICKET_PATH')
        if not hasattr(self,'_quantity_attempted'):self._quantity_attempted=set()
        self._quantity_attempted.add(node)
        cache_key=canonical([node,self.key,context])
        if cache_key in self._reads:return self._reads[cache_key]
        if self.reader is None:return self.evidence.add('GAP',[node],{'reason':'No guarded compiled quantity reader is installed for this graph node.'})
        from .source_availability import call as source_call, fact as availability_fact
        observations=[]
        def observe(value):
            ref=self.evidence.add('FACT',[node],availability_fact(node,value,at=value['last_observed_at'],evidence=[self.path_id],collector='investigator-read'))
            observations.append(ref)
        def settle_availability():
            estate=getattr(self,'estate',None)
            if not observations or not estate or not hasattr(self.ledger,'append'):return
            ref=observations[-1]
            try:self.ledger.append(estate,[self.evidence.get(ref)['value']])
            except ValueError as error:
                if str(error)!='FACT_SUBJECT_NOT_IN_GRAPH':raise
                # Retained continuation is not current graph-insertion authority.
                self.evidence.persist({'event':'AVAILABILITY_NOT_CURRENT_GRAPH_MEMBER','subject':node,'evidence_id':ref})
        try:
            result=copy.deepcopy(source_call(lambda:self.reader(node,self.key,copy.deepcopy(context)),observe=observe,clock=getattr(self,'availability_clock',lambda:self.now)))
        except Exception as exc:
            from .estate_graph_incremental import is_stop_condition
            if is_stop_condition(exc):raise
            settle_availability()
            from .source_availability import result as availability_result
            unavailable=getattr(exc,'source_availability',None) or availability_result(exc,at=self.now)
            return self.evidence.add('GAP',[node],{'reason':unavailable['message'],'error_type':type(exc).__name__,'availability':unavailable})
        settle_availability()
        if (not isinstance(result,dict) or result.get('subject')!=node or result.get('key')!=self.key
                or canonical(result.get('context'))!=canonical(context) or not result.get('receipt_id')
                or result.get('route_admitted')is not True or result.get('read_only_verified')is not True):
            raise ValueError('COMPILED_READ_ADMISSION_OR_SCOPE_DIFFERS')
        quantity(result)
        identity=self.evidence.add('READ',[node],result);self._reads[cache_key]=identity
        return identity

    def pending_quantity_nodes(self):
        if self.request_kind!='COMPARE' or self.reader is None:return []
        attempted=getattr(self,'_quantity_attempted',set())
        return [node for node in self.nodes if self.nodes[node]['kind']in ('TABLE','VIEW','SOURCE')and node not in attempted]

    def reproduce(self):
        if self.request_kind!='COMPARE':return []
        refs=[self._read(self.visual,self.context)]
        comparison=self.comparison
        if comparison:
            if comparison['kind'] in ('spreadsheet','own count','earlier value'):
                refs.append(self.evidence.add('GIVEN_COMPARISON',[self.visual],{'value':comparison['value'],'kind':comparison['kind'],'provenance':'TICKET_GIVEN_NOT_RECREATED'}))
            elif comparison['kind'] in ('report','source'):
                target=comparison.get('node')
                if target not in self.nodes:
                    refs.append(self.evidence.add('GAP',[self.visual],{'reason':'The ticket names a '+comparison['kind']+
                        ' comparison, but no comparison target is resolved within the admitted graph path. No comparison read was made; the named comparison was not replaced.',
                        'code':'COMPARISON_TARGET_UNAVAILABLE','comparison_kind':comparison['kind']}))
                    return refs
                other=self._read(target,comparison.get('context',self.context));refs.append(other)
                if all(self.evidence.get(i)['kind']=='READ' for i in refs):
                    refs.append(self._comparison(refs[0],other))
            else:raise ValueError('COMPARISON_KIND_UNSUPPORTED')
        return refs

    def _comparison(self,left,right):
        a=self.evidence.get(left);b=self.evidence.get(right)
        if a['kind']!='READ' or b['kind']!='READ':raise ValueError('COMPARISON_REQUIRES_COMPLETED_READS')
        return self.evidence.add('COMPARISON',a['subjects']+b['subjects'],{'left':left,'right':right,'support_ids':[left,right]})

    def quick_checks(self):
        # Independent read-only ledger lookups, no model/provider calls. Each
        # FactLedger.read owns its transaction; no DB connection crosses threads.
        with ThreadPoolExecutor(max_workers=min(4,len(self.nodes))) as pool:
            results=list(pool.map(lambda node:self.graph.node_facts(node,now=self.now),sorted(self.nodes)))
        if self.collector is not None:
            expected={'PIPELINE':('JOB_RUN',),'NOTEBOOK':('JOB_RUN',),'COPY_ACTIVITY':('JOB_RUN',),'MODEL':('REFRESH_RUN','REFRESH_STATE'),'TABLE':('TABLE_LOAD',),'VIEW':('TABLE_LOAD',),'SOURCE':('TABLE_LOAD',)}
            needed=[]
            for node,result in zip(sorted(self.nodes),results):
                kinds=expected.get(self.nodes[node]['kind'],())
                relevant=[v for v in result['facts'] if v['kind'] in kinds]
                if kinds and (not relevant or any(v['freshness']=='STALE' or v['state']=='UNAVAILABLE' for v in relevant)):needed.append(node)
            if needed:
                refreshed=self.graph.refresh_facts(needed,self.collector,now=self.now,required_kinds={node:expected.get(self.nodes[node]['kind'],()) for node in needed})
                replacements={(v['subject'],v['kind']):v for v in refreshed.get('facts',[])}
                for node,result in zip(sorted(self.nodes),results):
                    result['facts']=[v for v in result['facts'] if (node,v['kind']) not in replacements]+[v for (subject,_),v in replacements.items() if subject==node]
        refs=[]
        for node,result in zip(sorted(self.nodes),results):
            for value in result['facts']:
                if value['subject']!=node:raise ValueError('FACT_OUTSIDE_REQUESTED_NODE')
                refs.append(self.evidence.add('FACT',[node],value))
        return refs

    def invoke(self,name,args):
        if name not in self.schemas:raise ValueError('UNKNOWN_INVESTIGATOR_TOOL')
        Draft202012Validator(self.schemas[name]).validate(args)
        key=canonical([name,args])
        if key in self._obtained:
            if name=='get_evidence':return {'evidence_ids':[args['id']],'already_obtained':True,'note':'Already obtained this evidence; its factual summary remains in the evidence index.'}
            return {**copy.deepcopy(self._obtained[key]),'already_obtained':True}
        if name=='get_evidence':
            result={'evidence_ids':[args['id']],'evidence':self.evidence.get(args['id'])}
            self._obtained[key]=copy.deepcopy(result)
            return result
        if name=='compare_layers':
            if len(args['layers'])<2:raise ValueError('TWO_LAYERS_REQUIRED')
            refs=[self._read(node,args['filters']) for node in args['layers']]
            if any(self.evidence.get(i)['kind']!='READ' for i in refs):result={'evidence_ids':refs,'status':'UNAVAILABLE'}
            else:result={'evidence_ids':[*refs,*[self._comparison(a,b) for a,b in zip(refs,refs[1:])]],'status':'OBSERVED'}
        elif name=='check_explanation':
            comparison=self.evidence.get(args['comparison_id'])
            if comparison['kind']!='COMPARISON':raise ValueError('CHECK_REQUIRES_COMPARISON')
            if self.checks is None:
                ref=self.evidence.add('GAP',comparison['subjects'],{'reason':args['kind']+' producer is not installed.'});result={'evidence_ids':[ref],'status':'UNAVAILABLE'}
            else:
                value=copy.deepcopy(self.checks(args['kind'],copy.deepcopy(comparison),self.evidence.resolve([args['comparison_id']])))
                value['support_ids']=list(dict.fromkeys([args['comparison_id'],*value.get('support_ids',[])]))
                # Dependencies must already be registered, not supplied model receipts.
                self.evidence.resolve(value['support_ids'])
                ref=self.evidence.add(args['kind'],comparison['subjects'],value);result={'evidence_ids':[ref],'status':'OBSERVED'}
        elif name in ('node_facts','last_run','last_refresh'):
            node=args.get('node') or args.get('job') or args.get('model');value=self.graph.node_facts(node,now=self.now)
            kinds={'last_run':{'JOB_RUN','RUN_HISTORY','COVERAGE'},'last_refresh':{'REFRESH_RUN','REFRESH_STATE','RUN_HISTORY','COVERAGE'}}.get(name)
            values=[v for v in value['facts'] if kinds is None or v['kind'] in kinds]
            available=any(v.get('state') in ('OBSERVED','OBSERVED_NEGATIVE') and v.get('freshness')=='CURRENT' for v in values)
            result={'evidence_ids':[self.evidence.add('FACT',[node],v) for v in values],'facts':values,'status':'OBSERVED' if available else 'UNAVAILABLE'}
            if not result['evidence_ids']:result['evidence_ids']=[self.evidence.add('GAP',[node],{'reason':'No retained '+name+' observation.'})]
        elif name=='definition_diff':
            if timestamp(args['from_time'])>=timestamp(args['to_time']):raise ValueError('DEFINITION_DIFF_TIME_ORDER')
            node=args['node'];a=self.graph.as_of(args['from_time']).definition_of(node);b=self.graph.as_of(args['to_time']).definition_of(node)
            value={'before':a,'after':b,'changed':a.get('definition')!=b.get('definition')}
            result={'evidence_ids':[self.evidence.add('DEFINITION_DIFF',[node],value)],'result':value}
        elif name=='refresh_facts':
            if self.collector is None:
                result={'evidence_ids':[self.evidence.add('GAP',args['path'],{'reason':'Path collector is not installed.'})],'status':'UNAVAILABLE'}
            else:
                value=self.graph.refresh_facts(args['path'],self.collector,now=self.now)
                fact_ids=[self.evidence.add('FACT',[fact['subject']],fact) for fact in value.get('facts',[]) if fact['subject'] in args['path']]
                result={'evidence_ids':[self.evidence.add('FACT_REFRESH',args['path'],value),*fact_ids],'result':value}
        else:
            call_args=copy.deepcopy(args);subjects=[v for k,v in args.items() if k not in ('at',)]
            if name=='path_to_source':
                if args['visual']!=self.visual:raise ValueError('TARGET_VISUAL_SUBSTITUTION')
                value=copy.deepcopy(self.path)
            elif name=='as_of':value=self.graph.as_of(args['at']).definition_of(args['node'])
            elif name=='freshness':value=self.graph.freshness(args['node'],now=self.now)
            else:value=getattr(self.graph,name)(**call_args)
            result={'evidence_ids':[self.evidence.add('GRAPH',subjects,value)],'result':value}
        self._obtained[key]=copy.deepcopy(result);return result
