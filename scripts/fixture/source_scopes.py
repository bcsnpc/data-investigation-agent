"""Read-only controls for same-source, explicitly different export scopes."""
from datetime import date
from .source_history import TABLE,number


def grouped_quantity(column,values):
    if column not in ('warehouse_id','product_id','event_day'):
        raise ValueError('SOURCE_SCOPE_COLUMN_NOT_ALLOWED')
    if not isinstance(values,list)or len(values)!=2:raise ValueError('SOURCE_SCOPE_PAIR_REQUIRED')
    if column=='event_day':
        if any(not isinstance(v,str)or date.fromisoformat(v).isoformat()!=v for v in values):
            raise ValueError('SOURCE_SCOPE_EXACT_DATE_REQUIRED')
    else:values=[number(v,1)for v in values]
    if len(set(values))!=2:raise ValueError('SOURCE_SCOPE_PAIR_NOT_DISTINCT')
    parameters=[{'name':'@context_'+str(i),'value':v}for i,v in enumerate(values)]
    field='['+column+']'
    return {'query':'SELECT TOP (3) CONVERT(nvarchar(100),'+field+') AS scope_key,SUM(CONVERT(bigint,[units])) AS quantity FROM '+TABLE+
            ' WHERE '+field+' IN ('+','.join(p['name']for p in parameters)+') GROUP BY '+field+' ORDER BY '+field,
            'parameters':parameters,'read_only_objects':[TABLE],'max_rows':3,'result_columns':['scope_key','quantity']}
