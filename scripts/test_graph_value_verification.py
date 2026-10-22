"""Hostile mapped-value producers, honest qualifications and immutable graph history."""
import copy,hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from investigator import estate_graph_contract as c
from investigator.graph_value_verification import ValueVerificationResolver,scope_hash,PIN_KEYS
from investigator.estate_graph_repository import GraphRepository
from investigator.shared_state import SharedState
from test_estate_graph import graph,T0,T1
import test_report_scope_contract as inventory_fixture


def fixture():
    h=inventory_fixture.ReportScopeTests();h.setUp()
    cell={'target_id':'visual','measure_id':'measure','grouping_columns':[],'key_restrictions':[],'mode':'UNGROUPED'};cell['id']=c.digest(cell)
    translation={'restriction_mappings':[{'restriction_hash':c.digest(h.active[0]),'source':{'predicate':'recorded source predicate'},
        'target':{'predicate':'recorded target predicate'},'definition_hash':'a'*64}]}
    mapping={'version':'graph-value-mapping-v1','id':'mapping','producer':'LINEAGE_VALUE_COMPILER','estate':'estate','edge_id':'vm','source':'visual','target':'measure',
        'scope_hash':'','definition_hash':'a'*64,'graph_hash':c.digest(graph()),'source_statement_hash':'','target_statement_hash':'',
        'visual_address':{'report_id':'report-a','page_id':'page','target_id':'visual'},'visual_cell':cell,'inventory':h.inventory,'active_restrictions':h.active,'report_binding':h.binding,'report_catalog':h.reports,
        'mapping':translation,'mapping_hash':c.digest(translation),'tolerance':{'kind':'ABSOLUTE','value':'0','source':'Owner requested exact comparison'},
        'endpoint_hashes':{'source':'d'*64,'target':'e'*64}}
    statements={'source':'EVALUATE ROW("quantity",42)','target':'SELECT 42 AS quantity'}
    for side,statement in statements.items():mapping[side+'_statement_hash']=hashlib.sha256(statement.encode()).hexdigest()
    mapping['scope_hash']=scope_hash(mapping)
    check={'version':'graph-value-check-v1','id':'check','producer':'LINEAGE_VALUE_CHECK',**{k:mapping[k]for k in ('estate','edge_id','source','target','scope_hash','definition_hash','graph_hash')},
        'mapping_id':'mapping','source_read':'s','target_read':'t','explanation_read':None,'observed_at':T0}
    reads={}
    for side,identity in [('source','s'),('target','t')]:
        declared={'identity':'reader','engine':'synthetic','connection':'connection-'+side,'object':mapping[side]}
        reads[identity]={'id':identity,'producer':'QUERY_READ','status':'SUCCEEDED','estate':'estate','object_id':mapping[side],
            **{k:mapping[k]for k in ('scope_hash','definition_hash','mapping_hash')},'endpoint_hash':mapping['endpoint_hashes'][side],
            'statement_hash':mapping[side+'_statement_hash'],'statement':statements[side],
            'value':{'state':'VALUE','typed_value':{'type':'INT64','value':'42'}},
            'attestation':{'declared':declared,'reported':copy.deepcopy(declared),'reportable':['identity','engine','connection','object'],'binding':'VALUE_QUERY'},
            'snapshot':None,'observed_at':T0}
    pins={k:copy.deepcopy(mapping[k])for k in PIN_KEYS}
    resolver=ValueVerificationResolver(lambda i:copy.deepcopy(check)if i=='check'else None,
        lambda i:copy.deepcopy(mapping)if i=='mapping'else None,lambda i:copy.deepcopy(reads[i]),current_pins=lambda m:copy.deepcopy(pins))
    return resolver,check,mapping,reads,pins


def reseal(check,mapping,reads,pins):
    mapping['mapping_hash']=c.digest(mapping['mapping']);mapping['scope_hash']=scope_hash(mapping)
    check['scope_hash']=mapping['scope_hash']
    for read in reads.values():read.update(scope_hash=mapping['scope_hash'],mapping_hash=mapping['mapping_hash'])
    pins.update({k:copy.deepcopy(mapping[k])for k in PIN_KEYS})


