"""Reuse parsed definitions only while their freshly validated inputs are unchanged."""
import copy
from .context_search import latest
from .onboarding import Conflict, digest
from .runtime import fingerprint


class CatalogGuard:
    def __init__(self, workspace, producer):
        self.workspace = workspace
        before = self.signature()
        self.catalog = copy.deepcopy(producer(workspace))
        self.admitted = self.signature()
        if before != self.admitted:
            raise Conflict('Agent ticket metadata changed while building catalog')

    def signature(self):
        # Store.list/get and latest validate the retained content hashes afresh.
        # Hash complete records, not a hand-maintained subset of parsed fields.
        return digest({'models': self.workspace.store.list(True),
                       'context': latest(self.workspace.store),
                       'configuration': self.workspace.agent.config,
                       'intake_configuration': self.workspace.intake_configuration,
                       'engine': fingerprint()})

    def read(self):
        if self.signature() != self.admitted:
            raise Conflict('Agent ticket metadata changed')
        return copy.deepcopy(self.catalog)
