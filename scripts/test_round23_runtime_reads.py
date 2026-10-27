import hashlib
import json
import unittest
from unittest.mock import Mock
from investigator.guided_runtime_reads import SubjectHistory


class Tests(unittest.TestCase):
    def test_ticket_triage_selects_only_path_history_subjects_not_profiles_or_scan(self):
        from unittest.mock import patch
        reader=SubjectHistory(subjects={'job':{'kind':'JOB'},'model':{'kind':'MODEL'},'table':{'kind':'TABLE'},'other':{'kind':'JOB'}},allowed=['job','model','table','other'],http=Mock(),retain=Mock(),now=lambda:'2026-10-27T00:02:00Z',estate='fixture')
        with patch.object(SubjectHistory,'__call__',return_value={'status':'OBSERVED'})as read:
            result=reader.top_up('fixture',['model','job','table'],now='2026-10-27T00:02:00Z')
        self.assertEqual([c.args[0]for c in read.call_args_list],['job','model'])
        self.assertEqual(result['purpose'],'INVESTIGATION');self.assertEqual(result['unavailable_subjects'],['table'])
        with self.assertRaises(PermissionError):reader.top_up('fixture',['unadmitted'],now='2026-10-27T00:02:00Z')

    def test_one_explicit_subject_uses_supplied_investigation_meter_not_collector(self):
        node='job';calls=[]
        def http(path,**kw):
            calls.append(path)
            return {'status_code':200,'text':{'value':[{'id':'native-run','status':'Failed','startTimeUtc':'2026-10-27T00:00:00Z','endTimeUtc':'2026-10-27T00:01:00Z','failureReason':'copy failed'}]}}
        retain=lambda b:{'sha256':hashlib.sha256(b).hexdigest()}
        reader=SubjectHistory(subjects={node:{'kind':'JOB','workspace':'11111111-1111-1111-1111-111111111111','item':'22222222-2222-2222-2222-222222222222'}},allowed=[node],http=http,retain=retain,now=lambda:'2026-10-27T00:02:00Z')
        result=reader(node,{'JOB_RUN','RUN_HISTORY'})
        self.assertEqual(result['purpose'],'INVESTIGATION');self.assertEqual(len(calls),1)
        self.assertEqual(next(f for f in result['facts'] if f['kind']=='JOB_RUN')['value']['error'],'copy failed')
        with self.assertRaises(PermissionError):reader('unadmitted',{'JOB_RUN'})
        self.assertEqual(len(calls),1)


if __name__=='__main__':unittest.main()
