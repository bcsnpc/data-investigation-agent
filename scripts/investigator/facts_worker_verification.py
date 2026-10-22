"""Owner-side test of migrated table privileges under the actual worker role.

The caller supplies an already authenticated application database owner connection
and one existing graph node. No login/role is created. All probe writes roll back.
"""
from .facts_collectors import observation
from .shared_state import encoded, sha


def verify_worker_role(connection, *, estate, subject, at):
    value=observation(subject,'COVERAGE',{'worker_role_probe':True},at,
        ['worker-role-transactional-check'],'migration-test')
    identity=sha(value)
    try:
        connection.execute('BEGIN')
        connection.execute('SET LOCAL ROLE "id-dia-worker"')
        role=connection.execute('SELECT current_user').fetchone()[0]
        if role!='id-dia-worker':raise ValueError('FACT_WORKER_ROLE_NOT_ACTIVE')
        connection.execute('SELECT identity FROM estate_node_facts LIMIT 1')
        connection.execute('INSERT INTO estate_node_facts VALUES(%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',
            (estate,identity,subject,value['kind'],value['observed_at'],value['collected_at'],encoded(value),identity))
        connection.execute('INSERT INTO estate_fact_cursors VALUES(%s,%s,%s,%s,%s) ON CONFLICT(estate,collector,subject) DO UPDATE SET marker=excluded.marker',
            (estate,'worker-role-test',subject,'probe',value['collected_at']))
        rights={}
        for table in ('estate_node_facts','estate_fact_cursors'):
            rights[table]={operation:connection.execute('SELECT has_table_privilege(current_user,%s,%s)',(table,operation)).fetchone()[0]
                for operation in ('SELECT','INSERT','UPDATE','DELETE','TRUNCATE')}
        if rights['estate_node_facts']!={'SELECT':True,'INSERT':True,'UPDATE':False,'DELETE':False,'TRUNCATE':False}:
            raise ValueError('FACT_WORKER_APPEND_ONLY_RIGHTS_DIFFER')
        if rights['estate_fact_cursors']!={'SELECT':True,'INSERT':True,'UPDATE':True,'DELETE':False,'TRUNCATE':False}:
            raise ValueError('FACT_WORKER_CURSOR_RIGHTS_DIFFER')
        return {'status':'PASS','role':role,'privileges':rights,'writes':'ROLLED_BACK'}
    finally:
        connection.rollback()
