"""Local development auth worker. JSON in/out; credentials remain in memory."""
import json
import sys
from metadata_auth import FabricCliTokens, MetadataHttp
from onelake_metadata import collect


def metered_request(execute):
    print(json.dumps({'physical_read':'REQUEST','kind':'metadata_read'}),flush=True)
    if sys.stdin.readline().strip()!='ALLOW':raise RuntimeError('Metadata read not admitted')
    result=execute()
    print(json.dumps({'physical_read':'DONE','kind':'metadata_read','status':'AVAILABLE'}),flush=True)
    return result

if __name__ == '__main__':
    try:
        metered='--metered' in sys.argv
        request = json.loads(sys.stdin.readline()) if metered else json.load(sys.stdin)
        http = MetadataHttp(FabricCliTokens(request['tenant']),meter=metered_request if metered else None)
        if request['operation'] == 'request':
            result = http(request['endpoint'], request['method'], request['audience'])
        elif request['operation'] == 'tables':
            workspace, item = request['workspace'], request['item']
            base = f"delta/{workspace}/{item['id']}/api/2.1/unity-catalog/"
            result = collect(workspace, item['id'], item['displayName'] + '.Lakehouse',
                             get=lambda path: http(base + path, audience='onelake')['text'])
        else:
            raise ValueError('Unknown worker operation')
        print(json.dumps(result))
    except Exception as exc:
        print(json.dumps({'error_type': type(exc).__name__}))
        raise SystemExit(1)
