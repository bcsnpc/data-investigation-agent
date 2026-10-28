"""Dialect examples from admitted native schemas, never executed automatically."""
from copy import deepcopy
from .investigative_queries import validate


def sheet(layer):
    examples=[];samples=[]
    if layer['dialect']=='DAX':
        tables={a['id']:a['name']for a in layer['objects']if a.get('kind')=='SemanticTable'}
        for a in layer['objects']:
            table=tables.get(a.get('parent_id'))
            if not table:continue
            t="'"+table.replace("'","''")+"'";member='['+a['name'].replace(']',']]')+']'
            if a.get('kind')=='Measure':examples.append('EVALUATE ROW("value",'+member+')')
            elif a.get('kind')=='SemanticColumn':examples.append('EVALUATE TOPN(5,VALUES('+t+member+'))')
    else:
        for obj in layer['objects'][:1]:
            m=obj['metadata'];quote=lambda s:'['+s.replace(']',']]')+']'
            table=quote(m.get('schema_name','dbo'))+'.'+quote(m['name'])
            examples.append('SELECT COUNT(*) AS rows_observed FROM '+table)
            for c in m.get('columns',[])[:1]:
                column=quote(c['name']);examples.extend(['SELECT TOP 5 '+column+' FROM '+table,'SELECT DISTINCT TOP 5 '+column+' FROM '+table])
                if 'sample_values'in c:samples.append({'object':obj['id'],'column':c['name'],'values':deepcopy(c['sample_values']),'basis':'RETAINED_SCHEMA_SAMPLES_NOT_CURRENT_QUERY'})
    accepted=[]
    for example in examples:
        try:validate(example,layer)
        except (ValueError,TypeError,KeyError):continue
        if example not in accepted:accepted.append(example)
        if len(accepted)==3:break
    return {'dialect':layer['dialect'],'examples':accepted,'sample_values':samples,
       'sample_note':'No invented sample values. Use a bounded DISTINCT lookup on the admitted column when a filter value is unknown.',
       'rules':'Use exact native names and types. CAST/TRY_CAST/CONVERT apply on T-SQL. SQL endpoint routes use T-SQL, even for lakehouse tables. DAX uses EVALUATE and the retained measure definitions. Examples illustrate syntax only and do not recreate the ticket scope.'}
