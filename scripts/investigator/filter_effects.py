"""One declared restriction removed per probe; no pipeline or row-loss verdict."""
import copy
from . import declared_reproduction as reproduction
from .onboarding import digest
from .question_kind import UnimplementedRoute
from .usage_governance import UsageHold

KIND='DECLARED_FILTER_EFFECTS'
LIMIT='SNAPSHOT_UNVERIFIED: these within-layer filter reads cannot be tied to matching data versions; timing was not excluded. Current viewer selections, individual missing rows and business correctness remain unestablished.'


def active_restrictions(entries):
    return [(entry,index) for entry in sorted(entries,key=lambda e:e['id'])
            if entry['disposition']=='ACTIVE' for index in range(len(entry['restrictions']))]


def variant(entries, removed, index, keys):
    selected=[entry for entry in entries if entry['id']==removed]
    if len(selected)!=1 or selected[0]['disposition']!='ACTIVE':
        raise ValueError('Filter-effect removal must name one active declaration')
    if type(index) is not int or not 0<=index<len(selected[0]['restrictions']):
        raise ValueError('Filter-effect removal must name one restriction in its declaration')
    return reproduction.compose([restriction for entry,i in active_restrictions(entries)
        if (entry['id'],i)!=(removed,index) for restriction in [entry['restrictions'][i]]]+keys)


def run(adapter,layer,measure_id,scope,checked):
    from .process_debugging import attest,_observation,_surface_key
    marker=checked.get('finding')
    if checked.get('status')!='COMPLETED' or not marker or marker['label']!='REPRODUCED':
        raise UnimplementedRoute('Filter effects require reproduction at the resolved cell before attributing any restriction; no pipeline walk was attempted.')
    originals={o['id']:o for o in checked['observations']}
    reproduction.validate(marker,originals)
    definition=originals[marker['definition_evidence_id']]
    entries=reproduction._entries(definition,definition['declaration_inventory'],definition['declared_restrictions'])
    active=active_restrictions(entries)
    cell=marker.get('cell')
    if cell is None:raise UnimplementedRoute('Filter effects require an explicitly addressed visual; no pipeline walk was attempted.')
    keys=cell['key_restrictions'];rows=[];observed=[]
    full=originals[marker['lower_evidence_id']]
    pending=[{'target':cell['target_id'],'operation':'remove declaration '+e['id']+' restriction '+str(i)} for e,i in active]
    for index,(entry,restriction_index) in enumerate(active):
        from .observation_journal import pending as retain_pending
        retain_pending(pending[index:])
        applied=variant(entries,entry['id'],restriction_index,keys)
        cost=(adapter.declared_probe_cost(measure_id,{'cell':cell,'evidence':definition},
              applied,'WITHOUT_DECLARATION') if hasattr(adapter,'declared_probe_cost') else 1)
        remaining=getattr(adapter,'remaining_diagnostic_reads',None)
        if remaining is not None and remaining()<cost:
            raise UsageHold('Filter-effect diagnostic cap reached before removing declaration '+entry['id'])
        probe=attest(adapter.evaluate_declared_context(layer,measure_id,
            {'restrictions':copy.deepcopy(applied),'dimension_ids':[],
             'cell_id':cell['id'],'probe_purpose':'WITHOUT_DECLARATION','declaration_id':entry['id'],
             'restriction_index':restriction_index}))
        if probe.evidence:
            read=originals.get(probe.evidence['id'])
            if read is None:
                read=_observation(probe.evidence,'declared_filter_effect_read')
                read['execution_surface']=probe.execution_surface
                if probe.query:read['query']=probe.query
                observed.append(read);originals[read['id']]=read
        if probe.status!='OBSERVED' or not probe.evidence:
            raise UnimplementedRoute('Filter-effect quantity unavailable for declaration '+entry['id']+'; no pipeline walk was attempted.')
        quantity=reproduction.number(probe.value,allow_blank=True)
        if 'reproduction_quantity' in read and read['reproduction_quantity']!=quantity:
            raise ValueError('Reused filter-effect receipt changed its quantity')
        read['reproduction_quantity']=quantity
        if (_surface_key(probe.execution_surface)!=_surface_key(full['execution_surface'])
                or probe.execution_surface['identity'].casefold()!=full['execution_surface']['identity'].casefold()):
            raise ValueError('Filter effects require the reproduction surface and identity')
        rows.append({'declaration_id':entry['id'],'restriction_index':restriction_index,'read_evidence_id':read['id'],
                     'removed_restriction':copy.deepcopy(entry['restrictions'][restriction_index]),
                     'applied_restrictions':applied,'quantity':read['reproduction_quantity'],
                     'changed':read['reproduction_quantity']!=marker['reproduced_value']})
    result={'id':'filter-effects-'+digest({'cell':cell['id'],'reads':rows}),
        'tool':'process','check_kind':KIND,'comparison_status':'WITHIN_LAYER_CHECK',
        'reproduction_evidence_id':marker['id'],'variants':rows,'limitation':LIMIT}
    validate(result,{**originals,**{o['id']:o for o in observed}})
    observed.append(_observation(result,'established'))
    return {'finding':result,'observations':observed}


