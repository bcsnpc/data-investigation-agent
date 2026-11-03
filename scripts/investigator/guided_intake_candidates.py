"""Bounded native checks for a named measure before a missing-report question.

No visual is substituted, filters are never dropped, and equal values across
multiple measure identities do not authorize choosing one of them.
"""
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import re


def inventory(text,mapped,catalog):
    proposal=mapped.get('prefilled')or{}
    if mapped.get('status')=='READY' or any(proposal.get(k)for k in ('page','visual')):return {}
    origin=mapped.get('source')or{}
    if origin.get('kind')!='MAPPED_TEXT' or set(origin)!={'kind','text','provenance','figure_mentions'} or origin['text']!=text:return {}
    # Exhaust native named-container candidates before a question. An exact
    # selected visual is never changed by these report/table-level checks.
    named_reports=[r for r in catalog.ranked(text,'REPORT')if r['confidence']=='NAMED']
    reports=catalog.report_matches(text)
    tables=catalog.table_matches(text)
    if not named_reports and len(tables)>1 and not proposal.get('report'):
        return {r['id']:catalog.nodes[r['id']]for r in tables}
    if len(reports)>1 and not proposal.get('table') and not proposal.get('measure'):
        return {r['id']:catalog.nodes[r['id']]for r in reports}
    if any(proposal.get(k)for k in ('report','table','measure')):return {}
    details=proposal.get('details')or{}
    if any(details.get(k)for k in ('filters','date_range','approximate_date','record','users','roles')):return {}
    figure=proposal.get('reported_figure')or{}
    if figure.get('state')!='NUMBER' or figure.get('precision')!='EXACT':return {}
    named=details.get('measure')
    if not isinstance(named,str) or not named.strip():return {}
    nodes=catalog.nodes
    # Exhaust the actual named-measure inventory, not merely reports included
    # in a model's proposed short list. Missing candidates never confer authority.
    candidates={row['id']:nodes[row['id']]for row in catalog.measure_matches(text)
        if nodes.get(row.get('id'),{}).get('kind')=='MEASURE'}
    candidates={key:node for key,node in candidates.items()
        if node.get('label','').casefold()==named.casefold() and re.search(r'(?<!\w)'+re.escape(node['label'])+r'(?!\w)',text,re.I)}
    if not candidates:return {}
    if any(x['confidence']=='NAMED'for x in catalog.ranked(text,'REPORT')):return {}
    if re.search(r'\b(?:card|visual|matrix|chart|selected|filtered|filter|yesterday|last week|last month|this month)\b|20\d\d-\d\d-\d\d',text,re.I):return {}
    return candidates


