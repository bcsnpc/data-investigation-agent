'use strict';
const $ = id => document.getElementById(id);
let key = '', models = [], execution = false, preview = null, current = null, predecessor = null;
let generation = 0, timer = null, scopeRevision = 0;
let intakeId = null, intakeParent = null, intakeRequest = null, intakeSaved = null, questionRevision = 0;
const activeStates = ['READY', 'PLANNING', 'EXECUTING'];
const statusNames = {READY:'Queued', PLANNING:'Choosing a check', EXECUTING:'Checking', COMPLETED:'Checks finished', NEEDS_INPUT:'Needs your input', HELD:'Paused', CANCELLED:'Cancelled'};
function node(tag, text, cls) { const e=document.createElement(tag); if(text!==undefined)e.textContent=text; if(cls)e.className=cls; return e; }
function showError(error) { $('error').textContent=error.message || String(error); $('error').hidden=false; }
function clearError() { $('error').hidden=true; }
function stopPolling() { clearTimeout(timer); timer=null; generation++; }
async function api(path, body) {
  const credential=key;
  const response=await fetch('/api/workspace/'+path,{method:body===undefined?'GET':'POST',cache:'no-store',
    headers:{Authorization:'Bearer '+credential,...(body===undefined?{}:{'Content-Type':'application/json'})},body:body===undefined?undefined:JSON.stringify(body)});
  const result=await response.json();
  if(credential!==key)throw new Error('The workspace was signed out.');
  if(!response.ok)throw new Error(result.error || 'The request could not be completed.');
  return result;
}
function guard(fn) { return async event=>{event?.preventDefault();clearError();try{await fn(event);}catch(e){showError(e);}}; }
function options(select, items, empty) {
  select.replaceChildren();if(empty!==undefined){const o=node('option',empty);o.value='';select.append(o);}
  for(const item of items){const o=node('option',item.name);o.value=item.id;select.append(o);}
}
function selectedModel(){return models.find(m=>m.id===$('model').value);}
function selectableColumns(m){return (m?.columns||[]).filter(c=>!c.name.startsWith('_'));}
function columnLabel(c){return c.name.replaceAll('_',' ')+' · '+c.table_name;}
function invalidate(){scopeRevision++;intakeId=null;preview=null;$('preview').hidden=true;}
function modelChanged(){
  invalidate();const m=selectedModel();$('filters').replaceChildren();updateAll();
  options($('metric'),m?.measures || []);
  options($('breakdown'),selectableColumns(m).map(c=>({id:c.column_id,name:columnLabel(c)})),'No breakdown selected');
  $('review').disabled=!m || !m.measures.length;
}
function updateAll(){$('scope-empty').hidden=$('filters').children.length>0;$('scope-empty').textContent=selectedModel()?.dynamic_investigation?'No filters selected. The starting question covers the full model; diagnostic checks remain read-only and budgeted.':'Add at least one filter to keep the investigation bounded.';}
function addFilter(saved){
  const m=selectedModel();if(!m)return;
  if($('filters').children.length>=6)throw new Error('Use at most six filters for this investigation.');
  const row=node('div',undefined,'filter');const column=node('select'),operator=node('select'),value=node('textarea');
  const suffix=crypto.randomUUID();column.id='column-'+suffix;operator.id='operator-'+suffix;value.id='value-'+suffix;
  for(const [label,input] of [['Column',column],['Match',operator],['Values',value]]){const wrapper=node('div');const l=node('label',label);l.htmlFor=input.id;wrapper.append(l,input);row.append(wrapper);}
  options(column,selectableColumns(m).map(c=>({id:c.column_id,name:columnLabel(c)})));
  value.rows=2;value.placeholder='One value per line';value.setAttribute('aria-description','Use one value per line. For a range, enter start and exclusive end on separate lines.');
  const remove=node('button','Remove','quiet');remove.type='button';remove.addEventListener('click',()=>{row.remove();invalidate();updateAll();});row.append(remove);
  function changed(){const c=m.columns.find(x=>x.column_id===column.value);options(operator,(c?.operators || []).map(o=>({id:o,name:o==='range'?'Range':'Matches'})));value.placeholder=c?.data_type==='boolean'?'true or false':c?.data_type==='dateTime'?'YYYY-MM-DD, one per line':'One value per line';invalidate();}
  column.addEventListener('change',changed);if(saved)column.value=saved.column_id;changed();
  if(saved){operator.value=saved.operator || 'in';value.value=saved.values.map(v=>v===null?'[blank]':String(v)).join('\n');}
  row.read=()=>{
    const c=m.columns.find(x=>x.column_id===column.value);if(!c)throw new Error('Select a filter column.');
    const raw=value.value.split('\n').map(v=>v.trim());if(raw.some(v=>!v))throw new Error('Enter one filter value per line. Use [blank] to select blank values.');
    const values=raw.map(v=>{
      if(v==='[blank]')return null;
      if(c.data_type==='int64'){if(!/^-?\d+$/.test(v)||!Number.isSafeInteger(Number(v)))throw new Error('Enter an exact whole number.');return Number(v);}
      if(c.data_type==='boolean'){if(!['true','false'].includes(v))throw new Error('Enter true or false.');return v==='true';}
      return v;
    });return {column_id:column.value,operator:operator.value,values};
  };
  $('filters').append(row);updateAll();invalidate();
}
function scopePills(target,scope,columns){
  target.replaceChildren();
  for(const f of scope.filters){const c=columns[f.column_id];const vals=f.values.map(v=>v===null?'Blank':String(v));
    target.append(node('span',(c?columnLabel(c):'Selected column')+': '+(f.operator==='range'?vals[0]+' to before '+vals[1]:vals.join(', ')),'pill'));}
  if(!scope.filters.length)target.append(node('span','All records in the model','pill'));
  for(const id of scope.dimension_ids){const c=columns[id];target.append(node('span','Breakdown: '+(c?.name || 'Selected column'),'pill'));}
}
async function history(){
  const [data,questions,images]=await Promise.all([api('sessions'),api('questions'),api('attachments')]);
  renderImageHistory(images.images);
  $('question-history').replaceChildren(...questions.questions.map(q=>{const b=node('button');b.type='button';b.append(node('strong',q.text.slice(0,90)),node('small',q.status==='PROPOSED'?'Scope suggested':q.status==='NEEDS_INPUT'?'Clarification needed':q.status==='RESOLVING'?'Waiting for response':'Paused'));b.addEventListener('click',guard(async()=>{resetComposer();const epoch=generation;const draft=await api('questions/'+encodeURIComponent(q.id));if(epoch===generation)showIntake(draft);}));return b;}));$('history').replaceChildren();
  if(!data.sessions.length)$('history').append(node('p','Your investigations will appear here.','muted small'));
  for(const s of data.sessions){const button=node('button');button.type='button';button.classList.toggle('active',s.id===current?.id);
    button.append(node('strong',s.measure_name),node('small',s.symptom.slice(0,100)),node('small',new Date(s.created*1000).toLocaleString()));
    if(!s.id){button.disabled=true;button.append(node('small','Submission interrupted — operator review needed'));}
    else button.addEventListener('click',guard(()=>openSession(s.id)));
    $('history').append(button);}
}
function format(value){if(value===null)return 'Blank';if(typeof value==='boolean')return value?'True':'False';if(typeof value==='object'){if(value.type==='blank')return 'Blank';if('type' in value && 'value' in value)return format(value.value);return JSON.stringify(value);}return String(value);}
  function renderFact(fact){
    const card=node('article',undefined,'card fact');card.dataset.receiptId=fact.id;card.append(node('p',fact.origin.toUpperCase(),'eyebrow'),node('h2',fact.kind==='diagnostic'?'Diagnostic check':fact.metric));
    if(fact.kind==='diagnostic')card.append(node('p','This check can use a different scope from the original question. The query and evidence are available in Technical evidence.','muted small'));
    if(fact.calculation_context)card.append(node('p','Calculation path: '+fact.calculation_context.join(' → '),'muted small'));
  if(fact.status!=='COMPLETED'){card.append(node('p','This check did not return a usable result.','muted'));return card;}
  if(fact.kind==='records'){
    card.append(node('p',String(fact.values.length),'value'),node('p','Record groups captured','muted small'));
    if(fact.joint_aggregate){const a=fact.joint_aggregate;const detail=node('section',undefined,'joint-capture');
      detail.append(node('h3','Total and supporting records checked together'),node('p','Observed total: '+format(a.observed)));
      if(a.reconstructed)detail.append(node('p','Total rebuilt from records: '+format(a.reconstructed.value)));
      detail.append(node('p',a.status==='CAPTURE_RECONCILES'?'The captured total agrees with these records.':a.status==='CAPTURE_INCONSISTENCY'?'The captured total differs from these records. More evidence is needed.':'The record capture is insufficient to check the total.'));
      detail.append(node('p','Returned in one response. Report context and cause are not verified.','muted small'));card.append(detail);
    }return card;
  }
  if(fact.values.length===1 && fact.kind==='metric'){
    const row=fact.values[0];const values=row!==null && typeof row==='object'?Object.values(row):[row];
    card.append(node('p',values.map(format).join(' · '),'value'));
  }else if(fact.values.length){const table=node('table');table.append(node('caption','Captured values'));
    if(fact.kind==='diagnostic'){const head=node('tr');for(const name of Object.keys(fact.values[0]))head.append(node('th',name.replace(/^\[|\]$/g,'')));table.append(head);}
    for(const value of fact.values.slice(0,20)){const tr=node('tr');const vals=value!==null&&typeof value==='object'?Object.values(value):[value];for(const v of vals)tr.append(node('td',format(v)));table.append(tr);}card.append(table);
    if(fact.values.length>20)card.append(node('p','Showing 20 of '+fact.values.length+' captured rows. Download technical evidence for the full response.','muted small'));
  }else card.append(node('p','No rows returned.','muted'));
  card.append(node('p','Observed value · cause not verified','muted small'));return card;
}
function render(data){
  renderScreenshotResult(data.intake?.screenshot_review);
  current=data;$('composer').hidden=true;$('preview').hidden=true;$('result').hidden=false;
  $('result-title').textContent=data.measure_name;$('result-symptom').textContent=data.symptom;
  $('status').textContent=(!data.worker_attached&&activeStates.includes(data.status))?'Worker paused':statusNames[data.status]||data.status;
  $('summary').textContent=data.summary;$('question').textContent=data.question || '';$('question').hidden=!data.question;
  $('clarify').hidden=data.status!=='NEEDS_INPUT';$('cancel').hidden=['COMPLETED','CANCELLED'].includes(data.status);
  $('facts').replaceChildren(...data.facts.map(renderFact));
  if(!data.facts.length)$('facts').append(node('p','No results captured yet.','muted'));
  const explanations={CURRENT_SOURCE_MAPPING_MISSING:'An approved comparison with the connected records is missing for this metric and scope.',CURRENT_RECORD_MAPPING_MISSING:'A detailed record comparison has not been approved for this scope.',MAPPING_CONTEXT_VERSION_AND_CAUSAL_PROOF_NOT_VERIFIED:'Matching definitions, filters and data versions still need to be verified before a cause can be confirmed.'};
  const gaps=[...new Set(data.technical.outcome.gaps.map(g=>explanations[g.reason]||'An additional check needs reviewed context. Its details are in Technical evidence.'))];
  $('evidence-gaps').replaceChildren(...gaps.map(g=>node('li',g)));
  scopePills($('result-filters'),data.scope,data.columns);
  $('activity').replaceChildren();for(const e of data.activity.slice(-12)){const li=node('li',e.label);const t=node('time',new Date(e.created).toLocaleTimeString());t.dateTime=e.created;li.append(t);$('activity').append(li);}
  $('business').dataset.outcomeHash=data.outcome_hash;$('technical').dataset.outcomeHash=data.outcome_hash;
  $('identities').replaceChildren();for(const [label,value] of [['Session',data.id],['Scope',data.scope_hash],['Outcome',data.outcome_hash],['Cause verified',String(data.cause_verified)],['Delivery eligible',String(data.delivery_eligible)]])$('identities').append(node('dt',label),node('dd',value));
  $('technical-scope').textContent=JSON.stringify({scope:data.scope,budgets:data.technical.budgets,intake:data.intake},null,2);
  $('technical-outcome').textContent=JSON.stringify(data.technical.outcome,null,2);$('technical-decisions').textContent=JSON.stringify(data.technical.decisions,null,2);
}
async function openSession(id){
  stopPolling();const epoch=generation;const data=await api('sessions/'+encodeURIComponent(id));if(epoch!==generation)return;
  render(data);await history();schedule(epoch);
}
function schedule(epoch){
  if(!current||!activeStates.includes(current.status)||!current.worker_attached||current.job_status==='INTERRUPTED')return;
  timer=setTimeout(async()=>{try{const id=current.id;const data=await api('sessions/'+encodeURIComponent(id));if(epoch!==generation||id!==current?.id)return;render(data);schedule(epoch);}catch(e){if(epoch===generation)showError(e);}},2000);
}
function resetComposer(){resetIntake();stopPolling();current=null;predecessor=null;invalidate();$('result').hidden=true;$('composer').hidden=false;$('clarification-note').hidden=true;$('symptom').value='';modelChanged();}
$('login-form').addEventListener('submit',guard(async()=>{
  key=$('access-key').value;const result=await api('models');models=result.models;execution=result.execution_enabled;$('question-intake').hidden=!result.question_intake_enabled;$('screenshot-intake').hidden=!result.screenshot_intake_enabled;
  $('access-key').value='';$('login').hidden=true;$('workspace').hidden=false;$('signout').hidden=false;$('read-only').hidden=execution;
  options($('model'),models.map(m=>({id:m.id,name:m.name})));resetComposer();await history();
}));
$('signout').addEventListener('click',()=>{resetIntake();stopPolling();key='';models=[];current=null;preview=null;predecessor=null;$('workspace').hidden=true;$('login').hidden=false;$('signout').hidden=true;$('access-key').value='';$('history').replaceChildren();$('question-history').replaceChildren();$('image-history').replaceChildren();$('facts').replaceChildren();$('activity').replaceChildren();for(const id of ['technical-scope','technical-outcome','technical-decisions','identities'])$(id).replaceChildren();$('scope-form').reset();clearError();});
$('model').addEventListener('change',()=>{predecessor=null;$('clarification-note').hidden=true;modelChanged();});
$('scope-form').addEventListener('input',invalidate);$('scope-form').addEventListener('change',invalidate);
$('add-filter').addEventListener('click',guard(()=>addFilter()));
$('scope-form').addEventListener('submit',guard(async()=>{
  const filters=[...$('filters').children].map(row=>row.read());if(!filters.length&&!selectedModel()?.dynamic_investigation)throw new Error('Add at least one filter to keep this investigation bounded.');
  const request={model_id:$('model').value,measure_id:$('metric').value,symptom:$('symptom').value.trim(),filters,dimension_ids:$('breakdown').value?[$('breakdown').value]:[],predecessor,...(intakeId?{intake_id:intakeId}:{})};
  const revision=scopeRevision;$('review').disabled=true;try{const data=await api('previews',request);if(revision!==scopeRevision)throw new Error('The scope changed during review. Please review it again.');preview=data;$('preview-title').textContent=data.measure_name;$('preview-symptom').textContent=data.envelope.symptom;scopePills($('preview-filters'),data.envelope,data.columns);$('preview-note').textContent=data.scope_note;$('preview-contexts').replaceChildren(...(data.calculation_contexts||[]).map(c=>node('li',c.path.join(' \u2192 ')+': '+c.filters.map(f=>f.column+' = '+JSON.stringify(f.value)+(f.mode==='INTERSECT'?' (intersects existing filter)':' (replaces existing filter)')).join('; '))));$('preview').hidden=false;$('start').disabled=!execution;$('preview').scrollIntoView({behavior:'smooth',block:'nearest'});}finally{$('review').disabled=false;}
}));
$('start').addEventListener('click',guard(async()=>{if(!preview)return;const epoch=generation;$('start').disabled=true;try{const data=await api('sessions',{preview_id:preview.id});if(epoch===generation)await openSession(data.id);else await history();}finally{$('start').disabled=!execution;}}));
$('new-investigation').addEventListener('click',resetComposer);$('refresh-history').addEventListener('click',guard(history));
$('cancel').addEventListener('click',guard(async()=>{if(!current)return;const id=current.id;stopPolling();const epoch=generation;$('cancel').disabled=true;try{const data=await api('sessions/'+encodeURIComponent(id)+'/cancel',{});if(epoch===generation)render(data);await history();}finally{$('cancel').disabled=false;}}));
$('clarify').addEventListener('click',()=>{const data=current;resetComposer();predecessor=data.id;$('model').value=data.model_id;modelChanged();$('metric').value=data.scope.measure_id;$('symptom').value=data.symptom+'\n\nClarification: ';for(const f of data.scope.filters)addFilter(f);$('breakdown').value=data.scope.dimension_ids[0]||'';$('clarification-note').textContent=data.question;$('clarification-note').hidden=false;$('symptom').focus();});
function tab(technical){$('business').hidden=technical;$('technical').hidden=!technical;$('business-tab').setAttribute('aria-selected',String(!technical));$('technical-tab').setAttribute('aria-selected',String(technical));}
$('business-tab').addEventListener('click',()=>tab(false));$('technical-tab').addEventListener('click',()=>tab(true));
for(const id of ['business-tab','technical-tab'])$(id).addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){event.preventDefault();const technical=event.key==='End'||(event.key!=='Home'&&id==='business-tab');tab(technical);$(technical?'technical-tab':'business-tab').focus();}});
$('download').addEventListener('click',()=>{if(!current)return;const url=URL.createObjectURL(new Blob([JSON.stringify(current,null,2)],{type:'application/json'}));const a=node('a');a.href=url;a.download='investigation-'+current.id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});

