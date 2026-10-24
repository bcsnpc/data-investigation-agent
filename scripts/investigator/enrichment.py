"""Definition-pinned enrichment proposals, never runtime facts or graph promotion."""
import copy
import csv
import hashlib
import io
import json
import re
from .shared_state import encoded, sha, amount
from .estate_graph_contract import timestamp

FIELDS={'business_meaning','synonyms','calculation_explanation','hidden_logic','proposed_links'}
LINK_KINDS=('COMPUTED_FROM','FILTERED_BY','JOINED_VIA','COPIED_TO','DERIVED_IN_STEP')
SCHEMA={'type':'object','additionalProperties':False,'required':sorted(FIELDS),'properties':{
    'business_meaning':{'type':'string'},'synonyms':{'type':'array','items':{'type':'string'}},
    'calculation_explanation':{'type':'string'},'hidden_logic':{'type':'array','items':{'type':'string'}},
    'proposed_links':{'type':'array','items':{'type':'object','additionalProperties':False,
        'required':['target','relationship','start','end','quote'],'properties':{
            'target':{'type':'string'},'relationship':{'type':'string','enum':list(LINK_KINDS)},'start':{'type':'integer'},
            'end':{'type':'integer'},'quote':{'type':'string'}}}}}}


def task(value):
    required={'estate','subject','kind','definition_hash','definition','neighbours','evidence_ids'}
    if not isinstance(value,dict) or set(value)!=required:raise ValueError('ENRICHMENT_TASK_SHAPE')
    for key in ('estate','subject','kind'):
        if not isinstance(value[key],str) or not value[key]:raise ValueError('ENRICHMENT_TASK_ID')
    if not re.fullmatch('[a-f0-9]{64}',value['definition_hash']):raise ValueError('ENRICHMENT_DEFINITION_PIN')
    if not isinstance(value['definition'],str) or not 1<=len(value['definition'])<=24000:raise ValueError('ENRICHMENT_DEFINITION_BOUND')
    if not isinstance(value['neighbours'],list) or len(value['neighbours'])>100:raise ValueError('ENRICHMENT_NEIGHBOUR_BOUND')
    if any(not isinstance(n,dict) or set(n)!={'id','kind','label'} or any(not isinstance(n[k],str) or not n[k] for k in n) for n in value['neighbours']):raise ValueError('ENRICHMENT_NEIGHBOUR_SHAPE')
    if not isinstance(value['evidence_ids'],list) or not value['evidence_ids'] or any(not isinstance(e,str) or not e for e in value['evidence_ids']):raise ValueError('ENRICHMENT_EVIDENCE_REQUIRED')
    if len(encoded(value).encode())>64000:raise ValueError('ENRICHMENT_INPUT_BOUND')
    return copy.deepcopy(value)


def validate_output(value,source):
    source=task(source)
    if not isinstance(value,dict) or set(value)!=FIELDS:raise ValueError('ENRICHMENT_OUTPUT_SHAPE')
    for key in ('business_meaning','calculation_explanation'):
        if not isinstance(value[key],str) or not 1<=len(value[key])<=3000:raise ValueError('ENRICHMENT_TEXT_BOUND')
    for key in ('synonyms','hidden_logic'):
        if not isinstance(value[key],list) or len(value[key])>30 or any(not isinstance(s,str) or not 1<=len(s)<=1000 for s in value[key]):raise ValueError('ENRICHMENT_LIST_BOUND')
        if len(set(value[key]))!=len(value[key]):raise ValueError('ENRICHMENT_DUPLICATE_LIST_VALUE')
    links=value['proposed_links']
    if not isinstance(links,list) or len(links)>20:raise ValueError('ENRICHMENT_LINK_BOUND')
    allowed={n['id'] for n in source['neighbours']}
    for link in links:
        if not isinstance(link,dict) or set(link)!={'target','relationship','start','end','quote'}:raise ValueError('ENRICHMENT_LINK_SHAPE')
        if link['target'] not in allowed or link['target']==source['subject']:raise ValueError('ENRICHMENT_LINK_TARGET_NOT_IN_INPUT')
        if link['relationship'] not in LINK_KINDS:raise ValueError('ENRICHMENT_LINK_KIND')
        start,end=link['start'],link['end']
        if type(start) is not int or type(end) is not int or not 0<=start<end<=len(source['definition']):raise ValueError('ENRICHMENT_LINK_SPAN')
        if source['definition'][start:end]!=link['quote']:raise ValueError('ENRICHMENT_LINK_QUOTE_NOT_VERBATIM')
    return copy.deepcopy(value)


def cache_key(source):
    return sha([source['estate'],source['subject'],source['definition_hash'],sha(source['neighbours'])])


