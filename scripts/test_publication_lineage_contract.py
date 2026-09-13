import copy
from pathlib import Path
import unittest
from publication_lineage_contract import PARAMETERS,TABLES,resolve
from lineage_graph import build
from lineage_gap_policy import eligibility


class PublicationScopeTests(unittest.TestCase):
    def fixture(self,verify=False):
        values={'WORKSPACE':'11111111-1111-1111-1111-111111111111',
                'BRONZE_ID':'22222222-2222-2222-2222-222222222222',
                'SNAPSHOT_ID':'33333333-3333-3333-3333-333333333333',
                'MANIFEST_SHA256':'a'*64,'VERIFY_ONLY':verify}
        body=(Path(__file__).resolve().parents[1]/'infra/fabric/publish_source_snapshot.py').read_text()
        code='\n'.join(f'{key}={values[key]!r}' for key in PARAMETERS)+'\n'+body
        root=f"abfss://{values['WORKSPACE']}@onelake.dfs.fabric.microsoft.com/{values['BRONZE_ID']}/Tables/snapshot_{values['SNAPSHOT_ID'].replace('-','')}/"
        mappings=[{'source_snapshot_id':values['SNAPSHOT_ID'],'source_manifest_sha256':'a'*64,
                   'destination':root+name,'sql_table':'app.'+name,'bronze_proof_sha256':'b'*64} for name in sorted(TABLES)]
        return code,mappings,values

    def test_publisher_scope_is_exactly_ten_tables(self):
        code,mappings,_=self.fixture()
        contract=resolve(code,mappings)
        self.assertEqual(contract['possible_table_writes'],sorted(m['destination'] for m in mappings))
        self.assertEqual(contract['resolution'],'RESOLVED_BY_REVIEWED_CONTRACT')

    def test_verifier_has_no_table_writes(self):
        code,mappings,_=self.fixture(True)
        contract=resolve(code,mappings)
        self.assertEqual(contract['possible_table_writes'],[])
        self.assertEqual(len(contract['verified_table_dependencies']),10)

    def test_changed_code_or_extra_write_never_accepted(self):
        code,mappings,_=self.fixture()
        for changed in (code+"\nframes['orders'].write.save('another/path')",code.replace("mode('errorifexists')","mode('overwrite')")):
            self.assertIsNone(resolve(changed,mappings))

    def test_missing_duplicate_wrong_path_and_wrong_proof_rejected(self):
        code,mappings,_=self.fixture()
        for failure in ('missing','duplicate','path','hash','proof'):
            rows=copy.deepcopy(mappings)
            if failure=='missing':rows.pop()
            if failure=='duplicate':rows[-1]=rows[0]
            if failure=='path':rows[0]['destination']='elsewhere'
            if failure=='hash':rows[0]['source_manifest_sha256']='c'*64
            if failure=='proof':rows[0]['bronze_proof_sha256']='c'*64
            self.assertIsNone(resolve(code,rows))

    def test_changed_parameters_rejected(self):
        code,mappings,_=self.fixture()
        self.assertIsNone(resolve(code.replace("VERIFY_ONLY=False","VERIFY_ONLY='false'"),mappings))
        self.assertIsNone(resolve(code.replace('11111111-1111-1111-1111-111111111111','44444444-4444-4444-4444-444444444444'),mappings))

    def test_graph_preserves_resolutions_and_blocks_changed_body(self):
        code,mappings,values=self.fixture()
        notebook='nb';parent=f"fabric://{values['WORKSPACE']}/{values['BRONZE_ID']}"
        assets=[dict(id=notebook,parent=None,kind='Notebook',name='publisher',hash='nbhash',meta={}),
                dict(id='part',parent=notebook,kind='DefinitionPart',name='notebook-content.py',hash='definitionhash',meta={'content':code})]
        for row in mappings:
            assets.append(dict(id=row['sql_table'],parent=parent,kind='LakehouseTable',name='snapshot_'+values['SNAPSHOT_ID'].replace('-','')+'.'+row['sql_table'].split('.')[1],hash='tablehash',meta={}))
            row['sql_parent']='source'
            assets.append(dict(id='sql/'+row['sql_table'],parent='source',kind='SqlObject',name=row['sql_table'],hash='sqlhash',meta={}))
        graph=build(assets,{'records':[],'snapshot_mappings':mappings})
        self.assertFalse(graph.gaps)
        self.assertEqual(len(graph.resolved_gaps),5)
        self.assertTrue(eligibility(graph,'app.orders')['lineage_conclusions_allowed'])
        assets[1]['meta']['content']+="\nframes['orders'].write.save('unknown')"
        graph=build(assets,{'records':[],'snapshot_mappings':mappings})
        self.assertFalse(graph.resolved_gaps)
        self.assertFalse(eligibility(graph,'app.orders')['lineage_conclusions_allowed'])


if __name__=='__main__':unittest.main()
