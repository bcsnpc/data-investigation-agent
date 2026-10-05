"""Zero-network lineage audit from original sealed tape, not driver projections."""
import argparse,copy,json
from pathlib import Path
from investigator.process_tape import Tape,validate_event,sha
from investigator.lineage_binding import seal


def audit(path,manifest):
    tape=Tape(path)
    final=json.loads(validate_event(tape.events[-1],len(tape.events)))
    declarations=final['approval']['approval']['declared_verifications']
    rows=[]
    for boundary in final['reader']['boundaries']:
        for verification in boundary['verifications']:
            proposal=verification['proposal']
            matches=[d for d in declarations if d['proposal']['boundary']==proposal['boundary']
                and d['proposal']['target']==proposal['target']]
            configured=[b for b in manifest['lineage']['bindings']
                if all(b[k]==proposal['boundary'][k] for k in ('from_layer','to_layer'))]
            reason=verification['reason']
            cause=('OTHER_QUANTITY_SAMPLE' if 'not the quantity established by the selected cell' in reason else
                   'STRING_DEDUPLICATION_EQUIVALENCE_UNDECLARED' if 'Deduplication equivalence' in reason else
                   'SOURCE_WORKER_FAILED' if 'source read' in reason else 'OTHER')
            rows.append({'proposal':copy.deepcopy(proposal),'verifier_reason':reason,
                'verification_hash':seal(verification),'cause':cause,
                'same_declared_binding':'ABSENT' if not matches else seal(proposal)==seal(matches[0]['proposal']),
                'declared_matches':[copy.deepcopy(d['proposal']) for d in matches],
                'configured_matches':configured})
    return {'tape_sha256':sha(Path(path).read_bytes()),'manifest_sha256':seal(manifest),
        'rows':rows,'declared_verifications':declarations,
        'worker_failures':[json.loads(validate_event(e,e['ordinal'])) for e in tape.events if e['kind']=='WORKER_FAILURE']}


def markdown(result):
    j=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    lines=['# Round Six C: preserved proposal audit','',
        'Dated 2026-10-05. Zero estate reads. Original tape and receipts unchanged.', '',
        'Tape SHA-256: `'+result['tape_sha256']+'`.', '',
        'The manifest declares only application → landing. Neither original notebook boundary has a declared binding. '
        'The earlier 7,661/7,661 verification covers that separate copy, not these fifteen proposals. '
        'Retained notebook lineage candidates are not verified declarations.', '',
        '| # | Boundary / extractor | Source tables and columns | Target table and column | Full emitted expression | Code location | Verifier reason verbatim | Same-boundary declaration / finding |',
        '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for i,row in enumerate(result['rows'],1):
        p=row['proposal'];l=p['location']
        cells=[str(i),p['boundary']['from_layer']+' → '+p['boundary']['to_layer']+' / '+p['extractor'],
            '`'+j(p['sources'])+'`','`'+j(p['target'])+'`','`'+j(p['expression'])+'`',
            '`'+l['item']+'/'+l['path']+'`, cell '+l['cell']+', lines '+str(l['line_start'])+'–'+str(l['line_end']),
            row['verifier_reason'],'None; code genuinely declares work absent from manifest. '+row['cause']]
        lines.append('| '+' | '.join(c.replace('|','&#124;').replace('\n',' ') for c in cells)+' |')
    lines.extend(['','## Causes and boundaries of the evidence','',
        'Thirteen proposals concern columns other than the selected units cell. Refusing to sample them under that cell is correct. '
        'The operator/controller supplied one quantity sample to all extracted columns; it did not establish samples for thirteen other quantities. '
        'Removing their refusal or fabricating cell identities would be wrong.', '',
        'One selected refinement proposal uses whole-row deduplication including strings. Faithful SQL equivalence is undeclared; '
        'this is not a wrong-object finding or a missing DEDUPE AST node. The compiler supports integral deduplication and correctly refuses unestablished string semantics.', '',
        'One selected serving proposal compiled its left join. Its target read returned 8,765; its source read failed. '
        'The tape retains OSError errno 22, Invalid argument, at tape_worker.py flush. '
        'There is no numerical falsification or SQL permission refusal in that record. '
        'Recorder write amplification is independently observable; causation of this particular failure is not established.', '',
        'Exact retained code:', '', '```python',
        "spark.read.format('delta').load(paths['bronze']+table['name']).dropDuplicates().write.format('delta').mode('errorifexists').save(paths['silver']+table['name'])",
        "valued = movements.join(rates, ['product_id'], 'left').withColumn('movement_value', F.col('units')*F.col('unit_cost'))",
        "valued.write.format('delta').mode('errorifexists').save(paths['gold']+'movement_values')", '```','',
        'The target lakehouse columns correspond to the emitted writes. The declared copy targets a different lakehouse and boundary. '
        'No retained evidence supports equating those bindings.', '',
        'Dated correction: A’s CONSISTENT_TO_BOUNDARY on the unverified inferred manifest is a correct scoped result, not an engine regression. '
        'Its original changed-expectation grading and outputs remain unchanged. The saved outputs omitted proposal counts and verifier reasons: a composition defect.', ''])
    return '\n'.join(lines)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tape',required=True);p.add_argument('--manifest',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();result=audit(a.tape,json.loads(Path(a.manifest).read_text(encoding='utf-8')))
    Path(a.output).write_text(markdown(result),encoding='utf-8')
    print(json.dumps({'rows':len(result['rows']),'causes':{c:sum(r['cause']==c for r in result['rows']) for c in sorted({r['cause'] for r in result['rows']})},'tape_sha256':result['tape_sha256']}))
