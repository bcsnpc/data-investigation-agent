"""Publish exactly one approved cloud context using configured shared authority."""
import argparse,hashlib,json
from pathlib import Path
from cloud_context_prepare import publish
from investigator.shared_state import configured_state

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--sha256',required=True)
 a=p.parse_args();raw=a.candidate.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=a.sha256:raise ValueError('PUBLICATION_CANDIDATE_CHANGED')
 state=configured_state()
 if state is None or state.backend!='postgresql':raise ValueError('PUBLICATION_POSTGRES_REQUIRED')
 print(json.dumps(publish(state,json.loads(raw))))
if __name__=='__main__':main()
