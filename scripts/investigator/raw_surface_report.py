"""Bounded original self-description columns, separate from quantity extraction."""
from .native_identity import canonical

MAX_ROWS = 64
MAX_TEXT = 300


def capture(rows, columns):
    labels = {label for name in columns.values() for label in (name, '['+name+']')}
    captured = []
    for row in rows[:MAX_ROWS]:
        if not isinstance(row, dict): raise ValueError('Raw self-report requires result rows')
        entry = {}
        for label in labels & row.keys():
            value = row[label]
            if isinstance(value, str) and len(value)>MAX_TEXT:
                raise ValueError('Raw self-report text exceeds bound')
            if value is not None and not isinstance(value, (str, int, float)):
                from decimal import Decimal
                if not isinstance(value, Decimal): raise ValueError('Raw self-report requires scalar values')
            entry[label] = canonical(value)
        captured.append(entry)
    return {'version':1, 'encoding':'NATIVE_CANONICAL_SCALARS', 'columns':dict(columns),
            'rows':captured, 'returned_rows':len(rows), 'truncated':len(rows)>MAX_ROWS}


def report(raw):
    """Null/missing/inconsistent fields remain visible, never an invented answer."""
    if raw['truncated'] or not raw['rows']: return None
    result = {}
    for field, label in raw['columns'].items():
        answers = []
        for row in raw['rows']:
            keys = [k for k in (label, '['+label+']') if k in row]
            answers.append(row[keys[0]] if len(keys)==1 else None)
        answer = answers[0] if all(v==answers[0] for v in answers) else None
        result[field] = answer if isinstance(answer,str) and answer else None
    return result if any(v is not None for v in result.values()) else None


def validate(request, result):
    columns = request.get('surface_report_columns')
    if not columns: return
    raw = result.get('raw_surface_report')
    if not isinstance(raw,dict) or set(raw)!={'version','encoding','columns','rows','returned_rows','truncated'}:
        raise ValueError('Receipt requires raw self-report columns before extraction')
    if raw['version']!=1 or raw['encoding']!='NATIVE_CANONICAL_SCALARS' or raw['columns']!=columns:
        raise ValueError('Raw self-report declaration differs')
    rows=raw['rows'];total=raw['returned_rows']
    if (not isinstance(rows,list) or type(total) is not int or total<0 or len(rows)!=min(total,MAX_ROWS)
            or type(raw['truncated']) is not bool or raw['truncated']!=(total>MAX_ROWS)):
        raise ValueError('Raw self-report row bound differs')
    labels={label for name in columns.values() for label in (name,'['+name+']')}
    for row in rows:
        if not isinstance(row,dict) or set(row)-labels:
            raise ValueError('Raw self-report contains undeclared columns')
        for value in row.values():
            if isinstance(value,str) and len(value)>MAX_TEXT: raise ValueError('Raw self-report text exceeds bound')
            if value is not None and not isinstance(value,(str,bool)) and not (
                    isinstance(value,dict) and set(value)=={'number'} and isinstance(value['number'],str)
                    and len(value['number'])<=MAX_TEXT):
                raise ValueError('Raw self-report requires canonical scalar values')
    if result.get('surface_report')!=report(raw): raise ValueError('Extracted report differs from original self-report columns')
