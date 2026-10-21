"""Safe control-plane command failures, retaining exact non-secret output."""
import base64
import hashlib
import subprocess
from ..planner_recording import _safe
from ..process_tape import bytes_of


class ControlCommandFailure(RuntimeError):
    def __init__(self,receipt):
        self.receipt=receipt
        super().__init__('AZURE_CONTROL_COMMAND_FAILED:'+receipt['operation']+':'+str(receipt['returncode']))


def _output(value,name):
    if value is None:return {name:None,name+'_redacted':False}
    raw=value if isinstance(value,bytes)else value.encode('utf8')
    try:_safe(raw)
    except Exception:return {name:'REDACTED_SECRET_CONTENT',name+'_redacted':True}
    if isinstance(value,bytes):return {name:raw.decode('utf8',errors='replace'),name+'_base64':base64.b64encode(raw).decode(),name+'_redacted':False}
    return {name:value,name+'_redacted':False}


def execute_checked(execute,argv,*,operation,**kwargs):
    try:return execute(argv,**kwargs)
    except subprocess.CalledProcessError as error:
        receipt={'kind':'AZURE_CONTROL_FAILURE','operation':operation,'returncode':error.returncode,
                 'error_type':type(error).__name__,'command_sha256':hashlib.sha256(bytes_of([str(x)for x in argv])).hexdigest(),
                 **_output(error.stdout,'stdout'),**_output(error.stderr,'stderr')}
        _safe(bytes_of(receipt))
        # Never allow the original exception chain to print an unchecked body.
        raise ControlCommandFailure(receipt)from None
