'use strict';
let reportFormCatalog=null, reportFormRequest=null, reportFormRevision=0, reportFormSubject='REPORT', formLayoutEpoch=0;
function resetReportForm(){reportFormCatalog=null;reportFormRequest=null;reportFormRevision++;reportFormSubject='REPORT';formLayoutEpoch++;$('report-ticket-form').reset();$('form-cell-keys').replaceChildren();$('form-page-picture').replaceChildren();$('form-page-picture').hidden=false;$('form-cell-keys').hidden=false;$('form-measure-note').hidden=true;$('form-description').required=false;$('form-measure-text').textContent="It's about a measure, not a specific report";for(const id of ['form-report','form-report-search','form-page','form-target','form-mode'])$(id).disabled=false;$('form-intake').hidden=true;}
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
async function loadLegacyReportForm(refresh=false){
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
  loadFormPagePicture();
}
async function loadFormPagePicture(){
  const epoch=++formLayoutEpoch,host=$('form-page-picture');host.replaceChildren();
  const report=$('form-report').value,page=$('form-page').value;if(!report||!page)return;
  try{
    const result=await api('forms/layout',{report_id:report,page_id:page});if(epoch!==formLayoutEpoch)return;
    const drawing=layoutDrawing(result.page,$('form-target').value);
    drawing.setAttribute('role','group');
    for(const box of drawing.children){
      const visual=result.page.visuals[[...drawing.children].indexOf(box)];
      if(!reportFormVisuals().some(v=>v.target_id===visual.target_id))continue;
      box.tabIndex=0;box.setAttribute('role','button');box.setAttribute('aria-label','Select '+visual.name);
      const pick=()=>{$('form-target').value=visual.target_id;formTargetChanged();loadFormPagePicture();};
      box.addEventListener('click',pick);box.addEventListener('keydown',event=>{if(['Enter',' '].includes(event.key)){event.preventDefault();pick();}});
    }
    host.append(drawing,node('small',result.qualification));
  }catch(error){if(epoch===formLayoutEpoch)host.append(node('p','Page layout unavailable. You can use the optional visual-title choice.','muted'));}
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
$('form-measure-text').addEventListener('click',()=>{
  reportFormSubject=reportFormSubject==='REPORT'?'MEASURE_TEXT':'REPORT';formChanged();
  const measure=reportFormSubject==='MEASURE_TEXT';$('form-measure-note').hidden=!measure;
  $('form-measure-text').textContent=measure?'It is about a report instead':"It's about a measure, not a specific report";
  for(const id of ['form-report','form-report-search','form-page','form-target','form-mode'])$(id).disabled=measure;
  $('form-page-picture').hidden=measure;$('form-cell-keys').hidden=measure;
  for(const input of $('form-cell-keys').querySelectorAll('input'))input.disabled=measure;
  $('form-description').required=measure;
});
$('report-ticket-form').addEventListener('input',formChanged);
$('report-ticket-form').addEventListener('submit',guard(async()=>{
  const cellKeys=[...$('form-cell-keys').querySelectorAll('input')].filter(input=>!input.disabled).map(input=>{
    let value=input.value;if(input.dataset.dataType==='int64'){if(!/^-?\d+$/.test(value)||!Number.isSafeInteger(Number(value)))throw new Error('Enter an exact whole-number row key.');value=Number(value);}
    if(input.dataset.dataType==='boolean'){if(!['true','false'].includes(value))throw new Error('Enter true or false for this row key.');value=value==='true';}
    return {column_id:input.dataset.columnId,value};
  });
  if(!reportFormRequest)reportFormRequest={version:'estate-form-input-v1',request_key:crypto.randomUUID(),report_id:$('form-report').value||null,page_id:$('form-page').value||null,target_id:$('form-target').value||null,cell_mode:$('form-mode').value||null,value_seen:$('form-value').value||null,comparison:$('form-comparison').value||null,description:$('form-description').value,cell_keys:cellKeys};
  if(reportFormSubject==='MEASURE_TEXT')reportFormRequest={...reportFormRequest,subject:'MEASURE_TEXT',report_id:null,page_id:null,target_id:null,cell_mode:null,cell_keys:[]};
  const revision=reportFormRevision,epoch=key;$('form-submit').disabled=true;
  try{const saved=await api('forms',reportFormRequest);if(epoch!==key)return;if(revision!==reportFormRevision)throw new Error('The form changed while submitting; the original submission remains in history.');$('smart-ticket-intake').hidden=false;showSmartTicket(saved);await smartTicketHistory();}
  finally{$('form-submit').disabled=false;}
}));
