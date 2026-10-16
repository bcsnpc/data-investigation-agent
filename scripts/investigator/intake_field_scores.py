"""Field diagnostics from sealed references; never invent missing annotations."""
from .model_step_scores import score_intake

GROUPS = {
    'kind': ('nominated_question_kind',),
    'figure_precision': ('figure_state','figure_value','figure_precision'),
    'measure': ('model_id','measure_id'),
    'selections': ('filters','selection_value','dimension_ids'),
    'target': ('target_id','cell_mode'),
    'triage': ('ticket_shape','comparison_mode'),
}


def score(golden, records, model_version):
    accepted=score_intake(golden,records,model_version)
    byid={r['case_id']:r for r in records}
    details=[]
    for case in golden['cases']:
        row=byid.get(case['id'])
        checked=next(r for r in accepted['results'] if r['case_id']==case['id'])
        fields={name:all(checked['fields'].get(k,False) for k in members)
                for name,members in GROUPS.items()}
        # Kind nomination is visible even when another field prevents admission.
        expected=case['expected'].get('nominated_question_kind',case['expected'].get('question_kind'))
        fields['kind']=row is not None and row.get('nominated_question_kind')==expected
        proposal=(row or {}).get('intake',{}).get('proposal') or {}
        actual_target=(proposal.get('target_visual') or {}).get('target_id')
        fields['report_page']=fields['target'] and actual_target==case['expected'].get('target_id')
        details.append({'case_id':case['id'],'fields':fields,'full_match':all(checked['fields'].values())})
    total=len(details)
    return {'cases':total,'evaluated':accepted['evaluated'],
        'full_matches':sum(r['full_match'] for r in details),
        'field_accuracy':{name:sum(r['fields'][name] for r in details)/total
                          for name in (*GROUPS,'report_page')},
        'unscored_fields':{
            'primary_span':'No expected primary-span annotation exists in these sealed golden records. Verbatim validity is not semantic accuracy.',
            'comparison_spans':'No expected comparison-span annotation exists in these sealed golden records; no reference was invented.'},
        'basis':{'kind':'Recorded nomination compared to sealed kind, including rejected proposals.',
                 'report_page':'Target-derived report/page binding; not separate page-span interpretation.'},
        'results':details}
