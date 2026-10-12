"""Local OCR identification is retained candidate evidence, never causal proof."""
import json,re
from .onboarding import Conflict,digest,encoded,text
from .process_tape import uuid4,bounded_call
from .run_recording import operation

def normal(value):return ' '.join(re.findall(r'\w+',value.casefold()))

def request_shape(request,required,optional=()):
    if not isinstance(request,dict)or set(request)-set(required)-set(optional)or not set(required)<=set(request):raise ValueError('Invalid screenshot request fields')
    for key in required:text(request[key],200 if key.endswith('_id') else 100)
    if 'portal'in request:
        portal=request['portal']
        if not isinstance(portal,dict)or set(portal)!={'portal','tab'}:raise ValueError('Portal and tab names required')
        for value in portal.values():text(value,120)

def rank(ocr,pages):
    visible=' '+normal('\n'.join(line['text'] for line in ocr['lines']))+' '
    ranked=[]
    for page in pages:
        hits=[]
        for anchor in [page['names']['report'],page['names']['page'],*page['anchors']]:
            key=normal(anchor)
            if key and ' '+key+' ' in visible and key not in [normal(x) for x in hits]:hits.append(anchor)
        if not hits:continue
        # Distinct visual labels outweigh a shared page/report title.
        score=sum(2 if normal(a) in {normal(v) for v in page['anchors']} else 1 for a in hits)
        ranked.append(dict(page,score=score,matched_anchors=hits,status='CANDIDATE'))
    return sorted(ranked,key=lambda p:(-p['score'],p['candidate_id']))

