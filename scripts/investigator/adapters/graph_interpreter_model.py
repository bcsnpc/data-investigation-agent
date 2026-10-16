"""Installed structured provider; the graph interpreter caller owns metering."""
def propose(request,schema,options):
    from ticket_planner import _azure_generate
    from ..contract_vocabulary import instructions
    payload={key:value for key,value in request.items() if key!='instructions'}
    answer,metadata=_azure_generate(payload,instructions=instructions(request['instructions'],schema),
        schema=schema,name='retained_graph_edge_proposals',generation_options=options)
    return answer,metadata
