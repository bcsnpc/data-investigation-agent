"""Record internal failures without serializing exception locals or runtime data."""
import ast
from pathlib import Path
import traceback
import sqlite3
import re

SQLITE_PHASES=frozenset(('UNSPECIFIED','PROCESS_STAGE_ADMISSION','PROCESS_READ_RECEIPT_PERSISTENCE','FLEXIBLE_READ_RECEIPT_PERSISTENCE'))


def validate(detail):
    if (not isinstance(detail,dict) or set(detail)-{'sqlite'} not in ({'error_type','message','message_redacted','module','line'}, {'error_type','message','message_redacted','module','line','errno'})
            or any(not isinstance(detail[k],str) or not detail[k] for k in ('error_type','message','module'))
            or type(detail['message_redacted']) is not bool
            or (detail.get('errno') is not None and type(detail['errno']) is not int)
            or (detail['line'] is not None and (type(detail['line']) is not int or detail['line']<1))):
        raise ValueError('Process failure requires exception type, safe message and failing location')
    if 'sqlite' in detail:
        value=detail['sqlite']
        if (not isinstance(value,dict) or set(value)!={'code','name','phase'}
                or value['phase'] not in SQLITE_PHASES
                or (value['code'] is not None and (type(value['code']) is not int or not 0<=value['code']<=2147483647))
                or (value['name'] is not None and (not isinstance(value['name'],str) or not re.fullmatch(r'SQLITE_[A-Z0-9_]{1,48}',value['name'])))):
            raise ValueError('Invalid safe SQLite failure diagnostic')
    return detail


def capture(exc):
    if hasattr(exc,'recorded_failure'):return validate(exc.recorded_failure)
    frames=traceback.extract_tb(exc.__traceback__)
    frame=frames[-1] if frames else None
    message=str(exc)
    # Only source-authored literal exception messages are safe to retain. Dynamic
    # exception messages may contain values, query text or provider responses.
    literals=set()
    if frame:
        try:
            tree=ast.parse(Path(frame.filename).read_text(encoding='utf-8-sig'))
            for node in ast.walk(tree):
                if isinstance(node,ast.Raise) and isinstance(node.exc,ast.Call):
                    literals.update(a.value for a in node.exc.args if isinstance(a,ast.Constant) and isinstance(a.value,str))
        except (OSError,SyntaxError):pass
    # OS diagnostics are the evidence needed to distinguish pipe, file and
    # socket failures. Do not serialize filename/filename2 (which can be secret
    # paths); retain the OS reason and errno, rather than exception locals.
    os_message=exc.strerror if isinstance(exc,OSError) else None
    safe=os_message or (message if message in literals else 'Exception message withheld because it may contain runtime data.')
    result={'error_type':type(exc).__name__,'message':safe,
            'message_redacted':not bool(os_message) and message not in literals,
            'module':Path(frame.filename).name if frame else 'unknown',
            'line':frame.lineno if frame else None,
            'errno':exc.errno if isinstance(exc,OSError) else None}

    if isinstance(exc,sqlite3.Error):
        code=getattr(exc,'sqlite_errorcode',None);name=getattr(exc,'sqlite_errorname',None)
        if type(code) is not int or not 0<=code<=2147483647:code=None
        if not isinstance(name,str) or not re.fullmatch(r'SQLITE_[A-Z0-9_]{1,48}',name):name=None
        phase=getattr(exc,'sqlite_phase','UNSPECIFIED')
        if phase not in SQLITE_PHASES:phase='UNSPECIFIED'
        result['sqlite']={'code':code,'name':name,'phase':phase}
    return validate(result)
