from uuid import UUID
import json
def declared_source_connections(path, document):
    """Follow explicit native source-connection references only.

    Unknown definition forms are not interpreted. Pipeline sink or Script
    connections never acquire source provenance by recursive string search.
    """
    if path not in ('copyjob-content.json', 'pipeline-content.json'): return set()
    if isinstance(document,str): document=json.loads(document)
    references = set()
    if path == 'copyjob-content.json':
        ref = document['properties']['source']['connectionSettings'].get('externalReferences', {}).get('connection')
        if ref: references.add(str(UUID(ref)))
    elif path == 'pipeline-content.json':
        def activities(rows):
            if not isinstance(rows, list): raise ValueError('Pipeline activities must be a list')
            for activity in rows:
                if activity.get('type') == 'Copy':
                    source = activity.get('typeProperties', {}).get('source', {})
                    if source.get('type') == 'AzureSqlSource':
                        dataset = source.get('datasetSettings', {})
                        if dataset.get('type') != 'AzureSqlTable':
                            raise ValueError('SQL source dataset declaration unavailable')
                        ref = dataset.get('externalReferences', {}).get('connection')
                        if not ref: raise ValueError('SQL source connection declaration unavailable')
                        references.add(str(UUID(ref)))
                properties = activity.get('typeProperties', {})
                for name in ('activities', 'ifTrueActivities', 'ifFalseActivities', 'defaultActivities'):
                    if name in properties: activities(properties[name])
                for case in properties.get('cases', []): activities(case.get('activities', []))
        activities(document['properties']['activities'])
    return references