function resetIntake(){resetScreenshots();questionRevision++;intakeId=null;intakeParent=null;intakeRequest=null;intakeSaved=null;$('business-question').value='';$('business-question').placeholder='Include the report or metric name and the exact filters or dates you selected.';$('intake-status').hidden=true;$('intake-history').hidden=true;$('hold-question').hidden=true;$('intake-provenance').hidden=true;}
function showIntake(data){
  if(data.screenshot_review)restoreScreenshotReview(data.screenshot_review);
  intakeSaved=data.id;$('hold-question').hidden=data.status!=='RESOLVING';$('intake-history').hidden=false;$('intake-status').hidden=false;
  if(data.status==='NEEDS_INPUT'){intakeParent=data.id;intakeRequest=null;$('intake-status').textContent=data.question;$('business-question').value='';$('business-question').placeholder='Add the clarification requested above.';$('business-question').focus();return;}
  $('business-question').value=data.request?.text||data.text;
  if(data.status!=='PROPOSED'){$('intake-status').textContent=data.status==='RESOLVING'?'This question is still reserved or its response is uncertain. Check saved status; it will not be sent again automatically.':'The question could not be resolved safely. You can select the scope manually or submit a new question.';return;}
  intakeParent=null;const p=data.proposal;if(!models.some(m=>m.id===p.model_id))throw new Error('The model catalog changed. Reopen the workspace.');
  predecessor=null;$('clarification-note').hidden=true;$('model').value=p.model_id;modelChanged();$('metric').value=p.measure_id;$('symptom').value=data.text;
  for(const f of p.filters)addFilter(f);$('breakdown').value=p.dimension_ids[0]||'';intakeId=data.id;
  $('intake-provenance').hidden=false;$('intake-status').textContent='Metric and filters suggested. Review the selection below; no data checks have run.';
  $('scope-form').scrollIntoView({behavior:'smooth',block:'nearest'});
}
$('business-question').addEventListener('input',()=>{questionRevision++;intakeRequest=null;invalidate();});
$('question-form').addEventListener('submit',guard(async()=>{
  const submitted=$('business-question').value.trim();if(!submitted)throw new Error('Describe the reporting question.');
  const epoch=generation,revision=questionRevision,scope=scopeRevision;
  if(!intakeRequest)intakeRequest={text:submitted,parent_id:intakeParent,request_key:crypto.randomUUID(),...(screenshotReviewId&&!intakeParent?{screenshot_review_id:screenshotReviewId}:{})};
  $('resolve-question').disabled=true;$('intake-status').hidden=false;$('intake-status').textContent='Finding the metric and filters in the catalog...';
  try{const data=await api('questions',intakeRequest);if(epoch!==generation||revision!==questionRevision||scope!==scopeRevision)return;showIntake(data);await history();}finally{$('resolve-question').disabled=false;}
}));
$('intake-history').addEventListener('click',guard(async()=>{if(!intakeSaved)return;const epoch=generation,revision=questionRevision,scope=scopeRevision;const data=await api('questions/'+encodeURIComponent(intakeSaved));if(epoch===generation&&revision===questionRevision&&scope===scopeRevision)showIntake(data);}));

$('hold-question').addEventListener('click',guard(async()=>{if(!intakeSaved)return;const epoch=generation;const data=await api('questions/'+encodeURIComponent(intakeSaved)+'/hold',{});if(epoch===generation)showIntake(data);await history();}));
