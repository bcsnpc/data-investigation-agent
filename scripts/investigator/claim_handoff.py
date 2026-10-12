"""Optional claim-first gap phase: retained evidence, governed model, honest end.

The existing claim check owns all finding validation. This phase cannot convert
observational evidence into a causal outcome, change a referent, or grant scope.
"""
import copy
import json
from .onboarding import Conflict, digest, encoded
from .process_tape import event
from . import agent_handoff, claim_clarification


class ClaimHandoff:
    def __init__(self, workspace, *, generate=None):
        self.workspace, self.store, self.generate = workspace, workspace.store, generate
        with self.store.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS claim_handoffs(claim_id TEXT PRIMARY KEY,body TEXT,hash TEXT)')

    def get(self, identity):
        with self.store.connect() as db:
            row = db.execute('SELECT body,hash FROM claim_handoffs WHERE claim_id=?', (identity,)).fetchone()
        if row is None:
            return None
        body = json.loads(row[0])
        if digest(body) != row[1]:
            raise Conflict('Claim handoff evidence changed')
        return body

    def _save(self, body):
        with self.store.connect() as db:
            db.execute('UPDATE claim_handoffs SET body=?,hash=? WHERE claim_id=?',
                       (encoded(body), digest(body), body['claim_id']))
        event('CONFIGURATION', {'claim_handoff': copy.deepcopy(body)})

    def maybe(self, source, result=None):
        with self.store.connect() as db:
            _, current = self.workspace.claims._load(db, source['id'])
            if digest(current) != digest(source):
                raise Conflict('Automatic handoff source is not current retained claim state')
            if result is not None:
                retained = self.workspace.claim_investigations._load(db, source['id'])
                if retained is None or digest(retained) != digest(result):
                    raise Conflict('Automatic handoff result is not retained pipeline evidence')
        record = agent_handoff.authority(self.workspace, source, result)
        if record is None:
            return None
        identity = source['id']
        prior = self.get(identity)
        if prior is not None:
            return prior  # Once per claim, including failures and cap holds.
        body = {'claim_id': identity, 'authority': record, 'status': 'RUNNING',
                'finding': None, 'question': None, 'diagnostic_reads': 0,
                'physical_requests': 0, 'model_calls': 0}
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT 1 FROM claim_handoffs WHERE claim_id=?', (identity,)).fetchone()
            if row:
                return self.get(identity)
            db.execute('INSERT INTO claim_handoffs VALUES(?,?,?)', (identity, encoded(body), digest(body)))
        self._save(body)
        agent_handoff.validate(self.workspace, record,
            retained=lambda: self.get(identity)['authority'])
        try:
            return self._run(body)
        except Exception as exc:
            from .generation_policy import error_summary
            body.update(status='HELD', failure=error_summary(exc))
            self._save(body)
            # Billing/auth failures remain round stop conditions, not fallback.
            from .model_spend import SpendHold
            if isinstance(exc, SpendHold) or getattr(exc, 'status_code', None) in (401, 402, 403):
                raise
            return body

    def _run(self, body):
        from .agent_loop import AgentLoop
        from .agent_provider import GovernedDecision
        from .agent_journal import Journal
        from .question_intake import snapshot
        runtime = self.workspace.agent
        source = body['authority']['original']['source']
        original_result = body['authority']['original']['result']
        identity = body['claim_id']
        journal = Journal(self.store, 'claim-handoff:' + identity, now=runtime.clock)
        catalog = snapshot(self.workspace)
        recorded_catalog = source.get('catalog_hash')
        if recorded_catalog and recorded_catalog != digest(catalog):
            body.update(status='HELD', reason='HANDOFF_CATALOG_CHANGED')
            self._save(body); return body
        policy = body['authority']['policy']; deadline = runtime.clock() + policy['wall_seconds']
        decide = GovernedDecision(runtime, 'claim-handoff:' + identity, generate=self.generate,
                                 deadline=deadline)

        def admitted(kind, ordinal):
            agent_handoff.validate(self.workspace, body['authority'],
                retained=lambda: self.get(identity)['authority'])
            if runtime.clock() >= deadline:
                raise Conflict('Automatic handoff deadline')
            # Any quantity port below admits the same confirmed scope through
            # ordinary runtime/read guards and carries prior diagnostics.
            # Model reservations use the shared daily and dollar governors.

        def result(value):
            evidence_id = journal.persist({'event': 'HANDOFF_RETAINED_EVIDENCE', 'result': value})
            return {'status': 'AVAILABLE', 'data': copy.deepcopy(value), 'evidence_ids': [evidence_id]}

        def definitions():
            return result({'source': 'RETAINED_APPROVED_CONTEXT', 'catalog': catalog})

        def propose_answer(choice_id):
            # A proposal is grounded in an existing typed choice and remains
            # a question. It never adopts the candidate or replaces a fact.
            claim = source['claim']
            q, choices = claim_clarification.plan(claim, catalog)
            if q is None or choice_id not in choices:
                raise Conflict('No retained typed missing-fact candidate supports this proposal')
            selected=next(c for c in q['choices'] if c['id']==choice_id)
            label=(claim.get('selected_binding') or {}).get('label')
            proposal='Should we interpret this as '+selected['label']+(' for '+label if label else '')+'?'
            q,choices=claim_clarification.question(q['field'],proposal,
                [(selected['label'],choices[choice_id])],digest(catalog),[f['id']for f in claim['facts']])
            claim_clarification.validate_question(claim, q)
            with self.store.connect() as db:
                db.execute('BEGIN IMMEDIATE')
                revision, current = self.workspace.claims._load(db, identity)
                if revision != source['revision'] or digest(current) != digest(source):
                    raise Conflict('Claim changed before handoff question')
                current['revision'] += 1; current['status'] = 'CLARIFYING'
                current['questions'] = [q]; current['_choices'] = choices
                current['interpretation'] = None; current['engine_admission'] = None
                current['history'].append({'kind': 'AUTOMATIC_AGENT_QUESTION',
                    'authority_hash': body['authority']['hash'], 'question_id': q['id']})
                self.workspace.claims._persist(db, current)
            body['question'] = copy.deepcopy(q)
            response = result({'question': q, 'authority_hash': body['authority']['hash']})
            response['status'] = 'QUESTION_POSTED'
            return response

        obtained={}
        def standard():
            from .claim_reference import compile as compile_reference
            from .claim_investigations import ClaimInvestigations
            from .ticket_findings import from_state
            compiled=compile_reference(source,catalog)
            service=ClaimInvestigations(self.workspace)
            binding=source['claim']['selected_binding']
            prepared={'model_id':binding['model_id'],'measure_ids':[binding['measure_id']]}
            envelope=service._envelope(prepared,source)
            envelope.update({k:copy.deepcopy(compiled[k])for k in('target_visual','report_binding','reported_figure')})
            envelope.update(ticket_shape='MISMATCH_COMPLAINT',comparison_mode='VERTICAL')
            prior=(original_result or {}).get('reads',{}).get('diagnostic',0)
            if type(prior)is not int or not 0<=prior<envelope['limits']['cloud_calls']:
                raise Conflict('Automatic handoff has no remaining diagnostic capacity')
            state=runtime.create(envelope,'automatic-claim-gap:'+identity)
            body['session_id']=state['id'];self._save(body)
            with runtime.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE');state=runtime.load(db,state['id'])
                state['cloud_calls']=prior
                runtime.save(db,state,'AUTOMATIC_GAP_BUDGET_CARRIED',{'prior_diagnostic_reads':prior})
            try:
                runtime.run_process(state['id']);runtime.synthesize(state['id'])
                finding=from_state(runtime.get(state['id']))
            finally:
                retained=runtime.get(state['id'])
                body['diagnostic_reads']=retained['cloud_calls']-prior
                body['prior_diagnostic_reads']=prior
                body['physical_requests']=retained.get('physical_calls',0)
                body['read_receipts']=copy.deepcopy(retained.get('process_read_receipts',[]))
                self._save(body)
            response=result({'findings':finding})
            obtained.update(finding=finding,evidence_id=response['evidence_ids'][0])
            self._save(body)
            return response

        def delivery(decision, evidence, **context):
            finding=obtained.get('finding')
            if not finding or finding['classification']=='HELD' or decision['outcome']!=finding['classification']:
                raise ValueError('HANDOFF_FINDING_SUPPORT_NOT_ESTABLISHED')
            refs={ref for claim in decision['claims']for ref in claim['evidence_ids']}
            if obtained['evidence_id'] not in refs:
                raise ValueError('HANDOFF_FINDING_ORIGINAL_EVIDENCE_REQUIRED')
            # Revalidate original engine observations, coverage and outputs;
            # model-written claim prose is never the delivered explanation.
            from .ticket_findings import from_state
            actual=from_state(runtime.get(finding['session_id']))
            if actual!=finding:raise Conflict('Handoff finding changed')
            body['finding']=copy.deepcopy(actual)
            return {'validated':True,'outputs':copy.deepcopy(actual['outputs'])}

        empty = {'type': 'object', 'additionalProperties': False, 'properties': {}, 'required': []}
        q,choices=claim_clarification.plan(source['claim'],catalog)
        tools = {'inspect_retained_definitions': definitions, 'propose_missing_answer': propose_answer,
                 'run_standard_investigation':standard}
        schemas = {name: empty for name in tools}
        schemas['propose_missing_answer']={'type':'object','additionalProperties':False,'properties':{
            'choice_id':{'type':'string','minLength':1}},'required':['choice_id']}
        from .process_outcomes import OUTCOMES
        loop = AgentLoop(tools=tools, schemas=schemas, decide=decide,
            persist=journal.persist, validate_delivery=delivery, outcomes=OUTCOMES,
            admit=admitted, step_cap=policy['step_cap'], wall_seconds=policy['wall_seconds'])
        try:
            end = loop.run({'text': '\n'.join(d['request'].get('text', '') for d in source.get('documents', [])),
                'task': 'Address only the recorded gap. Run the standard governed check only for an already confirmed faithful scope. A missing-answer proposal selects one retained typed candidate for explicit user confirmation; it never adopts a fact. Do not repeat a question verbatim or replace the referent.',
                'gap': body['authority']['kind'],'missing_answer_candidates':q['choices']if q else[]}, fixed_facts=source['claim']['settled'],
                context_id=digest(catalog), starting_evidence={
                    'claim:' + digest(source): source,
                    **({'pipeline:' + digest(original_result): original_result} if original_result else {})})
        finally:
            body['model_calls']=decide.calls
            body['journal_identity']='claim-handoff:'+identity
            self._save(body)
        body.update(status=end['status'], loop=end, model_calls=decide.calls)
        if end['status'] == 'WAITING_FOR_USER' and not body['question']:
            raise ValueError('HANDOFF_QUESTION_NOT_RECORDED')
        self._save(body)
        return body


def maybe(workspace, source, result=None):
    if not agent_handoff.settings(workspace)['enabled']:
        return None
    return ClaimHandoff(workspace).maybe(source, result)
