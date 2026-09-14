"""Local operator launcher: capture the Azure key in memory, never print or save it."""
import argparse
import json
import os
import subprocess
from pathlib import Path

from metadata_config import ROOT, load_config
from lineage_graph import load_graph
from ticket_planner import plan_ticket
from ticket_workflow import TicketStore
from evaluate_ticket_planner import evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--ticket-id')
    mode.add_argument('--evaluate', action='store_true')
    parser.add_argument('--config',type=Path,default=ROOT / 'infra/metadata/development.json')
    args = parser.parse_args()
    settings = json.loads((ROOT / 'infra/llm/development.json').read_text())
    config = load_config(args.config)
    variables = ('AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_DEPLOYMENT')
    previous = {k: os.environ.get(k) for k in variables}
    try:
        result = subprocess.run([str(ROOT / '.local/azure-cli-env/Scripts/python.exe'), '-m', 'azure.cli',
                                 'cognitiveservices', 'account', 'keys', 'list',
                                 '--subscription', settings['subscription_id'],
                                 '--resource-group', settings['resource_group'], '--name', settings['account'],
                                 '-o', 'json'], capture_output=True, text=True, timeout=60, check=True)
        os.environ.update(AZURE_OPENAI_API_KEY=json.loads(result.stdout)['key1'],
                          AZURE_OPENAI_ENDPOINT=settings['endpoint'],
                          AZURE_OPENAI_DEPLOYMENT=settings['deployment'])
        if args.evaluate:
            estate = json.loads((ROOT / 'infra/fabric/environment.json').read_text())
            return 0 if evaluate(config, estate['investigation']['lineage_run'], ROOT / '.local/llm-evaluation.json') else 1
        store = TicketStore(Path(config['storage']['database']).with_name('workflow.sqlite'))
        ticket = store.get(args.ticket_id)
        if ticket is None:
            raise ValueError('Unknown ticket')
        graph = load_graph(config['storage']['database'], ticket['lineage_run'])
        record = plan_ticket(store, args.ticket_id, graph)
        print(json.dumps(record))
        return 1 if record['status'] == 'PLANNING_FAILED' else 0
    except Exception as exc:
        print(json.dumps({'status': 'LAUNCH_FAILED', 'error_type': type(exc).__name__}))
        return 1
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == '__main__':
    raise SystemExit(main())
