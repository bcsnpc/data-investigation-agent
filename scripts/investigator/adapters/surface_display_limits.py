"""Tested adapter/reader ceiling; display qualification, not attestation evidence."""
def ceiling(observation):
    if (observation.get('tool')=='bounded_dax'
            and observation.get('surface_report_binding')=='VALUE_QUERY'
            and observation.get('surface_report',{}).get('engine')=='OLAP Server'):
        return {'connection':'NOT_SELF_REPORTABLE_FOR_READER'}
    return {}
