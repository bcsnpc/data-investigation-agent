"""Installed Microsoft value and Azure decision ports for the ledger investigator.

These ports reuse the bounded native compilers and the existing daily/dollar
governors. Graph labels and model arguments never become native expressions.
"""
import copy
import hashlib
import json

from ..estate_graph_contract import canonical
from ..process_debugging import attest
from ..refresh_comparison import whole_entity_context


def installed_process(store,config,model,*,meter_read,max_boundaries=32,read_endpoint=None,judge_definition=None):
    """Construct the installed readers without owner/alternate-identity fallback.

    Callers own admitted input pins, the physical guard scope and its meter.
    The existing isolated worker remains the only SQL/DAX execution surface.
    """
    from .estate_installation import transports
    from .microsoft_process import MicrosoftProcessAdapter
    from fabric_sql_surface import read,reader_availability
    if not callable(meter_read):raise ValueError('GOVERNED_PROCESS_READER_REQUIRED')
    native,source=transports(config)
    configured=bool(config.get('fabric',{}).get('sql_reader'))
    return MicrosoftProcessAdapter(store,config,model,native,source,meter_read=meter_read,
        lower_surface=reader_availability(config) if configured else None,
        execute_lower=(lambda database,request:read(config,database,request)) if configured else None,
        read_endpoint=read_endpoint,max_boundaries=max_boundaries,judge_definition=judge_definition)


class ProcessValues:
    """Read exact resolved layers of one admitted measure through its adapter.

    ``process`` is the trusted, metered MicrosoftProcessAdapter constructed by
    the installed runtime. The graph slice must be the ticket's admitted path,
    not an arbitrary identifier mapping supplied by the model.
    """
    def __init__(self, process, *, graph_slice, visual, measure_id, retain):
        if not callable(process.meter_read) or not callable(retain):
            raise ValueError('GOVERNED_PROCESS_READER_REQUIRED')
        self.process=process;self.measure_id=measure_id;self.retain=retain
        self.nodes={node['id']:copy.deepcopy(node) for node in graph_slice['nodes']}
        if visual not in self.nodes:raise ValueError('TARGET_OUTSIDE_TICKET_PATH')
        measures=[node for node in self.nodes.values() if node['kind']=='MEASURE'
                  and node.get('properties',{}).get('asset_id')==measure_id]
        if len(measures)!=1:raise ValueError('EXACT_MEASURE_GRAPH_BINDING_REQUIRED')
        reachable={visual}
        for _ in range(len(self.nodes)):
            expanded=reachable|{e['target'] for e in graph_slice['edges'] if e['source'] in reachable and e['target'] in self.nodes}
            if expanded==reachable:break
            reachable=expanded
        if measures[0]['id'] not in reachable:raise ValueError('TARGET_MEASURE_NOT_CONNECTED')
        self.path=copy.deepcopy(process.resolve_path(measure_id))
        layers=self.path.get('layers',[])
        if not layers or layers[0].get('kind')!='presentation':raise ValueError('RESOLVED_PRESENTATION_REQUIRED')
        self.layers={visual:layers[0]};self.probes={}
        for node in self.nodes.values():
            asset=node.get('properties',{}).get('asset_id')
            matches=[layer for layer in layers if layer['id']==asset]
            if len(matches)==1:self.layers[node['id']]=matches[0]
        self.layers[measures[0]['id']]=layers[0]

    @staticmethod
    def scope(context):
        if context=={}:return {'filters':[],'dimension_ids':[]}
        if context==whole_entity_context():return {'filters':[],'dimension_ids':[]}
        if (not isinstance(context,dict) or set(context)-{'filters','dimension_ids'}
                or not isinstance(context.get('filters',[]),list)
                or not isinstance(context.get('dimension_ids',[]),list)):
            raise ValueError('DECLARED_SCOPE_SHAPE_UNSUPPORTED')
        return copy.deepcopy(context)

    def __call__(self,node,key,context):
        if key is not None:raise ValueError('KEYED_QUANTITY_ROUTE_NOT_INSTALLED')
        if node not in self.layers:raise ValueError('NO_EXACT_COMPILED_LAYER_FOR_GRAPH_NODE')
        scope=self.scope(context)
        probe=attest(self.process.evaluate(copy.deepcopy(self.layers[node]),self.measure_id,scope))
        # Preserve original failures and receipts even when no quantity exists.
        self.retain({'event':'INVESTIGATOR_NATIVE_PROBE','subject':node,'status':probe.status,
                     'reason':probe.reason,'failure':probe.failure,'evidence':probe.evidence,
                     'query':probe.query,'execution_surface':probe.execution_surface})
        if probe.status!='OBSERVED':raise ValueError(probe.reason or 'COMPILED_QUANTITY_NOT_OBTAINED')
        evidence=probe.evidence or {}
        if not evidence.get('id') or not probe.query:raise ValueError('ORIGINAL_NATIVE_READ_RECEIPT_REQUIRED')
        if scope.get('filters') or scope.get('dimension_ids'):
            # The native compiler retains its scope; never relabel an unfiltered
            # read as a filtered one. Existing lower compiler refuses translation.
            expected=scope
        else:expected=whole_entity_context()
        original=evidence.get('declared_context')
        if original is not None and canonical(original)!=canonical(expected):
            raise ValueError('NATIVE_DECLARED_CONTEXT_DIFFERS')
        value=probe.value
        if isinstance(value,dict) and set(value)=={'quantity'}:value=value['quantity']
        result={'subject':node,'key':key,'context':copy.deepcopy(context),
                'state':'BLANK' if value is None else 'VALUE','value':value,
                'receipt_id':evidence['id'],'route_admitted':True,'read_only_verified':True,
                'query':probe.query,'expression_hash':hashlib.sha256(probe.query.encode()).hexdigest(),
                'execution_surface':copy.deepcopy(probe.execution_surface),
                'native_evidence':copy.deepcopy(evidence),'warnings':['SNAPSHOT_UNVERIFIED']}
        from ..evidence_verdicts import quantity
        quantity(result)
        if evidence.get('attestation_warning'):result['warnings'].append(evidence['attestation_warning'])
        self.probes[evidence['id']]=probe
        return result


