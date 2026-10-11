"""Versioned token references. Ticket bytes, never copied model prose, own provenance."""
import copy,re
from jsonschema import Draft202012Validator

VERSION='ticket-token-references-v1'
EVIDENCE='_span_reference_evidence'
REFERENCE={'type':'array','items':{'type':'integer','minimum':1},'minItems':2,'maxItems':2}
INSTRUCTIONS="""Return token references, never copied quotes or character offsets. Each reference is [first,last], inclusive one-based token numbers from ticket_tokens. Code extracts the original text between those tokens, including original whitespace. Use enough context to identify the referent. Repeated figures need the reference to the actual occurrence; preserve real competing primary referents. Every relationship's column, value and precision reference must be inside its quote reference. All normal primary/comparison/context, selection-versus-mention and exact precision rules still apply."""

def enabled():
    from .process_tape import ACTIVE
    tape=ACTIVE.get()
    return not (tape is not None and tape.replaying and
        tape.bootstrap.get('state',{}).get('intake_span_protocol')!=VERSION)

def tokens(text):
    return [{'id':i,'text':m.group(),'start':m.start(),'end':m.end()}
            for i,m in enumerate(re.finditer(r"\w+|[^\w\s]",text),1)]

def wire_tokens(text):
    return [[t['id'],t['text']] for t in tokens(text)]

def schema():
    from .intake_extraction import SCHEMA
    value=copy.deepcopy(SCHEMA)
    def convert(node):
        if not isinstance(node,dict):return
        if node.get('type')=='object' and 'properties' in node:
            for key in list(node['properties']):
                if key=='occurrence':
                    del node['properties'][key];node['required'].remove(key)
                elif key in ('quote','column','value','precision_quote','primary'):
                    nullable=key in ('column','precision_quote')
                    node['properties'][key]={'anyOf':[copy.deepcopy(REFERENCE),{'type':'null'}]} if nullable else copy.deepcopy(REFERENCE)
                else:convert(node['properties'][key])
        elif node.get('type')=='array':convert(node['items'])
    convert(value)
    for key in ('comparisons','contexts'):value['properties'][key]['items']=copy.deepcopy(REFERENCE)
    value['properties']['version']={'type':'string','enum':[VERSION]};value['required'].append('version')
    return value

def decode(raw,text):
    Draft202012Validator(schema()).validate(raw)
    from .intake_extraction import SCHEMA
    from .proposal_limits import INTAKE_QUOTE
    ts=tokens(text); sources={};value=copy.deepcopy(raw);value.pop('version')
    def extract(ref,path):
        first,last=ref
        if not 1<=first<=last<=len(ts):raise ValueError('Ticket token reference is out of range or reversed: '+path)
        start,end=ts[first-1]['start'],ts[last-1]['end'];quote=text[start:end]
        if len(quote)>INTAKE_QUOTE:raise ValueError('Referenced quote exceeds consumer bound: '+path)
        sources[path]={'start':start,'end':end,'quote':quote}
        return quote
    value['primary']=extract(raw['primary'],'/primary')
    for key in ('comparisons','contexts'):
        value[key]=[extract(ref,f'/{key}/{i}') for i,ref in enumerate(raw[key])]
    for key in ('measures','figures','selections','visuals','reports','pages','dates','groupings','identifiers'):
        for i,item in enumerate(value[key]):
            for field in ('quote','column','value','precision_quote'):
                if field in item and item[field] is not None:item[field]=extract(raw[key][i][field],f'/{key}/{i}/{field}')
            parent=sources[f'/{key}/{i}/quote']
            for field in ('column','value','precision_quote'):
                source=sources.get(f'/{key}/{i}/{field}')
                if source and not parent['start']<=source['start']<=source['end']<=parent['end']:
                    raise ValueError('Nested token reference lies outside relationship: '+field)
            if key=='figures':
                positions=[m.start() for m in re.finditer('(?='+re.escape(parent['quote'])+')',text)]
                item['occurrence']=positions.index(parent['start'])+1
    Draft202012Validator(SCHEMA).validate(value)
    value[EVIDENCE]={'version':VERSION,'response':copy.deepcopy(raw)}
    return value

def unpack(raw,text):
    if EVIDENCE not in raw:return copy.deepcopy(raw),None
    evidence=raw[EVIDENCE]
    if set(evidence)!={'version','response'} or evidence['version']!=VERSION:raise ValueError('Invalid token provenance evidence')
    decoded=decode(evidence['response'],text)
    if decoded!=raw:raise ValueError('Canonical extraction differs from referenced ticket text')
    # The decoder above validates ranges and containment before this traversal.
    ts=tokens(text);sources={}
    def visit(node,path):
        if isinstance(node,list) and len(node)==2 and all(type(v) is int for v in node):
            start,end=ts[node[0]-1]['start'],ts[node[1]-1]['end']
            sources[path]={'start':start,'end':end,'quote':text[start:end]}
        elif isinstance(node,dict):
            for k,v in node.items():visit(v,path+'/'+k)
        elif isinstance(node,list):
            for i,v in enumerate(node):visit(v,path+'/'+str(i))
    visit(evidence['response'],'')
    decoded.pop(EVIDENCE)
    return decoded,sources


def relocate(value,old_text,new_text,offset):
    """Rebase only through the code-owned form document's exact description part."""
    if EVIDENCE not in value:return value
    if new_text[offset:offset+len(old_text)]!=old_text:raise ValueError('Form description relocation is not byte-identical')
    canonical,sources=unpack(value,old_text);raw=copy.deepcopy(value[EVIDENCE]['response']);ts=tokens(new_text)
    starts={t['start']:t['id'] for t in ts};ends={t['end']:t['id'] for t in ts}
    for path,source in sources.items():
        node=raw;parts=path.strip('/').split('/')
        for part in parts[:-1]:node=node[int(part)] if isinstance(node,list) else node[part]
        key=int(parts[-1]) if isinstance(node,list) else parts[-1]
        node[key]=[starts[source['start']+offset],ends[source['end']+offset]]
    return decode(raw,new_text)
