"""Trusted cloud adapter for the single ledger investigator; no dynamic imports."""
import json
from pathlib import Path
from investigator.ledger_investigator_tools import Tools
from investigator.ledger_investigator import Investigator


def run(plan,context,*,graph,ledger,value_reader,decide,admit,collector=None,checks=None,now,recording_class='EXACT'):
    """Root's registry supplies installed guarded ports, never the ticket/model.

    No refresh/run/write handler exists. In particular, value_reader must be a
    compiler-backed gateway read using the admitted graph identifiers.
    """
    options=plan['options'];ticket=json.loads(Path(options['ticket']).read_bytes())
    def persist(value):
        reference=context.record('investigator-event',value)
        return reference['key']
    tools=Tools(graph,ledger,visual=ticket.get('visual') or ticket['request']['subject'],key=ticket.get('key'),context=ticket.get('filters',{}),
        comparison=ticket.get('comparison'),persist=persist,now=now,value_reader=value_reader,collector=collector,checks=checks,request_kind=ticket.get('request',{}).get('kind','COMPARE'),recording_class=recording_class)
    result=Investigator(tools,decide=decide,persist=persist,admit=admit,step_cap=options.get('step_cap',12),wall_seconds=options.get('wall_seconds',900)).run(ticket,warnings=options.get('warnings',[]))
    # JSON run bundle is persisted through the normal outer capture before return.
    context.record('investigator-bundle',result)
    return result