class AzureDecision:
    """One native Azure request, reserved and recorded before dispatch.

    The provider's existing admission owns the shared dollar reservation; this
    port also owns the existing UsageGovernor's daily reservation and settlement.
    No credentials or provider are selected by ticket/model text.
    """
    def __init__(self, governor, *, session, directory, retain, options=None, producer=None):
        from ..generation_policy import validate
        if not callable(retain) or not session:raise ValueError('GOVERNED_MODEL_SESSION_REQUIRED')
        self.governor=governor;self.session=session;self.directory=directory;self.retain=retain
        self.options=validate(options);self.producer=producer;self.calls=0

    def __call__(self,payload,*,instructions,schema):
        from ticket_planner import _azure_generate,provider_body
        from ..contract_vocabulary import instructions as vocabulary
        from ..planner_recording import recording
        from ..generation_policy import failure_usage
        instruction=vocabulary(instructions,schema)
        body=provider_body(payload,instruction,schema,'ledger_investigator_action',
                           decision_tool=True,generation_options=self.options)
        size=len(json.dumps(body,ensure_ascii=False,separators=(',',':')))
        if size>self.options['max_payload_characters']:raise ValueError('INVESTIGATOR_PROVIDER_INPUT_BOUND')
        self.calls+=1;key='ledger-investigator:'+str(self.calls)
        with self.governor.runtime.db() as db:
            self.governor.reserve(db,self.session,key,'planner',size,
                                  output_tokens=self.options['max_output_tokens'])
        metadata={};error=None
        try:
            with recording({'session_id':self.session,'planner_call':self.calls,
                            'call_kind':'ledger_investigator_action','payload':payload,
                            'reservation':{'input_characters':size,'output_tokens':self.options['max_output_tokens']}},
                           distinct=True,directory=self.directory) as record:
                if record is None:raise ValueError('INVESTIGATOR_PROVIDER_CAPTURE_REQUIRED')
                record.safe_write('compiled-provider-body.json',json.dumps(body,sort_keys=True).encode())
                answer,metadata=(self.producer or _azure_generate)(payload,instructions=instruction,schema=schema,
                    name='ledger_investigator_action',decision_tool=True,generation_options=self.options,
                    max_request_characters=self.options['max_payload_characters'])
                self.retain({'event':'INVESTIGATOR_MODEL_USAGE','call':self.calls,'metadata':metadata,
                             'input_characters':size,'recording':str(record.path)})
                return answer
        except Exception as exc:error=exc;raise
        finally:
            usage=failure_usage(error) if error is not None else metadata.get('usage')
            with self.governor.runtime.db() as db:
                self.governor.settle(db,self.session,key,usage,uncertain=usage is None)

    def judge_definition(self,payload):
        from ..transformation_judgment import INSTRUCTIONS,SCHEMA,validate
        return validate(self(payload,instructions=INSTRUCTIONS,schema=SCHEMA))


