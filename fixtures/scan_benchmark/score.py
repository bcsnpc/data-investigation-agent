"""Scoring-only manifest comparison; no discovery, credentials or network.

Uses exact native addresses, not fuzzy names. Unimplemented dimensions are
reported as defects, never credited from the build plan or the expected answer.
"""
import argparse
import json
from pathlib import Path


def ratio(found,total):
    return None if not total else round(100*found/total,4)


def edge_key(edge):
    return edge['source'],edge['target'],edge['relation'],edge['knowledge']


def score(manifest, observation):
    if manifest.get('status')!='DEPLOYED_VERIFIED':
        raise ValueError('Unverified planned manifest cannot yield a live score')
    if observation.get('origin')!='DIA_NATIVE_DISCOVERY':
        raise ValueError('Owner build receipts and synthetic projections are not DIA scans')
    expected={o['address']:o for o in manifest['objects']}
    actual={o['address']:o for o in observation.get('objects',[])}
    if len(actual)!=len(observation.get('objects',[])):raise ValueError('Duplicate discovery addresses')
    gaps=[]
    permissions=observation.get('permission_gaps',[])
    permission_by_object={p['object']:p for p in permissions
        if p.get('status_code')in(401,403) or p.get('native_permission_error')is True}
    def protected(address):
        # Exact or explicitly scoped native schema permission evidence only.
        return next((p for name,p in permission_by_object.items()if address==name or
                     p.get('scope')=='schema'and address.startswith(name+'.')),None)
    for address in sorted(set(expected)-set(actual)):
        p=protected(address)
        if p is None or not p.get('missing_grant'):
            gaps.append(dict(kind='OBJECT_MISSING',object=address))
    ec={(a,c['name'])for a,o in expected.items()for c in o.get('columns',[])}
    ac={(a,c['name'])for a,o in actual.items()for c in o.get('columns',[])}
    for address,column in sorted(ec-ac):
        if not protected(address):gaps.append(dict(kind='COLUMN_MISSING',object=address,column=column))
    lineage={};observed_edges={edge_key(e)for e in observation.get('edges',[])}
    expected_edges={edge_key(e)for e in manifest.get('edges',[])}
    for knowledge in ('declared','parsed','inferable_only'):
        es={e for e in expected_edges if e[3]==knowledge};os={e for e in observed_edges if e[3]==knowledge}
        lineage[knowledge]=dict(expected=len(es),reported=len(os),correct=len(es&os),
            precision=ratio(len(es&os),len(os)),recall=ratio(len(es&os),len(es)))
        # Inferable-only truth is not discoverable fact. Its absence is not a
        # defect if uncertainty is explicitly reported for the affected object.
        for e in sorted(es-os):
            if knowledge=='inferable_only'and e[0]in observation.get('uncertain_objects',[]):continue
            if not protected(e[0])and not protected(e[1]):gaps.append(dict(kind='LINEAGE_MISSING',edge=list(e)))
        for e in sorted(os-es):gaps.append(dict(kind='LINEAGE_FALSE_POSITIVE',edge=list(e)))
    layers=0;authority=0
    for address,o in expected.items():
        found=actual.get(address,{})
        if found.get('layer')==o['layer']:layers+=1
        elif not protected(address):gaps.append(dict(kind='LAYER_WRONG_OR_UNKNOWN',object=address))
        if 'source_of_truth'in o:
            if found.get('source_of_truth')==o['source_of_truth']:authority+=1
            elif not protected(address):gaps.append(dict(kind='AUTHORITY_UNRESOLVED',object=address))
    traps=[]
    for t in manifest.get('traps',[]):
        observed=observation.get('traps',{}).get(t['id'],'MISSING')
        passed=observed in t['expected']
        if not passed:gaps.append(dict(kind='TRAP_UNHANDLED',object=t['id'],observed=observed))
        traps.append(dict(id=t['id'],status='CORRECT'if passed else'WRONG_OR_MISSING',observed=observed))
    permission_results=[]
    for p in manifest.get('expected_permission_gaps',[]):
        actual_gap=permission_by_object.get(p['id'],{})
        passed=bool(actual_gap.get('missing_grant'))and actual_gap.get('missing_grant')==p['missing_grant']
        permission_results.append(dict(object=p['id'],correct=passed))
        if not passed:gaps.append(dict(kind='PERMISSION_GAP_NOT_EXACT',object=p['id']))
    return dict(estate=manifest['estate'],status='PASS'if not gaps else'SCAN_DEFECTS',
        objects=dict(found=len(set(expected)&set(actual)),total=len(expected),percent=ratio(len(set(expected)&set(actual)),len(expected))),
        columns=dict(found=len(ec&ac),total=len(ec),percent=ratio(len(ec&ac),len(ec))),lineage=lineage,
        layers=dict(correct=layers,total=len(expected),percent=ratio(layers,len(expected))),
        source_of_truth=dict(correct=authority,total=sum('source_of_truth'in o for o in expected.values())),
        traps=traps,permission_gaps=permission_results,non_permission_misses=gaps)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True);p.add_argument('--observation',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=score(json.loads(a.manifest.read_text()),json.loads(a.observation.read_text()))
    a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))


if __name__=='__main__':main()
