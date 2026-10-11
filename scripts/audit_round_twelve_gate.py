"""Diagnose the authorised ten retained mismatches; never call an estate/provider."""
import json
from pathlib import Path
from investigator.conversational_oracle import load
from investigator.intake_extraction import retained_response


def audit(root):
    root=Path(root)
    oracle,seal=load(root/'acceptance/oracle')
    truth={r['id']:r for r in oracle['records']}
    final=json.loads((root/'docs/round-eleven-c-final-results.json').read_text())
    ids={r['id']:r['harmful_admission_fields'] for partition in ('dev','held_out')
         for r in final[partition]['rows'] if r['harmful_admission_fields']}
    paths=['question-gate-held-77482c0','question-gate-dev-77482c0-resume-1']
    rows={r['id']:r for path in paths for r in json.loads(
        (root/'.local/round-eleven'/path/'results.json').read_text())['rows']}
    result=[]
    for identity,fields in sorted(ids.items()):
        case=truth[identity];row=rows[identity]
        raw=retained_response(row['source_intake'])
        figure='reported_figure' in fields
        actual=(row['proposal']['reported_figure'] if figure else
                row['ticket']['settled']['COMPARISON'])
        rule=('VALIDATED_REFERENT_AND_SCOPE accepts the extracted reported figure. '
              'The ticket explicitly states a displayed value; the sealed oracle says NOT_STATED. '
              'No corrective question is established by this evidence.' if figure else
              'from_request(code_gate=True) overrides the nominated kind from current/source keywords; '
              'COMPARISON_ESTABLISHED_FROM_REQUEST suppresses the comparison question.')
        result.append({'id':identity,'partition':case['partition'],'fields':fields,
            'ticket':case['ticket'],'oracle':case['true_reported_figure'] if figure else case['true_comparison_route'],
            'actual':actual,'nominated_kind':raw['kind'],'gate_rule':rule,
            'finding':'SEALED_ORACLE_TEXT_CONFLICT' if figure else 'UNSAFE_COMPARISON_SETTLEMENT'})
    return {'oracle_sha256':seal['sha256'],'method':'Held-out inspected for authorised diagnosis only; no oracle or golden changes.',
            'estate_reads':0,'model_calls':0,'rows':result}


if __name__=='__main__':
    root=Path(__file__).resolve().parent.parent
    result=audit(root)
    (root/'docs/round-twelve-question-gate-diagnosis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'rows':len(result['rows']),'model_calls':0,'estate_reads':0}))
