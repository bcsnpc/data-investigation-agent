"""Check one supported native page requirement; not effective filter evaluation."""
import hashlib
import json
import re
from pathlib import Path
from report_definition_evidence import bundle

FIELD={'Column':{'Expression':{'SourceRef':{'Entity':'FactOrder'}},'Property':'order_id'}}


def assess(evidence, page_path, order_id=None):
    unsigned={k:v for k,v in evidence.items() if k!='bundle_hash'}
    if hashlib.sha256(json.dumps(unsigned,sort_keys=True).encode()).hexdigest()!=evidence.get('bundle_hash'):
        raise ValueError('Definition bundle hash differs')
    if order_id is not None and (not isinstance(order_id,str) or not re.fullmatch(r'ORD-\d{6}',order_id)):
        raise ValueError('Expected ORD- followed by six digits')
    result={'status':'UNSUPPORTED','classification':'UNRESOLVED','root_cause_verified':False,
            'automatic_defect_routing':False,'runtime_filter_verified':False,
            'bundle_hash':evidence['bundle_hash'],'scan_id':evidence['scan_id'],
            'report_id':evidence['report']['id'],'page_path':page_path,
            'required_context':[],'provided_context':{'order_id':order_id},
            'limitation':'Checks one native page drillthrough requirement only. Does not verify order existence, runtime filter application, inherited filters, slicers, bookmarks, RLS or DAX results.'}
    matches=[p for p in evidence['report_definitions'] if p['name']==page_path]
    if len(matches)!=1 or not re.fullmatch(r'definition/pages/[^/]+/page.json',page_path):
        result['reason']='Select one retained native page definition';return result
    if evidence['binding_status']!='RESOLVED_EXPLICIT_ID' or evidence['gaps']:
        result['reason']='Report/model definition evidence is incomplete';return result
    page=json.loads(matches[0]['metadata']['content'])
    binding=page.get('pageBinding',{})
    config=page.get('filterConfig',{})
    if not isinstance(binding,dict) or not isinstance(config,dict):
        result['reason']='Unsupported page binding or filter configuration';return result
    filters=config.get('filters',[])
    parameters=binding.get('parameters',[])
    if not isinstance(filters,list) or not isinstance(parameters,list) or any(not isinstance(v,dict) for v in filters+parameters):
        result['reason']='Unsupported filter or parameter list';return result
    supported=(binding.get('type')=='Drillthrough' and len(parameters)==1 and len(filters)==1)
    if supported:
        parameter,filter_=parameters[0],filters[0]
        supported=(parameter.get('fieldExpr')==FIELD and parameter.get('boundFilter')==filter_.get('name')
                   and isinstance(filter_.get('name'),str) and bool(filter_['name'])
                   and filter_.get('field')==FIELD and filter_.get('type')=='Categorical'
                   and filter_.get('howCreated')=='Drillthrough'
                   and set(filter_)=={'name','field','type','howCreated'}
                   and set(parameter)=={'name','boundFilter','fieldExpr'})
    if not supported:
        result['reason']='Page is not the supported single order drillthrough definition';return result
    result.update(status='NEEDS_INPUT' if order_id is None else 'CONTEXT_SUPPLIED',
                  required_context=['order_id'],definition_reference=matches[0]['id'],
                  reason='Provide the order ID used for drillthrough' if order_id is None else 'Order ID supplied; runtime application remains unverified')
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--scan',required=True)
    parser.add_argument('--report',required=True)
    parser.add_argument('--page',required=True)
    parser.add_argument('--order-id')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=assess(bundle(args.database,args.scan,args.report),args.page,args.order_id)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as output:json.dump(result,output,indent=2)
    print(json.dumps(result,indent=2))
