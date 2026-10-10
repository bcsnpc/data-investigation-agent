"""Translate existing evaluation picks without manufacturing questionnaire facts."""
from .intake_questionnaire import VERSION

def map_form(form, text):
    if not form.get('report_id') or not form.get('page_id'):
        raise ValueError('QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick invented')
    route=form.get('comparison')
    if route=='APPLICATION':comparison={'kind':'APPLICATION'}
    elif route in ('LOOKS_WRONG','STALE','DECLARED_SUBJECT'):
        comparison={'kind':'NOTHING'}
    elif route is None and form.get('subject')=='MEASURE_TEXT':
        comparison={'kind':'NOTHING'}
    else:
        raise ValueError('QUESTIONNAIRE_NOT_MEASURABLE: comparator not determined or lacks the other report/page pick; no substitute selected')
    return {'version':VERSION,'request_key':form['request_key'],'report_id':form['report_id'],
        'page_id':form['page_id'],'visual_id':form.get('target_id'),
        'comparing':comparison,'description':text}
