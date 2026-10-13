"""Trusted scheduled startup: public configuration only; no secret materialisation."""
import json
import os
from pathlib import Path
import tempfile


def main():
    from investigator.planner_recording import _safe
    from investigator.live_gateway import Gateway
    from scan_estate_graph import execute,validate
    config=json.loads(os.environ['DIA_GRAPH_SCAN_CONFIG'])
    gateway=json.loads(os.environ['DIA_GRAPH_SCAN_GATEWAY'])
    validate(config);Gateway(gateway)
    for value in (config,gateway):_safe(json.dumps(value,sort_keys=True).encode())
    with tempfile.TemporaryDirectory(prefix='graph-scan-config-')as folder:
        policy=Path(folder)/'gateway.json';policy.write_text(json.dumps(gateway),encoding='utf8')
        os.environ['DIA_GATEWAY_POLICY']=str(policy)
        try:print(json.dumps(execute(config),sort_keys=True))
        except Exception as error:
            from investigator.adapters.metadata_error import safe_failure
            print(json.dumps({'status':'FAILED','error_type':type(error).__name__,'failure':safe_failure(error)}))
            raise SystemExit(1)from None


if __name__=='__main__':main()
