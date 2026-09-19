"""Bounded structural hypotheses from discovered metadata, never business authority.

No data is queried at scan time. Relevant hypotheses can be tested during a ticket
through the ordinary budgeted, receipt-backed query tools.
"""
VERSION = 'domain-profile-v1'
from .onboarding import encoded
import copy


def for_planner(profile, focus_table=None):
    result=copy.deepcopy(profile)
    result['tables'].sort(key=lambda t:t['asset_id']!=focus_table)
    # Keep the selected table useful even when scoped member IDs are long.
    # Counts describe the stored profile, not a claim of catalog completeness.
    fields=('candidate_key_columns','date_columns','numeric_columns','measure_ids','relationship_evidence')
    for table in result['tables']:
        for field in fields:
            members=table.get(field,[])
            if len(members)>1:
                table[field+'_profile_count']=len(members)
                table[field]=members[:1]
                table['truncated']=True
    while len(result['tables'])>1 and len(encoded(result))>2500:
        result['tables'].pop();result['tables_truncated']=True
    if result['tables']:
        table=result['tables'][0]
        for field in reversed(fields):
            if len(encoded(result))<=2500:break
            if table.get(field):
                table.setdefault(field+'_profile_count',len(table[field]))
                table[field]=[];table['truncated']=True
    while result['tables'] and len(encoded(result))>2500:
        result['tables'].pop();result['tables_truncated']=True
    return result


def infer(assets, semantic_graph=None):
    current = [a for a in assets if a.get('availability', 'CURRENT') == 'CURRENT']
    tables = sorted((a for a in current if a['kind'] == 'SemanticTable'), key=lambda a: a['id'])
    relationships = [a for a in current if a['kind'] == 'SemanticRelationship']
    result = []
    for table in tables[:12]:
        columns = [a for a in current if a['kind'] == 'SemanticColumn' and a['parent_id'] == table['id']]
        measures = [a for a in current if a['kind'] == 'Measure' and a['parent_id'] == table['id']]
        evidence = []; roles = set(); keys = []
        for rel in relationships:
            meta = rel['metadata']
            for side in ('from', 'to'):
                if meta.get(side+'Table') != table['name']: continue
                cardinality = str(meta.get(side+'Cardinality', 'unknown')).lower()
                evidence.append(rel['id'])
                if cardinality == 'many': roles.add('LIKELY_FACT_OR_BRIDGE')
                if cardinality == 'one':
                    roles.add('LIKELY_DIMENSION_OR_UNIQUE_ENTITY')
                    matches = [c['id'] for c in columns if c['name'] == meta.get(side+'Column')]
                    keys.extend(matches)
        dates = [c['id'] for c in columns if str(c['metadata'].get('dataType', '')).lower() in ('date', 'datetime')]
        numeric = [c['id'] for c in columns if str(c['metadata'].get('dataType', '')).lower() in ('int64', 'double', 'decimal')]
        result.append({'asset_id': table['id'], 'name':table['name'], 'role_hypotheses': sorted(roles) or ['UNKNOWN'],
            'candidate_key_columns': sorted(set(keys))[:8], 'date_columns': dates[:8],
            'numeric_columns': numeric[:8], 'measure_ids': [m['id'] for m in measures[:8]],
            'relationship_evidence': sorted(set(evidence))[:8],
            'grain': 'UNKNOWN_UNTIL_TESTED', 'data_profile': 'NOT_MEASURED',
            'truncated': any(len(v) > 8 for v in (keys, dates, numeric, measures, evidence))})
    nodes = (semantic_graph or {}).get('measures', {})
    profile={'version': VERSION, 'provenance': 'DETERMINISTICALLY_DERIVED',
        'authority': 'STRUCTURAL_HYPOTHESES_ONLY', 'tables': result,
        'tables_truncated': len(tables) > 12,
        'dependency_context': 'semantic_graph', 'measure_count': len(nodes),
        'unknown_semantics': ['Business grain and event meaning', 'Additivity across dimensions/time',
                              'Intended join/rate/date rules', 'Freshness SLA'],
        'limits': 'Relationship cardinality is declared metadata, not measured uniqueness. Numeric types do not establish measures; date types do not establish business time. Roles can overlap. Use bounded query receipts to test relevant hypotheses; never infer intent from names.'}
    while result and len(encoded(profile))>6000:
        result.pop();profile['tables_truncated']=True
    return profile
