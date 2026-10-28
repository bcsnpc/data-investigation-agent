"""Reproduce graph health from an explicitly exported metadata-only snapshot."""
import argparse,json
from pathlib import Path
from investigator.graph_health import analyze,markdown

def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--assets');p.add_argument('--manifest');p.add_argument('--json',required=True);p.add_argument('--markdown',required=True);a=p.parse_args()
 snapshot=json.loads(Path(a.snapshot).read_bytes())
 if bool(a.assets)!=bool(a.manifest):p.error('--assets and --manifest must be supplied together')
 if a.assets:
  from investigator.adapters.graph_health_native import effective
  retained=json.loads(Path(a.assets).read_bytes());assets=retained['assets']+retained.get('native_relation_witnesses',[])
  snapshot=effective(snapshot,assets,json.loads(Path(a.manifest).read_bytes()))
 result=analyze(snapshot)
 Path(a.json).write_text(json.dumps(result,indent=2),encoding='utf8');Path(a.markdown).write_text(markdown(result),encoding='utf8')
 print(json.dumps(result['overall']))
if __name__=='__main__':main()
