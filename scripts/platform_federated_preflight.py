"""Operator authentication-only proof; never queries estate data or calls a model."""
import json
import os
from datetime import datetime, timezone
from investigator.adapters.federated_reader import Tokens, validate, SCOPES, claims, FederationUnavailable
from investigator.live_gateway import configured


def run(config, factory=Tokens):
    if not isinstance(config, list) or not 1 <= len(config) <= 6:
        raise ValueError('BOUNDED_AUTHENTICATION_CHECKS_REQUIRED')
    for row in config:
        if set(row) != {'authentication','scope'} or row['scope'] not in SCOPES:
            raise ValueError('AUTHENTICATION_CHECK_SHAPE')
        validate(row['authentication'])
    checks=[]
    for row in config:
        declaration=row['authentication']
        result={k:declaration[k] for k in ('tenant_id','client_id','principal_id')}
        result.update(scope=row['scope'],status='FAIL')
        try:
            access=factory(declaration).get_token(row['scope'])
            observed=claims(access)
            if (observed.get('tid')!=declaration['tenant_id'] or observed.get('oid')!=declaration['principal_id']
                    or (observed.get('appid') or observed.get('azp'))!=declaration['client_id']
                    or str(observed.get('aud','')).rstrip('/')!=row['scope'].removesuffix('/.default').rstrip('/')):
                raise ValueError('Token binding differs')
            result.update(status='PASS',audience=observed['aud'])
            del access,observed
        except FederationUnavailable as error:
            result.update(reason='FEDERATED_AUTHENTICATION_UNAVAILABLE_OR_BINDING_MISMATCH',
                          stage=error.stage,http_status=error.http_status,provider_code=error.provider_code)
        except Exception:
            result['reason']='FEDERATED_AUTHENTICATION_UNAVAILABLE_OR_BINDING_MISMATCH'
        checks.append(result)
    return {'kind':'FEDERATED_AUTHENTICATION_CONTROL','at':datetime.now(timezone.utc).isoformat(),
            'checks':checks,'status':'PASS' if all(r['status']=='PASS' for r in checks) else 'FAIL',
            'estate_reads':0,'model_calls':0,
            'limitation':'Authentication only; no estate query permission or path readiness established.'}


if __name__=='__main__':
    with configured(json.loads(os.environ['DIA_PLATFORM_GATEWAY_POLICY'])):
        result=run(json.loads(os.environ['DIA_FEDERATED_AUTH_CONFIG']))
    print(json.dumps(result))
    raise SystemExit(0 if result['status']=='PASS' else 1)
