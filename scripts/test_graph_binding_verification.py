import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
import sqlglot
from investigator import estate_graph_contract as c
from investigator.adapters.graph_binding_verification import BindingVerificationResolver,verify_binding
from investigator.adapters.binding_verification import BindingVerificationRoute
from investigator.lineage_binding import Ledger,seal
from investigator.verification_budget import VerificationBudget
from investigator.process_debugging import attest_surface
from investigator.onboarding import digest,encoded,Conflict
from investigator.receipt_integrity import seal as seal_read
from investigator.raw_surface_report import capture,report
from test_lineage_binding import proposal
from test_estate_graph import T0,proof


class GraphBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.db=sqlite3.connect(':memory:');self.addCleanup(self.db.close)
        self.db.executescript("ATTACH DATABASE ':memory:' AS lower_data; ATTACH DATABASE ':memory:' AS upper_data; CREATE TABLE lower_data.items(amount INT,key INT); CREATE TABLE upper_data.items(amount INT,key INT); INSERT INTO lower_data.items VALUES(3,1),(3,2),(4,3); INSERT INTO upper_data.items SELECT * FROM lower_data.items; CREATE TABLE flexible_diagnostics(id TEXT,model_id TEXT,created TEXT,status TEXT,request TEXT,result TEXT);")
        self.objects={name:{'asset_id':name,'connection':'endpoint','database':side,
            'catalog':{'id':name,'metadata':{'schema_name':side,'name':'items','type_desc':'USER_TABLE',
                'columns':[{'name':'amount','data_type':'int'},{'name':'key','data_type':'bigint'}]}}}
            for name,side in [('input-table','lower_data'),('output-table','upper_data')]}
        self.process=SimpleNamespace(model={'id':'model','context_id':'context'},config={'fabric':{'sql_reader':{'server':'endpoint'}}},
            store=SimpleNamespace(connect=lambda:self.db),meter_read=lambda kind,fn:fn())
        self.route=BindingVerificationRoute(self.process,objects=self.objects,context='context')
        self.binding=proposal();self.binding['sources'][0]['columns'].append('key');self.binding['expression']['relation']['columns'].append('key')
        self.ledger=Ledger(Path(self.tmp.name)/'bindings.jsonl')
        self.sample={'kind':'KEY_RANGE','column':'key','lower':1,'upper':20,'provenance':'synthetic explicit sample'}
        self.controls=[];self.budget=VerificationBudget({},1,record=self.controls.append)
        def execute(side,plan):
            query=plan['compiled']['query'];sql=sqlglot.transpile(query,read='tsql',write='sqlite')[0]
            cursor=self.db.execute(sql);quantities=dict(zip([col[0] for col in cursor.description],cursor.fetchone()))
            identity='read-'+side;database=self.objects['output-table' if side=='TARGET' else 'input-table']['database']
            columns={'identity':'report_identity','engine':'report_engine','object':'report_object'}
            native_row={**quantities,'report_identity':'reader','report_engine':'sqlite','report_object':database}
            raw=capture([native_row],columns);surface={'identity':'reader','engine':'sqlite','object':database,'connection':'endpoint'}
            request={'context_id':'context','read_address':plan['address'],'query':query,'surface_report_columns':columns}
            result={'rows':[quantities],'surface_report':report(raw),'surface_report_binding':'VALUE_QUERY','raw_surface_report':raw}
            self.db.execute('INSERT INTO flexible_diagnostics VALUES(?,?,?,?,?,?)',(identity,'model',T0,'COMPLETED',encoded({'plan':{'query':query},**request}),encoded(result)))
            seal_read(self.db,'bounded_fabric_sql',identity)
            evidence={'id':identity,'tool':'bounded_fabric_sql','execution_surface':surface,'surface_report':report(raw),
                'surface_report_binding':'VALUE_QUERY','surface_report_receipt_id':identity,
                'surface_report_types':{'engine':'ENGINE_PRODUCT','object':'DATABASE'},'read_address':plan['address'],
                'values':[quantities],'context_id':'context','request_hash':digest(request)}
            evidence['surface_attestation']=attest_surface(surface,report(raw),tuple(columns))
            return {'status':'COMPLETED','context':'context','address':plan['address'],'quantities':quantities,'evidence':evidence}
        self.route.execute=execute
        self.graph={'nodes':[],'edges':[]}
        for table in ('input-table','output-table'):
            self.graph['nodes'].append(c.node(table,'owner','TABLE',table,proof(),properties={'asset_id':table}))
            for column in ('amount','key'):
                identity=table+'/'+column
                self.graph['nodes'].append(c.node(identity,'owner','COLUMN',column,proof()))
                self.graph['edges'].append(c.edge(table+'-'+column,'owner','CONTAINS',table,identity,proof()))
        self.edge=c.edge('dependency','owner','COMPUTED_FROM','output-table/amount','input-table/amount',proof())
        self.graph['edges'].append(self.edge)

    def prepare(self):
        result=verify_binding(self.binding,route=self.route,sample=self.sample,budget=self.budget,ledger=self.ledger)
        resolver=BindingVerificationResolver(estate='estate',ledger=self.ledger,route=self.route,graph=self.graph,
            attachments={result['evidence_id']:'dependency'})
        return result,resolver

    def test_real_compiler_sealed_sqlite_profiles_accept_partial_attestation_with_distinct_objects(self):
        result,resolver=self.prepare();got=resolver(result['evidence_id'])
        self.assertEqual(got['status'],'VERIFIED');self.assertEqual(got['surface_difference']['grade'],'OBJECT_DISTINCT')
        self.assertEqual(got['snapshot'],'SNAPSHOT_UNVERIFIED');self.assertIn('semantic correctness',got['qualification'])
        self.assertEqual(self.budget.count,2);self.assertEqual(len(got['original_receipts']),2)
        self.assertTrue(all(o['evidence']['surface_attestation']['coverage']=='PARTIAL' for o in result['verification']['observations']))
    def test_sealed_physical_read_tamper_cannot_verify(self):
        result,resolver=self.prepare();self.db.execute("UPDATE flexible_diagnostics SET status='FAILED' WHERE id='read-SOURCE'")
        with self.assertRaises(Conflict):resolver(result['evidence_id'])
    def test_recompilation_endpoint_or_definition_mismatch_cannot_attach(self):
        result,resolver=self.prepare();resolver.graph['edges'][-1]['target']='input-table/key'
        # The key is an admitted dependency too, but a different code definition
        # must never be borrowed because its profile happens to agree.
        resolver.graph['edges'][-1]['provenance']['definition_hash']='b'*64
        with self.assertRaisesRegex(ValueError,'DEFINITION_OR_ENDPOINT'):resolver(result['evidence_id'])
        resolver.graph=copy.deepcopy(self.graph);self.route.objects['output-table']['catalog']['metadata']['name']='other_items'
        with self.assertRaisesRegex(ValueError,'ORIGINAL_QUERY_DIFFERS'):resolver(result['evidence_id'])
    def test_wrong_values_preserved_in_ledger_never_promoted(self):
        self.db.execute('UPDATE upper_data.items SET amount=amount+1')
        result,resolver=self.prepare();self.assertEqual(result['verification']['status'],'FALSIFIED')
        self.assertEqual(len(self.ledger.records()),1)
        with self.assertRaisesRegex(ValueError,'PROFILE_NOT_VERIFIED'):resolver(result['evidence_id'])
    def test_no_physical_meter_refuses_before_query(self):
        self.process.meter_read=None
        with self.assertRaisesRegex(ValueError,'METER_REQUIRED'):self.prepare()
        self.assertEqual(self.budget.count,0)

if __name__=='__main__':unittest.main()
