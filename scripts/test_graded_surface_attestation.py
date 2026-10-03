"""Hostile producers cannot manufacture independence out of coverage or labels."""
import copy,unittest
from dataclasses import replace
from investigator.process_debugging import Probe,attest,vertical
from investigator import surface_difference as difference,process_outcomes
from investigator.adapters.microsoft_process import semantic_self_report
from investigator import query_dax
from test_process_debugging import Adapter


def quantity(identity,engine='engine',obj='object',connection='connection',**changes):
    surface={'identity':'reader','engine':engine,'connection':connection,'object':obj}
    probe=attest(Probe('OBSERVED',identity,{'id':identity},1,execution_surface=surface,
        surface_report=dict(surface),surface_report_types={
            'engine':'ENGINE_PRODUCT','object':'CATALOG_NAME','connection':'SERVER_NAME'},
        surface_report_binding='VALUE_QUERY'))
    result=dict(probe.evidence,execution_surface=surface,status='COMPLETED');result.update(changes)
    return result


def comparison(a,b):
    return {'id':'comparison','comparison_status':'CROSS_SURFACE_VERIFIED',
        'upper_evidence_id':a['id'],'lower_evidence_id':b['id'],
        'upper_execution_surface':a['execution_surface'],'lower_execution_surface':b['execution_surface'],
        'upper_surface_attestation':a['surface_attestation'],'lower_surface_attestation':b['surface_attestation'],
        'surface_difference':difference.grade(a,b)}


