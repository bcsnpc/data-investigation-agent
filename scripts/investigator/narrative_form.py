"""Narrative presentation only; complete structured evidence remains in the output."""
import re
from urllib.parse import unquote
from . import path_narrative
from .snapshot_attestation import payload_comparisons,VERIFIED


def retained_limit(text,all_snapshots_unverified):
    """Coalesce only an explicit repeated trailing snapshot clause in display.

    The original statement stays in mandatory_limits and its judge receipt.
    Unrecognized wording and other uncertainties are never removed.
    """
    if all_snapshots_unverified and re.search(r'\bdoes not (?:establish|prove|confirm)\b',text,re.I):
        repeated=r',?\s+(?:or whether|nor that|or that|and whether|and that) both (?:sides|reads) (?:use|reflect) the same (?:snapshot|data version)\.$'
        return re.sub(repeated,'.',text,flags=re.I)
    return text


def layers(payload,source):
    result={}
    labels=source.get('technical_output',{}).get('layer_labels',{})
    def add(identity):
        if identity and identity!='unresolved upstream' and identity not in result:
            label=labels.get(identity,{})
            name=label.get('name') or unquote(identity.rstrip('/').rsplit('/',1)[-1])
            name=name.replace('_',' ')
            if label.get('container_name'):
                name+=' in '+label['container_name'].replace('_',' ')
            result[identity]={'term':'L'+str(len(result)),'name':name,'identifier':identity}
    for row in path_narrative.facts(payload):
        add(row['output']['layer']);add(row['input']['layer'])
    for boundary in source.get('technical_output',{}).get('unverified_boundaries',[]):
        add(boundary['upper_layer']);add(boundary['lower_layer'])
    # A missing/nonunique human label never makes distinct objects look identical.
    for item in result.values():
        if sum(other['name']==item['name'] for other in result.values())>1:
            same=[other for other in result.values() if other['name']==item['name']]
            for other in same:other['name']+=' ('+other['term']+'; container name unavailable or nonunique)'
    return result


def validate(text,business=False):
    if re.search(r'[{}]|\[\s*(?:\{|\[|["\']|\d+\s*[,\]]|null|true|false)|["\'][A-Za-z_]+["\']\s*:',text):
        raise ValueError('Narrative contains a serialized structure')
    if business:
        from .business_vocabulary import validate_identifier_form
        validate_identifier_form(text)
    if business and re.search(r'\b(?:SNAPSHOT_UNVERIFIED|SNAPSHOT_VERIFIED|snapshot_attestation|unverified_sides|evidence_ids|quantity_receipt_id|Comparison \d+|verified data version|check nearer the report|check further back)\b',text,re.I):
        raise ValueError('Business narrative contains schema vocabulary')
    lines=[line.strip().casefold().rstrip('.') for line in text.splitlines() if line.strip()]
    if len(lines)!=len(set(lines)):raise ValueError('Narrative repeats a line')
    return text


