"""Re-score recorded model decisions offline; no provider or estate requests."""
import argparse
import json
from pathlib import Path
from investigator.model_step_scores import score_intake,score_reader,compare
from investigator.translation_eval import score as score_translation


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-version',required=True)
    parser.add_argument('--golden',type=Path,required=True)
    parser.add_argument('--records',type=Path,required=True)
    parser.add_argument('--thresholds',type=Path,required=True)
    parser.add_argument('--previous',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    golden=json.loads(args.golden.read_text(encoding='utf-8'))
    scorer={'intake':score_intake,'reader':score_reader,'translation':score_translation}[golden['step']]
    score=scorer(golden,
                       json.loads(args.records.read_text(encoding='utf-8')),args.model_version)
    result=compare(score,json.loads(args.previous.read_text(encoding='utf-8')) if args.previous else None,
                   json.loads(args.thresholds.read_text(encoding='utf-8'))[golden['step']])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('step','model_version','evaluated','cases','score','delta','gate')}))
    return 0 if result['gate']=='PASSED' else 1


if __name__=='__main__':raise SystemExit(main())
