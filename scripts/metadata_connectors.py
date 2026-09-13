"""Metadata connectors expose discovery, definitions and history independently of storage."""
from typing import Protocol
from metadata_protocol import pages, definition


class UnsupportedCapability(Exception):
    pass


class MetadataConnector(Protocol):
    capabilities: frozenset[str]
    def discover_assets(self): ...
    def get_definition(self, asset): ...
    def get_refresh_history(self, asset): ...


class SqlMetadataConnector:
    capabilities = frozenset({'discovery', 'definition'})

    def __init__(self, config, catalog_reader):
        self.config, self.catalog_reader = config, catalog_reader

    def discover_assets(self):
        return self.catalog_reader(self.config['server'], self.config['database'], self.config['visibility_schema'])

    def get_definition(self, asset):
        return asset['definitions']

    def get_refresh_history(self, asset):
        raise UnsupportedCapability('SQL catalog has no refresh history')


class FabricMetadataConnector:
    capabilities = frozenset({'discovery', 'definition', 'refresh_history', 'tables'})

    def __init__(self, workspace, transport, table_reader):
        self.workspace, self.transport, self.table_reader = workspace, transport, table_reader

    def discover_assets(self):
        return pages(f'workspaces/{self.workspace}/items', self.transport)

    def get_definition(self, asset):
        suffix = '?format=TMSL' if asset['type'] == 'SemanticModel' else ''
        return definition(f"workspaces/{self.workspace}/items/{asset['id']}/getDefinition" + suffix, self.transport)

    def get_refresh_history(self, asset):
        return pages(f"workspaces/{self.workspace}/items/{asset['id']}/jobs/instances", self.transport)

    def get_tables(self, asset):
        target = f"workspaces/{self.workspace}/lakehouses/{asset['id']}/tables"
        try:
            return {'tables': pages(target, self.transport, key='data'), 'source': target, 'column_schema': False}
        except RuntimeError:
            data = self.table_reader(self.workspace, asset)
            return dict(data, column_schema=True)


class PowerBIMetadataConnector:
    capabilities = frozenset({'discovery', 'definition', 'refresh_history'})

    def __init__(self, fabric):
        self.fabric = fabric

    def discover_assets(self):
        return [item for item in self.fabric.discover_assets() if item['type'] in ('SemanticModel', 'Report')]

    def get_definition(self, asset):
        return self.fabric.get_definition(asset)

    def get_refresh_history(self, asset):
        if asset['type'] != 'SemanticModel':
            raise UnsupportedCapability('Reports have no model refresh history')
        return pages(f"groups/{self.fabric.workspace}/datasets/{asset['id']}/refreshes", self.fabric.transport, audience='powerbi')