def business(text,payload):
    from .reproduction_composition import from_payload,body
    reproduction=body(from_payload(payload))
    if reproduction is not None:return validate(reproduction,True)
    from .selection_descriptor import render as render_descriptor
    for entry in payload.get('evidence',[]):
        hint=entry.get('result',{}).get('descriptor_hint')
        if hint:
            wording=render_descriptor(hint,business=True)
            if wording:text=wording+' '+text
    from .declared_reproduction import KIND,render
    reproduction_limits=[]
    for entry in payload.get('evidence',[]):
        finding=entry.get('result',{})
        if finding.get('check_kind')==KIND:
            text=render(finding,business=True,include_limits=False)+' '+text
            from .declaration_inventory import qualifications
            from .reported_figure import qualification
            for limit in qualifications(finding['declarations'],finding['label'])[4:]+qualification(finding['reported_figure']):
                if limit not in reproduction_limits:reproduction_limits.append(limit)
        elif finding.get('check_kind')=='PROBE_NOT_EXECUTED':
            text='The selected calculation was not checked because the diagnostic read cap was reached; it would establish '+finding['would_establish']+'. '+text
        elif finding.get('check_kind')=='DECLARED_CONTEXT_REPRODUCTION_UNAVAILABLE':
            if finding.get('capability_status')=='UNDECLARED' and finding.get('question_kind'):
                continue
            from .declared_reproduction import NO_FIGURE,render_stopped
            if finding.get('unevaluated_probes'):text=render_stopped(finding['unevaluated_probes'],True)+' '+text
            text=('You did not provide the number shown in the report, so its saved selections could not be tested against your figure. '
                  if finding['reason']==NO_FIGURE else
                  'The declared selections could not be tested with the available evidence. ')+text
    if reproduction_limits:text+=' '+' '.join(reproduction_limits)
    from .surface_difference import wording
    statements=[]
    baseline=next((e['id'] for e in payload.get('evidence',[]) if e.get('test_purpose')=='ESTABLISH_BASELINE'),None)
    boundaries={r['comparison_id']:r for r in path_narrative.facts(payload)}
    report_input=next((r['input']['layer'] for r in boundaries.values()
        if any(e['id']==r['comparison_id'] and e.get('result',{}).get('referenced_evidence_ids',[None])[0]==baseline
               for e in payload.get('evidence',[])) and baseline is not None),None)
    for entry in payload.get('evidence',[]):
        c=entry.get('result',{})
        if c.get('comparison_status')=='CROSS_SURFACE_VERIFIED' and c.get('surface_difference'):
            sentence=wording(c['surface_difference'],business=True)
            boundary=boundaries.get(entry['id'])
            if boundary:
                refs=c.get('referenced_evidence_ids',[])
                comparison=('the report and the table used to prepare it' if refs and refs[0]==baseline else
                    'the table used to prepare the report and the table it is built from' if boundary['output']['layer']==report_input else
                    'the compared tables yielding '+str(boundary['output']['quantity'])+' and '+str(boundary['input']['quantity']))
                sentence='For '+comparison+', '+sentence[0].lower()+sentence[1:]
            if sentence not in statements:statements.append(sentence)
    if statements:
        text=text.replace('Recommended action:',' '.join(statements)+' Recommended action:') if 'Recommended action:' in text else text+' '+' '.join(statements)
    rows=[r for r in payload_comparisons(payload) if r.get('snapshot_attestation',{}).get('status')!=VERIFIED]
    # The deterministic body already qualifies timing in its own register.
    covered=any(phrase in text for phrase in ('whether the checks describe the same moment','update timing','which state is newer'))
    if rows and not covered:
        sentence='The checks may reflect different update times, so matching totals do not prove they are current and timing may explain a difference.'
        text=text.replace('Recommended action:',sentence+' Recommended action:') if 'Recommended action:' in text else text+' '+sentence
    return validate(text,True)


