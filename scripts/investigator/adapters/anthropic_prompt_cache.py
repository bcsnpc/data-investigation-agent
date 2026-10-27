"""Explicit, opt-in stable-prefix caching for the owner's Opus diagnostic."""
from copy import deepcopy
from hashlib import sha256
from ..estate_graph_contract import canonical


def assert_cache_reads(records):
    """Post-run assertion, never a reason to discard a delivered finding."""
    for record in records:
        if record['successful_call']>1 and record['cache_read_input_tokens']==0:
            raise AssertionError('DIAGNOSTIC_SUBSEQUENT_CALL_ZERO_CACHE_READS')


class StablePrefix:
    def __init__(self):
        self.system=None;self.tools=None;self.original_tools=None;self.calls=0

    def prepare(self,body):
        result=deepcopy(body)
        tools=deepcopy(body['tools'])
        if self.system is None:
            self.system=deepcopy(body['system']);self.original_tools=deepcopy(tools)
            # Query kinds can become active after get_lineage. Declare the same
            # generic contracts once; original local schemas still enforce the
            # CURRENT admitted layers and reject inactive/unknown addresses.
            names={tool['name']for tool in tools}
            purposes=['recreate','compare','record','lookup','security','different_question','history']
            for name in ('run_sql','run_dax'):
                if name not in names:
                    tools.append({'name':name,'description':'Read-only query on a currently admitted layer. Expand lineage first if inactive; exact current identifiers are in the context and current-state messages.',
                        'input_schema':{'type':'object','additionalProperties':False,'required':['layer','query','purpose'],
                            'properties':{'layer':{'type':'string'},'query':{'type':'string','minLength':1},'purpose':{'enum':purposes}}}})
            self.tools=sorted(tools,key=lambda tool:tool['name'])
            self.tools[-1]['cache_control']={'type':'ephemeral'}
        changing={}
        if body['system']!=self.system:
            changing['updated_context_after_pinned_prefix']=body['system']
        if body['tools']!=self.original_tools:
            # No tool definitions move inside the cached prefix. Changes to
            # admitted IDs, availability or schemas remain visible after it.
            changing['current_admitted_tools']=deepcopy(body['tools'])
        result['system']=deepcopy(self.system);result['tools']=deepcopy(self.tools)
        if changing:
            result['messages'].append({'role':'user','content':canonical(changing)})
        self.prefix_sha256=sha256(canonical([self.tools,self.system]).encode()).hexdigest()
        return result

    def observe(self,usage):
        self.calls+=1;usage=usage or{}
        counts={key:usage.get(key,0)for key in('input_tokens','output_tokens','cache_creation_input_tokens','cache_read_input_tokens')}
        if any(type(value)is not int or value<0 for value in counts.values()):
            raise ValueError('NATIVE_CACHE_USAGE_COUNTS_REQUIRED')
        return {'event':'REASONING_CACHE_USAGE','prefix_sha256':self.prefix_sha256,
                'successful_call':self.calls,**counts,
                'total_input_tokens':sum(counts[key]for key in('input_tokens','cache_creation_input_tokens','cache_read_input_tokens')),
                'subsequent_cache_read_check':'NOT_APPLICABLE'if self.calls==1 else'PASS'if counts['cache_read_input_tokens']>0 else'FAIL',
                'ttl':'5m','minimum_cacheable_tokens':512,'diagnostic_only':True}