class GradingTests(unittest.TestCase):
    def test_identity_only_or_version_only_difference_never_satisfies_boundary(self):
        for field in ('identity','version'):
            a=quantity('a');b=quantity('b')
            for o,value in ((a,'one'),(b,'two')):
                o['surface_report'][field]=value;o['execution_surface'][field]=value
                from investigator.process_debugging import attest_surface
                o['surface_attestation']=attest_surface(o['execution_surface'],o['surface_report'])
            with self.subTest(field=field):
                self.assertNotIn(difference.grade(a,b)['grade'],difference.BOUNDARY_GRADES)
                with self.assertRaisesRegex(ValueError,'lacks comparable'):
                    difference.validate(comparison(a,b),{'a':a,'b':b})

    def test_ip_against_hostname_and_other_incomparable_field_kinds_refused(self):
        for field in ('engine','object','connection'):
            a=quantity('a');b=quantity('b')
            a['surface_report'][field]='10.0.0.9';b['surface_report'][field]='server.example'
            a['execution_surface'][field]='10.0.0.9';b['execution_surface'][field]='server.example'
            from investigator.process_debugging import attest_surface
            for o in (a,b):o['surface_attestation']=attest_surface(o['execution_surface'],o['surface_report'])
            a['surface_report_types'][field]='IP_ADDRESS';b['surface_report_types'][field]='HOSTNAME'
            c=comparison(a,b)
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'INCOMPARABLE_SELF_REPORT_KINDS'):
                difference.validate(c,{'a':a,'b':b})

    def test_engine_difference_strongest_and_object_difference_weaker(self):
        a=quantity('a',obj='one');b=quantity('b',engine='other',obj='two')
        self.assertEqual(difference.validate(comparison(a,b),{'a':a,'b':b})['grade'],difference.ENGINE_INDEPENDENT)
        b=quantity('b',obj='two')
        self.assertEqual(difference.validate(comparison(a,b),{'a':a,'b':b})['grade'],difference.OBJECT_DISTINCT)
        self.assertIn('shared calculation fault',difference.wording(difference.grade(a,b),True))
        self.assertNotIn('independent',difference.wording(difference.grade(a,b),True))

    def test_connection_only_difference_is_within_layer(self):
        a=quantity('a');b=quantity('b',connection='other-session')
        self.assertEqual(difference.grade(a,b)['grade'],difference.WITHIN_LAYER)
        with self.assertRaisesRegex(ValueError,'NO_INDEPENDENT_LOWER_READ'):
            difference.validate(comparison(a,b),{'a':a,'b':b})

    def test_engine_version_in_engine_slot_is_not_product_independence(self):
        a=quantity('a',engine='1.0');b=quantity('b',engine='2.0')
        for o in (a,b):o['surface_report_types']['engine']='ENGINE_VERSION'
        with self.assertRaisesRegex(ValueError,'INCOMPARABLE_SELF_REPORT_KINDS'):
            difference.validate(comparison(a,b),{'a':a,'b':b})

    def test_metadata_report_cannot_be_substituted_for_quantity_self_report(self):
        a=quantity('a');b=quantity('b',engine='other')
        for changed in ({'surface_report_binding':'SEPARATE_METADATA_QUERY'},
                        {'surface_report_receipt_id':'metadata-probe'},
                        {'surface_report_binding':None}):
            hostile=dict(b,**changed)
            with self.subTest(changed=changed),self.assertRaisesRegex(ValueError,'QUANTITY_BOUND_SELF_REPORT_REQUIRED'):
                difference.validate(comparison(a,hostile),{'a':a,'b':hostile,'metadata-probe':b})

    def test_full_coverage_is_recorded_but_partial_can_establish_difference(self):
        a=quantity('a');b=quantity('b',engine='other')
        from investigator.process_debugging import attest_surface
        for o in (a,b):
            del o['surface_report']['connection']
            o['surface_attestation']=attest_surface(o['execution_surface'],o['surface_report'])
            self.assertEqual(o['surface_attestation']['coverage'],'PARTIAL')
            self.assertEqual(o['surface_attestation']['unattested_fields'],['connection'])
        self.assertEqual(difference.validate(comparison(a,b),{'a':a,'b':b})['grade'],difference.ENGINE_INDEPENDENT)
        full=quantity('full');self.assertEqual(full['surface_attestation']['coverage'],'FULL')

    def test_hostile_marker_cannot_upgrade_original_grade_or_attestation(self):
        a=quantity('a',obj='one');b=quantity('b',obj='two');c=comparison(a,b)
        c['surface_difference']['grade']=difference.ENGINE_INDEPENDENT
        with self.assertRaisesRegex(ValueError,'grade differs'):
            difference.validate(c,{'a':a,'b':b})

        c=comparison(a,b);a['surface_attestation']['attested_fields']=[]
        with self.assertRaisesRegex(ValueError,'Original quantity surface attestation'):
            difference.validate(c,{'a':a,'b':b})

    def test_synthesis_projection_cannot_drop_or_change_a_validated_grade(self):
        from investigator import evidence_synthesis
        from investigator.onboarding import Conflict
        from test_process_debugging import OutcomeContractTests
        assessment,observations=OutcomeContractTests().valid('CONSISTENT_TO_BOUNDARY')
        assessment.update(claim='The compared values agree.',alternatives=['Earlier states remain possible.'],limits=['Snapshot alignment is unknown.'])
        source={'observations':list(observations.values())}
        original=observations['comparison']
        for projected in ({}, {'surface_difference':{'grade':difference.ENGINE_INDEPENDENT}}):
            payload={'evidence':[{'id':original['id'],'result':projected}]}
            with self.subTest(projected=projected),self.assertRaisesRegex(Conflict,'dropped or changed surface difference'):
                evidence_synthesis.validate(copy.deepcopy(assessment),payload,source_state=source)

    def test_vertical_carries_grade_and_partial_omissions_into_both_outputs(self):
        adapter=Adapter(['top','lower'],{'top':1,'lower':1})
        original=adapter.evaluate
        def read(*args):
            p=original(*args);report={k:v for k,v in p.surface_report.items() if k!='connection'}
            return replace(p,surface_report=report)
        adapter.evaluate=read
        r=vertical(adapter,'m',{})
        self.assertEqual(r['classification'],'CONSISTENT_TO_BOUNDARY')
        process_outcomes.validate(r,{o['id']:o for o in r['_observations']})
        for key in ('business_output','technical_output'):
            self.assertEqual(r[key]['surface_difference_grades'][0]['grade'],difference.OBJECT_DISTINCT)
            self.assertTrue(r[key]['unattested_surface_fields'])
            hostile=copy.deepcopy(r);hostile[key]['surface_difference_grades']=[]
            with self.assertRaisesRegex(ValueError,'both outputs'):
                process_outcomes.validate(hostile,{o['id']:o for o in r['_observations']})

    def test_quantity_dax_compiles_same_query_self_report_without_general_info_access(self):
        assets=[{'id':'t','name':'Things','kind':'SemanticTable'},
                {'id':'m','name':'Total','kind':'Measure','parent_id':'t'}]
        query=semantic_self_report('EVALUATE ROW("value",[Total])')
        compiled=query_dax.compile_query(query,assets)
        self.assertIn('INFO.PROPERTIES()',compiled['query'])
        self.assertEqual(compiled['asset_ids'],['m'])
        for bad in ('EVALUATE INFO.PROPERTIES()',query.replace('"ProviderName"','"Password"'),
                    query.replace('[Value]','[Secret]')):
            with self.subTest(query=bad),self.assertRaises(ValueError):query_dax.compile_query(bad,assets)

    def test_grades_render_in_both_narratives_without_reducing_context_coverage(self):
        import json
        from investigator import narrative_form,path_narrative
        from investigator.output_contract import business_text,action
        from test_narrative_form import NarrativeFormTests
        for engines in (True,False):
            payload,source,_=NarrativeFormTests().fixture()
            payload['context_entry_points']=[{'id':str(i),'kind':'SqlObject' if i<11 else 'SemanticTable'} for i in range(28)]
            for e in payload['evidence']:
                c=e.get('result',{})
                if c.get('comparison_status')=='CROSS_SURFACE_VERIFIED':
                    a=quantity('a',obj='one');b=quantity('b',obj='two',engine='other' if engines else 'engine')
                    c['surface_difference']=difference.grade(a,b)
            before=json.dumps(payload,sort_keys=True)
            business=narrative_form.business(business_text('TRANSFORMATION_LOGIC',payload),payload)
            technical=narrative_form.technical('A join can repeat matches.',payload,source,action('TRANSFORMATION_LOGIC'))
            grade=difference.ENGINE_INDEPENDENT if engines else difference.OBJECT_DISTINCT
            self.assertIn(grade,technical)
            self.assertIn(difference.wording({'grade':grade},True),business)
            self.assertNotIn('engine-independent cross-surface comparison',technical if not engines else '')
            self.assertEqual(json.dumps(payload,sort_keys=True),before)
            self.assertEqual(len(payload['context_entry_points']),28)
            self.assertEqual(sum(e['kind']=='SqlObject' for e in payload['context_entry_points']),11)
        for text in ('An independent comparison explained this.', 'Engine independence proves the finding.'):
            with self.assertRaises(ValueError):path_narrative.validate_commentary(text)

    def test_sql_self_report_is_inline_not_borrowed_from_permission_guard(self):
        from pathlib import Path
        script=(Path(__file__).resolve().parents[1]/'infra/scripts/Read-FabricSqlAggregate.ps1').read_text()
        self.assertIn('SELECT q.*, SUSER_SNAME() AS __surface_identity, DB_NAME() AS __surface_object',script)
        self.assertIn('LEFT(@@VERSION, CHARINDEX',script)
        self.assertIn("surface_report_binding='VALUE_QUERY'",script)
        self.assertIn('$surfaceReport = $null',script)
        # All existing guards still execute/admit or record established reuse.
        self.assertIn("Begin-PhysicalRead 'sql_identity'",script)
        self.assertIn("Begin-Guard 'sql_database_permissions'",script)
        self.assertIn("Begin-Guard 'sql_object_permissions' $objectName",script)


if __name__=='__main__':unittest.main()
