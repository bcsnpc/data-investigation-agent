"""Run an approved evidence-led session, inspect history or reconcile an interruption."""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess

from investigator.onboarding import ModelStore
from investigator.runtime import Runtime
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.adaptive_planner import azure_plan
from metadata_config import load_config, ROOT
from run_native_diagnostic import transport as native_transport
from run_source_diagnostic import transport as source_transport


@contextmanager
def local_azure_key(settings_path):
    if settings_path is None:
        yield
        return
    settings=settings_path if isinstance(settings_path,dict) else json.loads(settings_path.read_text(encoding='utf-8-sig'))
    variables=('AZURE_OPENAI_API_KEY','AZURE_OPENAI_ENDPOINT','AZURE_OPENAI_DEPLOYMENT')
    previous={k:os.environ.get(k) for k in variables}
    try:
        result=subprocess.run([str(ROOT/'.local/azure-cli-env/Scripts/python.exe'),'-m','azure.cli',
            'cognitiveservices','account','keys','list','--subscription',settings['subscription_id'],
            '--resource-group',settings['resource_group'],'--name',settings['account'],'-o','json'],
            capture_output=True,text=True,check=True,timeout=60)
        os.environ.update(AZURE_OPENAI_API_KEY=json.loads(result.stdout)['key1'],
                          AZURE_OPENAI_ENDPOINT=settings['endpoint'],AZURE_OPENAI_DEPLOYMENT=settings['deployment'])
        yield
    finally:
        for key,value in previous.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value


def main():
    # Historical flags are not a second installation configuration route.
    # The typed direct diagnostic CLIs remain tools, not investigation runners.
    from run_estate_investigation import main as estate_main
    return estate_main()



if __name__=='__main__':raise SystemExit(main())
