"""Summarize current graph coverage without treating missing paths as success."""
import argparse
from collections import Counter
import json
from pathlib import Path
from lineage_graph import load_graph
from metadata_config import ROOT
from lineage_gap_policy import classify,eligibility


def audit(graph):
    visuals=[a for a in graph.assets.values() if a['kind']=='ReportVisual']
    bound={t for s,t,k in graph.edges if k=='binding' and graph.assets[t]['kind']=='ReportVisual'}
    results=[]
    for visual in sorted(bound):
        trace=graph.traverse(visual)
        sources=sorted(a['id'] for a in trace['assets'] if a['kind']=='SqlObject')
        results.append({'visual':visual,'source_tables':sources,'path_gaps':trace['unresolved'],
                        'investigation_eligibility':eligibility(graph,visual),
                        'status':'SOURCE_PATH_FOUND' if sources and not trace['unresolved'] else 'UNRESOLVED'})
    return {'status':'PARTIAL' if graph.gaps or any(r['status']=='UNRESOLVED' for r in results) or not bound else 'SUPPORTED_PATHS_RESOLVED',
            'assets':dict(sorted(Counter(a['kind'] for a in graph.assets.values()).items())),
            'edges':len(graph.edges),'visuals':len(visuals),'data_bound_visuals':len(bound),
            'visuals_without_discovered_binding':sorted(a['id'] for a in visuals if a['id'] not in bound),
            'source_paths_found':sum(r['status']=='SOURCE_PATH_FOUND' for r in results),
            'gap_reasons':dict(sorted(Counter(g['reason'] for g in graph.gaps).items())),
            'classified_gaps':[classify(graph,g) for g in graph.gaps],
            'investigation_supported_visuals':sum(r['investigation_eligibility']['lineage_conclusions_allowed'] for r in results),
            'gaps':graph.gaps,'visual_paths':results,
            'scope':'Captured static dependencies only; a source path does not prove complete runtime lineage. Unbound visuals may be text or unresolved.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,default=ROOT/'.local/metadata/inventory.sqlite')
    parser.add_argument('--run',required=True)
    args=parser.parse_args()
    result={'lineage_run':args.run,**audit(load_graph(args.database,args.run))}
    output=args.database.parent/('lineage-audit-'+args.run+'.json')
    output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('visual_paths','gaps','classified_gaps','visuals_without_discovered_binding')},indent=2))
