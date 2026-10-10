'use strict';
let questionnaireDefinition=null, questionnaireCatalog=null, questionnaireMode='WEB', questionnaireStep=0, questionnaireEpoch=0;
const questionnaireValues={};
function questionnaireReports(){return (questionnaireCatalog?.models||[]).flatMap(m=>m.reports.map(r=>({id:r.id,name:r.name})));}
async function loadReportForm(refresh=false){
  const credential=key, epoch=++questionnaireEpoch;
  const [definition,catalog]=await Promise.all([api('questionnaire/schema'),api('questionnaire/catalog',refresh?{refresh:true}:undefined)]);
  if(credential!==key||epoch!==questionnaireEpoch)return;
  questionnaireDefinition=definition;questionnaireCatalog=catalog;questionnaireStep=0;
  for(const k of Object.keys(questionnaireValues))delete questionnaireValues[k];
  for(const id of ['form-intake','question-intake','smart-ticket-form','scope-form'])$(id).hidden=true;
  $('smart-ticket-intake').hidden=false;$('simple-intake').hidden=false;
  $('simple-list-note').textContent=catalog.live_lists_connected?'Report and page choices are live. Visual titles use the approved saved definition.':'Choices use approved saved definitions; live listing is not connected.';
  await renderQuestionnaire();
  const id=new URL(location.href).searchParams.get('ticket');
  if(id){const saved=await api('tickets/'+encodeURIComponent(id));if(credential===key)showSmartTicket(saved);}
}
async function questionnaireList(field){
  if(field.name==='report_id')return questionnaireReports();
  if(field.name==='page_id'){
    if(!questionnaireValues.report_id)return [];
    if(questionnaireCatalog.live_lists_connected){const r=await api(field.list,{report_id:questionnaireValues.report_id,refresh:false});return r.pages.filter(p=>p.executable);}
    const pages=new Map();for(const m of questionnaireCatalog.models)for(const v of m.visuals||[])if(v.report_id===questionnaireValues.report_id)pages.set(v.page_id,{id:v.page_id,name:v.page_names?.[0]||v.page_id});return [...pages.values()];
  }
  if(!questionnaireValues.report_id||!questionnaireValues.page_id)return [];
  return (await api(field.list,{report_id:questionnaireValues.report_id,page_id:questionnaireValues.page_id})).visuals;
}
async function renderQuestionnaire(){
  const epoch=++questionnaireEpoch, host=$('simple-fields');host.replaceChildren();
  const fields=questionnaireDefinition.fields.filter(f=>f.kind!=='screenshot');
  const visible=questionnaireMode==='CHAT'?[fields[questionnaireStep]]:fields;
  $('simple-submit').textContent=questionnaireMode==='CHAT'&&questionnaireStep<fields.length-1?'Continue':'Submit ticket';
  $('simple-channel-note').textContent=questionnaireMode==='CHAT'?'Question '+(questionnaireStep+1)+' of '+fields.length:'';
  for(const field of visible){
    if(epoch!==questionnaireEpoch)return;
    const label=node('label',field.label+(field.optional?' (optional)':''));let control;
    if(field.kind==='select'){
      const choices=await questionnaireList(field);if(epoch!==questionnaireEpoch)return;
      control=node('select');options(control,choices,field.optional?'Not selected':'Choose '+field.label.toLowerCase());
      control.value=questionnaireValues[field.name]||'';
    }else if(field.kind==='comparison'){
      control=node('select');options(control,field.choices.map(c=>({id:c.value,name:c.label})),'Choose a comparison');control.value=questionnaireValues.comparing?.kind||'';
    }else{control=node('textarea');control.rows=4;control.maxLength=field.maxLength;control.value=questionnaireValues[field.name]||'';}
    control.id='simple-'+field.name;label.htmlFor=control.id;control.required=!field.optional;
    control.addEventListener(field.kind==='text'?'input':'change',guard(async()=>{
      questionnaireValues[field.name]=field.kind==='comparison'?{kind:control.value}:control.value||null;
      if(field.name==='report_id'){delete questionnaireValues.page_id;delete questionnaireValues.visual_id;}
      if(field.name==='page_id')delete questionnaireValues.visual_id;
      if(field.kind!=='text')await renderQuestionnaire();
    }));host.append(label,control);
    if(field.kind==='comparison')await renderComparisonExtras(host,field);
  }
}
async function renderComparisonExtras(host,field){
  const selected=questionnaireValues.comparing;if(!selected?.kind)return;
  const choice=field.choices.find(c=>c.value===selected.kind);
  for(const reveal of choice.reveals){
    if(reveal==='screenshot')continue;let control;
    if(reveal==='source_value'){control=node('input');control.maxLength=2000;control.value=selected.source_value||'';}
    else{
      control=node('select');let choices=questionnaireReports();
      if(reveal==='page_id'){
        const report=selected.kind==='OTHER_PAGE'?questionnaireValues.report_id:selected.report_id;
        choices=[];
        if(report&&questionnaireCatalog.live_lists_connected)choices=(await api('questionnaire/pages',{report_id:report,refresh:false})).pages.filter(p=>p.executable);
        else if(report){const seen=new Map();for(const m of questionnaireCatalog.models)for(const v of m.visuals||[])if(v.report_id===report)seen.set(v.page_id,{id:v.page_id,name:v.page_names?.[0]||v.page_id});choices=[...seen.values()];}
      }
      options(control,choices,reveal==='report_id'?'Choose another report':'Choose another page');control.value=selected[reveal]||'';control.required=true;
    }
    const label=node('label',reveal==='source_value'?'Value in the source (optional)':reveal==='report_id'?'Other report':'Other page');control.id='simple-other-'+reveal;label.htmlFor=control.id;host.append(label,control);
    control.addEventListener(reveal==='source_value'?'input':'change',guard(async()=>{selected[reveal]=control.value||null;if(reveal==='report_id'){delete selected.page_id;await renderQuestionnaire();}}));
  }
}
$('simple-form').addEventListener('submit',guard(async()=>{
  const fields=questionnaireDefinition.fields.filter(f=>f.kind!=='screenshot');
  if(questionnaireMode==='CHAT'&&questionnaireStep<fields.length-1){questionnaireStep++;await renderQuestionnaire();return;}
  const request={version:questionnaireDefinition.version,request_key:crypto.randomUUID(),report_id:questionnaireValues.report_id,page_id:questionnaireValues.page_id,
    visual_id:questionnaireValues.visual_id||null,comparing:questionnaireValues.comparing,description:questionnaireValues.description||'',screenshot_review_id:screenshotReviewId};
  $('simple-submit').disabled=true;
  try{const saved=await api('questionnaire',request);showSmartTicket(saved);$('simple-submitted').textContent='Ticket submitted';$('simple-ticket-link').href='/?ticket='+encodeURIComponent(saved.ticket.id);$('simple-ticket-link').textContent='Open ticket';await smartTicketHistory();}
  finally{$('simple-submit').disabled=false;}
}));
for(const [id,mode] of [['simple-web','WEB'],['simple-chat','CHAT']])$(id).addEventListener('click',guard(async()=>{questionnaireMode=mode;questionnaireStep=0;await renderQuestionnaire();}));
$('simple-refresh').addEventListener('click',guard(()=>loadReportForm(true)));
function renderQuestionnaireTicket(saved){
  const ticket=saved.ticket;$('smart-ticket-intake').hidden=false;
  const input=ticket.questionnaire_input||ticket.form_input||saved.request, facts=$('ticket-submitted-facts');facts.replaceChildren();
  for(const [label,value] of [['Report',input.report_id],['Page',input.page_id],['Visual',input.visual_id||input.target_id],['Comparison',input.comparing?.kind||input.comparison],['Value in the source',input.comparing?.source_value],['Description',input.description||input.text]]){
    if(!value)continue;
    const found=questionnaireCatalog?.models.flatMap(m=>[...m.reports,...(m.visuals||[]).flatMap(v=>[{id:v.target_id,name:v.names?.[0]},{id:v.page_id,name:v.page_names?.[0]}])]).find(v=>v.id===value);
    const choice=label==='Comparison'?questionnaireDefinition?.fields.find(f=>f.name==='comparing').choices.find(c=>c.value===value):null;
    facts.append(node('dt',label),node('dd',found?.name||choice?.label||value));
  }
  const thread=$('ticket-comments');thread.replaceChildren();
  for(const q of ticket.questions)thread.append(node('li','Investigator: '+q.question));
  if(ticket.questions.some(q=>q.field==='NUMBER'))thread.append(node('li','Investigator: You can attach a screenshot of the displayed number to help identify it.'));
  $('ticket-screenshot-answer').hidden=ticket.state!=='CLARIFYING'||!ticket.form_input||Boolean(ticket.intake_id);
  for(const c of ticket.comments||[]){const item=node('li',(c.actor==='USER'?'You':'Investigator')+': '+c.text);if(c.attachment)item.append(node('p','Attached screenshot: '+c.attachment.name));if(c.review)item.append(node('p','Reviewed visible details: '+c.review.text));thread.append(item);}
  if(ticket.session_id)api('tickets/'+encodeURIComponent(ticket.id)+'/progress').then(r=>{if(smartTicket?.ticket.id===ticket.id)$('ticket-progress').replaceChildren(...r.steps.map(s=>node('li',s.label+' — '+s.status.toLowerCase())));}).catch(showError);
}
$('ticket-comment-form').addEventListener('submit',guard(async()=>{
  if(!smartTicket)return;
  const r=await api('tickets/'+encodeURIComponent(smartTicket.ticket.id)+'/comments',{revision:smartTicket.revision,request_key:crypto.randomUUID(),text:$('ticket-comment-text').value,
    attachment_id:$('ticket-comment-attach').checked?screenshotAttachment?.id||null:null,review_id:$('ticket-comment-attach').checked?screenshotReviewId:null});
  $('ticket-comment-text').value='';showSmartTicket(r);
}));
$('ticket-screenshot-answer').addEventListener('click',guard(async()=>{
  if(!smartTicket||!screenshotReviewId)throw new Error('Upload, read and review the screenshot first.');
  const saved=await api('tickets/'+encodeURIComponent(smartTicket.ticket.id)+'/screenshot-reply',{revision:smartTicket.revision,review_id:screenshotReviewId,request_key:crypto.randomUUID()});showSmartTicket(saved);
}));
$('new-investigation').addEventListener('click',guard(()=>loadReportForm()));
