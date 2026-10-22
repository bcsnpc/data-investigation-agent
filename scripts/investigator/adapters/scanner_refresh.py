"""Two exact refresh GETs, using the scanner only during collector execution."""
from . import scanner_identity as auth
from .scanner_http import ScannerHttp


class RefreshHttp:
    def __init__(self, declaration, subjects, *, meter):
        self.declaration=auth.validate(declaration)
        self.workspaces=sorted({r['workspace'] for r in subjects.values() if r['kind']=='MODEL'})
        self.paths={f"groups/{r['workspace']}/datasets/{r['item']}/{suffix}"
                    for r in subjects.values() if r['kind']=='MODEL'
                    for suffix in ('refreshes?$top=20','refreshSchedule')}
        self.meter=meter
        self.identity={k:self.declaration[k] for k in ('tenant_id','client_id','principal_id')}

    def __call__(self,path,*,audience):
        if audience!='powerbi' or path not in self.paths:
            raise PermissionError('SCANNER_REFRESH_READ_ONLY')
        with auth.job(self.declaration,self.workspaces,kind='SCAN'):
            return ScannerHttp(auth.Tokens(self.declaration),meter=self.meter)(path,audience=audience)
