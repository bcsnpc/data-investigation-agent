"""Path-driven read tools. Models supply query text; code never synthesizes it."""
from copy import deepcopy
from decimal import Decimal,localcontext,ROUND_HALF_EVEN
from collections import deque
from datetime import datetime
import re
from .ai_investigation import schema


def compare_figure(figure,value):
    if figure['state']=='EMPTY':return {'matches':value is None,'precision':'EMPTY_STATE','weaker_claim':False}
    if value is None:return {'matches':False,'precision':figure['precision'],'weaker_claim':figure['precision']!='EXACT'}
    with localcontext() as context:
        context.prec=256
        actual,expected=Decimal(str(value)),Decimal(figure['value'])
        if not actual.is_finite() or not expected.is_finite():raise ValueError('FINITE_VALUE_REQUIRED')
        precision=figure['precision']
        if precision!='EXACT':
            place=precision['place'] if isinstance(precision,dict) else -precision
            actual=actual.quantize(Decimal(1).scaleb(place),rounding=ROUND_HALF_EVEN)
        return {'matches':actual==expected,'precision':precision,'weaker_claim':precision!='EXACT',
                'qualification':None if precision=='EXACT' else 'Compared at the stated digit precision, rounding ties to even; this is weaker than an exact match. No tolerance was inferred.'}