class EnrichmentStore:
    def __init__(self,state):self.state=state

    def cached(self,source):
        source=task(source)
        try:return self.state.get('enrichment_cache',cache_key(source))['body']
        except KeyError:return None

    def apply(self,source,output,*,at,producer,recording_class,evidence_ids):
        source=task(source);output=validate_output(output,source);at=timestamp(at)
        if recording_class not in ('EXACT','PRIVACY_PROJECTED','RECORDED_STUB'):raise ValueError('ENRICHMENT_RECORDING_CLASS')
        if recording_class=='RECORDED_STUB' and (self.state.backend!='sqlite' or self.state.mode!='offline'):raise ValueError('ENRICHMENT_STUB_PRIVATE_OFFLINE_ONLY')
        if not evidence_ids:raise ValueError('ENRICHMENT_MODEL_RECEIPT_REQUIRED')
        row={'subject':source['subject'],'estate':source['estate'],'kind':source['kind'],
            'definition_hash':source['definition_hash'],'definition_text_sha256':hashlib.sha256(source['definition'].encode()).hexdigest(),
            **output,'status':'INFERRED','updated_at':at,'recording_class':recording_class,
            'provenance':{'producer':producer,'evidence_ids':list(evidence_ids),'definition_evidence_ids':source['evidence_ids']},
            'input':source}
        row['proposed_links']=[{**link,'status':'INFERRED','definition_hash':source['definition_hash']} for link in row['proposed_links']]
        key=cache_key(source)
        try:old=self.state.get('enrichment_cache',key)
        except KeyError:old=None
        if old and old['body']['status']=='HUMAN_CONFIRMED':return old['body']
        self.state.put('enrichment_cache',key,row,revision=old['revision'] if old else None)
        current_key=sha([source['estate'],source['subject']])
        try:current=self.state.get('enrichment_current',current_key)
        except KeyError:current=None
        if current and current['body']['status']=='HUMAN_CONFIRMED':return current['body']
        self.state.put('enrichment_current',current_key,row,revision=current['revision'] if current else None)
        return row

    def projection(self,estate,subject,definition_hash=None):
        try:row=self.state.get('enrichment_current',sha([estate,subject]))['body']
        except KeyError:return None
        return {**{k:copy.deepcopy(row[k]) for k in ('estate','subject','synonyms','business_meaning','calculation_explanation','hidden_logic','definition_hash','status','proposed_links','provenance','recording_class')},
                'stale_definition':definition_hash is not None and row['definition_hash']!=definition_hash}

    def projections(self,estate,subjects):
        """One short read transaction for a bounded, already-authorized catalog."""
        if not isinstance(subjects,dict)or len(subjects)>200:raise ValueError('ENRICHMENT_SEARCH_SUBJECT_BOUND')
        def read(db):
            result={}
            for subject,definition_hash in subjects.items():
                try:row=self.state._get(db,'enrichment_current',sha([estate,subject]))['body']
                except KeyError:continue
                if row['estate']!=estate or row['subject']!=subject:raise ValueError('ENRICHMENT_SEARCH_IDENTITY_DIFFERS')
                if definition_hash is not None and row['definition_hash']!=definition_hash:continue
                result[subject]={k:copy.deepcopy(row[k])for k in ('synonyms','business_meaning','status','definition_hash','provenance')}
            return result
        return self.state._read_transaction(read)

    def confirm(self,source,output,*,at,reviewer):
        if not isinstance(reviewer,str) or not reviewer.strip():raise ValueError('ENRICHMENT_HUMAN_REVIEWER_REQUIRED')
        source=task(source);validated=validate_output(output,source)
        row=self.cached(source)
        if row is None:raise ValueError('ENRICHMENT_REVIEW_REQUIRES_RECORDED_PROPOSAL')
        row={**row,**validated,'status':'HUMAN_CONFIRMED','updated_at':timestamp(at),
             'provenance':{**row['provenance'],'human_reviewer':reviewer,'human_confirmed_at':timestamp(at)}}
        # Human prose correction cannot promote any relationship to verified.
        row['proposed_links']=[{**link,'status':'INFERRED','definition_hash':source['definition_hash']} for link in validated['proposed_links']]
        for namespace,key in (('enrichment_cache',cache_key(source)),('enrichment_current',sha([source['estate'],source['subject']]))):
            try:old=self.state.get(namespace,key)
            except KeyError:old=None
            self.state.put(namespace,key,row,revision=old['revision'] if old else None)
        return row


CSV_FIELDS=['estate','subject','definition_hash','business_meaning','synonyms','calculation_explanation','hidden_logic','proposed_links']


def export_csv(rows):
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=CSV_FIELDS);writer.writeheader()
    for row in rows:
        item={key:row[key] for key in CSV_FIELDS}
        for key in ('synonyms','hidden_logic','proposed_links'):
            value=copy.deepcopy(item[key])
            if key=='proposed_links':value=[{k:v for k,v in link.items() if k not in ('status','definition_hash')} for link in value]
            item[key]=encoded(value)
        for key,value in item.items():
            if value.startswith(('=','+','-','@',"'")):item[key]="'"+value
        writer.writerow(item)
    return stream.getvalue()


def import_csv(store,text,*,at,reviewer):
    reader=csv.DictReader(io.StringIO(text,newline=''))
    if reader.fieldnames!=CSV_FIELDS:raise ValueError('ENRICHMENT_REVIEW_CSV_COLUMNS')
    parsed=[]
    for number,row in enumerate(reader):
        if number>=1000 or None in row:raise ValueError('ENRICHMENT_REVIEW_BOUND')
        row={key:(value[1:] if value and value.startswith("'") else value) for key,value in row.items()}
        current=store.state.get('enrichment_current',sha([row['estate'],row['subject']]))['body']
        if row['definition_hash']!=current['definition_hash']:raise ValueError('ENRICHMENT_REVIEW_DEFINITION_DIFFERS')
        output={key:(json.loads(row[key]) if key in ('synonyms','hidden_logic','proposed_links') else row[key]) for key in FIELDS}
        validate_output(output,current['input']);parsed.append((current['input'],output))
    # All records validate before the first human correction is applied.
    return [store.confirm(source,output,at=at,reviewer=reviewer) for source,output in parsed]