def resolve(text, mapped, catalog, probe, *, record=lambda _:None, limit=3):
    result=deepcopy(mapped);proposal=deepcopy(mapped.get('prefilled')or{})
    candidates=inventory(text,mapped,catalog)
    if not candidates:return result
    if type(limit)is not int or not 1<=limit<=3:raise ValueError('INTAKE_CANDIDATE_BOUND')
    nodes=catalog.nodes
    figure=proposal.get('reported_figure')or{}
    observations=[]
    for key in sorted(candidates)[:limit]:
        observed=probe(key,deepcopy(proposal));observations.append({'candidate':key,'measure':key,'kind':candidates[key]['kind'],'name':candidates[key]['label'],**deepcopy(observed)})
    record({'event':'INTAKE_NATIVE_CANDIDATE_CHECKS','observations':observations,'total_candidates':len(candidates),'scope':'CANDIDATE_CALCULATIONS_NO_VISUAL_SUBSTITUTION'})
    result['candidate_checks']=observations
    result['candidate_inventory_count']=len(candidates)
    result['candidate_checks_exhaustive']=len(observations)==len(candidates)
    successful=[x for x in observations if x.get('status')=='SUCCEEDED' and x.get('query_id') and 'value'in x]
    def matches(observation):
        try:return figure.get('state')=='NUMBER' and figure.get('precision')=='EXACT' and Decimal(str(observation['value']))==Decimal(figure['value'])
        except (InvalidOperation,ValueError,TypeError):return False
    matching=[x for x in successful if matches(x)]
    exhaustive=len(observations)==len(candidates) and len(successful)==len(candidates)
    if exhaustive and len(matching)==1:
        measure=matching[0]['candidate'];kind=candidates[measure]['kind']
        field='report'if kind=='REPORT'else'table'if kind in ('TABLE','VIEW')else'measure'
        intake={k:v for k,v in proposal.items()if k not in ('report','table','measure')};intake[field]=measure
        from .guided_intake import admit_or_question
        admitted=admit_or_question(intake,catalog)
        if admitted['status']=='READY':
            binding={**admitted,'intake':{k:v for k,v in intake.items()},'candidate_checks':observations,
                    'source':deepcopy(mapped.get('source')),'candidate_field':field,
                    'resolution_assumption':'The '+field+' "'+candidates[measure]['label']+'", whose bounded native calculation matches the exact stated value, is the target. No visual or hidden filter was selected.'}
            try:
                checked=check_origin(binding['source'],binding['intake'],catalog,binding)
                if checked['status']=='READY':return binding
            except (ValueError,KeyError,TypeError):pass
    question=deepcopy(result.get('question')or{})
    question['text']='I attempted value checks for '+str(len(observations))+' candidates. '+('More than one still fits, so 'if len(matching)>1 else 'The checks did not uniquely resolve the target, so ')+ 'which report do you mean?'
    kinds={node['kind']for node in candidates.values()}
    if kinds<={'TABLE','VIEW'}or kinds=={'REPORT'}:
        field='report'if kinds=={'REPORT'}else'table'
        question['fields']=[{'field':field,'choices':[{'id':key,'name':node['label']}for key,node in candidates.items()]}]
        question['text']=question['text'].replace('which report do you mean?','which '+field+' do you mean?')
        result['question']=question
        return result
    if not any(field.get('field')=='report'for field in question.get('fields',[])):
        reports={row['id']:row for key in candidates for row in catalog.reports_for(key)}
        if reports:question['fields']=[{'field':'report','choices':[{'id':key,'name':reports[key]['name']}for key in sorted(reports)]}]
        else:
            choices=[]
            for key,node in candidates.items():
                models=[n for n in nodes.values()if n.get('kind')=='MODEL'and n.get('owner')and n['owner']==node.get('owner')]
                label=node['label']+(' in '+models[0]['label']if len(models)==1 else '')
                choices.append({'id':key,'name':label})
            question['fields']=[{'field':'measure','choices':choices}]
            question['text']=question['text'].replace('which report do you mean?','which named measure do you mean?')
    result['question']=question
    return result


def check_origin(origin,intake,catalog,binding=None):
    """A private installation binding narrows only name ties, never span checks."""
    from .guided_intake import Catalog
    from .guided_text_resolver import Resolver
    selected=catalog
    if binding and intake==binding['intake'] and origin==binding['source']:
        class NativeResolvedCatalog(Catalog):
            def measure_matches(self,text):
                rows=super().measure_matches(text)
                return [x for x in rows if x['id']==intake['measure']]if binding.get('candidate_field','measure')=='measure'else rows
            def table_matches(self,text):
                rows=super().table_matches(text)
                return [x for x in rows if x['id']==intake['table']]if binding.get('candidate_field')=='table'else rows
            def report_matches(self,text):
                rows=super().report_matches(text)
                return [x for x in rows if x['id']==intake['report']]if binding.get('candidate_field')=='report'else rows
        selected=NativeResolvedCatalog({'nodes':list(catalog.nodes.values()),'edges':catalog.edges})
    return Resolver(catalog=selected,model=None,record=lambda _:None).check(origin['text'],
        {'proposal':intake,'provenance':origin['provenance'],'figure_mentions':origin['figure_mentions']})


