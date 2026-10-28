"""Reproduce graph health from an explicitly exported metadata-only snapshot."""
import argparse,json
from pathlib import Path
from investigator.graph_health import analyze,markdown

def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--json',required=True);p.add_argument('--markdown',required=True);a=p.parse_args()
 result=analyze(json.loads(Path(a.snapshot).read_bytes()))
 Path(a.json).write_text(json.dumps(result,indent=2),encoding='utf8');Path(a.markdown).write_text(markdown(result),encoding='utf8')
 print(json.dumps(result['overall']))
if __name__=='__main__':main()
