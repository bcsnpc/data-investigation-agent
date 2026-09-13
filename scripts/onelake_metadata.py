"""Read OneLake schema/table metadata using the existing Fabric CLI identity.

Run with the Fabric CLI virtualenv Python. Tokens stay in this process.
"""
import argparse
import contextlib
import io
import json
from urllib.parse import quote


def collect(workspace, lakehouse, catalog, get=None):
    base = f'https://onelake.table.fabric.microsoft.com/delta/{quote(workspace, safe="")}/{quote(lakehouse, safe="")}/api/2.1/unity-catalog/'
    if get is None:
        import requests
        from fabric_cli.core.fab_auth import FabAuth
        with contextlib.redirect_stdout(io.StringIO()):
            token = FabAuth().get_access_token(['https://storage.azure.com/.default'], interactive_renew=False)
        if not token:
            raise RuntimeError('Storage authentication unavailable')
        def get(path):
            response = requests.get(base + path, headers={'Authorization': 'Bearer ' + token}, timeout=60, allow_redirects=False)
            if response.status_code != 200:
                raise RuntimeError(f'OneLake metadata HTTP {response.status_code}')
            return response.json()
    def listing(path, key):
        rows, seen = [], set()
        while True:
            value = get(path)
            rows.extend(value[key])
            page = value.get('next_page_token')
            if not page:
                return rows
            if page in seen:
                raise RuntimeError('Repeated OneLake page token')
            seen.add(page)
            path = path.split('&page_token=')[0] + '&page_token=' + quote(page, safe='')
    schemas = listing('schemas?catalog_name=' + quote(catalog, safe=''), 'schemas')
    tables = []
    for schema in schemas:
        for table in listing('tables?catalog_name=' + quote(catalog, safe='') + '&schema_name=' + quote(schema['name'], safe=''), 'tables'):
            full_name = catalog + '.' + schema['name'] + '.' + table['name']
            details = get('tables/' + quote(full_name, safe=''))
            details['schema_name'] = schema['name']
            tables.append(details)
    return {'schemas': schemas, 'tables': tables, 'source': base}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('workspace'); parser.add_argument('lakehouse'); parser.add_argument('catalog')
    args = parser.parse_args()
    try:
        print(json.dumps(collect(args.workspace, args.lakehouse, args.catalog)))
    except Exception as exc:
        print(json.dumps({'error_type': type(exc).__name__}))
        raise SystemExit(1)
