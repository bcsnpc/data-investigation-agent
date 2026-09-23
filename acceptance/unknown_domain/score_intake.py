"""Fixed-fixture intake grading, not a general semantic judge or runtime rule."""
def score(case,decision):
    expected=case['expected_action']
    if decision.get('action')!=expected:
        return {'passed':False,'reason':'UNNECESSARY_CLARIFICATION' if expected=='PROPOSE' else 'MISSING_MATERIAL_SCOPE_FACT'}
    if expected=='ASK':
        fact=case.get('missing_fact')
        if not fact or decision.get('question')!=case['decision']['question']:
            return {'passed':False,'reason':'MATERIAL_FACT_NOT_NAMED'}
        if case['payload'].get('user_context',{}).get(fact):
            return {'passed':False,'reason':'FACT_ALREADY_SUPPLIED'}
        return {'passed':True,'reason':'MATERIAL_FACT_REQUIRED','missing_fact':fact}
    if decision.get('question') is not None:
        return {'passed':False,'reason':'UNNECESSARY_CLARIFICATION'}
    if decision.get('measure_id')!=case['decision']['measure_id']:
        return {'passed':False,'reason':'WRONG_ANCHOR'}
    return {'passed':True,'reason':'PROCEED_TO_SCOPE_REVIEW'}
