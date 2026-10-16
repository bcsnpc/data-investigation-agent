"""Apply the dated human oracle decisions; never modify intake or old goldens.

This authoring tool produces a review diff, not an approval or an engine result.
R1 equivalence needs complete adapter evidence; failure stays a named exception.
"""
import argparse
import copy
import hashlib
import json
import re
import sqlite3
from pathlib import Path
from types import SimpleNamespace
from investigator.model_eval_intake import workspace
from investigator.question_intake import snapshot
from investigator.adapters import report_predicates
from investigator.declared_reproduction import compose
from investigator.onboarding import digest


def known(value, rule):
    return {'state':'DETERMINED','value':value,'basis':'Human oracle decision 2026-10-09, '+rule}


def na(reason):return {'state':'NOT_APPLICABLE','reason':reason}


def retained_context(catalog_path, model_id):
    with sqlite3.connect(Path(catalog_path).resolve().as_uri()+'?mode=ro',uri=True) as db:
        row=db.execute('SELECT c.id,c.body,c.hash FROM models m JOIN model_contexts c ON c.id=m.context_id WHERE m.id=?',(model_id,)).fetchone()
    if row is None:return None
    context=json.loads(row[1])
    if digest(context)!=row[2]:raise ValueError('Preserved context hash mismatch: '+row[0])
    return {'id':row[0],'context':context,'hash':row[2]}


def scope_proof(golden, models, long_record, context_catalog):
    """Compile retained declared restrictions, without any quantity/network read."""
    target=long_record['true_target_and_cell']['value']
    visual=next(v for m in models for v in m['visuals'] if v['target_id']==target['target_id'])
    measure=next(c['expected']['measure_id'] for c in golden['cases']
                 if c['expected'].get('target_id')==target['target_id'])
    owner=next(m for m in models if any(v['target_id']==target['target_id'] for v in m['visuals']))
    candidates=[v for v in owner['visuals'] if v['report_id']==visual['report_id'] and measure in v['measure_ids']]
    original=next(m for m in golden['catalog'] if m['id']==owner['id'])
    retained=retained_context(context_catalog,owner['id'])
    native=copy.deepcopy(original)
    native.update(context=copy.deepcopy(retained['context'] if retained else original['evaluation_context']),
                  context_id=retained['id'] if retained else 'sealed-eval',revision=1)
    native['workspace'],native['native_id']=measure.removeprefix('fabric://').split('/')[:2]
    # Explicit authored synthetic catalog membership supplies ownership for this
    # offline parse. It is not a new estate binding, permission or discovery claim.
    if not retained:
        for report in native['context']['reports']:
            report['model_id']='fabric://'+native['workspace']+'/'+native['native_id']
            report['binding_status']='RESOLVED_EXPLICIT_ID';report['gaps']=[]
    result={'candidate_ids':[v['target_id'] for v in candidates],
            'measure_id':measure,'catalog_sha256':hashlib.sha256(json.dumps(original,sort_keys=True).encode()).hexdigest(),
            'method':'Complete preserved local context when available; otherwise authored synthetic catalog, never assumed complete. No values queried.',
            'retained_context_id':retained['id'] if retained else None,'retained_context_hash':retained['hash'] if retained else None,
            'candidate_scopes':[],'status':'NOT_VERIFIED'}
    for candidate in candidates:
        try:
            declaration=report_predicates._extract(native,measure,{'report_binding':{'report_id':visual['report_id']}},candidate['target_id'])
            inventory=declaration['inventory']['entries']
            unsupported=[e.get('form',e.get('native_kind',str(e.get('reason')))) for e in inventory if e['disposition']=='UNSUPPORTED']
            if unsupported:raise ValueError('UNSUPPORTED declarations: '+', '.join(unsupported))
            result['candidate_scopes'].append({'target_id':candidate['target_id'],
                'restrictions':compose(declaration['restrictions']),
                'cell':'TOTAL' if candidate['grouping_columns'] else 'UNGROUPED'})
        except ValueError as exc:
            result['candidate_scopes'].append({'target_id':candidate['target_id'],'unavailable':str(exc)})
    scopes=result['candidate_scopes']
    if scopes and all('restrictions' in s for s in scopes) and all(s['restrictions']==scopes[0]['restrictions'] for s in scopes):
        result['status']='VERIFIED_EQUIVALENT_DECLARED_SCOPE'
    return result