class ClaimScreenshots:
    def __init__(self,workspace):
        self.workspace,self.store=workspace,workspace.store
        with self.store.connect() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS claim_screenshot_reviews(id TEXT PRIMARY KEY,request_key TEXT UNIQUE,body TEXT,hash TEXT);
            CREATE TABLE IF NOT EXISTS claim_screenshot_confirmations(id TEXT PRIMARY KEY,request_key TEXT UNIQUE,review_id TEXT,body TEXT,hash TEXT);
            CREATE TABLE IF NOT EXISTS claim_screenshot_portal_maps(id TEXT PRIMARY KEY,body TEXT,hash TEXT);''')

    def _pages(self):
        from .adapters.screenshot_fingerprints import catalog
        pages=getattr(self.workspace,'claim_screenshot_catalog',lambda:catalog(self.workspace))()
        if not isinstance(pages,list)or len(pages)>100 or len(encoded(pages))>1_000_000:raise Conflict('Screenshot catalog exceeds bound; explicitly scope the estate rather than truncate candidates')
        return pages

    def _guard(self):
        if self.workspace.agent.config.get('_estate',{}).get('recording',{}).get('tape_class')=='PRIVACY_PROJECTED':
            raise Conflict('Screenshot OCR unavailable: privacy projection does not cover image pixels')

    def _portal_key(self,portal):
        namespace=self.workspace.agent.config.get('_estate',{}).get('manifest_hash')
        if not namespace:
            # Injected installations have no manifest; their retained identity
            # inventory still isolates unrelated estates in one local store.
            namespace=digest(sorted({(p['model_id'],p['report_id'])for p in self._pages()}))
        return digest({'estate_manifest_or_inventory':namespace,'portal':portal})

    @operation('claim_screenshot_identify')
    def identify(self,request):
        self._guard();request_shape(request,('image_id','request_key'),('portal',))
        with self.store.connect() as db:
            prior=db.execute('SELECT id FROM claim_screenshot_reviews WHERE request_key=?',(request['request_key'],)).fetchone()
        if prior:
            saved=self.get(prior[0])
            if saved['request']!=request:raise Conflict('Screenshot identification key already used')
            return saved
        metadata,raw=self.workspace.screenshots.image(request['image_id'],content=True)
        from .local_screenshot_ocr import read,validate
        reader=getattr(self.workspace,'claim_screenshot_ocr',read)
        ocr=validate(bounded_call('claim_screenshot.local_ocr',{'sha256':metadata['sha256'],'mime':metadata['mime']},lambda:reader(raw,metadata['mime'])))
        pages=self._pages();candidates=rank(ocr,pages)
        method='RETAINED_DEFINITION_TEXT';portal=request.get('portal')
        if portal:
            key=self._portal_key(portal)
            with self.store.connect() as db:row=db.execute('SELECT body,hash FROM claim_screenshot_portal_maps WHERE id=?',(key,)).fetchone()
            if row:
                mapping=json.loads(row['body'])
                if digest(mapping)!=row['hash']:raise Conflict('Portal mapping integrity differs')
                matching=[p for p in pages if p['candidate_id']==mapping['candidate_id'] and p['definition_hash']==mapping['definition_hash']]
                if matching:
                    candidates=[dict(matching[0],score=0,matched_anchors=[],status='CANDIDATE')];method='USER_CONFIRMED_PORTAL_MAPPING'
        unique=bool(candidates) and (len(candidates)==1 or candidates[0]['score']>candidates[1]['score'])
        status='IDENTIFIED' if unique else ('NEEDS_INPUT' if candidates else 'UNREADABLE')
        body={'id':str(uuid4()),'request':request,'created':self.workspace.clock(),'status':status,
              'image':metadata,'ocr':ocr,'candidates':candidates[:3],'catalog_hash':digest(pages),
              'identification_method':method,'limitations':['Visible pixels do not establish hidden filters, RLS, cause or freshness.',
                'Numeric ties require a faithful admitted scope; no value probe was made.']}
        if status=='NEEDS_INPUT':body['question']={'text':'Which report page is shown?','choices':[{'candidate_id':p['candidate_id'],'label':p['label']} for p in candidates[:3]]}
        with self.store.connect() as db:db.execute('INSERT INTO claim_screenshot_reviews VALUES(?,?,?,?)',(body['id'],request['request_key'],encoded(body),digest(body)))
        return self.get(body['id'])

    def get(self,identity):
        self._guard()
        with self.store.connect() as db:
            row=db.execute('SELECT body,hash FROM claim_screenshot_reviews WHERE id=?',(identity,)).fetchone()
            confirmations=db.execute('SELECT body,hash FROM claim_screenshot_confirmations WHERE review_id=? ORDER BY rowid',(identity,)).fetchall()
        if not row:raise KeyError('Screenshot identification not found')
        body=json.loads(row['body'])
        if body['id']!=identity or digest(body)!=row['hash']:raise Conflict('Screenshot review integrity differs')
        body=dict(body,review_id=identity,hash=row['hash'],text='\n'.join(line['text'] for line in body['ocr']['lines']))
        checked=[]
        for item in confirmations:
            value=json.loads(item['body'])
            if digest(value)!=item['hash']:raise Conflict('Screenshot confirmation integrity differs')
            checked.append(value)
        body['confirmations']=checked
        candidates=body['candidates']
        chosen=next((p for p in candidates if checked and p['candidate_id']==checked[-1]['candidate_id']),None)
        selected=[chosen] if chosen else candidates
        body['candidate_bindings']=[{'model_id':p['model_id'],'report_id':p['report_id'],'page_id':p['page_id'],
            'target_ids':[v['target_id'] for v in p['targets']], 'label':p['label'],'evidence_ids':[identity],
            'status':'CONFIRMED' if chosen else 'CANDIDATE'} for p in selected]
        body['facts']=[]
        if chosen:
            region={'x':0,'y':0,'width':body['ocr']['width'],'height':body['ocr']['height']}
            body['facts'].append({'field':'scope','value':{'kind':'PAGE','report_id':chosen['report_id'],'page_id':chosen['page_id']},
                'source':{'kind':'SCREENSHOT_REGION','review_id':identity,'review_hash':row['hash'],'evidence_id':identity,'region':region},'authority':'SCREENSHOT_REVIEW'})
        if chosen or (body['status']=='IDENTIFIED' and len(selected)==1):
            page=selected[0]
            labels={label for visual in page['targets'] for label in visual['labels']}
            for line in body['ocr']['lines']:
                for label in sorted(labels):
                    if ' '+normal(label)+' ' not in ' '+normal(line['text'])+' ':continue
                    source={'kind':'SCREENSHOT_REGION','review_id':identity,'review_hash':row['hash'],
                            'evidence_id':identity,'region':line['region'],'text':line['text']}
                    body['facts'].append({'field':'metric','value':{'phrase':label},'source':source,'authority':'SCREENSHOT_REVIEW'})
                    # Only explicitly co-located label/value text is a figure.
                    # Nearby unlabeled numbers are not silently assigned a role.
                    tail=line['text'].casefold().replace(label.casefold(),'').strip(' :')
                    figure_line=line
                    if not tail:
                        neighbors=[]
                        r=line['region']
                        for other in body['ocr']['lines']:
                            if other is line:continue
                            q=other['region']
                            horizontal=min(r['x']+r['width'],q['x']+q['width'])>max(r['x'],q['x'])
                            gap=min(abs(q['y']-(r['y']+r['height'])),abs(r['y']-(q['y']+q['height'])))
                            if not horizontal or gap>min(80,3*max(r['height'],q['height'])):continue
                            # A value near two distinct metric labels is ambiguous.
                            competitors=[x for x in body['ocr']['lines'] if x is not line and x is not other
                                and any(normal(x['text'])==normal(a)for a in labels)
                                and min(x['region']['x']+x['region']['width'],q['x']+q['width'])>max(x['region']['x'],q['x'])
                                and min(abs(q['y']-(x['region']['y']+x['region']['height'])),abs(x['region']['y']-(q['y']+q['height'])))<=min(80,3*max(x['region']['height'],q['height']))]
                            if competitors:continue
                            from .reported_figure import from_candidates
                            try:
                                start=body['text'].find(other['text'])
                                from_candidates([{'start':start,'end':start+len(other['text']),'quote':other['text']}],body['text'])
                            except (ValueError,KeyError):continue
                            neighbors.append(other)
                        if len(neighbors)==1:figure_line=neighbors[0];tail=figure_line['text']
                    if tail:
                        from .reported_figure import from_candidates
                        try:
                            start=body['text'].find(figure_line['text'])+figure_line['text'].find(tail)
                            figure=from_candidates([{'start':start,'end':start+len(tail),'quote':tail}],body['text'])
                        except (ValueError,KeyError):continue
                        value_source=dict(source,region=figure_line['region'],text=figure_line['text'],label_region=line['region'],label_text=line['text'])
                        body['facts'].append({'field':'observation','value':{'role':'OBSERVED','figure':figure,'metric_phrase':label},'source':value_source,'authority':'SCREENSHOT_REVIEW'})
        # All OCR text is retained with positional provenance; identity candidates
        # are separate from facts and cannot become a guessed metric or figure.
        from .claim_facts import fact
        body['facts']=[fact(f['field'],f['value'],f['source'],authority=f['authority'])for f in body['facts']]
        return body

    @operation('claim_screenshot_confirm')
    def confirm(self,request):
        self._guard();request_shape(request,('review_id','candidate_id','request_key'),('portal',))
        review=self.get(request['review_id'])
        candidate=next((p for p in review['candidates'] if p['candidate_id']==request.get('candidate_id')),None)
        if not candidate:raise Conflict('Confirm only a retained screenshot candidate')
        if candidate['candidate_id'] not in {p['candidate_id'] for p in self._pages()}:raise Conflict('Screenshot definition changed; identify again')
        body={'id':str(uuid4()),'review_id':review['id'],'review_hash':review['hash'],'candidate_id':candidate['candidate_id'],
              'definition_hash':candidate['definition_hash'],'created':self.workspace.clock(),'request':request,'authority':'HUMAN_CONFIRMATION'}
        with self.store.connect() as db:
            prior=db.execute('SELECT body,hash FROM claim_screenshot_confirmations WHERE request_key=?',(request['request_key'],)).fetchone()
            if prior:
                old=json.loads(prior['body'])
                if digest(old)!=prior['hash'] or old['request']!=request:raise Conflict('Screenshot confirmation key differs')
                return self.get(review['id'])
            db.execute('INSERT INTO claim_screenshot_confirmations VALUES(?,?,?,?,?)',(body['id'],request['request_key'],review['id'],encoded(body),digest(body)))
            if request.get('portal'):
                key=self._portal_key(request['portal'])
                mapping={'candidate_id':candidate['candidate_id'],'definition_hash':candidate['definition_hash'],'confirmation_id':body['id'],'review_id':review['id'],'review_hash':review['hash']}
                db.execute('INSERT OR REPLACE INTO claim_screenshot_portal_maps VALUES(?,?,?)',(key,encoded(mapping),digest(mapping)))
        return self.get(review['id'])

    def load(self,review_id,catalog=None):
        value=self.get(review_id)
        if value['catalog_hash']!=digest(self._pages()):raise Conflict('Screenshot candidate catalog changed; identify again')
        return {k:value[k] for k in ('id','hash','text','facts','candidate_bindings')}
