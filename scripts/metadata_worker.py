"""Local development auth worker. JSON in/out; credentials remain in memory."""
import json
import sys
from metadata_auth import FabricCliTokens, MetadataHttp
from onelake_metadata import collect

if __name__ == '__main__':
    try:
        request = json.load(sys.stdin)
        http = MetadataHttp(FabricCliTokens(request['tenant']))
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