class ProcessChecks:
    """Check one model-selected boundary over the already obtained probes.

    This is not a second pipeline walk: no quantities are re-read, and only the
    exact requested adjacent boundary's retained definition is judged. Existing
    native assessment validators check the resulting proof before it crosses.
    """
    def __init__(self,values):self.values=values

    def __call__(self,kind,comparison,records):
        if kind!='DESIGN_CHECK':raise ValueError(kind+'_NATIVE_PRODUCER_NOT_INSTALLED')
        from ..native_verdict_support import design_witness
        from ..process_debugging import _observation,_answer
        from ..surface_difference import grade,BOUNDARY_GRADES
        comparison_value=comparison['value']
        left=records[comparison_value['left']]['value'];right=records[comparison_value['right']]['value']
        if canonical(left['context'])!=canonical(right['context']):raise ValueError('DESIGN_CONTEXT_DIFFERS')
        port=self.values
        if left['receipt_id'] not in port.probes or right['receipt_id'] not in port.probes:
            raise ValueError('DESIGN_ORIGINAL_PROBE_NOT_RETAINED')
        upper=port.probes[left['receipt_id']];lower=port.probes[right['receipt_id']]
        layers=port.path['layers'];pairs=[(index,a,b) for index,(a,b) in enumerate(zip(layers,layers[1:]),1)
            if (a['id'],b['id'])==(upper.layer,lower.layer)]
        if len(pairs)!=1:raise ValueError('DESIGN_REQUIRES_EXACT_ADJACENT_LAYERS')
        index,upper_layer,lower_layer=pairs[0]
        if upper.value==lower.value:raise ValueError('DESIGN_REQUIRES_OBSERVED_DIVERGENCE')
        difference=grade(upper.evidence,lower.evidence)
        if difference['grade'] not in BOUNDARY_GRADES:raise ValueError('DESIGN_ATTESTED_BOUNDARY_REQUIRED')
        if port.process.judge_definition is None:raise ValueError('GOVERNED_DEFINITION_JUDGMENT_NOT_INSTALLED')
        boundary={'upper':upper_layer,'lower':lower_layer,'index':index,'upper_probe':upper,'lower_probe':lower}
        definition=port.process.transformation_definition(boundary)
        if definition.get('status')!='COMPLETED' or definition.get('explains')is not True:
            raise ValueError('RETAINED_DEFINITION_DOES_NOT_ESTABLISH_MECHANISM')
        observations=[]
        for probe in port.probes.values():
            observations.append(_observation({**probe.evidence,'query':probe.query,
                                               'execution_surface':probe.execution_surface},'baseline','established'))
        marker={'id':'investigator-native-boundary-'+hashlib.sha256(canonical([left['receipt_id'],right['receipt_id']]).encode()).hexdigest(),
                'tool':'process','comparison_status':'CROSS_SURFACE_VERIFIED','surface_difference':difference,'values_equal':False,
                'lower_binding_provenance':lower.evidence.get('binding_provenance')}
        for side,probe in (('upper',upper),('lower',lower)):
            marker.update({side+'_layer':probe.layer,side+'_evidence_id':probe.evidence['id'],
                side+'_execution_surface':probe.execution_surface,side+'_surface_attestation':probe.evidence['surface_attestation'],
                side+'_declared_context':probe.evidence.get('declared_context')})
        observations.append(_observation(marker,'comparison'))
        observations.append(_observation(definition.get('evidence'),'transformation_definition'))
        assessment=_answer('TRANSFORMATION_LOGIC',5,observations,lower.layer,
            baseline={'status':'ESTABLISHED','layer':upper.layer,'reason':None,'evidence_ids':[upper.evidence['id']]},
            roles=('transformation_definition','comparison'),explanation=definition['explanation'],
            capabilities=port.process.capabilities())
        # A later-layer divergence remains connected to the original measure
        # through its actual presentation baseline, not a relabelled SQL read.
        measure_refs=[o['id'] for o in observations if o.get('test_purpose') in
                      ('TEST_CONTRIBUTION','ESTABLISH_BASELINE','REPRODUCE_MEASURE')]
        if not measure_refs:raise ValueError('ORIGINAL_MEASURE_BASELINE_REQUIRED')
        assessment['support']['measure_connection_evidence_ids']=measure_refs
        witness=design_witness(assessment,{o['id']:o for o in observations})
        port.retain({'event':'INVESTIGATOR_NATIVE_DEFINITION_CHECK','assessment':assessment,'witness':witness})
        return witness
