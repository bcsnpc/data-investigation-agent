"""Read-only live modified-item listings and per-owner definition fingerprints."""
from uuid import UUID
from urllib.parse import quote
from metadata_protocol import relative, definition
from metadata_inventory import expand_definition
from ..shared_state import sha


class Assets:
    def __init__(self): self.values = []
    def asset(self, identity, kind, name, source, metadata, parent=None):
        self.values.append({'id': identity, 'kind': kind, 'name': name, 'parent_id': parent, 'metadata': metadata})


class FabricChanges:
    def __init__(self, workspace, owners, http, *, max_pages=5, max_items=1000):
        self.workspace = str(UUID(workspace)); self.http = http
        if not owners or len(owners) > 100 or len(set(owners)) != len(owners): raise ValueError('GRAPH_OWNER_ALLOWLIST')
        self.owners = {str(UUID(owner)) for owner in owners}
        if type(max_pages) is not int or not 1 <= max_pages <= 10 or type(max_items) is not int or not 1 <= max_items <= 10000:
            raise ValueError('GRAPH_LISTING_BOUND')
        self.max_pages, self.max_items = max_pages, max_items
        self.identity = 'fabric-workspace:' + self.workspace + ':' + sha(sorted(self.owners))
        self.items = {}
        self.configured_owners=tuple(sorted(self.owner(key) for key in self.owners))

    def list_changes(self):
        base = 'workspaces/' + self.workspace + '/items'; endpoint = base
        items = {}; seen = set(); complete = False; count = 0
        for _ in range(self.max_pages):
            if endpoint in seen: raise ValueError('GRAPH_REPEATED_CONTINUATION')
            seen.add(endpoint); response = self.http(endpoint)
            if response['status_code'] != 200:
                from .metadata_error import MetadataUnavailable
                raise MetadataUnavailable(response['status_code'],response.get('text'))
            body = response['text']
            for item in body['value']:
                count += 1
                if count > self.max_items: raise ValueError('GRAPH_LISTING_ITEM_BOUND')
                identity = str(UUID(item['id']))
                if identity in items: raise ValueError('GRAPH_DUPLICATE_LISTED_ITEM')
                items[identity] = item
            next_url = body.get('continuationUri') or body.get('@odata.nextLink')
            token = body.get('continuationToken')
            if not next_url and not token: complete = True; break
            endpoint = relative(next_url) if next_url else base + '?continuationToken=' + quote(token, safe='')
            if not endpoint.startswith(base + '?'): raise ValueError('GRAPH_CONTINUATION_SCOPE')
        self.items = {key: value for key, value in items.items() if key in self.owners}
        signals = []
        for key, item in sorted(self.items.items()):
            # Missing modified metadata means definition-hash polling, not a false unchanged assertion.
            modified = item.get('lastModifiedDateTime') or item.get('modifiedDateTime') or item.get('modifiedTime')
            signals.append({'owner': self.owner(key), 'fingerprint': sha({'modified': modified, 'item': item}) if modified else None, 'deleted': False})
        # Workspace visibility can shrink on permission loss. Absence is not deletion proof.
        # Only an explicit deleted event may delete; a successful list is still not an owner tombstone.
        return {'items': signals, 'complete': False}

    def owner(self, identity): return 'fabric://' + self.workspace + '/' + identity

    def fetch(self, owner):
        prefix = 'fabric://' + self.workspace + '/'
        key = owner.removeprefix(prefix)
        if not owner.startswith(prefix) or key not in self.items: raise ValueError('GRAPH_FETCH_OWNER_SCOPE')
        item = self.items[key]; kind = item['type']
        if kind not in ('Report', 'SemanticModel', 'Notebook', 'DataPipeline', 'CopyJob'):
            raise RuntimeError('GRAPH_DEFINITION_KIND_UNAVAILABLE')
        endpoint = 'workspaces/' + self.workspace + '/items/' + key + '/getDefinition'
        def checked_call(*args,**kwargs):
            from .metadata_error import MetadataUnavailable
            response=self.http(*args,**kwargs)
            if response['status_code'] not in (200,202):
                raise MetadataUnavailable(response['status_code'],response.get('text'))
            return response
        parts = definition(endpoint + ('?format=TMSL' if kind == 'SemanticModel' else ''), checked_call)
        assets = Assets()
        # Volatile listing clocks are not definition content.
        metadata = {k: v for k, v in item.items() if k not in ('lastModifiedDateTime', 'modifiedDateTime', 'modifiedTime')}
        assets.asset(owner, kind, item['displayName'], endpoint, metadata)
        expand_definition(assets, owner, kind, parts, endpoint)
        return {'assets': assets.values, 'source_asset_ids': []}


class SqlSchemaChanges:
    """Bounded schema polling through the existing attested target-catalog reader.

    definitions(owner) is the caller's approved exact-object definition reader;
    this adapter neither creates SQL routes nor runs a whole database collector.
    """
    def __init__(self, identity, objects, read_catalog, definitions):
        if not objects or len(objects) > 100: raise ValueError('GRAPH_SQL_OWNER_BOUND')
        self.identity, self.objects, self.read_catalog, self.definitions = identity, objects, read_catalog, definitions
        self.configured_owners=tuple(sorted(objects))
    def list_changes(self):
        result = []
        for owner, obj in sorted(self.objects.items()):
            columns, proof = self.read_catalog(obj)
            if proof.get('kind') != 'NATIVE_TARGET_CATALOG': raise ValueError('GRAPH_SCHEMA_ATTESTATION_REQUIRED')
            # Column equality alone says nothing about a changed view/procedure
            # body. Without an observed object modify date, poll its definition.
            modified = proof.get('object_modified_at')
            result.append({'owner': owner, 'fingerprint': sha({'columns': columns, 'object': obj, 'modified': modified}) if modified else None, 'deleted': False})
        return {'items': result, 'complete': False}
    def fetch(self, owner):
        if owner not in self.objects: raise ValueError('GRAPH_SQL_OWNER_SCOPE')
        return self.definitions(owner, self.objects[owner])
