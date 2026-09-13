"""Reviewed finite write-scope contract; never executes captured notebook code."""
import ast
import hashlib
import re
from uuid import UUID

PARAMETERS=('WORKSPACE','BRONZE_ID','SNAPSHOT_ID','MANIFEST_SHA256','VERIFY_ONLY')
TABLES={'customers','products','orders','order_lines','payments','shipments','shipment_lines','refunds','refund_lines','audit_log'}
REVIEWED_BODIES={
    '07837619f52540e043bf241b2d8efddbf7cd29eb387097ffc93f89f91544984f',
    # Initial publisher differs only by omission of the receipt's informational mode field.
    'da510612a8f0634be6aecb1bc6918cf632ca9e61e3ce79bb1cf0717578b98df0',
}


def extract(code):
    tree=ast.parse(code)
    parameters={}
    body=list(tree.body)
    for name in PARAMETERS:
        if not body:return None
        node=body.pop(0)
        if not isinstance(node,ast.Assign) or len(node.targets)!=1 or not isinstance(node.targets[0],ast.Name) or node.targets[0].id!=name:
            return None
        try:parameters[name]=ast.literal_eval(node.value)
        except (ValueError,TypeError):return None
    digest=hashlib.sha256(ast.dump(ast.Module(body=body,type_ignores=[]),include_attributes=False).encode()).hexdigest()
    return parameters,digest


def resolve(code,mappings):
    parsed=extract(code)
    if not parsed:return None
    parameters,digest=parsed
    if digest not in REVIEWED_BODIES:return None
    try:
        for key in ('WORKSPACE','BRONZE_ID','SNAPSHOT_ID'):
            if str(UUID(parameters[key]))!=parameters[key]:return None
        if type(parameters['VERIFY_ONLY']) is not bool:return None
        if not re.fullmatch('[0-9a-f]{64}',parameters['MANIFEST_SHA256']):return None
    except (ValueError,TypeError,AttributeError):return None
    selected=[m for m in mappings if m.get('source_snapshot_id')==parameters['SNAPSHOT_ID']]
    if len(selected)!=10:return None
    root=f"abfss://{parameters['WORKSPACE']}@onelake.dfs.fabric.microsoft.com/{parameters['BRONZE_ID']}/Tables/snapshot_{parameters['SNAPSHOT_ID'].replace('-','')}/"
    names=set()
    proofs=set()
    for row in selected:
        if row.get('source_manifest_sha256')!=parameters['MANIFEST_SHA256']:return None
        path=row.get('destination','')
        if not path.startswith(root):return None
        name=path[len(root):]
        if name not in TABLES or name in names:return None
        if row.get('sql_table')!='app.'+name:return None
        if not re.fullmatch('[0-9a-f]{64}',row.get('bronze_proof_sha256','')):return None
        proofs.add(row['bronze_proof_sha256']);names.add(name)
    if names!=TABLES or len(proofs)!=1:return None
    return {'contract':'reviewed_snapshot_publication_v1','body_ast_sha256':digest,
            'mode':'VERIFY_ONLY' if parameters['VERIFY_ONLY'] else 'PUBLISH',
            'source_snapshot_id':parameters['SNAPSHOT_ID'],'source_manifest_sha256':parameters['MANIFEST_SHA256'],
            'bronze_proof_sha256':next(iter(proofs)),
            'possible_table_writes':[] if parameters['VERIFY_ONLY'] else sorted(m['destination'] for m in selected),
            'verified_table_dependencies':sorted(m['destination'] for m in selected),
            'resolution':'RESOLVED_BY_REVIEWED_CONTRACT',
            'scope':'Finite table dependency/write scope only; no assertion of which historical branch executed'}
