"""Explicit platform credential implementation; no ambient chain."""
def credential_type():
    from azure.identity import ManagedIdentityCredential
    return ManagedIdentityCredential


def trust_roots():
    import certifi
    return certifi.where()

CREDENTIAL_PATH_WORDS = r"secret|secrets|credentials?|tokens?|azure|ssh|env"
FORBIDDEN_HTTP_SEGMENTS = {"permissions", "users", "share", "shares", "roleassignments", "xmla"}
