"""Hosted local/Git code-source comparison; read-only token, no estate credential."""
import argparse,hashlib,json,os
from pathlib import Path
from urllib.request import Request,urlopen
from investigator.code_sources import read,MAX_BYTES
from investigator.adapters.git_code import RepositoryReader
from investigator.estate_manifest import load

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--revision',required=True)
    parser.add_argument('--output',required=True);args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    provenance=json.loads((root/'fixture-code/7ccafe59-0460-4c8a-a691-bfdfa75a2b25/fetch-provenance.json').read_text(encoding='utf8'))
    folder=provenance['source']['item_ids'][0];path=folder+'/notebook-content.py'
    local=load(root/'infra/estates/fixture.json')['lineage']['code_sources'][0]
    git=load(root/'infra/estates/fixture-code-git.json')['lineage']['code_sources'][0]
    if git['repo_url']!='https://github.com/'+os.environ['GITHUB_REPOSITORY']:
        raise ValueError('Declared repository differs from hosted repository')
    git=dict(git,ref=args.revision) # hosted checkout pins declared branch to SHA
    counts={'LOCAL_PATH':0,'GIT_REPOSITORY':0};receipts=[]
    def meter(kind):
        def run(fn):
            counts[kind]+=1
            if sum(counts.values())>4:raise RuntimeError('Hosted code-source cap4 exceeded')
            return fn()
        return run
    def request(method,endpoint):
        if method!='GET' or not endpoint.startswith('repos/'):
            raise ValueError('Read-only repository request required')
        url='https://api.github.com/'+endpoint
        with urlopen(Request(url,headers={'Authorization':'Bearer '+os.environ['CODE_READ_TOKEN'],
                        'Accept':'application/vnd.github+json'}),timeout=30) as response:
            raw=response.read(MAX_BYTES*2+1)
        if len(raw)>MAX_BYTES*2:raise ValueError('Repository response exceeds bound')
        return {'status':200,'body':json.loads(raw)}
    result={'revision':args.revision,'requests':counts,'receipts':receipts,'status':'STARTED'}
    try:
        left,receipt=read(local,path,meter=meter('LOCAL_PATH'),root=root);receipts.append(receipt)
        right,receipt=read(git,path,meter=meter('GIT_REPOSITORY'),git_fetch=RepositoryReader(request));receipts.append(receipt)
        if left!=right:raise ValueError('Repository/local normalized code differs')
        if left['content_hash']!=provenance['parts']['notebook-content.py']['sha256']:
            raise ValueError('Fixture code differs from fetched hash')
        result.update(status='PASSED',content_hash=left['content_hash'],read_only_actions_token=True)
    except Exception as exc:
        result.update(status='FAILED',error_type=type(exc).__name__,error=str(exc));raise
    finally:Path(args.output).write_text(json.dumps(result,indent=2),encoding='utf8')

if __name__=='__main__':main()
