import copy,json,tempfile,unittest
from pathlib import Path
from investigator.code_sources import validate_source,normalize,read
from investigator.estate_manifest import validate
from investigator.adapters.estate_installation import configuration
from investigator import process_tape as journal

ROOT=Path(__file__).resolve().parents[1]

class CodeSourceTests(unittest.TestCase):
    def manifest(self,kind='PLATFORM_ITEM_API'):
        m=json.loads((ROOT/'infra/estates/fixture.json').read_text())
        source={'id':'code','kind':kind,'identity':'code-account'}
        if kind=='PLATFORM_ITEM_API':source.update(workspace='11111111-1111-1111-1111-111111111111',item_ids=['22222222-2222-2222-2222-222222222222'])
        elif kind=='LOCAL_PATH':source.update(path='fixture/code')
        else:source.update(repo_url='https://example.test/project/repo',ref='fixture-code',path_prefix='code',token_reference='secret/code')
        m['lineage'].setdefault('code_sources',[]).append(source)
        m['identities'].append({'id':'code-account','principal':'code-only','credential_reference':'secret/code',
            'scopes':[{'resource':'code','rights':['READ']}]})
        m['accepted_limits'].append({'code':'CODE_READ_REQUIRES_WRITE_SCOPE','resource':'code',
            'statement':'reading processing instructions uses a separate account with edit access.'})
        return m

    def test_api_requires_accepted_limit_and_separate_identity(self):
        m=self.manifest();validate(m)
        without=copy.deepcopy(m);without['accepted_limits']=without['accepted_limits'][:-1]
        with self.assertRaisesRegex(ValueError,'CODE_READ_REQUIRES_WRITE_SCOPE'):validate(without)
        same=copy.deepcopy(m);reader=same['layers'][0]['reach']['reader'];same['lineage']['code_sources'][-1]['identity']=reader
        next(i for i in same['identities'] if i['id']==reader)['scopes'].append({'resource':'code','rights':['READ']})
        with self.assertRaisesRegex(ValueError,'must not use an investigation reader'):validate(same)

    def test_unknown_fields_and_kinds_refuse(self):
        for kind in ('LOCAL_PATH','GIT_REPOSITORY','PLATFORM_ITEM_API'):
            source=self.manifest(kind)['lineage']['code_sources'][-1]
            validate_source(source)
            source['password']='must-never-be-inline'
            with self.assertRaisesRegex(ValueError,'code_source'):validate_source(source)
        with self.assertRaises(ValueError):validate_source({'id':'x','kind':'UNKNOWN','identity':'x'})

    def test_git_inline_credentials_and_wrong_token_reference_refuse(self):
        m=self.manifest('GIT_REPOSITORY');m['lineage']['code_sources'][-1]['repo_url']='https://user:password@example.test/repo'
        with self.assertRaisesRegex(ValueError,'repo_url'):validate(m)
        m=self.manifest('GIT_REPOSITORY');m['lineage']['code_sources'][-1]['token_reference']='another-account'
        with self.assertRaisesRegex(ValueError,'token_reference'):validate(m)

    def test_code_credentials_stay_out_and_authorizations_reach_only_the_engine(self):
        m=validate(self.manifest());c=configuration(m)
        serialized=json.dumps(c)
        self.assertNotIn('secret/code',serialized)
        self.assertNotIn('code-only',serialized)
        self.assertNotIn('code_sources',serialized)
        self.assertEqual(c['_estate']['lineage']['code_locations'],m['lineage']['code_locations'])
        from metadata_config import worker_configuration
        layer=next(x for x in m['layers'] if x['role']=='SEMANTIC')
        workspace,model=layer['asset_id'].removeprefix('fabric://').split('/')[:2]
        worker=worker_configuration(c,{'workspace':workspace,'native_model_id':model})
        projected=json.dumps(worker)
        for forbidden in ('code_locations','code_sources','secret/code','code-only','_estate'):
            self.assertNotIn(forbidden,projected)

    def test_notebook_layouts_share_one_representation(self):
        code='x = 1\n'
        plain=normalize('unit.py',code.encode())
        sql=normalize('unit.sql',b'SELECT x FROM input')
        native=normalize('notebook-content.py',b'# CELL ********************\nx = 1\n',item_identity='logical-object')
        repo=normalize('unit.py',b'# Databricks notebook source\n# COMMAND ----------\nx = 1\n')
        ipynb=normalize('unit.ipynb',json.dumps({'nbformat':4,'metadata':{'language_info':{'name':'python'}},'cells':[
            {'cell_type':'markdown','source':['notes']},{'cell_type':'code','source':[code]}]}).encode())
        for unit in (plain,sql,native,repo,ipynb):
            self.assertEqual(set(unit),{'path','item_identity','content_hash','cells'})
            self.assertTrue(unit['cells'])
            for cell in unit['cells']:self.assertEqual(set(cell),{'id','language','source','line_start','line_end'})
        self.assertEqual(native['item_identity'],'logical-object')
        self.assertEqual(native['cells'][-1]['line_start'],2)
        self.assertEqual(repo['cells'][-1]['source'],plain['cells'][0]['source'])
        self.assertEqual(ipynb['cells'][0]['source'],code)

    def test_read_count_and_receipt_and_path_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'unit.py').write_text('x=1\n')
            source={'id':'code','kind':'LOCAL_PATH','identity':'code-reader','path':d}
            calls=[]
            def meter(call):calls.append(1);return call()
            unit,receipt=read(source,'unit.py',meter=meter)
            self.assertEqual(len(calls),1);self.assertEqual(receipt['content_hash'],unit['content_hash'])
            self.assertEqual(receipt['kind'],'LOCAL_PATH');self.assertTrue(receipt['retrieved_at'])
            for path in ('../unit.py','/unit.py','C:/unit.py','dir\\unit.py'):
                with self.assertRaises(ValueError):read(source,path,meter=meter)
            self.assertEqual(len(calls),1)

    def test_export_platform_sidecar_is_read_and_not_guessed_from_filename(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'notebook-content.py').write_text('x=1\n')
            (root/'.platform').write_text('{"config":{"logicalId":"declared-logical-id"}}')
            calls=[]
            unit,receipt=read({'id':'code','kind':'LOCAL_PATH','identity':'account','path':d},'notebook-content.py',
                meter=lambda fn:(calls.append(1),fn())[1])
            self.assertEqual(len(calls),2)
            self.assertEqual(unit['item_identity'],{'logical_id':'declared-logical-id'})
            self.assertEqual(receipt['item_identity'],unit['item_identity'])

    def test_local_code_read_tape_replays_without_io(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);file=root/'unit.py';file.write_text('x=1\n')
            source={'id':'code','kind':'LOCAL_PATH','identity':'account','path':d}
            bootstrap={'entry_point':'synthetic','context_identity':'offline','config':{},'profile':{},'usage_policy':None,'engine_hash':'offline','state':{}}
            tape=journal.Tape(root/'tape.json',bootstrap=bootstrap)
            with journal.active(tape):
                original=read(source,'unit.py',meter=lambda call:call())
                tape.finish({'read':original})
            file.unlink()
            replay=journal.Tape(root/'tape.json')
            with journal.active(replay):
                actual=read(source,'unit.py',meter=lambda call:call())
                replay.finish({'read':actual})
            self.assertEqual(original,actual)

    def test_export_replays_after_both_code_and_metadata_are_removed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);file=root/'notebook-content.py';file.write_text('x=1\n')
            metadata=root/'.platform';metadata.write_text('{"config":{"logicalId":"kept"}}')
            source={'id':'code','kind':'LOCAL_PATH','identity':'account','path':d}
            bootstrap={'entry_point':'synthetic','context_identity':'offline','config':{},'profile':{},'usage_policy':None,'engine_hash':'offline','state':{}}
            tape=journal.Tape(root/'tape.json',bootstrap=bootstrap)
            with journal.active(tape):
                original=read(source,file.name,meter=lambda call:call());tape.finish({'read':original})
            file.unlink();metadata.unlink()
            replay=journal.Tape(root/'tape.json')
            with journal.active(replay):
                actual=read(source,file.name,meter=lambda call:call());replay.finish({'read':actual})
            self.assertEqual(original,actual)

if __name__=='__main__':unittest.main()
