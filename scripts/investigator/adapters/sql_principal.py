"""Expected SQL surface principal, distinct from a reader display label.

Fabric SUSER_SNAME for an application reports client_id@tenant_id. The
credential validator owns both coordinates; a display name is never an alias
for the observed principal. Existing user-auth surfaces retain their account.
"""

def expected(reader):
    if reader.get('mode') == 'federated_reader':
        from .vault_user_cache import credential
        declaration = credential(reader)
        return declaration['client_id'] + '@' + declaration['tenant_id']
    account = reader.get('account')
    if not isinstance(account, str) or not account.strip():
        raise ValueError('SQL_READER_PRINCIPAL_REQUIRED')
    return account
