import copy
from unittest.mock import Mock
from metadata_config import validate_config,worker_configuration
from investigator.adapters.estate_installation import configuration
from investigator.estate_manifest import validate
from test_managed_identity_auth import cloud_manifest
from test_enterprise_discovery import DiscoveryTests

def model_only():
    m=cloud_manifest();m['layers']=[x for x in m['layers'] if x['role']=='SEMANTIC'][:1];m['resources']=[];m['pipelines']=[]
    m['accepted_limits']=[];m['system_of_record']=None;m['lineage']['bindings']=[];m['lineage']['source_delivery']=None
    m['lineage']['inference']={'enabled':False,'code_resources':[]}
    m['adapters'][0]['options'].pop('sql');m['adapters'][0]['options']['fabric'].pop('sql_reader')
    layer=m['layers'][0];layer['asset_id']='/'.join(layer['asset_id'].split('/')[:4]);layer['reach']['address']=layer['asset_id']
    ids={layer['id']};m['identities']=[i for i in m['identities'] if i['id']==layer['reach']['reader']]
    for i in m['identities']:i['scopes']=[{'resource':layer['id'],'rights':['READ','BUILD']}]
    return m

def test_model_only_manifest_worker_and_target_scope():
    m=model_only();validate(m);c=configuration(m)
    ws,model=m['layers'][0]['asset_id'].split('/')[2:4]
    w=worker_configuration(c,{'workspace':ws,'native_model_id':model})
    assert set(w)=={'version','fabric','storage'}
    validate_config(w)
    import pytest
    with pytest.raises(ValueError,match='declared layer'):worker_configuration(c,{'workspace':ws,'native_model_id':'11111111-1111-1111-1111-111111111111'})

def test_no_sql_does_not_relax_identity_or_source_validation():
    import pytest
    m=model_only();m['identities'][0]['credential_reference']='wrong'
    with pytest.raises(ValueError,match='credential reference'):configuration(m)
    m=model_only();m['layers'][0]['role']='APPLICATION'
    with pytest.raises(ValueError,match='required for declared non-semantic'):configuration(m)
    m=model_only();m['adapters'][0]['options']['sql']={'server':'wrong'}
    with pytest.raises(ValueError):configuration(m)

def test_model_only_discovery_repeats_without_sql_or_invented_coverage():
    from investigator.discovery_collect import Collector
    f=DiscoveryTests();f.setUp()
    try:
        f.config.pop('sql')
        from investigator.enterprise_discovery import Discovery
        f.discovery=Discovery(f.store,f.config)
        sql=Mock(side_effect=AssertionError('SQL must not be called'))
        collect=lambda:Collector(f.config,f.transport,sql).run()
        first=f.discovery.run(collect,'one');assert first['status'] in ('COMPLETE','PARTIAL')
        f.items=[]
        second=f.discovery.run(collect,'two');assert second['status'] in ('COMPLETE','PARTIAL')
        sql.assert_not_called()
        assert not any(a['id'].startswith('sql://') for a in second['body']['assets'])
        assert not any(k.startswith('sql://') for k in second['body']['coverage'])
    finally:f.doCleanups()

