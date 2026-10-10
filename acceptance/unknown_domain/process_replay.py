"""Replay engine decisions from bounded worker/provider bytes; no upstream decoding."""
from contextlib import ExitStack
import json
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from investigator import process_tape as journal
from investigator.onboarding import ModelStore
from investigator.runtime import Runtime,fingerprint
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.adaptive_planner import azure_plan
from investigator.question_intake import azure_resolve
from investigator.workspace import Workspace
from run_native_diagnostic import transport as native
from run_source_diagnostic import transport as source


def replay(path,output,*,allow_engine_drift=False,native_transport=None,source_transport=None):
    tape=journal.Tape(path);bootstrap=tape.bootstrap
    replay_engine_hash=fingerprint()
    if bootstrap['engine_hash']!=replay_engine_hash and not allow_engine_drift:
        raise journal.TapeError('ENGINE_VERSION_MISMATCH')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    for name in ('catalog.sqlite','inventory.sqlite'):
        if journal.sha((Path(path).parent/name).read_bytes())!=bootstrap['state']['artifacts'][name]:
            raise journal.TapeError('TAPE_BOOTSTRAP_ARTIFACT_CHANGED:'+name)
        shutil.copyfile(Path(path).parent/name,output/name)
    config=bootstrap['config'];settings=bootstrap['state']
    store=ModelStore(output/'catalog.sqlite',output/'inventory.sqlite',settings['environment'],
                     context_pins=settings.get('context_pins'))
    if 'fixture_state' in settings:store.acceptance_fixture_state=settings['fixture_state']
    runtime=Runtime(store,config,native_transport or (lambda r:native(config,r)),
                    source_transport or (lambda r:source(config,r)))
    agent=AdaptiveRuntime(runtime,azure_plan,planner_profile=bootstrap['profile'],usage_policy=bootstrap['usage_policy'])
    workspace=Workspace(agent,execution_enabled=True,question_resolver=azure_resolve,
        dynamic_read_limit=settings['dynamic_read_limit'],dynamic_input_limit=settings['dynamic_input_limit'])
    workspace.owner=settings['workspace_owner']
    methods={'intake':workspace.intake.resolve,'preview':workspace.preview,
             'create':agent.create,'run':agent.run,'synthesize':agent.synthesize}
    if tape.version in journal.SMART_VERSIONS:
        from investigator.smart_intake import SmartIntake
        controller=SmartIntake(workspace,settings.get('smart_intake'),settings.get('smart_ownership'),
                               auto_start=settings.get('smart_auto_start',False))
        workspace._smart_intake=controller
        methods.update(ticket_submit=controller.submit,ticket_reply=controller.reply,
            ticket_attach=controller.attach,ticket_share=controller.share,ticket_close=controller.close,
            ticket_respond=controller.respond,ticket_finish=controller.finish)
        def form_method(method):
            def invoke(*args,**kwargs):
                workspace.intake_configuration=settings.get('smart_intake')
                workspace.ownership_configuration=settings.get('smart_ownership')
                return getattr(workspace.forms,method)(*args,**kwargs)
            return invoke
        methods.update(form_submit=form_method('submit'),form_reply=form_method('reply'),
                       form_screenshot_reply=form_method('screenshot_reply'),form_comment=form_method('comment'))
    result=None;error=None;operations=[]
    with ExitStack() as stack:
        if allow_engine_drift:
            # Engine identity is a recorded environmental input, distinct from
            # executing current code. Pin its producers, never returned facts
            # or outputs. Changed decisions/requests still fail byte matching.
            for module in ('runtime','adaptive_runtime','workspace','question_intake','screenshot_intake'):
                stack.enter_context(patch('investigator.'+module+'.fingerprint',return_value=bootstrap['engine_hash']))
        stack.enter_context(journal.active(tape))
        stack.enter_context(patch.dict('os.environ',{'INVESTIGATOR_RECORD_PLANNER':'0',
            'AZURE_OPENAI_ENDPOINT':'https://offline.openai.azure.com',
            'AZURE_OPENAI_DEPLOYMENT':bootstrap['profile'].get('deployment','offline'),
            'AZURE_OPENAI_API_KEY':'offline-placeholder-credential'}))
        stack.enter_context(patch('socket.create_connection',side_effect=journal.TapeError('NETWORK_FORBIDDEN')))
        stack.enter_context(patch('socket.socket.connect',side_effect=journal.TapeError('NETWORK_FORBIDDEN')))
        while tape.events[tape.index]['kind']!='FINAL':
            operation=json.loads(tape.take('OPERATION_START'));name=operation['name']
            journal.event('CONFIGURATION',{'config':agent.config,'profile':agent.planner_profile,
                'usage_policy':agent.governor.policy if agent.governor else None})
            error=None;result=None
            try:result=methods[name](*operation['args'],**operation['kwargs'])
            except Exception as exc:
                if isinstance(exc,journal.TapeError):raise
                error=type(exc).__name__
            journal.event('OPERATION_END',{'name':name,'error':error})
            if name=='synthesize' and error is None and config.get('_estate',{}).get('trace_footer'):
                from investigator.run_recording import attach_trace_footer
                try:attach_trace_footer(agent,operation['args'][0],tape,result)
                except journal.TapeError:raise
                except Exception as exc:error=type(exc).__name__
            operations.append(name)
        final={'operation':name,'error':error,'outputs':((result or {}).get('synthesis') or {}).get('outputs') or (result or {}).get('refusal_outputs'),
               'status':(result or {}).get('status'),'result':result}
        # Preserve the recomputed return even on mismatch. It is diagnostic
        # evidence, never substituted for the sealed final or a passing replay.
        (output/'recomputed-final.json').write_bytes(journal.bytes_of(final))
        tape.finish(final)
    summary={'matched':True,'operations':operations,'outputs':final['outputs'],
             'outcome':((result or {}).get('assessment') or (result or {}).get('outcome') or {}).get('classification'),
             'session':result,
             'status':final['status'],'synthesis_status':((result or {}).get('synthesis') or {}).get('status'),
             'recorded_engine_hash':bootstrap['engine_hash'],'replay_engine_hash':replay_engine_hash,
             'recorded_engine_identity_used':allow_engine_drift,'network_requests':0,
             'claim':'Engine decisions and outputs replayed from bounded worker/provider bytes; upstream decoding not exercised.'}
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary
