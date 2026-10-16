"""Raw-definition deduplication through the existing immutable Files store."""
import hashlib
from pathlib import Path
import tempfile
from urllib.parse import urlsplit


class DefinitionSink:
    """No storage backend is inferred; callers supply the approved Files adapter."""
    def __init__(self,files,uri_prefix,*,recording_class,scratch=None):
        if recording_class!='EXACT':raise ValueError('GRAPH_PROJECTED_DEFINITION_CAPTURE_NOT_IMPLEMENTED')
        parsed=urlsplit(uri_prefix)
        if not parsed.scheme or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('GRAPH_DEFINITION_STORE_URI')
        self.files,self.uri_prefix,self.scratch=files,uri_prefix.rstrip('/'),scratch
        self.references={}

    def __call__(self,raw):
        if not isinstance(raw,bytes) or len(raw)>16*1024*1024:raise ValueError('GRAPH_DEFINITION_BYTE_BOUND')
        identity=hashlib.sha256(raw).hexdigest()
        if identity not in self.references:
            with tempfile.TemporaryDirectory(prefix='graph-definition-',dir=self.scratch) as folder:
                path=Path(folder)/'definition';path.write_bytes(raw)
                reference=self.files.capture(path)
                if reference!={'sha256':identity,'bytes':len(raw)}:raise ValueError('GRAPH_DEFINITION_CAPTURE_DIFFERS')
                self.files.verify(identity)
            self.references[identity]={**reference,'uri':self.uri_prefix+'/files/'+identity}
        return dict(self.references[identity])


    def read(self,reference):
        """Resolve only an exact manifest reference in the configured Files store."""
        if (not isinstance(reference,dict) or set(reference)!={'sha256','bytes','uri'}
                or reference['uri']!=self.uri_prefix+'/files/'+reference['sha256']
                or type(reference['bytes'])is not int or not 0<=reference['bytes']<=16*1024*1024):
            raise ValueError('GRAPH_DEFINITION_REFERENCE_DIFFERS')
        detail=self.files.describe(reference['sha256'])
        if detail['bytes']!=reference['bytes']:raise ValueError('GRAPH_DEFINITION_CAPTURE_DIFFERS')
        with tempfile.TemporaryDirectory(prefix='graph-definition-read-',dir=self.scratch) as folder:
            path=Path(folder)/'definition'
            self.files.restore(reference['sha256'],path)
            raw=path.read_bytes()
        if len(raw)!=reference['bytes'] or hashlib.sha256(raw).hexdigest()!=reference['sha256']:
            raise ValueError('GRAPH_DEFINITION_CAPTURE_DIFFERS')
        return raw