def probe_measure(factory,catalog,measure,proposal,execute_native,record,initial_intake_queries):
    from .investigative_queries import Queries
    from .model_spend import SpendHold
    from .usage_governance import UsageHold
    from .live_gateway import GatewayDenied
    from .planner_recording import _safe
    try:
        intake={**proposal,'measure':measure}
        path=factory.resolve_path(factory.target_path(intake));nodes={n['id']for n in path['nodes']}
        routes=[key for key,route in factory.routes.items()if route['dialect']=='DAX' and nodes.intersection(route['path_nodes'])]
        if len(routes)!=1:raise ValueError('CANDIDATE_MODEL_ROUTE_NOT_UNIQUE')
        key=routes[0];route=factory.prepare(key,nodes)
        layer={'dialect':route['dialect'],'objects':route['objects'],'label':route['label']}
        queries=Queries({key:layer},execute=execute_native,reserve=lambda *_:None,save=record,restored=initial_intake_queries)
        prior_queries=len(queries.records)
        name=catalog.nodes[measure]['label'].replace(']',']]')
        observed=queries.run(key,'EVALUATE ROW("value", ['+name+'])',kind='dax',purpose='recreate')
        initial_intake_queries.extend(queries.records[prior_queries:])
        if 'already_have'in observed:
            record({'event':'INTAKE_CANDIDATE_ALREADY_HAVE','query_id':observed['already_have']})
            observed=observed['record']
        if observed['status']!='SUCCEEDED':return {'status':'UNAVAILABLE','query_id':observed['id'],'error':observed.get('error')}
        rows=observed['result']['rows']
        if len(rows)!=1 or not isinstance(rows[0],(dict,list)) or len(rows[0])!=1:raise ValueError('CANDIDATE_SCALAR_REQUIRED')
        value=next(iter(rows[0].values()))if isinstance(rows[0],dict)else rows[0][0]
        return {'status':'SUCCEEDED','query_id':observed['id'],'value':value,'scope':'UNFILTERED_MEASURE_NO_VISUAL'}
    except (SpendHold,UsageHold,GatewayDenied):raise
    except Exception as error:
        message=str(error)
        try:_safe(message.encode())
        except ValueError:message=type(error).__name__
        record({'event':'INTAKE_CANDIDATE_FAILED','measure':measure,'error_type':type(error).__name__,'error':message})
        return {'status':'UNAVAILABLE','error_type':type(error).__name__,'error':message}


