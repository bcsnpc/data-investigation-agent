'use strict';
let credential='', current=null;
const $=id=>document.getElementById(id);
const message=text=>{$('message').textContent=text;};
async function api(path,body){
  const r=await fetch('/api/v2/admin/models'+path,{method:body?'POST':'GET',headers:{Authorization:'Bearer '+credential,'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
  const data=await r.json(); if(!r.ok)throw new Error(data.error); return data;
}
function show(model){
  current=model; $('detail').hidden=false; $('name').textContent=model.name;
  $('state').textContent=model.stage+' · '+model.readiness+' · revision '+model.revision;
  $('limit').textContent=model.context?.limitation||'Import a completed scan to review this model.';
  for(const field of $('review').elements)if(field.name)field.value=model.business[field.name]||'';
  $('enable').textContent=model.enabled?'Disable catalog':'Enable catalog';
  $('capabilities').replaceChildren();
  for(const [key,value] of Object.entries(model.context?.capabilities||{})){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=key;dd.textContent=value;$('capabilities').append(dt,dd);}
  $('measures').replaceChildren();
  for(const m of model.context?.measures||[]){const li=document.createElement('li');li.textContent=m.name;$('measures').append(li);}
  $('history').textContent=JSON.stringify({changes:model.context?.changes,versions:model.context_history,activity:model.events},null,2);
}
async function refresh(){const models=await api('');$('models').replaceChildren();for(const m of models){const b=document.createElement('button');b.type='button';b.textContent=m.name+' · '+(m.enabled?'Enabled':'Disabled');b.onclick=()=>show(m);$('models').append(b);}return models;}
async function act(work){try{message('Working…');await work();message('Saved.');}catch(e){message(e.message);}}
$('login').onsubmit=e=>{e.preventDefault();credential=$('token').value;$('token').value='';current=null;$('detail').hidden=true;$('models').replaceChildren();act(async()=>{await refresh();current=null;$('detail').hidden=true;});};
$('register').onsubmit=e=>{e.preventDefault();act(async()=>{const body=Object.fromEntries(new FormData(e.target));body.report_ids=body.report_ids.split(',').map(x=>x.trim()).filter(Boolean);show(await api('',body));await refresh();});};
$('scan').onsubmit=e=>{e.preventDefault();act(async()=>{if(!current)throw new Error('Select a model');show(await api('/'+current.id+'/import',{revision:current.revision,scan_id:new FormData(e.target).get('scan_id')}));await refresh();});};
$('review').onsubmit=e=>{e.preventDefault();act(async()=>{show(await api('/'+current.id+'/review',{revision:current.revision,business:Object.fromEntries(new FormData(e.target))}));await refresh();});};
$('enable').onclick=()=>act(async()=>{show(await api('/'+current.id+'/enable',{revision:current.revision,enabled:!current.enabled}));await refresh();});
