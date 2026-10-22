"""Facts-ledger migration. Applied by the application schema owner, never estate readers."""
TABLES = '''
CREATE TABLE IF NOT EXISTS estate_node_facts(
 estate TEXT NOT NULL, identity TEXT NOT NULL, subject TEXT NOT NULL,
 kind TEXT NOT NULL, observed_at TEXT NOT NULL, collected_at TEXT NOT NULL,
 body TEXT NOT NULL, body_hash TEXT NOT NULL,
 PRIMARY KEY(estate,identity),
 FOREIGN KEY(estate,subject) REFERENCES estate_graph_nodes(estate,identity));
CREATE INDEX IF NOT EXISTS estate_node_facts_lookup ON estate_node_facts(estate,subject,kind,observed_at,collected_at);
CREATE TABLE IF NOT EXISTS estate_fact_cursors(
 estate TEXT NOT NULL, collector TEXT NOT NULL, subject TEXT NOT NULL,
 marker TEXT NOT NULL, collected_at TEXT NOT NULL,
 PRIMARY KEY(estate,collector,subject));
'''


def sql(backend):
    if backend not in ('sqlite', 'postgresql'):
        raise ValueError('FACTS_BACKEND')
    grants = '''
GRANT SELECT, INSERT ON TABLE estate_node_facts TO "id-dia-worker";
GRANT SELECT, INSERT, UPDATE ON TABLE estate_fact_cursors TO "id-dia-worker";
''' if backend == 'postgresql' else ''
    return TABLES + grants