class MappedValueProofTests(unittest.TestCase):
    def test_agreement_has_distinct_grade_and_snapshot_limit(self):
        resolver,*_=fixture();proof=resolver('check')
        self.assertEqual('VALUE_VERIFIED',proof['status']);self.assertEqual('VALUE_QUERY_VERIFICATION',proof['producer'])
        self.assertEqual('SNAPSHOT_UNVERIFIED',proof['snapshot']);self.assertIn('under this recorded mapping',proof['qualification'])
        self.assertIn('not established',proof['qualification']);self.assertNotEqual('VERIFIED',proof['status'])

    def test_blank_is_comparable_and_not_zero_or_missing(self):
        resolver,check,mapping,reads,pins=fixture()
        for r in reads.values():r['value']={'state':'BLANK','typed_value':None}
        self.assertTrue(resolver('check')['values_equal'])
        reads['t']['value']={'state':'VALUE','typed_value':{'type':'INT64','value':'0'}}
        with self.assertRaisesRegex(ValueError,'UNEXPLAINED'):resolver('check')
        reads['t']['value']={'state':'UNAVAILABLE','typed_value':None}
        with self.assertRaisesRegex(ValueError,'RESULT_STATE'):resolver('check')

    def test_precision_never_defaults_or_accepts_nonfinite(self):
        for changed in (None,{'kind':'ABSOLUTE','value':'0','source':''},{'kind':'ABSOLUTE','value':'NaN','source':'owner'}, {'kind':'ABSOLUTE','value':'-1','source':'owner'}):
            resolver,check,mapping,reads,pins=fixture();mapping['tolerance']=changed
            with self.subTest(changed=changed),self.assertRaises(ValueError):resolver('check')

    def test_unsupported_inventory_and_missing_mapped_restriction_refuse(self):
        resolver,check,mapping,reads,pins=fixture();mapping['mapping']['restriction_mappings']=[];reseal(check,mapping,reads,pins)
        with self.assertRaisesRegex(ValueError,'RESTRICTION_COVERAGE'):resolver('check')
        resolver,check,mapping,reads,pins=fixture();entry=mapping['inventory']['entries'][0]
        entry.update(disposition='UNSUPPORTED',effect='EXCLUDED',restrictions=[]);mapping['active_restrictions']=[];mapping['mapping']['restriction_mappings']=[]
        reseal(check,mapping,reads,pins)
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_DECLARATION'):resolver('check')

    def test_wrong_or_unattested_read_and_changed_pins_refuse(self):
        for field,value in [('status','FAILED'),('mapping_hash','f'*64),('endpoint_hash','f'*64),('statement','SELECT 43 AS quantity')]:
            resolver,check,mapping,reads,pins=fixture();reads['t'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):resolver('check')
        resolver,check,mapping,reads,pins=fixture();reads['t']['attestation']['reported']={}
        with self.assertRaisesRegex(ValueError,'ATTESTATION'):resolver('check')
        for key in ('graph_hash','scope_hash','mapping_hash','definition_hash','endpoint_hashes'):
            resolver,check,mapping,reads,pins=fixture();pins[key]='changed'
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'CURRENT_PIN'):resolver('check')

    def test_forged_producer_missing_inventory_and_wrong_cell_refuse(self):
        resolver,check,mapping,reads,pins=fixture();check['producer']='MODEL_PROPOSAL'
        with self.assertRaisesRegex(ValueError,'CHECK_REQUIRED'):resolver('check')
        resolver,check,mapping,reads,pins=fixture();mapping['inventory']['entries']=[];reseal(check,mapping,reads,pins)
        with self.assertRaisesRegex(ValueError,'conservation'):resolver('check')
        resolver,check,mapping,reads,pins=fixture();mapping['visual_address']['target_id']='wrong-cell';reseal(check,mapping,reads,pins)
        with self.assertRaisesRegex(ValueError,'VISUAL_ADDRESS'):resolver('check')

    def test_partial_attestation_and_saved_defaults_are_visible(self):
        resolver,check,mapping,reads,pins=fixture()
        mapping['inventory']['entries'][0].update(assumption='SAVED_DEFAULT',volatility='VIEWER_CHANGEABLE');reseal(check,mapping,reads,pins)
        reads['s']['attestation'].update(reported={'identity':'reader'},reportable=['identity'])
        proof=resolver('check');self.assertIn('partial',proof['qualification']);self.assertIn('Saved slicer defaults',proof['qualification'])

    def test_difference_requires_cross_side_numeric_recomputation(self):
        resolver,check,mapping,reads,pins=fixture();reads['s']['value']['typed_value']['value']='45'
        with self.assertRaisesRegex(ValueError,'UNEXPLAINED'):resolver('check')
        mapping['mapping'].update(explanation_statement='SELECT SUM(mapped_units) FROM lower_rows',explanation_definition_hash='a'*64,
            explanation_endpoint_side='target',explanation_value_side='source')
        check['explanation_read']='x';reads['x']=copy.deepcopy(reads['t']);reads['x'].update(id='x',statement=mapping['mapping']['explanation_statement'])
        reads['x']['statement_hash']=hashlib.sha256(reads['x']['statement'].encode()).hexdigest();reseal(check,mapping,reads,pins)
        with self.assertRaisesRegex(ValueError,'EXPLANATION_DOES_NOT_REPRODUCE'):resolver('check')
        reads['x']['value']['typed_value']['value']='45';proof=resolver('check')
        self.assertTrue(proof['difference_explained']);self.assertFalse(proof['values_equal'])
        self.assertIn('numerically explained',proof['qualification'])
        mapping['mapping']['explanation_value_side']='target';reseal(check,mapping,reads,pins)
        with self.assertRaisesRegex(ValueError,'CANNOT_COMPARE_ITSELF'):resolver('check')

    def test_coverage_renders_value_grade_separately_from_full_verified(self):
        from graph_coverage_report import coverage,markdown
        from test_graph_coverage_report import node,edge
        value=edge('edge','visual','source','VALUE_VERIFIED');value['verification']={'state':'CURRENT','evidence_ids':['proof'],'scope_hash':'scope'}
        g={'nodes':[node('visual','VISUAL'),node('source','COLUMN',native_kind='SqlColumn',system_of_record=True)],'edges':[value]}
        result=coverage(g,g);totals=result['baseline_cohort']
        self.assertEqual(0,totals['complete_verified_paths']);self.assertEqual(1,totals['complete_value_verified_paths'])
        result['dependency_observations']=[]
        text=markdown({'at':T0,'estates':{'synthetic':result}})
        self.assertIn('Complete VALUE_VERIFIED',text)

    def test_partial_path_is_never_complete_value_verified(self):
        from investigator.graph_value_verification import value_path
        resolver,check,mapping,reads,pins=fixture()
        edges=[e for e in graph()['edges']if e['id']in ('vm','mc')]
        result=value_path(resolver,['check'],edges=edges,start='visual',terminal='column')
        self.assertEqual('PARTIAL',result['status']);self.assertFalse(result['complete'])
        self.assertEqual(['mc'],result['missing_edges']);self.assertEqual(['measure','visual'],result['reached'])
        complete=value_path(resolver,['check'],edges=edges[:1],start='visual',terminal='measure')
        self.assertEqual('VALUE_VERIFIED',complete['status']);self.assertTrue(complete['complete'])
        with self.assertRaisesRegex(ValueError,'DISCONNECTED'):
            value_path(resolver,['check'],edges=edges,start='unrelated',terminal='column')



class ValueGraphHistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.state=SharedState.offline(Path(self.tmp.name)/'state.sqlite');self.resolver,self.check,self.mapping,self.reads,self.pins=fixture()
        self.repo=GraphRepository(self.state,value_verification_resolver=self.resolver);self.repo.migrate();self.repo.replace(graph())

    def test_grade_attaches_and_pin_change_appends_stale_history(self):
        self.repo.value_verify_edges('estate',['check'],observed_at=T1)
        earned=next(e for e in self.repo.records('estate')['edges']if e['id']=='vm')
        self.assertEqual('VALUE_VERIFIED',earned['confidence']);self.assertEqual('DECLARED',earned['base_confidence'])
        self.assertEqual('VALUE_QUERY_VERIFICATION',earned['provenance']['source'])
        from investigator.estate_graph_api import coverage
        summary=coverage(self.repo.records('estate'));self.assertEqual(1,summary['edges_by_confidence']['VALUE_VERIFIED'])
        self.assertEqual('VALUE_VERIFIED',summary['value_verification'][0]['confidence'])
        changed=copy.deepcopy(self.pins);changed['mapping_hash']='f'*64
        T2='2026-10-13T02:00:00Z'
        self.assertEqual(1,self.repo.invalidate_value_proofs('estate',{'vm':changed},observed_at=T2)['changed'])
        stale=next(e for e in self.repo.records('estate')['edges']if e['id']=='vm')
        self.assertEqual('DECLARED',stale['confidence']);self.assertEqual('STALE',stale['verification']['state'])
        historical=next(e for e in self.repo.records('estate',at=T1)['edges']if e['id']=='vm')
        self.assertEqual('VALUE_VERIFIED',historical['confidence']);self.assertEqual(earned['verification'],historical['verification'])

    def test_forged_callback_cannot_attach_value_or_full_grade(self):
        self.repo.value_verification_resolver=lambda _:self.resolver('check')
        with self.assertRaisesRegex(ValueError,'TRUSTED_EDGE'):self.repo.value_verify_edges('estate',['check'],observed_at=T1)
        self.repo.verification_resolver=self.resolver
        with self.assertRaisesRegex(ValueError,'TRUSTED_EDGE'):self.repo.verify_edges('estate',['check'],observed_at=T1)
        edge=graph()['edges'][2];edge.update(confidence='VALUE_VERIFIED',base_confidence='VALUE_VERIFIED',
            provenance={**edge['provenance'],'source':'VALUE_QUERY_VERIFICATION'},verification={'state':'CURRENT','evidence_ids':['check'],'scope_hash':self.mapping['scope_hash']})
        with self.assertRaisesRegex(ValueError,'BASE_CONFIDENCE'):c.record(edge,edge=True)

    def test_definition_change_invalidates_value_proof_and_preserves_old_grade(self):
        self.repo.value_verify_edges('estate',['check'],observed_at=T1)
        changed=graph();changed.update(definition_hash='b'*64,observed_at='2026-10-13T02:00:00Z')
        changed['edges'][2]['provenance']['definition_hash']='b'*64
        self.repo.replace(changed)
        now=next(e for e in self.repo.records('estate')['edges']if e['id']=='vm')
        self.assertEqual('DECLARED',now['confidence']);self.assertEqual('STALE',now['verification']['state'])
        self.assertEqual('VALUE_VERIFIED',next(e for e in self.repo.records('estate',at=T1)['edges']if e['id']=='vm')['confidence'])

    def test_collection_failure_exposes_value_proof_as_stale_without_rewriting_history(self):
        from investigator.graph_scan_health import record
        self.repo.value_verify_edges('estate',['check'],observed_at=T1)
        T2='2026-10-13T02:00:00Z';record(self.state,'estate','owner',T2,'UNAVAILABLE','Reader refused')
        current=next(e for e in self.repo.records('estate')['edges']if e['id']=='vm')
        self.assertEqual('DECLARED',current['confidence']);self.assertEqual('STALE',current['verification']['state'])
        historic=next(e for e in self.repo.records('estate',at=T1)['edges']if e['id']=='vm')
        self.assertEqual('VALUE_VERIFIED',historic['confidence'])



