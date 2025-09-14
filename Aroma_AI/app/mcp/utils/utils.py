# small helper utilities for MCP package
def ensure_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]
