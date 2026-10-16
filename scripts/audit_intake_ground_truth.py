"""Audit pinned visual definitions, without a provider or estate transport."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from investigator.adapters.report_cells import catalog, declared_aliases


def audit(golden):
    rows = []
    for case in golden['cases']:
        if case.get('group') != 'nine':
            continue
        candidates = []
        parts = []
        for model in golden['catalog']:
            context = model.get('evaluation_context', {})
            aliases = declared_aliases({'context': context})
            # Enumerate definitions independently of the expected target IDs.
            # H's first named quantity is the subject; the second is its comparator.
            mentions = [(case['text'].find(name), member['id'])
                        for member in model['measures']
                        for name in [member['name'], *aliases.get(member['id'], [])]
                        if name in case['text']]
            if not mentions:
                continue
            metric = min(mentions)[1]
            reports = {r['report']['id'] for r in context.get('reports', [])
                       if r['report']['name'] in case['text']}
            candidates.extend(v for v in catalog({'context': context})
                              if v['report_id'] in reports and metric in v['measure_ids'])
            identities = {v['target_id'] for v in candidates}
            for report in context.get('reports', []):
                for part in report.get('report_definitions', []):
                    if part['id'] in identities:
                        content = part['metadata']['content']
                        parts.append({'id': part['id'], 'path': part['name'],
                                      'sha256': hashlib.sha256(content.encode()).hexdigest(),
                                      'definition': json.loads(content)})
        # Global is an explicit primary scope in A-C. A selected warehouse
        # does not identify a visual: either card or matrix can display it.
        global_scope = 'current global value' in case['text']
        matching = [v for v in candidates if not global_scope or not v['grouping_columns']]
        titles={p['id']:[t.get('properties',{}).get('text',{}).get('expr',{}).get('Literal',{}).get('Value','')[1:-1]
                         for t in p['definition'].get('visual',{}).get('visualContainerObjects',{}).get('title',[])]
                for p in parts}
        named=[v for v in matching if any(re.search(re.escape(t)+r'\s+(?:card|matrix)\b',case['text'],re.I)
                                          for t in titles.get(v['target_id'],[]) if t)]
        if named:matching=named
        rows.append({'case_id': case['id'], 'ticket': case['text'],
                     'measure_candidates': candidates, 'matching_primary': matching,
                     'count': len(matching), 'definition_parts': parts,
                     'annotation_agrees': {v['target_id'] for v in matching} == set(case['candidate_target_ids']),
                     'basis': 'Explicit primary global scope' if global_scope else
                              'No primary visual or cell-form constraint; selections do not select visuals'})
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('golden', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    value = json.loads(args.golden.read_text(encoding='utf8'))
    result = {'golden_sha256': hashlib.sha256(args.golden.read_bytes()).hexdigest(),
              'model_calls': 0, 'estate_reads': 0, 'cases': audit(value)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding='utf8')