def validate(marker,originals,quantities=None):
    from .process_debugging import _surface_key,attest_surface
    from .read_address import baseline
    if (marker.get('check_kind')!=KIND or marker.get('comparison_status')!='WITHIN_LAYER_CHECK'
            or marker.get('limitation')!=LIMIT):raise ValueError('Filter-effect contract differs')
    base=originals.get(marker.get('reproduction_evidence_id'))
    if not base:raise ValueError('Filter effects require their original reproduction')
    reproduction.validate(base,originals,quantities)
    if base['label']!='REPRODUCED' or base.get('cell') is None:raise ValueError('Filter effects require a reproduced requested cell')
    definition=originals[base['definition_evidence_id']]
    entries=reproduction._entries(definition,definition['declaration_inventory'],definition['declared_restrictions'])
    active=[(e['id'],i) for e,i in active_restrictions(entries)]
    variants=marker.get('variants')
    if not isinstance(variants,list) or [(r.get('declaration_id'),r.get('restriction_index')) for r in variants]!=active:
        raise ValueError('Every active declaration requires exactly one filter-effect probe')
    full=originals[base['lower_evidence_id']]
    for row in variants:
        if set(row)!={'declaration_id','restriction_index','read_evidence_id','removed_restriction','applied_restrictions','quantity','changed'}:
            raise ValueError('Filter-effect variant fields differ')
        read=originals.get(row['read_evidence_id'])
        entry=next(e for e in entries if e['id']==row['declaration_id'])
        if row['removed_restriction']!=entry['restrictions'][row['restriction_index']]:
            raise ValueError('Filter-effect removed restriction differs from its declaration')
        applied=variant(entries,row['declaration_id'],row['restriction_index'],base['cell']['key_restrictions'])
        if (not read or read.get('status')!='COMPLETED' or read.get('completeness')!='COMPLETE_RESPONSE'
                or read.get('measure_id')!=base['measure_id'] or read.get('definition_evidence_id')!=definition['id']
                or read.get('context_id')!=full.get('context_id') or read.get('model_revision')!=full.get('model_revision')
                or read.get('read_address')!=baseline(applied)
                or read.get('applied_restrictions')!=applied or row['applied_restrictions']!=applied):
            raise ValueError('Filter-effect scope differs from the original declaration and read')
        surfaces=[read.get('execution_surface'),full['execution_surface']]
        if (_surface_key(surfaces[0]) is None or _surface_key(surfaces[0])!=_surface_key(surfaces[1])
                or surfaces[0]['identity'].casefold()!=surfaces[1]['identity'].casefold()):
            raise ValueError('Filter-effect surface differs')
        attestation=read.get('surface_attestation') or {}
        if (attest_surface(surfaces[0],read.get('surface_report'),attestation.get('required_fields',()))!=attestation
                or attestation.get('status') not in ('MATCHED','PARTIAL') or attestation.get('missing_required_fields')):
            raise ValueError('Filter-effect probe is not attested')
        quantity=reproduction.number(read['reproduction_quantity'],allow_blank=True)
        if quantities is not None and (read['id'] not in quantities or reproduction.number(quantities[read['id']],allow_blank=True)!=quantity):
            raise ValueError('Filter effect differs from sealed quantity')
        if row['quantity']!=quantity or type(row['changed']) is not bool or row['changed']!=(quantity!=base['reproduced_value']):
            raise ValueError('Filter-effect result differs from original quantities')
    return marker


def render(marker,business=False):
    from .reproduction_composition import restrictions,value
    changed=sum(row['changed'] for row in marker['variants'])
    text=(str(changed)+' of '+str(len(marker['variants']))+' saved filters changed the observed value when each was removed separately. '
          'This identifies value effects under the saved selections, not individual missing movements.')
    for row in marker['variants']:
        label=restrictions({'composed_restrictions':[row['removed_restriction']]}) if business else (
            'declaration '+row['declaration_id']+' restriction '+str(row['restriction_index']))
        text+=' Removing '+label+' produced '+value(row['quantity'])+' ('+('changed' if row['changed'] else 'unchanged')+').'
        if not business:text+=' Receipt '+row['read_evidence_id']+'.'
    return text
