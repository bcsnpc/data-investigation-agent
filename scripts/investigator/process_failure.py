"""Record internal failures without serializing exception locals or runtime data."""
import ast
from pathlib import Path
import traceback


def validate(detail):
    if (not isinstance(detail,dict) or set(detail) not in ({'error_type','message','message_redacted','module','line'}, {'error_type','message','message_redacted','module','line','errno'})
            or any(not isinstance(detail[k],str) or not detail[k] for k in ('error_type','message','module'))
            or type(detail['message_redacted']) is not bool
            or (detail.get('errno') is not None and type(detail['errno']) is not int)
            or (detail['line'] is not None and (type(detail['line']) is not int or detail['line']<1))):
        raise ValueError('Process failure requires exception type, safe message and failing location')
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
    return {'error_type':type(exc).__name__,'message':safe,
            'message_redacted':not bool(os_message) and message not in literals,
            'module':Path(frame.filename).name if frame else 'unknown',
            'line':frame.lineno if frame else None,
            'errno':exc.errno if isinstance(exc,OSError) else None}
