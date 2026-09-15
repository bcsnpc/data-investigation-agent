"""Conservative bounded stop after repeated observations without nonblank values."""

def informative(observation):
    if not observation or observation['status']!='COMPLETED':return False
    values=observation['values']
    for row in values:
        if not isinstance(row,dict):continue
        if 'type' in row:
            if row.get('type')!='blank':return True
        else:
            # Dimension labels alone do not make all-BLANK metrics informative.
            if any(k!='[dimension]' and isinstance(v,dict) and v.get('type')!='blank' for k,v in row.items()):return True
    return False
