'use strict';
let reportFormCatalog=null, reportFormRequest=null, reportFormRevision=0;
function resetReportForm(){reportFormCatalog=null;reportFormRequest=null;reportFormRevision++;$('report-ticket-form').reset();$('form-cell-keys').replaceChildren();$('form-intake').hidden=true;}
function formReportOptions(){
  const previous=$('form-report').value,search=$('form-report-search').value.toLocaleLowerCase();
  const reports=reportFormCatalog.models.flatMap(m=>m.reports.map(r=>({id:r.id,name:r.name}))).filter(r=>r.name.toLocaleLowerCase().includes(search));
  options($('form-report'),reports,'Choose a report');
  for(const r of reportFormCatalog.unbound_reports||[]){if(!r.name.toLocaleLowerCase().includes(search))continue;const option=node('option',r.name+' — not available in approved context');option.value=r.id;option.disabled=true;$('form-report').append(option);}
  if(reports.some(r=>r.id===previous))$('form-report').value=previous;
  if(previous!==$('form-report').value)formReportChanged();
}
function reportFormModel(){return reportFormCatalog?.models.find(m=>m.reports.some(r=>r.id===$('form-report').value));}
function reportFormVisuals(){return (reportFormModel()?.visuals||[]).filter(v=>v.report_id===$('form-report').value&&v.page_id===$('form-page').value);}
function formChanged(){reportFormRevision++;reportFormRequest=null;}
async function loadReportForm(refresh=false){
  const epoch=key;const catalog=await api('forms/catalog',refresh?{refresh:true}:undefined);if(epoch!==key)return;
  reportFormCatalog=catalog;formChanged();$('form-intake').hidden=false;
  $('form-list-status').textContent=catalog.live_lists_connected?'Live report and page choices; visual titles from the approved context.':'Report choices from the approved context. Live report lists are not connected on this host.';
  $('form-report-search').value='';options($('form-report'),[],'Choose a report');formReportOptions();
  options($('form-comparison'),catalog.comparison_choices.map(c=>({id:c.route,name:c.label+(c.route==='OTHER_REPORT'?' (coming soon)':'')})),'Not specified');
  formReportChanged();
}
function formReportChanged(){
  formChanged();const m=reportFormModel();const visuals=(m?.visuals||[]).filter(v=>v.report_id===$('form-report').value);
  const pages=new Map();for(const v of visuals)pages.set(v.page_id,{id:v.page_id,name:v.page_names?.[0]||v.page_id});
  options($('form-page'),[...pages.values()],'Choose a page');formPageChanged();
  if(reportFormCatalog?.live_lists_connected&&$('form-report').value){
    const id=$('form-report').value,epoch=key;
    api('forms/pages',{report_id:id,refresh:false}).then(result=>{
      if(epoch!==key||id!==$('form-report').value)return;
      options($('form-page'),result.pages.filter(p=>p.executable),'Choose a page');formPageChanged();
      if(result.pages.some(p=>!p.executable))$('form-list-status').textContent='Some live pages have no approved executable definition; recollection is required to investigate those pages.';
    }).catch(error=>{if(epoch===key&&id===$('form-report').value){options($('form-page'),[],'Page list unavailable');formPageChanged();showError(error);}});
  }
}
function formPageChanged(){
  formChanged();options($('form-target'),reportFormVisuals().map(v=>({id:v.target_id,name:v.names?.[0]||'Unnamed visual'})),'Not sure — ask me');formTargetChanged();
}
function formTargetChanged(){
  formChanged();const v=reportFormVisuals().find(v=>v.target_id===$('form-target').value);
  options($('form-mode'),v?(v.grouping_columns.length?[{id:'KEYED',name:'One displayed row'},{id:'TOTAL',name:'Total row'}]:[{id:'UNGROUPED',name:'Single number'}]):[],'Not specified');
  if(v&&!v.grouping_columns.length)$('form-mode').value='UNGROUPED';formModeChanged();
}
function formModeChanged(){
  formChanged();const host=$('form-cell-keys');host.replaceChildren();
  if($('form-mode').value!=='KEYED')return;
  const v=reportFormVisuals().find(v=>v.target_id===$('form-target').value);const m=reportFormModel();
  for(const id of v?.grouping_columns||[]){
    const c=m.columns.find(c=>c.column_id===id);const label=node('label',c?.name||'Row key');const input=node('input');input.id='form-key-'+crypto.randomUUID();label.htmlFor=input.id;input.dataset.columnId=id;input.dataset.dataType=c?.data_type||'';input.required=true;input.maxLength=2000;input.placeholder='Value shown on this row';host.append(label,input);
  }
}
$('form-refresh').addEventListener('click',guard(()=>loadReportForm(true)));
$('form-report').addEventListener('change',formReportChanged);
$('form-report-search').addEventListener('input',formReportOptions);
$('form-page').addEventListener('change',formPageChanged);
$('form-target').addEventListener('change',formTargetChanged);
$('form-mode').addEventListener('change',formModeChanged);
$('report-ticket-form').addEventListener('input',formChanged);
$('report-ticket-form').addEventListener('submit',guard(async()=>{
  const cellKeys=[...$('form-cell-keys').querySelectorAll('input')].map(input=>{
    let value=input.value;if(input.dataset.dataType==='int64'){if(!/^-?\d+$/.test(value)||!Number.isSafeInteger(Number(value)))throw new Error('Enter an exact whole-number row key.');value=Number(value);}
    if(input.dataset.dataType==='boolean'){if(!['true','false'].includes(value))throw new Error('Enter true or false for this row key.');value=value==='true';}
    return {column_id:input.dataset.columnId,value};
  });
  if(!reportFormRequest)reportFormRequest={version:'estate-form-input-v1',request_key:crypto.randomUUID(),report_id:$('form-report').value||null,page_id:$('form-page').value||null,target_id:$('form-target').value||null,cell_mode:$('form-mode').value||null,value_seen:$('form-value').value||null,comparison:$('form-comparison').value||null,description:$('form-description').value,cell_keys:cellKeys};
  const revision=reportFormRevision,epoch=key;$('form-submit').disabled=true;
  try{const saved=await api('forms',reportFormRequest);if(epoch!==key)return;if(revision!==reportFormRevision)throw new Error('The form changed while submitting; the original submission remains in history.');$('smart-ticket-intake').hidden=false;showSmartTicket(saved);await smartTicketHistory();}
  finally{$('form-submit').disabled=false;}
}));
