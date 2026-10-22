"""Offline recorded enrichment responses; never confused with live model output."""
import json
from ..shared_state import sha, encoded
from .enrichment_anthropic import request_for, price, MODEL


class RecordedEnrichmentStub:
    provider='recorded-enrichment-stub'
    model=MODEL
    recording_class='RECORDED_STUB'
    request_for=staticmethod(request_for)
    price=staticmethod(price)
    def __init__(self,outputs):self.outputs=outputs;self.requests={};self.receipt=None
    def create(self,requests):
        self.requests={request['custom_id']:request for request in requests}
        self.receipt={'id':'msgbatch_recordedstub'+sha(requests)[:12],'processing_status':'ended','recording_class':self.recording_class}
        return self.receipt
    def restore(self,receipt):self.receipt=receipt
    def status(self,batch):return self.receipt
    def results(self,batch):
        # Result order deliberately reversed: IDs, not position, bind outputs.
        return [{'custom_id':key,'result':{'type':'succeeded','message':{
            'model':self.model,'stop_reason':'end_turn','content':[{'type':'text','text':encoded(self.outputs[json.loads(request['params']['messages'][0]['content'])['subject']])}],
            'usage':{'input_tokens':10,'output_tokens':10}}}} for key,request in reversed(list(self.requests.items()))]
