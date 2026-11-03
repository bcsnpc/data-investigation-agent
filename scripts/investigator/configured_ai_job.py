"""Durable configured-provider jobs; unfinished external calls are never replayed.

The legacy asynchronous Anthropic batch runner remains available for its saved
receipts. New configured jobs use the common structured-call surface.
"""
from copy import deepcopy
from datetime import datetime, timezone
from .shared_state import sha
from .ai_steps import Steps

NAMESPACE = 'configured_ai_jobs'


class ConfiguredJob:
    def __init__(self, state, config, record, *, steps_factory=Steps):
        from .privacy_capture import ACTIVE
        if ACTIVE.get() is not None:
            raise ValueError('ENRICHMENT_PROJECTED_SHARED_STATE_UNIMPLEMENTED')
        self.state, self.config, self.record = state, config, record
        self.steps_factory = steps_factory

    def submit(self, sources, *, batch_key, evaluation=False):
        try:
            self.state.get(NAMESPACE, batch_key)
        except KeyError:
            pass
        else:
            raise ValueError('CONFIGURED_AI_JOB_ALREADY_ADMITTED')
        body = {'status': 'ADMITTED', 'configuration_sha256': sha(self.config),
                'sources': deepcopy(sources), 'evaluation': evaluation, 'results': [],
                'started_at': datetime.now(timezone.utc).isoformat()}
        self.state.put(NAMESPACE, batch_key, body)
        steps = self.steps_factory(configuration=self.config['ai_routing'], tenant=self.config['tenant'],
            state=self.state, record=lambda event: self.record('configured-ai', event),
            investigator_configuration=self.config.get('investigator_configuration'))
        for index, source in enumerate(sources):
            # Commit the dispatch intent before contacting a provider. A crash
            # leaves IN_FLIGHT, not a licence to spend again on resume.
            body.update(status='IN_FLIGHT', current_index=index)
            self._save(batch_key, body)
            case_id = source.get('case_id') or 'enrichment:' + sha([batch_key, source])
            try:
                if evaluation:
                    output = steps.evaluate(source, case_id=case_id,
                        grading_role=self.config.get('grading_role', 'PRIMARY'))
                else:
                    output = steps.enrich(source, case_id=case_id)
                    from .enrichment import EnrichmentStore
                    EnrichmentStore(self.state).apply(source, output,
                        at=datetime.now(timezone.utc).isoformat(), producer='configured-provider',
                        recording_class='EXACT', evidence_ids=[sha([batch_key, index, output])])
            except Exception as error:
                body.update(status='INTERRUPTED', error_type=type(error).__name__)
                self._save(batch_key, body)
                raise
            body['results'].append({'case_id': case_id, 'output': output})
            body.update(status='BETWEEN_CALLS')
            self._save(batch_key, body)
        body.update(status='COMPLETED', completed_at=datetime.now(timezone.utc).isoformat())
        self._save(batch_key, body)
        return self.resume(batch_key)

    def _save(self, key, body):
        prior = self.state.get(NAMESPACE, key)
        self.state.put(NAMESPACE, key, deepcopy(body), revision=prior['revision'])

    def resume(self, batch_key):
        body = self.state.get(NAMESPACE, batch_key)['body']
        if body['configuration_sha256'] != sha(self.config):
            raise ValueError('CONFIGURED_AI_JOB_CONFIGURATION_CHANGED')
        return {'status': body['status'], 'batch_key': batch_key,
                'results': deepcopy(body['results']),
                'resubmitted': False, 'estate_reads': 0}
