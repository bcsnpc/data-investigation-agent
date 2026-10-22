'use strict';
const form=document.getElementById('essentials');
const output=document.getElementById('intake-result');
const goal=document.getElementById('goal');
goal.addEventListener('change',()=>{
  const comparing=goal.value==='COMPARE';
  document.getElementById('comparison-fields').hidden=!comparing;
  document.getElementById('comparison-reference').required=comparing;
});
async function send(path,body){
  const response=await fetch('/api/workspace/essentials'+path,{method:'POST',
    headers:{'Content-Type':'application/json','Authorization':'Bearer '+document.getElementById('access-key').value},
    body:JSON.stringify(body)});
  if(!response.ok)throw new Error('The question could not be saved. Check the workspace key and try again.');
  return response.json();
}
function show(result){
  output.replaceChildren();
  const heading=document.createElement('h2');
  heading.textContent=result.status==='READY'?'Your question is ready to investigate':result.status==='CLARIFYING'?'One detail to confirm':'Your question is saved and held';
  output.append(heading);
  if(result.status==='CLARIFYING'){
    const question=result.questions[0];
    const text=document.createElement('p');text.textContent=question.text;output.append(text);
    for(const choice of question.choices){
      const button=document.createElement('button');button.type='button';button.textContent=choice.label;
      button.addEventListener('click',async()=>{
        for(const peer of output.querySelectorAll('button'))peer.disabled=true;
        try{show(await send('/'+encodeURIComponent(result.intake_id)+'/reply',{
          choice_key:choice.key,request_key:crypto.randomUUID()}));}catch(error){showError(error);}
      });output.append(button);
    }
  }else if(result.status!=='READY'){
    const why=document.createElement('p');why.textContent=(result.reason||'intake unavailable').toLowerCase().replaceAll('_',' ');output.append(why);
  }
}
function showError(error){output.replaceChildren();const text=document.createElement('p');text.textContent=error.message;output.append(text);}
form.addEventListener('submit',async(event)=>{
  event.preventDefault();
  const data=new FormData(form),body={version:'investigator-essentials-v1',request_key:crypto.randomUUID(),
    report:data.get('report'),number:data.get('number'),goal:data.get('goal'),comparison:null};
  for(const name of ['page','value','description'])if(data.get(name))body[name]=data.get(name);
  if(body.goal==='COMPARE'){
    body.comparison={kind:document.getElementById('comparison-kind').value,reference:document.getElementById('comparison-reference').value};
    const value=document.getElementById('comparison-value').value;if(value)body.comparison.value=value;
  }
  try{show(await send('',body));}catch(error){showError(error);}
});
