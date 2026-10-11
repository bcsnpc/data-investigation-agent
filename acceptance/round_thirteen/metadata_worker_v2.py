"""Private V2 proposal: replay owned nested SQL worker, not skip its events.
The original bounded file-result bytes remain a separate recorded boundary.
"""
import json
from pathlib import Path
from investigator import process_tape as journal
from investigator.physical_reads import run as physical_run

def owned_bounded(name,request,producer):
 tape=journal.ACTIVE.get()
 if tape is None or not tape.replaying:raise RuntimeError('METADATA_V2_REPLAY_ONLY')
 tape.event('BOUNDED_REQUEST',journal.bytes_of({'name':name,'request':request}))
 result=producer()
 tape.event('BOUNDED_RESPONSE',journal.bytes_of(result));return result

def recorded_file_result():
 tape=journal.ACTIVE.get();body=tape.peek('BOUNDED_RESPONSE')
 if body is None:raise journal.TapeError('METADATA_V2_FILE_RESULT_BOUNDARY_MISSING')
 return json.loads(body)

def worker_command(tape):
 # Read ahead validates a typed witness; physical_reads/tape_worker later consume
 # and compare both events normally. Nothing is consumed or discarded here.
 auth=json.loads(tape.peek('AUTH_STATE') or b'null')
 if not isinstance(auth,dict) or set(auth)!={'name','value'} or auth['name']!='guard_connection' or not isinstance(auth['value'],str):raise journal.TapeError('METADATA_V2_GUARD_WITNESS_MISSING')
 index=tape.index+1
 if index>=len(tape.events) or tape.events[index]['kind']!='WORKER_START':raise journal.TapeError('METADATA_V2_WORKER_START_MISSING')
 start=json.loads(journal.validate_event(tape.events[index],index+1))
 if start.get('mode')!='STREAM' or not isinstance(start.get('command'),list):raise journal.TapeError('METADATA_V2_WORKER_SHAPE')
 return start

def sql_file_catalog(server,database,schema,*,script,credential_file):
 tape=journal.ACTIVE.get();start=worker_command(tape);expected=start['command']
 script=Path(script)
 # The descriptor records only the basename; never invent an absolute witness.
 if script.parts[-3:]!=('infra','scripts','Get-SqlMetadata.ps1') or not script.is_file():raise journal.TapeError('METADATA_V2_ARCHIVED_SCRIPT_MISSING')
 if expected.count('-File')!=1 or expected.index('-File')+1>=len(expected) or expected[expected.index('-File')+1]!='Get-SqlMetadata.ps1':raise journal.TapeError('METADATA_V2_SCRIPT_DESCRIPTOR_DIFFERS')
 if expected.count('-OutputPath')!=1:raise journal.TapeError('METADATA_V2_FILE_OUTPUT_BINDING_MISSING')
 index=expected.index('-OutputPath')+1
 if index>=len(expected) or not isinstance(expected[index],str):raise journal.TapeError('METADATA_V2_FILE_OUTPUT_BINDING_MISSING')
 # Ephemeral output-path spelling is a sealed environmental input. Never open,
 # create, overwrite or remove that original path. Only the captured JSON result
 # boundary stands in for the native unretained output file.
 output=expected[index]
 command=['powershell','-NoProfile','-File',str(script),'-Server',server,'-Database',database,'-VisibilitySchema',schema,'-CredentialPath',credential_file,'-OutputPath',output]
 def forbidden(*a,**k):raise AssertionError('PROCESS_NETWORK_CREDENTIAL_ACCESS_FORBIDDEN')
 completed=physical_run(command,input='{}',capture_output=True,text=True,encoding='utf-8',timeout=240,fallback=forbidden)
 if completed.returncode:raise RuntimeError('SQL metadata connection failed')
 return recorded_file_result()
