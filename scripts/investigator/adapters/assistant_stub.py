"""Interface-only native assistants; no network or evidence substitution."""
class GenieStub:
    def __init__(self,manifest):
        from ..estate_manifest import validate
        validate(manifest)
        if {a['implementation'] for a in manifest['adapters']}!={'databricks'}:
            raise ValueError('Genie stub requires a declared Databricks adapter')
    def propose(self,question):
        raise NotImplementedError('Genie transport is not installed; no network request')