def probe_target(factory,catalog,target,proposal,execute_native,record,initial_intake_queries):
    """Use exact native measure definitions or an explicitly named column.

    No calculation is guessed for an unsupported scope. Such a candidate gets
    a retained failed-check reason and cannot confer selection authority.
    """
    from .model_spend import SpendHold
    from .usage_governance import UsageHold
    from .live_gateway import GatewayDenied
    from .investigative_queries import Queries
    node=catalog.nodes[target];kind=node['kind'];details=proposal.get('details')or{}
    if kind=='MEASURE':return probe_measure(factory,catalog,target,proposal,execute_native,record,initial_intake_queries)
    try:
        if any(details.get(k)for k in ('filters','date_range','approximate_date','users','roles')):
            raise ValueError('CANDIDATE_SCOPE_NOT_COMPILED_NO_FILTER_OR_USER_DROPPED')
        text=proposal.get('description','')
        if re.search(r'\b(?:selected|filtered|yesterday|last week|last month|this month)\b|20\d\d-\d\d-\d\d',text,re.I):
            raise ValueError('CANDIDATE_SCOPE_NOT_COMPILED_NO_FILTER_DROPPED')
        if kind=='REPORT':
            if re.search(r'\b(?:card|visual|matrix|chart)\b',text,re.I):
                raise ValueError('CANDIDATE_VISUAL_SCOPE_NOT_COMPILED_NO_UNFILTERED_SUBSTITUTION')
            if details.get('record')or re.search(r'\b\w+_id\b|\brecord\s+[0-9]+',text,re.I):
                raise ValueError('CANDIDATE_RECORD_SCOPE_NOT_COMPILED_NO_AGGREGATE_SUBSTITUTION')
            measures=[r for r in catalog.measure_matches(text)if target in {p['id']for p in catalog.reports_for(r['id'])}and r['score']>=.86]
            if len(measures)!=1:raise ValueError('CANDIDATE_CALCULATION_NOT_UNIQUE')
            return probe_measure(factory,catalog,measures[0]['id'],proposal,execute_native,record,initial_intake_queries)
        asset=node.get('properties',{}).get('asset_id')
        routes=[i for i,r in factory.routes.items()if asset and asset in r['asset_ids']and r['dialect']=='T-SQL']
        if len(routes)!=1:raise ValueError('CANDIDATE_TABLE_ROUTE_NOT_UNIQUE')
        key=routes[0];route=factory.prepare(key,{target})
        objects=[a for a in route['objects']if a['id']==asset]
        if len(objects)!=1:raise ValueError('CANDIDATE_NATIVE_TABLE_NOT_BOUND')
        obj=objects[0];columns=obj['metadata']['columns'];metric=details.get('measure','')
        if metric in catalog.nodes:metric=catalog.nodes[metric]['label']
        numeric=[c for c in columns if re.search(r'int|decimal|numeric|float|real|money|double',c['data_type'],re.I)]
        measures=[c for c in numeric if c['name'].casefold()==str(metric).casefold()]
        if len(measures)!=1:raise ValueError('CANDIDATE_EXACT_NUMERIC_COLUMN_REQUIRED')
        quote=lambda s:'['+s.replace(']',']]')+']'
        table=quote(obj['metadata']['schema_name'])+'.'+quote(obj['metadata']['name'])
        query='SELECT SUM('+quote(measures[0]['name'])+') AS value FROM '+table
        if details.get('record'):
            keys=[]
            for column in numeric:
                found=re.findall(r'(?<!\w)'+re.escape(column['name'])+r'\s*(?:=|:)?\s*([0-9]+)(?!\w)',str(details['record']),re.I)
                if len(found)==1:keys.append((column['name'],found[0]))
            if len(keys)!=1:raise ValueError('CANDIDATE_RECORD_KEY_NOT_BOUND')
            query+=' WHERE '+quote(keys[0][0])+' = '+keys[0][1]
        elif re.search(r'\b(?:record|[A-Za-z][A-Za-z0-9_]*_id)\b',text,re.I):
            raise ValueError('CANDIDATE_RECORD_SCOPE_REQUIRED_NO_AGGREGATE_SUBSTITUTION')
        layer={'dialect':'T-SQL','objects':[obj],'label':route['label']}
        queries=Queries({key:layer},execute=execute_native,reserve=lambda *_:None,save=record,restored=initial_intake_queries)
        prior=len(queries.records);observed=queries.run(key,query,kind='sql',purpose='recreate')
        initial_intake_queries.extend(queries.records[prior:])
        if 'already_have'in observed:observed=observed['record']
        if observed['status']!='SUCCEEDED':return {'status':'UNAVAILABLE','query_id':observed['id'],'error':observed.get('error')}
        rows=observed['result']['rows']
        if len(rows)!=1 or not isinstance(rows[0],dict)or len(rows[0])!=1:raise ValueError('CANDIDATE_SCALAR_REQUIRED')
        return {'status':'SUCCEEDED','query_id':observed['id'],'value':next(iter(rows[0].values())),
                'scope':'SUM_OF_EXACT_NAMED_COLUMN_WITH_DECLARED_RECORD_KEY_IF_ANY','query':query}
    except (SpendHold,UsageHold,GatewayDenied):raise
    except Exception as error:
        from .planner_recording import _safe
        message=str(error)
        try:_safe(message.encode())
        except ValueError:message=type(error).__name__
        record({'event':'INTAKE_CANDIDATE_FAILED','candidate':target,'error_type':type(error).__name__,'error':message})
        return {'status':'UNAVAILABLE','error_type':type(error).__name__,'error':message}