class ReadTools:
    def __init__(self,*,graph,path,queries,intake,job_runs,refresh_history,security_definitions=None,
                 candidates=None,expand=None,definition_reader=None):
        self.graph,self.path,self.queries=graph,deepcopy(path),queries
        self.intake=deepcopy(intake)
        self.nodes={n['id']:n for n in (candidates or {}).get('nodes',[])}
        for node in path['nodes']:
            enriched=self.nodes.get(node['id'],{}).get('enrichment')
            self.nodes[node['id']]=deepcopy(node)
            if enriched:self.nodes[node['id']]['enrichment']=deepcopy(enriched)
        self.visible={n['id'] for n in path['nodes']}
        adjacent={}
        for edge in [*path.get('edges',[]),*(candidates or {}).get('edges',[])]:
            adjacent.setdefault(edge['source'],set()).add(edge['target'])
            adjacent.setdefault(edge['target'],set()).add(edge['source'])
        root=intake.get('visual') or intake.get('page') or intake.get('report')
        self.distance={root:0};queue=deque([root])
        while queue:
            current=queue.popleft()
            for target in adjacent.get(current,[]):
                if target not in self.distance:self.distance[target]=self.distance[current]+1;queue.append(target)
        owners={n.get('owner') for n in path['nodes'] if n.get('owner')}
        self.visible.update(i for i,n in self.nodes.items() if n.get('owner') in owners
                            and n['kind'] in ('MODEL','PIPELINE','COPY_ACTIVITY','NOTEBOOK'))
        self.expand=expand
        self.definition_reader=definition_reader
        self.job_runs,self.refresh_history,self.security=job_runs,refresh_history,security_definitions

    def definitions(self,args):
        retained=self.definition_reader(args['node']) if self.definition_reader else None
        return retained if retained is not None else self.graph.definition_of(args['node'])

    def lineage(self,args):
        # Expansions remain inside GraphAPI's existing admitted estate scope.
        operation=args.get('operation','PATH')
        if operation!='PATH':
            result=self.graph.explore(operation=operation,node=args.get('node'),words=args.get('words',''))
            self.nodes.update({n['id']:n for n in result['nodes']});self.visible.update(n['id']for n in result['nodes'])
            return result
        if not args.get('node'):raise ValueError('LINEAGE_NODE_REQUIRED')
        kind=self.nodes.get(args['node'],{}).get('kind')
        path=(self.graph.calculation_path(args['node']) if kind in ('PIPELINE','COPY_ACTIVITY','NOTEBOOK','QUERY_STEP','PROCEDURE','BOUNDARY','CALCULATED_COLUMN') else self.graph.path_to_source(args['node']))
        activated=self.expand(path) if self.expand else {}
        self.nodes.update({n['id']:n for n in path['nodes']});self.visible.update(n['id'] for n in path['nodes'])
        return {'path':path,'activated_layers':activated}

    def candidates(self,args):
        tokens=lambda text:set(re.findall(r'[^\W_]+',text.casefold()))
        words=tokens(args['words']);rows=[]
        selected=self.intake.get('visual')
        for node in self.nodes.values():
            if node['kind'] not in ('VISUAL','MEASURE','TABLE','VIEW','MODEL','PIPELINE','COPY_ACTIVITY','NOTEBOOK','SOURCE','COLUMN','CALCULATED_COLUMN','PROCEDURE','QUERY_STEP'):continue
            if selected and node['kind']=='VISUAL' and node['id']!=selected:continue
            meta=node.get('properties',{});enrichment=node.get('enrichment',{})
            names=' '.join([node['label'],*enrichment.get('synonyms',[]),enrichment.get('business_meaning',''),
                            (meta.get('native_location') or {}).get('container_name') or ''])
            hits=len(words & tokens(names))
            proximity=meta.get('lineage_distance',self.distance.get(node['id'],len(self.nodes)))
            rows.append({'id':node['id'],'name':node['label'],'kind':node['kind'],
                         'native_location':deepcopy(meta.get('native_location')),
                         'rank':{'word_matches':hits,'lineage_distance':proximity,
                                 'same_workspace':meta.get('workspace')==args.get('workspace') if args.get('workspace') else False,
                                 'same_owner':node.get('owner')==args.get('owner') if args.get('owner') else False,
                                 'last_activity':meta.get('last_activity','')}})
        def activity(value):
            try:
                parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
                return parsed.timestamp() if parsed.tzinfo else 0
            except (ValueError,TypeError,AttributeError):return 0
        rows.sort(key=lambda n:(-n['rank']['word_matches'],n['rank']['lineage_distance'],
                                -n['rank']['same_workspace'],-n['rank']['same_owner'],
                                -activity(n['rank']['last_activity']),n['id']))
        rows=rows[:5]
        self.visible.update(r['id'] for r in rows)
        checks=[]
        for check in args.get('checks',[]):
            if check['candidate'] not in {n['id'] for n in rows}:raise ValueError('CHECK_OUTSIDE_TOP_CANDIDATES')
            record=self.queries.run(check['layer'],check['query'],kind=check['kind'],purpose='recreate')
            if 'record' in record:record=record['record']
            value={'candidate':check['candidate'],'query_id':record.get('id'),'status':record.get('status')}
            if record.get('status')=='SUCCEEDED':
                native=record['result']['rows']
                if len(native)==1 and isinstance(native[0],dict) and len(native[0])==1:
                    scalar=next(iter(native[0].values()))
                    figure=self.intake.get('reported_figure')
                    if figure:value.update(compare_figure(figure,scalar))
            checks.append(value)
        matching=[c['candidate'] for c in checks if c.get('matches')]
        return {'candidates':rows,'checks':checks,'matching':matching,
                'resolution':'ONE_MATCH' if len(matching)==1 else 'TIED_MATCHES' if len(matching)>1 else 'NOT_ESTABLISHED'}

    def record_trace(self,args):
        # Each SQL/DAX statement is supplied by AI. A failed native read can
        # never turn into a claim that the record is absent.
        findings=[]
        for item in args['queries']:
            record=self.queries.run(item['layer'],item['query'],kind=item['kind'],purpose='record')
            if 'record' in record:record=record['record']
            row={'layer':item['layer'],'query_id':record.get('id'),'presence':'UNAVAILABLE'}
            if record.get('status')=='SUCCEEDED':
                values=record['result']['rows']
                if any(not isinstance(v,dict) or item['key_field'] not in v for v in values):
                    row['reason']='RESULT_MISSING_KEY_COLUMN'
                else:
                    hits=[v for v in values if str(v[item['key_field']])==args['key']]
                    row.update(presence='PRESENT' if hits else 'ABSENT',matching_rows=len(hits),
                               duplicate_observed=len(hits)>1,truncated=record.get('truncated',False))
                    if record.get('truncated') and not hits:row['presence']='UNESTABLISHED_IN_TRUNCATED_RESULT'
            findings.append(row)
        return {'key':args['key'],'layers':findings,'cause':'Read the retained transformation or job evidence at the first presence change; presence alone does not prove the cause.'}

    def security_definitions(self,args):
        if self.security is None:
            return {'status':'NOT_INSTALLED','node':args['node'],
                    'operation':'Read-only definitions and memberships; no impersonation, writes or role changes.',
                    'permission_need':'UNESTABLISHED; no access probe has run.',
                    'observed':'No security-definition reader is installed for this path. This is an implementation gap, not an observed permission refusal.'}
        return self.security(args['node'])

    def registry(self):
        ids=sorted(self.visible)
        def entry(description,properties,run,required=None):
            return {'description':description,'schema':schema(properties,required),'run':run}
        node={'enum':ids}
        registry={
            'get_definition':entry('Read the retained DAX, SQL, notebook or view definition for an admitted path object.',{'node':node},self.definitions),
            'get_lineage':entry('Read upstream lineage within the admitted estate and activate its known native query routes. Use a list_candidates result to open an upstream object not active yet; no unrelated catalog dump.',{'node':node,'operation':{'enum':['PATH','SEARCH','NEIGHBOURS','PRODUCERS','CONSUMERS','CANDIDATE_BINDINGS']},'words':{'type':'string','maxLength':256}},self.lineage,[]),
            'get_job_runs':entry('Read native job runs and load accounting. Audit source is preferred when declared.',{'node':{'enum':[i for i,n in self.nodes.items() if i in self.visible and n['kind'] in ('PIPELINE','COPY_ACTIVITY','NOTEBOOK')]}},lambda a:self.job_runs(a['node'])),
            'get_refresh_history':entry('Read the admitted model refresh facts, schedule and automatic-update setting.',{'node':{'enum':[i for i,n in self.nodes.items() if i in self.visible and n['kind']=='MODEL']}},lambda a:self.refresh_history(a['node'])),
            'get_security_definitions':entry('Read RLS/OLS roles, memberships, mapping, SQL policies, user-sensitive views, report access and connection mode where the existing reader can. Never impersonate or grant.',{'node':node},self.security_definitions)}
        check=schema({'candidate':{'type':'string'},'layer':{'enum':list(self.queries.layers)},
                      'kind':{'enum':['sql','dax']},'query':{'type':'string'}})
        registry['list_candidates']=entry('Rank named objects using path proximity, names, synonyms, workspace, ownership and activity. Supply your own cheap queries to check up to five candidates against the stated figure.',
            {'words':{'type':'string'},'workspace':{'type':'string'},'owner':{'type':'string'},
             'checks':{'type':'array','maxItems':5,'items':check}},self.candidates,['words'])
        record_query=schema({'layer':{'enum':list(self.queries.layers)},'kind':{'enum':['sql','dax']},
                             'query':{'type':'string'},'key_field':{'type':'string'}})
        registry['record_trace']=entry('Run your key lookup queries in source-to-model order. Distinguish presence, duplicates, absence, truncation and failed reads. Then inspect definitions/jobs for the cause.',
            {'key':{'type':'string'},'queries':{'type':'array','minItems':1,'maxItems':5,'items':record_query}},self.record_trace)
        # Empty enum tools are unavailable on this path, not invented scopes.
        return {name:value for name,value in registry.items()
                if all(prop.get('enum')!=[] for prop in value['schema']['properties'].values())}
