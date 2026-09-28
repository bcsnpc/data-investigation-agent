"""Narrative presentation only; complete structured evidence remains in the output."""
import re
from urllib.parse import unquote
from . import path_narrative
from .snapshot_attestation import payload_comparisons,VERIFIED


def layers(payload,source):
    result={}
    def add(identity):
        if identity and identity!='unresolved upstream' and identity not in result:
            name=unquote(identity.rstrip('/').rsplit('/',1)[-1]).replace('_',' ')
            result[identity]={'term':'L'+str(len(result)),'name':name,'identifier':identity}
    for row in path_narrative.facts(payload):
        add(row['output']['layer']);add(row['input']['layer'])
    for boundary in source.get('technical_output',{}).get('unverified_boundaries',[]):
        add(boundary['upper_layer']);add(boundary['lower_layer'])
    return result


def validate(text,business=False):
    if re.search(r'[{}]|\[\s*(?:\{|\[|["\']|\d+\s*[,\]]|null|true|false)|["\'][A-Za-z_]+["\']\s*:',text):
        raise ValueError('Narrative contains a serialized structure')
    if business and re.search(r'\b(?:SNAPSHOT_UNVERIFIED|SNAPSHOT_VERIFIED|snapshot_attestation|unverified_sides|evidence_ids|quantity_receipt_id|Comparison \d+|verified data version|check nearer the report|check further back)\b',text,re.I):
        raise ValueError('Business narrative contains schema vocabulary')
    lines=[line.strip().casefold().rstrip('.') for line in text.splitlines() if line.strip()]
    if len(lines)!=len(set(lines)):raise ValueError('Narrative repeats a line')
    return text


def business(text,payload):
    rows=[r for r in payload_comparisons(payload) if r.get('snapshot_attestation',{}).get('status')!=VERIFIED]
    # The deterministic body already qualifies timing in its own register.
    covered=any(phrase in text for phrase in ('whether the checks describe the same moment','update timing','which state is newer'))
    if rows and not covered:
        sentence='The checks may reflect different update times, so matching totals do not prove they are current and timing may explain a difference.'
        text=text.replace('Recommended action:',sentence+' Recommended action:') if 'Recommended action:' in text else text+' '+sentence
    return validate(text,True)


def technical(commentary,payload,source,recommended):
    registry=layers(payload,source)
    def short(text):
        for identity,item in sorted(registry.items(),key=lambda pair:len(pair[0]),reverse=True):text=text.replace(identity,item['term'])
        return text
    facts=path_narrative.facts(payload)
    measure=payload.get('scope',{}).get('measure_name') or payload.get('scope',{}).get('measure_id') or 'unnamed measure'
    # Put the actual finding first. Identifiers have one dedicated legend below.
    finding=['Measure: '+measure+'.']
    for i,row in sorted(enumerate(facts,1),key=lambda pair:pair[1]['values_equal']):
        lower,upper=row['input'],row['output'];a=registry[lower['layer']];b=registry[upper['layer']]
        finding.append(f"B{i} {'agrees' if row['values_equal'] else 'diverges'}: {a['term']} ({a['name']}, upstream input) {lower['quantity'] or 'unestablished'} -> {b['term']} ({b['name']}, downstream output) {upper['quantity'] or 'unestablished'}.")
    if not facts:finding.append('No independently compared boundary was established.')
    paragraphs=['\n'.join(finding),commentary]
    if registry:paragraphs.append('Layers:\n'+'\n'.join(f"{v['term']} - {v['name']}: {v['identifier']}" for v in registry.values()))
    limits=[];seen=set()
    def add(key,text):
        text=short(text)
        if key not in seen and text not in limits:limits.append(text);seen.add(key)
    detail=source.get('technical_output',{})
    grouped={}
    for item in detail.get('unattested_surface_fields',[]):
        key=(item['layer'],item['evidence_id']);grouped.setdefault(key,[])
        if item['field'] not in grouped[key]:grouped[key].append(item['field'])
    for (layer,receipt),fields in grouped.items():
        add(('surface',layer,receipt),'Unattested '+', '.join(fields)+' on '+layer+' (receipt '+receipt+').')
    rows=payload_comparisons(payload)
    unknown=[str(i) for i,r in enumerate(rows,1) if r.get('snapshot_attestation',{}).get('status')!=VERIFIED]
    if unknown:
        refs=', '.join('B'+i for i in unknown)
        add('snapshot','SNAPSHOT_UNVERIFIED for '+refs+': the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.')
    # The structured fields above replace their duplicated generated prose;
    # every other original qualification is retained once, with short layer refs.
    for text in source['limits']:
        if text.startswith('Unattested surface field ') and grouped:continue
        if re.match(r'Comparison \d+: SNAPSHOT_UNVERIFIED;',text) and unknown:continue
        add(('other',text),text)
    if limits:paragraphs.append('Limits:\n'+'\n'.join('- '+line for line in limits))
    for entry in payload.get('evidence',[]):
        timing=entry.get('result',{}).get('refresh_timing')
        if timing and timing.get('status')=='AVAILABLE':
            identity=timing.get('identity_provenance',{}).get('account','separately configured identity')
            paragraphs.append('Optional refresh timing was recorded from '+identity+' (receipt '+entry['id']+'); it is separate from the quantity reader and does not select the outcome.')
    paragraphs.append('Recommended action: '+recommended['text'])
    return validate('\n\n'.join(paragraphs))
