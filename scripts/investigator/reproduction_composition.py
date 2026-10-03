"""One engine-written answer over validated cell findings, separate from the walk."""
from urllib.parse import unquote
from . import reported_figure
import re
import copy


def requested(question):
    return bool(re.search(r'\b(?:reproduc\w*|selections?)\b|\b(?:declared|report) context\b',question,re.I))


def select(findings):
    rows=[r for r in findings if r.get('check_kind')=='DECLARED_CONTEXT_REPRODUCTION']
    if not rows:return None
    # A successful reproduction leads; otherwise the fullest tested scope leads.
    # Stable identity breaks ties, never native kind strings or expected values.
    ordered=sorted(rows,key=lambda r:(r.get('label')!='REPRODUCED',
        -len(r['composed_restrictions']),r.get('cell',{}).get('mode')!='KEYED',r['id']))
    return ordered[0]


def from_payload(payload):
    if payload.get('question') and not requested(payload['question']):return []
    rows=[copy.deepcopy(e['result']) for e in payload.get('evidence',[]) if e.get('result',{}).get('check_kind')=='DECLARED_CONTEXT_REPRODUCTION']
    for row in rows:
        name=payload.get('scope',{}).get('cell_display_names',{}).get(row.get('cell',{}).get('target_id'))
        if name:row['display_name']=name
    return rows


def answer(row):
    if row['label']=='REPRODUCED':return 'Yes — the saved declared context reproduces the reported figure.'
    if row['label']=='NOT_REPRODUCED':return 'No — the saved declared context does not reproduce the reported figure.'
    return 'No verdict: no figure supplied.'


def value(raw):
    if raw is None:return 'nothing'
    from decimal import Decimal
    return format(Decimal(str(raw)),',f')


def restrictions(row):
    from .business_vocabulary import validate_identifier_form
    parts=[]
    for r in row['composed_restrictions']:
        label=unquote(r['field_id'].rstrip('/').rsplit('/',1)[-1]).replace('_',' ')
        values=', '.join(str(v) for v in r['values']) or 'no permitted values'
        # Values are evidence content, not guesses or technical-word suppression.
        validate_identifier_form(label);validate_identifier_form(values)
        parts.append(label+': '+values)
    return '; '.join(parts)


def action(row):
    if row['label']=='REPRODUCED':
        return {'code':'CONFIRM_INTENT_OR_REQUEST_ENHANCEMENT','text':
            'If the saved restrictions ('+(restrictions(row) or 'none')+') are unintended, request an enhancement to the report selections, not a change to the data.'}
    if row['label']=='NOT_REPRODUCED':
        return {'code':'CONFIRM_SCOPE_INTENT','text':
            'Supply the current slicer positions, invoked bookmark, other selections and viewing account to narrow the remaining possibilities.'}
    return {'code':'CONFIRM_SCOPE_INTENT','text':'Supply the figure or empty state that you saw in the report.'}


def hedges(rows,lead):
    declarations=[d for r in rows for d in r['declarations']]
    result=[]
    if lead['label']=='NOT_REPRODUCED':
        result.append('A moved slicer, an invoked bookmark, user selection, row-level security or a genuine difference further back remains possible; none was excluded.')
    else:
        if any(d['disposition']=='ACTIVE' and d['assumption']=='SAVED_DEFAULT' for d in declarations):
            result.append('Assumed: viewer-changeable selections at their saved defaults; their current positions were not established.')
        if any(d['disposition']=='CONDITIONAL' for d in declarations):
            result.append('An invoked bookmark or stored alternative was not established.')
        result.append('Active user selections, row-level security and a difference further back remain unestablished.')
    result.append('The checks are not tied to a shared data version; they do not establish currency or business correctness.')
    result.extend(reported_figure.qualification(lead['reported_figure']))
    return list(dict.fromkeys(result))


def body(rows):
    lead=select(rows)
    if lead is None:return None
    mode=lead.get('cell',{}).get('mode')
    subject='The selected row' if mode=='KEYED' else 'The displayed total row' if mode=='TOTAL' else 'The answering visual'
    if lead.get('display_name'):subject+=' "'+lead['display_name']+'"'
    terms=restrictions(lead)
    lines=[subject+' produced '+value(lead['reproduced_value'])+'.',
        'The applied selections were '+terms+'.' if terms else 'No saved report filter restricts this calculation.']
    if lead['label']=='REPRODUCED':
        lines.append('These saved restrictions reproduce the reported figure of '+reported_figure.display(lead['reported_figure'])+'; this explains its reproduction by declared report design, not whether that design is intended.')
    elif lead['label']=='NOT_REPRODUCED':
        lines.append('This is not the reported figure of '+reported_figure.display(lead['reported_figure'])+'.')
    else:lines.append('No reported figure supplied; the produced value has no reproduction verdict.')
    lines.append('The same calculation without applying report declarations returned '+value(lead['undeclared_context_value'])+'; this is not an unrestricted total.')
    resolution=lead.get('selection_resolution')
    if resolution and resolution.get('resolution_kind')=='OBSERVED':
        lines.append(resolution['source']['quote']+' was observed as a value addressing the displayed row, not declared as a report filter.')
    # Other candidates are one line each, without reprinting their verdict/hedges.
    for i,row in enumerate(sorted((r for r in rows if r['id']!=lead['id']),key=lambda r:r['id']),1):
        role=row.get('cell',{}).get('mode')
        label='displayed total row' if role=='TOTAL' else 'selected row' if role=='KEYED' else 'visual'
        if row.get('display_name'):label+=' "'+row['display_name']+'"'
        lines.append('Other '+label+' '+str(i)+' produced '+value(row['reproduced_value'])+'.')
    lines.extend(hedges(rows,lead))
    lines.append('Recommended action: '+action(lead)['text'])
    return '\n'.join(lines)


def technical_cells(rows):
    from .declared_reproduction import render
    lead=select(rows)
    if not lead:return []
    result=[render(lead,include_limits=False)]
    for row in sorted((r for r in rows if r['id']!=lead['id']),key=lambda r:r['id']):
        cell=row.get('cell',{})
        result.append('Other '+(row.get('display_name') or 'cell '+cell.get('target_id','unestablished'))+
            ' ('+cell.get('mode','unestablished')+', receipt '+row['id']+'): declared-context value '+value(row['reproduced_value'])+
            '; undeclared-context value '+value(row['undeclared_context_value'])+'.')
    return result
