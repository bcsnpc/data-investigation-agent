"""Validate discovered lineage against independently known POC source dependencies."""
import json
from lineage_graph import load_graph
from metadata_config import ROOT


def validate():
    graph=load_graph(ROOT/'.local/metadata/inventory.sqlite')
    measure=graph.find('Measure','Net Sales')
    upstream=graph.traverse(measure)
    source_names={x['name'] for x in upstream['assets'] if x['kind']=='SqlObject'}
    expected={'app.orders','app.payments','app.refunds','app.order_lines','app.products','app.refund_lines'}
    assert source_names==expected,(source_names,expected)
    reports={a['name'] for a in graph.traverse(measure,'downstream')['assets'] if a['kind']=='Report'}
    assert reports=={'Executive Sales','Product Performance'},reports
    data_visuals={t for s,t,k in graph.edges if k=='binding' and graph.assets[t]['kind']=='ReportVisual'}
    for visual in data_visuals:
        trace=graph.traverse(visual)
        assert any(a['kind']=='SqlObject' for a in trace['assets']),visual
        assert not trace['unresolved'],trace['unresolved']
    # Metadata-scope source isolation and pipeline invocation must also be present.
    copies=[e for e in graph.edges if graph.assets[e[0]]['kind']=='SqlObject' and graph.assets[e[1]]['kind']=='LakehouseTable' and e[2]=='data']
    assert len(copies)==10,len(copies)
    assert any(k=='orchestration' for _,_,k in graph.edges)
    assert all(proof and all(p['hash'] for p in proof) for proof in graph.edges.values())
    assert not graph.gaps,graph.gaps
    result={'status':'PASS','edges':len(graph.edges),'data_bound_visuals':len(data_visuals),
            'net_sales_source_tables':sorted(source_names),'net_sales_reports':sorted(reports),'copy_mappings':len(copies),'unresolved':0}
    (ROOT/'.local/metadata/lineage-validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':validate()
