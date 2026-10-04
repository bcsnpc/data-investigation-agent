import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from investigator.load_audits import declarations
from investigator.adapters.load_audit import classify, read, COLUMNS


class AuditTests(unittest.TestCase):
    def row(self, **changes):
        return dict(run_id='run-a',pipeline_name='producer',status='Succeeded',rows_read='360',rows_written='360',
                    accounting_state='OBSERVED_COPY_OUTPUT',start_time_utc='2026-10-04T02:25:15Z',
                    end_time_utc='2026-10-04T02:26:24Z',high_watermark=None,**changes)

    def test_success_preserves_null_cut_and_own_counts(self):
        r=classify([self.row()],'producer')
        self.assertEqual(r['accounting'],{'rows_read':360,'rows_written':360})
        self.assertIsNone(r['high_watermark'])
        self.assertIn('not established',r['reason'])

    def test_failure_in_progress_missing_counts_never_current(self):
        for fields in ({'status':'Failed'},{'status':'InProgress'},{'rows_read':None},
                       {'rows_written':-1},{'rows_written':True},{'accounting_state':'UNAVAILABLE_COPY_OUTPUT'},
                       {'end_time_utc':'2026-10-04T01:00:00Z'}):
            row=self.row();row.update(fields)
            self.assertEqual(classify([row],'producer')['status'],'UNAVAILABLE')

    def test_ambiguous_same_start_wrong_producer_refused(self):
        r=self.row();other=dict(r,run_id='different')
        self.assertEqual(classify([r,other],'producer')['status'],'UNAVAILABLE')
        self.assertEqual(classify([r],'another')['status'],'UNAVAILABLE')

    def test_declarations_are_identity_only_and_unique(self):
        e={'delivery_asset_id':'delivery','producer_asset_id':'producer','audit_asset_id':'audit'}
        self.assertEqual(declarations([e]),[e])
        for wrong in ([e,e],[dict(e,query='SELECT 1')],[dict(e,audit_asset_id='')],[]):
            with self.assertRaises(ValueError):declarations(wrong)

    def test_declared_absent_audit_does_not_fall_back(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        a=MicrosoftProcessAdapter(None,{'load_audits':[{'delivery_asset_id':'delivery',
            'producer_asset_id':'producer','audit_asset_id':'absent'}]},None,None,None)
        with patch('investigator.context_search.latest',return_value={'assets':[]}),patch('investigator.adapters.job_history.classify') as fallback:
            result=a.job_history({'lower':{'transformation_asset_id':'delivery'}})
        self.assertEqual(result['status'],'UNAVAILABLE');fallback.assert_not_called()

    def test_accounting_needs_discovered_columns_and_query_bound_attestation(self):
        entry={'delivery_asset_id':'fabric://ws/delivery','producer_asset_id':'fabric://ws/producer',
               'audit_asset_id':'fabric://ws/lake/tables/dbo.audit'}
        assets=[{'id':entry['delivery_asset_id'],'kind':'CopyJob'},
                {'id':entry['producer_asset_id'],'kind':'DataPipeline'},
                {'id':entry['audit_asset_id'],'kind':'LakehouseTable','name':'dbo.audit','parent_id':'fabric://ws/lake'}]
        assets += [{'id':'col/'+k,'kind':'LakehouseColumn','parent_id':entry['audit_asset_id'],
                    'name':k,'metadata':{'type':'long' if t=='bigint' else 'string'}} for k,t in COLUMNS.items()]
        a=SimpleNamespace(store=None,config={'fabric':{'sql_reader':{'server':'server','account':'reader'}}},
            read_endpoint=lambda req:{'provisioningStatus':'Success','name':'lake'},execute_lower=lambda *args:None,
            model={'id':'m','revision':1,'context_id':'c'},meter_read=None)
        good={'status':'COMPLETED','id':'receipt','request_hash':'sealed','result':{'completeness':'COMPLETE_RESPONSE',
            'rows':[self.row()],'surface_report':{'identity':'reader','engine':'Microsoft Azure SQL Data Warehouse','object':'lake'}}}
        with patch('investigator.context_search.latest',return_value={'assets':assets}),patch('investigator.flexible_tools.run',return_value=good):
            result=read(a,entry)
            self.assertEqual(result['status'],'CURRENT')
            self.assertEqual(result['evidence']['surface_attestation']['consistency'],'MATCHED')
        bad=copy.deepcopy(good);bad['result']['surface_report']['identity']='publisher'
        with patch('investigator.context_search.latest',return_value={'assets':assets}),patch('investigator.flexible_tools.run',return_value=bad):
            self.assertEqual(read(a,entry)['status'],'UNAVAILABLE')
        with patch('investigator.context_search.latest',return_value={'assets':assets[:-1]}),patch('investigator.flexible_tools.run') as execute:
            self.assertEqual(read(a,entry)['status'],'UNAVAILABLE');execute.assert_not_called()


if __name__=='__main__':unittest.main()
