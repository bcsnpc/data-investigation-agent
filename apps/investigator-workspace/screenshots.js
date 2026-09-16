'use strict';
let screenshotReviewId=null, screenshotAttachment=null, screenshotRead=null, screenshotReadRequest=null;
let screenshotUploadKey=null, screenshotReviewKey=null, screenshotRevision=0;
const imageObjects=new Map();
function clearImage(id){const img=$(id);img.dataset.image='';img.dataset.request='';if(imageObjects.has(id))URL.revokeObjectURL(imageObjects.get(id));imageObjects.delete(id);img.removeAttribute('src');img.hidden=true;}
async function loadImage(id,attachment){
  const img=$(id);if(img.dataset.image===attachment.id)return;
  clearImage(id);if(!attachment.available&&attachment.available!==undefined)return;
  const request=crypto.randomUUID(),credential=key;img.dataset.request=request;
  const response=await fetch('/api/workspace/attachments/'+encodeURIComponent(attachment.id)+'/content',{headers:{Authorization:'Bearer '+credential},cache:'no-store'});
  if(!response.ok)throw new Error('The stored screenshot is unavailable. Reviewed text remains in the saved question.');
  const blob=await response.blob();if(key!==credential||img.dataset.request!==request)return;
  const url=URL.createObjectURL(blob);imageObjects.set(id,url);img.src=url;img.hidden=false;img.dataset.image=attachment.id;
}
function screenshotChanged(){screenshotReviewId=null;screenshotReviewKey=null;intakeParent=null;intakeRequest=null;questionRevision++;invalidate();}
function resetScreenshots(){screenshotRevision++;screenshotReviewId=null;screenshotAttachment=null;screenshotRead=null;screenshotReadRequest=null;screenshotUploadKey=null;screenshotReviewKey=null;$('screenshot-file').value='';$('screenshot-text').value='';$('screenshot-status').hidden=true;$('screenshot-review').hidden=true;$('remove-screenshot').hidden=true;$('screenshot-saved-status').hidden=true;$('hold-screenshot').hidden=true;$('result-screenshot').hidden=true;clearImage('screenshot-preview');clearImage('result-screenshot-image');}
function showImageRead(data){
  screenshotChanged();
  screenshotRead=data;$('screenshot-saved-status').hidden=false;$('hold-screenshot').hidden=data.status!=='READING';$('screenshot-status').hidden=false;
  $('screenshot-review').hidden=data.status!=='EXTRACTED';
  if(data.status==='EXTRACTED'){$('screenshot-text').value=data.extraction.visible_text;$('screenshot-uncertainties').replaceChildren(...data.extraction.uncertainties.map(t=>node('li',t)));$('screenshot-status').textContent=data.extraction.readable?'Check the extracted details against your screenshot.':'The image could not be read clearly. Enter the correct details or use a clearer screenshot.';}
  else $('screenshot-status').textContent=data.status==='READING'?'Image read is reserved or still pending. Check saved status; it will not be resent automatically.':'The image read was held. Describe the report in text, or reattach the image to request a new read.';
}
async function openScreenshot(image){
  resetComposer();screenshotAttachment=image;$('remove-screenshot').hidden=!image.available;const revision=screenshotRevision;
  await loadImage('screenshot-preview',image);if(revision!==screenshotRevision)return;
  const data=await api('attachments/'+encodeURIComponent(image.id)+'/reads');if(revision!==screenshotRevision)return;
  if(data.reads.length)showImageRead(data.reads[0]);
  else{$('screenshot-status').hidden=false;$('screenshot-status').textContent=image.available?'Screenshot attached. Select Read screenshot to extract visible details.':'Stored image removed. Saved transcriptions remain in question history.';}
}
function renderImageHistory(images){$('image-history').replaceChildren(...images.map(image=>{const b=node('button');b.type='button';b.append(node('strong',image.name),node('small',image.available?'Stored screenshot':'Image removed'));b.addEventListener('click',guard(()=>openScreenshot(image)));return b;}));}
function restoreScreenshotReview(review){
  screenshotReviewId=review.id;screenshotAttachment=review.attachment;$('screenshot-status').hidden=false;$('screenshot-status').textContent='Saved reviewed screenshot details are included in this question.';
  loadImage('screenshot-preview',review.attachment).catch(error=>{$('screenshot-status').textContent=error.message;});
}
function renderScreenshotResult(review){
  $('result-screenshot').hidden=!review;if(!review){clearImage('result-screenshot-image');return;}
  $('result-screenshot-text').textContent=review.text;$('result-screenshot-note').textContent=review.edited?'The extracted text was corrected during review.':'Extracted text was accepted during review.';
  const identity=review.id;$('result-screenshot').dataset.review=identity;
  loadImage('result-screenshot-image',review.attachment).catch(error=>{if($('result-screenshot').dataset.review===identity)$('result-screenshot-note').textContent=error.message;});
}
$('screenshot-file').addEventListener('change',guard(()=>{
  $('remove-screenshot').hidden=true;$('screenshot-saved-status').hidden=true;$('hold-screenshot').hidden=true;$('screenshot-status').hidden=true;
  const file=$('screenshot-file').files[0];screenshotRevision++;screenshotAttachment=null;screenshotRead=null;screenshotReadRequest=null;screenshotUploadKey=crypto.randomUUID();screenshotChanged();$('screenshot-review').hidden=true;clearImage('screenshot-preview');
  if(file){if(!['image/png','image/jpeg'].includes(file.type)||file.size>1048576)throw new Error('Choose a PNG or JPEG screenshot up to 1 MB.');const url=URL.createObjectURL(file);imageObjects.set('screenshot-preview',url);$('screenshot-preview').src=url;$('screenshot-preview').hidden=false;}
}));
$('read-screenshot').addEventListener('click',guard(async()=>{
  const revision=screenshotRevision,epoch=generation;$('read-screenshot').disabled=true;
  try{
    if(!screenshotAttachment){const file=$('screenshot-file').files[0];if(!file)throw new Error('Choose a screenshot first.');if(!['image/png','image/jpeg'].includes(file.type)||file.size>1048576)throw new Error('Choose a PNG or JPEG screenshot up to 1 MB.');
      const bytes=new Uint8Array(await file.arrayBuffer());let binary='';for(const byte of bytes)binary+=String.fromCharCode(byte);
      const attached=await api('attachments',{name:file.name,mime:file.type,base64:btoa(binary),request_key:screenshotUploadKey||crypto.randomUUID()});
      if(revision!==screenshotRevision||epoch!==generation)return;screenshotAttachment=attached;$('remove-screenshot').hidden=false;
    }
    if(!screenshotReadRequest)screenshotReadRequest={attachment_id:screenshotAttachment.id,request_key:crypto.randomUUID()};
    $('screenshot-status').hidden=false;$('screenshot-status').textContent='Reading the visible report details...';
    const result=await api('screenshot-reads',screenshotReadRequest);if(revision!==screenshotRevision||epoch!==generation)return;
    screenshotChanged();showImageRead(result);await history();
  }finally{$('read-screenshot').disabled=false;}
}));
$('screenshot-text').addEventListener('input',screenshotChanged);
$('confirm-screenshot').addEventListener('click',guard(async()=>{
  if(!screenshotRead||screenshotRead.status!=='EXTRACTED')throw new Error('Read the screenshot first.');
  const revision=screenshotRevision,text=$('screenshot-text').value.trim();if(!text)throw new Error('Enter the visible details you want to use.');
  const questionVersion=questionRevision;if(!screenshotReviewKey)screenshotReviewKey=crypto.randomUUID();
  const reviewed=await api('screenshot-reviews',{extraction_id:screenshotRead.id,text,request_key:screenshotReviewKey});
  if(revision!==screenshotRevision||questionVersion!==questionRevision)return;screenshotReviewId=reviewed.id;intakeRequest=null;questionRevision++;invalidate();
  $('screenshot-status').textContent='Reviewed screenshot details will be included. Describe your question below, then find the metric and filters.';
}));
$('screenshot-saved-status').addEventListener('click',guard(async()=>{if(!screenshotRead)return;const revision=screenshotRevision;const data=await api('screenshot-reads/'+encodeURIComponent(screenshotRead.id));if(revision===screenshotRevision)showImageRead(data);}));
$('hold-screenshot').addEventListener('click',guard(async()=>{if(!screenshotRead)return;const revision=screenshotRevision;const data=await api('screenshot-reads/'+encodeURIComponent(screenshotRead.id)+'/hold',{});if(revision===screenshotRevision)showImageRead(data);}));
$('remove-screenshot').addEventListener('click',guard(async()=>{if(!screenshotAttachment)return;const revision=screenshotRevision;await api('attachments/'+encodeURIComponent(screenshotAttachment.id)+'/remove',{});if(revision!==screenshotRevision)return;resetScreenshots();screenshotChanged();$('screenshot-status').hidden=false;$('screenshot-status').textContent='Stored image removed. Previously saved transcriptions and questions remain available.';await history();}));
