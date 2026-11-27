"""Fetch pinned Microsoft MIT schema sources only; no datasets or model calls."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

COMMIT='26dc1258b431470f515775b8c98ae77e1d66e39a'
PREFIX='samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/'


def fetch(output):
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    with urlopen('https://api.github.com/repos/microsoft/sql-server-samples/git/trees/'+COMMIT+'?recursive=1',timeout=60)as r:tree=json.load(r)
    if tree.get('truncated'):raise ValueError('Truncated upstream tree')
    paths=[x['path']for x in tree['tree']if x['path'].startswith(PREFIX)and '/Tables/'in x['path']and x['path'].endswith('.sql')and '_Archive'not in x['path']]
    if len(paths)!=37:raise ValueError('Pinned table set differs')
    receipts=[]
    for path in paths:
        url='https://raw.githubusercontent.com/microsoft/sql-server-samples/'+COMMIT+'/'+quote(path)
        with urlopen(url,timeout=60)as r:raw=r.read(1024*1024+1)
        if len(raw)>1024*1024:raise ValueError('Schema file size bound')
        name=path[len(PREFIX):].replace('/','__');(root/name).write_bytes(raw)
        receipts.append(dict(path=path,file=name,sha256=hashlib.sha256(raw).hexdigest()))
    pin=dict(commit=COMMIT,license='MIT',copyright='Microsoft Corporation',files=receipts)
    (root/'source-pin.json').write_text(json.dumps(pin,indent=2)+'\n')
    return pin


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);a=p.parse_args()
    print(json.dumps(fetch(a.output),indent=2))