class ConfidenceMigrationTests(unittest.TestCase):
    def test_v3_preserves_old_migration_hashes_current_rows_and_historical_bytes(self):
        from investigator.shared_state import DDL,USAGE_DDL
        with tempfile.TemporaryDirectory() as folder:
            state=SharedState.offline(Path(folder)/'old.sqlite')
            with state.transaction() as db:
                db.execute('CREATE TABLE state_schema_versions(version INTEGER PRIMARY KEY,sha256 TEXT NOT NULL)')
                for version,text in ((1,DDL.format(number='TEXT')),(2,USAGE_DDL)):
                    for statement in text.split(';'):
                        if statement.strip():db.execute(statement)
                    db.execute('INSERT INTO state_schema_versions VALUES(?,?)',(version,hashlib.sha256(text.encode()).hexdigest()))
                from investigator.estate_graph_repository import DDL as history
                for statement in history.split(';'):
                    if statement.strip():db.execute(statement)
                before=json.dumps({'historical':'unchanged bytes','confidence':'VERIFIED'},indent=3)
                db.execute('INSERT INTO estate_graph_history VALUES(?,?,?,?,?,?,?,?)',('estate','edges','historical','owner',T0,None,before,'retained-hash'))
                for key in ('s','t'):db.execute('INSERT INTO estate_graph_nodes VALUES(?,?,?,?,?)',('estate',key,'DECLARED','opaque provenance','opaque original body'))
                db.execute('INSERT INTO estate_graph_edges VALUES(?,?,?,?,?,?,?)',('estate','e','s','t','DECLARED','opaque provenance','opaque edge'))
                oldhashes=db.execute('SELECT * FROM state_schema_versions ORDER BY version').fetchall()
            state.migrate();state.migrate()
            with state.transaction() as db:
                self.assertEqual(oldhashes,db.execute('SELECT * FROM state_schema_versions WHERE version<3 ORDER BY version').fetchall())
                self.assertEqual(before,db.execute('SELECT body FROM estate_graph_history').fetchone()[0])
                self.assertEqual('opaque edge',db.execute('SELECT body FROM estate_graph_edges').fetchone()[0])
                db.execute("UPDATE estate_graph_edges SET confidence='VALUE_VERIFIED'")
                with self.assertRaises(sqlite3.IntegrityError):db.execute("UPDATE estate_graph_edges SET confidence='INVENTED'")
                self.assertEqual([],db.execute('PRAGMA foreign_key_check').fetchall())

    def test_postgres_migration_changes_checks_only(self):
        from investigator.graph_value_migration import sql
        migration=sql('postgresql')
        self.assertEqual(4,len([s for s in migration.split(';')if s.strip()]))
        self.assertNotIn('UPDATE ',migration);self.assertNotIn('DELETE ',migration)
        self.assertIn('estate_graph_nodes_confidence_check',migration);self.assertIn('estate_graph_edges_confidence_check',migration)


if __name__=='__main__':unittest.main()
