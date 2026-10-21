"""Version three changes current confidence CHECKs; old migration bytes stay fixed."""

def sql(backend):
    if backend=='postgresql':
        return """
ALTER TABLE estate_graph_nodes DROP CONSTRAINT estate_graph_nodes_confidence_check;
ALTER TABLE estate_graph_nodes ADD CONSTRAINT estate_graph_nodes_confidence_check CHECK(confidence IN ('DECLARED','INFERRED','VALUE_VERIFIED','VERIFIED','UNKNOWN'));
ALTER TABLE estate_graph_edges DROP CONSTRAINT estate_graph_edges_confidence_check;
ALTER TABLE estate_graph_edges ADD CONSTRAINT estate_graph_edges_confidence_check CHECK(confidence IN ('DECLARED','INFERRED','VALUE_VERIFIED','VERIFIED','UNKNOWN'));
"""
    if backend!='sqlite':raise ValueError('GRAPH_CONFIDENCE_BACKEND')
    return """
CREATE TABLE estate_graph_nodes_v3(
 estate TEXT NOT NULL, identity TEXT NOT NULL, confidence TEXT NOT NULL CHECK(confidence IN ('DECLARED','INFERRED','VALUE_VERIFIED','VERIFIED','UNKNOWN')),
 provenance TEXT NOT NULL, body TEXT NOT NULL, PRIMARY KEY(estate,identity));
CREATE TABLE estate_graph_edges_v3(
 estate TEXT NOT NULL, identity TEXT NOT NULL, source TEXT NOT NULL, target TEXT NOT NULL,
 confidence TEXT NOT NULL CHECK(confidence IN ('DECLARED','INFERRED','VALUE_VERIFIED','VERIFIED','UNKNOWN')),
 provenance TEXT NOT NULL, body TEXT NOT NULL, PRIMARY KEY(estate,identity),
 FOREIGN KEY(estate,source) REFERENCES estate_graph_nodes_v3(estate,identity),
 FOREIGN KEY(estate,target) REFERENCES estate_graph_nodes_v3(estate,identity));
INSERT INTO estate_graph_nodes_v3 SELECT * FROM estate_graph_nodes;
INSERT INTO estate_graph_edges_v3 SELECT * FROM estate_graph_edges;
DROP TABLE estate_graph_edges;
DROP TABLE estate_graph_nodes;
ALTER TABLE estate_graph_nodes_v3 RENAME TO estate_graph_nodes;
ALTER TABLE estate_graph_edges_v3 RENAME TO estate_graph_edges;
"""
