"""Declared source semantics and deterministic delivery evidence, never a recount."""
import re
from datetime import datetime,timezone
from decimal import Decimal


def declaration(value):
    keys={'source_asset_id','key_column_id','version_column_id','modified_column_id','time_semantics'}
    if (not isinstance(value,dict) or set(value)!=keys or value['time_semantics']!='UTC_LAST_MODIFIED'
            or any(not isinstance(value[k],str) or not 1<=len(value[k])<=300 or value[k]!=value[k].strip() for k in keys)):
        raise ValueError('Source delivery requires explicit asset/column identities and UTC last-modified semantics')
    return dict(value)


def instant(value):
    """Keep all seven timestamp digits; never choose a freshness tolerance."""
    if not isinstance(value,str):raise ValueError('Missing UTC timestamp')
    m=re.fullmatch(r'(\d{4}-\d\d-\d\d)[T ](\d\d:\d\d:\d\d)(?:\.(\d{1,7}))?(?:Z|\+00:00)?',value)
    if not m:raise ValueError('Unusable UTC timestamp')
    whole=datetime.fromisoformat(m[1]+'T'+m[2]).replace(tzinfo=timezone.utc)
    return Decimal(int(whole.timestamp()))+Decimal('0.'+(m[3] or '0'))


def classify(audit,source,destination):
    if audit.get('status')!='CURRENT':
        return {'status':'UNAVAILABLE','reason':audit.get('reason') or 'Successful load accounting unavailable.'}
    try:
        def keyed(rows):
            result={}
            for r in rows:
                if set(r)!={'key','version','modified'}:raise ValueError('Delivery projection differs')
                key=int(r['key']);version=int(r['version'])
                if str(key)!=str(r['key']) or str(version)!=str(r['version']) or key in result:
                    raise ValueError('Delivery keys/versions are null, ambiguous or duplicated')
                result[key]={'version':version,'modified':r['modified']}
                instant(r['modified'])
            return result
        s,d=keyed(source),keyed(destination)
        if not s:raise ValueError('No source rows establish a change time')
        newest=max((r['modified'] for r in s.values()),key=instant)
        start,end=instant(audit['started_at']),instant(audit['completed_at'])
        if end<start:raise ValueError('Contradictory audited interval')
        missing=[k for k in s if k not in d]
        changed=[k for k in s if k in d and s[k]['version']!=d[k]['version']]
        extras=[k for k in d if k not in s]
        facts={'newest_source_change':newest,'last_successful_start':audit['started_at'],
               'last_successful_end':audit['completed_at'],'run_id':audit['run_id'],
               'accounting':audit['accounting'],'missing_rows':len(missing),
               'different_version_rows':len(changed),'destination_only_rows':len(extras)}
        if audit.get('excluded_rows'):facts['excluded_rows']=audit['excluded_rows']
        if not missing and not changed:
            return {'status':'UNAVAILABLE','reason':'No missing or different-version source rows establish a delivery gap.',**facts}
        affected=[instant(s[k]['modified']) for k in missing+changed]
        if all(t>end for t in affected):
            return {'status':'LATENT',**facts}
        if all(t<=start for t in affected):
            return {'status':'GAP',**facts}
        return {'status':'UNAVAILABLE','reason':'Affected source rows span different load intervals or changed during the load; a single delivery cause is not established.',**facts}
    except (ValueError,TypeError,KeyError):
        return {'status':'UNAVAILABLE','reason':'Delivery evidence has invalid keys, versions, UTC semantics or audit timestamps.'}


def validate(observation,observations):
    """Recompute the conclusion from the original completed reader observations."""
    audit=observation['audit_result'];groups=observation['row_evidence'];rows={}
    for side in ('source','destination'):
        rows[side]=[]
        if not groups.get(side):raise ValueError('Delivery enumeration has no pages')
        after=None
        for index,identity in enumerate(groups[side]):
            o=observations.get(identity,{})
            a=o.get('surface_attestation',{})
            if (o.get('status')!='COMPLETED' or o.get('completeness')!='COMPLETE_RESPONSE'
                    or a.get('consistency')!='MATCHED' or a.get('missing_required_fields')
                    or o.get('surface_report_binding')!='VALUE_QUERY'):
                raise ValueError('Delivery requires complete attested source and destination pages')
            page=decode(o['values']);keys=[int(r['key']) for r in page]
            final=index==len(groups[side])-1
            if (o.get('delivery_page_after')!=after or keys!=sorted(set(keys))
                    or (after is not None and keys and keys[0]<=after)
                    or (len(page)>=249 if final else len(page)!=249)):
                raise ValueError('Delivery pages do not establish complete ordered enumeration')
            rows[side].extend(page)
            if keys:after=keys[-1]
    original=observations.get(observation['audit_evidence_id'],{})
    from .load_accounting import classify as classify_audit
    metadata=original.get('metadata',{})
    entry=metadata.get('declared_audit',{})
    if original.get('completeness')!='COMPLETE_RESPONSE' or original.get('surface_attestation',{}).get('consistency')!='MATCHED':
        raise ValueError('Delivery requires original complete attested audit rows')
    if (metadata.get('load_accounting')!=audit or classify_audit(decode(original.get('values')),
            entry.get('producer_asset_id','').rsplit('/',1)[-1])!=audit):
        raise ValueError('Delivery audit differs from its original accounting receipt')
    expected=classify(audit,rows['source'],rows['destination'])
    if expected!=observation['delivery_result'] or expected['status'] not in ('LATENT','GAP'):
        raise ValueError('Delivery conclusion differs from original rows and audit')
    return observation


def decode(rows):
    """Typed flexible-query values are a contract, not primitive row dictionaries."""
    if not isinstance(rows,list):raise ValueError('Expected typed query rows')
    result=[]
    for row in rows:
        if not isinstance(row,dict) or any(not isinstance(v,dict) or 'value' not in v or 'type' not in v for v in row.values()):
            raise ValueError('Expected typed query cells')
        result.append({k:v['value'] for k,v in row.items()})
    return result


def render_account(observation,business=False):
    facts=observation.get('delivery_result')
    if not facts:
        audit=observation.get('metadata',{}).get('load_accounting')
        if not audit:return None
        if audit.get('status')!='CURRENT':return 'Load accounting was unavailable: '+audit['reason']
        facts={'run_id':audit['run_id'],'accounting':audit['accounting'],
            'last_successful_end':audit['completed_at'],'excluded_rows':audit.get('excluded_rows',[])}
    if not facts.get('accounting'):return None
    own=facts['accounting'];time=facts['last_successful_end']
    text=f"The recorded successful load finished at {time}; its own activity reported {own['rows_read']} rows read and {own['rows_written']} rows written."
    if not business:text='Run '+facts['run_id']+': '+text
    excluded=facts.get('excluded_rows',[])
    if excluded:
        if business:
            text+=' Damaged load-history entries were excluded; this is the latest usable record, not proof that no later load ran.'
        else:
            text+=' Excluded audit rows: '+ '; '.join('row '+str(e['row_index'])+' (run '+str(e['run_id'])+'): '+e['reason'] for e in excluded)
            text+=' This is the latest valid run, not proof that no later load ran.'
    if 'newest_source_change' in facts:
        text+=f" The newest application change read was {facts['newest_source_change']}; {facts['missing_rows']} source rows were absent and {facts['different_version_rows']} carried different versions in the destination."
        if facts.get('status')=='LATENT':text+=' The source changed after that load finished, so another load is required before checking delivery.'
        elif facts.get('status')=='GAP':text+=' The observed source changes predate that load, so this is a delivery difference requiring operational investigation.'
    return text