def revise(before, goldens, context_catalog):
    revised=copy.deepcopy(before);records=revised['records'];lookup={r['id']:r for r in records}
    catalogs={estate:snapshot(workspace(SimpleNamespace(store=None,config={}),g['catalog'],None))['models']
              for estate,g in goldens.items()}
    exceptions=[];proofs={}
    def qremove(r,field):
        r['legitimate_questions']=[q for q in r['legitimate_questions'] if q['field']!=field]
        r['illegitimate_questions']=[q for q in r['illegitimate_questions'] if q['field']!=field]
    def forbid(r,field,reason):
        qremove(r,field);r['illegitimate_questions'].append({'field':field,'reason':reason})
    def question(r,field,answer):
        qremove(r,field);r['legitimate_questions'].append({'field':field,'question':field+' clarification','answer':answer})
    for r in records:
        estate,name=r['id'].split(':',1);family=re.fullmatch(r'family-([A-I])(?:-(terse|noisy|typo|mention))?',name)
        if family:
            letter,variant=family.groups();long=lookup[estate+':family-'+letter]
            if letter=='A':
                r['true_comparison_route']=known('APPLICATION','C2')
                forbid(r,'COMPARISON','C2: higher than source movements explicitly chooses APPLICATION.')
            if letter=='I':
                r['true_comparison_route']=known('APPLICATION','C6')
                r['business_disposition']=known('BUSINESS_VALIDATION','C6')
                r['required_disposition']=known('CONTINUE_TECHNICAL_THEN_BUSINESS_VALIDATION','C6')
                forbid(r,'COMPARISON','C6: technical application check and separate business-owner handoff.')
            if variant in ('terse','noisy','typo','mention'):
                # R2 supplies intent; it never supplies a number that was not stated.
                if letter in ('E','G') and variant in ('terse','noisy','typo'):
                    r['true_target_and_cell']=na('C1: model-level named measure; no visual target required.')
                    r['true_reported_figure']=na('C1: no figure reported by this model-level request.')
                    r['true_comparison_route']=known('STALE' if letter=='E' else 'APPLICATION','C1')
                    r['required_disposition']=known('CONTINUE_ONLY_AFTER_CONSEQUENTIAL_FIELDS_RESOLVED','C1')
                    forbid(r,'NUMBER','C1: model-level currency/application request has no visual to choose.')
                    forbid(r,'COMPARISON','C1: comparison route explicit.')
                else:
                    r['true_target_and_cell']=copy.deepcopy(long['true_target_and_cell'])
                    r['true_reported_figure']=copy.deepcopy(long['true_reported_figure'])
                    r['true_report_and_page']=copy.deepcopy(long['true_report_and_page'])
                    if letter!='I':r['required_disposition']=copy.deepcopy(long['required_disposition'])
                    # A keyed row or two different measures cannot collapse.
                    if letter not in ('D','H'):
                        key=estate+':family-'+letter
                        proof=proofs.setdefault(key,scope_proof(goldens[estate],catalogs[estate],long,context_catalog))
                        r['scope_equivalence_review']=copy.deepcopy(proof)
                        if proof['status']=='VERIFIED_EQUIVALENT_DECLARED_SCOPE':
                            r['true_target_and_cell']=known({'model_id':next(m['id'] for m in catalogs[estate] if any(v['target_id']==long['true_target_and_cell']['value']['target_id'] for v in m['visuals'])),
                                'measure_id':proof['measure_id'],'scope':proof['candidate_scopes'][0]['restrictions'],'kind':'MEASURE_AT_SCOPE'},'R1')
                            forbid(r,'NUMBER','R1: retained candidate definitions establish the same measure and declared scope.')
                        else:
                            exceptions.append({'id':r['id'],'rule':'R1','reason':'Same-scope evidence incomplete; do not silently waive NUMBER.', 'evidence':proof})
                    if any(q['field']=='NUMBER' for q in r['legitimate_questions']) or letter in ('D','H') or r.get('scope_equivalence_review',{}).get('status')=='NOT_VERIFIED':
                        question(r,'NUMBER',known({'target':r['true_target_and_cell'],'reported_figure':r['true_reported_figure']},'R2'))
        if name in ('question-change-days','question-change-week'):
            r['true_comparison_route']=known('CHANGE_OVER_TIME','R4: sixth route, not implemented')
            r['required_disposition']=known('UNSUPPORTED_ROUTE','R4: change over time')
            r['legitimate_questions']=[]
            for field in ('NUMBER','REPORT_PAGE','COMPARISON'):forbid(r,field,'R4: unsupported change-over-time request; no clarification converts it to a current-state route.')
            if name=='question-change-week':r['unsolicited_earlier_value_answer']=known("I don't have it",'R4')
        if name in ('question-hiding-rows','refusal-unsupported-filter','refusal-unsupported-relative'):
            r['true_reported_figure']=known({'state':'NUMBER','value':'16','precision':{'state':'EXACT'}},'C3 / R5')
        if name=='question-hiding-rows' or name=='refusal-unsupported-relative':
            report_name=('Declared predicate fixture 20261001' if name=='question-hiding-rows' else 'Round Nine translation filters 20261007')
            models=catalogs[estate]
            choices=[(m,v) for m in models for v in m['visuals'] if any(report['id']==v['report_id'] and report['name']==report_name for report in m['reports']) and
                     (name!='question-hiding-rows' or 'Saved predicate selections' in v['page_names']) and
                     'CARD'==v['form'] and any(measure['id'] in v['measure_ids'] and measure['name']=='Handled Quantity' for measure in m['measures'])]
            if name=='question-hiding-rows':
                dated=[]
                for m,v in choices:
                    retained=retained_context(context_catalog,m['id'])
                    if not retained:continue
                    measure=next(x['id'] for x in m['measures'] if x['id'] in v['measure_ids'] and x['name']=='Handled Quantity')
                    workspace_id,native_id=measure.removeprefix('fabric://').split('/')[:2]
                    native={'id':m['id'],'workspace':workspace_id,'native_id':native_id,'context':retained['context'],'context_id':retained['id'],'revision':1}
                    declaration=report_predicates._extract(native,measure,{'report_binding':{'report_id':v['report_id']}},v['target_id'])
                    dates=[restriction for restriction in declaration['restrictions'] if restriction['field_id'].endswith('/columns/event_day')]
                    if dates:
                        dated.append((m,v));r['target_predicate_evidence']={'context_id':retained['id'],'context_hash':retained['hash'],
                            'target_id':v['target_id'],'date_restrictions':dates,'source':'Preserved local definition; no value query.'}
                choices=dated
            if len(choices)!=1:
                r['true_target_and_cell']={'state':'UNDETERMINED',
                    'reason':'The human description matches '+str(len(choices))+' cards with different declared contexts. No page/card choice is supplied; never choose using the reported value.',
                    'candidate_ids':[v['target_id'] for m,v in choices]}
                exceptions.append({'id':r['id'],'rule':'C4' if name=='question-hiding-rows' else 'R5',
                    'reason':'Retained evaluation definitions do not uniquely bind the human-described card; no predicate evidence may be invented.',
                    'evidence':{'candidate_scopes':[{'target_id':v['target_id'],'names':v['names'],'page':v['page_names']} for m,v in choices]}})
            else:
                m,v=choices[0]
                r['true_target_and_cell']=known({'target_id':v['target_id'],'display_names':v['names'],'mode':'UNGROUPED','selected_filters':[],'dimension_ids':[],'cell_keys':[]},'C4 / R5')
                r['true_report_and_page']=known({'report_id':v['report_id'],'report_name':report_name,'page_id':v['page_id'],'page_names':v['page_names']},'C4 / R5')
                forbid(r,'NUMBER','C4 / R5: owner names the card and exact reported figure.')
            if name=='question-hiding-rows':
                r['true_comparison_route']=na('C4: declared-subject FILTER_EFFECT, not a pipeline question.')
                r['required_disposition']=known('REPRODUCE_THEN_FILTER_EFFECT_OR_UNIMPLEMENTED_ROUTE','C4')
            else:r['required_disposition']=known('HOLD_UNLESS_RELATIVE_DATE_TRANSLATION_VERIFIED','R5')
        if name=='refusal-unsupported-filter':
            r['required_disposition']=known('HOLD_UNSUPPORTED_FILTER','R5')
            r['legitimate_questions']=[];r['filter_details_answer']=known('no details','R5')
        if name=='refusal-nonexistent-column':
            r['required_disposition']=known('HOLD_NONEXISTENT_COLUMN','R5')
            r['legitimate_questions']=[]
            forbid(r,'NUMBER','R5: user rejected warehouse_name; re-asking cannot substitute an existing column.')
        if name in ('refusal-two-figures','refusal-two-figures-total'):
            r['true_reported_figure']=known({'state':'AMBIGUOUS','values':['16','17'] if name=='refusal-two-figures' else ['8765','8766'],
                                           'precision':{'state':'EXACT'},'selected_value':None},'R3: both reported values, no primary choice')
            r['legitimate_questions']=[]
            question(r,'FIGURE',known({'answer':"Both values are showing, I can't say which",'disposition':'HOLD_TWO_REPORTED_FIGURES'},'R3'))
            r['required_disposition']=known('HOLD_TWO_REPORTED_FIGURES','R3')
        if name in ('refusal-unidentified-visual','refusal-unidentified-measure'):
            r['legitimate_questions']=[]
            question(r,'REPORT_OR_SCREENSHOT',known({'answer':"I don't know / I don't have one",'disposition':'HOLD_UNIDENTIFIED_REFERENT'},'R3'))
            r['required_disposition']=known('HOLD_UNIDENTIFIED_REFERENT','R3')
        if name.startswith('refusal-business-'):r['true_reported_figure']=na('C5: business-owner judgment, not a reported quantity.')
        if (not family or not family.group(2)) and any(q['field']=='NUMBER' for q in r['legitimate_questions']) and r['true_target_and_cell']['state']=='DETERMINED' and 'target_id' in r['true_target_and_cell']['value'] and r['true_target_and_cell']['value']['mode']!='KEYED':
            proof=scope_proof(goldens[estate],catalogs[estate],r,context_catalog)
            r['scope_equivalence_review']=proof
            if proof['status']=='VERIFIED_EQUIVALENT_DECLARED_SCOPE':
                r['true_target_and_cell']=known({'measure_id':proof['measure_id'],'scope':proof['candidate_scopes'][0]['restrictions'],'kind':'MEASURE_AT_SCOPE'},'R1')
                forbid(r,'NUMBER','R1: all candidate total/ungrouped definitions have the same measure and declared restrictions.')
            else:exceptions.append({'id':r['id'],'rule':'R1','reason':'Complete retained definitions do not establish equivalent scope.','evidence':proof})
        if r['true_comparison_route']['state']!='UNDETERMINED' and name not in ('refusal-two-figures','refusal-two-figures-total','refusal-unidentified-visual','refusal-unidentified-measure'):
            forbid(r,'COMPARISON','Human-reviewed comparison/declared subject is established; no route question needed.')
        # Remove contradictory question dispositions and refresh answers after corrections.
        legal={q['field'] for q in r['legitimate_questions']}
        r['illegitimate_questions']=[q for q in r['illegitimate_questions'] if q['field'] not in legal]
        for q in r['legitimate_questions']:
            if q['field']=='NUMBER':q['answer']=known({'target':r['true_target_and_cell'],'reported_figure':r['true_reported_figure']},'R2 / corrected truth')
    return revised,exceptions


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--original',required=True);parser.add_argument('--rebuilt',required=True)
    parser.add_argument('--root',type=Path,default=Path('.'));parser.add_argument('--context-catalog',required=True)
    args=parser.parse_args();root=args.root/'acceptance/oracle'
    baseline=root/'oracle-draft-before-owner-review.json'
    if not baseline.exists():baseline.write_bytes((root/'oracle-draft.json').read_bytes())
    old_review=root/'oracle-review-before-owner-review.md'
    if not old_review.exists():old_review.write_bytes((root/'oracle-review.md').read_bytes())
    before=json.loads(baseline.read_text())
    goldens={'original':json.loads(Path(args.original).read_text()),'rebuilt':json.loads(Path(args.rebuilt).read_text())}
    revised,exceptions=revise(before,goldens,args.context_catalog)
    diff=[]
    for old,new in zip(before['records'],revised['records']):
        assert old['id']==new['id'] and old['golden_record_hash']==new['golden_record_hash']
        changes={k:{'before':old.get(k),'after':new.get(k)} for k in sorted(old.keys()|new.keys()) if old.get(k)!=new.get(k)}
        if changes:diff.append({'id':old['id'],'fields':changes})
    result={'status':'REVIEW_DIFF_BEFORE_SEALING','owner':'Chiranjeevi Bhogireddy','reviewer':'Claude','date':'2026-10-09',
            'records_changed':len(diff),'changes':diff,'exceptions':exceptions,'estate_reads':0,'model_calls':0}
    revised['owner_review_decision']={'owner':'Chiranjeevi Bhogireddy','reviewer':'Claude','date':'2026-10-09',
        'status':'AMENDMENTS_APPLIED_DIFF_NOT_YET_SEALED','exceptions':exceptions,
        'source':'oracle-approval.md; conditional approval after amendments and diff'}
    (root/'oracle-draft.json').write_text(json.dumps(revised,indent=2)+'\n',encoding='utf-8')
    (root/'oracle-approval-diff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    lines=['# Oracle approval amendments — diff before sealing','',f"Changed records: {len(diff)} / 68. No original golden or split changed. No seal or scoring.",'']
    for change in diff:
        lines+=['## '+change['id'],'']
        for field,values in change['fields'].items():
            lines += ['### '+field,'','Before: `'+json.dumps(values['before'],ensure_ascii=False)+'`','',
                      'After: `'+json.dumps(values['after'],ensure_ascii=False)+'`','']
    lines+=['# R1 evidence exceptions','']
    for exception in exceptions:
        lines += ['- '+exception['id']+': '+exception['reason']+' '+json.dumps(exception['evidence']['candidate_scopes'])]
    unknown=[{'id':r['id'],'fields':{k:v.get('reason') for k,v in r.items() if isinstance(v,dict) and v.get('state')=='UNDETERMINED'}} for r in revised['records']]
    unknown=[r for r in unknown if r['fields']]
    lines+=['','# Remaining undetermined records','',*[json.dumps(r) for r in unknown]]
    (root/'oracle-approval-diff.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    review=['# Conversational oracle — owner/reviewer amendments','',
            'Revised draft; not sealed or scored. Field-by-field changes: [oracle-approval-diff.md](oracle-approval-diff.md).',
            'Original reviewed draft and paragraphs are preserved in the before-owner-review files.','']
    for r in revised['records']:
        review+=['## '+r['id']+' ('+r['partition']+')','',r['ticket'],'']
        for k in ('true_target_and_cell','true_reported_figure','true_comparison_route','true_report_and_page','required_disposition'):
            review+=['- '+k+': '+json.dumps(r[k],ensure_ascii=False)]
        review+=['- Legitimate '+q['field']+': '+json.dumps(q['answer'],ensure_ascii=False) for q in r['legitimate_questions']]
        review+=['- Illegitimate '+q['field']+': '+q['reason'] for q in r['illegitimate_questions']]
        if r.get('scope_equivalence_review'):review+=['- R1 basis: '+r['scope_equivalence_review']['status']+'; context '+str(r['scope_equivalence_review']['retained_context_id'])+' / '+str(r['scope_equivalence_review']['retained_context_hash'])]
        if r.get('business_disposition'):review+=['- Separate business handoff: '+json.dumps(r['business_disposition'])]
        review+=['']
    (root/'oracle-review.md').write_text('\n'.join(review),encoding='utf-8')
    print(json.dumps({'changed':len(diff),'evidence_exceptions':len(exceptions),'remaining_undetermined_records':len(unknown)}))


if __name__=='__main__':main()