def technical(commentary,payload,source,recommended):
    path_narrative.validate_mechanism(commentary,source['limits'])
    registry=layers(payload,source)
    def short(text):
        for identity,item in sorted(registry.items(),key=lambda pair:len(pair[0]),reverse=True):text=text.replace(identity,item['term'])
        return text
    facts=path_narrative.facts(payload)
    measure=payload.get('scope',{}).get('measure_name') or payload.get('scope',{}).get('measure_id') or 'unnamed measure'
    # Put the actual finding first. Identifiers have one dedicated legend below.
    finding=['Measure: '+measure+'.']
    from .selection_descriptor import render as render_descriptor
    for entry in payload.get('evidence',[]):
        hint=entry.get('result',{}).get('descriptor_hint')
        if hint:
            wording=render_descriptor(hint)
            if wording:finding.append(wording)
    for i,row in sorted(enumerate(facts,1),key=lambda pair:pair[1]['values_equal']):
        lower,upper=row['input'],row['output'];a=registry[lower['layer']];b=registry[upper['layer']]
        finding.append(f"B{i} {'agrees' if row['values_equal'] else 'diverges'}: {a['term']} ({a['name']}, upstream input) {lower['quantity'] or 'unestablished'} -> {b['term']} ({b['name']}, downstream output) {upper['quantity'] or 'unestablished'}.")
    from .surface_difference import wording
    for row in payload.get('evidence',[]):
        c=row.get('result',{})
        if c.get('comparison_status')=='CROSS_SURFACE_VERIFIED' and c.get('surface_difference'):
            finding.append(wording(c['surface_difference'])+' (receipt '+row['id']+').')
    if not facts:finding.append('No independently compared boundary was established.')
    from .declared_reproduction import KIND,render
    from .reproduction_composition import from_payload,technical_cells
    cell_lines=technical_cells(from_payload(payload))
    if cell_lines:finding.extend(cell_lines)
    for entry in payload.get('evidence',[]):
        result=entry.get('result',{})
        if result.get('check_kind')==KIND:
            if not cell_lines:finding.append(render(result,include_limits=False))
        elif result.get('check_kind')=='PROBE_NOT_EXECUTED':
            finding.append('Probe not executed for '+result['target_id']+': '+result['reason']+' Would establish '+result['would_establish']+'.')
        elif result.get('check_kind')=='DECLARED_CONTEXT_REPRODUCTION_UNAVAILABLE':
            finding.append('Declared-context reproduction unavailable: '+result['reason'])
            if result.get('unevaluated_probes'):
                from .declared_reproduction import render_stopped
                finding.append(render_stopped(result['unevaluated_probes']))
    paragraphs=['\n'.join(finding),commentary]
    if registry:paragraphs.append('Layers:\n'+'\n'.join(f"{v['term']} - {v['name']}: {v['identifier']}" for v in registry.values()))
    limits=[];seen=set()
    def add(key,text):
        text=short(text)
        if key not in seen and text not in limits:limits.append(text);seen.add(key)
    detail=source.get('technical_output',{})
    by_field={}
    for item in detail.get('unattested_surface_fields',[]):
        key=(item['layer'],item['field']);by_field.setdefault(key,[])
        if item['evidence_id'] not in by_field[key]:by_field[key].append(item['evidence_id'])
    grouped={}
    for (layer,field),receipts in by_field.items():
        grouped.setdefault((layer,tuple(receipts)),[]).append(field)
    for (layer,receipts),fields in grouped.items():
        reference=('receipt ' if len(receipts)==1 else 'receipts ')+', '.join(receipts)
        ceiling=payload.get('scope',{}).get('surface_attestation_ceiling',{}).get(layer,{})
        note=('; connection is not self-reportable on this surface for this reader' if 'connection' in fields and ceiling.get('connection')=='NOT_SELF_REPORTABLE_FOR_READER' else '')
        add(('surface',layer,receipts),'Unattested '+', '.join(fields)+' on '+layer+' ('+reference+')'+note+'.')
    rows=payload_comparisons(payload)
    unknown=[str(i) for i,r in enumerate(rows,1) if r.get('snapshot_attestation',{}).get('status')!=VERIFIED]
    if unknown:
        refs=', '.join('B'+i for i in unknown)
        add('snapshot','SNAPSHOT_UNVERIFIED for '+refs+': the reads cannot be tied to matching data versions; agreement does not prove currency, and different update timing was not excluded as a cause of divergence.')
    # The structured fields above replace their duplicated generated prose;
    # every other original qualification is retained once, with short layer refs.
    from .reproduction_composition import from_payload,select,hedges
    candidates=from_payload(payload);lead=select(candidates)
    cell_limits={limit for r in candidates for limit in r['limitations']} if lead else set()
    for text in source['limits']:
        if text in cell_limits:continue
        if text.startswith('Unattested surface field ') and grouped:continue
        if re.match(r'Comparison \d+: SNAPSHOT_UNVERIFIED;',text) and unknown:continue
        add(('other',text),retained_limit(text,bool(rows) and len(unknown)==len(rows)))
    if lead:
        for text in hedges(candidates,lead):add(('cell',text),text)
    if limits:paragraphs.append('Limits:\n'+'\n'.join('- '+line for line in limits))
    for entry in payload.get('evidence',[]):
        timing=entry.get('result',{}).get('refresh_timing')
        if timing and timing.get('status')=='AVAILABLE':
            identity=timing.get('identity_provenance',{}).get('account','separately configured identity')
            paragraphs.append('Optional refresh timing was recorded from '+identity+' (receipt '+entry['id']+'); it is separate from the quantity reader and does not select the outcome.')
    paragraphs.append('Recommended action: '+recommended['text'])
    return validate('\n\n'.join(paragraphs))
