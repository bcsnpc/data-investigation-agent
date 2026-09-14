'use strict';
const $ = id => document.getElementById(id);
let token = '', session = 0, ticketId = '', selected = null, offset = null, busy = false;
let submission=null;const planningKeys=new Map();
const show = (id, visible) => { $(id).hidden = !visible; };
const message = text => { $('message').textContent = text; };
function element(tag, text) { const node = document.createElement(tag); node.textContent = text; return node; }
async function api(path, body, key) {
  const current = session;
  const response = await fetch(path, {method:body ? 'POST':'GET', cache:'no-store',
    headers:{Authorization:'Bearer '+token, ...(body ? {'Content-Type':'application/json'}:{}),...(key?{'Idempotency-Key':key}:{})},
    ...(body ? {body:JSON.stringify(body)}:{})});
  if (current !== session) throw new Error('Session changed.');
  if (!response.ok) {
    if (response.status === 401) throw new Error('Access token was not accepted. Disconnect and try again.');
    if (response.status === 409) throw new Error('This draft or its context changed. Refresh and review a current draft.');
    if (response.status === 404) throw new Error('That ticket or draft could not be found.');
    throw new Error('The request could not be completed. Refresh and try again.');
  }
  return response.json();
}
async function action(button, work) {
  if(busy)return;
  busy=true;
  button.disabled = true; message('');
  try { await work(); } catch (error) { message(error.message); }
  finally { button.disabled = false; busy=false; }
}
function resetViews() { for (const id of ['ticket','drafts-card','review','evidence']) show(id,false); selected=null; }
$('login-form').addEventListener('submit', event => { event.preventDefault(); action(event.submitter, async () => {
  token=$('token').value; $('token').value=''; await api('/api/investigations?limit=1');
  show('login',false); show('workspace',true); show('disconnect',true);
}); });
$('disconnect').addEventListener('click', () => { session++;token='';selected=null;ticketId='';resetViews();show('workspace',false);show('login',true);show('disconnect',false);message('Disconnected.'); });
async function drafts(append=false) {
  const result=await api('/api/tickets/'+encodeURIComponent(ticketId)+'/plans?offset='+(append ? offset:0));
  if (!append) $('drafts').replaceChildren();
  for (const item of result.items) {
    const button=element('button',item.status.replaceAll('_',' ')); button.className='draft';
    button.append(element('small','Open draft '+item.id.slice(0,8)));
    button.addEventListener('click',()=>action(button,()=>review(item.id))); $('drafts').append(button);
  }
  if (!append && !result.items.length) $('drafts').append(element('p','No drafts yet. Run ticket planning, then refresh.'));
  offset=result.next_offset;show('more',offset!==null);show('drafts-card',true);
}
async function loadTicket(id) {
  resetViews();
  const result=await api('/api/tickets/'+encodeURIComponent(id));ticketId=id;
  $('ticket-id').value=id;$('ticket-title').textContent=result.ticket.ticket.title;
  $('description').textContent=result.ticket.ticket.description;$('ticket-status').textContent=result.ticket.status;
  $('timeline').replaceChildren(...result.ticket.timeline.map(item=>element('div',new Date(item.at*1000).toLocaleString()+' · '+item.status)));
  show('ticket',true);await drafts();
  if(result.ticket.investigation_run_id) await evidence(result.ticket.investigation_run_id);
}
$('open-form').addEventListener('submit',event=>{event.preventDefault();action(event.submitter,()=>loadTicket($('ticket-id').value.trim()));});
$('refresh').addEventListener('click',event=>action(event.currentTarget,()=>loadTicket(ticketId)));
$('more').addEventListener('click',event=>action(event.currentTarget,()=>drafts(true)));
$('create-form').addEventListener('submit',event=>{event.preventDefault();action(event.submitter,async()=>{
  const body={title:$('new-title').value.trim(),report:$('new-report').value.trim(),description:$('new-description').value.trim()};
  const encoded=JSON.stringify(body);if(!submission || submission.encoded!==encoded)submission={encoded,key:crypto.randomUUID()};
  const result=await api('/api/tickets',body,submission.key);await loadTicket(result.ticket_id);
  $('create-form').closest('details').open=false;message('Ticket submitted. Generate a draft to review its proposed scope.');
});});
$('generate').addEventListener('click',event=>action(event.currentTarget,async()=>{
  const id=ticketId;if(!planningKeys.has(id))planningKeys.set(id,crypto.randomUUID());
  message('Generating a draft. This may take up to two minutes.');
  const result=await api('/api/tickets/'+encodeURIComponent(id)+'/plan',{confirm:true},planningKeys.get(id));
  if(result.status==='FAILED')throw new Error('Planning failed. The same request will not be charged again automatically. Review the local provider setup before trying a new request.');
  if(result.status==='RUNNING'){message('Planning is still running or its outcome is uncertain. Refresh drafts shortly.');return;}
  await drafts();await review(result.plan_id);message('Draft ready. Review the scope before approving.');
}));
async function review(id) {
  selected=null;show('review',false);const result=await api('/api/plans/'+encodeURIComponent(id));selected=result;
  const scope=result.draft.plan;$('scope').replaceChildren();$('questions').replaceChildren();
  if(scope) for(const [label,value] of [['Report',result.report_name || 'Unresolved report'],['Metric',scope.metric],['Currency',scope.currency],['Order',scope.order_id || 'All orders']]) {
    $('scope').append(element('dt',label),element('dd',value || 'Not specified'));
  }
  for(const question of scope?.questions || []) $('questions').append(element('p',question));
  $('confirm').checked=false;
  const allowed=result.draft.status==='DRAFT_REQUIRES_REVIEW' && !result.approval;
  show('approve-form',allowed);$('approval-note').replaceChildren();
  if(result.approval) {
    $('approval-note').append(element('span','Already approved. '));
    const button=element('button','Open investigation ticket');button.className='secondary';
    button.addEventListener('click',()=>action(button,()=>loadTicket(result.approval.ticket_id)));$('approval-note').append(button);
  } else if(!allowed) $('approval-note').textContent='This draft needs clarification or could not be planned. It cannot be approved.';
  show('review',true);
}
$('approve-form').addEventListener('submit',event=>{event.preventDefault();const draft=selected;if(!draft || !$('confirm').checked)return;
  action(event.submitter,async()=>{const result=await api('/api/plans/'+draft.draft.id+'/approve',{confirm:true,plan_hash:draft.plan_hash});
    await loadTicket(result.ticket_id);message('Investigation queued. Refresh status after the worker runs.');});});
