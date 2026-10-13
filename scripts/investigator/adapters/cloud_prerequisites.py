"""Adapter-owned platform prerequisite checks."""
def observe_platform(manifest, platform, principal, observe):
    microsoft=any(row['implementation']=='microsoft'for row in manifest['adapters'])
    if microsoft:
        scanner=platform.get('scanner_principal','UNCONFIGURED')
        for key,label in [('read_only_admin','Service principals can access read-only admin APIs'),
                          ('detailed_metadata','Enhance admin APIs responses with detailed metadata'),
                          ('dax_mashup','Enhance admin APIs responses with DAX and mashup expressions')]:
            observe('tenant.'+key,scanner,label+' has not been established for the scanner.',
                    'A Fabric administrator enables the setting for the scanner security group, then retain a successful scanner response with the corresponding metadata. If the setting cannot be read, report MISSING.')
        observe('semantic.execute_queries',principal,'Read + Build and Dataset Execute Queries REST API have not been established for the worker.',
                'Grant model Read + Build only where approved, enable Dataset Execute Queries REST API, and test through the reader. Service-principal RLS/SSO restrictions may prevent this route.')
        observe('semantic.xmla_read',principal,'XMLA connectivity/read capability has not been established.',
                'If using XMLA, confirm supported capacity, endpoint read access and model Read + Build; never enable write or request admin for diagnostics.',required=False)
        observe('monitoring.history',principal,'Workspace monitoring history availability is not established.',
                'Monitoring is optional. Have an owner enable it if wanted, then query retained run history as the existing reader. Empty rows prove no timing/accounting data, not successful ingestion.',required=False)
        observe('rls.impersonation',principal,'Impersonation is not configured or approved in this round.',
                'Use a separately approved, model-scoped impersonation reader only when the client opts in. Otherwise name the RLS limitation.',required=False)
