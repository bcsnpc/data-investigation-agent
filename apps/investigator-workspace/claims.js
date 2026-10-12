/* Claim intake is additive. Confirmation records an interpretation, not a finding. */
(() => {
  let current = null, screenshot = null, pending = false, revision = 0;
  const el = id => document.getElementById(id);
  const key = () => crypto.randomUUID();
  const run = fn => guard(async () => {
    if (pending) return;
    pending = true;
    try { await fn(); } finally { pending = false; }
  })();
  const request = async (path, body) => {
    const started = revision, result = await api(path, body);
    if (started !== revision) throw new Error('This response belongs to an earlier question.');
    return result;
  };
  const endpoint = 'claims';
  function paragraph(parent, text) { parent.appendChild(node('p', text)); }
  function render(record) {
    current = record;
    const box = el('claim-result'); box.hidden = false; box.replaceChildren();
    paragraph(box, ({CLARIFYING: 'One detail will help us choose the right check.',
      AWAITING_CONFIRMATION: 'Check that we understood your question.',
      CONFIRMED: 'Your interpretation is confirmed. No finding has been made.',
      HELD: 'This question needs more evidence before a check can start.'})[record.status] || 'Question saved.');
    if (record.interpretation?.text) paragraph(box, record.interpretation.text);
    if (record.questions?.length) {
      const form = node('form');
      for (const q of record.questions) {
        const group = node('fieldset'); group.appendChild(node('legend', q.question));
        for (const choice of q.choices || []) {
          const label = node('label'); const radio = document.createElement('input');
          radio.type = 'radio'; radio.name = q.id; radio.value = choice.id;
          label.append(radio, document.createTextNode(choice.label)); group.appendChild(label);
        }
        const label = node('label', 'Or answer in your own words');
        const input = document.createElement('textarea'); input.maxLength = 2000;
        input.rows = 2; input.dataset.question = q.id; label.appendChild(input);
        group.appendChild(label); form.appendChild(group);
      }
      const submit = node('button', 'Save my answer'); submit.type = 'submit'; form.appendChild(submit);
      form.addEventListener('submit', event => { event.preventDefault(); run(async () => {
        const answers = record.questions.map(q => {
          const text = [...form.querySelectorAll('textarea')].find(x => x.dataset.question === q.id).value.trim();
          const selected = [...form.querySelectorAll('input:checked')].find(x => x.name === q.id);
          if (text && selected) throw new Error('Use either a choice or your own words for each answer.');
          if (!text && !selected) throw new Error('Please answer the pending question.');
          return {question_id:q.id, ...(text ? {text} : {choice_id:selected.value})};
        });
        render(await request(endpoint + '/' + encodeURIComponent(record.id) + '/replies',
          {revision:record.revision, answers, request_key:key()}));
      }); });
      box.appendChild(form);
    }
    if (record.status === 'AWAITING_CONFIRMATION') {
      const confirm = node('button', 'Yes, that is my question'); confirm.type = 'button';
      confirm.addEventListener('click', () => run(async () => render(await request(
        endpoint + '/' + encodeURIComponent(record.id) + '/confirm',
        {revision:record.revision,accepted:true,request_key:key()}))));
      box.appendChild(confirm);
      paragraph(box, 'If anything is wrong, edit your description and submit it again before confirming.');
    }
    const link = node('a', 'Open this saved question');
    link.href = '#claim=' + encodeURIComponent(record.id); box.appendChild(link);
  }
  function renderScreenshot(review) {
    screenshot = review;
    const box = el('claim-image-result'); box.hidden = false; box.replaceChildren();
    paragraph(box, 'Visible text was read locally. Hidden selections and security rules are not established by an image.');
    if (review.question) paragraph(box, typeof review.question === 'string' ? review.question : review.question.text || 'Which report and page is this?');
    // Indistinguishable names need a visible locator, not a hidden-ID choice.
    for (const candidate of review.status === 'NEEDS_LOCATOR' || review.locator_required ? [] : review.candidates || []) {
      const button = node('button', candidate.label); button.type = 'button';
      button.addEventListener('click', () => run(async () => {
        const portal = portalContext();
        renderScreenshot(await request('claim-screenshots/' + encodeURIComponent(review.review_id) + '/confirm',
          {candidate_id:candidate.candidate_id,request_key:key(),...(portal ? {portal} : {})}));
      })); box.appendChild(button);
    }
    if (review.confirmations?.length) paragraph(box, 'Report and page confirmed.');
  }
  function portalContext() {
    const portal = el('claim-portal').value.trim(), tab = el('claim-portal-tab').value.trim();
    if (!!portal !== !!tab) throw new Error('Give both the portal name and tab, or leave both blank.');
    return portal ? {portal,tab} : null;
  }
  el('claim-read-image').addEventListener('click', () => run(async () => {
    const file = el('claim-image').files[0];
    if (!file) throw new Error('Choose a screenshot first.');
    if (file.size > 1024*1024) throw new Error('Use a screenshot smaller than 1 MB.');
    const data = await new Promise((resolve,reject) => {const reader = new FileReader(); reader.onload = () => resolve(reader.result); reader.onerror = reject; reader.readAsDataURL(file);});
    const image = await request('attachments', {name:file.name,mime:file.type,base64:data.split(',')[1],request_key:key()});
    const portal = portalContext();
    renderScreenshot(await request('claim-screenshots', {image_id:image.id,request_key:key(),...(portal ? {portal} : {})}));
  }));
  el('claim-form').addEventListener('submit', event => { event.preventDefault(); run(async () => {
    const text = el('claim-text').value.trim();
    if (!text && !screenshot) throw new Error('Describe your question or read a screenshot.');
    render(await request(endpoint, {text,request_key:key(),...(screenshot ? {screenshot_evidence:{review_id:screenshot.review_id}} : {})}));
  }); });
  function reset() {
    revision++;
    current = null; screenshot = null; el('claim-form').reset();
    el('claim-result').hidden = true; el('claim-image-result').hidden = true;
  }
  el('new-investigation').addEventListener('click', reset);
  el('signout').addEventListener('click', reset);
  el('claim-image').addEventListener('change', () => { revision++; screenshot = null; el('claim-image-result').hidden = true; });
  function openSaved() {
    if (location.hash.startsWith('#claim=')) run(async () => render(await request(endpoint + '/' + encodeURIComponent(decodeURIComponent(location.hash.slice(7))))));
  }
  window.addEventListener('hashchange', openSaved);
  window.addEventListener('workspace-ready', openSaved);
})();
