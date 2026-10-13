"""Operator-only existing credential check. No estate query or model request."""
import argparse
import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from investigator.adapters import vault_user_cache as reader_auth
from investigator.adapters.managed_identity import secret, validate_secret_reference, TokenBindingError
from investigator.live_gateway import configured


def validate(config):
    if not isinstance(config, dict) or set(config) != {'version','readers','model_key'} or config['version'] != 1:
        raise ValueError('AUTH_PREFLIGHT_CONFIGURATION_REQUIRED')
    readers=config['readers']
    if not isinstance(readers,list) or len(readers)!=2:
        raise ValueError('AUTH_PREFLIGHT_TWO_READERS_REQUIRED')
    scopes=set();channels=set()
    for row in readers:
        if set(row)!={'channel','authentication'} or not isinstance(row['channel'],str) or not row['channel'] or len(row['channel'])>100:
            raise ValueError('AUTH_PREFLIGHT_CHANNEL_REQUIRED')
        reader_auth.validate(row['authentication'])
        scopes.add(row['authentication']['scope']);channels.add(row['channel'])
    if scopes!={reader_auth.PBI,reader_auth.SQL} or len(channels)!=2:
        raise ValueError('AUTH_PREFLIGHT_DISTINCT_CLIENT_CHANNELS_REQUIRED')
    key=config['model_key']
    if key is not None:
        if set(key)!={'channel','reference'} or not isinstance(key['channel'],str) or not key['channel']:
            raise ValueError('AUTH_PREFLIGHT_MODEL_REFERENCE_REQUIRED')
        validate_secret_reference(key['reference'])
    return config


def run(config, *, tokens_factory=reader_auth.Tokens, secret_reader=secret):
    config=validate(config)
    checks=[]
    for row in config['readers']:
        declaration=row['authentication']
        check={'kind':'EXISTING_READER_AUTHENTICATION','channel':row['channel'],
               'scope':declaration['scope'],'tenant_id':declaration['tenant_id'],
               'principal_id':declaration['principal_id'],'status':'FAIL'}
        try:
            access=tokens_factory(declaration,gateway_identity=row['channel']).get_token(declaration['scope'])
            part=access.split('.')[1]
            claims=json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4)))
            # Never copy arbitrary claims or SDK error text into an output.
            expected=declaration['scope'].removesuffix('/.default').rstrip('/')
            if (claims.get('tid')!=declaration['tenant_id'] or claims.get('oid')!=declaration['principal_id']
                    or str(claims.get('aud','')).rstrip('/')!=expected):
                raise ValueError('binding')
            check.update(status='PASS',audience=expected)
            del access,claims,part
        except Exception:
            check['reason']='READER_CREDENTIAL_UNAVAILABLE_OR_BINDING_MISMATCH'
        checks.append(check)
    key=config['model_key']
    if key is not None:
        check={'kind':'MODEL_KEY_AVAILABILITY','channel':key['channel'],'status':'FAIL','model_call_verified':False}
        try:
            value=secret_reader(key['reference'],gateway_identity=key['channel'])
            if not isinstance(value,str) or not value:raise ValueError('empty')
            del value
            check['status']='PASS'
        except TokenBindingError as error:
            check['reason']=error.reason
        except Exception:
            check['reason']='VERSIONED_MODEL_KEY_UNAVAILABLE'
        checks.append(check)
    return {'version':1,'kind':'PLATFORM_AUTH_PREFLIGHT','recorded_at':datetime.now(timezone.utc).isoformat(),
            'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','checks':checks,
            'estate_reads':0,'model_calls':0,
            'limitation':'Credentials refreshed only; no estate permission or model API capability established.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--environment-config',action='store_true',required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        config=json.loads(os.environ['DIA_PLATFORM_AUTH_CONFIG'])
        policy=json.loads(os.environ['DIA_PLATFORM_GATEWAY_POLICY'])
        with configured(policy):result=run(config)
    except Exception:
        result={'version':1,'kind':'PLATFORM_AUTH_PREFLIGHT','status':'FAIL','reason':'AUTH_PREFLIGHT_CONFIGURATION_OR_POLICY_REFUSED',
                'estate_reads':0,'model_calls':0}
    encoded=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.output:args.output.write_text(encoded,encoding='utf-8')
    print(encoded,end='')
    return 0 if result['status']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