async function evidence(id) {
  const result=await api('/api/investigations/'+encodeURIComponent(id));const summary=result.summary;
  $('classification').textContent=summary.classification;$('summary').textContent=summary.text;
  $('observations').replaceChildren(...summary.observations.map(item=>{const row=document.createElement('tr');
    for(const value of [item.metric,item.layer,item.value===null?'Unavailable':item.value+(item.currency && item.metric!=='order_count'?' '+item.currency:''),item.status])row.append(element('td',value));return row;}));
  $('boundaries').replaceChildren(...summary.boundaries.map(item=>element('p',item.metric+' · '+item.status)));
  $('explanation').replaceChildren();
  if(result.explanation) {
    const explanation=result.explanation.explanation;
    $('explanation').append(element('h3','Evidence highlights'),element('p','AI selected these findings from the saved evidence.'),element('p',explanation.limitations));
    for(const [heading,items] of [['Findings',explanation.findings],['Suggested next steps',explanation.next_steps]]) {
      $('explanation').append(element('h4',heading));const list=document.createElement('ul');
      for(const item of items) {
        const row=element('li',item.text);const refs=document.createElement('details');
        refs.append(element('summary','Evidence references'));
        for(const ref of item.references)refs.append(element('p',ref));
        row.append(refs);list.append(row);
      }
      $('explanation').append(list);
    }
  } else $('explanation').append(element('p','No validated AI explanation is saved for this evidence yet.'));
  show('evidence',true);
}
$('ticket-id').value=new URLSearchParams(location.search).get('ticket') || '';
