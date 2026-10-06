"""Installed adapter's legacy workspace and reader configuration decoding."""


def scope(config):
    options=config.get('fabric',{})
    return options.get('workspace_id'),options.get('native_reader')


def required_workspace(config):
    return config['fabric']['workspace_id']


def workspace_root(workspace):
    return 'fabric://'+workspace
