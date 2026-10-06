"""Configure a pinned producer's lineage service from its sealed estate input.

The tape already pins the entire manifest hash and adapter projection. This
sidecar supplies that input, never a saved answer or guessed source declaration.
No recorder contract or historical producer is rewritten.
"""
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def install(module,tape,manifest_path):
    from investigator.process_tape import TapeError
    config=tape.bootstrap['config'];estate=config.get('_estate',{})
    lineage=estate.get('lineage',{})
    enabled=any(r['may_infer_from_code'] for r in lineage.get('code_locations',[]))
    if not enabled:
        yield
        return
    if manifest_path is None:raise TapeError('MISSING_SEALED_ESTATE_MANIFEST')
    from investigator.estate_manifest import load
    from investigator.onboarding import digest
    from investigator.adapters.estate_installation import configuration
    manifest=load(manifest_path)
    if digest(manifest)!=estate.get('manifest_hash'):
        raise TapeError('SEALED_ESTATE_MANIFEST_HASH_DIFFERS')
    # The archived producer lives in a temporary directory. Its path resolver
    # must use the recorded installation root, not that archive directory.
    # Derive it only from a sealed path and its manifest-relative
    # suffix, then require the entire configuration projection to match.
    import metadata_config
    relative=Path(manifest['adapters'][0]['options']['fabric']['auth']['python'])
    absolute=Path(config['fabric']['auth']['python'])
    if relative.is_absolute() or not absolute.is_absolute() or tuple(absolute.parts[-len(relative.parts):])!=relative.parts:
        raise TapeError('SEALED_ESTATE_ROOT_NOT_ESTABLISHED')
    root=absolute
    for _ in relative.parts:root=root.parent
    original_root=metadata_config.ROOT
    try:
        metadata_config.ROOT=root
        projected=configuration(manifest)
    finally:metadata_config.ROOT=original_root
    if projected!=config:raise TapeError('SEALED_ESTATE_CONFIGURATION_DIFFERS')
    from investigator.adapters.code_lineage import Installation
    # Reads of the approval, ledger and source are replayed at their existing
    # bounded calls. Neither these paths nor credentials are opened by install.
    service=Installation(manifest,Path(manifest_path),root)
    original=module.AdaptiveRuntime
    def factory(*args,**kwargs):
        if 'process_lineage' in kwargs:raise TapeError('DUPLICATE_REPLAY_LINEAGE_INSTALLATION')
        return original(*args,process_lineage=service,**kwargs)
    module.AdaptiveRuntime=factory
    try:yield
    finally:module.AdaptiveRuntime=original
